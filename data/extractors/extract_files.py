"""
Extraction de données depuis fichiers CSV (INSEE, BCE, etc.).

Ce module charge des fichiers CSV téléchargés manuellement depuis des sources
institutionnelles (INSEE, BCE/ECB) et les normalise au format standard du projet.

Usage:
    python -m data.extractors.extract_files
"""

import logging
from pathlib import Path
from typing import Literal

import pandas as pd

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Chemins
DATA_DIR = Path(__file__).parent.parent
RAW_FILES_DIR = DATA_DIR / "raw" / "files"
PROCESSED_DIR = DATA_DIR / "processed"


def load_csv_file(
    filepath: Path,
    encoding: str = "utf-8",
    separator: str = ",",
    date_column: str | None = None,
    date_format: str | None = None,
) -> pd.DataFrame:
    """
    Charge un fichier CSV avec gestion des encodages et séparateurs.

    Args:
        filepath: Chemin du fichier CSV.
        encoding: Encodage du fichier (utf-8, latin-1, etc.).
        separator: Séparateur de colonnes (, ou ; typique INSEE).
        date_column: Nom de la colonne date à parser.
        date_format: Format de date strptime (ex: %Y-%m).

    Returns:
        DataFrame avec les données chargées.

    Raises:
        FileNotFoundError: Si le fichier n'existe pas.
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Fichier non trouvé: {filepath}")

    logger.info(f"Chargement: {filepath}")
    logger.info(f"  Encodage: {encoding}, Séparateur: '{separator}'")

    # Essai de lecture avec les paramètres donnés
    try:
        df = pd.read_csv(filepath, encoding=encoding, sep=separator)
    except UnicodeDecodeError:
        # Fallback sur latin-1 si utf-8 échoue
        logger.warning(f"Encodage {encoding} échoué, essai avec latin-1")
        df = pd.read_csv(filepath, encoding="latin-1", sep=separator)

    # Parse de la colonne date si spécifiée
    if date_column and date_column in df.columns:
        if date_format:
            df[date_column] = pd.to_datetime(df[date_column], format=date_format)
        else:
            df[date_column] = pd.to_datetime(df[date_column], infer_datetime_format=True)
        df = df.set_index(date_column)

    logger.info(f"  Lignes: {len(df)}, Colonnes: {list(df.columns)}")
    return df


def normalize_insee_inflation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise les données d'inflation INSEE au format standard.

    Attendu: CSV avec colonnes période (YYYY-MM) et valeur inflation.

    Args:
        df: DataFrame brut de l'INSEE.

    Returns:
        DataFrame normalisé avec index Date et colonne 'inflation_eu'.
    """
    # L'INSEE utilise souvent des formats variés, on s'adapte
    df = df.copy()

    # Renommage vers format standard
    df.columns = [c.lower().strip() for c in df.columns]

    # Cherche la colonne de valeur (souvent nommée "valeur" ou contient des chiffres)
    value_col = None
    for col in df.columns:
        if "valeur" in col or "value" in col or "indice" in col:
            value_col = col
            break

    if value_col:
        df = df.rename(columns={value_col: "inflation_eu"})

    # Assure que l'index est bien un DatetimeIndex
    if not isinstance(df.index, pd.DatetimeIndex):
        logger.warning("Index non datetime, tentative de conversion")

    return df


def normalize_ecb_rate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise les données de taux directeur BCE au format standard.

    Args:
        df: DataFrame brut de la BCE/ECB.

    Returns:
        DataFrame normalisé avec index Date et colonne 'ecb_rate'.
    """
    df = df.copy()
    df.columns = [c.lower().strip() for c in df.columns]

    # Cherche la colonne de taux
    for col in df.columns:
        if "rate" in col or "taux" in col or "value" in col:
            df = df.rename(columns={col: "ecb_rate"})
            break

    return df


def load_and_normalize(
    filepath: Path,
    source_type: Literal["insee_inflation", "ecb_rate"],
    **load_kwargs,
) -> pd.DataFrame:
    """
    Charge et normalise un fichier selon son type de source.

    Args:
        filepath: Chemin du fichier.
        source_type: Type de source pour appliquer la bonne normalisation.
        **load_kwargs: Arguments passés à load_csv_file.

    Returns:
        DataFrame normalisé.
    """
    df = load_csv_file(filepath, **load_kwargs)

    if source_type == "insee_inflation":
        return normalize_insee_inflation(df)
    elif source_type == "ecb_rate":
        return normalize_ecb_rate(df)
    else:
        logger.warning(f"Type de source inconnu: {source_type}, retour sans normalisation")
        return df


def list_available_files() -> list[Path]:
    """Liste les fichiers CSV disponibles dans le dossier raw/files."""
    if not RAW_FILES_DIR.exists():
        RAW_FILES_DIR.mkdir(parents=True, exist_ok=True)
        return []
    return list(RAW_FILES_DIR.glob("*.csv"))


def main() -> None:
    """Point d'entrée principal."""
    logger.info("=== Extraction fichiers CSV ===")

    files = list_available_files()
    if not files:
        logger.warning(
            f"Aucun fichier trouvé dans {RAW_FILES_DIR}\n"
            "Téléchargez manuellement des fichiers depuis:\n"
            "  - INSEE: https://www.insee.fr\n"
            "  - BCE: https://sdw.ecb.europa.eu"
        )
        return

    logger.info(f"Fichiers trouvés: {[f.name for f in files]}")

    # Exemple de traitement (à adapter selon les fichiers réels)
    for filepath in files:
        try:
            # Détection automatique basique du type
            name_lower = filepath.name.lower()
            if "insee" in name_lower or "inflation" in name_lower:
                df = load_and_normalize(
                    filepath,
                    source_type="insee_inflation",
                    separator=";",  # INSEE utilise souvent ;
                    encoding="latin-1",
                )
            elif "ecb" in name_lower or "bce" in name_lower or "rate" in name_lower:
                df = load_and_normalize(
                    filepath,
                    source_type="ecb_rate",
                    separator=",",
                )
            else:
                df = load_csv_file(filepath)

            # Sauvegarde en format normalisé
            output_path = PROCESSED_DIR / f"normalized_{filepath.stem}.csv"
            df.to_csv(output_path)
            logger.info(f"Sauvegardé: {output_path}")

        except Exception as e:
            logger.error(f"Erreur sur {filepath.name}: {e}")


if __name__ == "__main__":
    main()
