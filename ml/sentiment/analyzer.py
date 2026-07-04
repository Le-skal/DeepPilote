"""
Analyseur de sentiment pour headlines financiers.

Utilise Mistral AI pour scorer le sentiment des textes.
"""

import logging
import hashlib
import time
from typing import Optional, Union
from datetime import datetime, timedelta
from functools import lru_cache

import pandas as pd

from ml.sentiment.config import SENTIMENT_CONFIG, MISTRAL_CONFIG
from ml.sentiment.client import MistralClient, MockMistralClient
from ml.sentiment.prompts import create_sentiment_prompt

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Analyseur de sentiment pour headlines financiers.

    Utilise Mistral AI pour extraire un score de sentiment [-1, 1].

    Attributes:
        client: Client Mistral (ou mock)
        config: Configuration du scoring
        cache: Cache des résultats (optionnel)
    """

    def __init__(
        self,
        client: Optional[Union[MistralClient, MockMistralClient]] = None,
        use_mock: bool = False,
    ):
        """
        Initialise l'analyseur.

        Args:
            client: Client Mistral personnalisé
            use_mock: Utiliser le mock client (pas d'appels API)
        """
        if client:
            self.client = client
        elif use_mock:
            self.client = MockMistralClient()
        else:
            self.client = MistralClient()

        self.config = SENTIMENT_CONFIG
        self._cache: dict[str, tuple[float, datetime]] = {}

    def analyze(self, headline: str) -> dict:
        """
        Analyse le sentiment d'un headline.

        Args:
            headline: Le headline à analyser

        Returns:
            Dict avec score, label, et metadata
        """
        # Vérifier le cache
        cache_key = self._get_cache_key(headline)
        if self.config.enable_cache and cache_key in self._cache:
            score, timestamp = self._cache[cache_key]
            if datetime.now() - timestamp < timedelta(hours=self.config.cache_ttl_hours):
                return {
                    "headline": headline,
                    "score": score,
                    "label": self._score_to_label(score),
                    "cached": True,
                }

        # Appeler l'API
        try:
            prompt = create_sentiment_prompt(headline)
            result = self.client.chat_json(prompt)

            score = float(result.get("score", 0.0))
            score = max(self.config.min_score, min(self.config.max_score, score))

            # Mettre en cache
            if self.config.enable_cache:
                self._cache[cache_key] = (score, datetime.now())

            return {
                "headline": headline,
                "score": score,
                "label": result.get("label", self._score_to_label(score)),
                "cached": False,
            }

        except Exception as e:
            logger.error(f"Erreur analyse sentiment: {e}")
            return {
                "headline": headline,
                "score": 0.0,
                "label": "error",
                "error": str(e),
                "cached": False,
            }

    def analyze_score(self, headline: str) -> float:
        """
        Retourne uniquement le score de sentiment.

        Args:
            headline: Le headline à analyser

        Returns:
            Score entre -1 et 1
        """
        result = self.analyze(headline)
        return result.get("score", 0.0)

    def analyze_batch(
        self,
        headlines: list[str],
        show_progress: bool = True,
    ) -> list[dict]:
        """
        Analyse plusieurs headlines.

        Args:
            headlines: Liste de headlines
            show_progress: Afficher la progression

        Returns:
            Liste de résultats
        """
        results = []
        total = len(headlines)

        for i, headline in enumerate(headlines):
            if show_progress and (i + 1) % 10 == 0:
                logger.info(f"Progression: {i + 1}/{total}")

            result = self.analyze(headline)
            results.append(result)

            # Rate limiting entre appels
            if not result.get("cached", False) and i < total - 1:
                time.sleep(self.config.batch_delay)

        return results

    def analyze_dataframe(
        self,
        df: pd.DataFrame,
        text_column: str = "headline",
        score_column: str = "sentiment_score",
    ) -> pd.DataFrame:
        """
        Ajoute une colonne de sentiment à un DataFrame.

        Args:
            df: DataFrame avec les headlines
            text_column: Nom de la colonne texte
            score_column: Nom de la colonne score à créer

        Returns:
            DataFrame avec la colonne sentiment
        """
        if text_column not in df.columns:
            raise ValueError(f"Colonne {text_column} non trouvée")

        headlines = df[text_column].tolist()
        results = self.analyze_batch(headlines, show_progress=True)

        scores = [r["score"] for r in results]
        df_result = df.copy()
        df_result[score_column] = scores

        return df_result

    def _score_to_label(self, score: float) -> str:
        """Convertit un score en label."""
        if score >= self.config.positive_threshold:
            return "positive"
        elif score <= self.config.negative_threshold:
            return "negative"
        return "neutral"

    def _get_cache_key(self, headline: str) -> str:
        """Génère une clé de cache pour un headline."""
        return hashlib.md5(headline.encode()).hexdigest()

    def get_stats(self) -> dict:
        """Retourne les statistiques de l'analyseur."""
        return {
            "cache_size": len(self._cache),
            "cache_enabled": self.config.enable_cache,
            "model": MISTRAL_CONFIG.model,
        }

    def clear_cache(self) -> None:
        """Vide le cache."""
        self._cache.clear()


def create_sentiment_features(
    df: pd.DataFrame,
    sentiment_scores: pd.Series,
    windows: list[int] = [5, 20],
) -> pd.DataFrame:
    """
    Crée des features de sentiment pour le ML.

    Args:
        df: DataFrame original
        sentiment_scores: Series de scores de sentiment
        windows: Fenêtres pour moyennes mobiles

    Returns:
        DataFrame avec features de sentiment
    """
    features = pd.DataFrame(index=df.index)

    # Score brut
    features["sentiment_score"] = sentiment_scores

    # Moyennes mobiles
    for window in windows:
        features[f"sentiment_sma_{window}"] = (
            sentiment_scores.rolling(window=window, min_periods=1).mean()
        )

    # Écart-type (volatilité du sentiment)
    features["sentiment_volatility"] = (
        sentiment_scores.rolling(window=20, min_periods=5).std()
    )

    # Changement de sentiment
    features["sentiment_change"] = sentiment_scores.diff()

    return features
