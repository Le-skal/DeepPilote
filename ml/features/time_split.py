"""
Utilitaires pour le split temporel des données.

Implémente le walk-forward validation pour éviter le look-ahead bias.
"""

from datetime import datetime
from typing import Generator, Optional

import pandas as pd
from sklearn.model_selection import TimeSeriesSplit

from ml.config import TRAIN_YEARS, TEST_YEARS, TRADING_DAYS_YEAR


def walk_forward_split(
    df: pd.DataFrame,
    train_years: int = TRAIN_YEARS,
    test_years: int = TEST_YEARS,
    step_years: int = 1,
) -> Generator[tuple[pd.DataFrame, pd.DataFrame], None, None]:
    """
    Génère des splits walk-forward pour la validation temporelle.

    Le walk-forward avance dans le temps :
    - Train sur [t, t+train_years]
    - Test sur [t+train_years, t+train_years+test_years]
    - Puis avance de step_years et recommence

    Args:
        df: DataFrame avec index DatetimeIndex
        train_years: Nombre d'années d'entraînement
        test_years: Nombre d'années de test
        step_years: Pas d'avancement entre chaque split

    Yields:
        Tuple (df_train, df_test)

    Example:
        >>> for train, test in walk_forward_split(df, train_years=5, test_years=1):
        ...     model.fit(train)
        ...     score = model.evaluate(test)
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("L'index du DataFrame doit être un DatetimeIndex")

    # Trier par date
    df = df.sort_index()

    start_date = df.index.min()
    end_date = df.index.max()

    # Nombre de jours approximatif
    train_days = train_years * TRADING_DAYS_YEAR
    test_days = test_years * TRADING_DAYS_YEAR
    step_days = step_years * TRADING_DAYS_YEAR

    # Itérer sur les fenêtres
    current_start = 0

    while True:
        train_end = current_start + train_days
        test_end = train_end + test_days

        # Vérifier qu'on a assez de données
        if test_end > len(df):
            break

        # Extraire les données
        df_train = df.iloc[current_start:train_end]
        df_test = df.iloc[train_end:test_end]

        # Vérifier que les splits ne sont pas vides
        if len(df_train) > 0 and len(df_test) > 0:
            yield df_train, df_test

        # Avancer
        current_start += step_days


def walk_forward_split_dates(
    df: pd.DataFrame,
    train_years: int = TRAIN_YEARS,
    test_years: int = TEST_YEARS,
    step_years: int = 1,
) -> Generator[tuple[datetime, datetime, datetime, datetime], None, None]:
    """
    Génère les dates des splits walk-forward.

    Args:
        df: DataFrame avec index DatetimeIndex
        train_years: Nombre d'années d'entraînement
        test_years: Nombre d'années de test
        step_years: Pas d'avancement

    Yields:
        Tuple (train_start, train_end, test_start, test_end)
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("L'index du DataFrame doit être un DatetimeIndex")

    df = df.sort_index()

    for df_train, df_test in walk_forward_split(df, train_years, test_years, step_years):
        yield (
            df_train.index.min(),
            df_train.index.max(),
            df_test.index.min(),
            df_test.index.max(),
        )


def time_series_cv(
    n_samples: int,
    n_splits: int = 5,
    test_size: Optional[int] = None,
) -> TimeSeriesSplit:
    """
    Crée un splitter TimeSeriesSplit de sklearn.

    Args:
        n_samples: Nombre total d'échantillons
        n_splits: Nombre de splits
        test_size: Taille du test set (défaut: auto)

    Returns:
        Objet TimeSeriesSplit configuré
    """
    if test_size is None:
        # Par défaut : 1 année de test
        test_size = min(TRADING_DAYS_YEAR, n_samples // (n_splits + 1))

    return TimeSeriesSplit(n_splits=n_splits, test_size=test_size)


def get_train_test_indices(
    df: pd.DataFrame,
    train_end_date: str,
) -> tuple[pd.Index, pd.Index]:
    """
    Retourne les indices train/test basés sur une date de coupure.

    Args:
        df: DataFrame avec index DatetimeIndex
        train_end_date: Date de fin d'entraînement (format 'YYYY-MM-DD')

    Returns:
        Tuple (train_index, test_index)
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("L'index du DataFrame doit être un DatetimeIndex")

    cutoff = pd.Timestamp(train_end_date)

    train_idx = df.index[df.index <= cutoff]
    test_idx = df.index[df.index > cutoff]

    return train_idx, test_idx


def assert_no_lookahead(
    train_dates: pd.DatetimeIndex,
    test_dates: pd.DatetimeIndex,
) -> None:
    """
    Vérifie qu'il n'y a pas de look-ahead bias.

    Raises:
        AssertionError si les données de test précèdent les données d'entraînement
    """
    if len(train_dates) == 0 or len(test_dates) == 0:
        raise ValueError("Les indices train et test ne doivent pas être vides")

    train_max = train_dates.max()
    test_min = test_dates.min()

    assert test_min > train_max, (
        f"Look-ahead bias détecté ! "
        f"Train max: {train_max}, Test min: {test_min}"
    )
