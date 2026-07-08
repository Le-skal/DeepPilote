"""
Service ML pour calculer régime et poids du portefeuille.

Utilise les données en base pour fournir des prédictions en temps réel.
Le modèle HMM est réentraîné automatiquement toutes les 6 heures (TTL cache).
"""

from datetime import datetime

import numpy as np
import pandas as pd
from cachetools import TTLCache

from api.database import get_engine
from ml.config import ETF_TICKERS, REGIME_NAMES
from ml.models.regime_hmm import RegimeHMM
from ml.portfolio.optimizer import PortfolioOptimizer

# Cache avec TTL de 6 heures (21600 secondes)
# Le modèle sera réentraîné automatiquement après expiration
MODEL_CACHE_TTL = 6 * 60 * 60  # 6 heures
_model_cache: TTLCache = TTLCache(maxsize=1, ttl=MODEL_CACHE_TTL)


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
        credit_spread_hy AS credit_spread,
        yield_curve_10y2y,
        t10y,
        t3mo
    FROM macro_indicator
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
    FROM price
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


def _train_hmm() -> tuple[RegimeHMM | None, pd.DataFrame | None, str]:
    """
    Entraîne un nouveau modèle HMM.

    Returns:
        Tuple (modèle, features, date)
    """
    print("[ML] Training HMM model...")

    macro_df = get_macro_data(days=1500)
    returns_df = get_etf_returns(days=1500)

    features = compute_regime_features(macro_df, returns_df)

    if features.empty or len(features) < 100:
        print("[ML] Not enough data to train HMM")
        return None, None, ""

    # Entraîner HMM
    hmm = RegimeHMM(n_regimes=4)
    hmm.fit(features)

    last_date = features.index[-1].strftime("%Y-%m-%d")

    print(f"[ML] HMM trained on {len(features)} samples, last date: {last_date}")

    return hmm, features, last_date


def _get_trained_hmm() -> tuple[RegimeHMM | None, pd.DataFrame | None, str]:
    """
    Retourne un modèle HMM entraîné (avec cache TTL de 6h).

    Le modèle est réentraîné automatiquement quand :
    - Le cache expire (après 6h)
    - Le service redémarre (cold start Render)

    Returns:
        Tuple (modèle, features, date)
    """
    cache_key = "hmm_model"

    if cache_key in _model_cache:
        print("[ML] Using cached HMM model")
        return _model_cache[cache_key]

    # Cache miss → entraîner le modèle
    result = _train_hmm()

    if result[0] is not None:
        _model_cache[cache_key] = result

    return result


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
        REGIME_NAMES.get(i, f"regime_{i}"): round(float(proba[i]), 3) for i in range(4)
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
    weights = {ticker: round(float(w), 4) for ticker, w in result["weights_dict"].items()}

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
    """Vide le cache du modèle HMM (force réentraînement)."""
    _model_cache.clear()
    print("[ML] Cache cleared, model will be retrained on next request")


def get_cache_info() -> dict:
    """Retourne les infos sur le cache."""
    return {
        "cache_size": len(_model_cache),
        "cache_ttl_seconds": MODEL_CACHE_TTL,
        "cache_ttl_hours": MODEL_CACHE_TTL / 3600,
    }


# Explications des régimes pour les débutants
REGIME_EXPLANATIONS = {
    "bull": "Marché haussier : les prix montent. Favoriser les actions (SPY, QQQ).",
    "bear": "Marché baissier : les prix baissent. Privilégier les valeurs refuges (GLD, TLT).",
    "volatile": "Marché instable : grandes variations. Réduire les positions risquées.",
    "stable": "Marché calme : peu de mouvements. Bon moment pour diversifier.",
}


