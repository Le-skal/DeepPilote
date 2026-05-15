"""
Module d'évaluation et comparaison des modèles.

Contient :
- Évaluation des modèles de régime (labels historiques, métriques clustering)
- Comparaison des modèles de prédiction (accuracy, AUC, F1)
"""

from ml.evaluation.regime_labels import (
    create_historical_labels,
    get_nber_recession_dates,
    add_recession_labels,
    get_crisis_periods,
    evaluate_regime_labels,
)
from ml.evaluation.compare_regime_models import (
    evaluate_regime_model,
    compare_all_regime_models,
    get_best_regime_model,
    plot_regime_comparison,
)
from ml.evaluation.compare_prediction_models import (
    evaluate_prediction_model,
    compare_all_prediction_models,
    get_best_prediction_model,
    walk_forward_comparison,
    get_feature_importance_comparison,
)

__all__ = [
    # Regime labels
    "create_historical_labels",
    "get_nber_recession_dates",
    "add_recession_labels",
    "get_crisis_periods",
    "evaluate_regime_labels",
    # Regime comparison
    "evaluate_regime_model",
    "compare_all_regime_models",
    "get_best_regime_model",
    "plot_regime_comparison",
    # Prediction comparison
    "evaluate_prediction_model",
    "compare_all_prediction_models",
    "get_best_prediction_model",
    "walk_forward_comparison",
    "get_feature_importance_comparison",
]
