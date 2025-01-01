from sqlalchemy import Column, Integer, String, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from . import Base

TrainPassengerCars = Table(
    'train_passenger_cars',
    Base.metadata,
    Column('trainID', Integer, ForeignKey('train.trainID'), primary_key=True),
    Column('passengerCarID', Integer, ForeignKey('passenger_car.carriageID'), primary_key=True),
    Column('position', Integer, nullable=False),
    UniqueConstraint('trainID', 'position', name='unique_position_per_train')
)

class Train(Base):
    __tablename__ = 'train'

    trainID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    railcarID = Column(Integer, ForeignKey('railcar.carriageID'), nullable=False)

    railcar = relationship("Railcar", backref="train", uselist=False)
    passenger_cars = relationship(
        "PassengerCar",
        secondary=TrainPassengerCars,
        backref="trains",
        lazy="subquery"
    )