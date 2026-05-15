"""
Stratégie DeepPilot - Allocation d'actifs ML.

Combine :
1. Détection de régime (HMM)
2. Prédiction de rendement (Random Forest)
3. Optimisation de portefeuille (Markowitz)

Réallocation mensuelle avec frais de transaction.
"""

import numpy as np
import pandas as pd
from typing import Optional

from ml.config import (
    ETF_TICKERS,
    N_REGIMES,
    REGIME_NAMES,
    MIN_WEIGHT,
    MAX_WEIGHT,
    TRANSACTION_COST,
    PREDICTION_HORIZON,
)
from ml.models.regime_hmm import RegimeHMM
from ml.models.predict_rf import ReturnPredictorRF
from ml.portfolio.optimizer import PortfolioOptimizer
from ml.features.feature_engineering import (
    prepare_regime_features,
    prepare_prediction_features,
    create_target,
)


class DeepPilotStrategy:
    """
    Stratégie d'allocation DeepPilot.

    Pipeline :
    1. Détecter le régime de marché actuel (HMM)
    2. Pour chaque ETF, prédire la probabilité de rendement positif
    3. Ajuster les expected returns selon régime + prédictions
    4. Optimiser les poids via Markowitz

    Attributes:
        regime_model: Modèle HMM de détection de régime
        prediction_models: Dict {ticker: modèle RF}
        optimizer: Optimiseur de portefeuille
    """

    def __init__(
        self,
        risk_free_rate: float = 0.03,
        min_weight: float = MIN_WEIGHT,
        max_weight: float = MAX_WEIGHT,
        regime_adjustment: bool = True,
    ):
        """
        Initialise la stratégie.

        Args:
            risk_free_rate: Taux sans risque annualisé
            min_weight: Poids minimum par actif
            max_weight: Poids maximum par actif
            regime_adjustment: Ajuster les poids selon le régime
        """
        self.risk_free_rate = risk_free_rate
        self.min_weight = min_weight
        self.max_weight = max_weight
        self.regime_adjustment = regime_adjustment

        self.regime_model = RegimeHMM()
        self.prediction_models: dict[str, ReturnPredictorRF] = {}
        self.optimizer = PortfolioOptimizer(
            risk_free_rate=risk_free_rate,
            min_weight=min_weight,
            max_weight=max_weight,
        )

        self._is_fitted = False
        self._current_regime: Optional[int] = None
        self._current_weights: Optional[np.ndarray] = None
        self._tickers: list[str] = []

    def fit(
        self,
        df_prices: pd.DataFrame,
        df_macro: pd.DataFrame,
        tickers: Optional[list[str]] = None,
    ) -> "DeepPilotStrategy":
        """
        Entraîne tous les modèles.

        Args:
            df_prices: DataFrame avec prix des ETF (colonnes = tickers)
            df_macro: DataFrame avec données macro (VIX, spread crédit, yield curve)
            tickers: Liste des tickers à utiliser (défaut: ETF_TICKERS)

        Returns:
            self
        """
        self._tickers = tickers or [t for t in ETF_TICKERS if t in df_prices.columns]

        # Préparer les données
        df_returns = df_prices[self._tickers].pct_change().dropna()

        # Combiner pour features de régime
        df_combined = pd.concat([df_prices, df_macro], axis=1).dropna()

        # 1. Entraîner le modèle de régime
        print("Entraînement du modèle de régime (HMM)...")
        X_regime = prepare_regime_features(df_combined)
        self.regime_model.fit(X_regime)

        # Prédire les régimes pour le dataset
        regimes = self.regime_model.predict_series(X_regime)

        # 2. Entraîner un modèle de prédiction par ticker
        print("Entraînement des modèles de prédiction...")
        for ticker in self._tickers:
            print(f"  - {ticker}")

            # Préparer les features de prédiction
            X_pred = prepare_prediction_features(df_combined, ticker, regimes)
            y = create_target(df_combined, ticker, PREDICTION_HORIZON)

            # Aligner les indices
            common_idx = X_pred.index.intersection(y.index)
            X_pred = X_pred.loc[common_idx]
            y = y.loc[common_idx]

            # Enlever les NaN
            valid_mask = ~(X_pred.isna().any(axis=1) | y.isna())
            X_pred = X_pred[valid_mask]
            y = y[valid_mask]

            if len(X_pred) > 100:  # Assez de données
                model = ReturnPredictorRF()
                model.fit(X_pred, y)
                self.prediction_models[ticker] = model

        self._is_fitted = True
        return self

    def predict_regime(self, X_regime: pd.DataFrame) -> int:
        """
        Prédit le régime actuel.

        Args:
            X_regime: Features de régime (dernière observation)

        Returns:
            Régime prédit (0-3)
        """
        if not self._is_fitted:
            raise ValueError("La stratégie doit être entraînée")

        # Prendre la dernière prédiction
        labels = self.regime_model.predict(X_regime)
        self._current_regime = labels[-1]
        return self._current_regime

    def predict_returns(
        self,
        df_combined: pd.DataFrame,
        regimes: pd.Series,
    ) -> pd.Series:
        """
        Prédit les probabilités de rendement positif par ticker.

        Args:
            df_combined: Données combinées (prix + macro)
            regimes: Série des régimes

        Returns:
            Series avec P(return > 0) par ticker
        """
        if not self._is_fitted:
            raise ValueError("La stratégie doit être entraînée")

        predictions = {}

        for ticker in self._tickers:
            if ticker in self.prediction_models:
                X_pred = prepare_prediction_features(df_combined, ticker, regimes)

                # Prendre les dernières données valides
                X_pred = X_pred.dropna().tail(1)

                if len(X_pred) > 0:
                    proba = self.prediction_models[ticker].predict_proba(X_pred)
                    predictions[ticker] = proba[0, 1]  # P(class=1)
                else:
                    predictions[ticker] = 0.5  # Neutre si pas de données
            else:
                predictions[ticker] = 0.5  # Neutre si pas de modèle

        return pd.Series(predictions, name="prob_positive")

    def get_adjusted_returns(
        self,
        base_returns: pd.Series,
        prediction_probas: pd.Series,
        regime: int,
    ) -> pd.Series:
        """
        Ajuste les returns attendus selon prédictions et régime.

        Args:
            base_returns: Returns historiques annualisés
            prediction_probas: P(return > 0) par ticker
            regime: Régime actuel

        Returns:
            Returns ajustés
        """
        # Ajustement basé sur les prédictions
        # Proba > 0.5 → bonus, < 0.5 → malus
        prediction_adjustment = (prediction_probas - 0.5) * 0.10  # +/- 5% max

        # Ajustement basé sur le régime
        regime_multiplier = {
            0: 1.0,   # bull : normal
            1: 0.7,   # bear : réduire exposure
            2: 0.8,   # volatile : légèrement réduire
            3: 1.1,   # stable : légèrement augmenter
        }

        if self.regime_adjustment:
            multiplier = regime_multiplier.get(regime, 1.0)
        else:
            multiplier = 1.0

        adjusted = (base_returns + prediction_adjustment) * multiplier

        return adjusted

    def compute_weights(
        self,
        df_returns: pd.DataFrame,
        prediction_probas: pd.Series,
        regime: int,
        lookback_days: int = 252,
    ) -> dict:
        """
        Calcule les poids optimaux.

        Args:
            df_returns: Returns journaliers récents
            prediction_probas: P(return > 0) par ticker
            regime: Régime actuel
            lookback_days: Jours pour estimation covariance

        Returns:
            Dict avec poids et métriques
        """
        # Returns et covariance historiques
        recent = df_returns[self._tickers].tail(lookback_days)
        base_returns = recent.mean() * 252
        cov_matrix = recent.cov() * 252

        # Ajuster les returns
        adjusted_returns = self.get_adjusted_returns(
            base_returns,
            prediction_probas,
            regime,
        )

        # Optimiser
        result = self.optimizer.optimize(
            adjusted_returns.values,
            cov_matrix.values,
            asset_names=self._tickers,
            objective="sharpe",
        )

        self._current_weights = result["weights"]

        # Ajouter le contexte
        result["regime"] = regime
        result["regime_name"] = REGIME_NAMES.get(regime, f"regime_{regime}")
        result["predictions"] = prediction_probas.to_dict()

        return result

    def rebalance(
        self,
        df_prices: pd.DataFrame,
        df_macro: pd.DataFrame,
        current_date: pd.Timestamp,
        lookback_days: int = 252,
    ) -> dict:
        """
        Effectue un rebalancement complet.

        Args:
            df_prices: Prix des ETF
            df_macro: Données macro
            current_date: Date du rebalancement
            lookback_days: Jours d'historique

        Returns:
            Dict avec nouveaux poids et métriques
        """
        if not self._is_fitted:
            raise ValueError("La stratégie doit être entraînée")

        # Filtrer jusqu'à la date courante (pas de look-ahead)
        df_prices_hist = df_prices.loc[:current_date]
        df_macro_hist = df_macro.loc[:current_date]

        # Combiner
        df_combined = pd.concat([df_prices_hist, df_macro_hist], axis=1).dropna()

        # 1. Détecter le régime
        X_regime = prepare_regime_features(df_combined)
        regime = self.predict_regime(X_regime)

        # 2. Prédire les returns
        regimes = self.regime_model.predict_series(X_regime)
        probas = self.predict_returns(df_combined, regimes)

        # 3. Calculer les returns
        df_returns = df_prices_hist[self._tickers].pct_change().dropna()

        # 4. Optimiser
        result = self.compute_weights(df_returns, probas, regime, lookback_days)
        result["date"] = current_date

        return result

    def get_current_weights(self) -> Optional[pd.Series]:
        """
        Retourne les poids actuels.

        Returns:
            Series des poids ou None
        """
        if self._current_weights is None:
            return None

        return pd.Series(
            self._current_weights,
            index=self._tickers,
            name="weight"
        )

    def get_regime_info(self) -> dict:
        """
        Retourne les informations sur le régime actuel.

        Returns:
            Dict avec régime et statistiques
        """
        if self._current_regime is None:
            return {"regime": None}

        return {
            "regime": self._current_regime,
            "regime_name": REGIME_NAMES.get(self._current_regime, "unknown"),
        }

    def get_model_summary(self) -> dict:
        """
        Retourne un résumé des modèles entraînés.

        Returns:
            Dict avec informations sur les modèles
        """
        return {
            "is_fitted": self._is_fitted,
            "tickers": self._tickers,
            "n_prediction_models": len(self.prediction_models),
            "regime_model": "HMM" if self._is_fitted else None,
            "prediction_model": "Random Forest" if self._is_fitted else None,
            "optimizer": "Markowitz (max Sharpe)",
            "constraints": {
                "min_weight": self.min_weight,
                "max_weight": self.max_weight,
            },
        }
