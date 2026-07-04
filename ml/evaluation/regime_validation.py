"""
Validation économique des modèles de régime.

Phase 4.5 : Remplace le silhouette score par des métriques économiques
plus pertinentes pour évaluer la qualité des régimes détectés.

Métriques :
- crisis_recall : % des crises historiques détectées comme bear/volatile
- regime_return_separation : rendement moyen(bull) > rendement moyen(bear)
- regime_vol_separation : volatilité(volatile) > volatilité(stable)
"""

import numpy as np
import pandas as pd
from typing import Optional

from ml.config import REGIME_NAMES
from ml.evaluation.regime_labels import get_crisis_periods


def calculate_crisis_recall(
    regimes: pd.Series,
    prices: pd.DataFrame,
    spy_col: str = "SPY",
    crisis_regimes: tuple[int, ...] = (1, 2),  # bear et volatile
) -> dict:
    """
    Calcule le recall de détection des crises historiques.

    Une crise est considérée détectée si le modèle prédit un régime
    bear (1) ou volatile (2) pendant au moins 50% de la période.

    Args:
        regimes: Series des régimes prédits (index = dates)
        prices: DataFrame avec les prix (pour aligner les dates)
        spy_col: Colonne de prix pour référence
        crisis_regimes: Tuple des régimes considérés comme "crise" (bear, volatile)

    Returns:
        Dict avec recall global et détail par crise
    """
    crisis_periods = get_crisis_periods()

    results = {
        "crises_detected": 0,
        "crises_total": 0,
        "recall": 0.0,
        "details": {},
    }

    for crisis_name, (start, end) in crisis_periods.items():
        # Filtrer les régimes pour cette période
        mask = (regimes.index >= start) & (regimes.index <= end)
        crisis_regimes_period = regimes[mask]

        if len(crisis_regimes_period) == 0:
            # Pas de données pour cette période
            results["details"][crisis_name] = {
                "detected": False,
                "reason": "no_data",
                "coverage": 0.0,
            }
            continue

        # Calculer le % de jours en régime bear ou volatile
        crisis_days = crisis_regimes_period.isin(crisis_regimes).sum()
        total_days = len(crisis_regimes_period)
        coverage = crisis_days / total_days

        # Considéré comme détecté si >= 50% des jours en régime crise
        detected = coverage >= 0.50

        results["crises_total"] += 1
        if detected:
            results["crises_detected"] += 1

        results["details"][crisis_name] = {
            "detected": detected,
            "coverage": round(coverage, 3),
            "crisis_days": int(crisis_days),
            "total_days": int(total_days),
            "dominant_regime": REGIME_NAMES.get(
                crisis_regimes_period.mode().iloc[0] if len(crisis_regimes_period) > 0 else -1,
                "unknown"
            ),
        }

    # Calculer le recall global
    if results["crises_total"] > 0:
        results["recall"] = round(
            results["crises_detected"] / results["crises_total"],
            3
        )

    return results


