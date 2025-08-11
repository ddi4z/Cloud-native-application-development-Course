from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, orm
from src.domain.models.user import UserStatus
from sqlalchemy.sql import func
import uuid

Base = orm.declarative_base()

class UserDB(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    phoneNumber = Column(String)
    dni = Column(String)
    fullName = Column(String)
    password = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    token = Column(String, nullable=False)
    status = Column(SQLEnum(UserStatus), nullable=False)
    expireAt = Column(DateTime(timezone=True), nullable=False)
    createdAt = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