def get_predictions() -> dict:
    """
    Génère des prédictions de signal pour chaque ETF.

    Utilise le régime actuel et les returns récents pour estimer
    la probabilité de rendement positif sur le prochain mois.

    Returns:
        Dict avec predictions, top_picks, regime, regime_explanation, as_of
    """
    from api.models.ml import (
        SIGNAL_CONFIG,
        TICKER_DISPLAY_NAMES,
        SignalType,
        probability_to_signal,
    )

    # Récupérer le régime actuel
    regime_info = get_current_regime()
    regime = regime_info["regime"]
    regime_proba = regime_info["probabilities"]

    # Récupérer les returns récents
    returns_df = get_etf_returns(days=60)

    predictions = []

    for ticker in ETF_TICKERS:
        # Base probability from regime
        if regime == "bull":
            base_prob = 0.60
        elif regime == "bear":
            base_prob = 0.35
        elif regime == "volatile":
            base_prob = 0.45
        else:  # stable
            base_prob = 0.52

        # Ajuster selon les returns récents du ticker
        if ticker in returns_df.columns and len(returns_df) > 20:
            recent_returns = returns_df[ticker].tail(20).sum()
            # Bonus/malus basé sur momentum
            momentum_adj = min(0.15, max(-0.15, recent_returns * 2))
            prob = base_prob + momentum_adj
        else:
            prob = base_prob

        # Ajuster pour les actifs défensifs en bear market
        if regime == "bear" and ticker in ["GLD", "TLT", "SH"]:
            prob += 0.20
        elif regime == "bull" and ticker in ["SH"]:
            prob -= 0.20

        # Clamp entre 0.1 et 0.9
        prob = min(0.9, max(0.1, prob))

        # Convertir en signal
        signal = probability_to_signal(prob)
        signal_info = SIGNAL_CONFIG[signal]

        predictions.append({
            "ticker": ticker,
            "display_name": TICKER_DISPLAY_NAMES.get(ticker, ticker),
            "probability": round(prob, 2),
            "signal": signal,
            "signal_label": signal_info["label"],
            "signal_emoji": signal_info["emoji"],
            "signal_explanation": signal_info["explanation"],
        })

    # Trier par probabilité décroissante
    predictions.sort(key=lambda x: x["probability"], reverse=True)

    # Top 3
    top_picks = [p["ticker"] for p in predictions[:3]]

    return {
        "predictions": predictions,
        "top_picks": top_picks,
        "regime": regime,
        "regime_explanation": REGIME_EXPLANATIONS.get(
            regime, "Régime inconnu"
        ),
        "as_of": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "model_info": {
            "regime_model": "HMM 4 régimes",
            "prediction_model": "Momentum + Régime",
            "retrain_frequency": "6 heures",
        },
    }


