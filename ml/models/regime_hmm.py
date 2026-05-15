"""
Modèle de détection de régime basé sur Hidden Markov Model.

Choix final pour la détection de régime - capture les transitions temporelles.
"""

import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM
from sklearn.preprocessing import StandardScaler
from typing import Optional

from ml.config import N_REGIMES, REGIME_NAMES


class RegimeHMM:
    """
    Détection de régime de marché avec Hidden Markov Model.

    Avantages sur K-Means et GMM :
    - Modélise les transitions entre régimes
    - Capture la dynamique temporelle
    - Plus stable (régimes persistants)

    Attributes:
        n_regimes: Nombre d'états cachés (régimes)
        model: Modèle GaussianHMM de hmmlearn
        scaler: StandardScaler pour normalisation
    """

    def __init__(
        self,
        n_regimes: int = N_REGIMES,
        covariance_type: str = "full",
        n_iter: int = 100,
        random_state: int = 42,
    ):
        """
        Initialise le modèle HMM.

        Args:
            n_regimes: Nombre d'états cachés
            covariance_type: Type de covariance ('full', 'diag', 'spherical', 'tied')
            n_iter: Nombre max d'itérations EM
            random_state: Seed pour reproductibilité
        """
        self.n_regimes = n_regimes
        self.covariance_type = covariance_type
        self.n_iter = n_iter
        self.random_state = random_state

        self.model = GaussianHMM(
            n_components=n_regimes,
            covariance_type=covariance_type,
            n_iter=n_iter,
            random_state=random_state,
        )
        self.scaler = StandardScaler()
        self._is_fitted = False
        self._regime_order: Optional[np.ndarray] = None

    def fit(self, X: pd.DataFrame) -> "RegimeHMM":
        """
        Entraîne le modèle HMM.

        Args:
            X: Features de régime (doit être une série temporelle continue)

        Returns:
            self
        """
        # Normaliser les features
        X_scaled = self.scaler.fit_transform(X)

        # Entraîner HMM
        self.model.fit(X_scaled)

        # Réordonner les états par volatilité
        self._reorder_states(X)

        self._is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Prédit la séquence de régimes la plus probable (Viterbi).

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
        Retourne les probabilités pour chaque régime à chaque instant.

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
            DataFrame avec colonnes prob_bull, prob_bear, etc.
        """
        proba = self.predict_proba(X)
        columns = [f"prob_{REGIME_NAMES.get(i, f'regime_{i}')}" for i in range(self.n_regimes)]
        return pd.DataFrame(proba, index=X.index, columns=columns)

    def _reorder_states(self, X: pd.DataFrame) -> None:
        """
        Réordonne les états pour cohérence avec les régimes attendus.
        """
        X_scaled = self.scaler.transform(X)
        labels = self.model.predict(X_scaled)

        # Calculer la volatilité moyenne par état
        state_vols = []
        for i in range(self.n_regimes):
            mask = labels == i
            if mask.sum() > 0 and "spy_volatility_20d" in X.columns:
                vol = X.loc[mask, "spy_volatility_20d"].mean()
            elif mask.sum() > 0 and "vix_zscore" in X.columns:
                vol = X.loc[mask, "vix_zscore"].mean()
            else:
                vol = 0
            state_vols.append((i, vol))

        # Trier par volatilité
        state_vols.sort(key=lambda x: x[1])

        # Mapping : stable(3) < bull(0) < bear(1) < volatile(2)
        self._regime_order = np.zeros(self.n_regimes, dtype=int)

        if self.n_regimes == 4:
            order = [3, 0, 1, 2]  # stable, bull, bear, volatile
            for idx, (state_id, _) in enumerate(state_vols):
                self._regime_order[state_id] = order[idx]
        else:
            for idx, (state_id, _) in enumerate(state_vols):
                self._regime_order[state_id] = idx

    def get_transition_matrix(self) -> pd.DataFrame:
        """
        Retourne la matrice de transition entre régimes.

        Returns:
            DataFrame avec probabilités de transition P(regime_j | regime_i)
        """
        if not self._is_fitted:
            raise ValueError("Le modèle doit être entraîné")

        raw_transmat = self.model.transmat_

        # Réordonner si nécessaire
        if self._regime_order is not None:
            inverse_order = np.argsort(self._regime_order)
            # Réordonner lignes et colonnes
            transmat = raw_transmat[inverse_order][:, inverse_order]
        else:
            transmat = raw_transmat

        index = [REGIME_NAMES.get(i, f"regime_{i}") for i in range(self.n_regimes)]
        return pd.DataFrame(transmat, index=index, columns=index).round(3)

    def get_stationary_distribution(self) -> pd.Series:
        """
        Retourne la distribution stationnaire des régimes.

        Returns:
            Series avec probabilité d'être dans chaque régime à long terme
        """
        if not self._is_fitted:
            raise ValueError("Le modèle doit être entraîné")

        raw_startprob = self.model.startprob_

        # Réordonner si nécessaire
        if self._regime_order is not None:
            inverse_order = np.argsort(self._regime_order)
            startprob = raw_startprob[inverse_order]
        else:
            startprob = raw_startprob

        index = [REGIME_NAMES.get(i, f"regime_{i}") for i in range(self.n_regimes)]
        return pd.Series(startprob, index=index, name="stationary_prob").round(3)

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

        # Calculer la durée moyenne de chaque régime
        regime_durations = self._compute_regime_durations(labels)

        stats = []
        for regime in range(self.n_regimes):
            mask = labels == regime
            count = mask.sum()
            pct = count / len(labels) * 100
            avg_proba = proba[mask, regime].mean() if count > 0 else 0
            avg_duration = regime_durations.get(regime, 0)

            regime_data = X[mask]
            regime_stats = {
                "regime": regime,
                "name": REGIME_NAMES.get(regime, f"regime_{regime}"),
                "count": count,
                "pct": round(pct, 1),
                "avg_confidence": round(avg_proba, 3),
                "avg_duration_days": round(avg_duration, 1),
            }

            for col in X.columns:
                regime_stats[f"{col}_mean"] = round(regime_data[col].mean(), 4) if count > 0 else 0

            stats.append(regime_stats)

        return pd.DataFrame(stats)

    def _compute_regime_durations(self, labels: np.ndarray) -> dict:
        """
        Calcule la durée moyenne de chaque régime.

        Returns:
            Dict {regime: durée_moyenne_jours}
        """
        durations = {i: [] for i in range(self.n_regimes)}

        current_regime = labels[0]
        current_duration = 1

        for i in range(1, len(labels)):
            if labels[i] == current_regime:
                current_duration += 1
            else:
                durations[current_regime].append(current_duration)
                current_regime = labels[i]
                current_duration = 1

        # Ajouter la dernière séquence
        durations[current_regime].append(current_duration)

        # Calculer les moyennes
        return {
            regime: np.mean(durs) if durs else 0
            for regime, durs in durations.items()
        }

    def get_log_likelihood(self, X: pd.DataFrame) -> float:
        """Retourne la log-vraisemblance du modèle sur les données."""
        if not self._is_fitted:
            raise ValueError("Le modèle doit être entraîné")
        X_scaled = self.scaler.transform(X)
        return self.model.score(X_scaled)
