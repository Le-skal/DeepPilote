"""
Service ML pour calculer régime et poids du portefeuille.

Utilise les données en base pour fournir des prédictions en temps réel.
"""

import pandas as pd
import numpy as np
from functools import lru_cache
from datetime import datetime, timedelta

from api.database import get_engine
from ml.config import ETF_TICKERS, REGIME_NAMES, REGIME_FEATURES
from ml.models.regime_hmm import RegimeHMM
from ml.portfolio.optimizer import PortfolioOptimizer


def get_macro_data(days: int = 500) -> pd.DataFrame:
    """
    Charge les données macro depuis la base.

    Args:
        days: Nombre de jours d'historique

    Returns:
        DataFrame avec les indicateurs macro
    """
    engine = get_engine()
    if engine is None:
        return pd.DataFrame()

    query = f"""
    SELECT
        date,
        vix,
        credit_spread,
        yield_curve_10y2y,
        t10y,
        t3mo
    FROM macro_indicators
    WHERE date >= CURRENT_DATE - INTERVAL '{days} days'
    ORDER BY date
    """

    try:
        df = pd.read_sql(query, engine, parse_dates=["date"])
        df = df.set_index("date")
        return df
    except Exception as e:
        print(f"[ERROR] get_macro_data: {e}")
        return pd.DataFrame()


def get_etf_returns(days: int = 500) -> pd.DataFrame:
    """
    Charge les returns des ETF depuis la base.

    Returns:
        DataFrame avec returns journaliers par ETF
    """
    engine = get_engine()
    if engine is None:
        return pd.DataFrame()

    tickers_str = ", ".join([f"'{t}'" for t in ETF_TICKERS])

    query = f"""
    SELECT
        date,
        ticker,
        close
    FROM etf_prices
    WHERE ticker IN ({tickers_str})
    AND date >= CURRENT_DATE - INTERVAL '{days} days'
    ORDER BY date, ticker
    """

    try:
        df = pd.read_sql(query, engine, parse_dates=["date"])
        # Pivot pour avoir une colonne par ticker
        df_pivot = df.pivot(index="date", columns="ticker", values="close")
        # Calculer les returns
        returns = df_pivot.pct_change().dropna()
        return returns
    except Exception as e:
        print(f"[ERROR] get_etf_returns: {e}")
        return pd.DataFrame()


