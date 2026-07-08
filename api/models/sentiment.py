"""
Schemas Pydantic pour l'API Sentiment.

Expose l'analyse de sentiment Mistral via API REST.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class SentimentRequest(BaseModel):
    """Requête pour analyser des headlines."""

    headlines: list[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Liste de headlines à analyser (1-10)",
        examples=[["S&P 500 rallies to new highs", "Fed raises rates amid inflation fears"]],
    )


class SentimentResult(BaseModel):
    """Résultat d'analyse pour un headline."""

    headline: str = Field(..., description="Le headline analysé")
    score: float = Field(..., ge=-1, le=1, description="Score de sentiment (-1 à +1)")
    label: str = Field(..., description="Label: positive, negative, neutral")
    cached: bool = Field(default=False, description="Résultat depuis le cache")


class SentimentResponse(BaseModel):
    """Réponse avec les résultats d'analyse."""

    results: list[SentimentResult]
    model: str = Field(..., description="Modèle utilisé: mistral ou mock")
    processed_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Timestamp du traitement",
    )


class MarketSentiment(BaseModel):
    """Sentiment global du marché."""

    score: float = Field(..., ge=-1, le=1, description="Score agrégé (-1 à +1)")
    label: str = Field(..., description="Label: pessimiste, neutre, optimiste")
    interpretation: str = Field(
        ...,
        description="Interprétation en français pour les débutants",
        examples=["Les investisseurs sont optimistes, le marché monte"],
    )
    confidence: str = Field(..., description="Niveau de confiance: high, medium, low")
    as_of: str = Field(..., description="Date du calcul")


class SentimentStats(BaseModel):
    """Statistiques du service de sentiment."""

    cache_size: int
    model: str
    is_mock: bool
