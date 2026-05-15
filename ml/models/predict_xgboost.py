"""
Modèle de prédiction de rendement basé sur XGBoost.

Alternative plus puissante au Random Forest, pour comparaison.
"""

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from typing import Optional


class ReturnPredictorXGBoost:
    """
    Prédiction de rendement avec XGBoost.

    Avantages :
    - Gère bien les features hétérogènes
    - Régularisation intégrée (moins d'overfitting)
    - Peut capturer des interactions complexes

    Attributes:
        model: XGBClassifier
        scaler: StandardScaler pour normalisation
    """

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 5,
        learning_rate: float = 0.1,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        random_state: int = 42,
    ):
        """
        Initialise le modèle XGBoost.

        Args:
            n_estimators: Nombre d'arbres
            max_depth: Profondeur max des arbres
            learning_rate: Taux d'apprentissage
            subsample: Fraction des samples par arbre
            colsample_bytree: Fraction des features par arbre
            random_state: Seed pour reproductibilité
        """
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.subsample = subsample
        self.colsample_bytree = colsample_bytree
        self.random_state = random_state

        self.model = xgb.XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            random_state=random_state,
            use_label_encoder=False,
            eval_metric="logloss",
            verbosity=0,
        )
        self.scaler = StandardScaler()
        self._is_fitted = False
        self._feature_names: Optional[list[str]] = None

    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        eval_set: Optional[list[tuple]] = None,
        early_stopping_rounds: Optional[int] = None,
    ) -> "ReturnPredictorXGBoost":
        """
        Entraîne le modèle.

        Args:
            X: Features de prédiction
            y: Target binaire (1 si return positif)
            eval_set: Set de validation pour early stopping
            early_stopping_rounds: Arrêt si pas d'amélioration

        Returns:
            self
        """
        self._feature_names = list(X.columns)

        # Normaliser
        X_scaled = self.scaler.fit_transform(X)

        # Préparer eval_set si fourni
        fit_params = {}
        if eval_set is not None:
            X_val, y_val = eval_set[0]
            X_val_scaled = self.scaler.transform(X_val)
            fit_params["eval_set"] = [(X_val_scaled, y_val)]
            if early_stopping_rounds:
                fit_params["early_stopping_rounds"] = early_stopping_rounds

        # Entraîner
        self.model.fit(X_scaled, y, **fit_params)

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

    def get_feature_importance(self) -> pd.DataFrame:
        """
        Retourne l'importance des features.

        Returns:
            DataFrame avec importance par feature (gain, weight, cover)
        """
        if not self._is_fitted:
            raise ValueError("Le modèle doit être entraîné")

        # Importance par gain (contribution moyenne à la réduction de perte)
        importance_gain = self.model.get_booster().get_score(importance_type="gain")
        # Importance par weight (nombre de fois utilisée)
        importance_weight = self.model.get_booster().get_score(importance_type="weight")
        # Importance par cover (nombre moyen de samples impactés)
        importance_cover = self.model.get_booster().get_score(importance_type="cover")

        # Créer DataFrame avec toutes les features
        data = []
        for feat in self._feature_names:
            # XGBoost nomme les features f0, f1, etc. si pas de noms
            xgb_feat = f"f{self._feature_names.index(feat)}"
            data.append({
                "feature": feat,
                "gain": importance_gain.get(xgb_feat, 0),
                "weight": importance_weight.get(xgb_feat, 0),
                "cover": importance_cover.get(xgb_feat, 0),
            })

        df = pd.DataFrame(data)

        # Normaliser le gain comme importance principale
        if df["gain"].sum() > 0:
            df["importance"] = df["gain"] / df["gain"].sum()
        else:
            df["importance"] = 0

        return df.sort_values("importance", ascending=False)

    def get_feature_importance_sklearn(self) -> pd.Series:
        """
        Retourne l'importance des features (format sklearn).

        Returns:
            Series avec importance par feature
        """
        if not self._is_fitted:
            raise ValueError("Le modèle doit être entraîné")

        importance = self.model.feature_importances_
        return pd.Series(
            importance,
            index=self._feature_names,
            name="importance"
        ).sort_values(ascending=False)

    def get_best_iteration(self) -> Optional[int]:
        """
        Retourne la meilleure itération (si early stopping utilisé).

        Returns:
            Numéro de l'itération ou None
        """
        if not self._is_fitted:
            return None
        return getattr(self.model, "best_iteration", None)
