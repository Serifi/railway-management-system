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

    train = relationship("Train", back_populates="maintenances")
    employee = relationship("Employee", back_populates="maintenances")

    @validates('to_time')
    def validate_time_order(self, key, value):
        if self.from_time and value <= self.from_time:
            raise ValueError("to_time must be after from_time")
        return value