from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .carriage import Carriage, Railcar, PassengerCar
from .train import Train, TrainPassengerCars
from .maintenance import Maintenance
from .employee import Employee
