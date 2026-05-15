"""
Repository pour les analyses (corrélations, stats).

Calcule les métriques d'analyse à partir des données brutes.
"""

from datetime import date
from typing import Optional

import numpy as np
from sqlalchemy import text
from sqlalchemy.orm import Session


# Liste des ETF du portefeuille (sans benchmarks)
PORTFOLIO_TICKERS = ["SPY", "EFA", "EEM", "TLT", "HYG", "GLD", "VNQ", "SH"]


def get_correlation_matrix(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    tickers: Optional[list[str]] = None,
) -> dict:
    """
    Calcule la matrice de corrélation des returns.

    Args:
        db: Session SQLAlchemy
        start_date: Date de début
        end_date: Date de fin
        tickers: Liste des tickers (défaut: 8 ETF du portefeuille)

    Returns:
        Dictionnaire avec tickers, matrix, pairs
    """
    if tickers is None:
        tickers = PORTFOLIO_TICKERS

    # Récupérer les returns pour chaque ticker
    returns_data = {}

    for ticker in tickers:
        query = """
            SELECT date, ret_1d
            FROM feature
            WHERE ticker = :ticker AND ret_1d IS NOT NULL
        """
        params = {"ticker": ticker}

        if start_date:
            query += " AND date >= :start_date"
            params["start_date"] = start_date

        if end_date:
            query += " AND date <= :end_date"
            params["end_date"] = end_date

        query += " ORDER BY date"

        result = db.execute(text(query), params)
        rows = result.fetchall()

        returns_data[ticker] = {row.date: row.ret_1d for row in rows}

    # Aligner les dates
    all_dates = set()
    for ticker_data in returns_data.values():
        all_dates.update(ticker_data.keys())

    common_dates = sorted(all_dates)

    # Filtrer les dates communes à tous les tickers
    for d in list(common_dates):
        for ticker in tickers:
            if d not in returns_data.get(ticker, {}):
                common_dates.remove(d)
                break

    if len(common_dates) < 20:
        return {
            "tickers": tickers,
            "matrix": [],
            "pairs": [],
            "start_date": start_date,
            "end_date": end_date,
        }

    # Construire la matrice de returns
    n = len(tickers)
    returns_matrix = np.zeros((len(common_dates), n))

    for i, ticker in enumerate(tickers):
        for j, d in enumerate(common_dates):
            returns_matrix[j, i] = returns_data[ticker].get(d, 0)

    # Calculer la matrice de corrélation
    corr_matrix = np.corrcoef(returns_matrix.T)

    # Construire les paires
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append({
                "ticker_1": tickers[i],
                "ticker_2": tickers[j],
                "correlation": round(float(corr_matrix[i, j]), 4),
            })

    # Trier par corrélation (plus faible = plus intéressant pour diversification)
    pairs.sort(key=lambda x: x["correlation"])

    return {
        "tickers": tickers,
        "matrix": [[round(float(x), 4) for x in row] for row in corr_matrix],
        "pairs": pairs,
        "start_date": common_dates[0] if common_dates else None,
        "end_date": common_dates[-1] if common_dates else None,
    }


def get_etf_stats(
    db: Session,
    ticker: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Optional[dict]:
    """
    Calcule les statistiques pour un ETF.

    Args:
        db: Session SQLAlchemy
        ticker: Symbole de l'ETF
        start_date: Date de début
        end_date: Date de fin

    Returns:
        Dictionnaire avec les stats ou None
    """
    # Récupérer les prix
    query = """
        SELECT date, close
        FROM price
        WHERE ticker = :ticker AND close IS NOT NULL
    """
    params = {"ticker": ticker.upper()}

    if start_date:
        query += " AND date >= :start_date"
        params["start_date"] = start_date

    if end_date:
        query += " AND date <= :end_date"
        params["end_date"] = end_date

    query += " ORDER BY date"

    result = db.execute(text(query), params)
    rows = result.fetchall()

    if len(rows) < 20:
        return None

    dates = [row.date for row in rows]
    prices = np.array([float(row.close) for row in rows])  # Convertir Decimal en float

    # Calculer les returns
    returns = np.diff(prices) / prices[:-1]

    # Stats de base
    first_price = prices[0]
    last_price = prices[-1]
    total_return = (last_price / first_price - 1) * 100

    # Annualisé (252 jours de trading)
    years = len(returns) / 252
    annualized_return = ((last_price / first_price) ** (1 / years) - 1) * 100 if years > 0 else 0
    annualized_vol = np.std(returns) * np.sqrt(252) * 100

    # Sharpe (avec risk-free = 0 pour simplifier, sera corrigé en prod)
    sharpe = annualized_return / annualized_vol if annualized_vol > 0 else None

    # Max drawdown
    cummax = np.maximum.accumulate(prices)
    drawdowns = (prices - cummax) / cummax
    max_drawdown = np.min(drawdowns) * 100

    # Distribution
    skewness = float(np.mean(((returns - np.mean(returns)) / np.std(returns)) ** 3)) if np.std(returns) > 0 else 0
    kurtosis = float(np.mean(((returns - np.mean(returns)) / np.std(returns)) ** 4) - 3) if np.std(returns) > 0 else 0

    positive_days = np.sum(returns > 0) / len(returns) * 100
    best_day = np.max(returns) * 100
    worst_day = np.min(returns) * 100

    return {
        "ticker": ticker.upper(),
        "start_date": dates[0],
        "end_date": dates[-1],
        "count": len(prices),
        "first_price": round(first_price, 2),
        "last_price": round(last_price, 2),
        "min_price": round(float(np.min(prices)), 2),
        "max_price": round(float(np.max(prices)), 2),
        "total_return": round(total_return, 2),
        "annualized_return": round(annualized_return, 2),
        "annualized_volatility": round(annualized_vol, 2),
        "sharpe_ratio": round(sharpe, 2) if sharpe else None,
        "max_drawdown": round(max_drawdown, 2),
        "skewness": round(skewness, 3),
        "kurtosis": round(kurtosis, 3),
        "positive_days_pct": round(positive_days, 1),
        "best_day": round(best_day, 2),
        "worst_day": round(worst_day, 2),
    }


def get_all_etf_stats(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> list[dict]:
    """
    Calcule les stats pour tous les ETF du portefeuille.

    Args:
        db: Session SQLAlchemy
        start_date: Date de début
        end_date: Date de fin

    Returns:
        Liste de dictionnaires avec les stats par ETF
    """
    stats = []
    for ticker in PORTFOLIO_TICKERS:
        etf_stats = get_etf_stats(db, ticker, start_date, end_date)
        if etf_stats:
            stats.append(etf_stats)

    return stats
