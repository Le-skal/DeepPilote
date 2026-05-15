"""
Tests pour les modèles de prédiction de rendement.

Teste LogReg, XGBoost et Random Forest.
"""

import numpy as np
import pandas as pd
import pytest

from ml.models.predict_logreg import ReturnPredictorLogReg
from ml.models.predict_xgboost import ReturnPredictorXGBoost
from ml.models.predict_rf import ReturnPredictorRF


@pytest.fixture
def sample_prediction_data():
    """Génère des données de prédiction synthétiques."""
    np.random.seed(42)
    n_samples = 500

    dates = pd.date_range("2020-01-01", periods=n_samples, freq="D")

    # Features de prédiction
    X = pd.DataFrame({
        "return_lag_1": np.random.randn(n_samples) * 0.02,
        "return_lag_5": np.random.randn(n_samples) * 0.03,
        "sma_20_ratio": np.random.randn(n_samples) * 0.1 + 1,
        "sma_50_ratio": np.random.randn(n_samples) * 0.15 + 1,
        "rsi_14": np.random.uniform(30, 70, n_samples),
        "macd_signal": np.random.randn(n_samples) * 0.01,
        "bollinger_position": np.random.uniform(-1, 1, n_samples),
        "regime": np.random.choice([0, 1, 2, 3], n_samples),
    }, index=dates)

    # Target binaire avec un peu de signal
    signal = 0.3 * (X["sma_20_ratio"] > 1).astype(float) + 0.2 * (X["rsi_14"] > 50).astype(float)
    y = (signal + np.random.randn(n_samples) * 0.3 > 0.5).astype(int)
    y = pd.Series(y, index=dates, name="target")

    return X, y


@pytest.fixture
def train_test_split(sample_prediction_data):
    """Split train/test pour les données."""
    X, y = sample_prediction_data

    train_size = int(len(X) * 0.7)
    X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
    y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]

    return X_train, X_test, y_train, y_test


class TestReturnPredictorLogReg:
    """Tests pour ReturnPredictorLogReg."""

    def test_init(self):
        """Test de l'initialisation."""
        model = ReturnPredictorLogReg()
        assert not model._is_fitted

    def test_fit(self, train_test_split):
        """Test de l'entraînement."""
        X_train, X_test, y_train, y_test = train_test_split

        model = ReturnPredictorLogReg()
        model.fit(X_train, y_train)

        assert model._is_fitted
        assert model._feature_names is not None

    def test_predict(self, train_test_split):
        """Test de la prédiction."""
        X_train, X_test, y_train, y_test = train_test_split

        model = ReturnPredictorLogReg()
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)

        assert len(predictions) == len(X_test)
        assert set(predictions).issubset({0, 1})

    def test_predict_proba(self, train_test_split):
        """Test des probabilités."""
        X_train, X_test, y_train, y_test = train_test_split

        model = ReturnPredictorLogReg()
        model.fit(X_train, y_train)

        proba = model.predict_proba(X_test)

        assert proba.shape == (len(X_test), 2)
        assert np.allclose(proba.sum(axis=1), 1.0)
        assert (proba >= 0).all() and (proba <= 1).all()

    def test_get_coefficients(self, train_test_split):
        """Test des coefficients."""
        X_train, X_test, y_train, y_test = train_test_split

        model = ReturnPredictorLogReg()
        model.fit(X_train, y_train)

        coefs = model.get_coefficients()

        assert isinstance(coefs, pd.Series)
        assert len(coefs) == X_train.shape[1]

    def test_get_feature_importance(self, train_test_split):
        """Test de l'importance des features."""
        X_train, X_test, y_train, y_test = train_test_split

        model = ReturnPredictorLogReg()
        model.fit(X_train, y_train)

        importance = model.get_feature_importance()

        assert isinstance(importance, pd.DataFrame)
        assert "feature" in importance.columns
        assert "importance" in importance.columns


class TestReturnPredictorXGBoost:
    """Tests pour ReturnPredictorXGBoost."""

    def test_init(self):
        """Test de l'initialisation."""
        model = ReturnPredictorXGBoost()
        assert not model._is_fitted

    def test_fit(self, train_test_split):
        """Test de l'entraînement."""
        X_train, X_test, y_train, y_test = train_test_split

        model = ReturnPredictorXGBoost()
        model.fit(X_train, y_train)

        assert model._is_fitted

    def test_predict(self, train_test_split):
        """Test de la prédiction."""
        X_train, X_test, y_train, y_test = train_test_split

        model = ReturnPredictorXGBoost()
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)

        assert len(predictions) == len(X_test)
        assert set(predictions).issubset({0, 1})

    def test_feature_importance(self, train_test_split):
        """Test de l'importance des features."""
        X_train, X_test, y_train, y_test = train_test_split

        model = ReturnPredictorXGBoost()
        model.fit(X_train, y_train)

        importance = model.get_feature_importance()

        assert isinstance(importance, pd.DataFrame)
        assert "feature" in importance.columns

    def test_feature_importance_sklearn(self, train_test_split):
        """Test de l'importance format sklearn."""
        X_train, X_test, y_train, y_test = train_test_split

        model = ReturnPredictorXGBoost()
        model.fit(X_train, y_train)

        importance = model.get_feature_importance_sklearn()

        assert isinstance(importance, pd.Series)
        assert len(importance) == X_train.shape[1]


