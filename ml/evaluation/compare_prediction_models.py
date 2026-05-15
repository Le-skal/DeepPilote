"""
Comparaison des modèles de prédiction de rendement.

Compare Logistic Regression, XGBoost et Random Forest sur les mêmes données.
"""

import numpy as np
import pandas as pd
from typing import Optional
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    log_loss,
    confusion_matrix,
)

from ml.models.predict_logreg import ReturnPredictorLogReg
from ml.models.predict_xgboost import ReturnPredictorXGBoost
from ml.models.predict_rf import ReturnPredictorRF


def evaluate_prediction_model(
    model,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict:
    """
    Évalue un modèle de prédiction sur train et test.

    Args:
        model: Modèle entraîné (LogReg, XGBoost ou RF)
        X_train: Features d'entraînement
        y_train: Target d'entraînement
        X_test: Features de test
        y_test: Target de test

    Returns:
        Dict avec métriques
    """
    # Prédictions
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    y_proba_train = model.predict_proba(X_train)[:, 1]
    y_proba_test = model.predict_proba(X_test)[:, 1]

    # Métriques sur test
    metrics = {
        # Métriques de classification
        "accuracy_test": round(accuracy_score(y_test, y_pred_test), 4),
        "accuracy_train": round(accuracy_score(y_train, y_pred_train), 4),
        "precision_test": round(precision_score(y_test, y_pred_test, zero_division=0), 4),
        "recall_test": round(recall_score(y_test, y_pred_test, zero_division=0), 4),
        "f1_test": round(f1_score(y_test, y_pred_test, zero_division=0), 4),

        # Métriques probabilistes
        "auc_test": round(roc_auc_score(y_test, y_proba_test), 4),
        "auc_train": round(roc_auc_score(y_train, y_proba_train), 4),
        "log_loss_test": round(log_loss(y_test, y_proba_test), 4),

        # Overfitting check
        "overfit_gap": round(
            accuracy_score(y_train, y_pred_train) - accuracy_score(y_test, y_pred_test),
            4
        ),
    }

    # Directional accuracy (métrique clé pour le trading)
    # On considère qu'on a raison si on prédit positif et le return est positif
    metrics["directional_accuracy"] = metrics["accuracy_test"]

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred_test)
    metrics["confusion_matrix"] = {
        "true_neg": int(cm[0, 0]),
        "false_pos": int(cm[0, 1]),
        "false_neg": int(cm[1, 0]),
        "true_pos": int(cm[1, 1]),
    }

    # Distribution des prédictions
    metrics["pred_positive_rate"] = round((y_pred_test == 1).mean(), 4)
    metrics["actual_positive_rate"] = round((y_test == 1).mean(), 4)

    return metrics


def compare_all_prediction_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> pd.DataFrame:
    """
    Compare LogReg, XGBoost et Random Forest.

    Args:
        X_train: Features d'entraînement
        y_train: Target d'entraînement
        X_test: Features de test
        y_test: Target de test

    Returns:
        DataFrame avec métriques comparatives
    """
    models = {
        "Logistic Regression": ReturnPredictorLogReg(),
        "XGBoost": ReturnPredictorXGBoost(),
        "Random Forest": ReturnPredictorRF(),
    }

    results = []

    for name, model in models.items():
        print(f"Entraînement {name}...")

        # Entraîner
        model.fit(X_train, y_train)

        # Évaluer
        metrics = evaluate_prediction_model(model, X_train, y_train, X_test, y_test)

        # Extraire les métriques principales
        row = {
            "model": name,
            "accuracy": metrics["accuracy_test"],
            "auc": metrics["auc_test"],
            "precision": metrics["precision_test"],
            "recall": metrics["recall_test"],
            "f1": metrics["f1_test"],
            "log_loss": metrics["log_loss_test"],
            "overfit_gap": metrics["overfit_gap"],
        }

        results.append(row)

    df = pd.DataFrame(results)
    df = df.set_index("model")

    return df


def get_best_prediction_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    metric: str = "auc",
) -> tuple[str, object]:
    """
    Retourne le meilleur modèle selon la métrique choisie.

    Args:
        X_train: Features d'entraînement
        y_train: Target d'entraînement
        X_test: Features de test
        y_test: Target de test
        metric: 'accuracy', 'auc', 'f1', ou 'precision'

    Returns:
        Tuple (nom_modèle, modèle_entraîné)
    """
    comparison = compare_all_prediction_models(X_train, y_train, X_test, y_test)

    # Pour log_loss, plus bas = meilleur
    if metric == "log_loss":
        best_model_name = comparison[metric].idxmin()
    else:
        best_model_name = comparison[metric].idxmax()

    # Ré-entraîner le meilleur modèle
    if best_model_name == "Logistic Regression":
        model = ReturnPredictorLogReg()
    elif best_model_name == "XGBoost":
        model = ReturnPredictorXGBoost()
    else:
        model = ReturnPredictorRF()

    model.fit(X_train, y_train)

    return best_model_name, model


