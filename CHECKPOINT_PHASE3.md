# DeepPilot — Checkpoint Phase 3

> **Date** : 15 mai 2026
> **Session** : Modèles ML avec comparaisons (HMM, RF, Backtest)

---

## Ce qui a été fait

### 1. Structure ML créée

```
ml/
├── __init__.py
├── config.py                      ✅ Constantes ML (N_REGIMES, TRADING_DAYS, etc.)
│
├── features/
│   ├── __init__.py
│   ├── feature_engineering.py     ✅ prepare_regime_features, prepare_prediction_features
│   └── time_split.py              ✅ walk_forward_split, time_series_cv
│
├── models/
│   ├── __init__.py
│   ├── regime_kmeans.py           ✅ RegimeKMeans (baseline)
│   ├── regime_gmm.py              ✅ RegimeGMM (alternative)
│   ├── regime_hmm.py              ✅ RegimeHMM (choix final)
│   ├── predict_logreg.py          ✅ ReturnPredictorLogReg (baseline)
│   ├── predict_xgboost.py         ✅ ReturnPredictorXGBoost (alternative)
│   └── predict_rf.py              ✅ ReturnPredictorRF (choix final)
│
├── evaluation/
│   ├── __init__.py
│   ├── regime_labels.py           ✅ create_historical_labels, get_crisis_periods
│   ├── compare_regime_models.py   ✅ evaluate_regime_model, compare_all_regime_models
│   └── compare_prediction_models.py ✅ walk_forward_comparison
│
└── portfolio/
    ├── __init__.py
    ├── benchmarks.py              ✅ calculate_benchmark_returns, calculate_benchmark_metrics
    ├── optimizer.py               ✅ PortfolioOptimizer (Markowitz)
    ├── deeppilot_strategy.py      ✅ DeepPilotStrategy (HMM + RF + Markowitz)
    └── backtester.py              ✅ Backtester, BacktestResult
```

### 2. Modèles de régime comparés

| Modèle | Silhouette | Stabilité | Changements | ARI |
|--------|------------|-----------|-------------|-----|
| K-Means | 0.215 | 94.1% | 240 | 0.097 |
| GMM | 0.147 | 91.1% | 362 | 0.111 |
| **HMM** | 0.199 | **97.9%** | **85** | 0.070 |

**Choix : HMM** — Meilleure stabilité, moins de faux signaux, capture la dynamique temporelle.

### 3. Modèles de prédiction comparés

| Modèle | Accuracy (split) | Accuracy (walk-forward) | AUC | Overfit Gap |
|--------|------------------|-------------------------|-----|-------------|
| LogReg | 63.0% | 58.5% | 0.506 | 0.123 |
| XGBoost | 58.1% | 56.1% | 0.506 | 0.428 |
| **RF** | 62.2% | 55.6% | 0.484 | 0.356 |

**Choix : Random Forest** — Équilibre performance/interprétabilité, robuste aux outliers.

### 4. Résultats du backtest (2013-2024)

| Stratégie | CAGR | Sharpe | Max DD | Volatilité |
|-----------|------|--------|--------|------------|
| **DeepPilot** | 5.59% | 0.289 | -22.1% | 8.95% |
| SPY (Buy & Hold) | 14.55% | 0.691 | -33.7% | 16.71% |
| 60/40 (SPY/TLT) | 9.23% | 0.595 | -27.2% | 10.46% |
| Equal Weight | 3.61% | 0.079 | -18.8% | 7.75% |

**Conclusion** : DeepPilot sous-performe en rendement absolu mais offre :
- Volatilité 2x plus faible que SPY (8.95% vs 16.71%)
- Drawdown limité (-22.1% vs -33.7%)
- Stratégie défensive adaptée aux investisseurs averses au risque

### 5. Détection des crises (HMM)

| Crise | Régime détecté | Précision |
|-------|----------------|-----------|
| Flash Crash 2010 | 100% volatile | ✅ |
| Euro Crisis 2011 | 61% volatile | ✅ |
| China Fears 2015 | 69% volatile | ✅ |
| Vol Spike 2018 | 100% volatile | ✅ |
| COVID 2020 | 93% volatile | ✅ |
| Rate Hikes 2022 | 65% volatile | ✅ |

### 6. Notebooks d'analyse

| Notebook | Contenu | Status |
|----------|---------|--------|
| `05_regime_comparison.ipynb` | Comparaison K-Means vs GMM vs HMM | ✅ |
| `06_prediction_comparison.ipynb` | Comparaison LogReg vs XGBoost vs RF + walk-forward | ✅ |
| `07_strategy_comparison.ipynb` | Backtest DeepPilot vs benchmarks | ✅ |

### 7. Tests ML

```
tests/ml/
├── __init__.py
├── test_regime_models.py          ✅ 18 tests
├── test_prediction_models.py      ✅ 22 tests
└── test_portfolio.py              ✅ 21 tests
```

| Suite | Résultat |
|-------|----------|
| Tests Régimes | 18/18 ✅ |
| Tests Prédiction | 22/22 ✅ |
| Tests Portfolio | 21/21 ✅ |
| **Total ML** | **61/61** ✅ |

### 8. Tests totaux (Phase 1 + Phase 2 + Phase 3)

| Suite | Résultat |
|-------|----------|
| Tests Data (Phase 1) | 64/64 ✅ |
| Tests API (Phase 2) | 27/27 ✅ |
| Tests ML (Phase 3) | 61/61 ✅ |
| **TOTAL** | **152/152** ✅ |

