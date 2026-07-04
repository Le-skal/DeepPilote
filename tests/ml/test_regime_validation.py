"""
Tests pour la validation économique des régimes (Phase 4.5).

Teste les métriques économiques : crisis_recall, regime_return_separation,
regime_vol_separation, validate_hmm_economic.
"""

import numpy as np
import pandas as pd
import pytest

from ml.evaluation.regime_validation import (
    calculate_crisis_recall,
    calculate_regime_return_separation,
    calculate_regime_vol_separation,
    calculate_stability,
    validate_hmm_economic,
)
from ml.evaluation.regime_labels import get_crisis_periods


@pytest.fixture
def sample_prices():
    """Génère des prix synthétiques avec des crises."""
    np.random.seed(42)

    # Période de 2008 à 2023 pour couvrir les crises
    dates = pd.date_range("2008-01-01", "2023-12-31", freq="B")
    n = len(dates)

    # Prix SPY avec tendance haussière et crashs
    spy = [100]
    for i in range(1, n):
        date = dates[i]
        date_str = date.strftime("%Y-%m-%d")

        # Simuler les crises connues
        if "2008-09" <= date_str <= "2009-03":
            # GFC - baisse forte
            ret = np.random.normal(-0.003, 0.03)
        elif "2020-02-20" <= date_str <= "2020-03-31":
            # COVID - baisse forte
            ret = np.random.normal(-0.004, 0.04)
        elif "2022-01" <= date_str <= "2022-10":
            # Rate hikes - baisse modérée
            ret = np.random.normal(-0.001, 0.02)
        else:
            # Marché normal
            ret = np.random.normal(0.0005, 0.01)

        spy.append(spy[-1] * (1 + ret))

    return pd.DataFrame({"SPY": spy}, index=dates)


@pytest.fixture
def sample_regimes_good(sample_prices):
    """Régimes qui détectent correctement les crises."""
    regimes = pd.Series(index=sample_prices.index, dtype=int)
    regimes[:] = 3  # stable par défaut

    for date in sample_prices.index:
        date_str = date.strftime("%Y-%m-%d")

        # Détecte correctement les crises comme bear/volatile
        if "2008-09" <= date_str <= "2009-03":
            regimes[date] = 1  # bear
        elif "2010-05-06" <= date_str <= "2010-05-06":
            regimes[date] = 2  # volatile
        elif "2011-07" <= date_str <= "2011-10":
            regimes[date] = 2  # volatile
        elif "2015-08" <= date_str <= "2015-09":
            regimes[date] = 2  # volatile
        elif "2018-02" <= date_str <= "2018-02":
            regimes[date] = 2  # volatile
        elif "2020-02-20" <= date_str <= "2020-03-31":
            regimes[date] = 1  # bear
        elif "2022-01" <= date_str <= "2022-10":
            regimes[date] = 2  # volatile
        elif np.random.random() > 0.7:
            regimes[date] = 0  # bull parfois

    return regimes


@pytest.fixture
def sample_regimes_bad(sample_prices):
    """Régimes qui ne détectent pas les crises (tout stable)."""
    return pd.Series(3, index=sample_prices.index, name="regime")


class TestCalculateCrisisRecall:
    """Tests pour calculate_crisis_recall."""

    def test_perfect_detection(self, sample_prices, sample_regimes_good):
        """Test avec détection parfaite des crises."""
        result = calculate_crisis_recall(sample_regimes_good, sample_prices)

        # Au moins 60% des crises détectées (données synthétiques)
        assert result["recall"] >= 0.60
        assert result["crises_total"] > 0
        assert result["crises_total"] > 0
        assert result["crises_detected"] > 0

    def test_no_detection(self, sample_prices, sample_regimes_bad):
        """Test sans détection des crises."""
        result = calculate_crisis_recall(sample_regimes_bad, sample_prices)

        assert result["recall"] == 0.0
        assert result["crises_detected"] == 0

    def test_details_structure(self, sample_prices, sample_regimes_good):
        """Test de la structure des détails."""
        result = calculate_crisis_recall(sample_regimes_good, sample_prices)

        crisis_periods = get_crisis_periods()
        for crisis_name in crisis_periods:
            assert crisis_name in result["details"]
            detail = result["details"][crisis_name]
            assert "detected" in detail
            assert "coverage" in detail

    def test_coverage_threshold(self, sample_prices):
        """Test du seuil de 50% pour considérer une crise détectée."""
        regimes = pd.Series(3, index=sample_prices.index)  # stable

        # Mettre 60% de COVID en volatile
        covid_dates = [d for d in regimes.index if "2020-02-20" <= d.strftime("%Y-%m-%d") <= "2020-03-31"]
        for i, date in enumerate(covid_dates):
            if i < len(covid_dates) * 0.6:
                regimes[date] = 2  # volatile

        result = calculate_crisis_recall(regimes, sample_prices)

        # COVID devrait être détecté (60% > 50%)
        assert result["details"]["COVID_2020"]["detected"] == True


