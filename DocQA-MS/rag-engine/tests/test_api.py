import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestAPI:
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "IndexeurSémantique" in response.json()["service"]
    
    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_get_stats(self):
        response = client.get("/index/stats")
        assert response.status_code == 200
        assert "faiss_stats" in response.json()