def calculate_regime_return_separation(
    regimes: pd.Series,
    prices: pd.DataFrame,
    spy_col: str = "SPY",
) -> dict:
    """
    Vérifie que le rendement moyen du régime bull > rendement moyen du régime bear.

    C'est une validation économique intuitive : un modèle de régime doit
    identifier correctement les périodes de hausse vs baisse.

    Args:
        regimes: Series des régimes prédits
        prices: DataFrame avec les prix
        spy_col: Colonne de prix pour calculer les rendements

    Returns:
        Dict avec la séparation et les rendements par régime
    """
    # Calculer les rendements journaliers
    if spy_col not in prices.columns:
        return {
            "valid": False,
            "reason": f"Colonne {spy_col} non trouvée",
            "returns_by_regime": {},
        }

    returns = prices[spy_col].pct_change()

    # Aligner les indices
    common_idx = regimes.index.intersection(returns.index)
    regimes_aligned = regimes.loc[common_idx]
    returns_aligned = returns.loc[common_idx]

    # Calculer le rendement moyen par régime
    returns_by_regime = {}
    for regime_id, regime_name in REGIME_NAMES.items():
        mask = regimes_aligned == regime_id
        if mask.sum() > 0:
            mean_return = returns_aligned[mask].mean()
            # Annualisé
            annualized_return = mean_return * 252
            returns_by_regime[regime_name] = {
                "mean_daily": round(mean_return, 6),
                "annualized": round(annualized_return, 4),
                "n_days": int(mask.sum()),
            }
        else:
            returns_by_regime[regime_name] = {
                "mean_daily": None,
                "annualized": None,
                "n_days": 0,
            }

    # Vérifier la séparation bull > bear
    bull_return = returns_by_regime.get("bull", {}).get("annualized")
    bear_return = returns_by_regime.get("bear", {}).get("annualized")

    if bull_return is None or bear_return is None:
        valid = False
        reason = "Régime bull ou bear absent"
    else:
        valid = bull_return > bear_return
        reason = f"bull ({bull_return:.2%}) {'>' if valid else '<='} bear ({bear_return:.2%})"

    return {
        "valid": valid,
        "reason": reason,
        "returns_by_regime": returns_by_regime,
        "bull_return": bull_return,
        "bear_return": bear_return,
        "spread": round(bull_return - bear_return, 4) if bull_return and bear_return else None,
    }


def calculate_regime_vol_separation(
    regimes: pd.Series,
    prices: pd.DataFrame,
    spy_col: str = "SPY",
    window: int = 20,
) -> dict:
    """
    Vérifie que la volatilité du régime volatile > volatilité du régime stable.

    Args:
        regimes: Series des régimes prédits
        prices: DataFrame avec les prix
        spy_col: Colonne de prix pour calculer la volatilité
        window: Fenêtre pour la volatilité réalisée

    Returns:
        Dict avec la séparation et les volatilités par régime
    """
    if spy_col not in prices.columns:
        return {
            "valid": False,
            "reason": f"Colonne {spy_col} non trouvée",
            "vol_by_regime": {},
        }

    # Calculer la volatilité réalisée
    returns = prices[spy_col].pct_change()
    volatility = returns.rolling(window=window).std() * np.sqrt(252)

    # Aligner les indices
    common_idx = regimes.index.intersection(volatility.dropna().index)
    regimes_aligned = regimes.loc[common_idx]
    vol_aligned = volatility.loc[common_idx]

    # Calculer la volatilité moyenne par régime
    vol_by_regime = {}
    for regime_id, regime_name in REGIME_NAMES.items():
        mask = regimes_aligned == regime_id
        if mask.sum() > 0:
            mean_vol = vol_aligned[mask].mean()
            vol_by_regime[regime_name] = {
                "mean_annualized_vol": round(mean_vol, 4),
                "n_days": int(mask.sum()),
            }
        else:
            vol_by_regime[regime_name] = {
                "mean_annualized_vol": None,
                "n_days": 0,
            }

    # Vérifier la séparation volatile > stable
    volatile_vol = vol_by_regime.get("volatile", {}).get("mean_annualized_vol")
    stable_vol = vol_by_regime.get("stable", {}).get("mean_annualized_vol")

    if volatile_vol is None or stable_vol is None:
        valid = False
        reason = "Régime volatile ou stable absent"
    else:
        valid = volatile_vol > stable_vol
        reason = f"volatile ({volatile_vol:.2%}) {'>' if valid else '<='} stable ({stable_vol:.2%})"

    return {
        "valid": valid,
        "reason": reason,
        "vol_by_regime": vol_by_regime,
        "volatile_vol": volatile_vol,
        "stable_vol": stable_vol,
        "spread": round(volatile_vol - stable_vol, 4) if volatile_vol and stable_vol else None,
    }


def calculate_stability(regimes: pd.Series) -> float:
    """
    Calcule la stabilité des régimes (1 - taux de changement).

    Args:
        regimes: Series des régimes prédits

    Returns:
        Score de stabilité entre 0 et 1
    """
    if len(regimes) < 2:
        return 1.0

    changes = np.sum(np.diff(regimes.values) != 0)
    stability = 1 - (changes / len(regimes))
    return round(stability, 4)