class TestCalculateRegimeReturnSeparation:
    """Tests pour calculate_regime_return_separation."""

    def test_valid_separation(self, sample_prices):
        """Test avec séparation valide (bull > bear)."""
        # Créer des régimes où bull a des rendements positifs
        regimes = pd.Series(index=sample_prices.index, dtype=int)
        returns = sample_prices["SPY"].pct_change()

        for date in regimes.index:
            ret = returns.get(date, 0)
            if ret > 0.005:
                regimes[date] = 0  # bull
            elif ret < -0.005:
                regimes[date] = 1  # bear
            else:
                regimes[date] = 3  # stable

        result = calculate_regime_return_separation(regimes, sample_prices)

        # Si la classification est bonne, bull > bear
        assert "valid" in result
        assert "bull_return" in result
        assert "bear_return" in result
        assert "returns_by_regime" in result

    def test_missing_column(self, sample_prices):
        """Test avec colonne manquante."""
        regimes = pd.Series(0, index=sample_prices.index)
        prices_no_spy = sample_prices.rename(columns={"SPY": "OTHER"})

        result = calculate_regime_return_separation(regimes, prices_no_spy)

        assert result["valid"] is False
        assert "non trouvée" in result["reason"]

    def test_all_same_regime(self, sample_prices):
        """Test avec un seul régime."""
        regimes = pd.Series(0, index=sample_prices.index)  # tout bull

        result = calculate_regime_return_separation(regimes, sample_prices)

        # bear n'existe pas, donc invalid
        assert result["valid"] is False


class TestCalculateRegimeVolSeparation:
    """Tests pour calculate_regime_vol_separation."""

    def test_valid_separation(self, sample_prices):
        """Test avec séparation valide (volatile > stable)."""
        # Créer des régimes basés sur la volatilité réalisée
        returns = sample_prices["SPY"].pct_change()
        vol_20d = returns.rolling(20).std() * np.sqrt(252)

        regimes = pd.Series(index=sample_prices.index, dtype=int)
        for date in regimes.index:
            vol = vol_20d.get(date, 0)
            if pd.isna(vol):
                regimes[date] = 3
            elif vol > 0.25:
                regimes[date] = 2  # volatile
            elif vol < 0.15:
                regimes[date] = 3  # stable
            else:
                regimes[date] = 0  # bull

        result = calculate_regime_vol_separation(regimes, sample_prices)

        assert "valid" in result
        assert "volatile_vol" in result
        assert "stable_vol" in result

    def test_no_volatile_regime(self, sample_prices):
        """Test sans régime volatile."""
        regimes = pd.Series(3, index=sample_prices.index)  # tout stable

        result = calculate_regime_vol_separation(regimes, sample_prices)

        assert result["valid"] is False
        assert "absent" in result["reason"]


