"""
Populates the database with initial test data.
Run: python seed_db.py
"""

from datetime import datetime, timedelta
from models.employee import Employee, Session
from models.carriage import Carriage, Railcar, PassengerCar
from models.train import Train, TrainPassengerCars
from models.maintenance import Maintenance

def seed_db():
    session = Session()

    # -- Cleanup --
    session.query(Maintenance).delete()
    session.query(TrainPassengerCars).delete()
    session.query(Train).delete()
    session.query(Railcar).delete()
    session.query(PassengerCar).delete()
    session.query(Carriage).delete()
    session.query(Employee).delete()
    session.commit()

    # --- EMPLOYEES ---
    e1 = Employee(
        ssn="1234200101", firstName="John", lastName="Doe", password="pwd",
        department="Crew", role="Employee", username="john.doe"
    )
    e2 = Employee(
        ssn="1234200202", firstName="Jane", lastName="Smith", password="pwd",
        department="Maintenance", role="Admin", username="jane.smith"
    )
    e3 = Employee(
        ssn="1234200303", firstName="Max", lastName="Mustermann", password="pwd",
        department="Maintenance", role="Employee", username="max.mustermann"
    )
    session.add_all([e1, e2, e3])
    session.commit()

    # --- CARRIAGES ---
    c1 = Carriage(trackGauge="1435", type="Railcar")
    r1 = Railcar(carriage=c1, maxTractiveForce=100)
    session.add(r1)

    c2 = Carriage(trackGauge="1435", type="PassengerCar")
    p1 = PassengerCar(carriage=c2, numberOfSeats=50, maxWeight=40)
    session.add(p1)

    c3 = Carriage(trackGauge="1435", type="PassengerCar")
    p2 = PassengerCar(carriage=c3, numberOfSeats=80, maxWeight=60)
    session.add(p2)

    c4 = Carriage(trackGauge="1435", type="Railcar")
    r2 = Railcar(carriage=c4, maxTractiveForce=50)
    session.add(r2)

    c5 = Carriage(trackGauge="1000", type="Railcar")
    r3 = Railcar(carriage=c5, maxTractiveForce=70)
    session.add(r3)

    c6 = Carriage(trackGauge="1000", type="PassengerCar")
    p3 = PassengerCar(carriage=c6, numberOfSeats=40, maxWeight=30)
    session.add(p3)

    session.commit()

    # --- TRAINS ---
    t1 = Train(name="FastExpress", railcarID=r1.carriageID)  # uses railcar 1 (maxForce=100)
    session.add(t1)
    session.commit()
    session.execute(
        TrainPassengerCars.insert().values(
            trainID=t1.trainID, passengerCarID=p1.carriageID, position=1
        )
    )
    session.execute(
        TrainPassengerCars.insert().values(
            trainID=t1.trainID, passengerCarID=p2.carriageID, position=2
        )
    )
    session.commit()

    t2 = Train(name="LocalLine", railcarID=r2.carriageID)
    session.add(t2)
    session.commit()
    session.execute(
        TrainPassengerCars.insert().values(
            trainID=t2.trainID, passengerCarID=p1.carriageID, position=1
        )
    )
    session.commit()

    # --- MAINTENANCES ---
    m1 = Maintenance(
        employeeSSN=e1.ssn,
        trainID=t1.trainID,
        from_time=datetime.now(),
        to_time=datetime.now() + timedelta(hours=2)
    )
    session.add(m1)

    m2 = Maintenance(
        employeeSSN=e3.ssn,
        trainID=t1.trainID,
        from_time=datetime.now() + timedelta(days=1),
        to_time=datetime.now() + timedelta(days=1, hours=2)
    )
    session.add(m2)

    m3 = Maintenance(
        employeeSSN=e2.ssn,
        trainID=t2.trainID,
        from_time=datetime.now() + timedelta(hours=1),
        to_time=datetime.now() + timedelta(hours=3)
    )
    session.add(m3)

    session.commit()
    print("Database seeded with multiple employees, carriages, trains, and maintenances.")

if __name__ == "__main__":
    seed_db()