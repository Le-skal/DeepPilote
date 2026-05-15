# Conclusions de l'analyse exploratoire — DeepPilot

## Résumé des 4 notebooks

### 01 - Exploration des ETF
- **SPY** : Meilleur Sharpe ratio (~0.6), return ~10-12% annualisé
- **TLT** : Performance modeste mais décorrélée, utile en crise
- **GLD** : Excellent diversificateur, faible corrélation avec tout
- **SH** : Performance négative long terme, mais hedge efficace en bear market
- **Max Drawdown** : -34% sur SPY (COVID mars 2020)

### 02 - Corrélations
- **SPY/SH** : -0.99 (inverse parfait)
- **SPY/TLT** : -0.3 à -0.5 (flight to quality)
- **Actions entre elles** : +0.7 à +0.9 (diversification géo limitée)
- **En crise** : Corrélations actions augmentent, TLT devient plus anti-corrélé

### 03 - Distributions
- **Non-normalité** : Tous les ETF rejettent l'hypothèse de normalité
- **Skewness négative** : Pertes extrêmes plus fréquentes
- **Fat tails** : Événements 3σ sont 5-10x plus fréquents que prévu
- **Implication** : Markowitz sous-estime le risque

### 04 - Features macro
- **VIX** : Anti-corrélé SPY (-0.7), pic 80+ en mars 2020
- **Yield Curve** : Inversée 2022-2023, prédicteur de récession
- **Régimes** : Bull (VIX<15), Stress (VIX>30) clairement identifiables

---

## Features prometteuses pour le ML (Phase 3)

### Pour le modèle HMM (détection de régime)
1. VIX niveau et variation
2. Yield curve 10Y-2Y
3. Volatilité réalisée 20j
4. Returns SPY 20j (momentum)
5. Credit spread HY

### Pour le modèle Random Forest (prédiction rendement)
1. Tous les indicateurs techniques (SMA, RSI, MACD, Bollinger)
2. Returns laggés (1d, 5d, 20d)
3. Volatilité rolling
4. Régime HMM (output modèle 1)
5. Interactions VIX × momentum

---

## Observations clés pour le portefeuille

| Insight | Implication |
|---------|-------------|
| Corrélations augmentent en crise | Diversification moins efficace quand on en a le plus besoin |
| TLT anti-corrélé en stress | Garder une allocation bonds même si rendements faibles |
| GLD décorrélé | Inclure systématiquement dans le portefeuille |
| SH perd de la valeur long terme | Utiliser uniquement en bear market détecté |
| Fat tails | Ne pas se fier uniquement à la volatilité, utiliser CVaR |

---

## Résultats Phase 3 — Modèles ML

### HMM (Détection de régime)
- **4 régimes** détectés : bull, bear, volatile, stable
- **Stabilité** : 97.9% (transitions peu fréquentes)
- **Validation** : Détecte correctement COVID-2020, crise 2022

### Random Forest (Prédiction)
- **Accuracy** : 55-58%
- **AUC** : ~0.51
- **Features importantes** : VIX, momentum 20j, yield curve

### Backtest DeepPilot (2010-2025)
| Métrique | DeepPilot | SPY B&H | 60/40 |
|----------|-----------|---------|-------|
| CAGR | 5.59% | 12.8% | 8.2% |
| Volatilité | 8.5% | 15.2% | 9.8% |
| Sharpe | 0.41 | 0.71 | 0.62 |
| Max Drawdown | -17.2% | -33.7% | -22.4% |

> DeepPilot est une stratégie défensive : volatilité et drawdown réduits.

---

## Résultats Phase 4 — MLOps

### Drift Detection
- **Yield curve** : PSI = 5.49 (drift majeur post-2022, hausse des taux)
- **Volatilité SPY** : PSI = 0.31 (drift modéré)
- **Autres features** : PSI < 0.1 (stables)

### MLflow Tracking
- 4 expériences configurées (HMM, RF, backtest, production)
- Model registry avec versioning
- CI/CD GitHub Actions pour validation automatique

---

*Analyse réalisée sur données 2010-2026 (16 ans, ~4100 jours de trading)*
*Mise à jour : 15 mai 2026 (Phase 4 complète)*
