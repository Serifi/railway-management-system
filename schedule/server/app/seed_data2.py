from . import app, db
from app.models import Stopplan, Section, Track, TrainStation, Employee, Department, Role, RideExecution, Train

with app.app_context():
    db.create_all()

    # Erstelle TrainStations
    station1 = TrainStation(name='Station 1', address='123 Main St')
    station2 = TrainStation(name='Station 2', address='456 Elm St')
    station3 = TrainStation(name='Station 3', address='789 Oak St')
    station4 = TrainStation(name='Station 4', address='101 Pine St')

    db.session.add_all([station1, station2, station3, station4])
    db.session.commit()

    # Erstelle Sections mit Start- und Endstationen
    section1 = Section(
        usageFee=10.0, length=100.0, maxSpeed=120.0, trackGauge=1435,
        start_station=station1, end_station=station2
    )
    section2 = Section(
        usageFee=15.0, length=120.0, maxSpeed=130.0, trackGauge=1435,
        start_station=station2, end_station=station3
    )
    section3 = Section(
        usageFee=12.0, length=150.0, maxSpeed=110.0, trackGauge=1435,
        start_station=station3, end_station=station4
    )
    section4 = Section(
        usageFee=8.0, length=130.0, maxSpeed=140.0, trackGauge=1435,
        start_station=station4, end_station=station1
    )

    db.session.add_all([section1, section2, section3, section4])
    db.session.commit()

    # Erstelle Tracks und füge Sections hinzu
    track1 = Track(name='Track A', sections=[section1, section2])
    track2 = Track(name='Track B', sections=[section3, section4])

    db.session.add_all([track1, track2])
    db.session.commit()


    stopplan1 = Stopplan(
        name='Linz-Wien',
        minPrice=8.5,
        track=track1,
        trainStations=[station1, station2, station3],

    )
    stopplan2 = Stopplan(
        name='Linz-Salzburg',
        minPrice=10.5,
        track=track2,
        trainStations=[station3, station4],

    )

    db.session.add_all([stopplan1, stopplan2])
    db.session.commit()


    # Erstelle Employees
    employee1 = Employee(
        ssn='123-45-6789',
        firstName='Anna',
        lastName='Müller',
        password='passwort123',
        department=Department.Crew,
        role=Role.Employee,
        username='amueller'
    )
    employee2 = Employee(
        ssn='987-65-4321',
        firstName='Max',
        lastName='Schmidt',
        password='passwort456',
        department=Department.Maintenance,
        role=Role.Admin,
        username='mschmidt'
    )
    employee3 = Employee(
        ssn='555-44-3333',
        firstName='Julia',
        lastName='Weber',
        password='passwort789',
        department=Department.Crew,
        role=Role.Employee,
        username='jweber'
    )

    db.session.add_all([employee1, employee2, employee3])
    db.session.commit()

    # Erstelle Trains
    train1 = Train(name='ICE 123')
    train2 = Train(name='Railjet 456')
    train3 = Train(name='IC 789')

    db.session.add_all([train1, train2, train3])
    db.session.commit()

    # Erstelle RideExecutions
    from datetime import date, time

    ride_execution1 = RideExecution(
        price=25.0,
        isCanceled=False,
        delay=2,
        date=date(2024, 6, 20),
        time=time(14, 30),
        stopplan=stopplan1,
        train=train1,
        employees=[employee1, employee3]
    )

    ride_execution2 = RideExecution(
        price=30.0,
        isCanceled=False,
        delay=0,
        date=date(2024, 6, 21),
        time=time(16, 45),
        stopplan=stopplan2,
        train=train2,
        employees=[employee2]
    )

    db.session.add_all([ride_execution1, ride_execution2])
    db.session.commit()

    print("Mockdaten erfolgreich erstellt!")