def compute_regime_features(macro_df: pd.DataFrame, returns_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les features pour la détection de régime.

    Args:
        macro_df: Données macro
        returns_df: Returns des ETF

    Returns:
        DataFrame avec les features de régime
    """
    if macro_df.empty or returns_df.empty:
        return pd.DataFrame()

    # Aligner les dates
    common_dates = macro_df.index.intersection(returns_df.index)
    macro_df = macro_df.loc[common_dates]
    returns_df = returns_df.loc[common_dates]

    if len(common_dates) < 50:
        return pd.DataFrame()

    features = pd.DataFrame(index=common_dates)

    # VIX z-score
    if "vix" in macro_df.columns:
        vix = macro_df["vix"]
        features["vix_zscore"] = (vix - vix.rolling(60).mean()) / vix.rolling(60).std()

    # Credit spread z-score
    if "credit_spread" in macro_df.columns:
        cs = macro_df["credit_spread"]
        features["credit_spread_zscore"] = (cs - cs.rolling(60).mean()) / cs.rolling(60).std()

    # Yield curve
    if "yield_curve_10y2y" in macro_df.columns:
        features["yield_curve_10y2y"] = macro_df["yield_curve_10y2y"]

    # SPY return et volatilité sur 20 jours
    if "SPY" in returns_df.columns:
        spy_ret = returns_df["SPY"]
        features["spy_return_20d"] = spy_ret.rolling(20).sum()
        features["spy_volatility_20d"] = spy_ret.rolling(20).std() * np.sqrt(252)

    # Supprimer les NaN
    features = features.dropna()

    return features


@lru_cache(maxsize=1)
def _get_trained_hmm() -> tuple[RegimeHMM | None, pd.DataFrame | None, str]:
    """
    Retourne un modèle HMM entraîné (cached).

    Returns:
        Tuple (modèle, features, date)
    """
    macro_df = get_macro_data(days=1500)
    returns_df = get_etf_returns(days=1500)

    features = compute_regime_features(macro_df, returns_df)

    if features.empty or len(features) < 100:
        return None, None, ""

    # Entraîner HMM
    hmm = RegimeHMM(n_regimes=4)
    hmm.fit(features)

    last_date = features.index[-1].strftime("%Y-%m-%d")

    return hmm, features, last_date


def get_current_regime() -> dict:
    """
    Calcule le régime de marché actuel.

    Returns:
        Dict avec régime, confiance, probabilités
    """
    hmm, features, last_date = _get_trained_hmm()

    if hmm is None or features is None:
        # Fallback si pas de données
        return {
            "regime": "stable",
            "regime_id": 3,
            "confidence": 0.0,
            "as_of_date": datetime.now().strftime("%Y-%m-%d"),
            "probabilities": {
                "bull": 0.25,
                "bear": 0.25,
                "volatile": 0.25,
                "stable": 0.25,
            },
        }

    # Prédire sur les dernières données
    last_features = features.tail(1)
    regime_id = int(hmm.predict(last_features)[0])
    proba = hmm.predict_proba(last_features)[0]

    regime_name = REGIME_NAMES.get(regime_id, "unknown")
    confidence = float(proba[regime_id])

    probabilities = {
        REGIME_NAMES.get(i, f"regime_{i}"): round(float(proba[i]), 3)
        for i in range(4)
    }

    return {
        "regime": regime_name,
        "regime_id": regime_id,
        "confidence": round(confidence, 3),
        "as_of_date": last_date,
        "probabilities": probabilities,
    }


def get_portfolio_weights() -> dict:
    """
    Calcule les poids optimaux du portefeuille.

    Returns:
        Dict avec poids, métriques, régime
    """
    # Récupérer le régime actuel
    regime_info = get_current_regime()
    regime = regime_info["regime"]

    # Récupérer les returns
    returns_df = get_etf_returns(days=400)

    if returns_df.empty or len(returns_df) < 100:
        # Fallback: equal weight
        weights = {ticker: round(1.0 / len(ETF_TICKERS), 4) for ticker in ETF_TICKERS}
        return {
            "weights": weights,
            "expected_return": 0.08,
            "volatility": 0.15,
            "sharpe_ratio": 0.4,
            "regime": regime,
            "as_of_date": datetime.now().strftime("%Y-%m-%d"),
        }

    # Garder seulement les ETF du portefeuille
    available_tickers = [t for t in ETF_TICKERS if t in returns_df.columns]
    returns_df = returns_df[available_tickers]

    # Optimiser le portefeuille
    optimizer = PortfolioOptimizer(
        risk_free_rate=0.04,  # Taux actuel ~4%
        min_weight=0.05,
        max_weight=0.25,
    )

    result = optimizer.optimize_from_returns(
        returns_df,
        lookback_days=252,
        objective="sharpe",
    )

    # Formater les poids
    weights = {
        ticker: round(float(w), 4)
        for ticker, w in result["weights_dict"].items()
    }

    # Compléter les ETF manquants avec 0
    for ticker in ETF_TICKERS:
        if ticker not in weights:
            weights[ticker] = 0.0

    last_date = returns_df.index[-1].strftime("%Y-%m-%d")

    return {
        "weights": weights,
        "expected_return": round(result["expected_return"], 4),
        "volatility": round(result["volatility"], 4),
        "sharpe_ratio": round(result["sharpe_ratio"], 4),
        "regime": regime,
        "as_of_date": last_date,
    }


def clear_cache():
    """Vide le cache du modèle HMM."""
    _get_trained_hmm.cache_clear()
