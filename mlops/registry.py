"""
Module de Model Registry pour DeepPilot.

Gère le versioning et la promotion des modèles ML.

Workflow:
    1. Entraînement → log_model() → None (pas enregistré)
    2. Validation OK → register_model() → Staging
    3. Tests en prod OK → promote_model() → Production
    4. Nouveau modèle → archive_model() → Archived
"""

import logging
from typing import Optional, List, Dict, Any

import mlflow
from mlflow.tracking import MlflowClient
from mlflow.entities.model_registry import ModelVersion

from mlops.config import MLFLOW_CONFIG, MODEL_NAMES, MODEL_STAGES, PERFORMANCE_THRESHOLDS
from mlops.tracking import _init_mlflow

# Logger
logger = logging.getLogger(__name__)


def get_client() -> MlflowClient:
    """Retourne un client MLflow initialisé."""
    _init_mlflow()
    return MlflowClient()


def register_model(
    run_id: str,
    model_name: str,
    artifact_path: str = "models",
    tags: Optional[Dict[str, str]] = None,
) -> ModelVersion:
    """
    Enregistre un modèle depuis un run dans le registry.

    Args:
        run_id: ID du run MLflow
        model_name: Nom du modèle dans le registry
        artifact_path: Chemin de l'artifact du modèle
        tags: Tags additionnels

    Returns:
        ModelVersion créée
    """
    client = get_client()

    model_uri = f"runs:/{run_id}/{artifact_path}"

    # Enregistrer le modèle
    result = mlflow.register_model(model_uri, model_name)

    logger.info(f"Modèle enregistré: {model_name} v{result.version}")

    # Ajouter les tags si fournis
    if tags:
        for key, value in tags.items():
            client.set_model_version_tag(model_name, result.version, key, value)

    return result


def get_model_versions(model_name: str) -> List[ModelVersion]:
    """
    Liste toutes les versions d'un modèle.

    Args:
        model_name: Nom du modèle

    Returns:
        Liste des versions
    """
    client = get_client()

    try:
        versions = client.search_model_versions(f"name='{model_name}'")
        return list(versions)
    except Exception as e:
        logger.warning(f"Modèle non trouvé: {model_name} ({e})")
        return []


def get_latest_version(
    model_name: str,
    stage: str = "Production",
) -> Optional[ModelVersion]:
    """
    Récupère la dernière version d'un modèle dans un stage donné.

    Args:
        model_name: Nom du modèle
        stage: Stage (None, Staging, Production, Archived)

    Returns:
        ModelVersion ou None
    """
    client = get_client()

    try:
        versions = client.get_latest_versions(model_name, stages=[stage])
        return versions[0] if versions else None
    except Exception as e:
        logger.warning(f"Aucune version trouvée pour {model_name} en {stage}: {e}")
        return None


def load_model(
    model_name: str,
    stage: str = "Production",
    version: Optional[int] = None,
) -> Any:
    """
    Charge un modèle depuis le registry.

    Args:
        model_name: Nom du modèle
        stage: Stage à charger (ignoré si version spécifiée)
        version: Version spécifique (optionnel)

    Returns:
        Modèle chargé
    """
    _init_mlflow()

    if version:
        model_uri = f"models:/{model_name}/{version}"
    else:
        model_uri = f"models:/{model_name}/{stage}"

    logger.info(f"Chargement du modèle: {model_uri}")

    # Essayer sklearn d'abord, puis pyfunc
    try:
        model = mlflow.sklearn.load_model(model_uri)
    except Exception:
        try:
            model = mlflow.xgboost.load_model(model_uri)
        except Exception:
            model = mlflow.pyfunc.load_model(model_uri)

    return model


def promote_model(
    model_name: str,
    version: int,
    to_stage: str = "Production",
    archive_existing: bool = True,
) -> ModelVersion:
    """
    Promeut un modèle vers un nouveau stage.

    Args:
        model_name: Nom du modèle
        version: Version à promouvoir
        to_stage: Stage cible
        archive_existing: Si True, archive les modèles existants dans le stage cible

    Returns:
        ModelVersion mise à jour
    """
    client = get_client()

    # Archiver les modèles existants si demandé
    if archive_existing:
        existing = client.get_latest_versions(model_name, stages=[to_stage])
        for mv in existing:
            client.transition_model_version_stage(
                name=model_name,
                version=mv.version,
                stage="Archived",
            )
            logger.info(f"Modèle archivé: {model_name} v{mv.version}")

    # Promouvoir le nouveau modèle
    result = client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage=to_stage,
    )

    logger.info(f"Modèle promu: {model_name} v{version} → {to_stage}")

    return result


