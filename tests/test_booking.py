import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app

client = TestClient(app)


def test_create_and_get_booking():
    start = datetime.utcnow() + timedelta(days=1)
    end = start + timedelta(hours=1)
    response = client.post(
        "/bookings/",
        json={"name": "John", "start": start.isoformat(), "end": end.isoformat()},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "John"

    get_resp = client.get("/bookings/")
    assert get_resp.status_code == 200
    assert any(b["id"] == data["id"] for b in get_resp.json())
