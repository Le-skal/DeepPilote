"""
Tests unitaires pour l'extracteur de fichiers CSV.
"""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from data.extractors.extract_files import (
    list_available_files,
    load_csv_file,
    normalize_ecb_rate,
    normalize_insee_inflation,
)


class TestLoadCsvFile:
    """Tests de la fonction load_csv_file."""

    @pytest.fixture
    def temp_csv_utf8(self):
        """Crée un fichier CSV temporaire en UTF-8."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("date,value\n2024-01-01,100\n2024-01-02,101\n")
            return Path(f.name)

    @pytest.fixture
    def temp_csv_semicolon(self):
        """Crée un fichier CSV temporaire avec séparateur ;."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("date;valeur\n2024-01-01;100\n2024-01-02;101\n")
            return Path(f.name)

    def test_load_utf8_comma(self, temp_csv_utf8):
        """Charge un CSV standard UTF-8 avec virgules."""
        df = load_csv_file(temp_csv_utf8)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "date" in df.columns
        assert "value" in df.columns

    def test_load_semicolon_separator(self, temp_csv_semicolon):
        """Charge un CSV avec séparateur point-virgule (style INSEE)."""
        df = load_csv_file(temp_csv_semicolon, separator=";")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "valeur" in df.columns

    def test_file_not_found(self):
        """Vérifie qu'une erreur est levée si le fichier n'existe pas."""
        with pytest.raises(FileNotFoundError):
            load_csv_file(Path("/nonexistent/file.csv"))

    def test_parse_date_column(self, temp_csv_utf8):
        """Vérifie le parsing de la colonne date."""
        df = load_csv_file(temp_csv_utf8, date_column="date")
        assert isinstance(df.index, pd.DatetimeIndex)


class TestNormalizeInseeInflation:
    """Tests de la normalisation INSEE."""

    def test_normalize_columns_lowercase(self):
        """Vérifie que les colonnes sont mises en minuscules."""
        df = pd.DataFrame({"DATE": ["2024-01"], "VALEUR": [100]})
        result = normalize_insee_inflation(df)
        assert all(c.islower() for c in result.columns)

    def test_rename_valeur_column(self):
        """Vérifie le renommage de la colonne valeur."""
        df = pd.DataFrame({"date": ["2024-01"], "valeur": [2.5]})
        result = normalize_insee_inflation(df)
        assert "inflation_eu" in result.columns


class TestNormalizeEcbRate:
    """Tests de la normalisation BCE."""

    def test_rename_rate_column(self):
        """Vérifie le renommage de la colonne taux."""
        df = pd.DataFrame({"date": ["2024-01"], "rate": [4.5]})
        result = normalize_ecb_rate(df)
        assert "ecb_rate" in result.columns

    def test_rename_taux_column(self):
        """Vérifie le renommage de la colonne taux (français)."""
        df = pd.DataFrame({"date": ["2024-01"], "taux": [4.5]})
        result = normalize_ecb_rate(df)
        assert "ecb_rate" in result.columns


class TestListAvailableFiles:
    """Tests de la fonction list_available_files."""

    def test_returns_list(self):
        """Vérifie que la fonction retourne une liste."""
        result = list_available_files()
        assert isinstance(result, list)
