# train.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, validates
from . import Base

class TrainPassengerCar(Base):
    __tablename__ = 'train_passenger_cars'

    trainID = Column(Integer, ForeignKey('train.trainID'), primary_key=True)
    passengerCarID = Column(Integer, ForeignKey('passenger_car.carriageID'), primary_key=True)
    position = Column(Integer, nullable=False)

    # Many-to-One relationships to Train and PassengerCar
    train = relationship("Train", back_populates="passenger_cars_associations")
    passenger_car = relationship("PassengerCar", back_populates="train_passenger_cars_associations")

class Train(Base):
    __tablename__ = 'train'

    trainID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    railcarID = Column(Integer, ForeignKey('railcar.carriageID'), nullable=False)

    # One-to-one with Railcar
    railcar = relationship("Railcar", back_populates="train", uselist=False)

    # One-to-many with the association class
    passenger_cars_associations = relationship(
        "TrainPassengerCar",
        back_populates="train",
        cascade="all, delete-orphan"
    )

    # One-to-many with Maintenance
    maintenances = relationship("Maintenance", back_populates="train", cascade="all, delete-orphan")

    @validates('name')
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("Train name must not be empty")
        return value.strip()

    @validates('railcarID')
    def validate_railcarID(self, key, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("railcarID must be a positive integer")
        return value