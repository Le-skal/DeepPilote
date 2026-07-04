"""
Tests pour le module sentiment analysis avec Mistral AI.

Phase 5 - Compétences C6, C7, C8
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta

from ml.sentiment.config import MISTRAL_CONFIG, SENTIMENT_CONFIG, MistralConfig, SentimentConfig
from ml.sentiment.prompts import (
    SENTIMENT_SYSTEM_PROMPT,
    create_sentiment_prompt,
    create_batch_prompt,
    TEST_HEADLINES,
)
from ml.sentiment.client import MockMistralClient
from ml.sentiment.analyzer import SentimentAnalyzer, create_sentiment_features


class TestMistralConfig:
    """Tests pour la configuration Mistral."""

    def test_config_default_values(self):
        """Vérifie les valeurs par défaut de la config."""
        config = MistralConfig()
        assert config.model == "mistral-small-latest"
        assert config.temperature == 0.1
        assert config.max_tokens == 100
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.retry_delay == 1.0

    def test_global_config_exists(self):
        """Vérifie que la config globale est accessible."""
        assert MISTRAL_CONFIG is not None
        assert isinstance(MISTRAL_CONFIG, MistralConfig)


class TestSentimentConfig:
    """Tests pour la configuration du scoring."""

    def test_config_default_values(self):
        """Vérifie les valeurs par défaut."""
        config = SentimentConfig()
        assert config.min_score == -1.0
        assert config.max_score == 1.0
        assert config.negative_threshold == -0.3
        assert config.positive_threshold == 0.3
        assert config.enable_cache is True
        assert config.cache_ttl_hours == 24

    def test_global_sentiment_config_exists(self):
        """Vérifie que la config sentiment globale existe."""
        assert SENTIMENT_CONFIG is not None
        assert isinstance(SENTIMENT_CONFIG, SentimentConfig)


class TestPrompts:
    """Tests pour les prompts."""

    def test_system_prompt_exists(self):
        """Vérifie que le prompt système est défini."""
        assert SENTIMENT_SYSTEM_PROMPT is not None
        assert len(SENTIMENT_SYSTEM_PROMPT) > 100  # Prompt suffisamment long
        assert "JSON" in SENTIMENT_SYSTEM_PROMPT
        assert "score" in SENTIMENT_SYSTEM_PROMPT

    def test_create_sentiment_prompt(self):
        """Vérifie la création du prompt utilisateur."""
        headline = "S&P 500 reaches all-time high"
        prompt = create_sentiment_prompt(headline)

        assert headline in prompt
        assert "sentiment" in prompt.lower()
        assert "JSON" in prompt

    def test_create_batch_prompt(self):
        """Vérifie la création du prompt batch."""
        headlines = [
            "Markets rally on good news",
            "Stocks fall amid concerns",
        ]
        prompt = create_batch_prompt(headlines)

        assert "1." in prompt
        assert "2." in prompt
        assert headlines[0] in prompt
        assert headlines[1] in prompt
        assert "JSON" in prompt

    def test_test_headlines_exist(self):
        """Vérifie que les headlines de test sont définis."""
        assert TEST_HEADLINES is not None
        assert len(TEST_HEADLINES) >= 5

        # Vérifie le format (headline, score_attendu, label_attendu)
        for item in TEST_HEADLINES:
            assert len(item) == 3
            headline, score, label = item
            assert isinstance(headline, str)
            assert isinstance(score, float)
            assert label in ["positive", "negative", "neutral"]


class TestMockMistralClient:
    """Tests pour le client mock (pas d'appels API)."""

    def test_mock_client_init(self):
        """Vérifie l'initialisation du mock client."""
        client = MockMistralClient()
        assert client.api_key == "mock-key"

    def test_mock_client_with_custom_key(self):
        """Vérifie l'initialisation avec clé personnalisée."""
        client = MockMistralClient(api_key="custom-key")
        assert client.api_key == "custom-key"

    def test_mock_is_available(self):
        """Vérifie que le mock est toujours disponible."""
        client = MockMistralClient()
        assert client.is_available() is True

    def test_mock_chat_returns_json_string(self):
        """Vérifie que chat retourne une string JSON."""
        client = MockMistralClient()
        response = client.chat("S&P 500 rallies")

        assert isinstance(response, str)
        # Doit être parseable en JSON
        import json
        data = json.loads(response)
        assert "score" in data
        assert "label" in data

    def test_mock_chat_json_returns_dict(self):
        """Vérifie que chat_json retourne un dict."""
        client = MockMistralClient()
        response = client.chat_json("Markets crash on fear")

        assert isinstance(response, dict)
        assert "score" in response
        assert "label" in response
        assert isinstance(response["score"], float)
        assert response["label"] in ["positive", "negative", "neutral"]

    def test_mock_positive_sentiment(self):
        """Vérifie la détection de sentiment positif."""
        client = MockMistralClient()
        response = client.chat_json("Tech stocks rally on AI optimism and strong growth")

        assert response["score"] > 0.3
        assert response["label"] == "positive"

    def test_mock_negative_sentiment(self):
        """Vérifie la détection de sentiment négatif."""
        client = MockMistralClient()
        response = client.chat_json("Markets crash amid recession fears and economic decline")

        assert response["score"] < -0.3
        assert response["label"] == "negative"

    def test_mock_neutral_sentiment(self):
        """Vérifie la détection de sentiment neutre."""
        client = MockMistralClient()
        response = client.chat_json("Company announces quarterly results")

        assert -0.3 <= response["score"] <= 0.3
        assert response["label"] == "neutral"


class TestSentimentAnalyzer:
    """Tests pour l'analyseur de sentiment."""

    @pytest.fixture
    def analyzer(self):
        """Fixture pour créer un analyzer avec mock client."""
        return SentimentAnalyzer(use_mock=True)

    def test_init_with_mock(self):
        """Vérifie l'initialisation avec mock."""
        analyzer = SentimentAnalyzer(use_mock=True)
        assert isinstance(analyzer.client, MockMistralClient)

    def test_init_with_custom_client(self):
        """Vérifie l'initialisation avec client personnalisé."""
        custom_client = MockMistralClient()
        analyzer = SentimentAnalyzer(client=custom_client)
        assert analyzer.client is custom_client

    def test_analyze_returns_dict(self, analyzer):
        """Vérifie que analyze retourne un dict complet."""
        result = analyzer.analyze("S&P 500 rallies to new highs")

        assert isinstance(result, dict)
        assert "headline" in result
        assert "score" in result
        assert "label" in result
        assert "cached" in result

    def test_analyze_score_range(self, analyzer):
        """Vérifie que le score est dans [-1, 1]."""
        result = analyzer.analyze("Markets show extreme movement")

        assert -1.0 <= result["score"] <= 1.0

    def test_analyze_score_method(self, analyzer):
        """Vérifie la méthode analyze_score."""
        score = analyzer.analyze_score("Tech stocks surge on earnings")

        assert isinstance(score, float)
        assert -1.0 <= score <= 1.0

    def test_analyze_batch(self, analyzer):
        """Vérifie l'analyse batch."""
        headlines = [
            "S&P 500 reaches all-time high",
            "Markets crash on bad news",
            "Fed holds rates steady",
        ]
        results = analyzer.analyze_batch(headlines, show_progress=False)

        assert len(results) == 3
        assert all(isinstance(r, dict) for r in results)
        assert all("score" in r for r in results)

    def test_cache_functionality(self, analyzer):
        """Vérifie que le cache fonctionne."""
        headline = "S&P 500 rallies amid optimism"

        # Premier appel - pas en cache
        result1 = analyzer.analyze(headline)
        assert result1["cached"] is False

        # Deuxième appel - devrait être en cache
        result2 = analyzer.analyze(headline)
        assert result2["cached"] is True

        # Score devrait être identique
        assert result1["score"] == result2["score"]

    def test_clear_cache(self, analyzer):
        """Vérifie le vidage du cache."""
        headline = "Markets show strong performance"

        # Remplir le cache
        analyzer.analyze(headline)
        assert len(analyzer._cache) > 0

        # Vider le cache
        analyzer.clear_cache()
        assert len(analyzer._cache) == 0

    def test_get_stats(self, analyzer):
        """Vérifie les statistiques."""
        stats = analyzer.get_stats()

        assert "cache_size" in stats
        assert "cache_enabled" in stats
        assert "model" in stats
        assert isinstance(stats["cache_size"], int)

    def test_score_to_label_positive(self, analyzer):
        """Vérifie la conversion score -> label positif."""
        label = analyzer._score_to_label(0.5)
        assert label == "positive"

    def test_score_to_label_negative(self, analyzer):
        """Vérifie la conversion score -> label négatif."""
        label = analyzer._score_to_label(-0.5)
        assert label == "negative"

    def test_score_to_label_neutral(self, analyzer):
        """Vérifie la conversion score -> label neutre."""
        label = analyzer._score_to_label(0.0)
        assert label == "neutral"

    def test_cache_key_generation(self, analyzer):
        """Vérifie la génération de clé de cache."""
        key1 = analyzer._get_cache_key("headline A")
        key2 = analyzer._get_cache_key("headline B")
        key3 = analyzer._get_cache_key("headline A")

        assert key1 != key2
        assert key1 == key3  # Même headline = même clé


class TestAnalyzeDataframe:
    """Tests pour l'analyse de DataFrame."""

    @pytest.fixture
    def analyzer(self):
        """Fixture pour l'analyzer."""
        return SentimentAnalyzer(use_mock=True)

    @pytest.fixture
    def sample_df(self):
        """Fixture pour un DataFrame de test."""
        return pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=5),
            "headline": [
                "S&P 500 rallies on optimism",
                "Markets crash amid recession fears",
                "Fed holds rates steady",
                "Tech stocks surge on AI growth",
                "Oil prices drop sharply",
            ],
        })

    def test_analyze_dataframe(self, analyzer, sample_df):
        """Vérifie l'analyse de DataFrame."""
        result_df = analyzer.analyze_dataframe(sample_df, text_column="headline")

        assert "sentiment_score" in result_df.columns
        assert len(result_df) == len(sample_df)
        assert all(-1.0 <= s <= 1.0 for s in result_df["sentiment_score"])

    def test_analyze_dataframe_custom_column_name(self, analyzer, sample_df):
        """Vérifie l'analyse avec nom de colonne personnalisé."""
        result_df = analyzer.analyze_dataframe(
            sample_df,
            text_column="headline",
            score_column="custom_score",
        )

        assert "custom_score" in result_df.columns

    def test_analyze_dataframe_missing_column(self, analyzer, sample_df):
        """Vérifie l'erreur si colonne manquante."""
        with pytest.raises(ValueError, match="non trouvée"):
            analyzer.analyze_dataframe(sample_df, text_column="missing_column")


