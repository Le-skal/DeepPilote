"""
Chargement des données vers Supabase (PostgreSQL).

Ce module charge les données nettoyées (prix, macro, features) vers la base
de données Supabase, avec gestion de l'idempotence (INSERT ON CONFLICT).

Usage:
    python -m data.pipeline.load_to_db
"""

import logging
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

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
PROCESSED_DIR = DATA_DIR / "processed"
SQL_DIR = DATA_DIR / "sql" / "postgres"


def connect_supabase() -> Engine:
    """
    Crée une connexion SQLAlchemy vers Supabase.

    Returns:
        Engine SQLAlchemy configuré.

    Raises:
        ValueError: Si l'URL de connexion n'est pas définie.
    """
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        raise ValueError(
            "SUPABASE_DB_URL non définie.\n"
            "Format: postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres"
        )

    engine = create_engine(db_url)
    logger.info("Connexion Supabase établie")
    return engine


def execute_sql_file(engine: Engine, filepath: Path) -> None:
    """
    Exécute un fichier SQL sur la base de données.

    Args:
        engine: Engine SQLAlchemy.
        filepath: Chemin du fichier SQL.
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Fichier SQL non trouvé: {filepath}")

    sql_content = filepath.read_text(encoding="utf-8")
    logger.info(f"Exécution: {filepath.name}")

    with engine.connect() as conn:
        conn.execute(text(sql_content))
        conn.commit()


def load_etfs_metadata(engine: Engine) -> None:
    """
    Charge les métadonnées des ETF dans la table 'etf'.

    Args:
        engine: Engine SQLAlchemy.
    """
    # Métadonnées des 8 ETF + 2 benchmarks
    etfs = [
        ("SPY", "SPDR S&P 500 ETF Trust", "equity_us_large", "1993-01-22"),
        ("EFA", "iShares MSCI EAFE ETF", "equity_developed_ex_us", "2001-08-14"),
        ("EEM", "iShares MSCI Emerging Markets ETF", "equity_emerging", "2003-04-07"),
        ("TLT", "iShares 20+ Year Treasury Bond ETF", "bond_us_long", "2002-07-22"),
        ("HYG", "iShares iBoxx High Yield Corporate Bond ETF", "bond_high_yield", "2007-04-04"),
        ("GLD", "SPDR Gold Shares", "commodity_gold", "2004-11-18"),
        ("VNQ", "Vanguard Real Estate ETF", "reit_us", "2004-09-23"),
        ("SH", "ProShares Short S&P 500", "inverse_sp500", "2006-06-19"),
        ("URTH", "iShares MSCI World ETF", "equity_world", "2012-01-10"),
        ("QQQ", "Invesco QQQ Trust", "equity_us_tech", "1999-03-10"),
    ]

    df = pd.DataFrame(etfs, columns=["ticker", "name", "asset_class", "inception_date"])
    df["inception_date"] = pd.to_datetime(df["inception_date"])

    logger.info(f"Chargement de {len(df)} ETF dans la table 'etf'")

    # Upsert via INSERT ON CONFLICT
    with engine.connect() as conn:
        for _, row in df.iterrows():
            sql = text("""
                INSERT INTO etf (ticker, name, asset_class, inception_date)
                VALUES (:ticker, :name, :asset_class, :inception_date)
                ON CONFLICT (ticker) DO UPDATE SET
                    name = EXCLUDED.name,
                    asset_class = EXCLUDED.asset_class,
                    inception_date = EXCLUDED.inception_date
            """)
            conn.execute(sql, row.to_dict())
        conn.commit()

    logger.info("✓ Métadonnées ETF chargées")


def load_prices(engine: Engine, df: pd.DataFrame, tickers: list[str]) -> None:
    """
    Charge les prix dans la table 'price'.

    Args:
        engine: Engine SQLAlchemy.
        df: DataFrame avec les prix (colonnes = tickers).
        tickers: Liste des tickers à charger.
    """
    logger.info(f"Chargement des prix pour {len(tickers)} tickers...")

    # Transformer le DataFrame wide → long
    price_records = []
    for ticker in tickers:
        if ticker not in df.columns:
            continue
        for date, price in df[ticker].dropna().items():
            price_records.append({
                "ticker": ticker,
                "date": date,
                "close": float(price),
            })

    logger.info(f"  {len(price_records)} enregistrements à insérer")

    # Batch insert avec ON CONFLICT
    batch_size = 1000
    with engine.connect() as conn:
        for i in range(0, len(price_records), batch_size):
            batch = price_records[i:i + batch_size]
            for record in batch:
                sql = text("""
                    INSERT INTO price (ticker, date, close)
                    VALUES (:ticker, :date, :close)
                    ON CONFLICT (ticker, date) DO UPDATE SET
                        close = EXCLUDED.close
                """)
                conn.execute(sql, record)
            conn.commit()
            logger.info(f"  Batch {i // batch_size + 1}: {len(batch)} lignes")

    logger.info("✓ Prix chargés")


def load_macro(engine: Engine, df: pd.DataFrame) -> None:
    """
    Charge les indicateurs macro dans la table 'macro_indicator'.

    Args:
        engine: Engine SQLAlchemy.
        df: DataFrame avec les indicateurs macro.
    """
    # Colonnes macro attendues
    macro_cols = ["vix", "credit_spread_hy", "yield_curve_10y2y", "t3mo", "t10y",
                  "wti_oil", "usd_eur", "unemployment", "cpi"]

    present_cols = [c for c in macro_cols if c in df.columns]
    logger.info(f"Chargement macro: {present_cols}")

    records = []
    for date, row in df[present_cols].iterrows():
        record = {"date": date}
        for col in present_cols:
            val = row[col]
            record[col] = float(val) if pd.notna(val) else None
        records.append(record)

    logger.info(f"  {len(records)} enregistrements à insérer")

    # Construction dynamique du SQL
    cols_str = ", ".join(present_cols)
    vals_str = ", ".join([f":{c}" for c in present_cols])
    update_str = ", ".join([f"{c} = EXCLUDED.{c}" for c in present_cols])

    with engine.connect() as conn:
        for record in records:
            sql = text(f"""
                INSERT INTO macro_indicator (date, {cols_str})
                VALUES (:date, {vals_str})
                ON CONFLICT (date) DO UPDATE SET
                    {update_str}
            """)
            conn.execute(sql, record)
        conn.commit()

    logger.info("✓ Indicateurs macro chargés")


def load_features(engine: Engine, df: pd.DataFrame, tickers: list[str]) -> None:
    """
    Charge les features calculées dans la table 'feature'.

    Args:
        engine: Engine SQLAlchemy.
        df: DataFrame avec les features.
        tickers: Liste des tickers.
    """
    logger.info("Chargement des features...")

    # Features par ticker
    feature_suffixes = ["_ret_1d", "_ret_20d", "_vol_20d", "_sma_20", "_rsi_14"]

    records = []
    for ticker in tickers:
        ticker_cols = {
            suffix: f"{ticker}{suffix}"
            for suffix in feature_suffixes
            if f"{ticker}{suffix}" in df.columns
        }

        if not ticker_cols:
            continue

        for date, row in df.iterrows():
            record = {"ticker": ticker, "date": date}
            for suffix, col in ticker_cols.items():
                val = row[col]
                # Normaliser le nom de colonne pour la DB
                db_col = suffix.lstrip("_")
                record[db_col] = float(val) if pd.notna(val) else None
            records.append(record)

    logger.info(f"  {len(records)} enregistrements")

    # Insertion simplifiée (la structure exacte dépend du schéma créé)
    batch_size = 1000
    with engine.connect() as conn:
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            for record in batch:
                # Insertion basique - à adapter selon le schéma exact
                sql = text("""
                    INSERT INTO feature (ticker, date, ret_1d, ret_20d, vol_20d, sma_20, rsi_14)
                    VALUES (:ticker, :date, :ret_1d, :ret_20d, :vol_20d, :sma_20, :rsi_14)
                    ON CONFLICT (ticker, date) DO UPDATE SET
                        ret_1d = EXCLUDED.ret_1d,
                        ret_20d = EXCLUDED.ret_20d,
                        vol_20d = EXCLUDED.vol_20d,
                        sma_20 = EXCLUDED.sma_20,
                        rsi_14 = EXCLUDED.rsi_14
                """)
                conn.execute(sql, record)
            conn.commit()
            if i % 5000 == 0:
                logger.info(f"  Progression: {i}/{len(records)}")

    logger.info("✓ Features chargées")


def get_row_counts(engine: Engine) -> dict[str, int]:
    """
    Retourne le nombre de lignes dans chaque table.

    Args:
        engine: Engine SQLAlchemy.

    Returns:
        Dictionnaire {table_name: row_count}.
    """
    tables = ["etf", "price", "macro_indicator", "feature"]
    counts = {}

    with engine.connect() as conn:
        for table in tables:
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                counts[table] = result.scalar()
            except Exception:
                counts[table] = -1  # Table n'existe pas

    return counts


def main() -> None:
    """Point d'entrée principal."""
    from data.extractors.extract_yfinance import ALL_TICKERS, ETF_TICKERS

    logger.info("=== Chargement vers Supabase ===")

    # 1. Connexion
    try:
        engine = connect_supabase()
    except ValueError as e:
        logger.error(str(e))
        return

    # 2. Initialisation du schéma (si le fichier existe)
    schema_file = SQL_DIR / "01_init_schema.sql"
    if schema_file.exists():
        try:
            execute_sql_file(engine, schema_file)
            logger.info("Schéma initialisé")
        except Exception as e:
            logger.warning(f"Schéma peut-être déjà existant: {e}")

    # 3. Chargement des métadonnées ETF
    load_etfs_metadata(engine)

    # 4. Chargement des données
    dataset_files = sorted(PROCESSED_DIR.glob("dataset_*.csv"))
    if not dataset_files:
        logger.error(f"Aucun fichier dataset_*.csv dans {PROCESSED_DIR}")
        logger.info("Lancez d'abord le pipeline d'agrégation (aggregate.py)")
        return

    df = pd.read_csv(dataset_files[-1], index_col=0, parse_dates=True)
    logger.info(f"Dataset chargé: {dataset_files[-1].name} ({len(df)} lignes)")

    # 5. Chargement prix
    load_prices(engine, df, ALL_TICKERS)

    # 6. Chargement macro
    load_macro(engine, df)

    # 7. Chargement features
    load_features(engine, df, ETF_TICKERS)

    # 8. Vérification
    counts = get_row_counts(engine)
    logger.info("=== Résumé ===")
    for table, count in counts.items():
        logger.info(f"  {table}: {count} lignes")


if __name__ == "__main__":
    main()
