# DeepPilot — TODO Phase 4 : MLOps

> **Phase actuelle : Phase 4**
> Focus : MLflow tracking, CI/CD ML, monitoring des modèles
> Compétences visées : C11 (MLOps/déploiement ML), C13 (monitoring ML)

---

## ÉTAPE 0 — Setup MLOps [✅ FAIT]

### 0.1 Nouvelles dépendances

- [x] Ajouté au `requirements.txt` : `mlflow>=2.10.0`
- [x] `pip install -r requirements.txt`

### 0.2 Structure dossiers MLOps

- [x] Créé `mlops/__init__.py` (exports tracking, registry, monitoring)
- [x] Créé `mlops/config.py` (configuration MLflow + seuils performance)
- [x] Créé `mlops/tracking.py` (wrapper MLflow)
- [x] Créé `mlops/registry.py` (model registry)
- [x] Créé `mlops/monitoring.py` (drift detection + PSI)

---

## ÉTAPE 1 — MLflow Tracking [✅ FAIT]

### 1.1 Configuration MLflow

- [x] Créé `mlops/config.py` :
  - [x] `MLFLOW_TRACKING_URI` (local file store)
  - [x] `EXPERIMENTS` dict avec 4 expériences
  - [x] `MODEL_NAMES` pour le registry
  - [x] `PERFORMANCE_THRESHOLDS` pour validation

### 1.2 Tracking des expériences

- [x] Créé `mlops/tracking.py` avec toutes les fonctions wrapper

### 1.3 Intégration avec les modèles existants

- [x] Via notebooks (08_mlflow_tracking.ipynb montre l'intégration)

### 1.4 Notebook MLflow

- [x] Créé `analysis/08_mlflow_tracking.ipynb` :
  - [x] Démonstration du tracking HMM et RF
  - [x] Comparaison de runs
  - [x] Model Registry

---

## ÉTAPE 2 — Model Registry [✅ FAIT]

### 2.1 Enregistrement des modèles

- [x] Créé `mlops/registry.py` avec fonctions complètes

### 2.2 Workflow de promotion

- [x] Documenté dans `docs/mlops/README.md`

---

## ÉTAPE 3 — CI/CD ML [✅ FAIT]

### 3.1 GitHub Actions pour ML

- [x] Créé `.github/workflows/ml_tests.yml` :
  - [x] Trigger : push sur main, PR
  - [x] Job : lancer `pytest tests/ml/`
  - [x] Job : lancer `pytest tests/mlops/`
  - [x] Job : validate_models.py

### 3.2 Scripts de validation

- [x] Créé `scripts/validate_models.py` :
  - [x] Entraîne HMM et RF sur données récentes
  - [x] Vérifie métriques vs seuils
  - [x] Retourne code 0 si OK, 1 si échec

---

## ÉTAPE 4 — Monitoring ML [✅ FAIT]

### 4.1 Drift Detection

- [x] Créé `mlops/monitoring.py` avec PSI et KS test

### 4.2 Alertes de performance

- [x] `check_model_performance()` avec gestion seuils min/max

### 4.3 Classe ModelMonitor

- [x] Monitoring continu avec historique

### 4.4 Dashboard monitoring

- [x] Créé `analysis/09_model_monitoring.ipynb` :
  - [x] Visualisation PSI par feature
  - [x] Distributions avec drift
  - [x] Évolution métriques dans le temps

---

## ÉTAPE 5 — Tests MLOps [✅ FAIT]

### 5.1 Tests unitaires

- [x] `tests/mlops/__init__.py`
- [x] `tests/mlops/test_tracking.py` : 12 tests
- [x] `tests/mlops/test_monitoring.py` : 18 tests

### 5.2 Lancer les tests

- [x] **30 tests MLOps passent**
- [x] **182 tests totaux passent**

---

## ÉTAPE 6 — Documentation MLOps [✅ FAIT]

### 6.1 Guide MLflow

- [x] Créé `docs/mlops/README.md` :
  - [x] Comment lancer MLflow UI
  - [x] Comment tracker une expérience
  - [x] Comment promouvoir un modèle
  - [x] Monitoring et CI/CD

---

## ÉTAPE 7 — Commit final Phase 4 [À FAIRE]

- [ ] Commit : "feat: MLOps with MLflow tracking, model registry, CI/CD"
- [ ] Tag Git : `v0.4.0-mlops-phase`
- [ ] Push

---

## ✅ Definition of Done — Phase 4

La Phase 4 est terminée quand :

- [x] MLflow tracking fonctionnel
- [x] Model registry avec versioning
- [x] CI/CD GitHub Actions pour tests ML
- [x] Drift detection implémenté
- [x] Notebooks de démonstration (08, 09)
- [x] Tests MLOps passent (30 tests)
- [x] Documentation MLOps complète

**Compétences validées en Phase 4** : C11 (MLOps), C13 (monitoring ML)

---

## Progression

| Module | Fichiers | Tests | Status |
|--------|----------|-------|--------|
| mlops/config | 1 | - | ✅ |
| mlops/tracking | 1 | 12 | ✅ |
| mlops/registry | 1 | - | ✅ |
| mlops/monitoring | 1 | 18 | ✅ |
| tests/mlops | 3 | 30 | ✅ |
| .github/workflows | 1 | - | ✅ |
| scripts/validate_models | 1 | - | ✅ |
| analysis notebooks | 2 | - | ✅ |
| docs/mlops | 1 | - | ✅ |
| **Total** | **12 fichiers** | **30 tests** | ✅ 100% |

---

## 🚫 Hors scope Phase 4

- Déploiement cloud des modèles (Phase 6-7)
- Sentiment analysis Mistral (Phase 5)
- Interface utilisateur (Phase 6)
- Kubernetes / Docker (si nécessaire, Phase 7)
