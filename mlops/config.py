"""
Configuration MLflow pour DeepPilot.

Gère les paramètres de tracking et du model registry.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class MLflowConfig:
    """Configuration MLflow."""

    # URI de tracking (local par défaut)
    tracking_uri: str = os.getenv(
        "MLFLOW_TRACKING_URI",
        f"file:///{Path.cwd() / 'mlruns'}".replace("\\", "/")
    )

    # Nom de l'expérience par défaut
    default_experiment: str = "deeppilot"

    # Chemin des artifacts
    artifact_path: str = "models"

    # Expériences disponibles
    experiments: dict = None

    def __post_init__(self):
        """Initialise les expériences disponibles."""
        self.experiments = {
            "regime_detection": "deeppilot-regime",
            "return_prediction": "deeppilot-prediction",
            "portfolio_backtest": "deeppilot-backtest",
            "full_pipeline": "deeppilot-pipeline",
        }


# Instance globale
MLFLOW_CONFIG = MLflowConfig()

# Noms des modèles dans le registry
MODEL_NAMES = {
    "regime": "deeppilot-regime-hmm",
    "prediction": "deeppilot-prediction-rf",
    "strategy": "deeppilot-strategy",
}

# Stages du model registry
MODEL_STAGES = {
    "none": "None",
    "staging": "Staging",
    "production": "Production",
    "archived": "Archived",
}

# Seuils de performance minimaux pour promotion
PERFORMANCE_THRESHOLDS = {
    "regime": {
        "silhouette_min": 0.15,
        "stability_min": 0.90,
    },
    "prediction": {
        "accuracy_min": 0.52,
        "auc_min": 0.50,
    },
    "backtest": {
        "sharpe_min": 0.0,
        "max_drawdown_max": -0.40,  # Max DD ne doit pas dépasser -40%
    },
}
