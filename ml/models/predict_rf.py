"""
Modèle de prédiction de rendement basé sur Random Forest.

Choix final pour la prédiction - bon équilibre interprétabilité/performance.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from typing import Optional


class ReturnPredictorRF:
    """
    Prédiction de rendement avec Random Forest.

    Avantages :
    - Robuste à l'overfitting
    - Importance des features native
    - Pas besoin de normalisation (mais on garde pour cohérence)
    - Gère bien les features non-linéaires

    Attributes:
        model: RandomForestClassifier sklearn
        scaler: StandardScaler pour normalisation
    """

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 10,
        min_samples_split: int = 10,
        min_samples_leaf: int = 5,
        max_features: str = "sqrt",
        random_state: int = 42,
        n_jobs: int = -1,
    ):
        """
        Initialise le modèle Random Forest.

        Args:
            n_estimators: Nombre d'arbres
            max_depth: Profondeur max des arbres
            min_samples_split: Samples min pour split
            min_samples_leaf: Samples min par feuille
            max_features: Nombre de features par split ('sqrt', 'log2', int)
            random_state: Seed pour reproductibilité
            n_jobs: Nombre de jobs parallèles (-1 = tous les CPUs)
        """
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.max_features = max_features
        self.random_state = random_state
        self.n_jobs = n_jobs

        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            max_features=max_features,
            random_state=random_state,
            n_jobs=n_jobs,
        )
        self.scaler = StandardScaler()
        self._is_fitted = False
        self._feature_names: Optional[list[str]] = None

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "ReturnPredictorRF":
        """
        Entraîne le modèle.

        Args:
            X: Features de prédiction
            y: Target binaire (1 si return positif)

        Returns:
            self
        """
        self._feature_names = list(X.columns)

        # Normaliser (pas obligatoire pour RF, mais garde cohérence avec autres modèles)
        X_scaled = self.scaler.fit_transform(X)

        # Entraîner
        self.model.fit(X_scaled, y)

        self._is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Prédit la classe (0 ou 1).

        Args:
            X: Features

        Returns:
            Array des prédictions binaires
        """
        if not self._is_fitted:
            raise ValueError("Le modèle doit être entraîné")

        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Retourne les probabilités de chaque classe.

        Args:
            X: Features

        Returns:
            Array de shape (n_samples, 2) avec P(class=0) et P(class=1)
        """
        if not self._is_fitted:
            raise ValueError("Le modèle doit être entraîné")

        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)

    def predict_series(self, X: pd.DataFrame) -> pd.Series:
        """
        Prédit et retourne une Series.

        Args:
            X: Features

        Returns:
            Series des prédictions
        """
        preds = self.predict(X)
        return pd.Series(preds, index=X.index, name="prediction")

    def predict_proba_series(self, X: pd.DataFrame) -> pd.Series:
        """
        Retourne la probabilité de classe 1 comme Series.

        Args:
            X: Features

        Returns:
            Series des probabilités P(return > 0)
        """
        proba = self.predict_proba(X)
        return pd.Series(proba[:, 1], index=X.index, name="prob_positive")

    def get_feature_importance(self) -> pd.DataFrame:
        """
        Retourne l'importance des features.

        Returns:
            DataFrame avec importance par feature
        """
        if not self._is_fitted:
            raise ValueError("Le modèle doit être entraîné")

        importance = self.model.feature_importances_

        return pd.DataFrame({
            "feature": self._feature_names,
            "importance": importance,
        }).sort_values("importance", ascending=False)

    def get_feature_importance_series(self) -> pd.Series:
        """
        Retourne l'importance des features comme Series.

        Returns:
            Series avec importance par feature
        """
        if not self._is_fitted:
            raise ValueError("Le modèle doit être entraîné")

        return pd.Series(
            self.model.feature_importances_,
            index=self._feature_names,
            name="importance"
        ).sort_values(ascending=False)

    def get_oob_score(self) -> Optional[float]:
        """
        Retourne le score out-of-bag (si oob_score=True à l'init).

        Returns:
            Score OOB ou None
        """
        if not self._is_fitted:
            return None
        return getattr(self.model, "oob_score_", None)

    def get_tree_depths(self) -> dict:
        """
        Retourne les statistiques de profondeur des arbres.

        Returns:
            Dict avec min, max, mean depth
        """
        if not self._is_fitted:
            raise ValueError("Le modèle doit être entraîné")

        depths = [tree.get_depth() for tree in self.model.estimators_]
        return {
            "min": min(depths),
            "max": max(depths),
            "mean": round(np.mean(depths), 1),
        }

    def get_params_summary(self) -> dict:
        """
        Retourne un résumé des paramètres du modèle.

        Returns:
            Dict avec les paramètres clés
        """
        return {
            "n_estimators": self.n_estimators,
            "max_depth": self.max_depth,
            "min_samples_split": self.min_samples_split,
            "min_samples_leaf": self.min_samples_leaf,
            "max_features": self.max_features,
            "n_features": len(self._feature_names) if self._feature_names else None,
        }
