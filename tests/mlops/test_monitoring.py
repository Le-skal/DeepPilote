"""Tests pour le module mlops/monitoring.py."""

import pytest
import numpy as np
import pandas as pd

from mlops.monitoring import (
    calculate_psi,
    detect_data_drift,
    detect_prediction_drift,
    check_model_performance,
    ModelMonitor,
    DriftReport,
    PerformanceReport,
)


class TestPSI:
    """Tests pour le calcul du PSI."""

    def test_psi_identical_distributions(self):
        """PSI devrait être ~0 pour distributions identiques."""
        data = np.random.normal(0, 1, 1000)
        psi = calculate_psi(data, data)
        assert psi < 0.01

    def test_psi_similar_distributions(self):
        """PSI devrait être faible pour distributions similaires."""
        expected = np.random.normal(0, 1, 1000)
        actual = np.random.normal(0.05, 1.02, 1000)  # Très similaire
        psi = calculate_psi(expected, actual)
        assert psi < 0.1

    def test_psi_different_distributions(self):
        """PSI devrait être élevé pour distributions différentes."""
        expected = np.random.normal(0, 1, 1000)
        actual = np.random.normal(2, 2, 1000)  # Très différent
        psi = calculate_psi(expected, actual)
        assert psi > 0.25

    def test_psi_with_nan(self):
        """PSI devrait gérer les NaN."""
        expected = np.array([1, 2, 3, np.nan, 4, 5])
        actual = np.array([1.1, 2.1, 3.1, 4.1, np.nan, 5.1])
        psi = calculate_psi(expected, actual)
        assert psi >= 0

    def test_psi_empty_arrays(self):
        """PSI devrait retourner 0 pour arrays vides."""
        psi = calculate_psi(np.array([]), np.array([]))
        assert psi == 0.0


class TestDataDrift:
    """Tests pour la détection de drift des données."""

    @pytest.fixture
    def reference_data(self):
        """Données de référence."""
        np.random.seed(42)
        return pd.DataFrame({
            "feature_1": np.random.normal(0, 1, 500),
            "feature_2": np.random.uniform(0, 1, 500),
            "feature_3": np.random.exponential(1, 500),
        })

    def test_no_drift(self, reference_data):
        """Test sans drift (même distribution)."""
        np.random.seed(43)
        current_data = pd.DataFrame({
            "feature_1": np.random.normal(0, 1, 500),
            "feature_2": np.random.uniform(0, 1, 500),
            "feature_3": np.random.exponential(1, 500),
        })

        drift_detected, reports = detect_data_drift(
            reference_data, current_data, psi_threshold=0.25
        )

        # Pas de drift attendu (même distribution)
        assert len(reports) == 3
        # Au moins certains ne devraient pas avoir de drift
        no_drift_count = sum(1 for r in reports if not r.drift_detected)
        assert no_drift_count >= 2

    def test_with_drift(self, reference_data):
        """Test avec drift significatif."""
        np.random.seed(43)
        current_data = pd.DataFrame({
            "feature_1": np.random.normal(3, 2, 500),  # Drift fort
            "feature_2": np.random.uniform(0, 1, 500),  # Pas de drift
            "feature_3": np.random.exponential(1, 500),  # Pas de drift
        })

        drift_detected, reports = detect_data_drift(
            reference_data, current_data, psi_threshold=0.25
        )

        # Drift attendu sur feature_1
        feature_1_report = [r for r in reports if r.feature == "feature_1"][0]
        assert feature_1_report.drift_detected is True
        assert feature_1_report.psi > 0.25

    def test_drift_report_structure(self, reference_data):
        """Test la structure du DriftReport."""
        current_data = reference_data.copy()
        _, reports = detect_data_drift(reference_data, current_data)

        report = reports[0]
        assert isinstance(report, DriftReport)
        assert hasattr(report, "feature")
        assert hasattr(report, "drift_detected")
        assert hasattr(report, "psi")
        assert hasattr(report, "ks_statistic")
        assert hasattr(report, "ks_pvalue")
        assert hasattr(report, "timestamp")


