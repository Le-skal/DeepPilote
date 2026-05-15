"""
Repository pour les indicateurs macro.

Encapsule les requêtes SQL pour les données macro (FRED).
"""

from datetime import date
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


# Mapping des noms de colonnes vers les noms API
MACRO_COLUMNS = {
    "vix": "vix",
    "credit_spread": "credit_spread",
    "yield_curve_10y2y": "yield_curve_10y2y",
    "t3mo": "t3mo",
    "t10y": "t10y",
    "oil_wti": "oil_wti",
    "usd_eur": "usd_eur",
    "unemployment": "unemployment",
    "cpi": "cpi",
}


def get_macro_indicators(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 1000,
) -> list[dict]:
    """
    Récupère les indicateurs macro.

    Args:
        db: Session SQLAlchemy
        start_date: Date de début (optionnel)
        end_date: Date de fin (optionnel)
        limit: Nombre max de résultats

    Returns:
        Liste de dictionnaires avec les indicateurs
    """
    query = """
        SELECT date, vix, credit_spread_hy, yield_curve_10y2y, t3mo, t10y,
               wti_oil, usd_eur, unemployment, cpi
        FROM macro_indicator
        WHERE 1=1
    """
    params = {"limit": limit}

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
            "vix": row.vix,
            "credit_spread": row.credit_spread_hy,
            "yield_curve_10y2y": row.yield_curve_10y2y,
            "t3mo": row.t3mo,
            "t10y": row.t10y,
            "oil_wti": row.wti_oil,
            "usd_eur": row.usd_eur,
            "unemployment": row.unemployment,
            "cpi": row.cpi,
        }
        for row in rows
    ]


def get_latest_macro(db: Session) -> Optional[dict]:
    """
    Récupère les dernières valeurs connues des indicateurs macro.

    Args:
        db: Session SQLAlchemy

    Returns:
        Dictionnaire avec les dernières valeurs ou None
    """
    query = """
        SELECT date, vix, credit_spread_hy, yield_curve_10y2y, t3mo, t10y, wti_oil
        FROM macro_indicator
        WHERE vix IS NOT NULL
        ORDER BY date DESC
        LIMIT 1
    """
    result = db.execute(text(query))
    row = result.fetchone()

    if row:
        return {
            "as_of_date": row.date,
            "vix": row.vix,
            "t3mo": row.t3mo,
            "t10y": row.t10y,
            "yield_curve_10y2y": row.yield_curve_10y2y,
            "credit_spread": row.credit_spread_hy,
            "oil_wti": row.wti_oil,
        }
    return None


def get_macro_stats(db: Session, indicator: str) -> Optional[dict]:
    """
    Calcule les statistiques pour un indicateur macro.

    Args:
        db: Session SQLAlchemy
        indicator: Nom de l'indicateur (ex: "vix")

    Returns:
        Dictionnaire avec current, mean, std, min, max, percentile
    """
    if indicator not in MACRO_COLUMNS:
        return None

    column = MACRO_COLUMNS[indicator]

    query = f"""
        SELECT
            (SELECT {column} FROM macro_indicator WHERE {column} IS NOT NULL ORDER BY date DESC LIMIT 1) as current_value,
            AVG({column}) as mean_value,
            STDDEV({column}) as std_value,
            MIN({column}) as min_value,
            MAX({column}) as max_value,
            PERCENT_RANK() OVER (ORDER BY {column}) as percentile
        FROM macro_indicator
        WHERE {column} IS NOT NULL
    """

    # Requête simplifiée pour éviter les problèmes de window function
    query = f"""
        SELECT
            AVG({column}) as mean_value,
            STDDEV({column}) as std_value,
            MIN({column}) as min_value,
            MAX({column}) as max_value
        FROM macro_indicator
        WHERE {column} IS NOT NULL
    """

    result = db.execute(text(query))
    row = result.fetchone()

    if row:
        # Récupérer la valeur actuelle séparément
        current_query = f"""
            SELECT {column} as current_value, date
            FROM macro_indicator
            WHERE {column} IS NOT NULL
            ORDER BY date DESC
            LIMIT 1
        """
        current_result = db.execute(text(current_query))
        current_row = current_result.fetchone()

        current = current_row.current_value if current_row else None

        # Calculer le percentile
        percentile = None
        if current is not None and row.min_value is not None and row.max_value is not None:
            range_val = row.max_value - row.min_value
            if range_val > 0:
                percentile = ((current - row.min_value) / range_val) * 100

        return {
            "indicator": indicator,
            "current": current,
            "mean": row.mean_value,
            "std": row.std_value,
            "min": row.min_value,
            "max": row.max_value,
            "percentile": percentile,
        }
    return None
