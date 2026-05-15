# Checkpoint Phase 4 — MLOps

**Date** : 15 mai 2026
**Status** : ✅ Complète

---

## Résumé

La Phase 4 MLOps est terminée. Le projet dispose maintenant d'une infrastructure complète pour :
- Tracker les expériences ML avec MLflow
- Versionner les modèles dans un registry
- Détecter le drift des données et des prédictions
- Valider automatiquement les modèles via CI/CD

---

## Fichiers créés

### Module MLOps

| Fichier | Description |
|---------|-------------|
| `mlops/__init__.py` | Exports du module |
| `mlops/config.py` | Configuration MLflow, expériences, seuils |
| `mlops/tracking.py` | Wrapper MLflow (start_run, log_params, etc.) |
| `mlops/registry.py` | Model registry (register, load, promote) |
| `mlops/monitoring.py` | Drift detection (PSI, KS test, ModelMonitor) |

### Tests

| Fichier | Tests |
|---------|-------|
| `tests/mlops/__init__.py` | Module tests |
| `tests/mlops/test_tracking.py` | 12 tests |
| `tests/mlops/test_monitoring.py` | 18 tests |

### CI/CD

| Fichier | Description |
|---------|-------------|
| `.github/workflows/ml_tests.yml` | Tests ML et MLOps automatiques |
| `scripts/validate_models.py` | Validation des modèles |

### Notebooks

| Fichier | Description |
|---------|-------------|
| `analysis/08_mlflow_tracking.ipynb` | Démo tracking + registry |
| `analysis/09_model_monitoring.ipynb` | Démo monitoring + drift |

### Documentation

| Fichier | Description |
|---------|-------------|
| `docs/mlops/README.md` | Guide complet MLOps |

---

## Résultats des notebooks

### Notebook 08 - MLflow Tracking

**HMM Grid Search (4 configurations):**
| Config | n_regimes | Silhouette | Stability |
|--------|-----------|------------|-----------|
| 1 | 3 | 0.121 | 55.9% |
| 2 | 4 | 0.034 | 96.7% |
| 3 | 4 | 0.034 | 96.7% |
| 4 | 5 | -0.011 | 95.2% |

**Random Forest Grid Search (4 configurations):**
| Config | n_estimators | max_depth | Accuracy | AUC |
|--------|--------------|-----------|----------|-----|
| 1 | 50 | 5 | 0.608 | 0.495 |
| 2 | 100 | 5 | 0.613 | 0.498 |
| 3 | 100 | 8 | 0.604 | 0.514 |
| 4 | 200 | 10 | 0.600 | 0.514 |

**Models enregistrés:**
- `deeppilot-regime-hmm` v2
- `deeppilot-prediction-rf` v2

### Notebook 09 - Model Monitoring

**Drift Detection (référence < 2022 vs actuel >= 2022):**
| Feature | PSI | Status |
|---------|-----|--------|
| yield_curve_10y2y | 5.49 | DRIFT majeur |
| spy_volatility_20d | 0.31 | DRIFT |
| spy_return_20d | 0.09 | OK |
| credit_spread_zscore | 0.03 | OK |
| vix_zscore | 0.03 | OK |

> Le PSI de 5.49 sur la courbe des taux reflète les hausses de taux 2022-2023.

**Performance Monitoring:**
- Alertes déclenchées correctement quand métriques sous seuils
- Max drawdown check fonctionne pour valeurs négatives

---

## Résultats des tests

```
======================== 182 passed in 21.88s ========================
```

- **30 tests MLOps** : tracking, monitoring, drift detection
- **61 tests ML** : régimes, prédiction, portfolio
- **91 autres tests** : data, extractors, API

---

## Seuils de performance configurés

| Modèle | Métrique | Seuil |
|--------|----------|-------|
| HMM | silhouette_min | 0.15 |
| HMM | stability_min | 0.90 |
| RF | accuracy_min | 0.52 |
| RF | auc_min | 0.50 |
| Backtest | sharpe_min | 0.0 |
| Backtest | max_drawdown_max | -0.40 |

---

## Lancer MLflow UI

```bash
cd deeppilot
python -m mlflow ui --port 5000
```

Puis ouvrir http://localhost:5000

---

## Compétences validées

- **C11** : MLOps (tracking, registry, CI/CD)
- **C13** : Monitoring des modèles ML

---

## Prochaine étape

**Phase 5** : Service IA tiers (Mistral API pour sentiment analysis)

---

**Total fichiers Phase 4** : 12 fichiers
**Total tests Phase 4** : 30 tests