def get_model_track_record() -> dict:
    """
    Calcule les métriques de fiabilité historique du modèle.

    Évalue la performance du modèle HMM en comparant ses prédictions
    de régime avec les returns réels du marché.

    Returns:
        Dict avec accuracy, precision par régime, historique récent
    """
    hmm, features, last_date = _get_trained_hmm()

    if hmm is None or features is None or len(features) < 100:
        return {
            "overall_accuracy": None,
            "regime_accuracy": {},
            "recent_predictions": [],
            "sample_size": 0,
            "evaluation_period": None,
            "disclaimer": "Pas assez de données pour évaluer la fiabilité du modèle.",
        }

    # Récupérer les returns SPY pour valider les prédictions
    returns_df = get_etf_returns(days=1500)

    if returns_df.empty or "SPY" not in returns_df.columns:
        return {
            "overall_accuracy": None,
            "regime_accuracy": {},
            "recent_predictions": [],
            "sample_size": 0,
            "evaluation_period": None,
            "disclaimer": "Données de marché non disponibles pour validation.",
        }

    # Aligner features et returns
    common_dates = features.index.intersection(returns_df.index)
    features_aligned = features.loc[common_dates]
    spy_returns = returns_df.loc[common_dates, "SPY"]

    # Prédire les régimes sur tout l'historique
    regimes = hmm.predict(features_aligned)

    # Calculer les returns forward sur 20 jours (1 mois trading)
    forward_returns = spy_returns.rolling(20).sum().shift(-20).dropna()

    # Aligner avec les régimes
    valid_dates = forward_returns.index.intersection(features_aligned.index)
    regimes_valid = regimes[features_aligned.index.isin(valid_dates)]
    forward_valid = forward_returns.loc[valid_dates]

    if len(regimes_valid) < 50:
        return {
            "overall_accuracy": None,
            "regime_accuracy": {},
            "recent_predictions": [],
            "sample_size": len(regimes_valid),
            "evaluation_period": None,
            "disclaimer": "Échantillon trop petit pour évaluation statistique.",
        }

    # Définir ce qui est "correct" pour chaque régime
    # Bull: return > 2%, Bear: return < -2%, Volatile: |return| > 3%, Stable: |return| < 2%
    correct_predictions = []
    regime_stats = {0: {"correct": 0, "total": 0}, 1: {"correct": 0, "total": 0},
                    2: {"correct": 0, "total": 0}, 3: {"correct": 0, "total": 0}}

    for regime, fwd_ret in zip(regimes_valid, forward_valid.values):
        regime_stats[regime]["total"] += 1

        is_correct = False
        if regime == 0:  # Bull
            is_correct = fwd_ret > 0.01  # Return positif > 1%
        elif regime == 1:  # Bear
            is_correct = fwd_ret < -0.01  # Return négatif < -1%
        elif regime == 2:  # Volatile
            is_correct = abs(fwd_ret) > 0.03  # Grande variation > 3%
        elif regime == 3:  # Stable
            is_correct = abs(fwd_ret) < 0.02  # Petite variation < 2%

        if is_correct:
            regime_stats[regime]["correct"] += 1
            correct_predictions.append(1)
        else:
            correct_predictions.append(0)

    # Calculer accuracy globale
    overall_accuracy = sum(correct_predictions) / len(correct_predictions)

    # Accuracy par régime
    regime_accuracy = {}
    for regime_id, stats in regime_stats.items():
        name = REGIME_NAMES.get(regime_id, f"regime_{regime_id}")
        if stats["total"] > 0:
            acc = stats["correct"] / stats["total"]
            regime_accuracy[name] = {
                "accuracy": round(acc * 100, 1),
                "sample_size": stats["total"],
                "correct_predictions": stats["correct"],
            }

    # Dernières 12 prédictions mensuelles (rolling 20 jours)
    recent_predictions = []
    for i in range(-12, 0):
        try:
            idx = i * 20  # Approximation mensuelle
            if abs(idx) < len(regimes_valid):
                date = valid_dates[idx]
                regime_id = regimes_valid[idx]
                actual_return = forward_valid.iloc[idx] * 100
                predicted_regime = REGIME_NAMES.get(regime_id, "unknown")

                recent_predictions.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "predicted_regime": predicted_regime,
                    "actual_return_pct": round(actual_return, 2),
                    "was_correct": correct_predictions[idx] == 1,
                })
        except (IndexError, KeyError):
            continue

    return {
        "overall_accuracy": round(overall_accuracy * 100, 1),
        "regime_accuracy": regime_accuracy,
        "recent_predictions": recent_predictions,
        "sample_size": len(regimes_valid),
        "evaluation_period": {
            "start": valid_dates[0].strftime("%Y-%m-%d"),
            "end": valid_dates[-1].strftime("%Y-%m-%d"),
        },
        "methodology": {
            "bull_correct_if": "Return 20j > +1%",
            "bear_correct_if": "Return 20j < -1%",
            "volatile_correct_if": "|Return 20j| > 3%",
            "stable_correct_if": "|Return 20j| < 2%",
        },
        "disclaimer": "Performance passée ne garantit pas les résultats futurs. "
                     "Ce modèle est éducatif et ne constitue pas un conseil financier.",
    }
