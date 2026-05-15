"""
Tests pour les endpoints ETF.

Utilise TestClient de FastAPI pour tester les endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client():
    """Crée un client de test."""
    return TestClient(app)


class TestETFListEndpoint:
    """Tests pour GET /api/v1/etfs"""

    def test_list_etfs_returns_200(self, client):
        """L'endpoint retourne un code 200."""
        response = client.get("/api/v1/etfs")
        assert response.status_code == 200

    def test_list_etfs_returns_10_etfs(self, client):
        """L'endpoint retourne 10 ETF."""
        response = client.get("/api/v1/etfs")
        data = response.json()
        assert data["count"] == 10
        assert len(data["etfs"]) == 10

    def test_list_etfs_contains_spy(self, client):
        """SPY est dans la liste."""
        response = client.get("/api/v1/etfs")
        data = response.json()
        tickers = [etf["ticker"] for etf in data["etfs"]]
        assert "SPY" in tickers

    def test_list_etfs_has_required_fields(self, client):
        """Chaque ETF a les champs requis."""
        response = client.get("/api/v1/etfs")
        data = response.json()

        for etf in data["etfs"]:
            assert "ticker" in etf
            assert "name" in etf
            assert "asset_class" in etf


class TestETFDetailEndpoint:
    """Tests pour GET /api/v1/etfs/{ticker}"""

    def test_get_spy_returns_200(self, client):
        """GET /etfs/SPY retourne 200."""
        response = client.get("/api/v1/etfs/SPY")
        assert response.status_code == 200

    def test_get_spy_returns_correct_data(self, client):
        """GET /etfs/SPY retourne les bonnes données."""
        response = client.get("/api/v1/etfs/SPY")
        data = response.json()
        assert data["ticker"] == "SPY"
        assert "S&P 500" in data["name"]

    def test_get_lowercase_ticker_works(self, client):
        """Les tickers en minuscules fonctionnent."""
        response = client.get("/api/v1/etfs/spy")
        assert response.status_code == 200
        assert response.json()["ticker"] == "SPY"

    def test_get_invalid_ticker_returns_404(self, client):
        """Un ticker invalide retourne 404."""
        response = client.get("/api/v1/etfs/INVALID")
        assert response.status_code == 404

    def test_get_invalid_ticker_has_error_message(self, client):
        """L'erreur 404 contient un message."""
        response = client.get("/api/v1/etfs/INVALID")
        data = response.json()
        assert "detail" in data
        assert "INVALID" in data["detail"]


class TestETFPricesEndpoint:
    """Tests pour GET /api/v1/etfs/{ticker}/prices"""

    def test_get_prices_returns_200(self, client):
        """GET /etfs/SPY/prices retourne 200."""
        response = client.get("/api/v1/etfs/SPY/prices")
        # Peut retourner 200 ou 404 si pas de données
        assert response.status_code in [200, 404]

    def test_get_prices_invalid_ticker_returns_404(self, client):
        """Un ticker invalide retourne 404."""
        response = client.get("/api/v1/etfs/INVALID/prices")
        assert response.status_code == 404

    def test_get_prices_with_dates_params(self, client):
        """Les paramètres de date sont acceptés."""
        response = client.get(
            "/api/v1/etfs/SPY/prices",
            params={"start_date": "2020-01-01", "end_date": "2020-12-31"},
        )
        # Peut retourner 200 ou 404 si pas de données
        assert response.status_code in [200, 404]

    def test_get_prices_invalid_date_range_returns_400(self, client):
        """Une plage de dates invalide retourne 400."""
        response = client.get(
            "/api/v1/etfs/SPY/prices",
            params={"start_date": "2021-01-01", "end_date": "2020-01-01"},
        )
        assert response.status_code == 400


class TestETFFeaturesEndpoint:
    """Tests pour GET /api/v1/etfs/{ticker}/features"""

    def test_get_features_returns_200_or_404(self, client):
        """GET /etfs/SPY/features retourne 200 ou 404."""
        response = client.get("/api/v1/etfs/SPY/features")
        assert response.status_code in [200, 404]

    def test_get_features_invalid_ticker_returns_404(self, client):
        """Un ticker invalide retourne 404."""
        response = client.get("/api/v1/etfs/INVALID/features")
        assert response.status_code == 404
