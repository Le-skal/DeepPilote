"""
Optimisation de portefeuille avec Markowitz contraint.

Utilise scipy.optimize.minimize (SLSQP) comme spécifié dans CLAUDE.md.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Optional

from ml.config import (
    ETF_TICKERS,
    MIN_WEIGHT,
    MAX_WEIGHT,
    TRANSACTION_COST,
)


class PortfolioOptimizer:
    """
    Optimiseur de portefeuille Markowitz avec contraintes.

    Objectif : maximiser le ratio de Sharpe sous contraintes.

    Contraintes :
    - Poids entre MIN_WEIGHT et MAX_WEIGHT par actif
    - Somme des poids = 1
    - Pas de short (poids >= 0)

    Attributes:
        risk_free_rate: Taux sans risque annualisé
        min_weight: Poids minimum par actif
        max_weight: Poids maximum par actif
    """

    def __init__(
        self,
        risk_free_rate: float = 0.03,
        min_weight: float = MIN_WEIGHT,
        max_weight: float = MAX_WEIGHT,
    ):
        """
        Initialise l'optimiseur.

        Args:
            risk_free_rate: Taux sans risque annualisé (défaut 3%)
            min_weight: Poids minimum par actif (défaut 5%)
            max_weight: Poids maximum par actif (défaut 25%)
        """
        self.risk_free_rate = risk_free_rate
        self.min_weight = min_weight
        self.max_weight = max_weight

        self._last_result = None
        self._asset_names: Optional[list[str]] = None

    def optimize(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        asset_names: Optional[list[str]] = None,
        objective: str = "sharpe",
    ) -> dict:
        """
        Optimise le portefeuille.

        Args:
            expected_returns: Returns attendus annualisés (vecteur)
            cov_matrix: Matrice de covariance annualisée
            asset_names: Noms des actifs (optionnel)
            objective: 'sharpe', 'min_variance', ou 'max_return'

        Returns:
            Dict avec poids optimaux et métriques
        """
        n_assets = len(expected_returns)
        self._asset_names = asset_names or [f"asset_{i}" for i in range(n_assets)]

        # Poids initiaux : equal weight
        w0 = np.ones(n_assets) / n_assets

        # Contraintes
        constraints = [
            # Somme des poids = 1
            {"type": "eq", "fun": lambda w: np.sum(w) - 1},
        ]

        # Bounds : [min_weight, max_weight] pour chaque actif
        bounds = [(self.min_weight, self.max_weight) for _ in range(n_assets)]

        # Fonction objectif selon le type
        if objective == "sharpe":
            # Maximiser Sharpe = minimiser -Sharpe
            def neg_sharpe(w):
                port_return = np.dot(w, expected_returns)
                port_vol = np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))
                if port_vol == 0:
                    return 1e10
                return -(port_return - self.risk_free_rate) / port_vol
            obj_func = neg_sharpe

        elif objective == "min_variance":
            def variance(w):
                return np.dot(w.T, np.dot(cov_matrix, w))
            obj_func = variance

        elif objective == "max_return":
            def neg_return(w):
                return -np.dot(w, expected_returns)
            obj_func = neg_return

        else:
            raise ValueError(f"Objectif inconnu : {objective}")

        # Optimisation
        result = minimize(
            obj_func,
            w0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 1000, "ftol": 1e-9},
        )

        if not result.success:
            print(f"[WARN] Optimisation non convergée : {result.message}")

        # Normaliser les poids (au cas où)
        weights = result.x
        weights = weights / weights.sum()

        # Calculer les métriques du portefeuille optimal
        port_return = np.dot(weights, expected_returns)
        port_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe = (port_return - self.risk_free_rate) / port_vol if port_vol > 0 else 0

        self._last_result = {
            "weights": weights,
            "weights_dict": dict(zip(self._asset_names, weights.round(4))),
            "expected_return": round(port_return, 4),
            "volatility": round(port_vol, 4),
            "sharpe_ratio": round(sharpe, 4),
            "success": result.success,
            "message": result.message,
        }

        return self._last_result

    def optimize_from_returns(
        self,
        df_returns: pd.DataFrame,
        lookback_days: int = 252,
        objective: str = "sharpe",
    ) -> dict:
        """
        Optimise à partir d'un DataFrame de returns.

        Args:
            df_returns: DataFrame des returns journaliers
            lookback_days: Nombre de jours pour estimation
            objective: Type d'optimisation

        Returns:
            Dict avec poids optimaux et métriques
        """
        # Utiliser les derniers lookback_days
        recent_returns = df_returns.tail(lookback_days)

        # Estimer les paramètres
        expected_returns = recent_returns.mean() * 252  # Annualisés
        cov_matrix = recent_returns.cov() * 252  # Annualisée

        return self.optimize(
            expected_returns.values,
            cov_matrix.values,
            asset_names=list(df_returns.columns),
            objective=objective,
        )

    def get_weights_series(self) -> pd.Series:
        """
        Retourne les poids comme Series.

        Returns:
            Series des poids optimaux
        """
        if self._last_result is None:
            raise ValueError("Pas d'optimisation effectuée")

        return pd.Series(
            self._last_result["weights"],
            index=self._asset_names,
            name="weight"
        )

    def get_weights_df(self) -> pd.DataFrame:
        """
        Retourne les poids comme DataFrame avec détails.

        Returns:
            DataFrame avec poids et contraintes
        """
        if self._last_result is None:
            raise ValueError("Pas d'optimisation effectuée")

        weights = self._last_result["weights"]

        return pd.DataFrame({
            "asset": self._asset_names,
            "weight": weights.round(4),
            "weight_pct": (weights * 100).round(2),
            "at_min": weights <= self.min_weight + 0.001,
            "at_max": weights >= self.max_weight - 0.001,
        })

    def compute_efficient_frontier(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        n_points: int = 50,
        asset_names: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        """
        Calcule la frontière efficiente.

        Args:
            expected_returns: Returns attendus annualisés
            cov_matrix: Matrice de covariance annualisée
            n_points: Nombre de points sur la frontière
            asset_names: Noms des actifs

        Returns:
            DataFrame avec return, vol, sharpe pour chaque point
        """
        n_assets = len(expected_returns)
        asset_names = asset_names or [f"asset_{i}" for i in range(n_assets)]

        # Range de returns cibles
        min_ret = expected_returns.min()
        max_ret = expected_returns.max()
        target_returns = np.linspace(min_ret, max_ret, n_points)

        frontier = []

        for target_ret in target_returns:
            # Contraintes : somme = 1 et return = target
            constraints = [
                {"type": "eq", "fun": lambda w: np.sum(w) - 1},
                {"type": "eq", "fun": lambda w, r=target_ret: np.dot(w, expected_returns) - r},
            ]

            bounds = [(self.min_weight, self.max_weight) for _ in range(n_assets)]
            w0 = np.ones(n_assets) / n_assets

            # Minimiser la variance pour ce niveau de return
            def variance(w):
                return np.dot(w.T, np.dot(cov_matrix, w))

            result = minimize(
                variance,
                w0,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
            )

            if result.success:
                weights = result.x
                port_return = np.dot(weights, expected_returns)
                port_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                sharpe = (port_return - self.risk_free_rate) / port_vol if port_vol > 0 else 0

                frontier.append({
                    "return": round(port_return, 4),
                    "volatility": round(port_vol, 4),
                    "sharpe": round(sharpe, 4),
                })

        return pd.DataFrame(frontier)

    def calculate_turnover(
        self,
        old_weights: np.ndarray,
        new_weights: np.ndarray,
    ) -> float:
        """
        Calcule le turnover entre deux allocations.

        Args:
            old_weights: Anciens poids
            new_weights: Nouveaux poids

        Returns:
            Turnover (somme des changements absolus / 2)
        """
        return np.sum(np.abs(new_weights - old_weights)) / 2

    def calculate_transaction_cost(
        self,
        old_weights: np.ndarray,
        new_weights: np.ndarray,
        portfolio_value: float = 1.0,
        cost_per_trade: float = TRANSACTION_COST,
    ) -> float:
        """
        Calcule le coût de transaction pour un rebalancement.

        Args:
            old_weights: Anciens poids
            new_weights: Nouveaux poids
            portfolio_value: Valeur du portefeuille
            cost_per_trade: Coût par transaction (défaut 0.1%)

        Returns:
            Coût total en valeur absolue
        """
        turnover = self.calculate_turnover(old_weights, new_weights)
        return turnover * portfolio_value * cost_per_trade
