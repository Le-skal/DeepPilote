# DeepPilot

Copilote d'allocation d'actifs utilisant le Machine Learning pour investir dans un panier de 8 ETF diversifiés avec réallocation mensuelle.

## Objectif

Battre les benchmarks passifs (Buy & Hold MSCI World, 60/40 classique, NASDAQ 100, S&P 500) en tenant compte des frais de transaction, sur la période 2010-2025.

## Univers d'investissement

| Ticker | Nom | Classe d'actifs |
|--------|-----|-----------------|
| SPY | SPDR S&P 500 ETF | Actions US large cap |
| EFA | iShares MSCI EAFE | Actions développées hors US |
| EEM | iShares MSCI Emerging Markets | Actions émergents |
| TLT | iShares 20+ Year Treasury Bond | Obligations US longue durée |
| HYG | iShares iBoxx High Yield Corporate | Obligations corporate HY |
| GLD | SPDR Gold Shares | Or |
| VNQ | Vanguard Real Estate ETF | REIT US |
| SH | ProShares Short S&P 500 | Inverse S&P 500 |

## Modèles ML

- **HMM (Hidden Markov Model)** : Détection de 4 régimes de marché (bull, bear, volatile, stable)
- **Random Forest** : Prédiction du signe des rendements à 1 mois
- **Optimisation Markowitz** : Allocation de portefeuille avec contraintes

## Installation

```bash
# Cloner le repo
git clone <url>
cd deeppilot

# Créer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API
```

## Structure du projet

```
deeppilot/
├── data/
│   ├── extractors/     # Scripts d'extraction (yfinance, FRED, BigQuery)
│   ├── pipeline/       # Agrégation et nettoyage
│   ├── sql/            # Requêtes SQL (Postgres, BigQuery)
│   └── processed/      # Données nettoyées
├── ml/
│   ├── models/         # Modèles ML (HMM, GMM, K-Means, RF, XGBoost)
│   ├── features/       # Feature engineering
│   ├── portfolio/      # Optimisation et backtesting
│   └── evaluation/     # Métriques et comparaisons
├── mlops/
│   ├── tracking.py     # MLflow tracking
│   ├── registry.py     # Model registry
│   └── monitoring.py   # Drift detection
├── api/                # API FastAPI (RGPD compliant)
├── analysis/           # Notebooks d'exploration (01-09)
├── tests/              # Tests unitaires (182 tests)
└── docs/               # Documentation
```

## Lancer les tests

```bash
# Tous les tests
python -m pytest tests/ -v

# Tests ML uniquement
python -m pytest tests/ml/ -v

# Tests MLOps
python -m pytest tests/mlops/ -v
```

## MLflow UI

```bash
cd deeppilot
python -m mlflow ui --port 5000
# Ouvrir http://localhost:5000
```

## Résultats

### Performances du portefeuille DeepPilot (2010-2025)

| Métrique | DeepPilot | SPY (B&H) | 60/40 |
|----------|-----------|-----------|-------|
| CAGR | 5.59% | 12.8% | 8.2% |
| Volatilité | 8.5% | 15.2% | 9.8% |
| Sharpe | 0.41 | 0.71 | 0.62 |
| Max Drawdown | -17.2% | -33.7% | -22.4% |

> DeepPilot est une stratégie défensive : volatilité et drawdown réduits, au prix d'un rendement absolu inférieur.

## Tests

- **182 tests** passent
- Couverture : data, ML, MLOps, API

## Disclaimer

Ce projet est purement éducatif. Il ne constitue pas un conseil en investissement au sens de l'article L321-1 du Code monétaire et financier.

---

Projet de fin d'études Bachelor Data & IA — ECE Paris (2026)
