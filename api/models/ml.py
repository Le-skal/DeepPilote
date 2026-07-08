"""
Modèles Pydantic pour les endpoints ML.
"""

from enum import StrEnum

from pydantic import BaseModel, Field

# Noms lisibles pour les tickers
TICKER_DISPLAY_NAMES = {
    "SPY": "S&P 500",
    "QQQ": "NASDAQ 100",
    "EFA": "Actions Internationales",
    "EEM": "Marchés Émergents",
    "TLT": "Obligations US Long Terme",
    "HYG": "Obligations Haut Rendement",
    "GLD": "Or",
    "VNQ": "Immobilier US",
    "SH": "Short S&P 500",
    "URTH": "MSCI World",
}


class SignalType(StrEnum):
    """Type de signal de trading."""

    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


# Configuration des signaux
SIGNAL_CONFIG = {
    SignalType.STRONG_BUY: {
        "label": "Achat fort",
        "emoji": "🚀",
        "explanation": "Signal très positif - Tendance haussière forte",
        "threshold": 0.70,
    },
    SignalType.BUY: {
        "label": "Achat",
        "emoji": "📈",
        "explanation": "Signal positif - Tendance favorable",
        "threshold": 0.55,
    },
    SignalType.HOLD: {
        "label": "Conserver",
        "emoji": "⏸️",
        "explanation": "Signal neutre - Pas de direction claire",
        "threshold": 0.45,
    },
    SignalType.SELL: {
        "label": "Vente",
        "emoji": "📉",
        "explanation": "Signal négatif - Tendance défavorable",
        "threshold": 0.30,
    },
    SignalType.STRONG_SELL: {
        "label": "Vente forte",
        "emoji": "🔻",
        "explanation": "Signal très négatif - Risque de baisse élevé",
        "threshold": 0.0,
    },
}


def probability_to_signal(prob: float) -> SignalType:
    """Convertit une probabilité en signal."""
    if prob >= 0.70:
        return SignalType.STRONG_BUY
    elif prob >= 0.55:
        return SignalType.BUY
    elif prob >= 0.45:
        return SignalType.HOLD
    elif prob >= 0.30:
        return SignalType.SELL
    else:
        return SignalType.STRONG_SELL


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


class TickerPrediction(BaseModel):
    """Prédiction pour un ticker."""

    ticker: str = Field(..., description="Code du ticker (ex: SPY)")
    display_name: str = Field(..., description="Nom lisible (ex: S&P 500)")
    probability: float = Field(
        ..., ge=0, le=1, description="Probabilité de rendement positif (0-1)"
    )
    signal: SignalType = Field(..., description="Signal de trading")
    signal_label: str = Field(..., description="Label du signal en français")
    signal_emoji: str = Field(..., description="Emoji du signal")
    signal_explanation: str = Field(..., description="Explication du signal")


class PredictionsResponse(BaseModel):
    """Réponse avec toutes les prédictions."""

    predictions: list[TickerPrediction] = Field(
        ..., description="Prédictions par ticker, triées par probabilité décroissante"
    )
    top_picks: list[str] = Field(..., description="Top 3 tickers recommandés")
    regime: str = Field(..., description="Régime de marché actuel")
    regime_explanation: str = Field(
        ..., description="Ce que le régime signifie pour l'investissement"
    )
    as_of: str = Field(..., description="Date des prédictions")
    model_info: dict = Field(..., description="Informations sur les modèles utilisés")
