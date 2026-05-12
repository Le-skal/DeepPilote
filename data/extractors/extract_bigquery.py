"""
Extraction de données depuis Google BigQuery.

Ce module permet d'exécuter des requêtes SQL sur BigQuery et de récupérer
les résultats en DataFrame pandas.

Usage:
    python -m data.extractors.extract_bigquery
"""

import logging
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account

# Chargement des variables d'environnement
load_dotenv()

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Chemins
DATA_DIR = Path(__file__).parent.parent
RAW_DIR = DATA_DIR / "raw"


def get_bigquery_client() -> bigquery.Client:
    """
    Crée un client BigQuery avec les credentials du service account.

    Returns:
        Instance bigquery.Client configurée.

    Raises:
        ValueError: Si les credentials ne sont pas configurées.
    """
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    project_id = os.getenv("GCP_PROJECT_ID")

    if not credentials_path or not os.path.exists(credentials_path):
        raise ValueError(
            "GOOGLE_APPLICATION_CREDENTIALS non défini ou fichier inexistant.\n"
            "Téléchargez un service account JSON depuis la console GCP."
        )

    if not project_id:
        raise ValueError("GCP_PROJECT_ID non défini dans .env")

    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=["https://www.googleapis.com/auth/bigquery"],
    )

    client = bigquery.Client(credentials=credentials, project=project_id)
    logger.info(f"Client BigQuery créé pour projet: {project_id}")
    return client


def query_bigquery(sql_query: str) -> pd.DataFrame:
    """
    Exécute une requête SQL sur BigQuery et retourne un DataFrame.

    Args:
        sql_query: Requête SQL à exécuter.

    Returns:
        DataFrame avec les résultats de la requête.
    """
    client = get_bigquery_client()

    logger.info("Exécution de la requête BigQuery...")
    logger.debug(f"SQL: {sql_query[:200]}...")

    query_job = client.query(sql_query)
    results = query_job.result()

    df = results.to_dataframe()
    logger.info(f"Résultat: {len(df)} lignes, {len(df.columns)} colonnes")

    return df


def create_prices_table_sql(dataset_id: str, table_id: str) -> str:
    """
    Génère le SQL pour créer la table prices_history partitionnée.

    Args:
        dataset_id: ID du dataset BigQuery.
        table_id: ID de la table à créer.

    Returns:
        Requête SQL CREATE TABLE.
    """
    return f"""
    CREATE TABLE IF NOT EXISTS `{dataset_id}.{table_id}` (
        date DATE NOT NULL,
        ticker STRING NOT NULL,
        open FLOAT64,
        high FLOAT64,
        low FLOAT64,
        close FLOAT64,
        volume INT64
    )
    PARTITION BY date
    CLUSTER BY ticker
    OPTIONS (
        description = 'Prix historiques des ETF, partitionné par date',
        require_partition_filter = false
    )
    """


def monthly_aggregation_sql(dataset_id: str, table_id: str) -> str:
    """
    Génère le SQL pour agréger les prix mensuels.

    Args:
        dataset_id: ID du dataset BigQuery.
        table_id: ID de la table source.

    Returns:
        Requête SQL d'agrégation mensuelle.
    """
    return f"""
    SELECT
        DATE_TRUNC(date, MONTH) AS month,
        ticker,
        FIRST_VALUE(close) OVER (
            PARTITION BY ticker, DATE_TRUNC(date, MONTH)
            ORDER BY date
        ) AS open_month,
        MAX(high) AS high_month,
        MIN(low) AS low_month,
        LAST_VALUE(close) OVER (
            PARTITION BY ticker, DATE_TRUNC(date, MONTH)
            ORDER BY date
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS close_month,
        SUM(volume) AS volume_month,
        COUNT(*) AS trading_days
    FROM `{dataset_id}.{table_id}`
    GROUP BY month, ticker
    ORDER BY month DESC, ticker
    """


def main() -> None:
    """Point d'entrée principal — exemple d'utilisation."""
    logger.info("=== Test connexion BigQuery ===")

    try:
        client = get_bigquery_client()
        project_id = os.getenv("GCP_PROJECT_ID")

        # Test simple : liste des datasets
        datasets = list(client.list_datasets())
        if datasets:
            logger.info(f"Datasets trouvés: {[d.dataset_id for d in datasets]}")
        else:
            logger.info("Aucun dataset trouvé. Créez le dataset 'deeppilot' via la console GCP.")

        # Exemple de requête sur données publiques (pour test)
        test_query = """
        SELECT
            COUNT(*) as row_count,
            MIN(Date) as min_date,
            MAX(Date) as max_date
        FROM `bigquery-public-data.covid19_open_data.covid19_open_data`
        WHERE country_code = 'FR'
        LIMIT 1
        """

        logger.info("Test requête sur données publiques...")
        df = query_bigquery(test_query)
        logger.info(f"Résultat test:\n{df}")

    except ValueError as e:
        logger.error(f"Configuration manquante: {e}")
    except Exception as e:
        logger.error(f"Erreur BigQuery: {e}")


if __name__ == "__main__":
    main()
