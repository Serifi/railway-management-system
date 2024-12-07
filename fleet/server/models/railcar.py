from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Railcar(Base):
    __tablename__ = 'railcar'

    carriageID = Column(Integer, ForeignKey('carriage.carriageID'), primary_key=True)
    maxTractiveForce = Column(Integer, nullable=False)
    carriage = relationship("Carriage", backref="railcar")