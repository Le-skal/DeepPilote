"""
Repository pour les features calculées.

Encapsule les requêtes SQL pour les features ML des ETF.
"""

from datetime import date
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


def get_features(
    db: Session,
    ticker: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 1000,
) -> list[dict]:
    """
    Récupère les features calculées pour un ETF.

    Args:
        db: Session SQLAlchemy
        ticker: Symbole de l'ETF
        start_date: Date de début (optionnel)
        end_date: Date de fin (optionnel)
        limit: Nombre max de résultats

    Returns:
        Liste de dictionnaires avec les features
    """
    query = """
        SELECT
            date, ticker,
            ret_1d, ret_5d, ret_20d, ret_60d,
            vol_20d, vol_60d,
            sma_20, sma_50, sma_200,
            rsi_14, macd, macd_signal, bb_position
        FROM feature
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
            "return_1d": row.ret_1d,
            "return_5d": row.ret_5d,
            "return_20d": row.ret_20d,
            "return_60d": row.ret_60d,
            "volatility_20d": row.vol_20d,
            "volatility_60d": row.vol_60d,
            "sma_20": row.sma_20,
            "sma_50": row.sma_50,
            "sma_200": row.sma_200,
            "rsi_14": row.rsi_14,
            "macd": row.macd,
            "macd_signal": row.macd_signal,
            "bb_position": row.bb_position,
        }
        for row in rows
    ]


def get_latest_features(db: Session, ticker: str) -> Optional[dict]:
    """
    Récupère les dernières features pour un ETF.

    Args:
        db: Session SQLAlchemy
        ticker: Symbole de l'ETF

    Returns:
        Dictionnaire avec les dernières features ou None
    """
    query = """
        SELECT
            date, ticker,
            ret_1d, ret_5d, ret_20d, ret_60d,
            vol_20d, vol_60d,
            sma_20, sma_50, sma_200,
            rsi_14, macd, macd_signal, bb_position
        FROM feature
        WHERE ticker = :ticker
        ORDER BY date DESC
        LIMIT 1
    """
    result = db.execute(text(query), {"ticker": ticker.upper()})
    row = result.fetchone()

    if row:
        return {
            "date": row.date,
            "ticker": row.ticker,
            "return_1d": row.ret_1d,
            "return_5d": row.ret_5d,
            "return_20d": row.ret_20d,
            "return_60d": row.ret_60d,
            "volatility_20d": row.vol_20d,
            "volatility_60d": row.vol_60d,
            "sma_20": row.sma_20,
            "sma_50": row.sma_50,
            "sma_200": row.sma_200,
            "rsi_14": row.rsi_14,
            "macd": row.macd,
            "macd_signal": row.macd_signal,
            "bb_position": row.bb_position,
        }
    return None
