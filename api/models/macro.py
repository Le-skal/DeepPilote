"""
Schemas Pydantic pour les indicateurs macro.

Définit les modèles de réponse pour les endpoints /macro/*
"""

from datetime import date as date_type

from pydantic import BaseModel, Field


class MacroIndicator(BaseModel):
    """Indicateurs macro à une date donnée."""

    date: date_type = Field(..., description="Date (YYYY-MM-DD)")

    # Volatilité
    vix: float | None = Field(None, description="VIX (indice de volatilité)")

    # Taux
    t3mo: float | None = Field(None, description="Taux 3 mois US Treasury")
    t10y: float | None = Field(None, description="Taux 10 ans US Treasury")
    yield_curve_10y2y: float | None = Field(None, description="Spread 10Y-2Y (courbe des taux)")

    # Crédit
    credit_spread: float | None = Field(None, description="Spread crédit High Yield")

    # Matières premières
    oil_wti: float | None = Field(None, description="Prix pétrole WTI (USD)")

    # Change
    usd_eur: float | None = Field(None, description="Taux USD/EUR")

    # Emploi / Inflation (mensuels)
    unemployment: float | None = Field(None, description="Taux de chômage US (%)")
    cpi: float | None = Field(None, description="CPI US (indice)")

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
    vix: float | None = Field(None, description="VIX")
    t3mo: float | None = Field(None, description="Taux 3 mois")
    t10y: float | None = Field(None, description="Taux 10 ans")
    yield_curve_10y2y: float | None = Field(None, description="Spread 10Y-2Y")
    credit_spread: float | None = Field(None, description="Spread crédit HY")
    oil_wti: float | None = Field(None, description="Pétrole WTI")


class MacroSummary(BaseModel):
    """Résumé des indicateurs macro (stats)."""

    indicator: str = Field(..., description="Nom de l'indicateur")
    current: float | None = Field(None, description="Valeur actuelle")
    mean: float | None = Field(None, description="Moyenne historique")
    std: float | None = Field(None, description="Écart-type")
    min: float | None = Field(None, description="Minimum historique")
    max: float | None = Field(None, description="Maximum historique")
    percentile: float | None = Field(None, description="Percentile actuel (0-100)")
