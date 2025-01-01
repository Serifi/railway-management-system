from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from . import Base

class Carriage(Base):
    __tablename__ = 'carriage'

    carriageID = Column(Integer, primary_key=True, autoincrement=True)
    trackGauge = Column(String, nullable=False)
    type = Column(String, nullable=False)

class Railcar(Base):
    __tablename__ = 'railcar'

    carriageID = Column(Integer, ForeignKey('carriage.carriageID'), primary_key=True)
    maxTractiveForce = Column(Integer, nullable=False)
    carriage = relationship("Carriage", backref="railcar")

class PassengerCar(Base):
    __tablename__ = 'passenger_car'

    carriageID = Column(Integer, ForeignKey('carriage.carriageID'), primary_key=True)
    numberOfSeats = Column(Integer, nullable=False)
    maxWeight = Column(Integer, nullable=False)
    carriage = relationship("Carriage", backref="passenger_car")