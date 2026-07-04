"""
Router pour les endpoints ML (régime et portfolio).
"""

from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from api.models.ml import RegimeResponse, PortfolioWeights
from api.services.ml_service import get_current_regime, get_portfolio_weights

router = APIRouter(prefix="/ml", tags=["ML"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/regime",
    response_model=RegimeResponse,
    summary="Régime de marché actuel",
    description="""
    Retourne le régime de marché détecté par le modèle HMM.

    Le modèle analyse les indicateurs macro (VIX, spread crédit, yield curve)
    et les returns récents pour identifier l'un des 4 régimes :
    - **bull** : marché haussier
    - **bear** : marché baissier
    - **volatile** : haute volatilité
    - **stable** : marché calme
    """,
)
@limiter.limit("30/minute")
def get_regime(request: Request) -> RegimeResponse:
    """Retourne le régime de marché actuel."""
    result = get_current_regime()
    return RegimeResponse(**result)


@router.get(
    "/portfolio",
    response_model=PortfolioWeights,
    summary="Poids optimaux du portefeuille",
    description="""
    Retourne l'allocation optimale calculée par l'optimiseur Markowitz.

    L'optimisation maximise le ratio de Sharpe sous contraintes :
    - Poids minimum : 5% par ETF
    - Poids maximum : 25% par ETF
    - Somme des poids = 100%
    - Pas de vente à découvert

    L'allocation tient compte du régime de marché actuel.
    """,
)
@limiter.limit("30/minute")
def get_portfolio(request: Request) -> PortfolioWeights:
    """Retourne les poids optimaux du portefeuille."""
    result = get_portfolio_weights()
    return PortfolioWeights(**result)
