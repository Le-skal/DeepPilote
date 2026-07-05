"""
Modèles Pydantic pour les endpoints ML.
"""

from pydantic import BaseModel, Field


class RegimeResponse(BaseModel):
    """Régime de marché actuel."""

    regime: str = Field(..., description="Nom du régime (bull, bear, volatile, stable)")
    regime_id: int = Field(..., description="ID du régime (0-3)")
    confidence: float = Field(..., ge=0, le=1, description="Confiance de la prédiction")
    as_of_date: str = Field(..., description="Date de la dernière donnée")
    probabilities: dict[str, float] = Field(..., description="Probabilités pour chaque régime")


class PortfolioWeights(BaseModel):
    """Poids optimaux du portefeuille."""

    weights: dict[str, float] = Field(..., description="Poids par ETF")
    expected_return: float = Field(..., description="Return attendu annualisé")
    volatility: float = Field(..., description="Volatilité annualisée")
    sharpe_ratio: float = Field(..., description="Ratio de Sharpe")
    regime: str = Field(..., description="Régime utilisé pour l'optimisation")
    as_of_date: str = Field(..., description="Date de l'optimisation")


class PortfolioStats(BaseModel):
    """Statistiques du portefeuille."""

    expected_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float | None = None
