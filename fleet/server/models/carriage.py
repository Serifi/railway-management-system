from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Carriage(Base):
    __tablename__ = 'carriage'

    carriageID = Column(Integer, primary_key=True, autoincrement=True)
    trackGauge = Column(String, nullable=False)
    type = Column(String, nullable=False)