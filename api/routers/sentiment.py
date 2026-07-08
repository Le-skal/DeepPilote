"""
Router pour les endpoints Sentiment.

Expose l'analyse de sentiment Mistral via API REST.
Utilise le flux RSS de L'AGEFI pour les news financières.
"""

from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from api.models.sentiment import (
    MarketSentiment,
    SentimentRequest,
    SentimentResponse,
    SentimentStats,
)
from api.services.sentiment_service import (
    analyze_headlines,
    clear_sentiment_cache,
    get_market_sentiment,
    get_sentiment_stats,
)
from api.services.rss_service import analyze_market_sentiment_from_rss

router = APIRouter(prefix="/sentiment", tags=["Sentiment"])
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/analyze",
    response_model=SentimentResponse,
    summary="Analyser des headlines",
    description="""
    Analyse le sentiment de headlines financiers.

    Utilise Mistral AI pour scorer chaque headline de -1 (très négatif) à +1 (très positif).

    **Labels:**
    - **positive** : score >= 0.3
    - **negative** : score <= -0.3
    - **neutral** : entre -0.3 et 0.3

    **Note:** Si pas de clé API Mistral, un modèle mock est utilisé automatiquement.
    """,
)
@limiter.limit("10/minute")
def analyze(request: Request, payload: SentimentRequest) -> SentimentResponse:
    """Analyse une liste de headlines."""
    result = analyze_headlines(payload.headlines)
    return SentimentResponse(**result)


@router.get(
    "/market",
    response_model=MarketSentiment,
    summary="Sentiment global du marché",
    description="""
    Retourne le sentiment agrégé du marché basé sur les news financières.

    **Source:** Flux RSS de L'AGEFI (news financières françaises).

    Analyse les ~30 dernières headlines avec Mistral AI pour déterminer
    l'humeur générale des investisseurs.

    **Labels:**
    - **optimiste** : Les investisseurs sont confiants
    - **pessimiste** : Les investisseurs sont prudents
    - **neutre** : Pas de tendance claire

    **Confiance:**
    - **high** : 20+ headlines analysées avec cohérence
    - **medium** : 10+ headlines ou légère variance
    - **low** : Peu de données ou résultats inconsistants
    """,
)
@limiter.limit("30/minute")
async def market_sentiment(request: Request) -> MarketSentiment:
    """Retourne le sentiment global du marché basé sur les news RSS."""
    try:
        # Utiliser le flux RSS L'AGEFI
        result = await analyze_market_sentiment_from_rss(
            feed_key="agefi",
            max_headlines=30,
        )
        return MarketSentiment(
            score=result["score"],
            label=result["label"],
            interpretation=result["interpretation"],
            confidence=result["confidence"],
            as_of=result["as_of"],
        )
    except Exception as e:
        # Fallback vers le mock en cas d'erreur
        print(f"[SENTIMENT] RSS error, using mock: {e}")
        result = get_market_sentiment()
        return MarketSentiment(
            score=result["score"],
            label=result["label"],
            interpretation=f"{result['interpretation']} (fallback - RSS indisponible)",
            confidence="low",
            as_of=result["as_of"],
        )


@router.get(
    "/stats",
    response_model=SentimentStats,
    summary="Statistiques du service",
    description="Retourne les statistiques du service de sentiment (cache, modèle).",
)
@limiter.limit("30/minute")
def stats(request: Request) -> SentimentStats:
    """Retourne les statistiques du service."""
    return SentimentStats(**get_sentiment_stats())


@router.post(
    "/clear-cache",
    summary="Vider le cache",
    description="Vide le cache de sentiment pour forcer de nouvelles analyses.",
)
@limiter.limit("2/minute")
def clear_cache(request: Request) -> dict:
    """Vide le cache de sentiment."""
    clear_sentiment_cache()
    return {"message": "Cache cleared successfully"}
