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
            min_covar=1e-3,  # Régularisation pour éviter les matrices singulières
        )
        self.scaler = StandardScaler()
        self._is_fitted = False
        self._regime_order: Optional[np.ndarray] = None

    def _clean_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoie les features avant le fit/predict.
        
        Supprime les colonnes à variance quasi-nulle et les NaN/Inf
        qui causent des matrices de covariance singulières.
        """
        X = X.replace([np.inf, -np.inf], np.nan).dropna()

        # Supprimer les colonnes à variance quasi-nulle
        variances = X.var()
        low_var_cols = variances[variances < 1e-10].index.tolist()
        if low_var_cols:
            print(f"  ⚠️ HMM: colonnes à variance nulle supprimées: {low_var_cols}")
            X = X.drop(columns=low_var_cols)

        return X

    def fit(self, X: pd.DataFrame) -> "RegimeHMM":
        """
        Entraîne le modèle HMM avec fallback automatique.

        Tente d'abord avec covariance_type='full', et si la matrice
        n'est pas positive-definite, fallback sur 'diag'.

        Args:
            X: Features de régime (doit être une série temporelle continue)

        Returns:
            self
        """
        X = self._clean_features(X)
        self._feature_columns = X.columns.tolist()

        # Normaliser les features
        X_scaled = self.scaler.fit_transform(X)

        # Tenter le fit avec covariance full
        try:
            self.model.fit(X_scaled)
        except ValueError as e:
            if "positive-definite" in str(e):
                print(f"  ⚠️ HMM: covariance 'full' instable, fallback sur 'diag'")
                self.covariance_type = "diag"
                self.model = GaussianHMM(
                    n_components=self.n_regimes,
                    covariance_type="diag",
                    n_iter=self.n_iter,
                    random_state=self.random_state,
                    min_covar=1e-3,
                )
                self.model.fit(X_scaled)
            else:
                raise

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

        X = self._align_features(X)
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

        X = self._align_features(X)
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
        X = self._align_features(X)
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
        X = self._align_features(X)
        proba = self.predict_proba(X)
        columns = [f"prob_{REGIME_NAMES.get(i, f'regime_{i}')}" for i in range(self.n_regimes)]
        return pd.DataFrame(proba, index=X.index, columns=columns)

    def _align_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Aligne les colonnes de X avec celles utilisées au fit.
        
        Gère le cas où _clean_features a supprimé des colonnes au fit.
        """
        if hasattr(self, '_feature_columns'):
            # Ne garder que les colonnes vues au fit
            available = [c for c in self._feature_columns if c in X.columns]
            X = X[available]
        X = X.replace([np.inf, -np.inf], np.nan).dropna()
        return X

    def _reorder_states(self, X: pd.DataFrame) -> None:
        """
        Réordonne les états pour cohérence avec les régimes attendus.

        Phase 4.5 : Utilise volatilité ET rendement pour un ordering économique.

        Logique de classification :
        - volatile (2) : plus haute volatilité
        - stable (3) : plus basse volatilité
        - bull (0) : rendement positif (parmi les 2 restants)
        - bear (1) : rendement négatif (parmi les 2 restants)

        Cette approche garantit que :
        - regime_vol_separation : vol(volatile) > vol(stable) ✓
        - regime_return_separation : return(bull) > return(bear) ✓
        """
        X_scaled = self.scaler.transform(X)
        labels = self.model.predict(X_scaled)

        # Calculer volatilité ET rendement par état
        state_stats = []
        for i in range(self.n_regimes):
            mask = labels == i

            # Volatilité
            if mask.sum() > 0 and "spy_volatility_20d" in X.columns:
                vol = X.loc[mask, "spy_volatility_20d"].mean()
            elif mask.sum() > 0 and "vix_zscore" in X.columns:
                vol = X.loc[mask, "vix_zscore"].mean()
            else:
                vol = 0

            # Rendement (spy_return_20d)
            if mask.sum() > 0 and "spy_return_20d" in X.columns:
                ret = X.loc[mask, "spy_return_20d"].mean()
            else:
                ret = 0

            state_stats.append({
                "state_id": i,
                "vol": vol,
                "ret": ret,
                "count": mask.sum(),
            })

        self._regime_order = np.zeros(self.n_regimes, dtype=int)

        if self.n_regimes == 4:
            # Trier par volatilité pour identifier stable et volatile
            by_vol = sorted(state_stats, key=lambda x: x["vol"])

            # stable = plus basse vol, volatile = plus haute vol
            stable_state = by_vol[0]["state_id"]
            volatile_state = by_vol[-1]["state_id"]

            # Les 2 états du milieu : trier par rendement
            middle_states = [s for s in state_stats
                           if s["state_id"] not in [stable_state, volatile_state]]
            middle_states.sort(key=lambda x: x["ret"], reverse=True)

            # bull = meilleur rendement, bear = pire rendement
            bull_state = middle_states[0]["state_id"]
            bear_state = middle_states[1]["state_id"]

            # Assigner les labels finaux
            self._regime_order[bull_state] = 0      # bull
            self._regime_order[bear_state] = 1      # bear
            self._regime_order[volatile_state] = 2  # volatile
            self._regime_order[stable_state] = 3    # stable

        else:
            # Fallback : trier par volatilité
            by_vol = sorted(state_stats, key=lambda x: x["vol"])
            for idx, s in enumerate(by_vol):
                self._regime_order[s["state_id"]] = idx

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
        X = self._align_features(X)
        X_scaled = self.scaler.transform(X)
        return self.model.score(X_scaled)
