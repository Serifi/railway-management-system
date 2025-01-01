import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

from routes import engine, SessionLocal
from models import Base
from models.employee import Employee, Department, Role
from models.carriage import Carriage, Railcar, PassengerCar
from models.train import Train, TrainPassengerCar
from models.maintenance import Maintenance

from datetime import datetime, timedelta
import random

def drop_and_create_tables():
    """Drops all tables and recreates them."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("All tables have been dropped and recreated.")

def generate_valid_ssn(existing_ssns):
    """
    Generates a valid Austrian SSN following this format:
    - First four digits: random from 0-9 (e.g., 5244)
    - Then two digits for the day (01-31) (e.g., 24)
    - Then two digits for the month (01-12) (e.g., 11)
    - Then two digits for the year (00-99) (e.g., 02)
    Example: 5244241102
    """
    while True:
        first_four = ''.join(str(random.randint(0, 9)) for _ in range(4))
        day = random.randint(1, 31)
        month = random.randint(1, 12)
        year = random.randint(0, 99)
        ssn = f"{first_four}{day:02d}{month:02d}{year:02d}"
        if ssn not in existing_ssns:
            existing_ssns.add(ssn)
            return ssn

def populate_employees(session):
    """Populates the Employee table with diverse and valid data."""
    employees = []
    existing_ssns = set()

    # Reserved SSNs for specific tests
    reserved_ssns = {
        "5244241102",
        "5244241103",
        "5244241104",
        "5244241105"
    }
    existing_ssns.update(reserved_ssns)

    # Create reserved employees
    reserved_employees = [
        Employee(
            ssn=ssn,
            firstName=f"TestFirst{i}",
            lastName=f"TestLast{i}",
            password=f"TestPass{i}!",
            department=Department.Maintenance if i % 2 == 0 else Department.Crew,
            role=Role.Employee,
            username=f"testuser{i}"
        )
        for i, ssn in enumerate(reserved_ssns, start=1)
    ]
    employees.extend(reserved_employees)

    # Create additional employees
    for i in range(len(reserved_employees) + 1, 21):  # Total of 20 employees
        ssn = generate_valid_ssn(existing_ssns)
        first_name = f"FirstName{i}"
        last_name = f"LastName{i}"
        password = f"Password{i}!"
        department = random.choice(list(Department))
        role = random.choice(list(Role))
        username = f"user{i}"

        emp = Employee(
            ssn=ssn,
            firstName=first_name,
            lastName=last_name,
            password=password,
            department=department,
            role=role,
            username=username
        )
        employees.append(emp)

    session.add_all(employees)
    print(f"{len(employees)} employees added.")

def populate_carriages(session):
    """Creates 10 Railcars and the corresponding PassengerCars."""
    railcars = []
    passenger_cars = []

    track_gauge_counts = {'1435': 0, '1000': 0}

    # Step 1: Create Railcars
    for _ in range(10):
        gauge = random.choice(['1435', '1000'])

        # Create the Carriage
        c = Carriage(
            trackGauge=gauge,
            type="Railcar"
        )
        # Create Railcar linked via relationship
        r = Railcar(
            carriage=c,
            maxTractiveForce=random.randint(1000, 5000)
        )
        session.add(c)
        session.add(r)

        railcars.append(r)
        track_gauge_counts[gauge] += 1

    # Step 2: Create PassengerCars (2 per Railcar) based on gauge counts
    for gauge, count in track_gauge_counts.items():
        for _ in range(count * 2):
            c = Carriage(
                trackGauge=gauge,
                type="PassengerCar"
            )
            p = PassengerCar(
                carriage=c,
                numberOfSeats=random.randint(50, 100),
                maxWeight=random.randint(500, 1500)
            )
            session.add(c)
            session.add(p)
            passenger_cars.append(p)

    session.flush()  # Flush after creating Carriage & Railcar/PassengerCar objects

    print(f"{len(railcars)} Railcars and {len(passenger_cars)} PassengerCars created.")

def calculate_total_weight(passenger_cars):
    """Calculates the total maxWeight of all PassengerCars."""
    return sum(pc.maxWeight for pc in passenger_cars)

def populate_trains(session):
    """
    Assigns 2 PassengerCars to each Train (Railcar)
    matching the same trackGauge and checks maxTractiveForce constraints.
    """
    railcars = session.query(Railcar).all()
    passenger_cars = session.query(PassengerCar).all()

    trains = []
    for rc in railcars:
        train = Train(
            name=f"Train{rc.carriageID}",
            railcarID=rc.carriageID
        )
        session.add(train)
        session.flush()  # Assign trainID

        gauge = rc.carriage.trackGauge
        compatible_pcs = [pc for pc in passenger_cars if pc.carriage.trackGauge == gauge]
        if len(compatible_pcs) < 2:
            print(f"Warning: Not enough PassengerCars with trackGauge {gauge} for Train {train.trainID}.")
            continue

        assigned = random.sample(compatible_pcs, 2)
        for idx, pc in enumerate(assigned, start=1):
            assoc = TrainPassengerCar(
                trainID=train.trainID,
                passengerCarID=pc.carriageID,
                position=idx
            )
            session.add(assoc)

        # Remove these PassengerCars from the pool
        for pc in assigned:
            passenger_cars.remove(pc)

        # Check maxTractiveForce
        total_w = calculate_total_weight(assigned)
        if total_w > rc.maxTractiveForce:
            print(f"Warning: Train {train.trainID} exceeds maxTractiveForce of {rc.maxTractiveForce}.")

        trains.append(train)

    session.flush()
    print(f"{len(trains)} Trains with their PassengerCars assigned.")

def populate_maintenances(session):
    """Populates the Maintenance table with valid data."""
    maintenance_employees = session.query(Employee).filter_by(department=Department.Maintenance).all()
    trains = session.query(Train).all()

    maintenances = []
    for _ in range(20):
        if not maintenance_employees or not trains:
            break
        emp = random.choice(maintenance_employees)
        trn = random.choice(trains)
        from_time = datetime.now() + timedelta(days=random.randint(-10, 10))
        to_time = from_time + timedelta(hours=random.randint(1, 5))

        m = Maintenance(
            employeeSSN=emp.ssn,
            trainID=trn.trainID,
            from_time=from_time,
            to_time=to_time
        )
        maintenances.append(m)

    session.add_all(maintenances)
    print(f"{len(maintenances)} Maintenance entries added.")

def populate():
    """Seeds the database with test data."""
    with SessionLocal() as session:
        drop_and_create_tables()

        # Order: Employees -> Carriages -> Trains -> Maintenances
        populate_employees(session)
        populate_carriages(session)
        populate_trains(session)
        populate_maintenances(session)

        session.commit()
    print("Database ready.")

if __name__ == "__main__":
    populate()