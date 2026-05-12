"""
Tests unitaires pour l'extracteur yfinance.
"""

import pandas as pd
import pytest

from data.extractors.extract_yfinance import (
    ALL_TICKERS,
    BENCHMARK_TICKERS,
    ETF_TICKERS,
    download_etf_prices,
)


class TestConstants:
    """Tests des constantes."""

    def test_etf_tickers_count(self):
        """Vérifie qu'on a bien 8 ETF."""
        assert len(ETF_TICKERS) == 8

    def test_benchmark_tickers_count(self):
        """Vérifie qu'on a bien 2 benchmarks."""
        assert len(BENCHMARK_TICKERS) == 2

    def test_all_tickers_combined(self):
        """Vérifie que ALL_TICKERS combine ETF + benchmarks."""
        assert len(ALL_TICKERS) == 10
        assert all(t in ALL_TICKERS for t in ETF_TICKERS)
        assert all(t in ALL_TICKERS for t in BENCHMARK_TICKERS)


class TestDownloadEtfPrices:
    """Tests de la fonction download_etf_prices."""

    @pytest.fixture
    def sample_data(self):
        """Télécharge un petit échantillon pour les tests."""
        # On teste sur une courte période pour accélérer les tests
        return download_etf_prices(
            tickers=["SPY", "TLT"],
            start_date="2024-01-01",
            end_date="2024-01-31",
        )

    def test_returns_dataframe(self, sample_data):
        """Vérifie que la fonction retourne un DataFrame."""
        assert isinstance(sample_data, pd.DataFrame)

    def test_has_expected_columns(self, sample_data):
        """Vérifie que les colonnes correspondent aux tickers demandés."""
        assert "SPY" in sample_data.columns
        assert "TLT" in sample_data.columns

    def test_index_is_datetime(self, sample_data):
        """Vérifie que l'index est de type DatetimeIndex."""
        assert isinstance(sample_data.index, pd.DatetimeIndex)

    def test_no_completely_empty_ticker(self, sample_data):
        """Vérifie qu'aucun ticker n'est complètement vide."""
        for col in sample_data.columns:
            # Au moins 50% des valeurs doivent être non-nulles
            assert sample_data[col].notna().mean() > 0.5, f"Ticker {col} est presque vide"

    def test_prices_are_positive(self, sample_data):
        """Vérifie que tous les prix sont positifs."""
        for col in sample_data.columns:
            valid_prices = sample_data[col].dropna()
            assert (valid_prices > 0).all(), f"Prix négatifs trouvés pour {col}"


class TestDownloadEdgeCases:
    """Tests des cas limites."""

    def test_single_ticker(self):
        """Vérifie le fonctionnement avec un seul ticker."""
        data = download_etf_prices(
            tickers=["SPY"],
            start_date="2024-01-01",
            end_date="2024-01-15",
        )
        assert isinstance(data, pd.DataFrame)
        assert len(data.columns) >= 1

    def test_short_period(self):
        """Vérifie le fonctionnement sur une période très courte."""
        data = download_etf_prices(
            tickers=["SPY"],
            start_date="2024-01-02",
            end_date="2024-01-05",
        )
        assert len(data) >= 1  # Au moins 1 jour de trading
