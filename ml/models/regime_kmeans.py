"""
Modèle de détection de régime basé sur K-Means.

Baseline simple pour comparaison avec HMM.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import Optional

from ml.config import N_REGIMES, REGIME_NAMES


class RegimeKMeans:
    """
    Détection de régime de marché avec K-Means clustering.

    Attributes:
        n_regimes: Nombre de régimes (clusters)
        model: Modèle KMeans sklearn
        scaler: StandardScaler pour normalisation
    """

    def __init__(self, n_regimes: int = N_REGIMES, random_state: int = 42):
        """
        Initialise le modèle K-Means.

        Args:
            n_regimes: Nombre de clusters/régimes
            random_state: Seed pour reproductibilité
        """
        self.n_regimes = n_regimes
        self.random_state = random_state
        self.model = KMeans(
            n_clusters=n_regimes,
            random_state=random_state,
            n_init=10,
        )
        self.scaler = StandardScaler()
        self._is_fitted = False
        self._regime_order: Optional[np.ndarray] = None

    def fit(self, X: pd.DataFrame) -> "RegimeKMeans":
        """
        Entraîne le modèle K-Means.

        Args:
            X: Features de régime (vix_zscore, credit_spread_zscore, etc.)

        Returns:
            self
        """
        # Normaliser les features
        X_scaled = self.scaler.fit_transform(X)

        # Entraîner K-Means
        self.model.fit(X_scaled)

        # Réordonner les clusters par volatilité moyenne (pour cohérence)
        self._reorder_clusters(X)

        self._is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Prédit le régime pour chaque observation.

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

    def _reorder_clusters(self, X: pd.DataFrame) -> None:
        """
        Réordonne les clusters pour que 0=bull, 1=bear, 2=volatile, 3=stable.

        L'ordre est basé sur la volatilité moyenne de SPY dans chaque cluster.
        """
        X_scaled = self.scaler.transform(X)
        labels = self.model.predict(X_scaled)

        # Calculer la volatilité moyenne par cluster
        cluster_vols = []
        for i in range(self.n_regimes):
            mask = labels == i
            if mask.sum() > 0 and "spy_volatility_20d" in X.columns:
                vol = X.loc[mask, "spy_volatility_20d"].mean()
            elif mask.sum() > 0 and "vix_zscore" in X.columns:
                vol = X.loc[mask, "vix_zscore"].mean()
            else:
                vol = 0
            cluster_vols.append((i, vol))

        # Trier par volatilité
        cluster_vols.sort(key=lambda x: x[1])

        # Mapping : plus basse vol = stable (3), plus haute = volatile (2)
        # Intermédiaires = bull (0), bear (1)
        self._regime_order = np.zeros(self.n_regimes, dtype=int)

        if self.n_regimes == 4:
            # stable, bull, bear, volatile (du moins au plus volatile)
            order = [3, 0, 1, 2]
            for idx, (cluster_id, _) in enumerate(cluster_vols):
                self._regime_order[cluster_id] = order[idx]
        else:
            # Ordre simple
            for idx, (cluster_id, _) in enumerate(cluster_vols):
                self._regime_order[cluster_id] = idx

    def get_regime_stats(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Calcule les statistiques par régime.

        Args:
            X: Features avec régimes prédits

        Returns:
            DataFrame avec stats par régime
        """
        labels = self.predict(X)

        stats = []
        for regime in range(self.n_regimes):
            mask = labels == regime
            count = mask.sum()
            pct = count / len(labels) * 100

            regime_data = X[mask]
            regime_stats = {
                "regime": regime,
                "name": REGIME_NAMES.get(regime, f"regime_{regime}"),
                "count": count,
                "pct": round(pct, 1),
            }

            # Stats par feature
            for col in X.columns:
                regime_stats[f"{col}_mean"] = round(regime_data[col].mean(), 4)

            stats.append(regime_stats)

        return pd.DataFrame(stats)

    def get_inertia(self) -> float:
        """Retourne l'inertie du modèle (somme des distances au centroïde)."""
        if not self._is_fitted:
            raise ValueError("Le modèle doit être entraîné")
        return self.model.inertia_
