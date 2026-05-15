"""
Configuration et constantes pour les modèles ML.
"""

# ETF du portefeuille
ETF_TICKERS = ["SPY", "EFA", "EEM", "TLT", "HYG", "GLD", "VNQ", "SH"]

# Benchmarks
BENCHMARK_TICKERS = ["URTH", "QQQ"]

# Régimes de marché
REGIME_NAMES = {
    0: "bull",      # Marché haussier
    1: "bear",      # Marché baissier
    2: "volatile",  # Haute volatilité
    3: "stable",    # Marché stable/range
}

N_REGIMES = 4

# Paramètres de validation
TRAIN_YEARS = 5       # Années d'entraînement pour walk-forward
TEST_YEARS = 1        # Années de test pour walk-forward
TRADING_DAYS_YEAR = 252

# Paramètres de portefeuille
MIN_WEIGHT = 0.05     # Poids minimum par ETF (5%)
MAX_WEIGHT = 0.25     # Poids maximum par ETF (25%)
TRANSACTION_COST = 0.001  # Frais de transaction (0.1%)
REBALANCE_FREQ = "M"  # Fréquence de rebalancement (mensuelle)

# Features pour détection de régime
REGIME_FEATURES = [
    "vix_zscore",
    "credit_spread_zscore",
    "yield_curve_10y2y",
    "spy_return_20d",
    "spy_volatility_20d",
]

# Features pour prédiction de rendement
PREDICTION_FEATURES = [
    "return_1d",
    "return_5d",
    "return_20d",
    "price_sma20_ratio",
    "price_sma50_ratio",
    "price_sma200_ratio",
    "rsi_14",
    "macd_signal_ratio",
    "bb_position",
    "regime",  # Output du modèle de régime
]

# Horizons de prédiction
PREDICTION_HORIZON = 20  # Jours (environ 1 mois de trading)

# Métriques cibles
TARGET_SHARPE = 0.8
TARGET_MAX_DRAWDOWN = -0.20  # -20%
TARGET_CAGR = 0.12  # 12%
