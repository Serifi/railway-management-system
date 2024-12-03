from sqlalchemy import Column, Integer, String
from models.Base import Base
from models.Section import Section

class Track(Base):
    __tablename__ = 'track'
    trackID = Column(Integer, primary_key=True)
    trackName = Column(String, nullable=False)

    def validate_section_sequence(self, section_ids, session):
        if len(section_ids) < 1:
            raise ValueError("Es muss mindestens eine Section angegeben werden, um eine Strecke zu bilden.")

        sections = session.query(Section).filter(Section.sectionID.in_(section_ids)).all()

        if len(sections) != len(section_ids):
            missing_ids = set(section_ids) - {s.sectionID for s in sections}
            raise ValueError(f"Folgende Sections existieren nicht: {missing_ids}")

        start_stations = {s.startStationID for s in sections}
        end_stations = {s.endStationID for s in sections}

        valid_start_stations = start_stations - end_stations
        if len(valid_start_stations) != 1:
            raise ValueError("Die Sections bilden keine gültige durchgängige Strecke. Kein eindeutiger Startpunkt gefunden.")

        valid_end_stations = end_stations - start_stations
        if len(valid_end_stations) != 1:
            raise ValueError("Die Sections bilden keine gültige durchgängige Strecke. Kein eindeutiger Endpunkt gefunden.")

        connected_stations = set()
        for section in sections:
            if section.startStationID in connected_stations or not connected_stations:
                connected_stations.add(section.startStationID)
                connected_stations.add(section.endStationID)
            elif section.endStationID in connected_stations:
                connected_stations.add(section.startStationID)
                connected_stations.add(section.endStationID)
            else:
                raise ValueError("Die Sections sind nicht vollständig verbunden.")

        return True