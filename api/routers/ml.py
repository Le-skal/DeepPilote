"""
Router pour les endpoints ML (régime et portfolio).
"""

from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from api.models.ml import PortfolioWeights, PredictionsResponse, RegimeResponse
from api.services.backtest_service import (
    get_backtest_comparison,
    get_yearly_returns,
)
from api.services.ml_service import (
    clear_cache,
    get_cache_info,
    get_current_regime,
    get_portfolio_weights,
    get_predictions,
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


@router.get(
    "/predictions",
    response_model=PredictionsResponse,
    summary="Prédictions et signaux par ETF",
    description="""
    Retourne les prédictions de rendement et signaux de trading pour chaque ETF.

    **Signaux :**
    - 🚀 **STRONG_BUY** : Probabilité >= 70% - Tendance très haussière
    - 📈 **BUY** : Probabilité >= 55% - Tendance favorable
    - ⏸️ **HOLD** : Probabilité 45-55% - Pas de direction claire
    - 📉 **SELL** : Probabilité 30-45% - Tendance défavorable
    - 🔻 **STRONG_SELL** : Probabilité < 30% - Risque de baisse

    Les prédictions sont basées sur :
    - Le régime de marché actuel (HMM)
    - Le momentum récent de chaque ETF
    - Les caractéristiques de chaque classe d'actifs

    **top_picks** : Les 3 ETF avec les meilleures probabilités.
    """,
)
@limiter.limit("30/minute")
def predictions(request: Request) -> PredictionsResponse:
    """Retourne les prédictions et signaux."""
    result = get_predictions()
    return PredictionsResponse(**result)


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


@router.get(
    "/backtest",
    summary="Comparaison aux benchmarks",
    description="""
    Compare la performance de différentes stratégies sur une période donnée.

    Benchmarks comparés :
    - **SPY** : S&P 500 Buy & Hold
    - **QQQ** : NASDAQ 100 Buy & Hold
    - **60/40** : 60% SPY + 40% TLT (rebalancé)
    - **Equal Weight** : Poids égaux sur les 8 ETF

    Retourne les métriques (Sharpe, CAGR, Max Drawdown) et les courbes cumulées.
    """,
)
@limiter.limit("10/minute")
def get_backtest(request: Request, years: int = 5) -> dict:
    """Retourne la comparaison aux benchmarks."""
    return get_backtest_comparison(years)


@router.get(
    "/yearly-returns",
    summary="Returns annuels par benchmark",
    description="Retourne les returns annuels pour chaque benchmark.",
)
@limiter.limit("10/minute")
def get_yearly(request: Request, years: int = 10) -> dict:
    """Retourne les returns annuels."""
    return get_yearly_returns(years)