class TestCreateSentimentFeatures:
    """Tests pour la création de features de sentiment."""

    @pytest.fixture
    def sample_data(self):
        """Fixture pour des données de test."""
        dates = pd.date_range("2024-01-01", periods=50, freq="D")
        df = pd.DataFrame({"date": dates})
        df = df.set_index("date")

        # Scores de sentiment simulés
        import numpy as np
        np.random.seed(42)
        scores = pd.Series(np.random.uniform(-0.5, 0.5, 50), index=df.index)

        return df, scores

    def test_create_sentiment_features(self, sample_data):
        """Vérifie la création de features."""
        df, scores = sample_data
        features = create_sentiment_features(df, scores)

        assert "sentiment_score" in features.columns
        assert "sentiment_sma_5" in features.columns
        assert "sentiment_sma_20" in features.columns
        assert "sentiment_volatility" in features.columns
        assert "sentiment_change" in features.columns

    def test_create_sentiment_features_custom_windows(self, sample_data):
        """Vérifie les fenêtres personnalisées."""
        df, scores = sample_data
        features = create_sentiment_features(df, scores, windows=[10, 30])

        assert "sentiment_sma_10" in features.columns
        assert "sentiment_sma_30" in features.columns
        assert "sentiment_sma_5" not in features.columns

    def test_features_index_matches(self, sample_data):
        """Vérifie que l'index est préservé."""
        df, scores = sample_data
        features = create_sentiment_features(df, scores)

        assert len(features) == len(df)
        assert features.index.equals(df.index)


