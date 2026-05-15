"""
Tests pour les modèles de détection de régime.

Teste K-Means, GMM et HMM.
"""

import numpy as np
import pandas as pd
import pytest

from ml.models.regime_kmeans import RegimeKMeans
from ml.models.regime_gmm import RegimeGMM
from ml.models.regime_hmm import RegimeHMM
from ml.config import N_REGIMES


@pytest.fixture
def sample_regime_features():
    """Génère des features de régime synthétiques."""
    np.random.seed(42)
    n_samples = 500

    # Simuler 4 régimes avec des caractéristiques différentes
    dates = pd.date_range("2020-01-01", periods=n_samples, freq="D")

    # Créer des features avec des patterns de régime
    vix_zscore = np.concatenate([
        np.random.normal(-0.5, 0.3, 125),  # Stable
        np.random.normal(0.3, 0.3, 125),   # Bull
        np.random.normal(1.5, 0.5, 125),   # Volatile
        np.random.normal(1.0, 0.4, 125),   # Bear
    ])

    spy_volatility = np.concatenate([
        np.random.normal(0.10, 0.02, 125),
        np.random.normal(0.12, 0.03, 125),
        np.random.normal(0.25, 0.05, 125),
        np.random.normal(0.20, 0.04, 125),
    ])

    spy_return = np.concatenate([
        np.random.normal(0.05, 0.05, 125),
        np.random.normal(0.10, 0.08, 125),
        np.random.normal(-0.02, 0.15, 125),
        np.random.normal(-0.15, 0.10, 125),
    ])

    return pd.DataFrame({
        "vix_zscore": vix_zscore,
        "spy_volatility_20d": spy_volatility,
        "spy_return_20d": spy_return,
        "credit_spread_zscore": np.random.randn(n_samples),
        "yield_curve_10y2y": np.random.randn(n_samples) * 0.5,
    }, index=dates)


class TestRegimeKMeans:
    """Tests pour RegimeKMeans."""

    def test_init(self):
        """Test de l'initialisation."""
        model = RegimeKMeans(n_regimes=4)
        assert model.n_regimes == 4
        assert not model._is_fitted

    def test_fit(self, sample_regime_features):
        """Test de l'entraînement."""
        model = RegimeKMeans(n_regimes=4)
        model.fit(sample_regime_features)

        assert model._is_fitted
        assert model._regime_order is not None

    def test_predict(self, sample_regime_features):
        """Test de la prédiction."""
        model = RegimeKMeans(n_regimes=4)
        model.fit(sample_regime_features)

        labels = model.predict(sample_regime_features)

        assert len(labels) == len(sample_regime_features)
        assert set(labels).issubset({0, 1, 2, 3})

    def test_predict_series(self, sample_regime_features):
        """Test de predict_series."""
        model = RegimeKMeans(n_regimes=4)
        model.fit(sample_regime_features)

        series = model.predict_series(sample_regime_features)

        assert isinstance(series, pd.Series)
        assert len(series) == len(sample_regime_features)
        assert series.name == "regime"

    def test_get_regime_stats(self, sample_regime_features):
        """Test des statistiques par régime."""
        model = RegimeKMeans(n_regimes=4)
        model.fit(sample_regime_features)

        stats = model.get_regime_stats(sample_regime_features)

        assert isinstance(stats, pd.DataFrame)
        assert "regime" in stats.columns
        assert "name" in stats.columns
        assert "count" in stats.columns

    def test_not_fitted_error(self, sample_regime_features):
        """Test de l'erreur si modèle non entraîné."""
        model = RegimeKMeans(n_regimes=4)

        with pytest.raises(ValueError, match="entraîné"):
            model.predict(sample_regime_features)


