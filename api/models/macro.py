"""
Schemas Pydantic pour les indicateurs macro.

Définit les modèles de réponse pour les endpoints /macro/*
"""

from datetime import date as date_type
from typing import Optional

from pydantic import BaseModel, Field


class MacroIndicator(BaseModel):
    """Indicateurs macro à une date donnée."""

    date: date_type = Field(..., description="Date (YYYY-MM-DD)")

    # Volatilité
    vix: Optional[float] = Field(None, description="VIX (indice de volatilité)")

    # Taux
    t3mo: Optional[float] = Field(None, description="Taux 3 mois US Treasury")
    t10y: Optional[float] = Field(None, description="Taux 10 ans US Treasury")
    yield_curve_10y2y: Optional[float] = Field(None, description="Spread 10Y-2Y (courbe des taux)")

    # Crédit
    credit_spread: Optional[float] = Field(None, description="Spread crédit High Yield")

    # Matières premières
    oil_wti: Optional[float] = Field(None, description="Prix pétrole WTI (USD)")

    # Change
    usd_eur: Optional[float] = Field(None, description="Taux USD/EUR")

    # Emploi / Inflation (mensuels)
    unemployment: Optional[float] = Field(None, description="Taux de chômage US (%)")
    cpi: Optional[float] = Field(None, description="CPI US (indice)")

    model_config = {"from_attributes": True}


class MacroIndicatorList(BaseModel):
    """Liste d'indicateurs macro."""

    start_date: date_type = Field(..., description="Date de début")
    end_date: date_type = Field(..., description="Date de fin")
    count: int = Field(..., description="Nombre d'enregistrements")
    indicators: list[MacroIndicator] = Field(..., description="Liste des indicateurs")


class MacroLatest(BaseModel):
    """Dernières valeurs connues des indicateurs macro."""

    as_of_date: date_type = Field(..., description="Date des dernières données")
    vix: Optional[float] = Field(None, description="VIX")
    t3mo: Optional[float] = Field(None, description="Taux 3 mois")
    t10y: Optional[float] = Field(None, description="Taux 10 ans")
    yield_curve_10y2y: Optional[float] = Field(None, description="Spread 10Y-2Y")
    credit_spread: Optional[float] = Field(None, description="Spread crédit HY")
    oil_wti: Optional[float] = Field(None, description="Pétrole WTI")


class MacroSummary(BaseModel):
    """Résumé des indicateurs macro (stats)."""

    indicator: str = Field(..., description="Nom de l'indicateur")
    current: Optional[float] = Field(None, description="Valeur actuelle")
    mean: Optional[float] = Field(None, description="Moyenne historique")
    std: Optional[float] = Field(None, description="Écart-type")
    min: Optional[float] = Field(None, description="Minimum historique")
    max: Optional[float] = Field(None, description="Maximum historique")
    percentile: Optional[float] = Field(None, description="Percentile actuel (0-100)")
