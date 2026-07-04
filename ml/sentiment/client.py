"""
Client wrapper pour l'API Mistral.

Gère la connexion, les erreurs et les retries.
"""

import json
import time
import logging
from typing import Optional

from ml.sentiment.config import MISTRAL_CONFIG
from ml.sentiment.prompts import SENTIMENT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class MistralClient:
    """
    Client wrapper pour l'API Mistral.

    Gère :
    - Connexion à l'API
    - Retry avec backoff exponentiel
    - Parsing des réponses JSON
    - Gestion des erreurs

    Attributes:
        config: Configuration Mistral
        client: Client Mistral officiel
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialise le client Mistral.

        Args:
            api_key: Clé API (utilise .env si non fournie)
        """
        self.api_key = api_key or MISTRAL_CONFIG.api_key
        self.config = MISTRAL_CONFIG
        self._client = None

    @property
    def client(self):
        """Lazy loading du client Mistral."""
        if self._client is None:
            if not self.api_key:
                raise ValueError(
                    "MISTRAL_API_KEY non définie. "
                    "Ajoutez-la dans .env ou passez-la en paramètre."
                )
            try:
                from mistralai import Mistral
                self._client = Mistral(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "mistralai non installé. "
                    "Lancez: pip install mistralai"
                )
        return self._client

    def chat(
        self,
        user_message: str,
        system_message: str = SENTIMENT_SYSTEM_PROMPT,
    ) -> str:
        """
        Envoie un message au modèle Mistral.

        Args:
            user_message: Message utilisateur
            system_message: Message système (prompt)

        Returns:
            Réponse du modèle (texte)

        Raises:
            Exception: Si tous les retries échouent
        """
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        last_error = None

        for attempt in range(self.config.max_retries):
            try:
                response = self.client.chat.complete(
                    model=self.config.model,
                    messages=messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                )

                # Extraire le contenu de la réponse
                content = response.choices[0].message.content
                return content.strip()

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Tentative {attempt + 1}/{self.config.max_retries} échouée: {e}"
                )

                if attempt < self.config.max_retries - 1:
                    # Backoff exponentiel
                    delay = self.config.retry_delay * (2 ** attempt)
                    time.sleep(delay)

        raise Exception(f"Échec après {self.config.max_retries} tentatives: {last_error}")

    def chat_json(
        self,
        user_message: str,
        system_message: str = SENTIMENT_SYSTEM_PROMPT,
    ) -> dict:
        """
        Envoie un message et parse la réponse JSON.

        Args:
            user_message: Message utilisateur
            system_message: Message système

        Returns:
            Réponse parsée en dict

        Raises:
            ValueError: Si la réponse n'est pas du JSON valide
        """
        response = self.chat(user_message, system_message)

        # Nettoyer la réponse (parfois le modèle ajoute du texte)
        response = response.strip()

        # Chercher le JSON dans la réponse
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]

        response = response.strip()

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Réponse non-JSON: {response}")
            raise ValueError(f"Réponse non-JSON du modèle: {e}")

    def is_available(self) -> bool:
        """
        Vérifie si l'API Mistral est disponible.

        Returns:
            True si l'API répond correctement
        """
        if not self.api_key:
            return False

        try:
            # Test simple
            response = self.chat("Réponds 'ok'", "Tu es un assistant. Réponds 'ok'.")
            return "ok" in response.lower()
        except Exception as e:
            logger.warning(f"API Mistral indisponible: {e}")
            return False


class MockMistralClient:
    """
    Client mock pour les tests (pas d'appels API).

    Retourne des scores basés sur des mots-clés simples.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialise le mock client."""
        self.api_key = api_key or "mock-key"

    def chat(self, user_message: str, system_message: str = "") -> str:
        """Simule une réponse."""
        score = self._estimate_sentiment(user_message)
        label = "positive" if score > 0.3 else "negative" if score < -0.3 else "neutral"
        return json.dumps({"score": score, "label": label})

    def chat_json(self, user_message: str, system_message: str = "") -> dict:
        """Retourne directement un dict."""
        return json.loads(self.chat(user_message, system_message))

    def _estimate_sentiment(self, text: str) -> float:
        """Estimation simple basée sur mots-clés."""
        text_lower = text.lower()

        positive_words = ["high", "rally", "surge", "gain", "rise", "beat", "growth", "optimism"]
        negative_words = ["crash", "fall", "drop", "fear", "concern", "decline", "loss", "recession"]

        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)

        if pos_count > neg_count:
            return min(0.8, 0.3 + pos_count * 0.2)
        elif neg_count > pos_count:
            return max(-0.8, -0.3 - neg_count * 0.2)
        return 0.0

    def is_available(self) -> bool:
        """Le mock est toujours disponible."""
        return True
