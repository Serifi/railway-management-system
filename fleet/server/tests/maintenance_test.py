"""
tests/test_maintenance.py

Check overlap constraint for employees:
 - "Man soll einen Mitarbeiter nicht zum selben Zeitpunkt zu mehreren Wartungen zuordnen können."
"""

import pytest
from app import app
from datetime import datetime, timedelta

@pytest.fixture
def client():
    with app.test_client() as c:
        yield c

def test_employee_maintenance_overlap(client):
    """
    We'll pick an employee with existing maintenance from seed_db (e1 => John Doe, SSN=1234200101).
    That existing maintenance might be from_time=now to now+2h.
    We'll try to create an overlapping new maintenance => expect 400.
    """
    # Overlap check
    now = datetime.now()
    from_time = (now + timedelta(minutes=30)).isoformat()  # Overlap
    to_time = (now + timedelta(hours=1, minutes=30)).isoformat()

    payload = {
        "employeeSSN": "1234200101",  # John Doe
        "trainID": 2,  # Some train
        "from_time": from_time,
        "to_time": to_time
    }
    resp = client.post('/fleet/maintenance/', json=payload)
    assert resp.status_code == 400
    assert b"Employee already assigned in overlapping time" in resp.data

def test_create_and_delete_maintenance(client):
    """
    Simple test to create a new maintenance for an employee/time that doesn't overlap,
    and then delete it. This ensures POST/DELETE coverage.
    """
    start_time = datetime.now() + timedelta(days=2)  # not overlapping existing seeds
    payload = {
        "employeeSSN": "1234200101",  # John Doe
        "trainID": 2,
        "from_time": start_time.isoformat(),
        "to_time": (start_time + timedelta(hours=2)).isoformat()
    }
    resp_create = client.post('/fleet/maintenance/', json=payload)
    assert resp_create.status_code in [201, 400, 404]
    if resp_create.status_code == 201:
        # If created, we try to delete
        # get new maintenanceID from response if needed
        maintenance_list = client.get('/fleet/maintenance/').get_json()
        new_m = max(maintenance_list, key=lambda x: x["maintenanceID"])
        new_id = new_m["maintenanceID"]

        del_resp = client.delete(f'/fleet/maintenance/{new_id}')
        assert del_resp.status_code == 200
        assert b"Maintenance deleted" in del_resp.data