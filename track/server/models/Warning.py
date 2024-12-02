from sqlalchemy import Column, Integer, String, Date
from models.Base import Base

class Warning(Base):
    __tablename__ = 'warning'

    warningID = Column(Integer, primary_key=True, autoincrement=True)
    warningName = Column(String, nullable=False)
    description = Column(String, nullable=False)
    startDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)