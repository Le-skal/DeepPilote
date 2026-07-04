"""
Module de sentiment analysis avec Mistral AI.

Phase 5 : Intégration d'un service IA tiers pour analyser
le sentiment des headlines financiers.

Compétences : C6 (veille), C7 (identifier services), C8 (paramétrer service)
"""

from ml.sentiment.config import MISTRAL_CONFIG, SENTIMENT_CONFIG
from ml.sentiment.client import MistralClient
from ml.sentiment.analyzer import SentimentAnalyzer
from ml.sentiment.prompts import SENTIMENT_SYSTEM_PROMPT, create_sentiment_prompt

__all__ = [
    "MISTRAL_CONFIG",
    "SENTIMENT_CONFIG",
    "MistralClient",
    "SentimentAnalyzer",
    "SENTIMENT_SYSTEM_PROMPT",
    "create_sentiment_prompt",
]
