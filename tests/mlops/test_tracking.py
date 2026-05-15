"""Tests pour le module mlops/tracking.py."""

import pytest
import tempfile
import shutil
from pathlib import Path

import mlflow

from mlops.tracking import (
    get_or_create_experiment,
    get_experiment_id,
    start_run,
    log_params,
    log_metrics,
    get_best_run,
)
from mlops.config import MLFLOW_CONFIG


@pytest.fixture(scope="module")
def temp_mlflow_dir():
    """Crée un répertoire temporaire pour MLflow."""
    tmpdir = tempfile.mkdtemp()
    original_uri = MLFLOW_CONFIG.tracking_uri
    MLFLOW_CONFIG.tracking_uri = f"file:///{tmpdir}/mlruns".replace("\\", "/")
    mlflow.set_tracking_uri(MLFLOW_CONFIG.tracking_uri)
    yield tmpdir
    MLFLOW_CONFIG.tracking_uri = original_uri
    shutil.rmtree(tmpdir, ignore_errors=True)


class TestExperiments:
    """Tests pour la gestion des expériences."""

    def test_get_or_create_experiment_new(self, temp_mlflow_dir):
        """Test création d'une nouvelle expérience."""
        exp_id = get_or_create_experiment("test_experiment_new")
        assert exp_id is not None
        assert isinstance(exp_id, str)

    def test_get_or_create_experiment_existing(self, temp_mlflow_dir):
        """Test récupération d'une expérience existante."""
        exp_id1 = get_or_create_experiment("test_experiment_existing")
        exp_id2 = get_or_create_experiment("test_experiment_existing")
        assert exp_id1 == exp_id2

    def test_get_experiment_id_valid_key(self, temp_mlflow_dir):
        """Test récupération par clé valide."""
        exp_id = get_experiment_id("regime_detection")
        assert exp_id is not None

    def test_get_experiment_id_invalid_key(self, temp_mlflow_dir):
        """Test avec clé invalide (utilise default)."""
        exp_id = get_experiment_id("invalid_key")
        assert exp_id is not None


class TestRuns:
    """Tests pour la gestion des runs."""

    def test_start_run_basic(self, temp_mlflow_dir):
        """Test démarrage d'un run basique."""
        with start_run(experiment="regime_detection", run_name="test_run") as run:
            assert run is not None
            assert run.info.run_id is not None

    def test_start_run_with_tags(self, temp_mlflow_dir):
        """Test démarrage d'un run avec tags."""
        with start_run(
            experiment="regime_detection",
            run_name="test_run_tags",
            tags={"custom_tag": "value"},
        ) as run:
            assert run.data.tags.get("custom_tag") == "value"


class TestLogging:
    """Tests pour le logging."""

    def test_log_params(self, temp_mlflow_dir):
        """Test logging des paramètres."""
        with start_run(experiment="regime_detection", run_name="test_params"):
            log_params({
                "n_regimes": 4,
                "n_iter": 100,
                "random_state": 42,
            })
            # Pas d'erreur = succès

    def test_log_params_with_list(self, temp_mlflow_dir):
        """Test logging des paramètres avec liste."""
        with start_run(experiment="regime_detection", run_name="test_params_list"):
            log_params({
                "features": ["vix", "credit_spread"],
            })
            # Pas d'erreur = succès (converti en JSON)

    def test_log_metrics(self, temp_mlflow_dir):
        """Test logging des métriques."""
        with start_run(experiment="regime_detection", run_name="test_metrics"):
            log_metrics({
                "accuracy": 0.85,
                "auc": 0.72,
                "f1": 0.68,
            })
            # Pas d'erreur = succès

    def test_log_metrics_with_step(self, temp_mlflow_dir):
        """Test logging des métriques avec step."""
        with start_run(experiment="regime_detection", run_name="test_metrics_step"):
            for step in range(3):
                log_metrics({"loss": 1.0 - step * 0.1}, step=step)
            # Pas d'erreur = succès


class TestBestRun:
    """Tests pour la récupération du meilleur run."""

    def test_get_best_run_empty(self, temp_mlflow_dir):
        """Test get_best_run sur expérience vide."""
        result = get_best_run("full_pipeline", metric="accuracy")
        # Peut être None si pas de runs avec cette métrique
        assert result is None or isinstance(result, dict)

    def test_get_best_run_with_data(self, temp_mlflow_dir):
        """Test get_best_run avec des données."""
        # Créer quelques runs
        for i, acc in enumerate([0.7, 0.8, 0.75]):
            with start_run(experiment="full_pipeline", run_name=f"run_{i}"):
                log_metrics({"accuracy": acc})

        result = get_best_run("full_pipeline", metric="accuracy", mode="max")
        assert result is not None
        assert result["metrics"]["accuracy"] == 0.8
