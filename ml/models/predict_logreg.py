"""
Modèle de prédiction de rendement basé sur Logistic Regression.

Baseline interprétable pour comparaison.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from typing import Optional


class ReturnPredictorLogReg:
    """
    Prédiction de rendement avec Logistic Regression.

    Baseline simple et interprétable.

    Attributes:
        model: LogisticRegression sklearn
        scaler: StandardScaler pour normalisation
    """

    def __init__(
        self,
        C: float = 1.0,
        max_iter: int = 1000,
        random_state: int = 42,
    ):
        """
        Initialise le modèle.

        Args:
            C: Inverse de la force de régularisation
            max_iter: Nombre max d'itérations
            random_state: Seed pour reproductibilité
        """
        self.C = C
        self.max_iter = max_iter
        self.random_state = random_state

        self.model = LogisticRegression(
            C=C,
            max_iter=max_iter,
            random_state=random_state,
            solver="lbfgs",
        )
        self.scaler = StandardScaler()
        self._is_fitted = False
        self._feature_names: Optional[list[str]] = None

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "ReturnPredictorLogReg":
        """
        Entraîne le modèle.

        Args:
            X: Features de prédiction
            y: Target binaire (1 si return positif)

        Returns:
            self
        """
        self._feature_names = list(X.columns)

        # Normaliser
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

    def get_coefficients(self) -> pd.Series:
        """
        Retourne les coefficients du modèle.

        Returns:
            Series avec coefficient par feature
        """
        if not self._is_fitted:
            raise ValueError("Le modèle doit être entraîné")

        coefs = self.model.coef_[0]
        return pd.Series(coefs, index=self._feature_names, name="coefficient").sort_values(
            key=abs, ascending=False
        )

    def get_feature_importance(self) -> pd.DataFrame:
        """
        Retourne l'importance des features (basée sur les coefficients).

        Returns:
            DataFrame avec importance par feature
        """
        coefs = self.get_coefficients()
        importance = np.abs(coefs) / np.abs(coefs).sum()

        return pd.DataFrame({
            "feature": coefs.index,
            "coefficient": coefs.values,
            "importance": importance.values,
        }).sort_values("importance", ascending=False)
