"""
Router pour les endpoints ML (régime et portfolio).
"""

from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from api.models.ml import PortfolioWeights, RegimeResponse
from api.services.ml_service import (
    clear_cache,
    get_cache_info,
    get_current_regime,
    get_portfolio_weights,
)

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

    Le modèle est réentraîné automatiquement toutes les 6 heures.
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


@router.api_route(
    "/status",
    methods=["GET", "HEAD"],
    summary="État du cache ML",
    description="Retourne les informations sur le cache du modèle HMM. Supporte GET et HEAD.",
)
@limiter.limit("30/minute")
def get_ml_status(request: Request) -> dict:
    """Retourne l'état du cache ML (GET et HEAD pour monitoring)."""
    return get_cache_info()


@router.post(
    "/refresh",
    summary="Force le réentraînement",
    description="Vide le cache et force le réentraînement du modèle HMM au prochain appel.",
)
@limiter.limit("2/minute")
def refresh_model(request: Request) -> dict:
    """Force le réentraînement du modèle."""
    clear_cache()
    return {"message": "Cache cleared, model will be retrained on next request"}
