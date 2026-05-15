"""
Feature engineering pour les modèles ML.

Prépare les features pour :
- Détection de régime de marché
- Prédiction de rendement
"""

import numpy as np
import pandas as pd
from typing import Optional

from ml.config import (
    PREDICTION_HORIZON,
    TRADING_DAYS_YEAR,
)


def prepare_regime_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prépare les features pour la détection de régime.

    Features créées :
    - vix_zscore : VIX normalisé (z-score rolling 252j)
    - credit_spread_zscore : Spread crédit HY normalisé
    - yield_curve_10y2y : Courbe des taux (déjà dans df)
    - spy_return_20d : Return SPY 20 jours
    - spy_volatility_20d : Volatilité réalisée SPY 20 jours

    Args:
        df: DataFrame avec colonnes VIX, credit_spread_hy, yield_curve_10y2y, SPY

    Returns:
        DataFrame avec les features de régime
    """
    features = pd.DataFrame(index=df.index)

    # VIX z-score (normalisation rolling)
    # Utiliser une fenêtre de 60 jours (plus réactive) avec min_periods=20
    rolling_window = 60
    min_periods = 20

    if "vix" in df.columns:
        vix = df["vix"].copy()
        vix_mean = vix.rolling(rolling_window, min_periods=min_periods).mean()
        vix_std = vix.rolling(rolling_window, min_periods=min_periods).std()
        features["vix_zscore"] = (vix - vix_mean) / vix_std
    elif "VIX" in df.columns:
        vix = df["VIX"].copy()
        vix_mean = vix.rolling(rolling_window, min_periods=min_periods).mean()
        vix_std = vix.rolling(rolling_window, min_periods=min_periods).std()
        features["vix_zscore"] = (vix - vix_mean) / vix_std

    # Credit spread z-score
    credit_col = None
    for col in ["credit_spread_hy", "credit_spread", "BAMLH0A0HYM2"]:
        if col in df.columns:
            credit_col = col
            break

    if credit_col:
        credit = df[credit_col].copy()
        credit_mean = credit.rolling(rolling_window, min_periods=min_periods).mean()
        credit_std = credit.rolling(rolling_window, min_periods=min_periods).std()
        # Éviter division par zéro si std est trop faible
        credit_std = credit_std.replace(0, np.nan)
        features["credit_spread_zscore"] = (credit - credit_mean) / credit_std
        features["credit_spread_zscore"] = features["credit_spread_zscore"].fillna(0)
    else:
        # Si pas de crédit spread, utiliser une colonne de zéros
        features["credit_spread_zscore"] = 0.0

    # Yield curve
    yield_col = None
    for col in ["yield_curve_10y2y", "T10Y2Y"]:
        if col in df.columns:
            yield_col = col
            break

    if yield_col:
        features["yield_curve_10y2y"] = df[yield_col].copy()
    else:
        features["yield_curve_10y2y"] = 0.0

    # SPY returns et volatilité
    spy_col = "SPY" if "SPY" in df.columns else None
    if spy_col:
        spy_price = df[spy_col].copy()
        # Return 20 jours (avec min_periods pour avoir plus de données)
        features["spy_return_20d"] = spy_price.pct_change(20)
        # Volatilité réalisée 20 jours (annualisée)
        daily_returns = spy_price.pct_change()
        features["spy_volatility_20d"] = (
            daily_returns.rolling(20, min_periods=10).std() * np.sqrt(TRADING_DAYS_YEAR)
        )
    else:
        features["spy_return_20d"] = 0.0
        features["spy_volatility_20d"] = 0.0

    # Forward fill puis backward fill pour combler les NaN restants
    # Ceci permet d'avoir des données même en début de période
    for col in features.columns:
        features[col] = features[col].ffill().bfill()

    # Dernier recours : remplacer les NaN restants par 0
    features = features.fillna(0.0)

    # Ne garder que les lignes où on a des données valides (au moins 3 features non-nulles)
    # Au lieu de dropna() strict qui supprime tout
    return features


def prepare_prediction_features(
    df: pd.DataFrame,
    ticker: str,
    regime_series: Optional[pd.Series] = None,
) -> pd.DataFrame:
    """
    Prépare les features pour la prédiction de rendement d'un ETF.

    Features créées :
    - return_1d, return_5d, return_20d : Returns lagged
    - price_sma20_ratio, price_sma50_ratio, price_sma200_ratio : Ratios prix/SMA
    - rsi_14 : RSI 14 jours
    - macd_signal_ratio : Ratio MACD/Signal
    - bb_position : Position dans les bandes de Bollinger
    - regime : Régime de marché (si fourni)

    Args:
        df: DataFrame avec les prix et features
        ticker: Symbole de l'ETF
        regime_series: Série des régimes (optionnel)

    Returns:
        DataFrame avec les features de prédiction
    """
    features = pd.DataFrame(index=df.index)

    # Vérifier que le ticker existe
    if ticker not in df.columns:
        raise ValueError(f"Ticker {ticker} non trouvé dans le DataFrame")

    price = df[ticker].copy()

    # Returns lagged (attention : on utilise les returns passés, pas futurs)
    features["return_1d"] = price.pct_change(1).shift(1)  # Return d'hier
    features["return_5d"] = price.pct_change(5).shift(1)  # Return des 5 derniers jours
    features["return_20d"] = price.pct_change(20).shift(1)

    # SMA ratios
    sma_20 = price.rolling(20).mean()
    sma_50 = price.rolling(50).mean()
    sma_200 = price.rolling(200).mean()

    features["price_sma20_ratio"] = price / sma_20
    features["price_sma50_ratio"] = price / sma_50
    features["price_sma200_ratio"] = price / sma_200

    # RSI 14
    features["rsi_14"] = _compute_rsi(price, 14)

    # MACD
    macd, signal = _compute_macd(price)
    # Ratio pour éviter les divisions par zéro
    features["macd_signal_ratio"] = np.where(
        np.abs(signal) > 0.001,
        macd / signal,
        0.0,
    )

    # Bollinger Bands position
    features["bb_position"] = _compute_bollinger_position(price, 20, 2)

    # Régime (si fourni)
    if regime_series is not None:
        features["regime"] = regime_series
    else:
        features["regime"] = 0  # Régime par défaut

    return features.dropna()


def create_target(
    df: pd.DataFrame,
    ticker: str,
    horizon: int = PREDICTION_HORIZON,
) -> pd.Series:
    """
    Crée la variable cible pour la prédiction.

    Args:
        df: DataFrame avec les prix
        ticker: Symbole de l'ETF
        horizon: Horizon de prédiction en jours

    Returns:
        Série avec 1 si return positif, 0 sinon
    """
    if ticker not in df.columns:
        raise ValueError(f"Ticker {ticker} non trouvé dans le DataFrame")

    price = df[ticker].copy()

    # Return forward (futur)
    forward_return = price.pct_change(horizon).shift(-horizon)

    # Label binaire
    target = (forward_return > 0).astype(int)
    target.name = f"{ticker}_target_{horizon}d"

    return target


def _compute_rsi(price: pd.Series, period: int = 14) -> pd.Series:
    """Calcule le RSI (Relative Strength Index)."""
    delta = price.diff()

    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    return rsi


def _compute_macd(
    price: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> tuple[pd.Series, pd.Series]:
    """Calcule le MACD et sa ligne de signal."""
    ema_fast = price.ewm(span=fast, adjust=False).mean()
    ema_slow = price.ewm(span=slow, adjust=False).mean()

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()

    return macd_line, signal_line


def _compute_bollinger_position(
    price: pd.Series,
    period: int = 20,
    std_dev: int = 2,
) -> pd.Series:
    """
    Calcule la position relative dans les bandes de Bollinger.

    Returns:
        0 si au niveau de la bande basse, 1 si au niveau de la bande haute
    """
    sma = price.rolling(period).mean()
    std = price.rolling(period).std()

    upper_band = sma + std_dev * std
    lower_band = sma - std_dev * std

    # Position normalisée entre 0 et 1
    position = (price - lower_band) / (upper_band - lower_band)

    return position.clip(0, 1)
