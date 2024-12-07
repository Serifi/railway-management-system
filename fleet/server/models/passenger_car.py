from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class PassengerCar(Base):
    __tablename__ = 'passenger_car'

    carriageID = Column(Integer, ForeignKey('carriage.carriageID'), primary_key=True)
    numberOfSeats = Column(Integer, nullable=False)
    maxWeight = Column(Integer, nullable=False)
    carriage = relationship("Carriage", backref="passenger_car")