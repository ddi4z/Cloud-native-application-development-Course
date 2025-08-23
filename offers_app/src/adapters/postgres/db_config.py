import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv(
    "CONNECTION_STRING", "postgresql+psycopg2://User:Password@localhost:5432/offers_db"
)

engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def init_db():
    """Inicializa la base de datos creando las tablas"""

    Base.metadata.create_all(bind=engine)
