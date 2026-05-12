"""
Règles de nettoyage centralisées pour les données DeepPilot.

Ce module définit les règles de détection et traitement des anomalies :
- Valeurs manquantes (NaN)
- Outliers (rendements extrêmes)
- Incohérences temporelles

Chaque règle est documentée avec sa justification.
"""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def check_temporal_monotonicity(df: pd.DataFrame) -> None:
    """
    Vérifie que l'index temporel est strictement croissant.

    Règle: L'index doit être monotone croissant (pas de doublons, pas de retours).
    Justification: Évite les erreurs de look-ahead bias dans les calculs ML.

    Args:
        df: DataFrame avec index DatetimeIndex.

    Raises:
        ValueError: Si l'index n'est pas monotone croissant.
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        logger.warning("Index non DatetimeIndex, conversion tentée")
        df.index = pd.to_datetime(df.index)

    if not df.index.is_monotonic_increasing:
        # Identifier les problèmes
        diff = df.index.to_series().diff()
        problems = diff[diff <= pd.Timedelta(0)]
        if len(problems) > 0:
            logger.error(f"Index non monotone à: {problems.index[:5].tolist()}")
            raise ValueError("Index temporel non monotone croissant")

    # Vérifier les doublons
    duplicates = df.index.duplicated()
    if duplicates.any():
        dup_dates = df.index[duplicates].unique()
        logger.error(f"Dates dupliquées: {dup_dates[:5].tolist()}")
        raise ValueError(f"{duplicates.sum()} dates dupliquées trouvées")

    logger.info("✓ Index temporel monotone et sans doublons")


def handle_missing_values(
    df: pd.DataFrame,
    critical_cols: list[str],
    max_consecutive_nan: int = 5,
) -> pd.DataFrame:
    """
    Gère les valeurs manquantes selon les règles définies.

    Règles:
    1. Colonnes critiques (prix ETF): forward-fill si gap <= max_consecutive_nan jours
    2. Colonnes critiques: suppression des lignes si gap > max_consecutive_nan jours
    3. Colonnes non-critiques (macro): forward-fill illimité (données mensuelles)

    Justification:
    - Les gaps courts (weekends, jours fériés) sont normaux → forward-fill
    - Les gaps longs indiquent un problème de données → mieux vaut supprimer
    - Les données macro sont mensuelles → forward-fill jusqu'à prochaine valeur

    Args:
        df: DataFrame à nettoyer.
        critical_cols: Colonnes où les NaN sont problématiques.
        max_consecutive_nan: Seuil de gap acceptable.

    Returns:
        DataFrame nettoyé.
    """
    df = df.copy()
    initial_rows = len(df)
    initial_nan = df.isna().sum().sum()

    # Identifier les colonnes présentes
    present_critical = [c for c in critical_cols if c in df.columns]
    other_cols = [c for c in df.columns if c not in present_critical]

    # 1. Forward-fill colonnes non-critiques (macro, etc.)
    if other_cols:
        df[other_cols] = df[other_cols].ffill()
        logger.info(f"Forward-fill appliqué sur {len(other_cols)} colonnes non-critiques")

    # 2. Traitement colonnes critiques
    for col in present_critical:
        # Identifier les blocs de NaN consécutifs
        is_nan = df[col].isna()
        nan_groups = (is_nan != is_nan.shift()).cumsum()
        nan_counts = is_nan.groupby(nan_groups).transform("sum")

        # Forward-fill uniquement les petits gaps
        small_gaps = is_nan & (nan_counts <= max_consecutive_nan)
        df.loc[small_gaps, col] = df[col].ffill().loc[small_gaps]

        # Marquer les grands gaps pour suppression potentielle
        large_gaps = is_nan & (nan_counts > max_consecutive_nan)
        if large_gaps.any():
            logger.warning(
                f"Colonne {col}: {large_gaps.sum()} NaN dans gaps > {max_consecutive_nan} jours"
            )

    # 3. Supprimer les lignes avec NaN restants dans colonnes critiques
    if present_critical:
        remaining_nan = df[present_critical].isna().any(axis=1)
        if remaining_nan.any():
            logger.info(f"Suppression de {remaining_nan.sum()} lignes avec NaN critiques")
            df = df[~remaining_nan]

    final_nan = df.isna().sum().sum()
    logger.info(
        f"NaN: {initial_nan} → {final_nan} | Lignes: {initial_rows} → {len(df)}"
    )

    return df


def detect_outliers(
    df: pd.DataFrame,
    tickers: list[str],
    threshold: float = 0.10,
) -> pd.DataFrame:
    """
    Détecte les rendements journaliers extrêmes (outliers).

    Règle: Un return > |threshold| (défaut 10%) est flaggé comme outlier.
    Justification:
    - Des returns > 10% en 1 jour sont rares mais possibles (flash crash, COVID)
    - On ne les supprime PAS (ce sont des données réelles), on les flag
    - Le flag permet aux modèles ML de les traiter différemment si besoin

    Args:
        df: DataFrame avec les prix.
        tickers: Liste des tickers à vérifier.
        threshold: Seuil de détection (défaut 0.10 = 10%).

    Returns:
        DataFrame avec colonne 'is_outlier' ajoutée.
    """
    df = df.copy()
    df["is_outlier"] = False

    for ticker in tickers:
        if ticker not in df.columns:
            continue

        # Calcul du return si pas déjà fait
        ret_col = f"{ticker}_ret_1d"
        if ret_col in df.columns:
            returns = df[ret_col]
        else:
            returns = df[ticker].pct_change()

        # Détection
        outliers = returns.abs() > threshold
        n_outliers = outliers.sum()

        if n_outliers > 0:
            df.loc[outliers, "is_outlier"] = True
            outlier_dates = df.index[outliers][:5].tolist()
            logger.warning(
                f"{ticker}: {n_outliers} outliers (|ret| > {threshold*100:.0f}%), "
                f"ex: {outlier_dates}"
            )

    total_outliers = df["is_outlier"].sum()
    logger.info(f"Total outliers flaggés: {total_outliers} lignes ({total_outliers/len(df)*100:.2f}%)")

    return df


def validate_price_range(
    df: pd.DataFrame,
    tickers: list[str],
    min_price: float = 0.01,
    max_price: float = 10000.0,
) -> bool:
    """
    Valide que les prix sont dans une plage raisonnable.

    Règle: Prix entre min_price et max_price.
    Justification: Détecte les erreurs d'échelle (prix en centimes vs dollars).

    Args:
        df: DataFrame avec les prix.
        tickers: Liste des tickers à valider.
        min_price: Prix minimum acceptable.
        max_price: Prix maximum acceptable.

    Returns:
        True si tous les prix sont valides, False sinon.
    """
    all_valid = True

    for ticker in tickers:
        if ticker not in df.columns:
            continue

        prices = df[ticker].dropna()
        below_min = (prices < min_price).sum()
        above_max = (prices > max_price).sum()

        if below_min > 0:
            logger.error(f"{ticker}: {below_min} prix < {min_price}")
            all_valid = False

        if above_max > 0:
            logger.error(f"{ticker}: {above_max} prix > {max_price}")
            all_valid = False

    if all_valid:
        logger.info(f"✓ Tous les prix dans la plage [{min_price}, {max_price}]")

    return all_valid


def validate_returns_range(
    df: pd.DataFrame,
    tickers: list[str],
    max_return: float = 0.50,
) -> bool:
    """
    Valide que les rendements journaliers sont dans une plage raisonnable.

    Règle: |return| <= max_return (défaut 50%).
    Justification: Un return > 50% en 1 jour est quasi impossible hors bug.

    Args:
        df: DataFrame avec les returns.
        tickers: Liste des tickers.
        max_return: Return maximum acceptable en valeur absolue.

    Returns:
        True si tous les returns sont valides, False sinon.
    """
    all_valid = True

    for ticker in tickers:
        ret_col = f"{ticker}_ret_1d"
        if ret_col not in df.columns:
            # Calcul à la volée
            if ticker in df.columns:
                returns = df[ticker].pct_change().dropna()
            else:
                continue
        else:
            returns = df[ret_col].dropna()

        extreme = (returns.abs() > max_return).sum()
        if extreme > 0:
            logger.error(f"{ticker}: {extreme} returns > |{max_return*100:.0f}%|")
            all_valid = False

    if all_valid:
        logger.info(f"✓ Tous les returns dans la plage [-{max_return*100:.0f}%, +{max_return*100:.0f}%]")

    return all_valid
