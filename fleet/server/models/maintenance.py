from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, validates
from . import Base

class Maintenance(Base):
    __tablename__ = 'maintenance'

    maintenanceID = Column(Integer, primary_key=True, autoincrement=True)
    employeeSSN = Column(String, ForeignKey('employee.ssn'), nullable=False)
    trainID = Column(Integer, ForeignKey('train.trainID'), nullable=False)
    from_time = Column(DateTime, nullable=False)
    to_time = Column(DateTime, nullable=False)

    # One-to-many relationship with Train and Employee
    train = relationship("Train", back_populates="maintenances")
    employee = relationship("Employee", back_populates="maintenances")