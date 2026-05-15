"""
Module de monitoring ML pour DeepPilot.

Fournit :
- Détection de drift des données
- Monitoring des performances
- Alertes automatiques
"""

import logging
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime

import numpy as np
import pandas as pd
from scipy import stats

# Logger
logger = logging.getLogger(__name__)


@dataclass
class DriftReport:
    """Rapport de drift pour une feature."""

    feature: str
    drift_detected: bool
    psi: float
    ks_statistic: float
    ks_pvalue: float
    mean_shift: float
    std_shift: float
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class PerformanceReport:
    """Rapport de performance d'un modèle."""

    model_name: str
    metrics: Dict[str, float]
    thresholds: Dict[str, float]
    alerts: List[str]
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    @property
    def has_alerts(self) -> bool:
        return len(self.alerts) > 0


def calculate_psi(
    expected: np.ndarray,
    actual: np.ndarray,
    n_bins: int = 10,
) -> float:
    """
    Calcule le Population Stability Index (PSI).

    PSI mesure le changement de distribution entre deux populations.
    - PSI < 0.1 : pas de changement significatif
    - 0.1 <= PSI < 0.25 : changement modéré
    - PSI >= 0.25 : changement significatif

    Args:
        expected: Distribution de référence (training)
        actual: Distribution actuelle (inference)
        n_bins: Nombre de bins pour la discrétisation

    Returns:
        Valeur PSI
    """
    # Gérer les valeurs manquantes
    expected = expected[~np.isnan(expected)]
    actual = actual[~np.isnan(actual)]

    if len(expected) == 0 or len(actual) == 0:
        return 0.0

    # Créer les bins basés sur les quantiles de expected
    breakpoints = np.percentile(expected, np.linspace(0, 100, n_bins + 1))
    breakpoints[0] = -np.inf
    breakpoints[-1] = np.inf

    # Calculer les proportions dans chaque bin
    expected_percents = np.histogram(expected, bins=breakpoints)[0] / len(expected)
    actual_percents = np.histogram(actual, bins=breakpoints)[0] / len(actual)

    # Éviter les divisions par zéro
    expected_percents = np.clip(expected_percents, 0.0001, None)
    actual_percents = np.clip(actual_percents, 0.0001, None)

    # Calculer PSI
    psi = np.sum((actual_percents - expected_percents) * np.log(actual_percents / expected_percents))

    return float(psi)


def detect_data_drift(
    X_reference: pd.DataFrame,
    X_current: pd.DataFrame,
    psi_threshold: float = 0.25,
    ks_alpha: float = 0.05,
) -> Tuple[bool, List[DriftReport]]:
    """
    Détecte le drift des données entre deux DataFrames.

    Args:
        X_reference: Données de référence (training)
        X_current: Données actuelles (inference)
        psi_threshold: Seuil PSI pour détecter le drift
        ks_alpha: Seuil de significativité pour le test KS

    Returns:
        Tuple (drift_detected, list of DriftReport)
    """
    reports = []
    drift_detected = False

    # Vérifier que les colonnes correspondent
    common_cols = list(set(X_reference.columns) & set(X_current.columns))

    for col in common_cols:
        ref_values = X_reference[col].dropna().values
        cur_values = X_current[col].dropna().values

        if len(ref_values) == 0 or len(cur_values) == 0:
            continue

        # Calculer PSI
        psi = calculate_psi(ref_values, cur_values)

        # Test de Kolmogorov-Smirnov
        ks_stat, ks_pvalue = stats.ks_2samp(ref_values, cur_values)

        # Calculer les shifts de moyenne et std
        mean_shift = (cur_values.mean() - ref_values.mean()) / (ref_values.std() + 1e-10)
        std_shift = (cur_values.std() - ref_values.std()) / (ref_values.std() + 1e-10)

        # Détecter le drift
        feature_drift = (psi >= psi_threshold) or (ks_pvalue < ks_alpha)

        if feature_drift:
            drift_detected = True
            logger.warning(f"Drift détecté sur {col}: PSI={psi:.3f}, KS p-value={ks_pvalue:.4f}")

        reports.append(DriftReport(
            feature=col,
            drift_detected=feature_drift,
            psi=psi,
            ks_statistic=ks_stat,
            ks_pvalue=ks_pvalue,
            mean_shift=mean_shift,
            std_shift=std_shift,
        ))

    return drift_detected, reports


def detect_prediction_drift(
    y_reference: np.ndarray,
    y_current: np.ndarray,
    psi_threshold: float = 0.25,
) -> Tuple[bool, float]:
    """
    Détecte le drift dans les prédictions du modèle.

    Args:
        y_reference: Prédictions de référence
        y_current: Prédictions actuelles
        psi_threshold: Seuil PSI

    Returns:
        Tuple (drift_detected, psi_value)
    """
    psi = calculate_psi(y_reference, y_current)
    drift_detected = psi >= psi_threshold

    if drift_detected:
        logger.warning(f"Drift de prédiction détecté: PSI={psi:.3f}")

    return drift_detected, psi


