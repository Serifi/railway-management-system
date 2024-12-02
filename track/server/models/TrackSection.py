from sqlalchemy import Table, Column, Integer, ForeignKey
from models.Base import Base

track_section = Table(
    'track_section',
    Base.metadata,
    Column('trackID', Integer, ForeignKey('track.trackID'), primary_key=True),
    Column('sectionID', Integer, ForeignKey('section.sectionID'), primary_key=True)
)