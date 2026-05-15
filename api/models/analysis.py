"""
Schemas Pydantic pour les analyses.

Définit les modèles de réponse pour les endpoints /analysis/*
"""

from datetime import date as date_type
from typing import Optional

from pydantic import BaseModel, Field


class CorrelationPair(BaseModel):
    """Corrélation entre deux ETF."""

    ticker_1: str = Field(..., description="Premier ETF")
    ticker_2: str = Field(..., description="Deuxième ETF")
    correlation: float = Field(..., description="Coefficient de corrélation (-1 à 1)")


class CorrelationMatrix(BaseModel):
    """Matrice de corrélation entre ETF."""

    start_date: date_type = Field(..., description="Date de début de la période")
    end_date: date_type = Field(..., description="Date de fin de la période")
    tickers: list[str] = Field(..., description="Liste des tickers")
    matrix: list[list[float]] = Field(..., description="Matrice de corrélation (NxN)")
    pairs: list[CorrelationPair] = Field(..., description="Corrélations par paire")


class ETFStats(BaseModel):
    """Statistiques descriptives pour un ETF."""

    ticker: str = Field(..., description="Symbole de l'ETF")
    start_date: date_type = Field(..., description="Date de début")
    end_date: date_type = Field(..., description="Date de fin")
    count: int = Field(..., description="Nombre d'observations")

    # Prix
    first_price: float = Field(..., description="Premier prix")
    last_price: float = Field(..., description="Dernier prix")
    min_price: float = Field(..., description="Prix minimum")
    max_price: float = Field(..., description="Prix maximum")

    # Returns
    total_return: float = Field(..., description="Return total (%)")
    annualized_return: float = Field(..., description="Return annualisé (%)")
    annualized_volatility: float = Field(..., description="Volatilité annualisée (%)")
    sharpe_ratio: Optional[float] = Field(None, description="Sharpe ratio (risk-free = T3MO)")

    # Risque
    max_drawdown: float = Field(..., description="Max drawdown (%)")
    skewness: float = Field(..., description="Skewness des returns")
    kurtosis: float = Field(..., description="Kurtosis des returns")

    # Distribution
    positive_days_pct: float = Field(..., description="% de jours positifs")
    best_day: float = Field(..., description="Meilleur jour (%)")
    worst_day: float = Field(..., description="Pire jour (%)")


class StatsResponse(BaseModel):
    """Réponse avec stats pour tous les ETF."""

    start_date: date_type
    end_date: date_type
    stats: list[ETFStats]


class HealthResponse(BaseModel):
    """Réponse du health check."""

    status: str = Field(..., description="Status de l'API")
    database: str = Field(..., description="Status de la base de données")
    version: str = Field(..., description="Version de l'API")