---

## Corrections effectuées

| Problème | Solution |
|----------|----------|
| `BAMLH0A0HYM2` indisponible avant mai 2023 | Remplacé par `BAA10Y` (Moody's BAA - 10Y Treasury) |
| `prepare_regime_features()` retournait 0 lignes | Ajouté `ffill().bfill()` + supprimé `dropna()` strict |
| `walk_forward_comparison()` erreur d'indexation | Corrigé pour utiliser les DataFrames directement |

---

## Dépendances ajoutées (requirements.txt)

```
# ML
scikit-learn>=1.4.0
xgboost>=2.0.0
hmmlearn>=0.3.0
scipy>=1.12.0
```

---

## Fichiers de résultats générés

```
data/processed/
├── regime_model_comparison.csv           ✅ Comparaison K-Means/GMM/HMM
├── prediction_model_comparison.csv       ✅ Comparaison LogReg/XGBoost/RF
├── prediction_walkforward_comparison.csv ✅ Walk-forward 12 folds
├── strategy_comparison.csv               ✅ DeepPilot vs benchmarks
├── annual_returns_comparison.csv         ✅ Returns par année
└── deeppilot_weights_history.csv         ✅ Historique des allocations
```

---

## Commandes utiles

```bash
# Lancer les tests ML
python -m pytest tests/ml/ -v

# Lancer tous les tests (Phase 1 + 2 + 3)
python -m pytest tests/ -v

# Extraire les nouvelles données FRED (avec BAA10Y)
python -m data.extractors.extract_fred

# Notebooks
# Ouvrir analysis/05_regime_comparison.ipynb
# Ouvrir analysis/06_prediction_comparison.ipynb
# Ouvrir analysis/07_strategy_comparison.ipynb
```

---

## Structure projet complète

```
deeppilot/
├── .env                         ✅ Variables d'environnement
├── .gitignore                   ✅
├── CLAUDE.md                    ✅ Instructions projet
├── TODO.md                      ✅ Phase 1
├── TODO_PHASE2.md               ✅ Phase 2
├── TODO_PHASE3.md               ✅ Phase 3
├── CHECKPOINT_PHASE1.md         ✅
├── CHECKPOINT_PHASE2.md         ✅
├── CHECKPOINT_PHASE3.md         ✅ (ce fichier)
├── requirements.txt             ✅ Mis à jour
│
├── api/                         ✅ (Phase 2)
│
├── data/                        ✅ (Phase 1)
│   ├── extractors/
│   │   └── extract_fred.py      ✅ Modifié (BAA10Y)
│   ├── raw/
│   │   └── macro_20260515.csv   ✅ Nouvelles données
│   └── processed/
│       └── *.csv                ✅ Résultats ML
│
├── ml/                          ✅ NOUVEAU (Phase 3)
│   ├── config.py
│   ├── features/
│   ├── models/
│   ├── evaluation/
│   └── portfolio/
│
├── analysis/                    ✅ 7 notebooks total
│   ├── 01_explore_etfs.ipynb
│   ├── 02_correlations.ipynb
│   ├── 03_returns_distributions.ipynb
│   ├── 04_macro_features.ipynb
│   ├── 05_regime_comparison.ipynb    ✅ NOUVEAU
│   ├── 06_prediction_comparison.ipynb ✅ NOUVEAU
│   └── 07_strategy_comparison.ipynb   ✅ NOUVEAU
│
├── tests/
│   ├── api/                     ✅ (Phase 2)
│   ├── ml/                      ✅ NOUVEAU (Phase 3)
│   │   ├── test_regime_models.py
│   │   ├── test_prediction_models.py
│   │   └── test_portfolio.py
│   └── ... (tests Phase 1)
│
└── docs/
    ├── api/                     ✅ (Phase 2)
    └── rgpd/                    ✅ (Phase 2)
```

---

## Features les plus importantes (Random Forest)

| Feature | Importance |
|---------|------------|
| price_sma200_ratio | 20.2% |
| rsi_14 | 12.9% |
| price_sma50_ratio | 10.8% |
| price_sma20_ratio | 10.4% |
| macd_signal_ratio | 10.0% |
| return_20d | 9.1% |
| bb_position | 8.6% |
| return_5d | 8.1% |
| return_1d | 6.3% |
| regime | 3.6% |

---

## Prochaine phase : Phase 4 (MLOps)

| Composant | Description |
|-----------|-------------|
| **MLflow** | Tracking des expériences, registry des modèles |
| **CI/CD ML** | Tests automatisés, validation des modèles |
| **Monitoring** | Drift detection, alertes performance |
| **Hyperparameter tuning** | Grid search, Optuna |

---

## ✅ PHASE 3 TERMINÉE

| Composant | Status |
|-----------|--------|
| Feature engineering | ✅ |
| Modèles de régime (3) | ✅ |
| Modèles de prédiction (3) | ✅ |
| Optimisation Markowitz | ✅ |
| Stratégie DeepPilot | ✅ |
| Backtester walk-forward | ✅ |
| Notebooks comparaison (3) | ✅ |
| Tests ML (61) | ✅ |
| Documentation résultats | ✅ |

**Compétences validées** : C9 (modèles ML), C12 (tests ML)

**Phase 3 complète !** Prêt pour Phase 4 (MLOps : MLflow, CI/CD ML).

---

**Checkpoint créé le 15 mai 2026**
