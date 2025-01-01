import re, os
from sqlalchemy import Column, String, Enum, UniqueConstraint, create_engine
from sqlalchemy.orm import sessionmaker, validates
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
    username = Column(String, nullable=False, unique=True)

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

    def generate_username(self):
        if not self.firstName or not self.lastName:
            raise ValueError("First/Last name required to generate username")
        self.username = f"{self.firstName.lower()}.{self.lastName.lower()}"