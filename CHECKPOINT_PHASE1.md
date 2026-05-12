# DeepPilot — Checkpoint Phase 1

> **Date** : 6 mai 2026
> **Session** : Setup initial + Pipeline data complet

---

## Ce qui a été fait

### 1. Structure projet créée

```
deeppilot/
├── .env                     ✅ Configuré (Supabase, FRED, GCP, Mistral, Gemini)
├── .env.example             ✅
├── .gitignore               ✅
├── .python-version          ✅ (3.11)
├── pyproject.toml           ✅ (black, ruff, pytest config)
├── requirements.txt         ✅
├── README.md                ✅
├── CLAUDE.md                ✅ (instructions projet)
├── TODO.md                  ✅ (roadmap Phase 1)
│
├── data/
│   ├── __init__.py
│   ├── README.md            ✅
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── extract_yfinance.py   ✅ Testé, fonctionne
│   │   ├── extract_fred.py       ✅ Testé, fonctionne
│   │   ├── extract_files.py      ✅ Créé (pas encore utilisé)
│   │   └── extract_bigquery.py   ✅ Créé, connexion testée
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── aggregate.py          ✅ Testé, fonctionne
│   │   ├── cleaning_rules.py     ✅
│   │   └── load_to_db.py         ✅ Testé, fonctionne
│   ├── sql/
│   │   ├── README.md             ✅
│   │   ├── postgres/
│   │   │   ├── 01_init_schema.sql    ✅ Exécuté sur Supabase
│   │   │   ├── 02_join_prices_macro.sql
│   │   │   ├── 03_monthly_returns.sql
│   │   │   ├── 04_rolling_volatility.sql
│   │   │   └── 05_correlation_matrix.sql
│   │   └── bigquery/
│   │       ├── 01_partitioned_prices.sql
│   │       └── 02_features_aggregation.sql
│   ├── raw/                      ✅ Données téléchargées
│   │   └── prices_20260506.csv   (767 KB, 10 ETF, 4109 jours)
│   │   └── macro_20260506.csv    (250 KB, 9 séries)
│   └── processed/
│       └── dataset_20260506.csv  ✅ (148 colonnes, 4109 lignes)
│
├── tests/
│   ├── __init__.py
│   ├── test_extract_yfinance.py  ✅
│   ├── test_extract_fred.py      ✅
│   ├── test_extract_files.py     ✅
│   ├── test_extract_bigquery.py  ✅
│   ├── test_aggregate.py         ✅
│   └── test_data_quality.py      ✅
│
├── docs/
│   ├── data_sources.md           ✅
│   ├── database_schema.md        ✅
│   └── rgpd/
│       ├── registre_traitements.md   ✅ (placeholder)
│       └── procedures_tri.md         ✅ (placeholder)
│
└── analysis/                     ⏳ À faire (notebooks)
```

### 2. Comptes & Services configurés

| Service | Status | Notes |
|---------|--------|-------|
| **Supabase** | ✅ Connecté | Projet `wkmikqcrjbfiaozrvmvm` |
| **FRED API** | ✅ Clé configurée | 9 séries macro téléchargées |
| **GCP/BigQuery** | ✅ Connecté | Projet `n8n-credentials-475110`, dataset `deeppilot` |
| **Mistral API** | ✅ Clé configurée | Pour Phase 5 (sentiment) |
| **Google AI (Gemini)** | ✅ Clé configurée | Backup IA |

### 3. Données extraites

#### Prix ETF (yfinance)
- **Période** : 2010-01-04 → 2026-05-05
- **Tickers** : SPY, EFA, EEM, TLT, HYG, GLD, VNQ, SH, URTH, QQQ
- **Lignes** : 4109 jours de trading
- **Fichier** : `data/raw/prices_20260506.csv`

#### Indicateurs Macro (FRED)
- **Séries** : VIX, credit_spread_hy, yield_curve_10y2y, t3mo, t10y, wti_oil, usd_eur, unemployment, cpi
- **Lignes** : 4330 (daily + monthly forward-filled)
- **Fichier** : `data/raw/macro_20260506.csv`

### 4. Pipeline exécuté

