# Modell für die Tabelle der Warnungen in der Datenbank
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import validates
from models.Base import Base
from datetime import datetime, timezone

class Warning(Base):
    __tablename__ = 'warning'

    # Spalten der Tabelle
    warningID = Column(Integer, primary_key=True, autoincrement=True)
    warningName = Column(String, nullable=False)
    description = Column(String, nullable=False)
    startDate = Column(DateTime, nullable=False)
    endDate = Column(DateTime, nullable=True)

    # Überprüfung des Namens der Warnung
    @validates('warningName')
    def validate_name(self, key, name):
        if not name or not name.strip():
            raise ValueError("Der Name der Warnung darf nicht leer sein")
        return name.strip()

    # Überprüfung, ob Startdatum in der Zukunft liegt
    @validates('startDate')
    def validate_start_date(self, key, value):
        now = datetime.now(timezone.utc)
        if not value:
            raise ValueError("Das Startdatum darf nicht leer sein")
        if value < now:
            raise ValueError("Das Startdatum muss in der Zukunft liegen")
        return value

    # Überprüfung, ob Enddatum nach Startdatum ist
    @validates('endDate')
    def validate_end_date(self, key, value):
        if value is None:
            return value
        if not self.startDate:
            raise ValueError("Das Startdatum muss zuerst gesetzt sein, bevor das Enddatum validiert wird")
        if value <= self.startDate:
            raise ValueError("Das Enddatum muss nach dem Startdatum liegen")
        return value