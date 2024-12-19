from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import validates
from models.Base import Base
from datetime import datetime

class Warning(Base):
    __tablename__ = 'warning'

    warningID = Column(Integer, primary_key=True, autoincrement=True)
    warningName = Column(String, nullable=False)
    description = Column(String, nullable=False)
    startDate = Column(DateTime, nullable=False)
    endDate = Column(DateTime, nullable=False)

    @validates('warningName')
    def validate_name(self, key, name):
        if not name or not name.strip():
            raise ValueError("Der Name der Warnung darf nicht leer sein.")
        return name.strip()

    @validates('startDate', 'endDate')
    def validate_dates(self, key, value):
        if not isinstance(value, datetime):
            raise ValueError(f"{key} muss ein gültiges Datum im Format 'YYYY-MM-DD HH:MM:SS' sein")

        if key == 'endDate':
            if self.startDate and value <= self.startDate:
                raise ValueError("Das Enddatum muss nach dem Startdatum liegen")

        return value