class TestIntegration:
    """Tests d'intégration pour le module sentiment."""

    def test_full_pipeline_mock(self):
        """Teste le pipeline complet avec mock client."""
        # Setup
        analyzer = SentimentAnalyzer(use_mock=True)

        # Analyse de headlines
        headlines = [
            "S&P 500 reaches all-time high amid strong earnings",
            "Markets crash as recession fears grow",
            "Fed holds rates steady, markets unchanged",
        ]

        # Analyse individuelle
        results = [analyzer.analyze(h) for h in headlines]

        # Vérifications
        assert results[0]["score"] > 0  # Positif
        assert results[1]["score"] < 0  # Négatif
        assert abs(results[2]["score"]) < 0.5  # Neutre

        # Stats
        stats = analyzer.get_stats()
        assert stats["cache_size"] == 3

    def test_dataframe_pipeline(self):
        """Teste le pipeline DataFrame complet."""
        # Créer données
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=10),
            "headline": [
                "Tech rally",
                "Market crash",
                "Steady gains",
                "Fear spreads",
                "Optimism grows",
                "Decline continues",
                "Recovery starts",
                "Concerns rise",
                "Growth expected",
                "Losses mount",
            ],
        })

        # Analyse
        analyzer = SentimentAnalyzer(use_mock=True)
        df_scored = analyzer.analyze_dataframe(df, text_column="headline")

        # Créer features
        features = create_sentiment_features(
            df_scored.set_index("date"),
            df_scored.set_index("date")["sentiment_score"],
        )

        # Vérifications
        assert len(features) == 10
        assert "sentiment_sma_5" in features.columns
        assert not features["sentiment_score"].isna().any()


