from sqlalchemy import Column, Integer, Float, String, ForeignKey
from models.Base import Base

class Section(Base):
    __tablename__ = 'section'
    sectionID = Column(Integer, primary_key=True, autoincrement=True)
    usageFee = Column(Float, nullable=False)
    length = Column(Float, nullable=False)
    maxSpeed = Column(Integer, nullable=False)
    trackGauge = Column(String, nullable=False)

    startStationID = Column(Integer, ForeignKey('trainStation.stationID'), nullable=False)
    endStationID = Column(Integer, ForeignKey('trainStation.stationID'), nullable=False)
