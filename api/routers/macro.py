"""
Router pour les endpoints macro.

Endpoints:
- GET /macro : indicateurs macro
- GET /macro/latest : dernières valeurs
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.database import get_db
from api.exceptions import InvalidDateRangeError, NoDataFoundError
from api.models.macro import MacroIndicator, MacroIndicatorList, MacroLatest
from api.repositories import macro_repository

router = APIRouter(prefix="/macro", tags=["Macro"])


@router.get(
    "",
    response_model=MacroIndicatorList,
    summary="Indicateurs macro",
    description="Retourne les indicateurs macro (VIX, taux, spreads, etc.).",
)
def get_macro(
    start_date: Optional[date] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    limit: int = Query(1000, ge=1, le=10000, description="Nombre max de résultats"),
    db: Session = Depends(get_db),
) -> MacroIndicatorList:
    """Récupère les indicateurs macro."""
    # Validation des dates
    if start_date and end_date and start_date > end_date:
        raise InvalidDateRangeError()

    indicators = macro_repository.get_macro_indicators(db, start_date, end_date, limit)

    if not indicators:
        raise NoDataFoundError("Aucun indicateur macro trouvé")

    # Déterminer les dates effectives
    dates = [i["date"] for i in indicators]
    actual_start = min(dates) if dates else start_date
    actual_end = max(dates) if dates else end_date

    return MacroIndicatorList(
        start_date=actual_start,
        end_date=actual_end,
        count=len(indicators),
        indicators=[MacroIndicator(**i) for i in indicators],
    )


@router.get(
    "/latest",
    response_model=MacroLatest,
    summary="Dernières valeurs macro",
    description="Retourne les dernières valeurs connues des indicateurs macro.",
)
def get_latest_macro(db: Session = Depends(get_db)) -> MacroLatest:
    """Récupère les dernières valeurs macro."""
    latest = macro_repository.get_latest_macro(db)

    if not latest:
        raise NoDataFoundError("Aucune donnée macro disponible")

    return MacroLatest(**latest)
