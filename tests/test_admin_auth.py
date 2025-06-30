import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_admin_requires_auth():
    response = client.get('/admin')
    assert response.status_code == 401

def test_admin_auth_success():
    response = client.get('/admin', auth=('admin','secret'))
    assert response.status_code == 200
