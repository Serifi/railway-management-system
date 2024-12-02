from sqlalchemy import Column, Integer, String
from models.Base import Base

class Track(Base):
    __tablename__ = 'track'
    trackID = Column(Integer, primary_key=True, autoincrement=True)
    trackName = Column(String, nullable=False)