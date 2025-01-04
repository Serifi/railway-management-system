from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .carriage import Carriage, Railcar, PassengerCar
from .employee import Employee
from .maintenance import Maintenance
from .train import Train