def archive_model(model_name: str, version: int) -> ModelVersion:
    """
    Archive une version de modèle.

    Args:
        model_name: Nom du modèle
        version: Version à archiver

    Returns:
        ModelVersion mise à jour
    """
    client = get_client()

    result = client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage="Archived",
    )

    logger.info(f"Modèle archivé: {model_name} v{version}")

    return result


def delete_model_version(model_name: str, version: int) -> None:
    """
    Supprime une version de modèle.

    Args:
        model_name: Nom du modèle
        version: Version à supprimer
    """
    client = get_client()
    client.delete_model_version(model_name, version)
    logger.info(f"Modèle supprimé: {model_name} v{version}")


def validate_model_for_promotion(
    model_name: str,
    version: int,
    model_type: str,
) -> tuple[bool, dict]:
    """
    Valide qu'un modèle respecte les seuils de performance.

    Args:
        model_name: Nom du modèle
        version: Version à valider
        model_type: Type de modèle (regime, prediction, backtest)

    Returns:
        Tuple (is_valid, validation_details)
    """
    client = get_client()

    # Récupérer les métriques du run associé
    model_version = client.get_model_version(model_name, str(version))
    run_id = model_version.run_id

    run = client.get_run(run_id)
    metrics = run.data.metrics

    # Vérifier les seuils
    thresholds = PERFORMANCE_THRESHOLDS.get(model_type, {})
    validation = {"passed": True, "checks": []}

    for threshold_name, threshold_value in thresholds.items():
        metric_name = threshold_name.replace("_min", "").replace("_max", "")
        actual_value = metrics.get(metric_name)

        if actual_value is None:
            check = {
                "metric": metric_name,
                "status": "MISSING",
                "message": f"Métrique {metric_name} non trouvée",
            }
            validation["passed"] = False
        elif threshold_name.endswith("_min"):
            passed = actual_value >= threshold_value
            check = {
                "metric": metric_name,
                "threshold": f">= {threshold_value}",
                "actual": actual_value,
                "status": "PASS" if passed else "FAIL",
            }
            if not passed:
                validation["passed"] = False
        elif threshold_name.endswith("_max"):
            passed = actual_value <= threshold_value
            check = {
                "metric": metric_name,
                "threshold": f"<= {threshold_value}",
                "actual": actual_value,
                "status": "PASS" if passed else "FAIL",
            }
            if not passed:
                validation["passed"] = False

        validation["checks"].append(check)

    return validation["passed"], validation


def get_model_lineage(model_name: str, version: int) -> dict:
    """
    Récupère la lignée d'un modèle (run, params, métriques).

    Args:
        model_name: Nom du modèle
        version: Version du modèle

    Returns:
        Dictionnaire avec les infos de lignée
    """
    client = get_client()

    model_version = client.get_model_version(model_name, str(version))
    run = client.get_run(model_version.run_id)

    return {
        "model_name": model_name,
        "version": version,
        "stage": model_version.current_stage,
        "run_id": model_version.run_id,
        "creation_time": model_version.creation_timestamp,
        "params": run.data.params,
        "metrics": run.data.metrics,
        "tags": run.data.tags,
    }


def list_registered_models() -> List[str]:
    """
    Liste tous les modèles enregistrés.

    Returns:
        Liste des noms de modèles
    """
    client = get_client()

    models = client.search_registered_models()
    return [m.name for m in models]


def get_production_models() -> Dict[str, Optional[ModelVersion]]:
    """
    Récupère tous les modèles en production.

    Returns:
        Dictionnaire {model_name: ModelVersion}
    """
    result = {}

    for model_key, model_name in MODEL_NAMES.items():
        version = get_latest_version(model_name, stage="Production")
        result[model_key] = version

    return result
