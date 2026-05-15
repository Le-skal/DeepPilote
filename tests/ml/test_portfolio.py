"""
Tests pour les modules de portefeuille.

Teste benchmarks, optimizer et backtester.
"""

import numpy as np
import pandas as pd
import pytest

from ml.portfolio.benchmarks import (
    create_buy_hold_benchmark,
    create_6040_benchmark,
    create_equal_weight_benchmark,
    calculate_benchmark_returns,
    calculate_benchmark_metrics,
    calculate_cumulative_returns,
    calculate_drawdown,
)
from ml.portfolio.optimizer import PortfolioOptimizer
from ml.config import ETF_TICKERS, MIN_WEIGHT, MAX_WEIGHT


@pytest.fixture
def sample_returns():
    """Génère des returns synthétiques pour les ETF."""
    np.random.seed(42)
    n_samples = 500
    dates = pd.date_range("2020-01-01", periods=n_samples, freq="D")

    # Simuler des returns avec différentes caractéristiques
    returns = pd.DataFrame({
        "SPY": np.random.normal(0.0005, 0.015, n_samples),     # Equity
        "TLT": np.random.normal(0.0002, 0.010, n_samples),     # Bonds
        "EFA": np.random.normal(0.0004, 0.016, n_samples),     # Intl equity
        "EEM": np.random.normal(0.0003, 0.020, n_samples),     # EM
        "GLD": np.random.normal(0.0002, 0.012, n_samples),     # Gold
        "HYG": np.random.normal(0.0003, 0.008, n_samples),     # HY bonds
        "VNQ": np.random.normal(0.0004, 0.018, n_samples),     # REITs
        "SH": np.random.normal(-0.0005, 0.015, n_samples),     # Short
        "QQQ": np.random.normal(0.0006, 0.018, n_samples),     # Tech
    }, index=dates)

    return returns


class TestBenchmarks:
    """Tests pour les benchmarks."""

    def test_create_buy_hold_benchmark(self, sample_returns):
        """Test du benchmark buy & hold."""
        benchmark = create_buy_hold_benchmark(sample_returns, "SPY")

        assert isinstance(benchmark, pd.Series)
        assert len(benchmark) == len(sample_returns)

    def test_create_buy_hold_invalid_ticker(self, sample_returns):
        """Test avec ticker invalide."""
        with pytest.raises(ValueError, match="non trouvé"):
            create_buy_hold_benchmark(sample_returns, "INVALID")

    def test_create_6040_benchmark(self, sample_returns):
        """Test du benchmark 60/40."""
        benchmark = create_6040_benchmark(sample_returns)

        assert isinstance(benchmark, pd.Series)
        assert len(benchmark) == len(sample_returns)
        # Le return devrait être entre SPY et TLT
        assert benchmark.mean() < sample_returns["SPY"].mean() * 1.5
        assert benchmark.mean() > sample_returns["TLT"].mean() * 0.5

    def test_create_equal_weight_benchmark(self, sample_returns):
        """Test du benchmark equal weight."""
        benchmark = create_equal_weight_benchmark(sample_returns)

        assert isinstance(benchmark, pd.Series)
        assert len(benchmark) == len(sample_returns)
        assert benchmark.name == "equal_weight"

    def test_calculate_benchmark_returns(self, sample_returns):
        """Test du calcul de tous les benchmarks."""
        benchmarks = calculate_benchmark_returns(sample_returns)

        assert isinstance(benchmarks, pd.DataFrame)
        assert len(benchmarks.columns) > 0

    def test_calculate_cumulative_returns(self, sample_returns):
        """Test des returns cumulés."""
        cumret = calculate_cumulative_returns(sample_returns["SPY"])

        assert cumret.iloc[0] == 1 + sample_returns["SPY"].iloc[0]
        assert cumret.iloc[-1] >= 0  # Ne devrait pas être négatif

    def test_calculate_drawdown(self, sample_returns):
        """Test du calcul de drawdown."""
        cumret = calculate_cumulative_returns(sample_returns["SPY"])
        dd = calculate_drawdown(cumret)

        assert (dd <= 0).all()  # Drawdown toujours négatif ou zéro
        assert dd.min() < 0  # Il devrait y avoir du drawdown

    def test_calculate_benchmark_metrics(self, sample_returns):
        """Test des métriques de benchmark."""
        benchmarks = calculate_benchmark_returns(sample_returns)
        metrics = calculate_benchmark_metrics(benchmarks)

        assert isinstance(metrics, pd.DataFrame)
        assert "sharpe" in metrics.columns
        assert "max_drawdown" in metrics.columns
        assert "cagr" in metrics.columns


