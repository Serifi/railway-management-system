from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Time(Base):
    __tablename__ = 'time'

    id = Column(Integer, primary_key=True, autoincrement=True)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)


class Maintenance(Base):
    __tablename__ = 'maintenance'

    id = Column(Integer, primary_key=True, autoincrement=True)
    trainID = Column(Integer, ForeignKey('train.trainID'), nullable=False)
    employeeID = Column(String, ForeignKey('employee.ssn'), nullable=False)
    timeID = Column(Integer, ForeignKey('time.id'), nullable=False)

    train = relationship("Train", backref="maintenances")
    employee = relationship("Employee", backref="maintenances")
    time = relationship("Time", backref="maintenances")
