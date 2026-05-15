# Guide MLOps DeepPilot

Ce guide explique comment utiliser les outils MLOps du projet DeepPilot.

## Table des matières

1. [MLflow Tracking](#mlflow-tracking)
2. [Model Registry](#model-registry)
3. [Monitoring](#monitoring)
4. [CI/CD](#cicd)

---

## MLflow Tracking

### Configuration

Le tracking MLflow est configuré dans `mlops/config.py` :

```python
from mlops import MLFLOW_CONFIG

print(MLFLOW_CONFIG.tracking_uri)  # file:///...mlruns
print(MLFLOW_CONFIG.experiments)   # dict des expériences
```

### Lancer MLflow UI

```bash
cd deeppilot
python -m mlflow ui --port 5000
```

Puis ouvrir http://localhost:5000 dans un navigateur.

> **Note** : `python -m mlflow` fonctionne sans activer de virtual environment.

### Tracker une expérience

```python
from mlops import start_run, log_params, log_metrics, log_model

# Démarrer un run
with start_run(experiment="regime_detection", run_name="hmm_v1") as run:
    # Logger les hyperparamètres
    log_params({"n_regimes": 4, "n_iter": 100})

    # Entraîner le modèle
    model = train_model(...)

    # Logger les métriques
    log_metrics({"silhouette": 0.22, "stability": 0.97})

    # Sauvegarder le modèle
    log_model(model, "hmm_model")
```

### Comparer des runs

```python
from mlops import get_best_run, compare_runs

# Trouver le meilleur run
best = get_best_run("regime_detection", metric="silhouette", mode="max")
print(f"Meilleur run: {best['run_id']}")
print(f"Métriques: {best['metrics']}")

# Comparer tous les runs
runs = compare_runs("regime_detection", metric="silhouette")
for run in runs:
    print(f"{run['run_name']}: {run['metrics']['silhouette']}")
```

---

## Model Registry

### Enregistrer un modèle

```python
from mlops.registry import register_model, MODEL_NAMES

# Après un run MLflow
model_version = register_model(
    run_id=best['run_id'],
    artifact_path="hmm_model",
    model_name=MODEL_NAMES['regime']
)
print(f"Enregistré: version {model_version}")
```

### Charger un modèle

```python
from mlops.registry import load_model, get_latest_version

# Charger la dernière version
model = load_model("deeppilot-regime-hmm", stage="Production")

# Ou une version spécifique
model = load_model("deeppilot-regime-hmm", version="3")
```

### Promouvoir un modèle

Le workflow de promotion :
1. **None** → **Staging** : après entraînement initial
2. **Staging** → **Production** : après validation
3. **Production** → **Archived** : quand remplacé

```python
from mlops.registry import promote_model, validate_model_for_promotion

# Valider avant promotion
is_valid, report = validate_model_for_promotion(
    model_name="deeppilot-regime-hmm",
    version="3",
    thresholds={"silhouette_min": 0.15, "stability_min": 0.90}
)

if is_valid:
    # Promouvoir en production
    promote_model(
        model_name="deeppilot-regime-hmm",
        version="3",
        target_stage="Production"
    )
```

---

## Monitoring

### Détection de drift

```python
from mlops.monitoring import detect_data_drift, calculate_psi

# Calculer le PSI pour une feature
psi = calculate_psi(X_train['vix'].values, X_new['vix'].values)
print(f"PSI: {psi}")
# PSI < 0.1: pas de drift
# 0.1 <= PSI < 0.25: drift modéré
# PSI >= 0.25: drift significatif

# Détecter le drift sur toutes les features
drift_detected, reports = detect_data_drift(X_train, X_new)
for r in reports:
    if r.drift_detected:
        print(f"Drift sur {r.feature}: PSI={r.psi:.3f}")
```

### Monitoring des performances

```python
from mlops.monitoring import check_model_performance, PERFORMANCE_THRESHOLDS

# Vérifier les métriques
metrics = {"accuracy": 0.58, "auc": 0.62}
report = check_model_performance(
    metrics,
    PERFORMANCE_THRESHOLDS['prediction'],
    model_name="deeppilot-rf"
)

if report.has_alerts:
    print(f"ALERTE: {report.alerts}")
```

### Monitoring continu

```python
from mlops.monitoring import ModelMonitor

# Créer un moniteur
monitor = ModelMonitor(
    model_name="deeppilot-hmm",
    X_reference=X_train,
    thresholds={"silhouette_min": 0.15}
)

# En production, vérifier périodiquement
drift, reports = monitor.check_data(X_new)
perf = monitor.check_performance({"silhouette": 0.20})

# Consulter le status
status = monitor.get_status()
print(f"Drift détecté: {status['drift_detected']}")
print(f"Alertes perf: {status['has_performance_alerts']}")
```

---

## CI/CD

### GitHub Actions

Deux workflows sont configurés :

#### 1. `ml_tests.yml`

Déclenché sur push/PR qui modifient `ml/` ou `mlops/` :
- Execute les tests unitaires ML (`tests/ml/`)
- Execute les tests MLOps (`tests/mlops/`)
- Valide que les modèles s'entraînent sans erreur

#### 2. Validation des modèles

Le script `scripts/validate_models.py` :
- Entraîne HMM et RF sur données récentes
- Vérifie que les métriques respectent les seuils
- Retourne code 0 si OK, 1 si échec

```bash
python scripts/validate_models.py
```

### Secrets GitHub requis

Pour que le CI/CD fonctionne, configurer ces secrets dans le repo GitHub :
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `FRED_API_KEY`

---

## Seuils de performance

Les seuils sont définis dans `mlops/config.py` :

| Modèle | Métrique | Seuil |
|--------|----------|-------|
| HMM | silhouette_min | 0.15 |
| HMM | stability_min | 0.90 |
| RF | accuracy_min | 0.52 |
| RF | auc_min | 0.50 |
| Backtest | sharpe_min | 0.0 |
| Backtest | max_drawdown_max | -0.40 |

---

## Notebooks de démonstration

- `analysis/08_mlflow_tracking.ipynb` : démo complète du tracking
- `analysis/09_model_monitoring.ipynb` : démo du monitoring

---

## Compétences validées

- **C11** : MLOps (tracking, registry, CI/CD)
- **C13** : Monitoring des modèles ML
