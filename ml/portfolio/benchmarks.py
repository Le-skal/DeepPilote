"""
Benchmarks de comparaison pour évaluer la stratégie DeepPilot.

Benchmarks :
- Buy & Hold MSCI World (proxy URTH)
- 60/40 classique (SPY/TLT)
- NASDAQ 100 (QQQ)
- S&P 500 pur (SPY)
- Equal Weight sur les 8 ETF
"""

import numpy as np
import pandas as pd
from typing import Optional

from ml.config import ETF_TICKERS, TRANSACTION_COST


def create_buy_hold_benchmark(
    df_returns: pd.DataFrame,
    ticker: str = "SPY",
) -> pd.Series:
    """
    Crée un benchmark buy & hold sur un seul actif.

    Args:
        df_returns: DataFrame des returns journaliers
        ticker: Ticker de l'actif (SPY, URTH, QQQ)

    Returns:
        Series des returns du benchmark
    """
    if ticker not in df_returns.columns:
        raise ValueError(f"Ticker {ticker} non trouvé dans les returns")

    return df_returns[ticker].copy()


def create_6040_benchmark(
    df_returns: pd.DataFrame,
    equity_ticker: str = "SPY",
    bond_ticker: str = "TLT",
    equity_weight: float = 0.60,
    rebalance_freq: str = "Y",
) -> pd.Series:
    """
    Crée un benchmark 60/40 (actions/obligations).

    Args:
        df_returns: DataFrame des returns journaliers
        equity_ticker: Ticker actions (défaut SPY)
        bond_ticker: Ticker obligations (défaut TLT)
        equity_weight: Poids actions (défaut 60%)
        rebalance_freq: Fréquence de rebalancement ('M', 'Q', 'Y')

    Returns:
        Series des returns du benchmark
    """
    if equity_ticker not in df_returns.columns:
        raise ValueError(f"Ticker {equity_ticker} non trouvé")
    if bond_ticker not in df_returns.columns:
        raise ValueError(f"Ticker {bond_ticker} non trouvé")

    bond_weight = 1 - equity_weight

    # Calculer les returns pondérés avec rebalancement périodique
    equity_ret = df_returns[equity_ticker]
    bond_ret = df_returns[bond_ticker]

    # Sans rebalancement exact, on utilise les poids fixes
    # (approximation acceptable pour benchmark)
    benchmark_ret = equity_weight * equity_ret + bond_weight * bond_ret

    benchmark_ret.name = f"{int(equity_weight*100)}/{int(bond_weight*100)}"

    return benchmark_ret


def create_equal_weight_benchmark(
    df_returns: pd.DataFrame,
    tickers: Optional[list[str]] = None,
    rebalance_freq: str = "M",
) -> pd.Series:
    """
    Crée un benchmark equal weight sur plusieurs actifs.

    Args:
        df_returns: DataFrame des returns journaliers
        tickers: Liste des tickers (défaut: les 8 ETF)
        rebalance_freq: Fréquence de rebalancement

    Returns:
        Series des returns du benchmark
    """
    if tickers is None:
        tickers = [t for t in ETF_TICKERS if t in df_returns.columns]

    n_assets = len(tickers)
    weight = 1.0 / n_assets

    # Returns pondérés égaux (approximation sans drift)
    benchmark_ret = df_returns[tickers].mean(axis=1)
    benchmark_ret.name = "equal_weight"

    return benchmark_ret


def calculate_benchmark_returns(
    df_returns: pd.DataFrame,
    include_benchmarks: Optional[list[str]] = None,
) -> pd.DataFrame:
    """
    Calcule les returns pour tous les benchmarks standards.

    Args:
        df_returns: DataFrame des returns journaliers
        include_benchmarks: Liste des benchmarks à inclure
            Options: 'spy', 'qqq', '6040', 'equal_weight', 'urth'

    Returns:
        DataFrame avec returns de chaque benchmark
    """
    if include_benchmarks is None:
        include_benchmarks = ["spy", "6040", "equal_weight"]

    benchmarks = {}

    # S&P 500 (SPY)
    if "spy" in include_benchmarks and "SPY" in df_returns.columns:
        benchmarks["SPY (Buy & Hold)"] = create_buy_hold_benchmark(df_returns, "SPY")

    # NASDAQ 100 (QQQ)
    if "qqq" in include_benchmarks and "QQQ" in df_returns.columns:
        benchmarks["QQQ (Buy & Hold)"] = create_buy_hold_benchmark(df_returns, "QQQ")

    # MSCI World (URTH)
    if "urth" in include_benchmarks and "URTH" in df_returns.columns:
        benchmarks["URTH (Buy & Hold)"] = create_buy_hold_benchmark(df_returns, "URTH")

    # 60/40
    if "6040" in include_benchmarks:
        if "SPY" in df_returns.columns and "TLT" in df_returns.columns:
            benchmarks["60/40 (SPY/TLT)"] = create_6040_benchmark(df_returns)

    # Equal Weight
    if "equal_weight" in include_benchmarks:
        benchmarks["Equal Weight"] = create_equal_weight_benchmark(df_returns)

    return pd.DataFrame(benchmarks)


def calculate_cumulative_returns(returns: pd.Series) -> pd.Series:
    """
    Calcule les returns cumulés (valeur du portefeuille).

    Args:
        returns: Series des returns journaliers

    Returns:
        Series des returns cumulés (base 1)
    """
    return (1 + returns).cumprod()


def calculate_drawdown(cumulative_returns: pd.Series) -> pd.Series:
    """
    Calcule le drawdown à chaque instant.

    Args:
        cumulative_returns: Returns cumulés (base 1)

    Returns:
        Series des drawdowns (valeurs négatives)
    """
    cummax = cumulative_returns.cummax()
    drawdown = (cumulative_returns - cummax) / cummax
    return drawdown


def calculate_benchmark_metrics(
    df_returns: pd.DataFrame,
    risk_free_rate: float = 0.03,
) -> pd.DataFrame:
    """
    Calcule les métriques pour tous les benchmarks.

    Args:
        df_returns: DataFrame avec returns des benchmarks (colonnes)
        risk_free_rate: Taux sans risque annualisé

    Returns:
        DataFrame avec métriques par benchmark
    """
    daily_rf = risk_free_rate / 252

    metrics = []

    for col in df_returns.columns:
        ret = df_returns[col].dropna()

        # Returns
        total_return = (1 + ret).prod() - 1
        n_years = len(ret) / 252
        cagr = (1 + total_return) ** (1 / n_years) - 1 if n_years > 0 else 0

        # Risque
        volatility = ret.std() * np.sqrt(252)
        downside_ret = ret[ret < 0]
        downside_vol = downside_ret.std() * np.sqrt(252) if len(downside_ret) > 0 else 0

        # Drawdown
        cumret = calculate_cumulative_returns(ret)
        dd = calculate_drawdown(cumret)
        max_dd = dd.min()

        # Ratios
        sharpe = (cagr - risk_free_rate) / volatility if volatility > 0 else 0
        sortino = (cagr - risk_free_rate) / downside_vol if downside_vol > 0 else 0
        calmar = cagr / abs(max_dd) if max_dd != 0 else 0

        metrics.append({
            "benchmark": col,
            "total_return": round(total_return * 100, 2),
            "cagr": round(cagr * 100, 2),
            "volatility": round(volatility * 100, 2),
            "sharpe": round(sharpe, 3),
            "sortino": round(sortino, 3),
            "max_drawdown": round(max_dd * 100, 2),
            "calmar": round(calmar, 3),
        })

    df = pd.DataFrame(metrics)
    df = df.set_index("benchmark")

    return df
