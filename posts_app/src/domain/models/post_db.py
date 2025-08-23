from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, orm
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

Base = orm.declarative_base()


class PostDB(Base):
    __tablename__ = "posts"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    routeId: Mapped[UUID]
    userId: Mapped[UUID]
    expireAt: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    createdAt: Mapped[datetime] = mapped_column(DateTime(timezone=True))
