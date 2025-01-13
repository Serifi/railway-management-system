# Modell für die Tabelle der Strecken in der Datenbank
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import validates
from models.Base import Base
from models.Section import Section

class Track(Base):
    __tablename__ = 'track'

    # Spalten der Tabelle
    trackID = Column(Integer, primary_key=True)
    trackName = Column(String, nullable=False)

    # Validierung für den Streckennamen
    @validates('trackName')
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("Der Streckenname darf nicht leer sein")
        return value.strip()

    # Validierung der Abschnittsreihenfolge für eine Strecke
    def validate_section_sequence(self, section_ids, session):
        # Überprüfung, ob mindestens ein Abschnitt angegeben wurde
        if len(section_ids) < 1:
            raise ValueError("Es muss mindestens ein Abschnitt angegeben werden, um eine Strecke zu bilden")

        # Überprüfung, ob alle Abschnitte existieren
        sections = session.query(Section).filter(Section.sectionID.in_(section_ids)).all()
        if len(sections) != len(section_ids):
            missing_ids = set(section_ids) - {s.sectionID for s in sections}
            raise ValueError(f"Folgende Abschnitte existieren nicht: {missing_ids}")

        # Überprüfung, ob alle Abschnitte dieselbe Spurweite haben
        track_gauges = {section.trackGauge for section in sections}
        if len(track_gauges) > 1:
            raise ValueError("Die Spurweiten der gewählten Abschnitte stimmen nicht überein")

        # Überprüfung der Start- und Endstationen der Abschnitte
        start_stations = {s.startStationID for s in sections}
        end_stations = {s.endStationID for s in sections}

        # Überprüfung, ob es genau eine gültige Startstation gibt
        valid_start_stations = start_stations - end_stations
        if len(valid_start_stations) != 1:
            raise ValueError("Die Abschnitte bilden keine gültige durchgängige Strecke")

        # Überprüfung, ob es genau eine gültige Endstation gibt
        valid_end_stations = end_stations - start_stations
        if len(valid_end_stations) != 1:
            raise ValueError("Die Abschnitte bilden keine gültige durchgängige Strecke")

        # Überprüfung, ob die Abschnitte vollständig verbunden sind
        connected_stations = set()
        for section in sections:
            if section.startStationID in connected_stations or not connected_stations:
                connected_stations.add(section.startStationID)
                connected_stations.add(section.endStationID)
            elif section.endStationID in connected_stations:
                connected_stations.add(section.startStationID)
                connected_stations.add(section.endStationID)
            else:
                raise ValueError("Die Abschnitte sind nicht vollständig verbunden")

        return True