class TestReturnPredictorRF:
    """Tests pour ReturnPredictorRF."""

    def test_init(self):
        """Test de l'initialisation."""
        model = ReturnPredictorRF()
        assert not model._is_fitted

    def test_fit(self, train_test_split):
        """Test de l'entraînement."""
        X_train, X_test, y_train, y_test = train_test_split

        model = ReturnPredictorRF()
        model.fit(X_train, y_train)

        assert model._is_fitted

    def test_predict(self, train_test_split):
        """Test de la prédiction."""
        X_train, X_test, y_train, y_test = train_test_split

        model = ReturnPredictorRF()
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)

        assert len(predictions) == len(X_test)
        assert set(predictions).issubset({0, 1})

    def test_predict_series(self, train_test_split):
        """Test de predict_series."""
        X_train, X_test, y_train, y_test = train_test_split

        model = ReturnPredictorRF()
        model.fit(X_train, y_train)

        series = model.predict_series(X_test)

        assert isinstance(series, pd.Series)
        assert len(series) == len(X_test)
        assert series.name == "prediction"

    def test_predict_proba_series(self, train_test_split):
        """Test de predict_proba_series."""
        X_train, X_test, y_train, y_test = train_test_split

        model = ReturnPredictorRF()
        model.fit(X_train, y_train)

        proba_series = model.predict_proba_series(X_test)

        assert isinstance(proba_series, pd.Series)
        assert len(proba_series) == len(X_test)
        assert (proba_series >= 0).all() and (proba_series <= 1).all()

    def test_feature_importance(self, train_test_split):
        """Test de l'importance des features."""
        X_train, X_test, y_train, y_test = train_test_split

        model = ReturnPredictorRF()
        model.fit(X_train, y_train)

        importance = model.get_feature_importance()

        assert isinstance(importance, pd.DataFrame)
        assert "feature" in importance.columns
        assert "importance" in importance.columns
        # Importances doivent sommer à ~1
        assert abs(importance["importance"].sum() - 1.0) < 0.01

    def test_get_tree_depths(self, train_test_split):
        """Test des profondeurs d'arbres."""
        X_train, X_test, y_train, y_test = train_test_split

        model = ReturnPredictorRF()
        model.fit(X_train, y_train)

        depths = model.get_tree_depths()

        assert "min" in depths
        assert "max" in depths
        assert "mean" in depths
        assert depths["min"] <= depths["mean"] <= depths["max"]

    def test_get_params_summary(self, train_test_split):
        """Test du résumé des paramètres."""
        X_train, X_test, y_train, y_test = train_test_split

        model = ReturnPredictorRF()
        model.fit(X_train, y_train)

        params = model.get_params_summary()

        assert "n_estimators" in params
        assert "max_depth" in params
        assert params["n_features"] == X_train.shape[1]


class TestModelComparison:
    """Tests comparant les 3 modèles."""

    def test_all_models_same_output_shape(self, train_test_split):
        """Vérifie que tous les modèles retournent la même shape."""
        X_train, X_test, y_train, y_test = train_test_split

        models = [
            ReturnPredictorLogReg(),
            ReturnPredictorXGBoost(),
            ReturnPredictorRF(),
        ]

        for model in models:
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            proba = model.predict_proba(X_test)

            assert len(preds) == len(X_test)
            assert proba.shape == (len(X_test), 2)

    def test_all_models_valid_probabilities(self, train_test_split):
        """Vérifie que tous les modèles retournent des probabilités valides."""
        X_train, X_test, y_train, y_test = train_test_split

        models = [
            ReturnPredictorLogReg(),
            ReturnPredictorXGBoost(),
            ReturnPredictorRF(),
        ]

        for model in models:
            model.fit(X_train, y_train)
            proba = model.predict_proba(X_test)

            # Probas entre 0 et 1
            assert (proba >= 0).all() and (proba <= 1).all()
            # Somme à 1
            assert np.allclose(proba.sum(axis=1), 1.0)

    def test_not_fitted_error(self, train_test_split):
        """Vérifie l'erreur si modèle non entraîné."""
        X_train, X_test, y_train, y_test = train_test_split

        models = [
            ReturnPredictorLogReg(),
            ReturnPredictorXGBoost(),
            ReturnPredictorRF(),
        ]

        for model in models:
            with pytest.raises(ValueError, match="entraîné"):
                model.predict(X_test)
