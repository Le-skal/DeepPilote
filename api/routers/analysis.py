"""
Router pour les endpoints d'analyse.

Endpoints:
- GET /analysis/correlations : matrice de corrélation
- GET /analysis/stats : statistiques par ETF
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.database import get_db
from api.exceptions import InvalidDateRangeError, NoDataFoundError
from api.models.analysis import CorrelationMatrix, ETFStats, StatsResponse
from api.repositories import analysis_repository

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.get(
    "/correlations",
    response_model=CorrelationMatrix,
    summary="Matrice de corrélation",
    description="Calcule la matrice de corrélation des returns entre les ETF.",
)
def get_correlations(
    start_date: Optional[date] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
) -> CorrelationMatrix:
    """Calcule la matrice de corrélation."""
    # Validation des dates
    if start_date and end_date and start_date > end_date:
        raise InvalidDateRangeError()

    result = analysis_repository.get_correlation_matrix(db, start_date, end_date)

    if not result["matrix"]:
        raise NoDataFoundError("Pas assez de données pour calculer les corrélations")

    return CorrelationMatrix(
        start_date=result["start_date"],
        end_date=result["end_date"],
        tickers=result["tickers"],
        matrix=result["matrix"],
        pairs=[
            {
                "ticker_1": p["ticker_1"],
                "ticker_2": p["ticker_2"],
                "correlation": p["correlation"],
            }
            for p in result["pairs"]
        ],
    )


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Statistiques par ETF",
    description="Calcule les statistiques descriptives pour chaque ETF (returns, volatilité, Sharpe, drawdown, etc.).",
)
def get_stats(
    start_date: Optional[date] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
) -> StatsResponse:
    """Calcule les statistiques pour tous les ETF."""
    # Validation des dates
    if start_date and end_date and start_date > end_date:
        raise InvalidDateRangeError()

    stats = analysis_repository.get_all_etf_stats(db, start_date, end_date)

    if not stats:
        raise NoDataFoundError("Pas assez de données pour calculer les statistiques")

    # Déterminer les dates effectives
    actual_start = min(s["start_date"] for s in stats) if stats else start_date
    actual_end = max(s["end_date"] for s in stats) if stats else end_date

    return StatsResponse(
        start_date=actual_start,
        end_date=actual_end,
        stats=[ETFStats(**s) for s in stats],
    )


@router.get(
    "/stats/{ticker}",
    response_model=ETFStats,
    summary="Statistiques d'un ETF",
    description="Calcule les statistiques descriptives pour un ETF spécifique.",
)
def get_etf_stats(
    ticker: str,
    start_date: Optional[date] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
) -> ETFStats:
    """Calcule les statistiques pour un ETF."""
    from api.exceptions import validate_ticker

    ticker = validate_ticker(ticker)

    # Validation des dates
    if start_date and end_date and start_date > end_date:
        raise InvalidDateRangeError()

    stats = analysis_repository.get_etf_stats(db, ticker, start_date, end_date)

    if not stats:
        raise NoDataFoundError(f"Pas assez de données pour {ticker}")

    return ETFStats(**stats)
