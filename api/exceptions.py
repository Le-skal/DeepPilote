"""
Exceptions personnalisées pour l'API.

Définit les erreurs métier avec leurs codes HTTP associés.
"""

from fastapi import HTTPException, status


class ETFNotFoundError(HTTPException):
    """ETF non trouvé dans la base de données."""

    def __init__(self, ticker: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ETF '{ticker}' non trouvé. Tickers valides: SPY, EFA, EEM, TLT, HYG, GLD, VNQ, SH, URTH, QQQ",
        )


class InvalidDateRangeError(HTTPException):
    """Plage de dates invalide."""

    def __init__(self, message: str = "La date de début doit être antérieure à la date de fin"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


class DatabaseConnectionError(HTTPException):
    """Erreur de connexion à la base de données."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Impossible de se connecter à la base de données. Réessayez plus tard.",
        )


class NoDataFoundError(HTTPException):
    """Aucune donnée trouvée pour les critères donnés."""

    def __init__(self, message: str = "Aucune donnée trouvée pour les critères spécifiés"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )


# Liste des tickers valides
VALID_TICKERS = {"SPY", "EFA", "EEM", "TLT", "HYG", "GLD", "VNQ", "SH", "URTH", "QQQ"}


def validate_ticker(ticker: str) -> str:
    """
    Valide qu'un ticker est dans la liste des ETF supportés.

    Args:
        ticker: Symbole de l'ETF à valider

    Returns:
        Ticker en majuscules

    Raises:
        ETFNotFoundError: Si le ticker n'est pas valide
    """
    ticker_upper = ticker.upper()
    if ticker_upper not in VALID_TICKERS:
        raise ETFNotFoundError(ticker)
    return ticker_upper
