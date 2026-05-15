# DeepPilot — TODO Phase 3 : Modèles ML avec comparaisons

> **Phase actuelle : Phase 3 — TERMINÉE**
> Focus : développer les modèles ML avec comparaisons rigoureuses entre algorithmes.
> Compétences visées : C9 (modèles ML), C12 (tests ML)

### Fix important appliqué
- Série FRED `BAMLH0A0HYM2` (High Yield Spread) indisponible avant mai 2023
- Remplacée par `BAA10Y` (Moody's BAA - 10Y Treasury) avec historique complet depuis 2010
- Feature engineering amélioré avec `ffill().bfill()` pour éviter les NaN

---

## ÉTAPE 0 — Setup ML [TERMINÉ]

### 0.1 Nouvelles dépendances

- [x] Ajouter au `requirements.txt` :
```
# ML
scikit-learn>=1.4.0
xgboost>=2.0.0
hmmlearn>=0.3.0
scipy>=1.12.0
```

- [x] `pip install -r requirements.txt`

### 0.2 Structure dossiers ML

- [x] Créer `ml/__init__.py`
- [x] Créer `ml/config.py` (constantes ML)
- [x] Créer `ml/features/__init__.py`
- [x] Créer `ml/models/__init__.py`
- [x] Créer `ml/evaluation/__init__.py`
- [x] Créer `ml/portfolio/__init__.py`

---

## ÉTAPE 1 — Préparation des features ML [TERMINÉ]

### 1.1 Feature engineering

- [x] Créer `ml/features/feature_engineering.py` :
  - [x] `prepare_regime_features(df)` : VIX z-score, spread crédit, yield curve, return SPY, volatilité
  - [x] `prepare_prediction_features(df, ticker, regime_series)` : lagged returns, SMA ratios, RSI, MACD, Bollinger, régime
  - [x] `create_target(df, ticker, horizon)` : target binaire

### 1.2 Split temporel

- [x] Créer `ml/features/time_split.py` :
  - [x] `walk_forward_split(df, train_years, test_years)` : générateur de splits
  - [x] `time_series_cv(n_samples, n_splits)` : wrapper TimeSeriesSplit
  - [x] `assert_no_lookahead(train_dates, test_dates)` : validation anti look-ahead

### 1.3 Tests

- [x] Créer `tests/ml/__init__.py`
- [ ] Créer `tests/ml/test_features.py` (à faire)

---

## ÉTAPE 2 — Modèle 1 : Détection de régime (comparaison) [TERMINÉ]

### 2.1 Baseline : K-Means

- [x] Créer `ml/models/regime_kmeans.py` :
  - [x] Classe `RegimeKMeans` avec `fit()`, `predict()`, `get_regime_stats()`

### 2.2 Alternative : GMM

- [x] Créer `ml/models/regime_gmm.py` :
  - [x] Classe `RegimeGMM` avec `fit()`, `predict()`, `predict_proba()`

### 2.3 Choix final : HMM

- [x] Créer `ml/models/regime_hmm.py` :
  - [x] Classe `RegimeHMM` avec `fit()`, `predict()`, `predict_proba()`, `get_transition_matrix()`

### 2.4 Labels historiques (ground truth)

- [x] Créer `ml/evaluation/regime_labels.py` :
  - [x] `create_historical_labels(df)` : règles bear/bull/volatile/stable
  - [x] `get_nber_recession_dates()` : périodes de récession
  - [x] `evaluate_regime_labels(predicted, historical)` : métriques ARI, NMI, accuracy

### 2.5 Comparaison des modèles de régime

- [x] Créer `ml/evaluation/compare_regime_models.py` :
  - [x] `evaluate_regime_model(model, X, y_true)` : silhouette, calinski, stabilité
  - [x] `compare_all_regime_models(X, y_true)` : compare K-Means, GMM, HMM
  - [x] `get_best_regime_model(X, y_true, metric)` : retourne le meilleur

### 2.6 Notebook comparaison régimes

- [x] Créer `analysis/05_regime_comparison.ipynb`
  - HMM choisi : stabilité 97.9%, seulement 85 changements
  - Détecte correctement les crises (COVID 93% volatile, 2022 65% volatile)

---

## ÉTAPE 3 — Modèle 2 : Prédiction de rendement (comparaison) [TERMINÉ]

### 3.1 Baseline : Logistic Regression

- [x] Créer `ml/models/predict_logreg.py` :
  - [x] Classe `ReturnPredictorLogReg` avec `fit()`, `predict()`, `predict_proba()`, `get_coefficients()`

### 3.2 Alternative : XGBoost

- [x] Créer `ml/models/predict_xgboost.py` :
  - [x] Classe `ReturnPredictorXGBoost` avec `fit()`, `predict()`, `predict_proba()`, `get_feature_importance()`

### 3.3 Choix final : Random Forest

- [x] Créer `ml/models/predict_rf.py` :
  - [x] Classe `ReturnPredictorRF` avec `fit()`, `predict()`, `predict_proba()`, `get_feature_importance()`

### 3.4 Comparaison des modèles de prédiction

- [x] Créer `ml/evaluation/compare_prediction_models.py` :
  - [x] `evaluate_prediction_model(model, X_train, y_train, X_test, y_test)` : accuracy, AUC, F1
  - [x] `compare_all_prediction_models(...)` : compare LogReg, XGBoost, RF
  - [x] `walk_forward_comparison(X, y)` : évaluation walk-forward
  - [x] `get_feature_importance_comparison(...)` : compare importance des features

### 3.5 Notebook comparaison prédictions

- [x] Créer `analysis/06_prediction_comparison.ipynb`
  - Walk-forward 12 folds : LogReg 58.5%, XGBoost 56%, RF 55.6%
  - Tous les modèles battent le hasard (50%)

---

## ÉTAPE 4 — Optimisation de portefeuille [TERMINÉ]

### 4.1 Stratégies benchmark

- [x] Créer `ml/portfolio/benchmarks.py` :
  - [x] `create_buy_hold_benchmark(df_returns, ticker)` : buy & hold
  - [x] `create_6040_benchmark(df_returns)` : 60/40 SPY/TLT
  - [x] `create_equal_weight_benchmark(df_returns)` : equal weight
  - [x] `calculate_benchmark_metrics(df_returns)` : Sharpe, CAGR, max DD, etc.

### 4.2 Optimisation Markowitz

- [x] Créer `ml/portfolio/optimizer.py` :
  - [x] Classe `PortfolioOptimizer` avec `optimize()`, `optimize_from_returns()`
  - [x] Contraintes : 5% <= w <= 25%, sum(w) = 1
  - [x] Calcul turnover et transaction costs
  - [x] Frontière efficiente

### 4.3 Stratégie DeepPilot

- [x] Créer `ml/portfolio/deeppilot_strategy.py` :
  - [x] Classe `DeepPilotStrategy` avec `fit()`, `rebalance()`, `compute_weights()`
  - [x] Intègre régime HMM + prédiction RF + optimisation Markowitz
  - [x] Ajustement des weights selon le régime

### 4.4 Backtester

- [x] Créer `ml/portfolio/backtester.py` :
  - [x] Classe `Backtester` avec `run()`, `compare_with_benchmarks()`
  - [x] `BacktestResult` dataclass avec returns, weights, trades, metrics
  - [x] Walk-forward avec réentraînement périodique
  - [x] Frais de transaction inclus

---

## ÉTAPE 5 — Comparaison finale des stratégies [TERMINÉ]

### 5.1 Évaluation complète

- [x] Comparaison intégrée dans le backtester

### 5.2 Notebook comparaison finale

- [x] Créer `analysis/07_strategy_comparison.ipynb`
  - DeepPilot : CAGR 5.59%, Sharpe 0.289, Max DD -22.1%
  - SPY : CAGR 14.55%, Sharpe 0.691, Max DD -33.7%
  - 60/40 : CAGR 9.23%, Sharpe 0.595, Max DD -27.2%
  - DeepPilot = stratégie défensive (vol 2x plus faible que SPY)

---

## ÉTAPE 6 — Tests ML [TERMINÉ]

### 6.1 Tests unitaires

- [x] Créer `tests/ml/test_regime_models.py` : 18 tests
- [x] Créer `tests/ml/test_prediction_models.py` : 22 tests
- [x] Créer `tests/ml/test_portfolio.py` : 21 tests

### 6.2 Tests d'intégration

- [ ] Créer `tests/ml/test_integration.py` (à faire si besoin)

### 6.3 Lancer les tests

- [x] `python -m pytest tests/ml/ -v` → **61 tests passent**
- [x] `python -m pytest` → **152 tests passent au total**

---

## ÉTAPE 7 — Documentation ML [TERMINÉ]

### 7.1 Documentation technique

- [x] Documentation intégrée dans les notebooks (05, 06, 07)
- [x] Conclusions et justifications dans chaque notebook

### 7.2 Rapport de comparaison

- [x] Résultats sauvegardés dans `data/processed/`:
  - `regime_model_comparison.csv`
  - `prediction_model_comparison.csv`
  - `prediction_walkforward_comparison.csv`
  - `strategy_comparison.csv`
  - `annual_returns_comparison.csv`
  - `deeppilot_weights_history.csv`

---

## ÉTAPE 8 — Commit final Phase 3 [À FAIRE]

- [ ] Commit : "feat: ML models with comparisons (HMM, RF, strategies)"
- [ ] Tag Git : `v0.3.0-ml-phase`
- [ ] Push

---

## ✅ Definition of Done — Phase 3

La Phase 3 est terminée quand :

- [x] 3 modèles de régime comparés (K-Means, GMM, HMM)
- [x] 3 modèles de prédiction comparés (LogReg, XGBoost, RF)
- [x] 4 stratégies backtestées (Buy&Hold SPY, 60/40, EqualWeight, DeepPilot)
- [x] Notebooks de comparaison avec conclusions (05, 06, 07)
- [x] Tests ML passent (61 tests, couverture OK)
- [x] Documentation des choix avec justifications (dans notebooks)
- [x] Métriques : Sharpe, CAGR, Max DD documentées dans le code

**Compétences validées en Phase 3** : C9 (modèles ML), C12 (tests ML)

### Résultats finaux

| Stratégie | CAGR | Sharpe | Max DD |
|-----------|------|--------|--------|
| DeepPilot | 5.59% | 0.289 | -22.1% |
| SPY | 14.55% | 0.691 | -33.7% |
| 60/40 | 9.23% | 0.595 | -27.2% |
| Equal Weight | 3.61% | 0.079 | -18.8% |

**Conclusion** : DeepPilot sous-performe en rendement absolu mais offre une volatilité 2x plus faible et un drawdown limité. Stratégie défensive adaptée aux investisseurs averses au risque.

---

## Progression

| Module | Fichiers | Tests | Status |
|--------|----------|-------|--------|
| ml/config | 1 | - | ✅ |
| ml/features | 2 | - | ✅ |
| ml/models | 6 | 40 | ✅ |
| ml/evaluation | 3 | - | ✅ |
| ml/portfolio | 4 | 21 | ✅ |
| analysis/ | 3 notebooks | - | ✅ |
| **Total** | **16 fichiers + 3 notebooks** | **61 tests** | ✅ |

---

## 🚫 Hors scope Phase 3

- MLflow tracking (Phase 4)
- Hyperparameter tuning automatisé (Phase 4)
- Sentiment analysis Mistral (Phase 5)
- Déploiement des modèles (Phase 6-7)
