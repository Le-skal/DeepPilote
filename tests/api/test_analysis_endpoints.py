"""
Tests pour les endpoints Analysis.

Utilise TestClient de FastAPI pour tester les endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client():
    """Crée un client de test."""
    return TestClient(app)


class TestCorrelationsEndpoint:
    """Tests pour GET /api/v1/analysis/correlations"""

    def test_get_correlations_returns_200_or_404(self, client):
        """GET /analysis/correlations retourne 200 ou 404."""
        response = client.get("/api/v1/analysis/correlations")
        assert response.status_code in [200, 404]

    def test_get_correlations_with_dates(self, client):
        """Les paramètres de date sont acceptés."""
        response = client.get(
            "/api/v1/analysis/correlations",
            params={"start_date": "2020-01-01", "end_date": "2020-12-31"},
        )
        assert response.status_code in [200, 404]


class TestStatsEndpoint:
    """Tests pour GET /api/v1/analysis/stats"""

    def test_get_stats_returns_200_or_404(self, client):
        """GET /analysis/stats retourne 200 ou 404."""
        response = client.get("/api/v1/analysis/stats")
        assert response.status_code in [200, 404]

    def test_get_etf_stats_returns_200_or_404(self, client):
        """GET /analysis/stats/SPY retourne 200 ou 404."""
        response = client.get("/api/v1/analysis/stats/SPY")
        assert response.status_code in [200, 404]

    def test_get_etf_stats_invalid_ticker(self, client):
        """Un ticker invalide retourne 404."""
        response = client.get("/api/v1/analysis/stats/INVALID")
        assert response.status_code == 404


class TestHealthEndpoint:
    """Tests pour GET /health"""

    def test_health_returns_200(self, client):
        """GET /health retourne 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_has_required_fields(self, client):
        """Le health check a les champs requis."""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert "version" in data

    def test_health_status_is_ok(self, client):
        """Le status est 'ok'."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"
