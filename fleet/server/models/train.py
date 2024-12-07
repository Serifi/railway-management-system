from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Train(Base):
    __tablename__ = 'train'

    trainID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    railcarID = Column(Integer, ForeignKey('railcar.carriageID'), nullable=False)
    railcar = relationship("Railcar", backref="train", uselist=False)

    passenger_cars = relationship(
        "PassengerCar",
        secondary="train_passenger_cars",
        backref="trains"
    )

class TrainPassengerCars(Base):
    __tablename__ = 'train_passenger_cars'

    trainID = Column(Integer, ForeignKey('train.trainID'), primary_key=True)
    passengerCarID = Column(Integer, ForeignKey('passenger_car.carriageID'), primary_key=True)