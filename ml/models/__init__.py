"""
Module des modèles ML (régime et prédiction).

Modèles de régime :
- RegimeKMeans : K-Means clustering (baseline)
- RegimeGMM : Gaussian Mixture Model (probabiliste)
- RegimeHMM : Hidden Markov Model (choix final)

Modèles de prédiction :
- ReturnPredictorLogReg : Logistic Regression (baseline)
- ReturnPredictorXGBoost : XGBoost (alternative puissante)
- ReturnPredictorRF : Random Forest (choix final)
"""

from ml.models.regime_kmeans import RegimeKMeans
from ml.models.regime_gmm import RegimeGMM
from ml.models.regime_hmm import RegimeHMM
from ml.models.predict_logreg import ReturnPredictorLogReg
from ml.models.predict_xgboost import ReturnPredictorXGBoost
from ml.models.predict_rf import ReturnPredictorRF

__all__ = [
    # Régime
    "RegimeKMeans",
    "RegimeGMM",
    "RegimeHMM",
    # Prédiction
    "ReturnPredictorLogReg",
    "ReturnPredictorXGBoost",
    "ReturnPredictorRF",
]
