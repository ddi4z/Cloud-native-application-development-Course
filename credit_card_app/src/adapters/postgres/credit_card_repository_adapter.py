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

    def _to_domain(self, db_card: CreditCardDB) -> CreditCard:
        return CreditCard.model_validate(db_card, from_attributes=True)

    def save(self, card: CreditCard) -> CreditCard:
        db = self._get_db()
        try:
            db_card = CreditCardDB(**card.model_dump())
            db.add(db_card)
            db.commit()
            db.refresh(db_card)
            return self._to_domain(db_card)
        finally:
            db.close()

    def find_by_user_id(self, user_id: str) -> List[CreditCard]:
        db = self._get_db()
        try:
            db_cards = db.query(CreditCardDB).filter(CreditCardDB.userId == user_id).all()
            return [self._to_domain(c) for c in db_cards]
        finally:
            db.close()

    def update_status(self, card_id: str, status: CreditCardStatus) -> Optional[CreditCard]:
        db = self._get_db()
        try:
            db_card = db.query(CreditCardDB).filter(CreditCardDB.id == str(card_id)).first()
            if not db_card:
                return None
            db_card.status = status
            db.commit()
            db.refresh(db_card)
            return self._to_domain(db_card)
        finally:
            db.close()

    def find_by_last_four_digits(self, user_id: str, last_four: str) -> Optional[CreditCard]:
        db = self._get_db()
        try:
            db_card = db.query(CreditCardDB).filter(
                CreditCardDB.userId == user_id,
                CreditCardDB.lastFourDigits == last_four
            ).first()
            return self._to_domain(db_card) if db_card else None
        finally:
            db.close()

    def count(self) -> int:
        db = self._get_db()
        try:
            return db.query(CreditCardDB).count()
        finally:
            db.close()

    def reset(self) -> None:
        db = self._get_db()
        try:
            db.query(CreditCardDB).delete()
            db.commit()
        finally:
            db.close()