def validate_hmm_economic(
    regimes: pd.Series,
    prices: pd.DataFrame,
    spy_col: str = "SPY",
    thresholds: Optional[dict] = None,
) -> dict:
    """
    Validation économique complète du modèle HMM.

    Remplace le silhouette score par des métriques économiques :
    - crisis_recall >= 0.80
    - regime_return_separation = True
    - regime_vol_separation = True
    - stability >= 0.90

    Args:
        regimes: Series des régimes prédits
        prices: DataFrame avec les prix
        spy_col: Colonne de prix
        thresholds: Dict des seuils (optionnel, utilise les défauts sinon)

    Returns:
        Dict avec résultats de validation et métriques détaillées
    """
    # Seuils par défaut
    if thresholds is None:
        thresholds = {
            "crisis_recall_min": 0.80,
            "stability_min": 0.90,
        }

    # Calculer toutes les métriques
    crisis_results = calculate_crisis_recall(regimes, prices, spy_col)
    return_results = calculate_regime_return_separation(regimes, prices, spy_col)
    vol_results = calculate_regime_vol_separation(regimes, prices, spy_col)
    stability = calculate_stability(regimes)

    # Évaluer chaque critère
    checks = {
        "crisis_recall": {
            "value": crisis_results["recall"],
            "threshold": thresholds["crisis_recall_min"],
            "passed": crisis_results["recall"] >= thresholds["crisis_recall_min"],
            "details": crisis_results["details"],
        },
        "regime_return_separation": {
            "value": return_results["valid"],
            "threshold": True,
            "passed": return_results["valid"],
            "details": return_results,
        },
        "regime_vol_separation": {
            "value": vol_results["valid"],
            "threshold": True,
            "passed": vol_results["valid"],
            "details": vol_results,
        },
        "stability": {
            "value": stability,
            "threshold": thresholds["stability_min"],
            "passed": stability >= thresholds["stability_min"],
        },
    }

    # Résultat global
    all_passed = all(check["passed"] for check in checks.values())
    n_passed = sum(1 for check in checks.values() if check["passed"])

    return {
        "valid": all_passed,
        "checks_passed": n_passed,
        "checks_total": len(checks),
        "checks": checks,
        "summary": {
            "crisis_recall": crisis_results["recall"],
            "return_separation": return_results["valid"],
            "vol_separation": vol_results["valid"],
            "stability": stability,
        },
    }


def print_validation_report(validation_result: dict) -> None:
    """
    Affiche un rapport de validation formaté.

    Args:
        validation_result: Résultat de validate_hmm_economic()
    """
    print("\n" + "=" * 60)
    print("VALIDATION ÉCONOMIQUE HMM")
    print("=" * 60)

    status = "VALIDÉ" if validation_result["valid"] else "ÉCHOUÉ"
    print(f"\nStatut: [{status}] ({validation_result['checks_passed']}/{validation_result['checks_total']} critères)")

    print("\nDétail des critères:")
    print("-" * 40)

    for name, check in validation_result["checks"].items():
        icon = "[OK]" if check["passed"] else "[FAIL]"

        if isinstance(check["value"], bool):
            value_str = "True" if check["value"] else "False"
        elif isinstance(check["value"], float):
            value_str = f"{check['value']:.3f}"
        else:
            value_str = str(check["value"])

        print(f"{icon} {name}: {value_str} (seuil: {check['threshold']})")

    # Détails des crises
    if "crisis_recall" in validation_result["checks"]:
        details = validation_result["checks"]["crisis_recall"].get("details", {})
        if details:
            print("\nDétection des crises:")
            for crisis_name, crisis_data in details.items():
                icon = "[OK]" if crisis_data.get("detected") else "[MISS]"
                coverage = crisis_data.get("coverage", 0)
                print(f"  {icon} {crisis_name}: {coverage:.1%} en régime crise")

    print()
