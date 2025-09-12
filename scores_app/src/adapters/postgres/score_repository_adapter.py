import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.models.score_request import ScoreRequest
from src.domain.models.score_db import Base, ScoreDB
from src.errors import (
    InvalidSizeError,
)

load_dotenv()


class PostgresScoreRepositoryAdapter:
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

    def calculate(self, score_request: ScoreRequest) -> int:
        """calculates offer's score"""
        with self._get_session() as db:
            percentage_per_size = {
                "VOLUMINOSO": 1,
                "LARGE": 1,
                "MEDIANO": 0.5,
                "MEDIUM": 0.5,
                "PEQUEÑO": 0.25,
                "SMALL": 0.25,
            }

            percentage = percentage_per_size.get(score_request.size.upper(), 0)
            if percentage == 0:
                raise InvalidSizeError(f"Size '{score_request.size.upper()}' is not valid.")

            calculated_value = score_request.amount_offered - (percentage * score_request.baggage_value)

        
            orm_score = db.query(ScoreDB).filter(ScoreDB.offer_id == score_request.offer_id).first()

            if orm_score:
                orm_score.value = calculated_value
            else:
                orm_score = ScoreDB(
                    offer_id=score_request.offer_id,
                    value=calculated_value,
                )
                db.add(orm_score)

            db.commit()
            db.refresh(orm_score)
            return calculated_value
