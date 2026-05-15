"""
Router pour les endpoints ETF.

Endpoints:
- GET /etfs : liste des ETF
- GET /etfs/{ticker} : détails d'un ETF
- GET /etfs/{ticker}/prices : historique des prix
- GET /etfs/{ticker}/features : features calculées
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.database import get_db
from api.exceptions import InvalidDateRangeError, NoDataFoundError, validate_ticker
from api.models.etf import (
    ETFBase,
    ETFFeature,
    ETFFeatureList,
    ETFListResponse,
    ETFPrice,
    ETFPriceList,
)
from api.repositories import etf_repository, features_repository

router = APIRouter(prefix="/etfs", tags=["ETF"])


@router.get(
    "",
    response_model=ETFListResponse,
    summary="Liste des ETF",
    description="Retourne la liste des 10 ETF disponibles avec leurs métadonnées.",
)
def list_etfs() -> ETFListResponse:
    """Liste tous les ETF du portefeuille."""
    etfs = etf_repository.get_all_etfs()
    return ETFListResponse(
        count=len(etfs),
        etfs=[ETFBase(**etf) for etf in etfs],
    )


@router.get(
    "/{ticker}",
    response_model=ETFBase,
    summary="Détails d'un ETF",
    description="Retourne les métadonnées d'un ETF spécifique.",
)
def get_etf(ticker: str) -> ETFBase:
    """Récupère les détails d'un ETF."""
    ticker = validate_ticker(ticker)
    etf = etf_repository.get_etf_by_ticker(ticker)
    return ETFBase(**etf)


@router.get(
    "/{ticker}/prices",
    response_model=ETFPriceList,
    summary="Historique des prix",
    description="Retourne l'historique des prix ajustés pour un ETF.",
)
def get_prices(
    ticker: str,
    start_date: Optional[date] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    limit: int = Query(1000, ge=1, le=10000, description="Nombre max de résultats"),
    db: Session = Depends(get_db),
) -> ETFPriceList:
    """Récupère l'historique des prix d'un ETF."""
    ticker = validate_ticker(ticker)

    # Validation des dates
    if start_date and end_date and start_date > end_date:
        raise InvalidDateRangeError()

    prices = etf_repository.get_prices(db, ticker, start_date, end_date, limit)

    if not prices:
        raise NoDataFoundError(f"Aucun prix trouvé pour {ticker}")

    # Déterminer les dates effectives
    dates = [p["date"] for p in prices]
    actual_start = min(dates) if dates else start_date
    actual_end = max(dates) if dates else end_date

    return ETFPriceList(
        ticker=ticker,
        start_date=actual_start,
        end_date=actual_end,
        count=len(prices),
        prices=[ETFPrice(**p) for p in prices],
    )


@router.get(
    "/{ticker}/features",
    response_model=ETFFeatureList,
    summary="Features calculées",
    description="Retourne les features ML calculées pour un ETF (returns, volatilité, indicateurs techniques).",
)
def get_features(
    ticker: str,
    start_date: Optional[date] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    limit: int = Query(1000, ge=1, le=10000, description="Nombre max de résultats"),
    db: Session = Depends(get_db),
) -> ETFFeatureList:
    """Récupère les features calculées d'un ETF."""
    ticker = validate_ticker(ticker)

    # Validation des dates
    if start_date and end_date and start_date > end_date:
        raise InvalidDateRangeError()

    features = features_repository.get_features(db, ticker, start_date, end_date, limit)

    if not features:
        raise NoDataFoundError(f"Aucune feature trouvée pour {ticker}")

    # Déterminer les dates effectives
    dates = [f["date"] for f in features]
    actual_start = min(dates) if dates else start_date
    actual_end = max(dates) if dates else end_date

    return ETFFeatureList(
        ticker=ticker,
        start_date=actual_start,
        end_date=actual_end,
        count=len(features),
        features=[ETFFeature(**f) for f in features],
    )
