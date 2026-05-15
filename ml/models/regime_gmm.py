"""
Modèle de détection de régime basé sur Gaussian Mixture Model.

Alternative probabiliste à K-Means.
"""

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from typing import Optional

from ml.config import N_REGIMES, REGIME_NAMES


class RegimeGMM:
    """
    Détection de régime de marché avec Gaussian Mixture Model.

    Avantages sur K-Means :
    - Fournit des probabilités par régime
    - Gère mieux les clusters de formes différentes

    Attributes:
        n_regimes: Nombre de composantes (régimes)
        model: Modèle GaussianMixture sklearn
        scaler: StandardScaler pour normalisation
    """

    def __init__(
        self,
        n_regimes: int = N_REGIMES,
        covariance_type: str = "full",
        random_state: int = 42,
    ):
        """
        Initialise le modèle GMM.

        Args:
            n_regimes: Nombre de composantes
            covariance_type: Type de covariance ('full', 'tied', 'diag', 'spherical')
            random_state: Seed pour reproductibilité
        """
        self.n_regimes = n_regimes
        self.covariance_type = covariance_type
        self.random_state = random_state
        self.model = GaussianMixture(
            n_components=n_regimes,
            covariance_type=covariance_type,
            random_state=random_state,
            n_init=5,
            max_iter=200,
        )
        self.scaler = StandardScaler()
        self._is_fitted = False
        self._regime_order: Optional[np.ndarray] = None

    def fit(self, X: pd.DataFrame) -> "RegimeGMM":
        """
        Entraîne le modèle GMM.

        Args:
            X: Features de régime

        Returns:
            self
        """
        # Normaliser les features
        X_scaled = self.scaler.fit_transform(X)

        # Entraîner GMM
        self.model.fit(X_scaled)

        # Réordonner les composantes par volatilité
        self._reorder_components(X)

        self._is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Prédit le régime le plus probable pour chaque observation.

        Args:
            X: Features de régime

        Returns:
            Array des régimes (0 à n_regimes-1)
        """
        if not self._is_fitted:
            raise ValueError("Le modèle doit être entraîné avant de prédire")

        X_scaled = self.scaler.transform(X)
        raw_labels = self.model.predict(X_scaled)

        # Réordonner selon l'ordre établi
        if self._regime_order is not None:
            labels = np.array([self._regime_order[l] for l in raw_labels])
        else:
            labels = raw_labels

        return labels

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Retourne les probabilités pour chaque régime.

        Args:
            X: Features de régime

        Returns:
            Array de shape (n_samples, n_regimes) avec probabilités
        """
        if not self._is_fitted:
            raise ValueError("Le modèle doit être entraîné avant de prédire")

        X_scaled = self.scaler.transform(X)
        raw_proba = self.model.predict_proba(X_scaled)

        # Réordonner les colonnes selon l'ordre établi
        if self._regime_order is not None:
            # Créer l'ordre inverse pour réordonner les colonnes
            inverse_order = np.argsort(self._regime_order)
            proba = raw_proba[:, inverse_order]
        else:
            proba = raw_proba

        return proba

    def predict_series(self, X: pd.DataFrame) -> pd.Series:
        """
        Prédit le régime et retourne une Series avec le même index.

        Args:
            X: Features de régime

        Returns:
            Series des régimes
        """
        labels = self.predict(X)
        return pd.Series(labels, index=X.index, name="regime")

    def predict_proba_df(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Retourne les probabilités comme DataFrame.

        Args:
            X: Features de régime

        Returns:
            DataFrame avec colonnes prob_regime_0, prob_regime_1, etc.
        """
        proba = self.predict_proba(X)
        columns = [f"prob_{REGIME_NAMES.get(i, f'regime_{i}')}" for i in range(self.n_regimes)]
        return pd.DataFrame(proba, index=X.index, columns=columns)

    def _reorder_components(self, X: pd.DataFrame) -> None:
        """
        Réordonne les composantes pour cohérence avec les régimes attendus.
        """
        X_scaled = self.scaler.transform(X)
        labels = self.model.predict(X_scaled)

        # Calculer la volatilité moyenne par composante
        component_vols = []
        for i in range(self.n_regimes):
            mask = labels == i
            if mask.sum() > 0 and "spy_volatility_20d" in X.columns:
                vol = X.loc[mask, "spy_volatility_20d"].mean()
            elif mask.sum() > 0 and "vix_zscore" in X.columns:
                vol = X.loc[mask, "vix_zscore"].mean()
            else:
                vol = 0
            component_vols.append((i, vol))

        # Trier par volatilité
        component_vols.sort(key=lambda x: x[1])

        # Mapping
        self._regime_order = np.zeros(self.n_regimes, dtype=int)

        if self.n_regimes == 4:
            order = [3, 0, 1, 2]  # stable, bull, bear, volatile
            for idx, (component_id, _) in enumerate(component_vols):
                self._regime_order[component_id] = order[idx]
        else:
            for idx, (component_id, _) in enumerate(component_vols):
                self._regime_order[component_id] = idx

    def get_regime_stats(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Calcule les statistiques par régime.

        Args:
            X: Features avec régimes prédits

        Returns:
            DataFrame avec stats par régime
        """
        labels = self.predict(X)
        proba = self.predict_proba(X)

        stats = []
        for regime in range(self.n_regimes):
            mask = labels == regime
            count = mask.sum()
            pct = count / len(labels) * 100
            avg_proba = proba[mask, regime].mean() if count > 0 else 0

            regime_data = X[mask]
            regime_stats = {
                "regime": regime,
                "name": REGIME_NAMES.get(regime, f"regime_{regime}"),
                "count": count,
                "pct": round(pct, 1),
                "avg_confidence": round(avg_proba, 3),
            }

            for col in X.columns:
                regime_stats[f"{col}_mean"] = round(regime_data[col].mean(), 4) if count > 0 else 0

            stats.append(regime_stats)

        return pd.DataFrame(stats)

    def get_bic(self) -> float:
        """Retourne le BIC (Bayesian Information Criterion)."""
        if not self._is_fitted:
            raise ValueError("Le modèle doit être entraîné")
        return self.model.bic(self.scaler.transform(
            pd.DataFrame(self.scaler.mean_.reshape(1, -1))
        ))

    def get_aic(self) -> float:
        """Retourne l'AIC (Akaike Information Criterion)."""
        if not self._is_fitted:
            raise ValueError("Le modèle doit être entraîné")
        return self.model.aic(self.scaler.transform(
            pd.DataFrame(self.scaler.mean_.reshape(1, -1))
        ))
