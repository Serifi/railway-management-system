"""
tests/test_trains.py

Automated tests for train_routes with extended checks:
 - Weak railcar constraint
 - Track gauge constraint
 - Delete train with maintenance
"""

import pytest
from app import app
from datetime import datetime, timedelta

@pytest.fixture
def client():
    with app.test_client() as c:
        yield c

def test_create_train_weak_railcar(client):
    """
    Test: sum of passenger car weights > railcar maxTractiveForce -> 400 error
    We'll assume railcarID=4 (in seed_db: r2 = 50 force) if that ID is correct
    and passengerCars includes 2 big cars with total weight > 50.
    Adjust if necessary.
    """
    # Hypothetical passengerCarIDs from seed
    # p1 => 40 weight, p2 => 60 weight
    # Summed weight = 100 => definitely > railcar 4's maxTractiveForce=50
    payload = {
        "name": "TooHeavyTrain",
        "railcarID": 4,  # check if this matches your DB: railcar with 50 force
        "passengerCars": [
            {"id": 2, "position": 1},  # p1 (weight 40)
            {"id": 3, "position": 2}   # p2 (weight 60)
        ]
    }
    resp = client.post('/fleet/trains/', json=payload)
    assert resp.status_code == 400
    assert b"Railcar too weak" in resp.data

def test_create_train_gauge_mismatch(client):
    """
    Test: railcar gauge != passengerCar gauge -> 400 error
    Example: railcar with gauge=1435 + passengerCar with gauge=1000
    """
    # Suppose railcarID=5 (r3 => gauge=1000) + passengerCarID=2 or 3 => gauge=1435
    payload = {
        "name": "GaugeMismatchTrain",
        "railcarID": 5,  # r3 => gauge=1000
        "passengerCars": [
            {"id": 2, "position": 1},  # p1 => gauge=1435 => mismatch
        ]
    }
    resp = client.post('/fleet/trains/', json=payload)
    assert resp.status_code == 400
    assert b"Track gauge mismatch" in resp.data

def test_delete_train_with_maintenance(client):
    """
    Try deleting a train that has maintenance.
    If train 1 (FastExpress) has existing maintenance in seed_db,
    then deletion must fail with 400.
    """
    train_id = 1  # Assuming seed_db created train 1 with maintenance
    resp = client.delete(f'/fleet/trains/{train_id}')
    assert resp.status_code == 400
    assert b"Cannot delete train with existing maintenance" in resp.data

def test_delete_train_no_maintenance(client):
    """
    If there's a train with no maintenance, we can delete it.
    Possibly train 2 => 'LocalLine' has maintenance as well. Check seed_db.
    If both have maintenance, we can create a new train, then delete it.
    """
    # Create a new train with no maintenance
    payload = {
        "name": "TempTrainNoMaint",
        "railcarID": 5,   # gauge=1000 railcar
        "passengerCars": [
            {"id": 6, "position": 1}  # p3 => gauge=1000
        ]
    }
    create_resp = client.post('/fleet/trains/', json=payload)
    assert create_resp.status_code == 201
    new_train_id = create_resp.get_json().get("trainID")

    # Now delete it
    delete_resp = client.delete(f'/fleet/trains/{new_train_id}')
    assert delete_resp.status_code == 200
    assert b"Train deleted" in delete_resp.data