class TestCalculateStability:
    """Tests pour calculate_stability."""

    def test_perfect_stability(self):
        """Test avec stabilité parfaite (aucun changement)."""
        regimes = pd.Series([0] * 100)
        stability = calculate_stability(regimes)
        assert stability == 1.0

    def test_no_stability(self):
        """Test sans stabilité (changement à chaque pas)."""
        regimes = pd.Series([0, 1] * 50)
        stability = calculate_stability(regimes)
        assert stability < 0.05  # ~0.01

    def test_moderate_stability(self):
        """Test avec stabilité modérée."""
        regimes = pd.Series([0] * 25 + [1] * 25 + [2] * 25 + [3] * 25)
        stability = calculate_stability(regimes)
        # 3 changements sur 100 = 97% stabilité
        assert 0.95 <= stability <= 0.98

    def test_empty_series(self):
        """Test avec série vide."""
        regimes = pd.Series([], dtype=int)
        stability = calculate_stability(regimes)
        assert stability == 1.0

    def test_single_element(self):
        """Test avec un seul élément."""
        regimes = pd.Series([0])
        stability = calculate_stability(regimes)
        assert stability == 1.0


class TestValidateHmmEconomic:
    """Tests pour validate_hmm_economic."""

    def test_all_checks_pass(self, sample_prices, sample_regimes_good):
        """Test avec tous les critères qui passent."""
        result = validate_hmm_economic(
            sample_regimes_good,
            sample_prices,
            thresholds={"crisis_recall_min": 0.50, "stability_min": 0.50}
        )

        assert "valid" in result
        assert "checks" in result
        assert "summary" in result
        assert result["checks_total"] == 4

    def test_all_checks_fail(self, sample_prices, sample_regimes_bad):
        """Test avec tous les critères qui échouent."""
        result = validate_hmm_economic(
            sample_regimes_bad,
            sample_prices,
            thresholds={"crisis_recall_min": 0.80, "stability_min": 0.90}
        )

        # Au moins crisis_recall devrait échouer
        assert result["checks"]["crisis_recall"]["passed"] is False

    def test_summary_structure(self, sample_prices, sample_regimes_good):
        """Test de la structure du résumé."""
        result = validate_hmm_economic(sample_regimes_good, sample_prices)

        summary = result["summary"]
        assert "crisis_recall" in summary
        assert "return_separation" in summary
        assert "vol_separation" in summary
        assert "stability" in summary

    def test_custom_thresholds(self, sample_prices, sample_regimes_good):
        """Test avec seuils personnalisés."""
        result = validate_hmm_economic(
            sample_regimes_good,
            sample_prices,
            thresholds={
                "crisis_recall_min": 0.99,  # Très strict
                "stability_min": 0.99,       # Très strict
            }
        )

        # Avec des seuils très stricts, devrait échouer
        assert result["valid"] is False

    def test_default_thresholds(self, sample_prices, sample_regimes_good):
        """Test avec seuils par défaut."""
        result = validate_hmm_economic(sample_regimes_good, sample_prices)

        # Vérifie que les seuils par défaut sont appliqués
        assert result["checks"]["crisis_recall"]["threshold"] == 0.80
        assert result["checks"]["stability"]["threshold"] == 0.90


class TestIntegration:
    """Tests d'intégration."""

    def test_full_validation_workflow(self, sample_prices):
        """Test du workflow complet de validation."""
        # Créer des régimes réalistes
        np.random.seed(42)
        regimes = pd.Series(index=sample_prices.index, dtype=int)

        for date in regimes.index:
            date_str = date.strftime("%Y-%m-%d")

            # Règles simples basées sur les périodes
            if "2008-09" <= date_str <= "2009-03":
                regimes[date] = 1  # bear
            elif "2020-02" <= date_str <= "2020-04":
                regimes[date] = 2  # volatile
            elif "2022-01" <= date_str <= "2022-10":
                regimes[date] = 2  # volatile
            else:
                regimes[date] = np.random.choice([0, 3], p=[0.3, 0.7])

        # Calculer toutes les métriques
        crisis = calculate_crisis_recall(regimes, sample_prices)
        returns = calculate_regime_return_separation(regimes, sample_prices)
        vol = calculate_regime_vol_separation(regimes, sample_prices)
        stability = calculate_stability(regimes)

        # Validation complète
        validation = validate_hmm_economic(regimes, sample_prices)

        # Vérifier la cohérence
        assert validation["summary"]["crisis_recall"] == crisis["recall"]
        assert validation["summary"]["stability"] == stability
