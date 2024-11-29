from sqlalchemy import Column, Integer, String, create_engine, Enum, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, validates
import re
import os

from models.Role import Role
from models.Department import Department

Base = declarative_base()

class Employee(Base):
    __tablename__ = 'employee'

    ssn = Column(String, primary_key=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    password = Column(String, nullable=False)
    department = Column(Enum(Department), nullable=False)
    role = Column(Enum(Role), nullable=False)
    username = Column(String, nullable=False, unique=True)

    __table_args__ = (UniqueConstraint('username', name='unique_username'),)

    @validates('firstName', 'lastName')
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError(f"{key} darf nicht leer sein")
        return value.strip()

    @validates('ssn')
    def validate_ssn(self, key, value):
        pattern = r"^\d{4}(0[1-9]|[12][0-9]|3[01])(0[1-9]|1[0-2])\d{2}$"
        if not re.match(pattern, str(value)):
            raise ValueError("SSN entspricht nicht den österreichischen Richtlinien")
        return value

    def generate_username(self):
        if not self.firstName or not self.lastName:
            raise ValueError("Vorname und Nachname müssen gesetzt sein, um einen Benutzernamen zu generieren")
        self.username = f"{self.firstName.lower()}.{self.lastName.lower()}"

DATABASE_URL = f"sqlite:///{os.path.abspath('server/db/fleet.db')}"
engine = create_engine(DATABASE_URL, echo=True)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)