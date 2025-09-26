import os
import sys

import pytest
from fastapi.testclient import TestClient

DATABASE_URL = os.getenv("DATABASE_URL", "")
pytestmark = pytest.mark.skipif(
    not DATABASE_URL.startswith("postgresql"),
    reason="PostgreSQL DATABASE_URL required for Supabase-backed tests",
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app

client = TestClient(app)


def test_admin_requires_auth():
    response = client.get("/admin")
    assert response.status_code == 401


def test_admin_auth_success():
    response = client.get("/admin", auth=("admin", "secret"))
    assert response.status_code == 200
