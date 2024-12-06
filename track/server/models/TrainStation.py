from sqlalchemy import Column, Integer, String
from models.Base import Base

class TrainStation(Base):
    __tablename__ = 'trainStation'
    stationID = Column(Integer, primary_key=True, autoincrement=True)
    stationName = Column(String, nullable=False)
    address = Column(String, nullable=False)