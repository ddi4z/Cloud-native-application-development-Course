import os
from typing import List, Optional
from uuid import UUID

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Integer, DateTime, UUID as PG_UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from routes_app.domain.models.models import Trayecto
from routes_app.domain.ports.routes_repository_port import RoutesRepositoryPort
from routes_app.errors import TrayectoNotFoundError, FlightIdAlreadyExistsError

load_dotenv()

# Definición de Base de Datos
Base = declarative_base()

class TrayectoDB(Base):
    """Modelo ORM que representa la tabla 'trayectos' en la base de datos."""
    __tablename__ = 'trayectos'
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True)
    flightId = Column(String, unique=True, index=True, nullable=False)
    sourceAirportCode = Column(String, nullable=False)
    sourceCountry = Column(String, nullable=False)
    destinyAirportCode = Column(String, nullable=False)
    destinyCountry = Column(String, nullable=False)
    bagCost = Column(Integer, nullable=False)
    plannedStartDate = Column(DateTime(timezone=True), nullable=False)
    plannedEndDate = Column(DateTime(timezone=True), nullable=False)
    createdAt = Column(DateTime(timezone=True), nullable=False)
    updatedAt = Column(DateTime(timezone=True), nullable=False)

# Implementación del adaptador
class PostgresRoutesRepositoryAdapter(RoutesRepositoryPort):
    """Implementación de PostgreSQL del repositorio de Trayectos usando SQLAlchemy."""
    def __init__(self):
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("La variable de entorno DATABASE_URL no está configurada.")
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    def _get_session(self) -> Session:
        return self.SessionLocal()

    def _to_domain(self, db_obj: TrayectoDB) -> Trayecto:
        return Trayecto.model_validate(db_obj.__dict__)

    def create(self, trayecto: Trayecto) -> Trayecto:
        """Crea un nuevo registro de Trayecto, lanzando un error si el flightId ya existe."""
        db_obj = TrayectoDB(**trayecto.model_dump())
        with self._get_session() as db:
            try:
                db.add(db_obj)
                db.commit()
                db.refresh(db_obj)
            except IntegrityError:
                db.rollback()
                raise FlightIdAlreadyExistsError(f"El flightId '{trayecto.flightId}' ya existe.")
        return self._to_domain(db_obj)

    def get(self, trayecto_id: UUID) -> Trayecto:
        """Obtiene un Trayecto por su ID, lanzando un error si no se encuentra."""
        with self._get_session() as db:
            db_obj = db.query(TrayectoDB).filter(TrayectoDB.id == trayecto_id).first()
            if not db_obj:
                raise TrayectoNotFoundError(f"Trayecto con id '{trayecto_id}' no encontrado.")
            return self._to_domain(db_obj)

    def list(self) -> List[Trayecto]:
        """Retorna una lista de todos los Trayectos."""
        with self._get_session() as db:
            db_objs = db.query(TrayectoDB).all()
            return [self._to_domain(db_obj) for db_obj in db_objs]

    def delete(self, trayecto_id: UUID) -> bool:
        """Elimina un Trayecto por su ID, lanzando un error si no se encuentra."""
        with self._get_session() as db:
            db_obj = db.query(TrayectoDB).filter(TrayectoDB.id == trayecto_id).first()
            if not db_obj:
                raise TrayectoNotFoundError(f"Trayecto con id '{trayecto_id}' no encontrado.")
            db.delete(db_obj)
            db.commit()
            return True

    def get_by_flight_id(self, flight_id: str) -> Trayecto:
        """Obtiene un Trayecto por su flightId, lanzando un error si no se encuentra."""
        with self._get_session() as db:
            db_obj = db.query(TrayectoDB).filter(TrayectoDB.flightId == flight_id).first()
            if not db_obj:
                raise TrayectoNotFoundError(f"Trayecto con flightId '{flight_id}' no encontrado.")
            return self._to_domain(db_obj)

    def count(self) -> int:
        """Cuenta el número total de Trayectos."""
        with self._get_session() as db:
            return db.query(TrayectoDB).count()
            
    def reset(self) -> None:
        """Elimina todos los registros de la tabla de Trayectos."""
        with self._get_session() as db:
            db.query(TrayectoDB).delete()
            db.commit()

    def update(self, trayecto: Trayecto) -> Trayecto:
        """Actualiza un registro de Trayecto, lanzando un error si no se encuentra."""
        with self._get_session() as db:
            db_obj = db.query(TrayectoDB).filter(TrayectoDB.id == trayecto.id).first()
            if not db_obj:
                raise TrayectoNotFoundError(f"Trayecto con id '{trayecto.id}' no encontrado para actualizar.")
            
            update_data = trayecto.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
            return self._to_domain(db_obj)