from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from . import Base

class Maintenance(Base):
    __tablename__ = 'maintenance'

    maintenanceID = Column(Integer, primary_key=True, autoincrement=True)
    employeeSSN = Column(String, ForeignKey('employee.ssn'), nullable=False)
    trainID = Column(Integer, ForeignKey('train.trainID'), nullable=False)
    from_time = Column(TIMESTAMP, nullable=False)
    to_time = Column(TIMESTAMP, nullable=False)

    employee = relationship("Employee", backref="maintenances")
    train = relationship("Train", backref="maintenances")