# DeepPilot

Copilote d'allocation d'actifs qui investit dans un panier de 8 ETF diversifiés avec réallocation mensuelle.

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
│   ├── extractors/     # Scripts d'extraction
│   ├── pipeline/       # Agrégation et nettoyage
│   ├── sql/            # Requêtes SQL
│   ├── raw/            # Données brutes (gitignored)
│   └── processed/      # Données nettoyées
├── analysis/           # Notebooks d'exploration
├── tests/              # Tests unitaires
└── docs/               # Documentation
```

## Disclaimer

Ce projet est purement éducatif. Il ne constitue pas un conseil en investissement au sens de l'article L321-1 du Code monétaire et financier.

---

Projet de fin d'études Bachelor Data & IA — ECE Paris
