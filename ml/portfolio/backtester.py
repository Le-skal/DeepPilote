"""
Backtester pour évaluer les stratégies.

Implémente le walk-forward backtesting avec frais de transaction.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional

from ml.config import (
    ETF_TICKERS,
    TRANSACTION_COST,
)
from ml.portfolio.benchmarks import (
    calculate_benchmark_returns,
    calculate_cumulative_returns,
    calculate_drawdown,
)


@dataclass
class BacktestResult:
    """
    Résultats d'un backtest.

    Attributes:
        returns: Series des returns journaliers
        weights_history: DataFrame des poids au fil du temps
        trades_history: Liste des trades effectués
        metrics: Dict des métriques finales
    """
    returns: pd.Series
    weights_history: pd.DataFrame
    trades_history: list = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    benchmark_comparison: Optional[pd.DataFrame] = None


class Backtester:
    """
    Backtester pour stratégies d'allocation.

    Simule l'exécution d'une stratégie avec :
    - Rebalancement mensuel
    - Frais de transaction
    - Walk-forward training (optionnel)

    Attributes:
        transaction_cost: Coût par transaction
        rebalance_freq: Fréquence de rebalancement
        risk_free_rate: Taux sans risque
    """

    def __init__(
        self,
        transaction_cost: float = TRANSACTION_COST,
        rebalance_freq: str = "M",
        risk_free_rate: float = 0.03,
    ):
        """
        Initialise le backtester.

        Args:
            transaction_cost: Coût par trade (défaut 0.1%)
            rebalance_freq: Fréquence ('D', 'W', 'M', 'Q', 'Y')
            risk_free_rate: Taux sans risque annualisé
        """
        self.transaction_cost = transaction_cost
        self.rebalance_freq = rebalance_freq
        self.risk_free_rate = risk_free_rate

    def run(
        self,
        strategy,
        df_prices: pd.DataFrame,
        df_macro: pd.DataFrame,
        start_date: str,
        end_date: str,
        train_years: int = 3,
        retrain_freq: str = "Y",
    ) -> BacktestResult:
        """
        Exécute le backtest walk-forward.

        Args:
            strategy: Instance de DeepPilotStrategy
            df_prices: Prix des ETF
            df_macro: Données macro
            start_date: Date de début du backtest
            end_date: Date de fin
            train_years: Années d'entraînement initial
            retrain_freq: Fréquence de réentraînement ('M', 'Q', 'Y')

        Returns:
            BacktestResult avec tous les résultats
        """
        # Préparer les dates
        start = pd.Timestamp(start_date)
        end = pd.Timestamp(end_date)

        # Date de début du training
        train_start = start - pd.DateOffset(years=train_years)

        # Vérifier les données
        df_prices = df_prices.loc[train_start:end].copy()
        df_macro = df_macro.loc[train_start:end].copy()

        # Calculer les returns
        tickers = [t for t in ETF_TICKERS if t in df_prices.columns]
        df_returns = df_prices[tickers].pct_change().dropna()

        # Dates de rebalancement
        rebalance_dates = self._get_rebalance_dates(df_prices.loc[start:end].index)
        retrain_dates = self._get_retrain_dates(df_prices.loc[start:end].index, retrain_freq)

        # Initialiser
        portfolio_returns = []
        weights_history = []
        trades_history = []

        current_weights = np.ones(len(tickers)) / len(tickers)  # Equal weight initial
        portfolio_value = 1.0

        # Training initial
        print(f"Training initial ({train_start.date()} -> {start.date()})...")
        train_prices = df_prices.loc[train_start:start]
        train_macro = df_macro.loc[train_start:start]
        strategy.fit(train_prices, train_macro, tickers)

        # Boucle sur les jours de trading
        trading_days = df_returns.loc[start:end].index

        for i, date in enumerate(trading_days):
            # Réentraîner si nécessaire
            if date in retrain_dates:
                print(f"Réentraînement à {date.date()}...")
                train_end = date - pd.Timedelta(days=1)
                train_start_new = train_end - pd.DateOffset(years=train_years)
                strategy.fit(
                    df_prices.loc[train_start_new:train_end],
                    df_macro.loc[train_start_new:train_end],
                    tickers,
                )

            # Rebalancer si c'est une date de rebalancement
            if date in rebalance_dates:
                old_weights = current_weights.copy()

                # Obtenir les nouveaux poids
                result = strategy.rebalance(
                    df_prices.loc[:date],
                    df_macro.loc[:date],
                    date,
                )

                new_weights = result["weights"]

                # Calculer le coût de transaction
                turnover = np.sum(np.abs(new_weights - old_weights)) / 2
                trade_cost = turnover * self.transaction_cost

                # Appliquer le coût
                portfolio_value *= (1 - trade_cost)

                # Mettre à jour les poids
                current_weights = new_weights

                # Logger
                weights_history.append({
                    "date": date,
                    **{t: w for t, w in zip(tickers, new_weights)},
                    "regime": result.get("regime"),
                })

                trades_history.append({
                    "date": date,
                    "turnover": round(turnover, 4),
                    "cost": round(trade_cost, 6),
                    "regime": result.get("regime"),
                })

            # Calculer le return du jour
            daily_returns = df_returns.loc[date, tickers].values
            portfolio_return = np.dot(current_weights, daily_returns)

            # Mettre à jour la valeur
            portfolio_value *= (1 + portfolio_return)

            portfolio_returns.append({
                "date": date,
                "return": portfolio_return,
                "value": portfolio_value,
            })

        # Créer les résultats
        returns_df = pd.DataFrame(portfolio_returns).set_index("date")
        returns_series = returns_df["return"]
        returns_series.name = "DeepPilot"

        weights_df = pd.DataFrame(weights_history)
        if len(weights_df) > 0:
            weights_df = weights_df.set_index("date")

        # Calculer les métriques
        metrics = self._calculate_metrics(returns_series)

        return BacktestResult(
            returns=returns_series,
            weights_history=weights_df,
            trades_history=trades_history,
            metrics=metrics,
        )

    def compare_with_benchmarks(
        self,
        strategy_returns: pd.Series,
        df_returns: pd.DataFrame,
        benchmarks: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        """
        Compare la stratégie avec les benchmarks.

        Args:
            strategy_returns: Returns de la stratégie
            df_returns: Returns des ETF
            benchmarks: Liste des benchmarks à inclure

        Returns:
            DataFrame avec métriques comparatives
        """
        if benchmarks is None:
            benchmarks = ["spy", "6040", "equal_weight"]

        # Calculer les returns des benchmarks
        benchmark_df = calculate_benchmark_returns(df_returns, benchmarks)

        # Aligner les indices
        common_idx = strategy_returns.index.intersection(benchmark_df.index)
        strategy_aligned = strategy_returns.loc[common_idx]
        benchmark_aligned = benchmark_df.loc[common_idx]

        # Combiner
        all_returns = pd.concat([
            strategy_aligned.to_frame("DeepPilot"),
            benchmark_aligned
        ], axis=1)

        # Calculer les métriques pour tous
        metrics = []
        for col in all_returns.columns:
            m = self._calculate_metrics(all_returns[col])
            m["strategy"] = col
            metrics.append(m)

        comparison = pd.DataFrame(metrics).set_index("strategy")

        return comparison

    def _get_rebalance_dates(self, index: pd.DatetimeIndex) -> set:
        """
        Retourne les dates de rebalancement.

        Args:
            index: Index des dates

        Returns:
            Set des dates de rebalancement
        """
        if self.rebalance_freq == "D":
            return set(index)
        elif self.rebalance_freq == "W":
            # Premier jour de chaque semaine
            return set(index.to_series().groupby(pd.Grouper(freq="W")).first().dropna())
        elif self.rebalance_freq == "M":
            # Premier jour de chaque mois
            return set(index.to_series().groupby(pd.Grouper(freq="MS")).first().dropna())
        elif self.rebalance_freq == "Q":
            # Premier jour de chaque trimestre
            return set(index.to_series().groupby(pd.Grouper(freq="QS")).first().dropna())
        elif self.rebalance_freq == "Y":
            # Premier jour de chaque année
            return set(index.to_series().groupby(pd.Grouper(freq="YS")).first().dropna())
        else:
            raise ValueError(f"Fréquence inconnue : {self.rebalance_freq}")

    def _get_retrain_dates(self, index: pd.DatetimeIndex, freq: str) -> set:
        """
        Retourne les dates de réentraînement.

        Args:
            index: Index des dates
            freq: Fréquence de réentraînement

        Returns:
            Set des dates de réentraînement
        """
        if freq == "M":
            return set(index.to_series().groupby(pd.Grouper(freq="MS")).first().dropna())
        elif freq == "Q":
            return set(index.to_series().groupby(pd.Grouper(freq="QS")).first().dropna())
        elif freq == "Y":
            return set(index.to_series().groupby(pd.Grouper(freq="YS")).first().dropna())
        else:
            return set()  # Pas de réentraînement

    def _calculate_metrics(self, returns: pd.Series) -> dict:
        """
        Calcule toutes les métriques de performance.

        Args:
            returns: Series des returns journaliers

        Returns:
            Dict avec métriques
        """
        returns = returns.dropna()

        if len(returns) == 0:
            return {}

        # Période
        n_days = len(returns)
        n_years = n_days / 252

        # Returns
        total_return = (1 + returns).prod() - 1
        cagr = (1 + total_return) ** (1 / n_years) - 1 if n_years > 0 else 0

        # Risque
        volatility = returns.std() * np.sqrt(252)
        downside_returns = returns[returns < 0]
        downside_vol = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0

        # Drawdown
        cumret = calculate_cumulative_returns(returns)
        dd = calculate_drawdown(cumret)
        max_dd = dd.min()

        # Ratios
        daily_rf = self.risk_free_rate / 252
        excess_return = cagr - self.risk_free_rate
        sharpe = excess_return / volatility if volatility > 0 else 0
        sortino = excess_return / downside_vol if downside_vol > 0 else 0
        calmar = cagr / abs(max_dd) if max_dd != 0 else 0

        # Win rate
        win_rate = (returns > 0).mean()

        return {
            "total_return_pct": round(total_return * 100, 2),
            "cagr_pct": round(cagr * 100, 2),
            "volatility_pct": round(volatility * 100, 2),
            "sharpe_ratio": round(sharpe, 3),
            "sortino_ratio": round(sortino, 3),
            "max_drawdown_pct": round(max_dd * 100, 2),
            "calmar_ratio": round(calmar, 3),
            "win_rate": round(win_rate, 4),
            "n_days": n_days,
            "n_years": round(n_years, 2),
        }


def run_full_backtest(
    df_prices: pd.DataFrame,
    df_macro: pd.DataFrame,
    start_date: str = "2013-01-01",
    end_date: str = "2024-12-31",
    train_years: int = 3,
) -> tuple[BacktestResult, pd.DataFrame]:
    """
    Fonction helper pour lancer un backtest complet.

    Args:
        df_prices: Prix des ETF
        df_macro: Données macro
        start_date: Date de début
        end_date: Date de fin
        train_years: Années d'entraînement

    Returns:
        Tuple (résultat backtest, comparaison benchmarks)
    """
    from ml.portfolio.deeppilot_strategy import DeepPilotStrategy

    # Créer la stratégie
    strategy = DeepPilotStrategy()

    # Créer le backtester
    backtester = Backtester()

    # Lancer le backtest
    print(f"Backtest {start_date} -> {end_date}")
    result = backtester.run(
        strategy,
        df_prices,
        df_macro,
        start_date,
        end_date,
        train_years=train_years,
    )

    # Calculer les returns ETF
    tickers = [t for t in ETF_TICKERS if t in df_prices.columns]
    df_returns = df_prices[tickers].pct_change().dropna()

    # Comparer aux benchmarks
    comparison = backtester.compare_with_benchmarks(
        result.returns,
        df_returns,
    )

    result.benchmark_comparison = comparison

    return result, comparison
