"""
Configuration pour le module sentiment analysis.

Paramètres de l'API Mistral et du scoring de sentiment.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class MistralConfig:
    """Configuration de l'API Mistral."""

    # Clé API (depuis .env)
    api_key: str = os.getenv("MISTRAL_API_KEY", "")

    # Modèle à utiliser
    # mistral-small-latest : bon rapport qualité/prix pour classification
    model: str = "mistral-small-latest"

    # Température (0 = déterministe, 1 = créatif)
    # Basse pour classification de sentiment
    temperature: float = 0.1

    # Tokens max pour la réponse
    max_tokens: int = 100

    # Timeout en secondes
    timeout: int = 30

    # Retry config
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class SentimentConfig:
    """Configuration du scoring de sentiment."""

    # Plage de scores
    min_score: float = -1.0
    max_score: float = 1.0

    # Seuils de classification
    negative_threshold: float = -0.3
    positive_threshold: float = 0.3

    # Cache des résultats (éviter appels répétés)
    enable_cache: bool = True
    cache_ttl_hours: int = 24

    # Batch processing
    batch_size: int = 10
    batch_delay: float = 0.5  # Délai entre batches (rate limit)


# Instances globales
MISTRAL_CONFIG = MistralConfig()
SENTIMENT_CONFIG = SentimentConfig()


def validate_config() -> bool:
    """
    Valide la configuration Mistral.

    Returns:
        True si la config est valide
    """
    if not MISTRAL_CONFIG.api_key:
        print("ATTENTION: MISTRAL_API_KEY non définie dans .env")
        return False
    return True
