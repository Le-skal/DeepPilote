"""
Module de tracking MLflow pour DeepPilot.

Fournit des wrappers simples pour logger les expériences ML.

Usage:
    from mlops.tracking import start_run, log_params, log_metrics, log_model

    with start_run(experiment="regime_detection", run_name="hmm_v1"):
        log_params({"n_regimes": 4, "n_iter": 100})
        model.fit(X_train)
        log_metrics({"silhouette": 0.25, "stability": 0.98})
        log_model(model, "regime_hmm")
"""

import logging
from pathlib import Path
from typing import Any, Optional, Dict, Union
from contextlib import contextmanager
import tempfile
import json

import mlflow
from mlflow.tracking import MlflowClient

from mlops.config import MLFLOW_CONFIG, MODEL_NAMES

# Logger
logger = logging.getLogger(__name__)


def _init_mlflow() -> None:
    """Initialise MLflow avec la configuration."""
    mlflow.set_tracking_uri(MLFLOW_CONFIG.tracking_uri)
    logger.info(f"MLflow tracking URI: {MLFLOW_CONFIG.tracking_uri}")


def get_or_create_experiment(name: str) -> str:
    """
    Récupère ou crée une expérience MLflow.

    Args:
        name: Nom de l'expérience

    Returns:
        ID de l'expérience
    """
    _init_mlflow()

    experiment = mlflow.get_experiment_by_name(name)
    if experiment is None:
        experiment_id = mlflow.create_experiment(name)
        logger.info(f"Expérience créée: {name} (ID: {experiment_id})")
    else:
        experiment_id = experiment.experiment_id
        logger.info(f"Expérience existante: {name} (ID: {experiment_id})")

    return experiment_id


def get_experiment_id(experiment_key: str) -> str:
    """
    Récupère l'ID d'une expérience par sa clé.

    Args:
        experiment_key: Clé de l'expérience (ex: "regime_detection")

    Returns:
        ID de l'expérience MLflow
    """
    experiment_name = MLFLOW_CONFIG.experiments.get(
        experiment_key, MLFLOW_CONFIG.default_experiment
    )
    return get_or_create_experiment(experiment_name)


@contextmanager
def start_run(
    experiment: str = "full_pipeline",
    run_name: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    nested: bool = False,
):
    """
    Context manager pour démarrer un run MLflow.

    Args:
        experiment: Clé de l'expérience (regime_detection, return_prediction, etc.)
        run_name: Nom du run (optionnel)
        tags: Tags additionnels
        nested: Si True, permet les runs imbriqués

    Yields:
        mlflow.ActiveRun

    Example:
        with start_run(experiment="regime_detection", run_name="hmm_v1") as run:
            log_params({"n_regimes": 4})
            # ... training ...
            log_metrics({"accuracy": 0.85})
    """
    _init_mlflow()

    experiment_id = get_experiment_id(experiment)
    mlflow.set_experiment(experiment_id=experiment_id)

    # Tags par défaut
    default_tags = {
        "project": "deeppilot",
        "experiment_type": experiment,
    }
    if tags:
        default_tags.update(tags)

    with mlflow.start_run(run_name=run_name, tags=default_tags, nested=nested) as run:
        logger.info(f"Run démarré: {run.info.run_id}")
        yield run

    logger.info(f"Run terminé: {run.info.run_id}")


def end_run(status: str = "FINISHED") -> None:
    """
    Termine le run actif.

    Args:
        status: Status du run (FINISHED, FAILED, KILLED)
    """
    mlflow.end_run(status=status)


def log_params(params: Dict[str, Any]) -> None:
    """
    Log les hyperparamètres.

    Args:
        params: Dictionnaire de paramètres

    Example:
        log_params({
            "n_regimes": 4,
            "n_iter": 100,
            "random_state": 42,
        })
    """
    # MLflow n'accepte que des valeurs simples
    clean_params = {}
    for key, value in params.items():
        if isinstance(value, (list, dict)):
            clean_params[key] = json.dumps(value)
        else:
            clean_params[key] = value

    mlflow.log_params(clean_params)
    logger.debug(f"Params logged: {list(params.keys())}")


def log_metrics(metrics: Dict[str, float], step: Optional[int] = None) -> None:
    """
    Log les métriques.

    Args:
        metrics: Dictionnaire de métriques
        step: Étape (pour les métriques temporelles)

    Example:
        log_metrics({
            "accuracy": 0.85,
            "auc": 0.72,
            "f1": 0.68,
        })
    """
    # S'assurer que les valeurs sont des floats
    clean_metrics = {k: float(v) for k, v in metrics.items() if v is not None}

    mlflow.log_metrics(clean_metrics, step=step)
    logger.debug(f"Metrics logged: {clean_metrics}")


