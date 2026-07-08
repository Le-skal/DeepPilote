"""
Service de sentiment pour l'API.

Wrapper autour de ml/sentiment/analyzer.py avec:
- Fallback automatique vers MockClient si pas de clé API
- Cache TTL pour éviter appels répétés
- Agrégation pour sentiment marché global
"""

import logging
import os
from datetime import datetime
from functools import lru_cache

from ml.sentiment.analyzer import SentimentAnalyzer
from ml.sentiment.client import MistralClient, MockMistralClient

logger = logging.getLogger(__name__)

# Headlines de démonstration pour le sentiment marché
# En production, on les récupérerait d'une API de news
DEMO_HEADLINES = [
    "S&P 500 closes at record high as tech stocks rally",
    "Fed signals potential rate cuts in coming months",
    "Unemployment falls to lowest level in decades",
    "Corporate earnings beat expectations across sectors",
    "Consumer confidence reaches multi-year high",
]


@lru_cache(maxsize=1)
def _get_analyzer() -> tuple[SentimentAnalyzer, bool]:
    """
    Crée l'analyseur avec fallback vers mock si pas de clé API.

    Returns:
        Tuple (analyzer, is_mock)
    """
    api_key = os.getenv("MISTRAL_API_KEY")

    if api_key:
        try:
            client = MistralClient()
            # Test que le client fonctionne
            if client.is_available():
                logger.info("Sentiment: Utilisation du client Mistral")
                return SentimentAnalyzer(client=client), False
        except Exception as e:
            logger.warning(f"Sentiment: Erreur client Mistral, fallback mock: {e}")

    # Fallback vers mock
    logger.info("Sentiment: Utilisation du client Mock (pas de clé API)")
    return SentimentAnalyzer(use_mock=True), True


def get_analyzer() -> SentimentAnalyzer:
    """Retourne l'analyseur de sentiment."""
    analyzer, _ = _get_analyzer()
    return analyzer


def is_using_mock() -> bool:
    """Vérifie si on utilise le mock client."""
    _, is_mock = _get_analyzer()
    return is_mock


def analyze_headlines(headlines: list[str]) -> dict:
    """
    Analyse une liste de headlines (version sync).

    Args:
        headlines: Liste de headlines à analyser

    Returns:
        Dict avec results, model, processed_at
    """
    analyzer = get_analyzer()
    is_mock = is_using_mock()

    results = []
    for headline in headlines:
        result = analyzer.analyze(headline)
        results.append(
            {
                "headline": result["headline"],
                "score": result["score"],
                "label": result["label"],
                "cached": result.get("cached", False),
            }
        )

    return {
        "results": results,
        "model": "mock" if is_mock else "mistral",
        "processed_at": datetime.now().isoformat(),
    }


async def analyze_headlines_async(headlines: list[str]) -> list[dict]:
    """
    Analyse une liste de headlines (version async pour RSS).

    Args:
        headlines: Liste de headlines à analyser

    Returns:
        Liste de résultats avec score et label
    """
    analyzer = get_analyzer()

    results = []
    for headline in headlines:
        result = analyzer.analyze(headline)
        results.append(
            {
                "headline": result["headline"],
                "score": result["score"],
                "label": result["label"],
            }
        )

    return results


def get_market_sentiment() -> dict:
    """
    Retourne le sentiment global du marché.

    Utilise des headlines de démonstration pour simuler
    l'agrégation de news financières.

    Returns:
        Dict avec score, label, interpretation, confidence, as_of
    """
    analyzer = get_analyzer()
    is_mock = is_using_mock()

    # Analyser les headlines de démo
    scores = []
    for headline in DEMO_HEADLINES:
        result = analyzer.analyze(headline)
        scores.append(result["score"])

    # Calculer le score moyen
    avg_score = sum(scores) / len(scores) if scores else 0.0

    # Déterminer le label et l'interprétation
    if avg_score >= 0.3:
        label = "optimiste"
        interpretation = "Les investisseurs sont confiants. Tendance favorable aux actions."
        confidence = "high" if avg_score >= 0.5 else "medium"
    elif avg_score <= -0.3:
        label = "pessimiste"
        interpretation = "Les investisseurs sont prudents. Privilégier les actifs défensifs."
        confidence = "high" if avg_score <= -0.5 else "medium"
    else:
        label = "neutre"
        interpretation = "Pas de tendance claire. Le marché attend des signaux."
        confidence = "low"

    return {
        "score": round(avg_score, 2),
        "label": label,
        "interpretation": interpretation,
        "confidence": confidence,
        "as_of": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "_model": "mock" if is_mock else "mistral",
        "_headlines_count": len(DEMO_HEADLINES),
    }


def get_sentiment_stats() -> dict:
    """Retourne les statistiques du service."""
    analyzer = get_analyzer()
    is_mock = is_using_mock()
    stats = analyzer.get_stats()

    return {
        "cache_size": stats.get("cache_size", 0),
        "model": stats.get("model", "unknown"),
        "is_mock": is_mock,
    }


def clear_sentiment_cache() -> None:
    """Vide le cache de sentiment."""
    analyzer = get_analyzer()
    analyzer.clear_cache()
    logger.info("Sentiment: Cache vidé")
