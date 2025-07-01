import sys
import os

# Configure test database before importing the application
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app

client = TestClient(app)


def test_create_and_get_booking():
    # ensure clean state
    existing = client.get("/bookings/")
    for b in existing.json():
        client.delete(f"/bookings/{b['id']}")
    start = datetime.utcnow() + timedelta(days=1)
    end = start + timedelta(hours=1)
    response = client.post(
        "/bookings/",
        json={"name": "John", "building": "1 Savoie", "start": start.isoformat(), "end": end.isoformat()},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "John"
    assert data["booking_status"] == "pending"

    confirm_resp = client.post(f"/bookings/{data['id']}/confirm")
    assert confirm_resp.status_code == 200
    assert confirm_resp.json()["booking_status"] == "confirmed"

    get_resp = client.get("/bookings/")
    assert get_resp.status_code == 200
    assert any(b["id"] == data["id"] and b["booking_status"] == "confirmed" for b in get_resp.json())


def test_deny_booking():
    start = datetime.utcnow() + timedelta(days=2)
    end = start + timedelta(hours=1)
    resp = client.post(
        "/bookings/",
        json={"name": "Jane", "building": "3 Savoie", "start": start.isoformat(), "end": end.isoformat()},
    )
    assert resp.status_code == 200
    booking = resp.json()
    deny_resp = client.post(f"/bookings/{booking['id']}/deny")
    assert deny_resp.status_code == 200
    assert deny_resp.json()["booking_status"] == "denied"
    # slot should be free
    second_resp = client.post(
        "/bookings/",
        json={"name": "Other", "building": "5 Savoie", "start": start.isoformat(), "end": end.isoformat()},
    )
    assert second_resp.status_code == 200
