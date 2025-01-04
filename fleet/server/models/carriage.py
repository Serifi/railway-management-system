# carriage.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, validates
from . import Base

class Carriage(Base):
    __tablename__ = 'carriage'

    carriageID = Column(Integer, primary_key=True, autoincrement=True)
    trackGauge = Column(String, nullable=False)
    type = Column(String, nullable=False)

    @validates('trackGauge')
    def validate_trackGauge(self, key, value):
        if value not in ['1435', '1000']:
            raise ValueError("trackGauge must be '1435' or '1000'")
        return value

    @validates('type')
    def validate_type(self, key, value):
        if value not in ["Railcar", "PassengerCar"]:
            raise ValueError("type must be 'Railcar' or 'PassengerCar'")
        return value

class Railcar(Base):
    __tablename__ = 'railcar'

    carriageID = Column(Integer, ForeignKey('carriage.carriageID'), primary_key=True)
    maxTractiveForce = Column(Integer, nullable=False)

    carriage = relationship("Carriage", back_populates="railcar_detail", uselist=False)
    train = relationship("Train", back_populates="railcar", uselist=False)

    @validates('maxTractiveForce')
    def validate_maxTractiveForce(self, key, value):
        if value <= 0:
            raise ValueError("maxTractiveForce must be positive")
        return value

class PassengerCar(Base):
    __tablename__ = 'passenger_car'

    carriageID = Column(Integer, ForeignKey('carriage.carriageID'), primary_key=True)
    numberOfSeats = Column(Integer, nullable=False)
    maxWeight = Column(Integer, nullable=False)

    carriage = relationship("Carriage", back_populates="passenger_car_detail", uselist=False)
    train_passenger_cars_associations = relationship(
        "TrainPassengerCar",
        back_populates="passenger_car",
        cascade="all, delete-orphan"
    )

    @validates('numberOfSeats')
    def validate_numberOfSeats(self, key, value):
        if value <= 0:
            raise ValueError("numberOfSeats must be positive")
        return value

    @validates('maxWeight')
    def validate_maxWeight(self, key, value):
        if value <= 0:
            raise ValueError("maxWeight must be positive")
        return value

Carriage.railcar_detail = relationship("Railcar", back_populates="carriage", uselist=False)
Carriage.passenger_car_detail = relationship("PassengerCar", back_populates="carriage", uselist=False)