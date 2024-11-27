from sqlalchemy import Column, Integer, String, create_engine, Enum
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Employee(Base):
    __tablename__ = 'employee'

    ssn = Column(Integer, primary_key=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    password = Column(String, nullable=False)
    department = Column(Enum('Crew', 'Maintenance', name="department_enum"), nullable=False)
    role = Column(Enum('Admin', 'User', name="role_enum"), nullable=False)

import os

DATABASE_URL = f"sqlite:///{os.path.abspath('track/backend/db/track.db')}"

engine = create_engine(DATABASE_URL, echo=True)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