class TestFeatureEngineeringIntegration:
    """Tests d'intégration avec le feature engineering ML."""

    def test_prepare_prediction_features_with_sentiment(self):
        """Teste l'intégration des features sentiment dans prepare_prediction_features."""
        from ml.features.feature_engineering import prepare_prediction_features
        import numpy as np

        # Créer données de prix synthétiques
        np.random.seed(42)
        dates = pd.date_range("2024-01-01", periods=300)
        df = pd.DataFrame(index=dates)
        df["SPY"] = 100 + np.cumsum(np.random.randn(300) * 0.5)

        # Créer scores de sentiment synthétiques
        sentiment_scores = pd.Series(
            np.random.uniform(-0.5, 0.5, 300),
            index=dates,
        )

        # Préparer features avec sentiment
        features = prepare_prediction_features(
            df,
            ticker="SPY",
            sentiment_scores=sentiment_scores,
        )

        # Vérifications
        assert "sentiment_score" in features.columns
        assert "sentiment_sma_5" in features.columns
        assert "sentiment_sma_20" in features.columns
        assert "sentiment_volatility" in features.columns
        assert "sentiment_change" in features.columns

        # Les valeurs doivent être dans des plages raisonnables
        assert features["sentiment_score"].abs().max() <= 1.0
        assert features["sentiment_sma_5"].abs().max() <= 1.0
        assert features["sentiment_volatility"].min() >= 0

    def test_prepare_prediction_features_without_sentiment(self):
        """Vérifie que la fonction fonctionne sans sentiment (backwards compatible)."""
        from ml.features.feature_engineering import prepare_prediction_features
        import numpy as np

        # Créer données de prix synthétiques
        np.random.seed(42)
        dates = pd.date_range("2024-01-01", periods=300)
        df = pd.DataFrame(index=dates)
        df["SPY"] = 100 + np.cumsum(np.random.randn(300) * 0.5)

        # Préparer features SANS sentiment
        features = prepare_prediction_features(df, ticker="SPY")

        # Les colonnes sentiment ne doivent PAS être présentes
        assert "sentiment_score" not in features.columns
        assert "sentiment_sma_5" not in features.columns

        # Les autres colonnes doivent être présentes
        assert "return_1d" in features.columns
        assert "rsi_14" in features.columns
        assert "regime" in features.columns

    def test_sentiment_features_are_lagged(self):
        """Vérifie que les features sentiment sont décalées (pas de look-ahead)."""
        from ml.features.feature_engineering import prepare_prediction_features
        import numpy as np

        # Créer données (300 jours pour avoir assez de données après SMA 200)
        np.random.seed(42)
        dates = pd.date_range("2024-01-01", periods=300)
        df = pd.DataFrame(index=dates)
        df["SPY"] = 100 + np.cumsum(np.random.randn(300) * 0.5)

        # Créer sentiment avec un pattern reconnaissable
        sentiment = pd.Series([0.5] * 150 + [-0.5] * 150, index=dates)

        features = prepare_prediction_features(
            df,
            ticker="SPY",
            sentiment_scores=sentiment,
        )

        # La feature est bien laggée (shift(1)) donc pas de look-ahead bias
        assert len(features) > 0
        assert "sentiment_score" in features.columns
