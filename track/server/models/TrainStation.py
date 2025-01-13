# Modell für die Tabelle der Bahnhöfe in der Datenbank
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import validates
import re
from models.Base import Base

class TrainStation(Base):
    __tablename__ = 'trainStation'

    # Spalten der Tabelle
    stationID = Column(Integer, primary_key=True, autoincrement=True)
    stationName = Column(String, unique=True, nullable=False)
    address = Column(String, nullable=False)

    # Validierung für den Bahnhofsnamen
    @validates('stationName')
    def validate_station_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("Der Name des Bahnhofs darf nicht leer sein")
        pattern = r"^[a-zA-ZäöüÄÖÜß\s.]+(?:Bahnhof|bahnhof).*$"
        if not re.match(pattern, value):
            raise ValueError("Der Name des Bahnhofs ist ungültig")
        return value.strip()

    # Validierung für die Adresse
    @validates('address')
    def validate_address(self, key, value):
        pattern = r"^[a-zA-ZäöüÄÖÜß\s.\-']+\s\d+(-\d+)?,\s\d{4}\s[a-zA-ZäöüÄÖÜß\s.\-']+$"
        if not re.match(pattern, value):
            raise ValueError("Die Adresse muss das Format 'Straße Nummer, PLZ Ort' haben")
        return value.strip()