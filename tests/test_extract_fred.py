"""
Tests unitaires pour l'extracteur FRED.

Note: Les tests qui appellent l'API FRED nécessitent une clé API valide.
On utilise des mocks pour les tests unitaires purs.
"""

import os
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from data.extractors.extract_fred import FRED_SERIES, get_fred_client, get_fred_series


class TestConstants:
    """Tests des constantes."""

    def test_fred_series_count(self):
        """Vérifie qu'on a les 9 séries attendues."""
        assert len(FRED_SERIES) == 9

    def test_fred_series_format(self):
        """Vérifie le format des tuples (code, nom, description)."""
        for series in FRED_SERIES:
            assert len(series) == 3
            code, name, desc = series
            assert isinstance(code, str)
            assert isinstance(name, str)
            assert isinstance(desc, str)
            assert len(code) > 0
            assert len(name) > 0

    def test_vix_in_series(self):
        """Vérifie que le VIX est bien dans les séries."""
        codes = [s[0] for s in FRED_SERIES]
        assert "VIXCLS" in codes

    def test_risk_free_rate_in_series(self):
        """Vérifie que le taux sans risque 3 mois est présent."""
        codes = [s[0] for s in FRED_SERIES]
        assert "DGS3MO" in codes


class TestGetFredClient:
    """Tests de la fonction get_fred_client."""

    def test_raises_without_api_key(self):
        """Vérifie qu'une erreur est levée sans clé API."""
        with patch.dict(os.environ, {}, clear=True):
            # On force la suppression de la clé
            if "FRED_API_KEY" in os.environ:
                del os.environ["FRED_API_KEY"]
            with pytest.raises(ValueError, match="FRED_API_KEY"):
                get_fred_client()


class TestGetFredSeriesMocked:
    """Tests avec mock du client FRED."""

    @pytest.fixture
    def mock_fred(self):
        """Crée un mock du client FRED."""
        with patch("data.extractors.extract_fred.get_fred_client") as mock:
            fred_instance = MagicMock()
            mock.return_value = fred_instance

            # Simule des données de série
            def mock_get_series(code, **kwargs):
                dates = pd.date_range("2024-01-01", "2024-01-10", freq="D")
                return pd.Series([10.0 + i for i in range(len(dates))], index=dates)

            fred_instance.get_series = mock_get_series
            yield fred_instance

    def test_returns_dataframe(self, mock_fred):
        """Vérifie que get_fred_series retourne un DataFrame."""
        series = [("TEST1", "test1", "Test series 1")]
        result = get_fred_series(series, "2024-01-01", "2024-01-10")
        assert isinstance(result, pd.DataFrame)

    def test_has_expected_columns(self, mock_fred):
        """Vérifie que les colonnes correspondent aux noms demandés."""
        series = [
            ("TEST1", "col_a", "Test A"),
            ("TEST2", "col_b", "Test B"),
        ]
        result = get_fred_series(series, "2024-01-01", "2024-01-10")
        assert "col_a" in result.columns
        assert "col_b" in result.columns

    def test_index_is_datetime(self, mock_fred):
        """Vérifie que l'index est de type DatetimeIndex."""
        series = [("TEST1", "test1", "Test")]
        result = get_fred_series(series, "2024-01-01", "2024-01-10")
        assert isinstance(result.index, pd.DatetimeIndex)


@pytest.mark.skipif(
    not os.getenv("FRED_API_KEY"),
    reason="FRED_API_KEY non définie - test d'intégration ignoré",
)
class TestGetFredSeriesIntegration:
    """Tests d'intégration avec l'API FRED réelle."""

    def test_download_vix(self):
        """Test réel du téléchargement du VIX."""
        series = [("VIXCLS", "vix", "VIX")]
        result = get_fred_series(series, "2024-01-01", "2024-01-31")
        assert "vix" in result.columns
        # VIX doit être entre 9 et 90 historiquement
        vix_values = result["vix"].dropna()
        assert len(vix_values) > 0
        assert vix_values.min() >= 0
        assert vix_values.max() <= 100
