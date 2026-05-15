"""
Extraction des données macroéconomiques depuis FRED (Federal Reserve).

Ce module télécharge les indicateurs macro (VIX, courbe de taux, spreads, etc.)
via l'API FRED, puis les sauvegarde en CSV.

Usage:
    python -m data.extractors.extract_fred
"""

import logging
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from fredapi import Fred

# Chargement des variables d'environnement
load_dotenv()

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Séries FRED à récupérer
# Format: (code_fred, nom_colonne, description)
FRED_SERIES: list[tuple[str, str, str]] = [
    ("VIXCLS", "vix", "CBOE Volatility Index"),
    ("BAA10Y", "credit_spread_hy", "Moody's BAA Corporate - 10Y Treasury Spread"),
    ("T10Y2Y", "yield_curve_10y2y", "10Y-2Y Treasury Yield Spread"),
    ("DGS3MO", "t3mo", "3-Month Treasury Rate (risk-free)"),
    ("DGS10", "t10y", "10-Year Treasury Rate"),
    ("DCOILWTICO", "wti_oil", "WTI Crude Oil Price"),
    ("DEXUSEU", "usd_eur", "USD/EUR Exchange Rate"),
    ("UNRATE", "unemployment", "US Unemployment Rate (monthly)"),
    ("CPIAUCSL", "cpi", "US CPI Inflation (monthly)"),
]

# Chemins
DATA_DIR = Path(__file__).parent.parent
RAW_DIR = DATA_DIR / "raw"


def get_fred_client() -> Fred:
    """
    Crée un client FRED avec la clé API.

    Returns:
        Instance Fred configurée.

    Raises:
        ValueError: Si la clé API n'est pas définie.
    """
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise ValueError(
            "FRED_API_KEY non définie. "
            "Créez un compte sur https://fred.stlouisfed.org/docs/api/api_key.html"
        )
    return Fred(api_key=api_key)


def get_fred_series(
    series_ids: list[tuple[str, str, str]],
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """
    Télécharge plusieurs séries FRED et les fusionne.

    Les séries mensuelles sont forward-fillées pour aligner sur les données daily.

    Args:
        series_ids: Liste de tuples (code_fred, nom_colonne, description).
        start_date: Date de début au format YYYY-MM-DD.
        end_date: Date de fin au format YYYY-MM-DD.

    Returns:
        DataFrame avec index DatetimeIndex et colonnes = noms des séries.
    """
    fred = get_fred_client()
    logger.info(f"Téléchargement de {len(series_ids)} séries FRED")
    logger.info(f"Période: {start_date} → {end_date}")

    all_series = {}
    failed_series = []

    for fred_code, col_name, description in series_ids:
        try:
            logger.info(f"  → {fred_code} ({description})")
            series = fred.get_series(
                fred_code,
                observation_start=start_date,
                observation_end=end_date,
            )
            all_series[col_name] = series
        except Exception as e:
            logger.error(f"  ✗ Échec {fred_code}: {e}")
            failed_series.append(fred_code)

    if failed_series:
        logger.warning(f"Séries non téléchargées: {failed_series}")

    # Création du DataFrame
    df = pd.DataFrame(all_series)
    df.index = pd.to_datetime(df.index)
    df.index.name = "Date"

    # Forward-fill pour les séries mensuelles (unemployment, cpi)
    # Cela propage la dernière valeur connue jusqu'à la prochaine publication
    df = df.ffill()

    logger.info(f"Lignes: {len(df)}, Colonnes: {list(df.columns)}")
    return df


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
    macro_data = get_fred_series(FRED_SERIES, start_date, end_date)

    # Sauvegarde
    filename = f"macro_{datetime.now().strftime('%Y%m%d')}.csv"
    filepath = RAW_DIR / filename
    save_to_csv(macro_data, filepath)

    # Stats finales
    logger.info("=== Résumé ===")
    logger.info(f"Colonnes: {list(macro_data.columns)}")
    logger.info(f"Période: {macro_data.index.min()} → {macro_data.index.max()}")
    logger.info(f"NaN par colonne:\n{macro_data.isna().sum()}")

    # Validations basiques
    if "vix" in macro_data.columns:
        vix_range = macro_data["vix"].dropna()
        logger.info(f"VIX range: {vix_range.min():.1f} - {vix_range.max():.1f}")

    if "yield_curve_10y2y" in macro_data.columns:
        yc = macro_data["yield_curve_10y2y"].dropna()
        inversions = (yc < 0).sum()
        logger.info(f"Jours d'inversion courbe taux: {inversions}")


if __name__ == "__main__":
    main()
