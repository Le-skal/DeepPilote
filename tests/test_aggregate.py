"""
Tests unitaires pour le pipeline d'agrégation.
"""

import numpy as np
import pandas as pd
import pytest

from data.pipeline.aggregate import (
    compute_returns,
    compute_technical_indicators,
    compute_volatility,
    merge_prices_macro,
)


class TestMergePricesMacro:
    """Tests de la fusion prix/macro."""

    @pytest.fixture
    def sample_prices(self):
        """Données prix de test."""
        dates = pd.date_range("2024-01-01", periods=10, freq="D")
        return pd.DataFrame(
            {
                "SPY": [400 + i for i in range(10)],
                "TLT": [100 - i * 0.5 for i in range(10)],
            },
            index=dates,
        )

    @pytest.fixture
    def sample_macro(self):
        """Données macro de test."""
        dates = pd.date_range("2024-01-01", periods=10, freq="D")
        return pd.DataFrame(
            {
                "vix": [15 + i * 0.5 for i in range(10)],
                "t3mo": [5.0] * 10,
            },
            index=dates,
        )

    def test_merge_keeps_all_columns(self, sample_prices, sample_macro):
        """Vérifie que toutes les colonnes sont conservées."""
        result = merge_prices_macro(sample_prices, sample_macro)
        assert "SPY" in result.columns
        assert "TLT" in result.columns
        assert "vix" in result.columns
        assert "t3mo" in result.columns

    def test_merge_keeps_all_rows(self, sample_prices, sample_macro):
        """Vérifie que toutes les lignes sont conservées."""
        result = merge_prices_macro(sample_prices, sample_macro)
        assert len(result) == len(sample_prices)

    def test_merge_with_missing_macro_dates(self, sample_prices):
        """Vérifie le forward-fill des données macro manquantes."""
        # Macro avec moins de dates
        macro_dates = pd.date_range("2024-01-01", periods=5, freq="D")
        macro_df = pd.DataFrame({"vix": [15, 16, 17, 18, 19]}, index=macro_dates)

        result = merge_prices_macro(sample_prices, macro_df)

        # Les valeurs manquantes doivent être forward-fillées
        assert result["vix"].iloc[5] == 19  # Dernière valeur connue


class TestComputeReturns:
    """Tests du calcul des rendements."""

    @pytest.fixture
    def prices_df(self):
        """DataFrame de prix pour les tests."""
        dates = pd.date_range("2024-01-01", periods=100, freq="D")
        # Prix simulés avec tendance
        spy_prices = 400 + np.cumsum(np.random.randn(100) * 2)
        return pd.DataFrame({"SPY": spy_prices}, index=dates)

    def test_returns_columns_created(self, prices_df):
        """Vérifie que les colonnes de returns sont créées."""
        result = compute_returns(prices_df, ["SPY"])
        assert "SPY_ret_1d" in result.columns
        assert "SPY_ret_5d" in result.columns
        assert "SPY_ret_20d" in result.columns
        assert "SPY_logret_1d" in result.columns

    def test_returns_first_value_is_nan(self, prices_df):
        """Le premier return doit être NaN (pas de valeur précédente)."""
        result = compute_returns(prices_df, ["SPY"])
        assert pd.isna(result["SPY_ret_1d"].iloc[0])

    def test_log_returns_close_to_simple_for_small_changes(self, prices_df):
        """Les log returns doivent être proches des simple returns pour petits changements."""
        result = compute_returns(prices_df, ["SPY"])
        simple = result["SPY_ret_1d"].dropna()
        log = result["SPY_logret_1d"].dropna()
        # Pour des returns < 10%, différence < 1%
        small_returns = simple[simple.abs() < 0.1]
        small_log = log[simple.abs() < 0.1]
        diff = (small_returns - small_log).abs()
        assert diff.max() < 0.01


class TestComputeVolatility:
    """Tests du calcul de la volatilité."""

    @pytest.fixture
    def returns_df(self):
        """DataFrame avec log returns pour les tests."""
        dates = pd.date_range("2024-01-01", periods=100, freq="D")
        log_returns = np.random.randn(100) * 0.01  # ~1% vol daily
        df = pd.DataFrame({"SPY_logret_1d": log_returns}, index=dates)
        return df

    def test_volatility_columns_created(self, returns_df):
        """Vérifie que les colonnes de volatilité sont créées."""
        result = compute_volatility(returns_df, ["SPY"])
        assert "SPY_vol_20d" in result.columns
        assert "SPY_vol_60d" in result.columns

    def test_volatility_is_annualized(self, returns_df):
        """Vérifie que la volatilité est annualisée (× sqrt(252))."""
        result = compute_volatility(returns_df, ["SPY"])
        vol_20d = result["SPY_vol_20d"].dropna()
        # Daily vol ~1% → annualized ~16%
        assert vol_20d.mean() > 0.10  # Plus de 10%
        assert vol_20d.mean() < 0.30  # Moins de 30%


class TestComputeTechnicalIndicators:
    """Tests des indicateurs techniques."""

    @pytest.fixture
    def prices_df(self):
        """DataFrame de prix avec assez de données pour tous les indicateurs."""
        dates = pd.date_range("2024-01-01", periods=250, freq="D")
        # Prix avec tendance haussière
        spy_prices = 400 + np.cumsum(np.random.randn(250) * 2 + 0.5)
        return pd.DataFrame({"SPY": spy_prices}, index=dates)

    def test_sma_columns_created(self, prices_df):
        """Vérifie que les SMA sont calculées."""
        result = compute_technical_indicators(prices_df, ["SPY"])
        assert "SPY_sma_20" in result.columns
        assert "SPY_sma_50" in result.columns
        assert "SPY_sma_200" in result.columns

    def test_rsi_in_valid_range(self, prices_df):
        """Le RSI doit être entre 0 et 100."""
        result = compute_technical_indicators(prices_df, ["SPY"])
        rsi = result["SPY_rsi_14"].dropna()
        assert rsi.min() >= 0
        assert rsi.max() <= 100

    def test_macd_columns_created(self, prices_df):
        """Vérifie que le MACD est calculé."""
        result = compute_technical_indicators(prices_df, ["SPY"])
        assert "SPY_macd" in result.columns
        assert "SPY_macd_signal" in result.columns

    def test_bollinger_position_typically_between_0_1(self, prices_df):
        """La position Bollinger est généralement entre 0 et 1."""
        result = compute_technical_indicators(prices_df, ["SPY"])
        bb_pos = result["SPY_bb_position"].dropna()
        # Peut dépasser [0, 1] si le prix sort des bandes
        # En tendance haussière (données test), la moyenne peut être > 0.5
        assert 0 < bb_pos.mean() < 1.2
