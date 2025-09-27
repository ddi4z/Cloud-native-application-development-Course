import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.models.user import User, UserStatus
from src.domain.models.user_creation_request import UserCreationRequest
from src.domain.models.user_db import Base, UserDB
from src.domain.models.user_update_request import UserUpdateRequest
from src.errors import (
    InvalidCredentialsError,
    InvalidTokenError,
    MissingTokenError,
    MissingUserInformationError,
    UnauthorizedUserStatusError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.domain.models.user_callback_request import UserCallbackRequest

load_dotenv()


class PostgresUserRepositoryAdapter:
    """Postgres implementation of UserRepository using SQLAlchemy."""

    def __init__(self):
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL not set in environment variables")
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        Base.metadata.create_all(bind=self.engine)

    def _get_session(self):
        """Create a new database session."""
        return self.SessionLocal()

    def generate_expiration_time(self, time_now: datetime) -> datetime:
        return time_now + timedelta(hours=1)

    def _to_domain(self, user_db: UserDB) -> User:
        return User(
            id=user_db.id,
            username=user_db.username,
            email=user_db.email,
            phoneNumber=user_db.phoneNumber,
            dni=user_db.dni,
            fullName=user_db.fullName,
            password=user_db.password,
            salt=user_db.salt,
            token=user_db.token,
            status=user_db.status,
            expireAt=user_db.expireAt,
            createdAt=user_db.createdAt,
            updatedAt=user_db.updatedAt,
        )

    def create(self, user_dto: UserCreationRequest) -> User:
        with self._get_session() as db:
            if not all([user_dto.username, user_dto.password, user_dto.email]):
                raise MissingUserInformationError(
                    "Username, password, and email are required."
                )

            existing = (
                db.query(UserDB)
                .filter(
                    (UserDB.username == user_dto.username)
                    | (UserDB.email == user_dto.email)
                )
                .first()
            )
            if existing:
                raise UserAlreadyExistsError("Username or email already exists.")

            salt = os.urandom(16).hex()
            password_hash = hashlib.sha256(
                (user_dto.password + salt).encode()
            ).hexdigest()
            time_now = datetime.now(timezone.utc)

            orm_user = UserDB(
                username=user_dto.username,
                email=user_dto.email,
                phoneNumber=user_dto.phoneNumber,
                dni=user_dto.dni,
                fullName=user_dto.fullName,
                password=password_hash,
                salt=salt,
                token=str(uuid4()),
                status=UserStatus.PENDING_VERIFICATION,
                expireAt=self.generate_expiration_time(time_now),
                createdAt=time_now,
                updatedAt=time_now,
            )

            db.add(orm_user)
            db.commit()
            db.refresh(orm_user)
            return self._to_domain(orm_user)

    def update(self, user_id: str, update_data: UserUpdateRequest) -> User:
        with self._get_session() as db:
            user = db.query(UserDB).filter(UserDB.id == user_id).first()
            if not user:
                raise UserNotFoundError(f"User with id {user_id} not found.")

            if not any(
                [
                    update_data.status,
                    update_data.dni,
                    update_data.fullName,
                    update_data.phoneNumber,
                ]
            ):
                raise MissingUserInformationError(
                    "At least one field must be provided for update."
                )

            for key, value in update_data.model_dump(exclude_none=True).items():
                setattr(user, key, value)
            user.updatedAt = datetime.now(timezone.utc)

            db.commit()
            db.refresh(user)
            return self._to_domain(user)

    def authenticate(self, username: str, password: str) -> Optional[User]:
        with self._get_session() as db:
            if not all([username, password]):
                raise MissingUserInformationError("Username and password are required.")

            user = db.query(UserDB).filter(UserDB.username == username).first()
            if not user:
                raise InvalidCredentialsError("Invalid username or password.")

            salted_password = hashlib.sha256(
                (password + user.salt).encode()
            ).hexdigest()
            if user.password != salted_password:
                raise InvalidCredentialsError("Invalid username or password.")

            if user.status != UserStatus.VERIFIED:
                raise UnauthorizedUserStatusError(
                    "User status does not allow authentication."
                )

            time_now = datetime.now(timezone.utc)
            user.token = str(uuid4())
            user.expireAt = self.generate_expiration_time(time_now)
            user.updatedAt = time_now

            db.commit()
            db.refresh(user)
            return self._to_domain(user)

    def get_current_user(self, token: Optional[str]) -> Optional[User]:
        with self._get_session() as db:
            if not token:
                raise MissingTokenError("Token is missing from the request header.")

            user = db.query(UserDB).filter(UserDB.token == token).first()
            if not user or user.expireAt < datetime.now(timezone.utc):
                raise InvalidTokenError("The token is invalid or has expired.")

            return self._to_domain(user)

    def count(self) -> int:
        with self._get_session() as db:
            return db.query(UserDB).count()

    def reset(self) -> None:
        with self._get_session() as db:
            db.query(UserDB).delete()
            db.commit()

    def patch(self, user_id: str, callback_data: UserCallbackRequest) -> User:
        SECRET_TOKEN = callback_data.secretToken
        RUV = callback_data.ruv
        SCORE = callback_data.score

        token = f"{SECRET_TOKEN}:{RUV}:{SCORE}"
        sha_token = hashlib.sha256(token.encode()).hexdigest()
        assert sha_token == callback_data.verifyToken

        updated_user = self.update(
            user_id, UserUpdateRequest(status=UserStatus.VERIFIED)
        )
        return self._to_domain(updated_user)
