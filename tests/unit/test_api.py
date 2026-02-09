import pytest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from agentops.api.app import create_app


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


class TestHealthEndpoints:
    def test_health(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_health_response_format(self, client):
        response = client.get("/api/v1/health")
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "environment" in data


class TestRunEndpoints:
    def test_create_run_requires_auth(self, client):
        response = client.post("/api/v1/runs", json={"topic": "test"})
        assert response.status_code == 401

    def test_list_runs_requires_auth(self, client):
        response = client.get("/api/v1/runs")
        assert response.status_code == 401


class TestGuardrailEndpoints:
    def test_violations_requires_auth(self, client):
        response = client.get("/api/v1/guardrails/violations")
        assert response.status_code == 401


class TestMetricEndpoints:
    def test_prometheus_metrics(self, client):
        response = client.get("/api/v1/metrics/prometheus")
        assert response.status_code == 200
        assert "agentops" in response.text or response.status_code == 200
