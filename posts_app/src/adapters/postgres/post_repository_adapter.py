import hashlib
import os
from typing import Optional, List
from uuid import uuid4, UUID
from datetime import datetime, timedelta, timezone


from sqlalchemy import create_engine, select, func, delete
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from src.domain.models.posts import Post
from src.domain.models.post_creation_request import PostCreationRequest
from src.domain.ports.post_repository_port import PostRepositoryPort

from src.domain.models.post_db import Base, PostDB
from src.errors import (
    InvalidCredentialsError, MissingIdError, MissingPostInformationError,
    InvalidExpirationDate, PostNotFoundError
)

load_dotenv()

class PostgresUserRepositoryAdapter:
    """Postgres implementation of UserRepository using SQLAlchemy."""

    def __init__(self):
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL not set in environment variables")
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)


    # helper methods

    def sequence(self) -> UUID:
        return uuid4()
    
    def _to_domain(self, post_db: PostDB) -> Post:
        return Post(
            id = post_db.id,
            routeId = post_db.routeId,
            userId = post_db.userId,
            expireAt = post_db.expireAt,
            createdAt = post_db.createdAt
        )

    def _get_session(self):
        """Create a new database session."""
        return self.SessionLocal()
    
    # DB Methods

    def create(self, post_dto: PostCreationRequest) -> Post:
        with self._get_session() as db:
            if not all([post_dto.routeId, post_dto.expireAt, post_dto.userId]):
                raise MissingPostInformationError("Route Id, Expiration date, and User id are all required.")
            
            if post_dto.expireAt <= datetime.now(timezone.utc):
                raise InvalidExpirationDate("Expiration date must be in the future.")
            
            new_id = self.sequence()
            time_now = datetime.now(timezone.utc)

            orm_post = PostDB(
                id = new_id,
                routeId = post_dto.routeId,
                userId = post_dto.userId,
                expireAt = post_dto.expireAt,
                createdAt = time_now
            )

            db.add(orm_post)
            db.commit()
            db.refresh(orm_post)
            return self._to_domain(orm_post)
        

    def filter(self, expire: Optional[bool] = None, route: Optional[UUID] = None, owner: Optional[UUID] = None,) -> List[Post]:
        
        if expire is not None and not isinstance(expire, bool):
            raise InvalidCredentialsError('Expired has to be boolean')
        if route is not None and not isinstance(route, UUID):
            raise InvalidCredentialsError('Route has tu be a valid id')
        if owner is not None and not isinstance(owner, UUID):
            raise InvalidCredentialsError('Owner has tu be a valid id')
        
        time_now = datetime.now(timezone.utc)
        stmt = select(PostDB)

        if expire is True:
            stmt = stmt.where(PostDB.expireAt <= time_now)
        elif expire is False:
            stmt = stmt.where(PostDB.expireAt > time_now)

        if route is not None:
            stmt = stmt.where(PostDB.routeId == route)
        if owner is not None:
            stmt = stmt.where(PostDB.userId == owner)

        with self._get_session() as s:
            rows = s.execute(stmt).scalars().all()
        return [self._to_domain(r) for r in rows]

    def query(self, id: str) -> Optional[Post]:
        if not isinstance(id, (str, UUID)) or (isinstance(id, str) and not id.strip()):
            raise InvalidCredentialsError("Id is required and must be a UUID string.")
        
        try:
            post_id = id if isinstance(id, UUID) else UUID(id)
        except (ValueError, TypeError):
            raise InvalidCredentialsError("Id doesn't have the correct format. Expected UUID.")

        with self._get_session() as s:
            row = s.get(PostDB, post_id)
            if not row:
                raise PostNotFoundError("The provided id is not in the database")
            return self._to_domain(row)
        
    def delete(self, id:str | UUID):
        if id is None or (isinstance(id, str) and not id.strip()):
            raise MissingIdError("Id is missing from the request header.")
        try:
            post_id = id if isinstance(id, UUID) else UUID(id)
        except Exception:
            raise InvalidCredentialsError("Id must be a string with UUID format.")

        with self._get_session() as s:
            row = s.get(PostDB, post_id)
            if not row:
                raise PostNotFoundError("The provided id is not in the database")
            deleted = self._to_domain(row)
            s.delete(row)
            return deleted
        
    def ping(self) -> str:
        with self._get_session() as s:
            s.execute(select(func.now()))
        return "pong"

    def count(self) -> int:
        with self._get_session() as db:
            return db.query(PostDB).count()

    def reset(self) -> None:
        with self._get_session() as db:
            db.query(PostDB).delete()
            db.commit()