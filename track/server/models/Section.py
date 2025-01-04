from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import validates
from models.Base import Base
from models.TrainStation import TrainStation

class Section(Base):
    __tablename__ = 'section'

    sectionID = Column(Integer, primary_key=True, autoincrement=True)
    usageFee = Column(Float, nullable=False)
    length = Column(Float, nullable=False)
    maxSpeed = Column(Integer, nullable=False)
    trackGauge = Column(String, nullable=False)

    startStationID = Column(Integer, ForeignKey('trainStation.stationID'), nullable=False)
    endStationID = Column(Integer, ForeignKey('trainStation.stationID'), nullable=False)

    @validates('usageFee')
    def validate_usage_fee(self, key, value):
        if value <= 0:
            raise ValueError("Die Nutzungsgebühr muss größer als 0 sein")
        return value

    @validates('length')
    def validate_length(self, key, value):
        if value <= 0:
            raise ValueError("Die Distanz muss größer als 0 sein")
        return value

    @validates('maxSpeed')
    def validate_max_speed(self, key, value):
        if value <= 0:
            raise ValueError("Die maximale Geschwindigkeit muss größer als 0 sein")
        return value

    @validates('trackGauge')
    def validate_track_gauge(self, key, value):
        if value not in ['1000', '1435']:
            raise ValueError("Die Spurweite ist ungültig. Erlaubte Werte sind '1000' oder '1435'")
        return value

def validate_station(session, key, value, start_station_id=None):
    station = session.query(TrainStation).filter(TrainStation.stationID == value).first()
    if not station:
        raise ValueError(f"Bahnhof mit ID {value} existiert nicht")

    if key == 'endStationID' and value == start_station_id:
        raise ValueError("Start- und Endbahnhof dürfen nicht identisch sein")
    return value