def check_model_performance(
    metrics: Dict[str, float],
    thresholds: Dict[str, float],
    model_name: str = "unknown",
) -> PerformanceReport:
    """
    Vérifie que les métriques respectent les seuils.

    Args:
        metrics: Métriques actuelles du modèle
        thresholds: Seuils à respecter (format: "metric_min" ou "metric_max")
        model_name: Nom du modèle

    Returns:
        PerformanceReport
    """
    alerts = []

    for threshold_name, threshold_value in thresholds.items():
        metric_name = threshold_name.replace("_min", "").replace("_max", "")
        actual_value = metrics.get(metric_name)

        if actual_value is None:
            alerts.append(f"Métrique manquante: {metric_name}")
            continue

        if threshold_name.endswith("_min") and actual_value < threshold_value:
            alerts.append(
                f"{metric_name}: {actual_value:.4f} < seuil min {threshold_value:.4f}"
            )
        elif threshold_name.endswith("_max"):
            # Pour les métriques négatives (ex: max_drawdown), plus négatif = pire
            # Donc -0.45 est pire que -0.40 (dépasse le seuil max)
            if threshold_value < 0:
                # Seuil négatif : on alerte si actual est plus négatif
                if actual_value < threshold_value:
                    alerts.append(
                        f"{metric_name}: {actual_value:.4f} < seuil max {threshold_value:.4f}"
                    )
            else:
                # Seuil positif : on alerte si actual dépasse
                if actual_value > threshold_value:
                    alerts.append(
                        f"{metric_name}: {actual_value:.4f} > seuil max {threshold_value:.4f}"
                    )

    if alerts:
        logger.warning(f"Alertes performance pour {model_name}: {alerts}")

    return PerformanceReport(
        model_name=model_name,
        metrics=metrics,
        thresholds=thresholds,
        alerts=alerts,
    )


def generate_monitoring_summary(
    drift_reports: List[DriftReport],
    performance_report: PerformanceReport,
) -> Dict:
    """
    Génère un résumé du monitoring.

    Args:
        drift_reports: Liste des rapports de drift
        performance_report: Rapport de performance

    Returns:
        Dictionnaire résumé
    """
    n_features_drift = sum(1 for r in drift_reports if r.drift_detected)
    n_features_total = len(drift_reports)

    return {
        "timestamp": datetime.now().isoformat(),
        "model_name": performance_report.model_name,
        "data_drift": {
            "detected": n_features_drift > 0,
            "features_affected": n_features_drift,
            "features_total": n_features_total,
            "psi_values": {r.feature: r.psi for r in drift_reports},
        },
        "performance": {
            "metrics": performance_report.metrics,
            "has_alerts": performance_report.has_alerts,
            "alerts": performance_report.alerts,
        },
        "action_required": n_features_drift > 0 or performance_report.has_alerts,
    }


class ModelMonitor:
    """
    Classe pour monitorer un modèle en continu.

    Usage:
        monitor = ModelMonitor(
            model_name="deeppilot-regime-hmm",
            X_reference=X_train,
            thresholds={"silhouette_min": 0.15}
        )

        # Lors de l'inférence
        drift, reports = monitor.check_data(X_new)
        perf_report = monitor.check_performance(new_metrics)
    """

    def __init__(
        self,
        model_name: str,
        X_reference: pd.DataFrame,
        thresholds: Dict[str, float],
        psi_threshold: float = 0.25,
        ks_alpha: float = 0.05,
    ):
        """
        Initialise le moniteur.

        Args:
            model_name: Nom du modèle
            X_reference: Données de référence (training)
            thresholds: Seuils de performance
            psi_threshold: Seuil PSI pour le drift
            ks_alpha: Seuil alpha pour le test KS
        """
        self.model_name = model_name
        self.X_reference = X_reference.copy()
        self.thresholds = thresholds
        self.psi_threshold = psi_threshold
        self.ks_alpha = ks_alpha

        # Historique
        self.drift_history: List[Tuple[datetime, bool]] = []
        self.performance_history: List[PerformanceReport] = []

        logger.info(f"ModelMonitor initialisé pour {model_name}")

    def check_data(self, X_current: pd.DataFrame) -> Tuple[bool, List[DriftReport]]:
        """
        Vérifie le drift des données.

        Args:
            X_current: Données actuelles

        Returns:
            Tuple (drift_detected, reports)
        """
        drift, reports = detect_data_drift(
            self.X_reference,
            X_current,
            psi_threshold=self.psi_threshold,
            ks_alpha=self.ks_alpha,
        )

        self.drift_history.append((datetime.now(), drift))

        return drift, reports

    def check_performance(self, metrics: Dict[str, float]) -> PerformanceReport:
        """
        Vérifie les performances du modèle.

        Args:
            metrics: Métriques actuelles

        Returns:
            PerformanceReport
        """
        report = check_model_performance(
            metrics=metrics,
            thresholds=self.thresholds,
            model_name=self.model_name,
        )

        self.performance_history.append(report)

        return report

    def get_status(self) -> Dict:
        """
        Retourne le status actuel du modèle.

        Returns:
            Dictionnaire avec le status
        """
        recent_drift = self.drift_history[-1] if self.drift_history else (None, False)
        recent_perf = self.performance_history[-1] if self.performance_history else None

        return {
            "model_name": self.model_name,
            "last_drift_check": recent_drift[0].isoformat() if recent_drift[0] else None,
            "drift_detected": recent_drift[1],
            "last_performance_check": recent_perf.timestamp.isoformat() if recent_perf else None,
            "has_performance_alerts": recent_perf.has_alerts if recent_perf else False,
            "n_checks": len(self.drift_history),
        }