class TestRegimeGMM:
    """Tests pour RegimeGMM."""

    def test_init(self):
        """Test de l'initialisation."""
        model = RegimeGMM(n_regimes=4)
        assert model.n_regimes == 4
        assert not model._is_fitted

    def test_fit(self, sample_regime_features):
        """Test de l'entraînement."""
        model = RegimeGMM(n_regimes=4)
        model.fit(sample_regime_features)

        assert model._is_fitted
        assert model._regime_order is not None

    def test_predict_proba(self, sample_regime_features):
        """Test des probabilités."""
        model = RegimeGMM(n_regimes=4)
        model.fit(sample_regime_features)

        proba = model.predict_proba(sample_regime_features)

        assert proba.shape == (len(sample_regime_features), 4)
        # Chaque ligne doit sommer à ~1
        assert np.allclose(proba.sum(axis=1), 1.0, atol=1e-5)

    def test_predict_proba_df(self, sample_regime_features):
        """Test du DataFrame de probabilités."""
        model = RegimeGMM(n_regimes=4)
        model.fit(sample_regime_features)

        proba_df = model.predict_proba_df(sample_regime_features)

        assert isinstance(proba_df, pd.DataFrame)
        assert len(proba_df.columns) == 4


class TestRegimeHMM:
    """Tests pour RegimeHMM."""

    def test_init(self):
        """Test de l'initialisation."""
        model = RegimeHMM(n_regimes=4)
        assert model.n_regimes == 4
        assert not model._is_fitted

    def test_fit(self, sample_regime_features):
        """Test de l'entraînement."""
        model = RegimeHMM(n_regimes=4)
        model.fit(sample_regime_features)

        assert model._is_fitted

    def test_get_transition_matrix(self, sample_regime_features):
        """Test de la matrice de transition."""
        model = RegimeHMM(n_regimes=4)
        model.fit(sample_regime_features)

        trans_mat = model.get_transition_matrix()

        assert isinstance(trans_mat, pd.DataFrame)
        assert trans_mat.shape == (4, 4)
        # Chaque ligne doit sommer à ~1
        assert np.allclose(trans_mat.sum(axis=1), 1.0, atol=1e-5)

    def test_get_stationary_distribution(self, sample_regime_features):
        """Test de la distribution stationnaire."""
        model = RegimeHMM(n_regimes=4)
        model.fit(sample_regime_features)

        dist = model.get_stationary_distribution()

        assert isinstance(dist, pd.Series)
        assert len(dist) == 4
        assert abs(dist.sum() - 1.0) < 0.1  # Devrait être proche de 1

    def test_get_log_likelihood(self, sample_regime_features):
        """Test de la log-vraisemblance."""
        model = RegimeHMM(n_regimes=4)
        model.fit(sample_regime_features)

        ll = model.get_log_likelihood(sample_regime_features)

        assert isinstance(ll, float)
        assert ll < 0  # Log-likelihood est négatif

    def test_stability(self, sample_regime_features):
        """Test que HMM produit des régimes stables."""
        model = RegimeHMM(n_regimes=4)
        model.fit(sample_regime_features)

        labels = model.predict(sample_regime_features)
        changes = np.sum(np.diff(labels) != 0)
        stability = 1 - (changes / len(labels))

        # HMM devrait être raisonnablement stable
        assert stability > 0.7


class TestModelComparison:
    """Tests comparant les 3 modèles."""

    def test_all_models_same_output_shape(self, sample_regime_features):
        """Vérifie que tous les modèles retournent la même shape."""
        models = [
            RegimeKMeans(n_regimes=4),
            RegimeGMM(n_regimes=4),
            RegimeHMM(n_regimes=4),
        ]

        for model in models:
            model.fit(sample_regime_features)
            labels = model.predict(sample_regime_features)
            assert len(labels) == len(sample_regime_features)

    def test_all_models_valid_labels(self, sample_regime_features):
        """Vérifie que tous les modèles retournent des labels valides."""
        models = [
            RegimeKMeans(n_regimes=4),
            RegimeGMM(n_regimes=4),
            RegimeHMM(n_regimes=4),
        ]

        for model in models:
            model.fit(sample_regime_features)
            labels = model.predict(sample_regime_features)
            assert set(labels).issubset({0, 1, 2, 3})
