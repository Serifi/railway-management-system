from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class TrainStation(Base):
    __tablename__ = 'trainStation'

    stationID = Column(Integer, primary_key=True, autoincrement=True)
    stationName = Column(String, nullable=False)
    address = Column(String, nullable=False)

import os

DATABASE_URL = f"sqlite:///{os.path.abspath('server/db/track.db')}"

engine = create_engine(DATABASE_URL, echo=True)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