#### Agrégation (`aggregate.py`)
- Fusion prix + macro
- Nettoyage (forward-fill, détection outliers)
- **148 colonnes** calculées dont :
  - Returns : 1d, 5d, 20d, 60d (simples + log)
  - Volatilité : 20d, 60d (annualisée)
  - Indicateurs techniques : SMA 20/50/200, RSI 14, MACD, Bollinger Bands
- **Outliers détectés** : COVID mars 2020, avril 2025
- **Fichier** : `data/processed/dataset_20260506.csv`

### 5. Base de données Supabase

#### Tables créées et remplies

| Table | Lignes | Description |
|-------|--------|-------------|
| `etf` | 10 | Métadonnées des ETF |
| `price` | 40 579 | Prix historiques (ticker × date) |
| `macro_indicator` | 4 109 | Indicateurs macro par date |
| `feature` | 32 872 | Features calculées (ticker × date) |

#### Vue créée
- `v_prices_with_macro` : jointure prix × macro

#### RLS
- **Désactivé** (pas d'utilisateurs en Phase 1)

---

## Ce qu'il reste à faire (Phase 1)

### Priorité haute
- [x] **Étape 3** : ~~Télécharger 1-2 fichiers CSV INSEE/BCE~~ ✅ Done (insee_inflation_eu.csv, ecb_main_refinancing_rate.csv)
- [x] **Étape 4** : ~~Charger les prix dans BigQuery~~ ✅ Done (40579 lignes dans prices_simple)
- [x] **Étape 8** : ~~Créer les 4 notebooks d'analyse exploratoire~~ ✅ Done

### Priorité moyenne
- [ ] **Étape 7** : Tester les requêtes SQL documentées
- [ ] **Étape 10** : Lancer pytest avec couverture > 70%

### Priorité basse
- [ ] Nettoyer les PerformanceWarning dans `aggregate.py`
- [ ] Ajouter plus de séries FRED si `credit_spread_hy` reste vide

---

## Commandes utiles

```bash
# Activer l'environnement
cd C:\Users\User\OneDrive\Desktop\deepilot
# (si venv créé) .venv\Scripts\activate

# Relancer le pipeline complet
python -m data.extractors.extract_yfinance
python -m data.extractors.extract_fred
python -m data.pipeline.aggregate
python -m data.pipeline.load_to_db

# Lancer les tests
pytest tests/ -v

# Vérifier le formatage
black data/ tests/ --check
ruff check data/ tests/
```

---

## Variables d'environnement (.env)

```
SUPABASE_URL=https://wkmikqcrjbfiaozrvmvm.supabase.co
SUPABASE_KEY=***
SUPABASE_DB_URL=postgresql://postgres:***@db.wkmikqcrjbfiaozrvmvm.supabase.co:5432/postgres

FRED_API_KEY=***

GOOGLE_APPLICATION_CREDENTIALS=C:\Users\User\OneDrive\Desktop\deepilot\credentials.json
GCP_PROJECT_ID=n8n-credentials-475110

MISTRAL_API_KEY=***
GOOGLE_AI_API_KEY=***
```

---

## Prochaine session

Reprendre à :
1. Télécharger fichier INSEE (inflation EU) → `data/raw/files/`
2. Charger dans BigQuery
3. Créer les notebooks d'analyse

---

**Checkpoint créé le 6 mai 2026 à ~20:45**
**Mis à jour le 6 mai 2026 à ~21:30**

---

## ✅ PHASE 1 TERMINÉE

| Composant | Status |
|-----------|--------|
| Setup environnement | ✅ |
| Extraction yfinance | ✅ 10 ETF, 4109 jours |
| Extraction FRED | ✅ 9 séries macro |
| Extraction fichiers CSV | ✅ INSEE + BCE |
| BigQuery | ✅ 40579 lignes |
| Pipeline agrégation | ✅ 148 colonnes |
| Supabase | ✅ 77k+ lignes, 4 tables |
| Requêtes SQL | ✅ 5 Postgres + 2 BigQuery |
| Notebooks analyse | ✅ 4 notebooks + conclusions |
| Documentation | ✅ |
| Tests pytest | ✅ 64 passed |

**Phase 1 complète !** Prêt pour Phase 2 (API REST data + RGPD).
