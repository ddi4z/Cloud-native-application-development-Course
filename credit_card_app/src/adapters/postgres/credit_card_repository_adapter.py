import os
from typing import List, Optional
from uuid import UUID
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.domain.models.credit_card import CreditCard, CreditCardStatus
from src.domain.models.credit_card_db import CreditCardDB, Base
from src.domain.ports.credit_card_repository_port import CreditCardRepositoryPort

class PostgresCreditCardRepositoryAdapter(CreditCardRepositoryPort):
    def __init__(self):
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("La variable de entorno DATABASE_URL no está configurada.")
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    def _get_db(self) -> Session:
        return self.SessionLocal()

    def save(self, card: CreditCard) -> CreditCard:
        db = self._get_db()
        db_card = CreditCardDB(**card.model_dump())
        db.add(db_card)
        db.commit()
        db.refresh(db_card)
        db.close()
        return CreditCard.model_from_db(db_card)

    def find_by_user_id(self, user_id: str) -> List[CreditCard]:
        db = self._get_db()
        db_cards = db.query(CreditCardDB).filter(CreditCardDB.userId == user_id).all()
        db.close()
        return [CreditCard.model_validate(c) for c in db_cards]

    def update_status(self, card_id: UUID, status: CreditCardStatus) -> Optional[CreditCard]:
        db = self._get_db()
        db_card = db.query(CreditCardDB).filter(CreditCardDB.id == card_id).first()
        if db_card:
            db_card.status = status
            db.commit()
            db.refresh(db_card)
            db.close()
            return CreditCard.model_validate(db_card)
        db.close()
        return None

    def find_by_last_four_digits(self, user_id: str, last_four: str) -> Optional[CreditCard]:
        db = self._get_db()
        db_card = db.query(CreditCardDB).filter(
            CreditCardDB.userId == user_id,
            CreditCardDB.lastFourDigits == last_four
        ).first()
        db.close()
        return CreditCard.from_orm(db_card) if db_card else None

    def count(self) -> int:
        db = self._get_db()
        count = db.query(CreditCardDB).count()
        db.close()
        return count

    def reset(self) -> None:
        db = self._get_db()
        db.query(CreditCardDB).delete()
        db.commit()
        db.close()