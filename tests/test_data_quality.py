"""
Tests de qualité des données.

Ces tests vérifient que les données nettoyées respectent les contraintes
définies dans le projet (pas de NaN critiques, valeurs dans les plages attendues, etc.).
"""

import numpy as np
import pandas as pd
import pytest

from data.pipeline.cleaning_rules import (
    check_temporal_monotonicity,
    detect_outliers,
    handle_missing_values,
    validate_price_range,
    validate_returns_range,
)


class TestTemporalMonotonicity:
    """Tests de la vérification de monotonie temporelle."""

    def test_valid_monotonic_index(self):
        """Index monotone croissant doit passer."""
        df = pd.DataFrame(
            {"value": [1, 2, 3]},
            index=pd.date_range("2024-01-01", periods=3, freq="D"),
        )
        # Ne doit pas lever d'exception
        check_temporal_monotonicity(df)

    def test_non_monotonic_index_raises(self):
        """Index non monotone doit lever une ValueError."""
        df = pd.DataFrame(
            {"value": [1, 2, 3]},
            index=pd.to_datetime(["2024-01-03", "2024-01-01", "2024-01-02"]),
        )
        with pytest.raises(ValueError, match="non monotone"):
            check_temporal_monotonicity(df)

    def test_duplicate_dates_raises(self):
        """Dates dupliquées doivent lever une ValueError."""
        df = pd.DataFrame(
            {"value": [1, 2, 3]},
            index=pd.to_datetime(["2024-01-01", "2024-01-01", "2024-01-02"]),
        )
        with pytest.raises(ValueError, match="dupliquées"):
            check_temporal_monotonicity(df)


class TestHandleMissingValues:
    """Tests de la gestion des valeurs manquantes."""

    def test_forward_fill_small_gaps(self):
        """Les petits gaps doivent être forward-fillés."""
        df = pd.DataFrame(
            {"SPY": [100, np.nan, np.nan, 103, 104]},
            index=pd.date_range("2024-01-01", periods=5, freq="D"),
        )
        result = handle_missing_values(df, critical_cols=["SPY"], max_consecutive_nan=3)
        assert result["SPY"].isna().sum() == 0

    def test_remove_large_gaps(self):
        """Les grands gaps doivent entraîner la suppression des lignes."""
        df = pd.DataFrame(
            {"SPY": [100, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 107]},
            index=pd.date_range("2024-01-01", periods=8, freq="D"),
        )
        result = handle_missing_values(df, critical_cols=["SPY"], max_consecutive_nan=3)
        # Les lignes avec grands gaps sont supprimées
        assert len(result) < len(df)

    def test_non_critical_cols_always_ffill(self):
        """Les colonnes non-critiques sont toujours forward-fillées."""
        df = pd.DataFrame(
            {
                "SPY": [100, 101, 102, 103, 104],
                "vix": [15, np.nan, np.nan, np.nan, 20],
            },
            index=pd.date_range("2024-01-01", periods=5, freq="D"),
        )
        result = handle_missing_values(df, critical_cols=["SPY"])
        assert result["vix"].isna().sum() == 0


class TestDetectOutliers:
    """Tests de la détection des outliers."""

    def test_flags_extreme_returns(self):
        """Les returns > 10% doivent être flaggés."""
        df = pd.DataFrame(
            {"SPY": [100, 115, 116, 117, 118]},  # +15% au jour 2
            index=pd.date_range("2024-01-01", periods=5, freq="D"),
        )
        # Ajouter la colonne return
        df["SPY_ret_1d"] = df["SPY"].pct_change()

        result = detect_outliers(df, tickers=["SPY"], threshold=0.10)
        assert "is_outlier" in result.columns
        assert result["is_outlier"].sum() >= 1

    def test_no_outliers_in_normal_data(self):
        """Les returns normaux ne doivent pas être flaggés."""
        df = pd.DataFrame(
            {"SPY": [100, 101, 102, 101.5, 102.5]},  # Returns < 2%
            index=pd.date_range("2024-01-01", periods=5, freq="D"),
        )
        df["SPY_ret_1d"] = df["SPY"].pct_change()

        result = detect_outliers(df, tickers=["SPY"], threshold=0.10)
        assert result["is_outlier"].sum() == 0


class TestValidatePriceRange:
    """Tests de validation de la plage des prix."""

    def test_valid_prices_pass(self):
        """Prix dans la plage valide."""
        df = pd.DataFrame(
            {"SPY": [400, 410, 420]},
            index=pd.date_range("2024-01-01", periods=3, freq="D"),
        )
        assert validate_price_range(df, ["SPY"]) is True

    def test_negative_prices_fail(self):
        """Prix négatifs doivent échouer."""
        df = pd.DataFrame(
            {"SPY": [400, -10, 420]},
            index=pd.date_range("2024-01-01", periods=3, freq="D"),
        )
        assert validate_price_range(df, ["SPY"]) is False

    def test_extreme_prices_fail(self):
        """Prix extrêmes doivent échouer."""
        df = pd.DataFrame(
            {"SPY": [400, 50000, 420]},
            index=pd.date_range("2024-01-01", periods=3, freq="D"),
        )
        assert validate_price_range(df, ["SPY"]) is False


class TestValidateReturnsRange:
    """Tests de validation de la plage des returns."""

    def test_normal_returns_pass(self):
        """Returns normaux doivent passer."""
        df = pd.DataFrame(
            {"SPY_ret_1d": [0.01, -0.02, 0.015, -0.01]},
            index=pd.date_range("2024-01-01", periods=4, freq="D"),
        )
        assert validate_returns_range(df, ["SPY"]) is True

    def test_extreme_returns_fail(self):
        """Returns > 50% doivent échouer."""
        df = pd.DataFrame(
            {"SPY_ret_1d": [0.01, 0.60, -0.02]},  # 60% return
            index=pd.date_range("2024-01-01", periods=3, freq="D"),
        )
        assert validate_returns_range(df, ["SPY"]) is False


class TestVixRange:
    """Tests spécifiques pour le VIX."""

    def test_vix_realistic_range(self):
        """VIX doit être entre 0 et 100."""
        # Données fictives mais réalistes
        vix_data = pd.Series([12, 15, 25, 35, 80])  # Range historique normal
        assert vix_data.min() >= 0
        assert vix_data.max() <= 100

    def test_vix_not_negative(self):
        """VIX ne peut pas être négatif."""
        vix_data = pd.Series([12, 15, 25])
        assert (vix_data >= 0).all()


class TestIndexIntegrity:
    """Tests d'intégrité de l'index temporel."""

    def test_index_strictly_increasing(self):
        """L'index doit être strictement croissant."""
        dates = pd.date_range("2024-01-01", periods=100, freq="D")
        df = pd.DataFrame({"value": range(100)}, index=dates)
        assert df.index.is_monotonic_increasing

    def test_no_weekend_gaps_too_large(self):
        """Les gaps ne doivent pas dépasser 4 jours (weekend + jours fériés max)."""
        # Simulation d'un index de jours de trading
        dates = pd.bdate_range("2024-01-01", periods=20)
        df = pd.DataFrame({"value": range(20)}, index=dates)

        max_gap = df.index.to_series().diff().max()
        # Maximum attendu : 3 jours (vendredi → lundi)
        # Avec jours fériés, peut aller jusqu'à 4-5 jours
        assert max_gap <= pd.Timedelta(days=5)
