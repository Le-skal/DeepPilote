"""
Stratégie DeepPilot - Allocation d'actifs ML.

Combine :
1. Détection de régime (HMM)
2. Prédiction de rendement (Random Forest)
3. Optimisation de portefeuille (Markowitz)

Réallocation mensuelle avec frais de transaction.
Logging MLflow automatique si MLFLOW_TRACKING_URI est défini.
"""

import os
import time
import numpy as np
import pandas as pd
from typing import Optional
from datetime import datetime

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

# MLflow tracking (optionnel - activé si MLFLOW_TRACKING_URI est défini)
_MLFLOW_ENABLED = bool(os.getenv("MLFLOW_TRACKING_URI"))
if _MLFLOW_ENABLED:
    try:
        import mlflow
        from mlflow.exceptions import RestException
        print(f"[MLflow] Tracking activé: {os.getenv('MLFLOW_TRACKING_URI')}")
    except ImportError:
        _MLFLOW_ENABLED = False
        print("[MLflow] Package non installé, tracking désactivé")


# ─── Retry wrapper pour appels MLflow distants ───────────────────────
_MLFLOW_MAX_RETRIES = int(os.getenv("MLFLOW_MAX_RETRIES", "5"))
_MLFLOW_RETRY_DELAY = int(os.getenv("MLFLOW_RETRY_DELAY", "5"))


def _safe_mlflow_call(func, *args, **kwargs):
    """
    Exécute un appel MLflow avec retry automatique.
    
    Le serveur distant (Render free tier) peut mettre du temps à persister
    les ressources (runs, experiments). Ce wrapper retente l'appel en cas
    de RestException (RESOURCE_DOES_NOT_EXIST, etc.).
    """
    for attempt in range(_MLFLOW_MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except RestException as e:
            if attempt < _MLFLOW_MAX_RETRIES - 1:
                wait = _MLFLOW_RETRY_DELAY * (attempt + 1)
                print(f"  ⏳ MLflow retry {attempt + 1}/{_MLFLOW_MAX_RETRIES} "
                      f"dans {wait}s... ({e.error_code})")
                time.sleep(wait)
            else:
                print(f"  ❌ MLflow: échec après {_MLFLOW_MAX_RETRIES} tentatives")
                raise


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
        """
        self._tickers = tickers or [t for t in ETF_TICKERS if t in df_prices.columns]

        # Préparer les données
        df_returns = df_prices[self._tickers].pct_change().dropna()

        # Combiner pour features de régime
        df_combined = pd.concat([df_prices, df_macro], axis=1).dropna()

        # =============================================================
        # 1. GESTION DU RUN MLFLOW (AVEC RETRY)
        # =============================================================
        if _MLFLOW_ENABLED:
            _safe_mlflow_call(mlflow.set_experiment, "deeppilot-training")
            
            # Gestion dynamique : si un run parent existe (le backtest), on fait du nested
            is_nested = mlflow.active_run() is not None
            _safe_mlflow_call(
                mlflow.start_run,
                run_name=f"training_{datetime.now().strftime('%Y%m%d_%H%M')}", 
                nested=is_nested,
            )
            
            _safe_mlflow_call(mlflow.log_params, {
                "n_tickers": len(self._tickers),
                "tickers": ",".join(self._tickers),
                "risk_free_rate": self.risk_free_rate,
                "min_weight": self.min_weight,
                "max_weight": self.max_weight,
                "training_samples": len(df_combined),
                "training_start": str(df_combined.index.min().date()),
                "training_end": str(df_combined.index.max().date()),
            })

        # =============================================================
        # 2. ENTRAÎNEMENT DES MODÈLES
        # =============================================================
        print("Entraînement du modèle de régime (HMM)...")
        X_regime = prepare_regime_features(df_combined)
        self.regime_model.fit(X_regime)

        # Prédire les régimes pour le dataset
        regimes = self.regime_model.predict_series(X_regime)

        # MLflow: logger les métriques HMM
        if _MLFLOW_ENABLED:
            regime_counts = regimes.value_counts().to_dict()
            _safe_mlflow_call(mlflow.log_metrics, {
                "hmm_n_regimes": N_REGIMES,
                "hmm_samples": len(X_regime),
                **{f"regime_{k}_count": v for k, v in regime_counts.items()},
            })

        print("Entraînement des modèles de prédiction...")
        rf_metrics = {}
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

                # Collecter les métriques RF
                if hasattr(model, 'model') and hasattr(model.model, 'oob_score_'):
                    rf_metrics[f"rf_{ticker}_oob_score"] = model.model.oob_score_

        # =============================================================
        # 3. FERMETURE DU RUN MLFLOW
        # =============================================================
        if _MLFLOW_ENABLED:
            if rf_metrics:
                _safe_mlflow_call(mlflow.log_metrics, rf_metrics)
            _safe_mlflow_call(mlflow.log_metric, "rf_models_trained", len(self.prediction_models))
            mlflow.end_run()  # Ferme proprement la session d'entraînement courante

        self._is_fitted = True
        return self

    def predict_regime(self, X_regime: pd.DataFrame) -> int:
        """
        Prédit le régime actuel.
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
        """
        prediction_adjustment = (prediction_probas - 0.5) * 0.10  # +/- 5% max

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
        """
        recent = df_returns[self._tickers].tail(lookback_days)
        base_returns = recent.mean() * 252
        cov_matrix = recent.cov() * 252

        adjusted_returns = self.get_adjusted_returns(
            base_returns,
            prediction_probas,
            regime,
        )

        result = self.optimizer.optimize(
            adjusted_returns.values,
            cov_matrix.values,
            asset_names=self._tickers,
            objective="sharpe",
        )

        self._current_weights = result["weights"]

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
        """
        if not self._is_fitted:
            raise ValueError("La stratégie doit être entraînée")

        df_prices_hist = df_prices.loc[:current_date]
        df_macro_hist = df_macro.loc[:current_date]

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
