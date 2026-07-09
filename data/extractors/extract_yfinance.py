"""
Extraction des prix ETF depuis Yahoo Finance.

Ce module télécharge les prix ajustés (adjusted close) des ETF et benchmarks
depuis yfinance, puis les sauvegarde en CSV.

Supporte le mode incrémental : ne télécharge que les données depuis la dernière
date en base de données (via variable INCREMENTAL=true).

Usage:
    python -m data.extractors.extract_yfinance                    # Full reload
    INCREMENTAL=true python -m data.extractors.extract_yfinance   # Incrémental
"""

import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep

import pandas as pd
import yfinance as yf

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Constantes
# ETF du portefeuille DeepPilot (URTH remplace SPY qui est maintenant benchmark)
ETF_TICKERS: list[str] = ["URTH", "EFA", "EEM", "TLT", "HYG", "GLD", "VNQ", "SH"]
BENCHMARK_TICKERS: list[str] = ["SPY", "QQQ"]
ALL_TICKERS: list[str] = ETF_TICKERS + BENCHMARK_TICKERS

# Chemins
DATA_DIR = Path(__file__).parent.parent
RAW_DIR = DATA_DIR / "raw"


def download_etf_prices(
    tickers: list[str],
    start_date: str,
    end_date: str,
    max_retries: int = 3,
) -> pd.DataFrame:
    """
    Télécharge les prix ajustés des ETF depuis Yahoo Finance.

    Args:
        tickers: Liste des tickers à télécharger.
        start_date: Date de début au format YYYY-MM-DD.
        end_date: Date de fin au format YYYY-MM-DD.
        max_retries: Nombre de tentatives en cas d'erreur réseau.

    Returns:
        DataFrame avec index DatetimeIndex et colonnes = tickers.
        Les valeurs sont les prix ajustés (adjusted close).
    """
    logger.info(f"Téléchargement de {len(tickers)} tickers: {tickers}")
    logger.info(f"Période: {start_date} → {end_date}")

    for attempt in range(max_retries):
        try:
            # yfinance >= 0.2.x : "Close" contient déjà l'adjusted close
            data = yf.download(
                tickers=tickers,
                start=start_date,
                end=end_date,
                progress=True,
                auto_adjust=True,  # Retourne les prix ajustés
            )

            # Si un seul ticker, yf.download retourne un DataFrame simple
            # Si plusieurs tickers, retourne un MultiIndex (OHLCV, Ticker)
            if isinstance(data.columns, pd.MultiIndex):
                # On prend uniquement la colonne "Close"
                prices = data["Close"]
            else:
                # Un seul ticker
                prices = data[["Close"]]
                prices.columns = tickers

            # Vérification des données
            missing_tickers = [t for t in tickers if t not in prices.columns]
            if missing_tickers:
                logger.warning(f"Tickers manquants: {missing_tickers}")

            valid_tickers = [t for t in tickers if t in prices.columns]
            logger.info(f"Tickers téléchargés avec succès: {valid_tickers}")
            logger.info(f"Nombre de lignes: {len(prices)}")

            return prices

        except Exception as e:
            logger.error(f"Erreur tentative {attempt + 1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                sleep(2 ** attempt)  # Backoff exponentiel
            else:
                raise RuntimeError(f"Échec après {max_retries} tentatives: {e}")

    return pd.DataFrame()


def save_to_csv(df: pd.DataFrame, filepath: Path) -> None:
    """
    Sauvegarde le DataFrame en CSV.

    Args:
        df: DataFrame à sauvegarder.
        filepath: Chemin du fichier de sortie.
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=True, date_format="%Y-%m-%d")
    logger.info(f"Données sauvegardées: {filepath}")
    logger.info(f"Taille: {filepath.stat().st_size / 1024:.1f} KB")


def get_last_date_from_db() -> str | None:
    """
    Récupère la dernière date de prix en base de données.

    Returns:
        Date au format YYYY-MM-DD ou None si pas de connexion.
    """
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        logger.warning("SUPABASE_DB_URL non définie, mode full reload")
        return None

    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT MAX(date) FROM price"))
            last_date = result.scalar()

        if last_date:
            logger.info(f"Dernière date en DB: {last_date}")
            return last_date.strftime("%Y-%m-%d")
        return None
    except Exception as e:
        logger.warning(f"Impossible de lire la DB: {e}")
        return None


def main() -> None:
    """Point d'entrée principal."""
    # Mode incrémental ?
    incremental = os.getenv("INCREMENTAL", "false").lower() == "true"

    if incremental:
        logger.info("=== MODE INCRÉMENTAL ===")
        last_date = get_last_date_from_db()
        if last_date:
            # On recule de 5 jours pour rattraper d'éventuels ajustements
            start_dt = datetime.strptime(last_date, "%Y-%m-%d") - timedelta(days=5)
            start_date = start_dt.strftime("%Y-%m-%d")
            logger.info(f"Téléchargement depuis {start_date} (5 jours avant dernière date)")
        else:
            start_date = "2010-01-01"
            logger.info("Pas de date en DB, full reload")
    else:
        logger.info("=== MODE FULL RELOAD ===")
        start_date = "2010-01-01"

    end_date = datetime.now().strftime("%Y-%m-%d")

    # Téléchargement
    prices = download_etf_prices(ALL_TICKERS, start_date, end_date)

    # Sauvegarde
    filename = f"prices_{datetime.now().strftime('%Y%m%d')}.csv"
    filepath = RAW_DIR / filename
    save_to_csv(prices, filepath)

    # Stats finales
    logger.info("=== Résumé ===")
    logger.info(f"Mode: {'incrémental' if incremental else 'full reload'}")
    logger.info(f"Colonnes: {list(prices.columns)}")
    logger.info(f"Période: {prices.index.min()} → {prices.index.max()}")
    logger.info(f"Lignes: {len(prices)}")
    logger.info(f"NaN par colonne:\n{prices.isna().sum()}")


if __name__ == "__main__":
    main()
