"""
Comparaison des modèles de détection de régime.

Compare K-Means, GMM et HMM sur les mêmes données.
"""

import numpy as np
import pandas as pd
from typing import Optional
from sklearn.metrics import (
    adjusted_rand_score,
    silhouette_score,
    calinski_harabasz_score,
)

from ml.models.regime_kmeans import RegimeKMeans
from ml.models.regime_gmm import RegimeGMM
from ml.models.regime_hmm import RegimeHMM
from ml.evaluation.regime_labels import create_historical_labels, evaluate_regime_labels
from ml.config import N_REGIMES, REGIME_NAMES


def evaluate_regime_model(
    model,
    X: pd.DataFrame,
    y_true: Optional[pd.Series] = None,
) -> dict:
    """
    Évalue un modèle de régime.

    Args:
        model: Modèle entraîné (KMeans, GMM ou HMM)
        X: Features de régime
        y_true: Labels historiques (optionnel)

    Returns:
        Dict avec métriques
    """
    # Prédictions
    labels = model.predict(X)

    # Métriques de clustering intrinsèques
    from sklearn.preprocessing import StandardScaler
    X_scaled = StandardScaler().fit_transform(X)

    silhouette = silhouette_score(X_scaled, labels)
    calinski = calinski_harabasz_score(X_scaled, labels)

    # Stabilité des régimes (durée moyenne)
    regime_changes = np.sum(np.diff(labels) != 0)
    stability = 1 - (regime_changes / len(labels))

    # Distribution des régimes
    unique, counts = np.unique(labels, return_counts=True)
    distribution = dict(zip(unique, counts / len(labels)))

    metrics = {
        "silhouette_score": round(silhouette, 4),
        "calinski_harabasz": round(calinski, 2),
        "stability": round(stability, 4),
        "regime_changes": regime_changes,
        "distribution": {REGIME_NAMES.get(k, k): round(v, 3) for k, v in distribution.items()},
    }

    # Métriques vs labels historiques (si fournis)
    if y_true is not None:
        common_idx = X.index.intersection(y_true.index)
        if len(common_idx) > 0:
            y_pred = pd.Series(labels, index=X.index)
            eval_result = evaluate_regime_labels(y_pred.loc[common_idx], y_true.loc[common_idx])
            metrics["vs_historical"] = eval_result

    # Métriques spécifiques au modèle
    model_name = type(model).__name__

    if model_name == "RegimeKMeans":
        metrics["inertia"] = round(model.get_inertia(), 2)
    elif model_name == "RegimeHMM":
        metrics["log_likelihood"] = round(model.get_log_likelihood(X), 2)

    return metrics


def compare_all_regime_models(
    X: pd.DataFrame,
    y_true: Optional[pd.Series] = None,
    n_regimes: int = N_REGIMES,
) -> pd.DataFrame:
    """
    Compare K-Means, GMM et HMM sur les mêmes données.

    Args:
        X: Features de régime
        y_true: Labels historiques (optionnel)
        n_regimes: Nombre de régimes

    Returns:
        DataFrame avec métriques comparatives
    """
    models = {
        "K-Means": RegimeKMeans(n_regimes=n_regimes),
        "GMM": RegimeGMM(n_regimes=n_regimes),
        "HMM": RegimeHMM(n_regimes=n_regimes),
    }

    results = []

    for name, model in models.items():
        print(f"Entraînement {name}...")

        # Entraîner
        model.fit(X)

        # Évaluer
        metrics = evaluate_regime_model(model, X, y_true)

        # Extraire les métriques principales
        row = {
            "model": name,
            "silhouette": metrics["silhouette_score"],
            "calinski_harabasz": metrics["calinski_harabasz"],
            "stability": metrics["stability"],
            "regime_changes": metrics["regime_changes"],
        }

        # Ajouter ARI si labels historiques
        if "vs_historical" in metrics:
            row["adj_rand_index"] = metrics["vs_historical"]["adjusted_rand_index"]
            row["accuracy_vs_hist"] = metrics["vs_historical"]["accuracy"]

        results.append(row)

    df = pd.DataFrame(results)
    df = df.set_index("model")

    return df


def get_best_regime_model(
    X: pd.DataFrame,
    y_true: Optional[pd.Series] = None,
    metric: str = "silhouette",
) -> tuple[str, object]:
    """
    Retourne le meilleur modèle selon la métrique choisie.

    Args:
        X: Features de régime
        y_true: Labels historiques
        metric: 'silhouette', 'stability', ou 'adj_rand_index'

    Returns:
        Tuple (nom_modèle, modèle_entraîné)
    """
    comparison = compare_all_regime_models(X, y_true)

    if metric not in comparison.columns:
        raise ValueError(f"Métrique {metric} non disponible")

    best_model_name = comparison[metric].idxmax()

    # Ré-entraîner le meilleur modèle
    if best_model_name == "K-Means":
        model = RegimeKMeans()
    elif best_model_name == "GMM":
        model = RegimeGMM()
    else:
        model = RegimeHMM()

    model.fit(X)

    return best_model_name, model


def plot_regime_comparison(
    X: pd.DataFrame,
    df_prices: pd.DataFrame,
    spy_col: str = "SPY",
) -> dict:
    """
    Prépare les données pour visualiser les régimes des 3 modèles.

    Args:
        X: Features de régime
        df_prices: DataFrame avec les prix
        spy_col: Colonne SPY pour le graphique

    Returns:
        Dict avec DataFrames pour chaque modèle
    """
    models = {
        "K-Means": RegimeKMeans(),
        "GMM": RegimeGMM(),
        "HMM": RegimeHMM(),
    }

    results = {}

    for name, model in models.items():
        model.fit(X)
        regimes = model.predict_series(X)

        # Créer DataFrame pour le plot
        plot_df = pd.DataFrame({
            "price": df_prices[spy_col].loc[X.index] if spy_col in df_prices.columns else None,
            "regime": regimes,
            "regime_name": regimes.map(REGIME_NAMES),
        })

        results[name] = plot_df

    return results
