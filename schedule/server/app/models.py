import enum

from . import db

track_section = db.Table('track_section',
    db.Column('track_id', db.Integer, db.ForeignKey('tracks.id'), primary_key=True),
    db.Column('section_id', db.Integer, db.ForeignKey('sections.id'), primary_key=True)
)

trainStation_stopplan = db.Table('trainStation_stopplan',
    db.Column('trainStation_id', db.Integer, db.ForeignKey('trainStations.id'), primary_key=True),
    db.Column('stopplan_id', db.Integer, db.ForeignKey('stopplans.id'), primary_key=True)
)

section_warning = db.Table('section_warning',
    db.Column('section_id', db.Integer, db.ForeignKey('sections.id'), primary_key=True),
    db.Column('warning_id', db.Integer, db.ForeignKey('warnings.id'), primary_key=True)
)

class Warning(db.Model):
    __tablename__ = 'warnings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    startDate = db.Column(db.DateTime, nullable=False)
    endDate = db.Column(db.DateTime, nullable=False)

    sections = db.relationship('Section', secondary=section_warning, back_populates='warnings')


class TrainStation(db.Model):
    __tablename__ = 'trainStations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)

    stopplans = db.relationship('Stopplan', secondary=trainStation_stopplan, back_populates='trainStations')

    start_sections = db.relationship('Section', foreign_keys='Section.start_station_id', back_populates='start_station')
    end_sections = db.relationship('Section', foreign_keys='Section.end_station_id', back_populates='end_station')


class Section(db.Model):
    __tablename__ = 'sections'
    id = db.Column(db.Integer, primary_key=True)
    usageFee = db.Column(db.Float, nullable=False)
    length = db.Column(db.Float, nullable=False)
    maxSpeed = db.Column(db.Float, nullable=False)
    trackGauge = db.Column(db.Integer, nullable=False)

    tracks = db.relationship('Track', secondary=track_section, back_populates='sections')
    warnings = db.relationship('Warning', secondary=section_warning, back_populates='sections')

    start_station_id = db.Column(db.Integer, db.ForeignKey('trainStations.id'), nullable=False)
    end_station_id = db.Column(db.Integer, db.ForeignKey('trainStations.id'), nullable=False)

    start_station = db.relationship('TrainStation', foreign_keys=[start_station_id], back_populates='start_sections')
    end_station = db.relationship('TrainStation', foreign_keys=[end_station_id], back_populates='end_sections')


class Track(db.Model):
    __tablename__ = 'tracks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100) , nullable=False)

    sections = db.relationship('Section', secondary=track_section, back_populates='tracks')
    stopplans = db.relationship('Stopplan', back_populates='track')

class Stopplan(db.Model):
    __tablename__= 'stopplans'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    minPrice = db.Column(db.Float, nullable=True)

    trackID = db.Column(db.Integer, db.ForeignKey('tracks.id'), nullable=False)
    track = db.relationship('Track', back_populates='stopplans')
    trainStations = db.relationship('TrainStation', secondary=trainStation_stopplan ,back_populates='stopplans')
    rideExecutions = db.relationship('RideExecution', back_populates='stopplan')

class Role(enum.Enum):
    Admin = "Admin"
    Employee = "Employee"

class Department(enum.Enum):
    Crew = "Crew"
    Maintenance = "Maintenance"


execution_employee= db.Table('execution_employee',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('execution_id', db.Integer, db.ForeignKey('rideExecutions.id')),
    db.Column('employee_ssn', db.Integer, db.ForeignKey('employees.ssn'))
)


class Employee(db.Model):
    __tablename__ = 'employees'

    ssn = db.Column(db.String, primary_key=True)
    firstName = db.Column(db.String, nullable=False)
    lastName = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    department = db.Column(db.Enum(Department), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)

    rideExecutions = db.relationship('RideExecution', secondary=execution_employee, back_populates='employees')

class Train(db.Model):
    __tablename__ = 'trains'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    rideExecutions = db.relationship('RideExecution', back_populates='train')

class RideExecution(db.Model):
    __tablename__ = 'rideExecutions'
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=True)
    isCanceled = db.Column(db.Boolean, nullable=True)
    delay = db.Column(db.Integer, nullable=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)

    stopplanID = db.Column(db.Integer, db.ForeignKey('stopplans.id'), nullable=False)
    stopplan = db.relationship('Stopplan', back_populates='rideExecutions')
    trainID = db.Column(db.Integer, db.ForeignKey('trains.id'), nullable=False)
    train = db.relationship('Train', back_populates='rideExecutions')
    employees = db.relationship('Employee', secondary=execution_employee, back_populates='rideExecutions')