class TestPredictionDrift:
    """Tests pour la détection de drift des prédictions."""

    def test_no_prediction_drift(self):
        """Test sans drift de prédictions."""
        np.random.seed(42)
        y_ref = np.random.binomial(1, 0.6, 500)
        y_cur = np.random.binomial(1, 0.6, 500)

        drift, psi = detect_prediction_drift(y_ref, y_cur, psi_threshold=0.25)
        assert psi < 0.25

    def test_with_prediction_drift(self):
        """Test avec drift de prédictions."""
        np.random.seed(42)
        y_ref = np.random.binomial(1, 0.3, 500)  # 30% positifs
        y_cur = np.random.binomial(1, 0.8, 500)  # 80% positifs

        drift, psi = detect_prediction_drift(y_ref, y_cur, psi_threshold=0.25)
        assert drift is True
        assert psi > 0.25


class TestPerformanceCheck:
    """Tests pour la vérification des performances."""

    def test_performance_ok(self):
        """Test avec métriques OK."""
        metrics = {"accuracy": 0.75, "auc": 0.80}
        thresholds = {"accuracy_min": 0.50, "auc_min": 0.60}

        report = check_model_performance(metrics, thresholds, "test_model")

        assert isinstance(report, PerformanceReport)
        assert report.has_alerts is False
        assert len(report.alerts) == 0

    def test_performance_below_threshold(self):
        """Test avec métriques sous le seuil."""
        metrics = {"accuracy": 0.45, "auc": 0.80}
        thresholds = {"accuracy_min": 0.50, "auc_min": 0.60}

        report = check_model_performance(metrics, thresholds, "test_model")

        assert report.has_alerts is True
        assert len(report.alerts) == 1
        assert "accuracy" in report.alerts[0]

    def test_performance_above_max_threshold(self):
        """Test avec métrique au-dessus du max."""
        metrics = {"max_drawdown": -0.45}
        thresholds = {"max_drawdown_max": -0.40}

        report = check_model_performance(metrics, thresholds, "test_model")

        assert report.has_alerts is True

    def test_missing_metric(self):
        """Test avec métrique manquante."""
        metrics = {"accuracy": 0.75}
        thresholds = {"accuracy_min": 0.50, "auc_min": 0.60}

        report = check_model_performance(metrics, thresholds, "test_model")

        assert report.has_alerts is True
        assert any("manquante" in alert for alert in report.alerts)


class TestModelMonitor:
    """Tests pour la classe ModelMonitor."""

    @pytest.fixture
    def monitor(self):
        """Crée un moniteur de test."""
        np.random.seed(42)
        X_ref = pd.DataFrame({
            "feature_1": np.random.normal(0, 1, 500),
            "feature_2": np.random.uniform(0, 1, 500),
        })
        thresholds = {"accuracy_min": 0.50}
        return ModelMonitor("test_model", X_ref, thresholds)

    def test_monitor_init(self, monitor):
        """Test initialisation du moniteur."""
        assert monitor.model_name == "test_model"
        assert len(monitor.drift_history) == 0
        assert len(monitor.performance_history) == 0

    def test_monitor_check_data(self, monitor):
        """Test vérification des données."""
        np.random.seed(43)
        X_current = pd.DataFrame({
            "feature_1": np.random.normal(0, 1, 500),
            "feature_2": np.random.uniform(0, 1, 500),
        })

        drift, reports = monitor.check_data(X_current)

        assert isinstance(drift, bool)
        assert len(reports) == 2
        assert len(monitor.drift_history) == 1

    def test_monitor_check_performance(self, monitor):
        """Test vérification des performances."""
        metrics = {"accuracy": 0.75}

        report = monitor.check_performance(metrics)

        assert isinstance(report, PerformanceReport)
        assert len(monitor.performance_history) == 1

    def test_monitor_get_status(self, monitor):
        """Test récupération du status."""
        status = monitor.get_status()

        assert status["model_name"] == "test_model"
        assert status["n_checks"] == 0
        assert status["drift_detected"] is False
