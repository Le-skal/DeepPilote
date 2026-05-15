"""
Module MLOps pour DeepPilot.

Fournit :
- Tracking des expériences (MLflow)
- Model registry (versioning)
- Monitoring (drift detection)
"""

from mlops.config import MLflowConfig, MLFLOW_CONFIG, MODEL_NAMES, PERFORMANCE_THRESHOLDS

from mlops.tracking import (
    start_run,
    end_run,
    log_params,
    log_metrics,
    log_model,
    log_artifact,
    log_figure,
    log_dataframe,
    get_experiment_id,
    get_best_run,
    compare_runs,
)

from mlops.registry import (
    register_model,
    get_model_versions,
    get_latest_version,
    load_model,
    promote_model,
    archive_model,
    validate_model_for_promotion,
    get_production_models,
)

from mlops.monitoring import (
    calculate_psi,
    detect_data_drift,
    detect_prediction_drift,
    check_model_performance,
    ModelMonitor,
    DriftReport,
    PerformanceReport,
)

__all__ = [
    # Config
    "MLflowConfig",
    "MLFLOW_CONFIG",
    "MODEL_NAMES",
    "PERFORMANCE_THRESHOLDS",
    # Tracking
    "start_run",
    "end_run",
    "log_params",
    "log_metrics",
    "log_model",
    "log_artifact",
    "log_figure",
    "log_dataframe",
    "get_experiment_id",
    "get_best_run",
    "compare_runs",
    # Registry
    "register_model",
    "get_model_versions",
    "get_latest_version",
    "load_model",
    "promote_model",
    "archive_model",
    "validate_model_for_promotion",
    "get_production_models",
    # Monitoring
    "calculate_psi",
    "detect_data_drift",
    "detect_prediction_drift",
    "check_model_performance",
    "ModelMonitor",
    "DriftReport",
    "PerformanceReport",
]
# MLOps module
