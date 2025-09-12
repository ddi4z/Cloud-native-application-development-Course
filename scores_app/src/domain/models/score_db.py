from sqlalchemy import Column
from sqlalchemy import String, orm, Float

Base = orm.declarative_base()


class ScoreDB(Base):
    __tablename__ = "scores"

    offer_id = Column(String, primary_key=True)
    value = Column(Float, nullable=False)