"""
Tests pour les endpoints Macro.

Utilise TestClient de FastAPI pour tester les endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client():
    """Crée un client de test."""
    return TestClient(app)


class TestMacroEndpoint:
    """Tests pour GET /api/v1/macro"""

    def test_get_macro_returns_200_or_404(self, client):
        """GET /macro retourne 200 ou 404."""
        response = client.get("/api/v1/macro")
        assert response.status_code in [200, 404]

    def test_get_macro_with_dates(self, client):
        """Les paramètres de date sont acceptés."""
        response = client.get(
            "/api/v1/macro",
            params={"start_date": "2020-01-01", "end_date": "2020-12-31"},
        )
        assert response.status_code in [200, 404]

    def test_get_macro_invalid_date_range(self, client):
        """Une plage de dates invalide retourne 400."""
        response = client.get(
            "/api/v1/macro",
            params={"start_date": "2021-01-01", "end_date": "2020-01-01"},
        )
        assert response.status_code == 400


class TestMacroLatestEndpoint:
    """Tests pour GET /api/v1/macro/latest"""

    def test_get_latest_macro_returns_200_or_404(self, client):
        """GET /macro/latest retourne 200 ou 404."""
        response = client.get("/api/v1/macro/latest")
        assert response.status_code in [200, 404]
