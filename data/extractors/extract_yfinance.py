"""
Extraction des prix ETF depuis Yahoo Finance.

Ce module télécharge les prix ajustés (adjusted close) des ETF et benchmarks
depuis yfinance, puis les sauvegarde en CSV.

Usage:
    python -m data.extractors.extract_yfinance
"""

import logging
from datetime import datetime
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
ETF_TICKERS: list[str] = ["SPY", "EFA", "EEM", "TLT", "HYG", "GLD", "VNQ", "SH"]
BENCHMARK_TICKERS: list[str] = ["URTH", "QQQ"]
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


def main() -> None:
    """Point d'entrée principal."""
    # Paramètres
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
    logger.info(f"Colonnes: {list(prices.columns)}")
    logger.info(f"Période: {prices.index.min()} → {prices.index.max()}")
    logger.info(f"Lignes: {len(prices)}")
    logger.info(f"NaN par colonne:\n{prices.isna().sum()}")


if __name__ == "__main__":
    main()
