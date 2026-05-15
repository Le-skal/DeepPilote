"""
Schemas Pydantic pour les ETF.

Définit les modèles de réponse pour les endpoints /etfs/*
"""

from datetime import date as date_type
from typing import Optional

from pydantic import BaseModel, Field


class ETFBase(BaseModel):
    """Métadonnées d'un ETF."""

    ticker: str = Field(..., description="Symbole de l'ETF (ex: SPY)")
    name: str = Field(..., description="Nom complet de l'ETF")
    asset_class: str = Field(..., description="Classe d'actifs")
    description: Optional[str] = Field(None, description="Description du rôle dans le portefeuille")

    model_config = {"from_attributes": True}


class ETFPrice(BaseModel):
    """Prix d'un ETF à une date donnée."""

    date: date_type = Field(..., description="Date du prix (YYYY-MM-DD)")
    ticker: str = Field(..., description="Symbole de l'ETF")
    open: Optional[float] = Field(None, description="Prix d'ouverture")
    high: Optional[float] = Field(None, description="Prix le plus haut")
    low: Optional[float] = Field(None, description="Prix le plus bas")
    close: float = Field(..., description="Prix de clôture ajusté")
    volume: Optional[int] = Field(None, description="Volume échangé")

    model_config = {"from_attributes": True}


class ETFPriceList(BaseModel):
    """Liste de prix pour un ETF."""

    ticker: str = Field(..., description="Symbole de l'ETF")
    start_date: date_type = Field(..., description="Date de début")
    end_date: date_type = Field(..., description="Date de fin")
    count: int = Field(..., description="Nombre de prix retournés")
    prices: list[ETFPrice] = Field(..., description="Liste des prix")


class ETFFeature(BaseModel):
    """Features calculées pour un ETF à une date donnée."""

    date: date_type = Field(..., description="Date")
    ticker: str = Field(..., description="Symbole de l'ETF")

    # Returns
    return_1d: Optional[float] = Field(None, description="Return 1 jour (%)")
    return_5d: Optional[float] = Field(None, description="Return 5 jours (%)")
    return_20d: Optional[float] = Field(None, description="Return 20 jours (%)")
    return_60d: Optional[float] = Field(None, description="Return 60 jours (%)")

    # Volatilité
    volatility_20d: Optional[float] = Field(None, description="Volatilité 20 jours")
    volatility_60d: Optional[float] = Field(None, description="Volatilité 60 jours")

    # Indicateurs techniques
    sma_20: Optional[float] = Field(None, description="SMA 20 jours")
    sma_50: Optional[float] = Field(None, description="SMA 50 jours")
    sma_200: Optional[float] = Field(None, description="SMA 200 jours")
    rsi_14: Optional[float] = Field(None, description="RSI 14 jours")
    macd: Optional[float] = Field(None, description="MACD")
    macd_signal: Optional[float] = Field(None, description="Signal MACD")
    bb_position: Optional[float] = Field(None, description="Position Bollinger (0-1)")

    model_config = {"from_attributes": True}


class ETFFeatureList(BaseModel):
    """Liste de features pour un ETF."""

    ticker: str
    start_date: date_type
    end_date: date_type
    count: int
    features: list[ETFFeature]


class ETFListResponse(BaseModel):
    """Réponse pour la liste des ETF."""

    count: int = Field(..., description="Nombre d'ETF")
    etfs: list[ETFBase] = Field(..., description="Liste des ETF")
