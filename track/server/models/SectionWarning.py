# Zwischentabelle für Abschnitte und Warnungen
from sqlalchemy import Table, Column, Integer, ForeignKey
from models.Base import Base

section_warning = Table(
    'section_warning',
    Base.metadata,
    Column('sectionID', Integer, ForeignKey('section.sectionID'), primary_key=True),
    Column('warningID', Integer, ForeignKey('warning.warningID'), primary_key=True)
)