def log_model(
    model: Any,
    model_name: str,
    model_type: str = "sklearn",
    registered_name: Optional[str] = None,
) -> None:
    """
    Log un modèle entraîné.

    Args:
        model: Modèle entraîné
        model_name: Nom de l'artifact (sans caractères spéciaux)
        model_type: Type de modèle (sklearn, xgboost, custom)
        registered_name: Nom pour le model registry (optionnel)

    Example:
        log_model(rf_model, "random_forest", model_type="sklearn")
    """
    # artifact_path ne doit pas contenir de /
    artifact_path = model_name

    if model_type == "sklearn":
        mlflow.sklearn.log_model(
            model,
            artifact_path,
            registered_model_name=registered_name,
        )
    elif model_type == "xgboost":
        mlflow.xgboost.log_model(
            model,
            artifact_path,
            registered_model_name=registered_name,
        )
    else:
        # Pour les modèles custom (HMM, etc.), on utilise pickle
        mlflow.pyfunc.log_model(
            artifact_path,
            python_model=model,
            registered_model_name=registered_name,
        )

    logger.info(f"Modèle loggé: {model_name} (type: {model_type})")


def log_artifact(filepath: Union[str, Path], artifact_path: Optional[str] = None) -> None:
    """
    Log un fichier artifact (CSV, plot, etc.).

    Args:
        filepath: Chemin du fichier
        artifact_path: Sous-dossier dans les artifacts

    Example:
        log_artifact("results/metrics.csv", artifact_path="results")
    """
    mlflow.log_artifact(str(filepath), artifact_path=artifact_path)
    logger.info(f"Artifact loggé: {filepath}")


def log_figure(fig, filename: str, artifact_path: str = "plots") -> None:
    """
    Log une figure matplotlib.

    Args:
        fig: Figure matplotlib
        filename: Nom du fichier (avec extension)
        artifact_path: Sous-dossier dans les artifacts
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / filename
        fig.savefig(filepath, dpi=150, bbox_inches="tight")
        log_artifact(filepath, artifact_path=artifact_path)


def log_dataframe(df, filename: str, artifact_path: str = "data") -> None:
    """
    Log un DataFrame pandas.

    Args:
        df: DataFrame pandas
        filename: Nom du fichier (avec extension .csv)
        artifact_path: Sous-dossier dans les artifacts
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / filename
        df.to_csv(filepath, index=True)
        log_artifact(filepath, artifact_path=artifact_path)


def log_dict(data: dict, filename: str, artifact_path: str = "config") -> None:
    """
    Log un dictionnaire en JSON.

    Args:
        data: Dictionnaire à logger
        filename: Nom du fichier (avec extension .json)
        artifact_path: Sous-dossier dans les artifacts
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / filename
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)
        log_artifact(filepath, artifact_path=artifact_path)


def get_best_run(
    experiment: str,
    metric: str,
    mode: str = "max",
) -> Optional[dict]:
    """
    Récupère le meilleur run d'une expérience.

    Args:
        experiment: Clé de l'expérience
        metric: Métrique à optimiser
        mode: "max" ou "min"

    Returns:
        Dictionnaire avec les infos du meilleur run
    """
    _init_mlflow()
    client = MlflowClient()

    experiment_id = get_experiment_id(experiment)
    order = "DESC" if mode == "max" else "ASC"

    runs = client.search_runs(
        experiment_ids=[experiment_id],
        order_by=[f"metrics.{metric} {order}"],
        max_results=1,
    )

    if not runs:
        return None

    best_run = runs[0]
    return {
        "run_id": best_run.info.run_id,
        "metrics": best_run.data.metrics,
        "params": best_run.data.params,
        "tags": best_run.data.tags,
    }


def compare_runs(
    experiment: str,
    metric: str,
    n_runs: int = 5,
) -> list:
    """
    Compare les derniers runs d'une expérience.

    Args:
        experiment: Clé de l'expérience
        metric: Métrique principale
        n_runs: Nombre de runs à comparer

    Returns:
        Liste de dictionnaires avec les infos des runs
    """
    _init_mlflow()
    client = MlflowClient()

    experiment_id = get_experiment_id(experiment)

    runs = client.search_runs(
        experiment_ids=[experiment_id],
        order_by=[f"metrics.{metric} DESC"],
        max_results=n_runs,
    )

    return [
        {
            "run_id": run.info.run_id,
            "run_name": run.data.tags.get("mlflow.runName", "N/A"),
            "metrics": run.data.metrics,
            "params": run.data.params,
        }
        for run in runs
    ]
