"""
Pipeline d'agrégation et de nettoyage des données.

Ce module fusionne les données prix ETF et macro, applique les règles de nettoyage,
et calcule les features de base (returns, volatilité, indicateurs techniques).

En mode incrémental (INCREMENTAL=true), charge l'historique depuis Supabase
puis ajoute les nouvelles données avant de recalculer les features.

Usage:
    python -m data.pipeline.aggregate                    # Depuis fichiers raw
    INCREMENTAL=true python -m data.pipeline.aggregate   # Depuis DB + nouvelles données
"""

import logging
import os
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from data.pipeline.cleaning_rules import (
    check_temporal_monotonicity,
    detect_outliers,
    handle_missing_values,
)

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Chemins
DATA_DIR = Path(__file__).parent.parent
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


def merge_prices_macro(prices_df: pd.DataFrame, macro_df: pd.DataFrame) -> pd.DataFrame:
    """
    Fusionne les données prix et macro sur la colonne date.

    Les features macro mensuelles sont forward-fillées pour avoir une valeur
    pour chaque jour de trading.

    Args:
        prices_df: DataFrame des prix ETF (index = Date).
        macro_df: DataFrame des indicateurs macro (index = Date).

    Returns:
        DataFrame fusionné avec toutes les colonnes.
    """
    logger.info(f"Fusion prix ({len(prices_df)} lignes) + macro ({len(macro_df)} lignes)")

    # S'assurer que les index sont des DatetimeIndex
    if not isinstance(prices_df.index, pd.DatetimeIndex):
        prices_df.index = pd.to_datetime(prices_df.index)
    if not isinstance(macro_df.index, pd.DatetimeIndex):
        macro_df.index = pd.to_datetime(macro_df.index)

    # Merge sur l'index date (outer join pour garder toutes les dates)
    merged = prices_df.join(macro_df, how="left")

    # Forward-fill des features macro (données mensuelles propagées)
    macro_cols = macro_df.columns.tolist()
    merged[macro_cols] = merged[macro_cols].ffill()

    logger.info(f"Résultat fusion: {len(merged)} lignes, {len(merged.columns)} colonnes")
    return merged


def clean_data(df: pd.DataFrame, etf_tickers: list[str]) -> pd.DataFrame:
    """
    Applique les règles de nettoyage sur le DataFrame.

    Args:
        df: DataFrame à nettoyer.
        etf_tickers: Liste des colonnes ETF (prix critiques).

    Returns:
        DataFrame nettoyé avec colonne 'is_outlier' ajoutée.
    """
    logger.info("=== Nettoyage des données ===")

    # 1. Vérification monotonie temporelle
    check_temporal_monotonicity(df)

    # 2. Gestion des valeurs manquantes
    df = handle_missing_values(df, critical_cols=etf_tickers)

    # 3. Détection des outliers (returns > |10%|)
    df = detect_outliers(df, etf_tickers, threshold=0.10)

    logger.info(f"Données nettoyées: {len(df)} lignes")
    return df


