# Modell für die Tabelle der Mitarbeiter in der Datenbank
from sqlalchemy import Column, String, Enum, UniqueConstraint
from sqlalchemy.orm import validates
import re
from models.Base import Base
from models.Department import Department
from models.Role import Role

class Employee(Base):
    __tablename__ = 'employee'

    # Spalten der Tabelle
    ssn = Column(String, primary_key=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    password = Column(String, nullable=False)
    department = Column(Enum(Department), nullable=False)
    role = Column(Enum(Role), nullable=False)
    username = Column(String, nullable=False, unique=True)

    # Benutzername eindeutig
    __table_args__ = (UniqueConstraint('username', name='unique_username'),)

    # Validierung für Sozialversicherungsnummer anhand österreichischer Richtlinien
    @validates('ssn')
    def validate_ssn(self, key, value):
        pattern = r"^\d{4}(0[1-9]|[12][0-9]|3[01])(0[1-9]|1[0-2])\d{2}$"
        if not re.match(pattern, str(value)):
            raise ValueError("Sozialversicherungsnummer ist ungültig")
        return value

    # Validierung für Vor- und Nachname
    @validates('firstName', 'lastName')
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("Vor- und Nachname dürfen nicht leer sein")
        return value.strip()