def walk_forward_comparison(
    X: pd.DataFrame,
    y: pd.Series,
    train_years: int = 3,
    test_years: int = 1,
) -> pd.DataFrame:
    """
    Compare les modèles avec walk-forward validation.

    Args:
        X: Features complètes
        y: Target complète
        train_years: Années d'entraînement
        test_years: Années de test

    Returns:
        DataFrame avec métriques moyennes par modèle
    """
    from ml.features.time_split import walk_forward_split

    models_metrics = {
        "Logistic Regression": [],
        "XGBoost": [],
        "Random Forest": [],
    }

    for i, (X_train_split, X_test_split) in enumerate(walk_forward_split(X, train_years, test_years)):
        print(f"Fold {i + 1}...")

        # walk_forward_split retourne des DataFrames, pas des indices
        # On aligne y avec les indices des DataFrames
        train_idx = X_train_split.index
        test_idx = X_test_split.index

        X_train = X_train_split
        y_train = y.loc[y.index.intersection(train_idx)]
        X_test = X_test_split
        y_test = y.loc[y.index.intersection(test_idx)]

        # Aligner X et y (au cas où il y aurait des décalages)
        common_train = X_train.index.intersection(y_train.index)
        common_test = X_test.index.intersection(y_test.index)

        X_train, y_train = X_train.loc[common_train], y_train.loc[common_train]
        X_test, y_test = X_test.loc[common_test], y_test.loc[common_test]

        # Skip si pas assez de données
        if len(X_train) < 50 or len(X_test) < 10:
            print(f"  Skip fold {i + 1}: pas assez de données (train={len(X_train)}, test={len(X_test)})")
            continue

        # Entraîner et évaluer chaque modèle
        models = {
            "Logistic Regression": ReturnPredictorLogReg(),
            "XGBoost": ReturnPredictorXGBoost(),
            "Random Forest": ReturnPredictorRF(),
        }

        for name, model in models.items():
            model.fit(X_train, y_train)
            metrics = evaluate_prediction_model(model, X_train, y_train, X_test, y_test)
            models_metrics[name].append(metrics)

    # Agréger les résultats
    results = []
    for name, metrics_list in models_metrics.items():
        row = {
            "model": name,
            "accuracy_mean": round(np.mean([m["accuracy_test"] for m in metrics_list]), 4),
            "accuracy_std": round(np.std([m["accuracy_test"] for m in metrics_list]), 4),
            "auc_mean": round(np.mean([m["auc_test"] for m in metrics_list]), 4),
            "auc_std": round(np.std([m["auc_test"] for m in metrics_list]), 4),
            "f1_mean": round(np.mean([m["f1_test"] for m in metrics_list]), 4),
            "overfit_gap_mean": round(np.mean([m["overfit_gap"] for m in metrics_list]), 4),
            "n_folds": len(metrics_list),
        }
        results.append(row)

    df = pd.DataFrame(results)
    df = df.set_index("model")

    return df


def get_feature_importance_comparison(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    top_n: int = 10,
) -> pd.DataFrame:
    """
    Compare l'importance des features entre les modèles.

    Args:
        X_train: Features d'entraînement
        y_train: Target d'entraînement
        top_n: Nombre de features à afficher

    Returns:
        DataFrame avec importance par feature et par modèle
    """
    # Entraîner les modèles
    logreg = ReturnPredictorLogReg()
    xgb = ReturnPredictorXGBoost()
    rf = ReturnPredictorRF()

    logreg.fit(X_train, y_train)
    xgb.fit(X_train, y_train)
    rf.fit(X_train, y_train)

    # Récupérer les importances
    logreg_imp = logreg.get_feature_importance()
    xgb_imp = xgb.get_feature_importance()
    rf_imp = rf.get_feature_importance()

    # Créer DataFrame combiné
    df = pd.DataFrame({
        "feature": X_train.columns,
    })

    # Ajouter les importances normalisées
    df = df.merge(
        logreg_imp[["feature", "importance"]].rename(columns={"importance": "logreg"}),
        on="feature", how="left"
    )
    df = df.merge(
        xgb_imp[["feature", "importance"]].rename(columns={"importance": "xgboost"}),
        on="feature", how="left"
    )
    df = df.merge(
        rf_imp[["feature", "importance"]].rename(columns={"importance": "random_forest"}),
        on="feature", how="left"
    )

    # Importance moyenne
    df["mean_importance"] = df[["logreg", "xgboost", "random_forest"]].mean(axis=1)

    # Trier et limiter
    df = df.sort_values("mean_importance", ascending=False).head(top_n)

    return df
