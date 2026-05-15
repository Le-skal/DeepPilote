"""
Module ML DeepPilot.

Contient les modèles de détection de régime, prédiction de rendement,
et optimisation de portefeuille.

Structure :
- config: Constantes et paramètres
- features: Feature engineering et time splits
- models: Modèles ML (régime et prédiction)
- evaluation: Évaluation et comparaison
- portfolio: Benchmarks, optimiseur et backtesting
"""

from ml.config import (
    ETF_TICKERS,
    N_REGIMES,
    REGIME_NAMES,
    MIN_WEIGHT,
    MAX_WEIGHT,
    TRANSACTION_COST,
)

__all__ = [
    "ETF_TICKERS",
    "N_REGIMES",
    "REGIME_NAMES",
    "MIN_WEIGHT",
    "MAX_WEIGHT",
    "TRANSACTION_COST",
]
