import uuid

from sqlalchemy import Column
from sqlalchemy import Enum as SQLEnum, DateTime
from sqlalchemy import String, orm
from sqlalchemy.sql import func

from credit_card_app.src.domain.models.credit_card import CreditCardStatus
from credit_card_app.src.domain.models.credit_card import CreditCardIssuer

Base = orm.declarative_base()


class CreditCardDB(Base):
    __tablename__ = "credit_cards"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    token = Column(String, nullable=False)
    userId = Column(String, nullable=False)
    lastFourDigits = Column(String, nullable=False)
    issuer = Column(SQLEnum(CreditCardIssuer), nullable=False)
    status = Column(SQLEnum(CreditCardStatus), nullable=False)

    createdAt = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updatedAt = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )