import re
from sqlalchemy import Column, String, Enum, UniqueConstraint
from sqlalchemy.orm import relationship, validates
import enum
from . import Base

class Role(enum.Enum):
    Admin = "Admin"
    Employee = "Employee"

class Department(enum.Enum):
    Crew = "Crew"
    Maintenance = "Maintenance"

class Employee(Base):
    __tablename__ = 'employee'

    ssn = Column(String, primary_key=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    password = Column(String, nullable=False)
    department = Column(Enum(Department), nullable=False)
    role = Column(Enum(Role), nullable=False)
    username = Column(String, unique=True, nullable=False)

    maintenances = relationship("Maintenance", back_populates="employee")

    __table_args__ = (
        UniqueConstraint('username', name='unique_username'),
    )

    @validates('firstName', 'lastName')
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError(f"{key} cannot be empty")
        return value.strip()

    @validates('ssn')
    def validate_ssn(self, key, value):
        pattern = r"^\d{4}(0[1-9]|[12][0-9]|3[01])(0[1-9]|1[0-2])\d{2}$"
        if not re.match(pattern, str(value)):
            raise ValueError("SSN does not match Austrian guidelines")
        return value