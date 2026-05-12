"""
Tests unitaires pour l'extracteur BigQuery.

Note: Les tests utilisent des mocks pour éviter d'appeler l'API GCP.
"""

import os
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from data.extractors.extract_bigquery import (
    create_prices_table_sql,
    get_bigquery_client,
    monthly_aggregation_sql,
    query_bigquery,
)


class TestGetBigqueryClient:
    """Tests de la fonction get_bigquery_client."""

    def test_raises_without_credentials(self):
        """Vérifie qu'une erreur est levée sans credentials."""
        with patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "", "GCP_PROJECT_ID": ""}):
            with pytest.raises(ValueError, match="GOOGLE_APPLICATION_CREDENTIALS"):
                get_bigquery_client()

    def test_raises_without_project_id(self):
        """Vérifie qu'une erreur est levée sans project ID."""
        with patch.dict(
            os.environ,
            {"GOOGLE_APPLICATION_CREDENTIALS": "/fake/path.json", "GCP_PROJECT_ID": ""},
        ):
            with patch("os.path.exists", return_value=True):
                with pytest.raises(ValueError, match="GCP_PROJECT_ID"):
                    get_bigquery_client()


class TestQueryBigqueryMocked:
    """Tests avec mock du client BigQuery."""

    @pytest.fixture
    def mock_bq_client(self):
        """Crée un mock du client BigQuery."""
        with patch("data.extractors.extract_bigquery.get_bigquery_client") as mock:
            client_instance = MagicMock()
            mock.return_value = client_instance

            # Mock du résultat de requête
            mock_result = MagicMock()
            mock_result.to_dataframe.return_value = pd.DataFrame(
                {"col1": [1, 2, 3], "col2": ["a", "b", "c"]}
            )

            query_job = MagicMock()
            query_job.result.return_value = mock_result
            client_instance.query.return_value = query_job

            yield client_instance

    def test_query_returns_dataframe(self, mock_bq_client):
        """Vérifie que query_bigquery retourne un DataFrame."""
        result = query_bigquery("SELECT * FROM test")
        assert isinstance(result, pd.DataFrame)

    def test_query_has_expected_shape(self, mock_bq_client):
        """Vérifie la forme du DataFrame retourné."""
        result = query_bigquery("SELECT * FROM test")
        assert len(result) == 3
        assert len(result.columns) == 2


class TestSqlGenerators:
    """Tests des générateurs de requêtes SQL."""

    def test_create_prices_table_sql(self):
        """Vérifie la structure de la requête CREATE TABLE."""
        sql = create_prices_table_sql("my_dataset", "prices_history")
        assert "CREATE TABLE" in sql
        assert "my_dataset.prices_history" in sql
        assert "PARTITION BY date" in sql
        assert "CLUSTER BY ticker" in sql

    def test_monthly_aggregation_sql(self):
        """Vérifie la structure de la requête d'agrégation."""
        sql = monthly_aggregation_sql("my_dataset", "prices_history")
        assert "DATE_TRUNC(date, MONTH)" in sql
        assert "my_dataset.prices_history" in sql
        assert "GROUP BY" in sql

    def test_sql_contains_required_columns(self):
        """Vérifie que les colonnes requises sont présentes."""
        sql = create_prices_table_sql("ds", "tb")
        required_columns = ["date", "ticker", "open", "high", "low", "close", "volume"]
        for col in required_columns:
            assert col in sql.lower()
