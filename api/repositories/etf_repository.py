"""
Repository pour les données ETF.

Encapsule les requêtes SQL pour les prix et métadonnées ETF.
"""

from datetime import date
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


# Métadonnées des ETF (statiques)
ETF_METADATA = {
    "SPY": {
        "name": "SPDR S&P 500 ETF Trust",
        "asset_class": "Actions US large cap",
        "description": "Cœur actions US",
    },
    "EFA": {
        "name": "iShares MSCI EAFE",
        "asset_class": "Actions développées hors US",
        "description": "Diversification géographique",
    },
    "EEM": {
        "name": "iShares MSCI Emerging Markets",
        "asset_class": "Actions émergents",
        "description": "Beta émergent",
    },
    "TLT": {
        "name": "iShares 20+ Year Treasury Bond",
        "asset_class": "Obligations US longue durée",
        "description": "Anti-corrélation actions",
    },
    "HYG": {
        "name": "iShares iBoxx High Yield Corporate",
        "asset_class": "Obligations corporate haut rendement",
        "description": "Exposition spread crédit",
    },
    "GLD": {
        "name": "SPDR Gold Shares",
        "asset_class": "Or / matières premières",
        "description": "Refuge inflation et crise",
    },
    "VNQ": {
        "name": "Vanguard Real Estate ETF",
        "asset_class": "REIT US (immobilier coté)",
        "description": "Diversification actifs réels",
    },
    "SH": {
        "name": "ProShares Short S&P 500",
        "asset_class": "Inverse S&P 500 (-1x)",
        "description": "Exposition marché baissier",
    },
    "URTH": {
        "name": "iShares MSCI World ETF",
        "asset_class": "Actions monde",
        "description": "Benchmark MSCI World",
    },
    "QQQ": {
        "name": "Invesco QQQ Trust",
        "asset_class": "Actions US tech (NASDAQ 100)",
        "description": "Benchmark NASDAQ 100",
    },
}


def get_all_etfs() -> list[dict]:
    """
    Retourne la liste de tous les ETF avec leurs métadonnées.

    Returns:
        Liste de dictionnaires avec ticker, name, asset_class, description
    """
    return [
        {"ticker": ticker, **metadata}
        for ticker, metadata in ETF_METADATA.items()
    ]


def get_etf_by_ticker(ticker: str) -> Optional[dict]:
    """
    Retourne les métadonnées d'un ETF.

    Args:
        ticker: Symbole de l'ETF

    Returns:
        Dictionnaire avec les métadonnées ou None si non trouvé
    """
    ticker_upper = ticker.upper()
    if ticker_upper in ETF_METADATA:
        return {"ticker": ticker_upper, **ETF_METADATA[ticker_upper]}
    return None


def get_prices(
    db: Session,
    ticker: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 1000,
) -> list[dict]:
    """
    Récupère les prix d'un ETF.

    Args:
        db: Session SQLAlchemy
        ticker: Symbole de l'ETF
        start_date: Date de début (optionnel)
        end_date: Date de fin (optionnel)
        limit: Nombre max de résultats

    Returns:
        Liste de dictionnaires avec date, ticker, open, high, low, close, volume
    """
    query = """
        SELECT date, ticker, open, high, low, close, volume
        FROM price
        WHERE ticker = :ticker
    """
    params = {"ticker": ticker.upper(), "limit": limit}

    if start_date:
        query += " AND date >= :start_date"
        params["start_date"] = start_date

    if end_date:
        query += " AND date <= :end_date"
        params["end_date"] = end_date

    query += " ORDER BY date DESC LIMIT :limit"

    result = db.execute(text(query), params)
    rows = result.fetchall()

    return [
        {
            "date": row.date,
            "ticker": row.ticker,
            "open": row.open,
            "high": row.high,
            "low": row.low,
            "close": row.close,
            "volume": row.volume,
        }
        for row in rows
    ]


def get_price_date_range(db: Session, ticker: str) -> tuple[Optional[date], Optional[date]]:
    """
    Retourne la plage de dates disponible pour un ETF.

    Args:
        db: Session SQLAlchemy
        ticker: Symbole de l'ETF

    Returns:
        Tuple (min_date, max_date) ou (None, None) si pas de données
    """
    query = """
        SELECT MIN(date) as min_date, MAX(date) as max_date
        FROM price
        WHERE ticker = :ticker
    """
    result = db.execute(text(query), {"ticker": ticker.upper()})
    row = result.fetchone()

    if row and row.min_date:
        return row.min_date, row.max_date
    return None, None
