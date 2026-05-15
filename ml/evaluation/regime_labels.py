"""
Création des labels historiques pour évaluer les modèles de régime.

Utilise des règles basées sur les indicateurs connus pour créer un ground truth.
"""

import numpy as np
import pandas as pd
from typing import Optional

from ml.config import REGIME_NAMES


def create_historical_labels(
    df: pd.DataFrame,
    spy_col: str = "SPY",
    vix_col: Optional[str] = None,
) -> pd.Series:
    """
    Crée des labels de régime basés sur des règles historiques.

    Règles :
    - BEAR (1) : Drawdown SPY > 20%
    - VOLATILE (2) : VIX > 25 (sans être en bear)
    - BULL (0) : Return SPY 60j > 5% et VIX < 20
    - STABLE (3) : Sinon

    Args:
        df: DataFrame avec prix SPY et optionnellement VIX
        spy_col: Nom de la colonne SPY
        vix_col: Nom de la colonne VIX (auto-détecté si None)

    Returns:
        Series avec labels 0-3
    """
    labels = pd.Series(index=df.index, dtype=int)

    # Trouver la colonne VIX
    if vix_col is None:
        for col in ["vix", "VIX", "VIXCLS"]:
            if col in df.columns:
                vix_col = col
                break

    # Calculer les indicateurs
    if spy_col in df.columns:
        spy = df[spy_col].copy()

        # Drawdown
        cummax = spy.cummax()
        drawdown = (spy - cummax) / cummax

        # Return 60 jours
        return_60d = spy.pct_change(60)
    else:
        # Si pas de SPY, utiliser des valeurs neutres
        drawdown = pd.Series(0, index=df.index)
        return_60d = pd.Series(0, index=df.index)

    # VIX
    if vix_col and vix_col in df.columns:
        vix = df[vix_col].copy()
    else:
        vix = pd.Series(20, index=df.index)  # Valeur neutre

    # Appliquer les règles (ordre important)
    # Par défaut : stable (3)
    labels[:] = 3

    # Bull : return positif et VIX bas
    bull_mask = (return_60d > 0.05) & (vix < 20)
    labels[bull_mask] = 0

    # Volatile : VIX élevé (mais pas bear)
    volatile_mask = (vix > 25) & (drawdown > -0.20)
    labels[volatile_mask] = 2

    # Bear : drawdown important (priorité sur volatile)
    bear_mask = drawdown < -0.20
    labels[bear_mask] = 1

    labels.name = "historical_regime"
    return labels


def get_nber_recession_dates() -> list[tuple[str, str]]:
    """
    Retourne les dates des récessions NBER depuis 2007.

    Returns:
        Liste de tuples (start_date, end_date)
    """
    return [
        ("2007-12-01", "2009-06-30"),  # Grande Récession
        ("2020-02-01", "2020-04-30"),  # COVID-19
    ]


def add_recession_labels(
    df: pd.DataFrame,
    recession_dates: Optional[list[tuple[str, str]]] = None,
) -> pd.Series:
    """
    Ajoute un label binaire pour les périodes de récession NBER.

    Args:
        df: DataFrame avec index DatetimeIndex
        recession_dates: Liste de (start, end) dates, ou None pour NBER

    Returns:
        Series avec 1 si récession, 0 sinon
    """
    if recession_dates is None:
        recession_dates = get_nber_recession_dates()

    labels = pd.Series(0, index=df.index, name="recession")

    for start, end in recession_dates:
        mask = (df.index >= start) & (df.index <= end)
        labels[mask] = 1

    return labels


def get_crisis_periods() -> dict[str, tuple[str, str]]:
    """
    Retourne les périodes de crise majeures pour annotation.

    Returns:
        Dict {nom_crise: (start_date, end_date)}
    """
    return {
        "GFC_2008": ("2008-09-01", "2009-03-31"),
        "Flash_Crash_2010": ("2010-05-06", "2010-05-06"),
        "Euro_Crisis_2011": ("2011-07-01", "2011-10-31"),
        "China_Fears_2015": ("2015-08-01", "2015-09-30"),
        "Vol_Spike_2018": ("2018-02-01", "2018-02-28"),
        "COVID_2020": ("2020-02-20", "2020-03-31"),
        "Rate_Hikes_2022": ("2022-01-01", "2022-10-31"),
    }


def evaluate_regime_labels(
    predicted: pd.Series,
    historical: pd.Series,
) -> dict:
    """
    Évalue les labels de régime prédits vs historiques.

    Args:
        predicted: Labels prédits (0-3)
        historical: Labels historiques (0-3)

    Returns:
        Dict avec métriques d'évaluation
    """
    from sklearn.metrics import (
        adjusted_rand_score,
        normalized_mutual_info_score,
        accuracy_score,
    )

    # Aligner les indices
    common_idx = predicted.index.intersection(historical.index)
    pred = predicted.loc[common_idx]
    hist = historical.loc[common_idx]

    # Métriques de clustering
    ari = adjusted_rand_score(hist, pred)
    nmi = normalized_mutual_info_score(hist, pred)

    # Accuracy (si les labels sont alignés)
    acc = accuracy_score(hist, pred)

    # Confusion par régime
    confusion = {}
    for regime in range(4):
        pred_mask = pred == regime
        hist_mask = hist == regime
        tp = (pred_mask & hist_mask).sum()
        fp = (pred_mask & ~hist_mask).sum()
        fn = (~pred_mask & hist_mask).sum()
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        confusion[REGIME_NAMES[regime]] = {
            "precision": round(precision, 3),
            "recall": round(recall, 3),
        }

    return {
        "adjusted_rand_index": round(ari, 4),
        "normalized_mutual_info": round(nmi, 4),
        "accuracy": round(acc, 4),
        "per_regime": confusion,
    }