class TestPortfolioOptimizer:
    """Tests pour PortfolioOptimizer."""

    def test_init(self):
        """Test de l'initialisation."""
        optimizer = PortfolioOptimizer()

        assert optimizer.risk_free_rate == 0.03
        assert optimizer.min_weight == MIN_WEIGHT
        assert optimizer.max_weight == MAX_WEIGHT

    def test_optimize_sharpe(self, sample_returns):
        """Test de l'optimisation max Sharpe."""
        optimizer = PortfolioOptimizer()

        # Calculer les paramètres
        expected_returns = sample_returns.mean() * 252
        cov_matrix = sample_returns.cov() * 252

        result = optimizer.optimize(
            expected_returns.values,
            cov_matrix.values,
            asset_names=list(sample_returns.columns),
            objective="sharpe",
        )

        assert "weights" in result
        assert "sharpe_ratio" in result
        assert len(result["weights"]) == len(sample_returns.columns)

        # Contraintes respectées
        assert result["weights"].sum() == pytest.approx(1.0, abs=0.001)
        assert all(w >= MIN_WEIGHT - 0.001 for w in result["weights"])
        assert all(w <= MAX_WEIGHT + 0.001 for w in result["weights"])

    def test_optimize_min_variance(self, sample_returns):
        """Test de l'optimisation min variance."""
        optimizer = PortfolioOptimizer()

        expected_returns = sample_returns.mean() * 252
        cov_matrix = sample_returns.cov() * 252

        result = optimizer.optimize(
            expected_returns.values,
            cov_matrix.values,
            asset_names=list(sample_returns.columns),
            objective="min_variance",
        )

        assert "weights" in result
        assert "volatility" in result

    def test_optimize_from_returns(self, sample_returns):
        """Test de l'optimisation depuis DataFrame."""
        optimizer = PortfolioOptimizer()

        result = optimizer.optimize_from_returns(sample_returns)

        assert "weights" in result
        assert result["weights"].sum() == pytest.approx(1.0, abs=0.001)

    def test_get_weights_series(self, sample_returns):
        """Test de get_weights_series."""
        optimizer = PortfolioOptimizer()
        optimizer.optimize_from_returns(sample_returns)

        weights = optimizer.get_weights_series()

        assert isinstance(weights, pd.Series)
        assert weights.sum() == pytest.approx(1.0, abs=0.001)

    def test_get_weights_df(self, sample_returns):
        """Test de get_weights_df."""
        optimizer = PortfolioOptimizer()
        optimizer.optimize_from_returns(sample_returns)

        weights_df = optimizer.get_weights_df()

        assert isinstance(weights_df, pd.DataFrame)
        assert "asset" in weights_df.columns
        assert "weight" in weights_df.columns
        assert "weight_pct" in weights_df.columns

    def test_calculate_turnover(self):
        """Test du calcul de turnover."""
        optimizer = PortfolioOptimizer()

        old_weights = np.array([0.25, 0.25, 0.25, 0.25])
        new_weights = np.array([0.30, 0.20, 0.25, 0.25])

        turnover = optimizer.calculate_turnover(old_weights, new_weights)

        # Turnover = |0.05| + |0.05| = 0.10, divisé par 2 = 0.05
        assert turnover == pytest.approx(0.05, abs=0.001)

    def test_calculate_transaction_cost(self):
        """Test du calcul de coût de transaction."""
        optimizer = PortfolioOptimizer()

        old_weights = np.array([0.25, 0.25, 0.25, 0.25])
        new_weights = np.array([0.30, 0.20, 0.25, 0.25])

        cost = optimizer.calculate_transaction_cost(
            old_weights,
            new_weights,
            portfolio_value=100000,
            cost_per_trade=0.001,
        )

        # Turnover 0.05 * 100000 * 0.001 = 5
        assert cost == pytest.approx(5.0, abs=0.1)

    def test_efficient_frontier(self, sample_returns):
        """Test du calcul de la frontière efficiente."""
        optimizer = PortfolioOptimizer()

        expected_returns = sample_returns.mean() * 252
        cov_matrix = sample_returns.cov() * 252

        frontier = optimizer.compute_efficient_frontier(
            expected_returns.values,
            cov_matrix.values,
            n_points=10,
        )

        assert isinstance(frontier, pd.DataFrame)
        assert "return" in frontier.columns
        assert "volatility" in frontier.columns
        assert "sharpe" in frontier.columns

    def test_not_optimized_error(self):
        """Test de l'erreur si pas d'optimisation."""
        optimizer = PortfolioOptimizer()

        with pytest.raises(ValueError, match="optimisation"):
            optimizer.get_weights_series()


class TestMetricsCalculation:
    """Tests pour les calculs de métriques."""

    def test_sharpe_calculation(self, sample_returns):
        """Test du calcul du Sharpe ratio."""
        metrics = calculate_benchmark_metrics(
            sample_returns[["SPY"]],
            risk_free_rate=0.03,
        )

        # Sharpe devrait être dans une plage raisonnable
        assert -3 < metrics.loc["SPY", "sharpe"] < 3

    def test_max_drawdown_calculation(self, sample_returns):
        """Test du calcul du max drawdown."""
        metrics = calculate_benchmark_metrics(sample_returns[["SPY"]])

        # Max drawdown devrait être négatif
        assert metrics.loc["SPY", "max_drawdown"] < 0

    def test_calmar_calculation(self, sample_returns):
        """Test du calcul du Calmar ratio."""
        metrics = calculate_benchmark_metrics(sample_returns[["SPY"]])

        # Calmar devrait exister
        assert "calmar" in metrics.columns