def compute_returns(df: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    """
    Calcule les rendements simples et log pour différentes périodes.

    Args:
        df: DataFrame avec les prix.
        tickers: Liste des tickers pour lesquels calculer les returns.

    Returns:
        DataFrame avec colonnes de returns ajoutées.
    """
    logger.info("Calcul des rendements...")

    for ticker in tickers:
        if ticker not in df.columns:
            continue

        price = df[ticker]

        # Returns simples
        df[f"{ticker}_ret_1d"] = price.pct_change(1)
        df[f"{ticker}_ret_5d"] = price.pct_change(5)
        df[f"{ticker}_ret_20d"] = price.pct_change(20)
        df[f"{ticker}_ret_60d"] = price.pct_change(60)

        # Log returns (meilleur pour ML, additivité temporelle)
        df[f"{ticker}_logret_1d"] = np.log(price / price.shift(1))

    return df


def compute_volatility(df: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    """
    Calcule la volatilité réalisée rolling.

    Args:
        df: DataFrame avec les log returns.
        tickers: Liste des tickers.

    Returns:
        DataFrame avec colonnes de volatilité ajoutées.
    """
    logger.info("Calcul de la volatilité réalisée...")

    for ticker in tickers:
        logret_col = f"{ticker}_logret_1d"
        if logret_col not in df.columns:
            continue

        logret = df[logret_col]

        # Volatilité rolling (annualisée : * sqrt(252))
        df[f"{ticker}_vol_20d"] = logret.rolling(20).std() * np.sqrt(252)
        df[f"{ticker}_vol_60d"] = logret.rolling(60).std() * np.sqrt(252)

    return df


def compute_technical_indicators(df: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    """
    Calcule les indicateurs techniques de base.

    Indicateurs:
    - SMA 20, 50, 200 jours
    - RSI 14 jours
    - MACD (12, 26, 9)
    - Bandes de Bollinger (20 jours, 2 écarts-types)

    Args:
        df: DataFrame avec les prix.
        tickers: Liste des tickers.

    Returns:
        DataFrame avec indicateurs ajoutés.
    """
    logger.info("Calcul des indicateurs techniques...")

    for ticker in tickers:
        if ticker not in df.columns:
            continue

        price = df[ticker]

        # Simple Moving Averages
        df[f"{ticker}_sma_20"] = price.rolling(20).mean()
        df[f"{ticker}_sma_50"] = price.rolling(50).mean()
        df[f"{ticker}_sma_200"] = price.rolling(200).mean()

        # RSI (Relative Strength Index)
        delta = price.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df[f"{ticker}_rsi_14"] = 100 - (100 / (1 + rs))

        # MACD
        ema_12 = price.ewm(span=12, adjust=False).mean()
        ema_26 = price.ewm(span=26, adjust=False).mean()
        df[f"{ticker}_macd"] = ema_12 - ema_26
        df[f"{ticker}_macd_signal"] = df[f"{ticker}_macd"].ewm(span=9, adjust=False).mean()

        # Bollinger Bands
        sma_20 = df[f"{ticker}_sma_20"]
        std_20 = price.rolling(20).std()
        df[f"{ticker}_bb_upper"] = sma_20 + (2 * std_20)
        df[f"{ticker}_bb_lower"] = sma_20 - (2 * std_20)
        # Position relative dans les bandes (0 = lower, 1 = upper)
        df[f"{ticker}_bb_position"] = (price - df[f"{ticker}_bb_lower"]) / (
            df[f"{ticker}_bb_upper"] - df[f"{ticker}_bb_lower"]
        )

    return df


def compute_basic_features(df: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    """
    Pipeline complet de calcul des features.

    Args:
        df: DataFrame avec les prix et macro.
        tickers: Liste des tickers ETF.

    Returns:
        DataFrame avec toutes les features calculées.
    """
    logger.info("=== Calcul des features ===")

    df = compute_returns(df, tickers)
    df = compute_volatility(df, tickers)
    df = compute_technical_indicators(df, tickers)

    # Stats
    feature_cols = [c for c in df.columns if any(x in c for x in ["_ret_", "_vol_", "_sma_", "_rsi_", "_macd", "_bb_"])]
    logger.info(f"Features calculées: {len(feature_cols)} colonnes")

    return df


def load_latest_raw_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Charge les derniers fichiers prix et macro du dossier raw.

    Returns:
        Tuple (prices_df, macro_df).
    """
    # Trouver le dernier fichier prix
    price_files = sorted(RAW_DIR.glob("prices_*.csv"))
    if not price_files:
        raise FileNotFoundError(f"Aucun fichier prices_*.csv dans {RAW_DIR}")
    prices_df = pd.read_csv(price_files[-1], index_col=0, parse_dates=True)
    logger.info(f"Chargé: {price_files[-1].name}")

    # Trouver le dernier fichier macro
    macro_files = sorted(RAW_DIR.glob("macro_*.csv"))
    if not macro_files:
        raise FileNotFoundError(f"Aucun fichier macro_*.csv dans {RAW_DIR}")
    macro_df = pd.read_csv(macro_files[-1], index_col=0, parse_dates=True)
    logger.info(f"Chargé: {macro_files[-1].name}")

    return prices_df, macro_df


def load_history_from_db() -> tuple[pd.DataFrame, pd.DataFrame] | None:
    """
    Charge l'historique des prix et macro depuis Supabase.

    Returns:
        Tuple (prices_df, macro_df) ou None si pas de connexion.
    """
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        logger.warning("SUPABASE_DB_URL non définie")
        return None

    try:
        from sqlalchemy import create_engine

        engine = create_engine(db_url)

        # Charger les prix (format long -> wide)
        logger.info("Chargement des prix depuis Supabase...")
        prices_long = pd.read_sql(
            "SELECT date, ticker, close FROM price ORDER BY date",
            engine,
            parse_dates=["date"],
        )
        prices_df = prices_long.pivot(index="date", columns="ticker", values="close")
        prices_df.index.name = "Date"
        logger.info(f"  Prix: {len(prices_df)} lignes, {len(prices_df.columns)} tickers")

        # Charger les macro
        logger.info("Chargement macro depuis Supabase...")
        macro_df = pd.read_sql(
            "SELECT * FROM macro_indicator ORDER BY date",
            engine,
            parse_dates=["date"],
        )
        macro_df = macro_df.set_index("date")
        macro_df.index.name = "Date"
        logger.info(f"  Macro: {len(macro_df)} lignes")

        return prices_df, macro_df

    except Exception as e:
        logger.error(f"Erreur chargement DB: {e}")
        return None


def merge_incremental_data(
    db_prices: pd.DataFrame,
    db_macro: pd.DataFrame,
    new_prices: pd.DataFrame,
    new_macro: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Fusionne les données historiques DB avec les nouvelles données.

    Les nouvelles données écrasent les anciennes en cas de conflit (même date).

    Args:
        db_prices: Prix historiques depuis DB.
        db_macro: Macro historiques depuis DB.
        new_prices: Nouvelles données prix.
        new_macro: Nouvelles données macro.

    Returns:
        Tuple (merged_prices, merged_macro).
    """
    logger.info("Fusion des données historiques avec les nouvelles...")

    # Fusionner les prix (nouvelles données prioritaires)
    merged_prices = pd.concat([db_prices, new_prices])
    merged_prices = merged_prices[~merged_prices.index.duplicated(keep="last")]
    merged_prices = merged_prices.sort_index()
    logger.info(f"  Prix après fusion: {len(merged_prices)} lignes")

    # Fusionner les macro
    merged_macro = pd.concat([db_macro, new_macro])
    merged_macro = merged_macro[~merged_macro.index.duplicated(keep="last")]
    merged_macro = merged_macro.sort_index()
    logger.info(f"  Macro après fusion: {len(merged_macro)} lignes")

    return merged_prices, merged_macro


def main() -> None:
    """Point d'entrée principal du pipeline."""
    from data.extractors.extract_yfinance import ETF_TICKERS

    incremental = os.getenv("INCREMENTAL", "false").lower() == "true"

    if incremental:
        logger.info("=== Pipeline d'agrégation (MODE INCRÉMENTAL) ===")
    else:
        logger.info("=== Pipeline d'agrégation ===")

    # 1. Chargement des données brutes (nouvelles données du jour)
    try:
        new_prices, new_macro = load_latest_raw_data()
    except FileNotFoundError as e:
        logger.error(f"Données manquantes: {e}")
        logger.info("Lancez d'abord les extracteurs (extract_yfinance.py, extract_fred.py)")
        return

    # 2. En mode incrémental, charger l'historique depuis DB et fusionner
    if incremental:
        db_data = load_history_from_db()
        if db_data:
            db_prices, db_macro = db_data
            prices_df, macro_df = merge_incremental_data(
                db_prices, db_macro, new_prices, new_macro
            )
        else:
            logger.warning("Pas de données DB, utilisation des fichiers raw uniquement")
            prices_df, macro_df = new_prices, new_macro
    else:
        prices_df, macro_df = new_prices, new_macro

    # 3. Fusion prix + macro
    merged = merge_prices_macro(prices_df, macro_df)

    # 4. Nettoyage
    cleaned = clean_data(merged, etf_tickers=ETF_TICKERS)

    # 5. Calcul des features
    final = compute_basic_features(cleaned, tickers=ETF_TICKERS)

    # 6. Sauvegarde
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_file = PROCESSED_DIR / f"dataset_{datetime.now().strftime('%Y%m%d')}.csv"
    final.to_csv(output_file)
    logger.info(f"Dataset sauvegardé: {output_file}")

    # Stats finales
    logger.info("=== Résumé ===")
    logger.info(f"Mode: {'incrémental' if incremental else 'full reload'}")
    logger.info(f"Période: {final.index.min()} → {final.index.max()}")
    logger.info(f"Lignes: {len(final)}")
    logger.info(f"Colonnes: {len(final.columns)}")
    logger.info(f"NaN total: {final.isna().sum().sum()}")


if __name__ == "__main__":
    main()
