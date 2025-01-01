"""
tests/test_carriages.py

Check:
 - Carriage cannot be edited/deleted if assigned to a train
"""

import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as c:
        yield c

def test_edit_carriage_in_train(client):
    """
    Attempt to edit passengerCar that is currently in a train.
    According to seed_db, train 1 uses passengerCarIDs 2 (p1) and 3 (p2).
    """
    carriage_id_in_train = 2  # p1 in train 1
    update_payload = {
        "trackGauge": "1000"  # attempt mismatch just to see if it fails
    }
    resp = client.put(f'/fleet/carriages/{carriage_id_in_train}', json=update_payload)
    assert resp.status_code == 400
    assert b"Cannot edit carriage currently assigned to a train" in resp.data

def test_delete_carriage_in_train(client):
    """
    Attempt to delete passengerCar that is in a train.
    """
    carriage_id_in_train = 2
    resp = client.delete(f'/fleet/carriages/{carriage_id_in_train}')
    assert resp.status_code == 400
    assert b"Cannot delete carriage assigned to a train" in resp.data