# Data — DeepPilot

Ce dossier contient tout le code et les données liées au pipeline de données du projet.

## Structure

```
data/
├── extractors/              # Scripts d'extraction depuis les sources
│   ├── extract_yfinance.py  # Prix ETF via Yahoo Finance
│   ├── extract_fred.py      # Données macro via FRED API
│   ├── extract_files.py     # Fichiers CSV (INSEE, BCE)
│   └── extract_bigquery.py  # Requêtes BigQuery
│
├── pipeline/                # Pipeline de traitement
│   ├── aggregate.py         # Fusion et calcul des features
│   ├── cleaning_rules.py    # Règles de nettoyage centralisées
│   └── load_to_db.py        # Chargement vers Supabase
│
├── sql/                     # Requêtes SQL
│   ├── postgres/            # Requêtes Supabase
│   └── bigquery/            # Requêtes BigQuery
│
├── raw/                     # Données brutes (gitignored)
│   └── files/               # Fichiers CSV manuels
│
└── processed/               # Données nettoyées (gitignored)
```

## Sources de données

| Source | Type | Données | Fréquence |
|--------|------|---------|-----------|
| Yahoo Finance | API | Prix ETF (adjusted close) | Daily |
| FRED | API | Indicateurs macro (VIX, taux, spreads) | Daily/Monthly |
| INSEE | Fichier CSV | Inflation EU | Monthly |
| BCE/ECB | Fichier CSV | Taux directeur | Variable |
| BigQuery | Base | Agrégations volumineuses | - |

## Installation

```bash
# Environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows

# Dépendances
pip install -r requirements.txt

# Variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API
```

## Utilisation

### 1. Extraction des données brutes

```bash
# Prix ETF
python -m data.extractors.extract_yfinance

# Données macro FRED
python -m data.extractors.extract_fred

# Fichiers CSV (placer les fichiers dans data/raw/files/ d'abord)
python -m data.extractors.extract_files
```

### 2. Pipeline d'agrégation

```bash
# Fusionne prix + macro, nettoie, calcule les features
python -m data.pipeline.aggregate
```

### 3. Chargement en base

```bash
# Charge dans Supabase (nécessite schéma créé)
python -m data.pipeline.load_to_db
```

### Pipeline complet

```bash
# Dans l'ordre :
python -m data.extractors.extract_yfinance
python -m data.extractors.extract_fred
python -m data.pipeline.aggregate
python -m data.pipeline.load_to_db
```

## Fichiers produits

| Fichier | Emplacement | Description |
|---------|-------------|-------------|
| `prices_YYYYMMDD.csv` | `data/raw/` | Prix bruts des ETF |
| `macro_YYYYMMDD.csv` | `data/raw/` | Indicateurs macro bruts |
| `dataset_YYYYMMDD.csv` | `data/processed/` | Dataset final avec features |

## Variables d'environnement requises

```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJxxx
SUPABASE_DB_URL=postgresql://postgres:xxx@db.xxx.supabase.co:5432/postgres

# FRED API
FRED_API_KEY=xxx

# Google Cloud (BigQuery)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GCP_PROJECT_ID=your-project-id
```

## Tests

```bash
# Tous les tests
pytest tests/ -v

# Tests spécifiques
pytest tests/test_extract_yfinance.py -v
pytest tests/test_data_quality.py -v

# Avec couverture
pytest tests/ --cov=data --cov-report=html
```

## Règles de nettoyage

Voir `data/pipeline/cleaning_rules.py` pour les détails.

- **Valeurs manquantes** : forward-fill si gap ≤ 5 jours, suppression sinon
- **Outliers** : flaggés (returns > |10%|) mais non supprimés
- **Index temporel** : doit être strictement croissant, sans doublons

## Features calculées

| Feature | Description | Période |
|---------|-------------|---------|
| `{ticker}_ret_1d` | Return simple 1 jour | 1 jour |
| `{ticker}_ret_20d` | Return simple 20 jours | 20 jours |
| `{ticker}_logret_1d` | Log return 1 jour | 1 jour |
| `{ticker}_vol_20d` | Volatilité annualisée | 20 jours rolling |
| `{ticker}_sma_20/50/200` | Moyennes mobiles | 20/50/200 jours |
| `{ticker}_rsi_14` | RSI | 14 jours |
| `{ticker}_macd` | MACD | 12/26/9 |
| `{ticker}_bb_position` | Position Bollinger | 20 jours |

## Troubleshooting

### yfinance rate limiting
Si erreur `Too Many Requests`, attendre quelques minutes ou réduire la période.

### FRED API key invalid
Vérifier que `FRED_API_KEY` est bien défini dans `.env`.

### Supabase connection refused
Vérifier que l'IP n'est pas bloquée dans les settings Supabase (Database → Connection Pooling).

### BigQuery permission denied
Vérifier que le service account a les rôles `BigQuery Data Editor` et `BigQuery Job User`.
