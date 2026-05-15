"""
Module de gestion de portefeuille.

Contient les benchmarks, l'optimiseur Markowitz et la stratégie DeepPilot.
"""

from ml.portfolio.benchmarks import (
    create_buy_hold_benchmark,
    create_6040_benchmark,
    create_equal_weight_benchmark,
    calculate_benchmark_returns,
    calculate_benchmark_metrics,
)
from ml.portfolio.optimizer import PortfolioOptimizer
from ml.portfolio.deeppilot_strategy import DeepPilotStrategy
from ml.portfolio.backtester import Backtester, BacktestResult, run_full_backtest

__all__ = [
    "create_buy_hold_benchmark",
    "create_6040_benchmark",
    "create_equal_weight_benchmark",
    "calculate_benchmark_returns",
    "calculate_benchmark_metrics",
    "PortfolioOptimizer",
    "DeepPilotStrategy",
    "Backtester",
    "BacktestResult",
    "run_full_backtest",
]
