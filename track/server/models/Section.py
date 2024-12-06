from sqlalchemy import Column, Integer, Float, String, ForeignKey
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

    def validate_usage_fee(self, value):
        if value <= 0:
            raise ValueError("Nutzungsgebühr muss größer als 0 sein")
        return value

    def validate_length(self, value):
        if value <= 0:
            raise ValueError("Länge muss größer als 0 sein")
        return value

    def validate_max_speed(self, value):
        if value <= 0:
            raise ValueError("Maximale Geschwindigkeit muss größer als 0 sein")
        return value

    def validate_track_gauge(self, value):
        if value not in ['1000', '1435']:
            raise ValueError("Ungültiger Wert für 'trackGauge'. Erlaubte Werte sind '1000' oder '1435'")
        return value

    def validate_stations(self, key, value, session):
        station = session.query(TrainStation).filter(TrainStation.stationID == value).first()
        if not station:
            raise ValueError(f"Bahnhof mit ID {value} existiert nicht")

        if key == 'endStationID' and value == self.startStationID:
            raise ValueError("Start- und Endbahnhof dürfen nicht identisch sein")

        return value