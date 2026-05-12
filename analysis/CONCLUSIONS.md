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

## Prochaines étapes (Phase 3)

1. **HMM** : Entraîner sur VIX + yield curve + vol réalisée → 4 états (bull/bear/volatile/stable)
2. **Random Forest** : Prédire signe du return mensuel → features techniques + régime
3. **Backtest** : Optimisation Markowitz conditionnelle au régime
4. **Validation** : Walk-forward, pas de look-ahead bias

---

*Analyse réalisée sur données 2010-2026 (16 ans, ~4100 jours de trading)*
