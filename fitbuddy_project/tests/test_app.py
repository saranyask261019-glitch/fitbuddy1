from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_homepage_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "FitBuddy" in response.text

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_docs_load():
    response = client.get("/docs")
    assert response.status_code == 200
