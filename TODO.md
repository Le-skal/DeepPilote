# DeepPilot — TODO Phase 1 : Data + Analyse exploratoire

> **Phase actuelle : Phase 1 uniquement.**
> On ne fait PAS l'API, ni les modèles ML, ni l'app pour l'instant.
> Focus : collecter, nettoyer, charger en BDD, analyser. C'est tout.

> **Mode de travail** : coche les tâches dans l'ordre. Chaque section dépend des précédentes.

---

## ÉTAPE 0 — Setup environnement (avant tout)

### 0.1 Comptes et accès

- [ ] Créer compte **Supabase** (free tier) → noter URL + anon key + service_role key
- [ ] Créer projet Supabase nommé `deeppilot`
- [ ] Récupérer la connection string PostgreSQL (Settings → Database)
- [ ] Créer compte **FRED API** sur https://fred.stlouisfed.org/docs/api/api_key.html → noter API key
- [ ] Créer projet **Google Cloud** + activer BigQuery → télécharger service account JSON
- [ ] Créer compte **GitHub** repo `deeppilot` (privé pour l'instant)

### 0.2 Setup local

- [ ] Cloner le repo en local
- [ ] Créer environnement Python 3.11 (`python -m venv .venv` ou pyenv/conda)
- [ ] Activer l'environnement
- [ ] Créer `.python-version` avec `3.11`
- [ ] Créer `requirements.txt` avec les dépendances de base (voir 0.3)
- [ ] `pip install -r requirements.txt`
- [ ] Créer `.env.example` (cf. CLAUDE.md section 7)
- [ ] Créer `.env` local avec les vraies valeurs (NE PAS COMMIT)
- [ ] Vérifier que `.env` est dans `.gitignore`

### 0.3 Dépendances initiales (requirements.txt)

```
# Data
pandas>=2.2.0
numpy>=1.26.0
yfinance>=0.2.40
fredapi>=0.5.2
google-cloud-bigquery>=3.20.0
python-dotenv>=1.0.0

# Database
psycopg2-binary>=2.9.9
sqlalchemy>=2.0.0
supabase>=2.4.0

# Analyse
matplotlib>=3.8.0
seaborn>=0.13.0
plotly>=5.20.0
jupyter>=1.0.0
ipykernel>=6.29.0

# Tests + qualité
pytest>=8.0.0
pytest-cov>=4.1.0
black>=24.0.0
ruff>=0.3.0
great-expectations>=0.18.0
```

### 0.4 Configuration outils

- [ ] Créer `pyproject.toml` avec config black (ligne 100) et ruff
- [ ] Créer `.gitignore` (Python standard + `.env`, `data/raw/*.csv`, `*.parquet`, `mlruns/`, `.venv/`)
- [ ] Premier commit : "chore: initial project setup"
- [ ] Push sur GitHub

### 0.5 Lecture obligatoire

- [ ] Lire `CLAUDE.md` en entier
- [ ] S'assurer que Claude Code a accès à `CLAUDE.md` au démarrage de chaque session

---

## ÉTAPE 1 — Extraction des données prix ETF (yfinance)

### 1.1 Script d'extraction

- [ ] Créer `data/extractors/__init__.py` (vide)
- [ ] Créer `data/extractors/extract_yfinance.py`
- [ ] Définir constante `ETF_TICKERS = ["SPY", "EFA", "EEM", "TLT", "HYG", "GLD", "VNQ", "SH"]`
- [ ] Définir constante `BENCHMARK_TICKERS = ["URTH", "QQQ"]` (MSCI World + NASDAQ 100)
- [ ] Fonction `download_etf_prices(tickers, start_date, end_date) -> pd.DataFrame`
  - Utilise `yfinance.download()`
  - Récupère uniquement la colonne "Close" (qui est l'adjusted close en yfinance >= 0.2.x)
  - Gère les erreurs réseau (try/except + retry simple)
  - Logger les tickers téléchargés et les éventuels échecs
- [ ] Fonction `save_to_csv(df, filepath)` qui sauvegarde en `data/raw/prices_YYYYMMDD.csv`
- [ ] `if __name__ == "__main__"` : télécharge tous les tickers de 2010-01-01 à aujourd'hui
- [ ] Tester en local : exécuter le script, vérifier le CSV produit

### 1.2 Validation manuelle

- [ ] Ouvrir le CSV : vérifier que les 8 ETF + 2 benchmarks sont présents
- [ ] Vérifier qu'il y a ~3800 lignes (15 ans × 252 jours ouvrés)
- [ ] Vérifier qu'il n'y a pas de NaN suspects en début de période (SH lancé 2006, OK)
- [ ] Comparer 1-2 prix avec Yahoo Finance website pour valider

### 1.3 Tests unitaires

- [ ] Créer `tests/test_extract_yfinance.py`
- [ ] Test : `download_etf_prices` retourne un DataFrame avec colonnes attendues
- [ ] Test : index est de type DatetimeIndex
- [ ] Test : aucun ticker complètement vide

---

## ÉTAPE 2 — Extraction des données macro (FRED)

### 2.1 Identifier les séries FRED utiles

Liste des séries à récupérer (avec leurs codes FRED) :

- [ ] `VIXCLS` — VIX (CBOE Volatility Index)
- [ ] `BAMLH0A0HYM2` — High Yield credit spread (BofA)
- [ ] `T10Y2Y` — Courbe taux 10Y-2Y (yield curve)
- [ ] `DGS3MO` — 3-month Treasury (risk-free rate)
- [ ] `DGS10` — 10-year Treasury yield
- [ ] `DCOILWTICO` — WTI crude oil price (matières premières)
- [ ] `DEXUSEU` — USD/EUR exchange rate
- [ ] `UNRATE` — US unemployment rate (mensuel)
- [ ] `CPIAUCSL` — US CPI inflation (mensuel)

### 2.2 Script d'extraction

- [ ] Créer `data/extractors/extract_fred.py`
- [ ] Fonction `get_fred_series(series_ids, start_date, end_date) -> pd.DataFrame`
  - Utilise `fredapi.Fred(api_key=os.getenv("FRED_API_KEY"))`
  - Boucle sur les séries, concatène en DataFrame avec colonnes = noms de séries
  - Gère les fréquences différentes (daily / monthly) → on garde tout en daily, forward-fill pour les mensuelles
- [ ] Fonction `save_to_csv(df, filepath)` → `data/raw/macro_YYYYMMDD.csv`
- [ ] `if __name__ == "__main__"` : télécharge depuis 2010-01-01

### 2.3 Validation

- [ ] Vérifier que le VIX a des valeurs entre 9 et 90 (range historique réaliste)
- [ ] Vérifier que `T10Y2Y` est négatif sur 2022-2023 (inversion célèbre de la courbe)
- [ ] Vérifier que `DGS3MO` est ~5% sur 2023 (taux Fed après hausses)

### 2.4 Tests

- [ ] `tests/test_extract_fred.py` : tests basiques de structure du DataFrame

---

## ÉTAPE 3 — Extraction depuis fichiers (CSV INSEE/BCE)

> **But** : cocher la case "extraction depuis fichier de données" du référentiel C1.

### 3.1 Identifier 1-2 fichiers utiles

- [ ] Inflation EU mensuelle depuis INSEE (https://www.insee.fr) — télécharger CSV
- [ ] Taux directeur BCE depuis ECB Statistical Data Warehouse — télécharger CSV
- [ ] Sauvegarder les fichiers dans `data/raw/files/`

### 3.2 Script d'extraction

- [ ] Créer `data/extractors/extract_files.py`
- [ ] Fonction `load_csv_file(filepath, ...) -> pd.DataFrame`
  - Gère les encodages (`utf-8`, `latin-1`)
  - Gère les séparateurs (`,` vs `;` typique INSEE)
  - Parse les dates correctement
- [ ] Fonction de normalisation du format (colonnes harmonisées avec FRED)

### 3.3 Tests

- [ ] `tests/test_extract_files.py`

---

## ÉTAPE 4 — Setup BigQuery + extraction big data

> **But** : cocher la case "extraction depuis système big data" du référentiel C1.

### 4.1 Configuration GCP

- [ ] Activer l'API BigQuery dans la console GCP
- [ ] Créer un dataset `deeppilot` dans la région `EU` (RGPD)
- [ ] Créer une table `prices_history` dans BigQuery
- [ ] Charger les données prix CSV dans BigQuery (via console ou script)

### 4.2 Script d'extraction

- [ ] Créer `data/extractors/extract_bigquery.py`
- [ ] Fonction `query_bigquery(sql_query) -> pd.DataFrame`
  - Utilise `google.cloud.bigquery.Client`
  - Auth via service account JSON (path dans .env)
- [ ] Requête SQL d'exemple : agrégation mensuelle des prix avec partitioning par date

### 4.3 Validation

- [ ] Exécuter une requête simple, vérifier qu'on récupère bien des données

### 4.4 Tests

- [ ] `tests/test_extract_bigquery.py` (mock du client BQ pour ne pas appeler en vrai)

---

## ÉTAPE 5 — Pipeline d'agrégation et nettoyage

### 5.1 Script aggregate

- [ ] Créer `data/pipeline/__init__.py` (vide)
- [ ] Créer `data/pipeline/aggregate.py`
- [ ] Fonction `merge_prices_macro(prices_df, macro_df) -> pd.DataFrame`
  - Merge sur la colonne date
  - Forward-fill les features macro mensuelles
- [ ] Fonction `clean_data(df) -> pd.DataFrame`
  - Détection NaN : suppression si bloc > 5 jours, forward-fill sinon
  - Détection outliers (returns > |10%|) : flag dans une colonne `is_outlier` mais ne supprime pas
  - Vérification monotonie temporelle de l'index
- [ ] Fonction `compute_basic_features(df) -> pd.DataFrame`
  - Returns simples (1d, 5d, 20d, 60d)
  - Log returns
  - Volatilité réalisée (rolling 20 et 60 jours)
  - Indicateurs techniques basiques (SMA 20/50/200, RSI 14, MACD)
- [ ] `if __name__ == "__main__"` : lance le pipeline complet, sauve en `data/processed/`

### 5.2 Règles de nettoyage documentées

- [ ] Créer `data/pipeline/cleaning_rules.py` avec les règles centralisées
- [ ] Documenter chaque règle avec une docstring claire

### 5.3 Tests qualité données (great_expectations OU pytest simple)

- [ ] Créer `tests/test_data_quality.py`
- [ ] Test : pas de NaN dans colonnes critiques (close des 8 ETF) après cleaning
- [ ] Test : VIX entre 0 et 100
- [ ] Test : returns entre -50% et +50% (sécurité, pas de bug d'échelle)
- [ ] Test : index temporel strictement croissant

---

## ÉTAPE 6 — Schéma Supabase + chargement

### 6.1 Modélisation Merise

- [ ] Dessiner le MCD avec draw.io (`docs/database/mcd.png`)
- [ ] Entités principales :
  - `etf` (ticker PK, name, asset_class, inception_date)
  - `price` (ticker FK + date PK composite, open, high, low, close, volume)
  - `macro_indicator` (date PK, vix, credit_spread, yield_curve_10y2y, t3mo, ...)
  - `feature` (ticker FK + date PK composite, return_1d, return_20d, vol_20d, sma_20, rsi, ...)
- [ ] Dessiner le MPD (modèle physique avec types SQL) (`docs/database/mpd.png`)

### 6.2 Création des tables Supabase

- [ ] Créer `data/sql/postgres/01_init_schema.sql` avec les CREATE TABLE
- [ ] Définir les contraintes (PK, FK, NOT NULL, CHECK ranges)
- [ ] Créer les index sur (ticker, date) pour perf
- [ ] Exécuter le script via Supabase SQL Editor
- [ ] Vérifier les tables dans Supabase dashboard

### 6.3 Script de chargement

- [ ] Créer `data/pipeline/load_to_db.py`
- [ ] Fonction `connect_supabase() -> sqlalchemy.Engine`
- [ ] Fonction `load_etfs_metadata(engine)` (insertion des 8 ETF + 2 benchmarks)
- [ ] Fonction `load_prices(engine, df)` avec INSERT ON CONFLICT DO UPDATE (idempotent)
- [ ] Fonction `load_macro(engine, df)` idem
- [ ] Fonction `load_features(engine, df)` idem
- [ ] `if __name__ == "__main__"` : charge tout depuis `data/processed/`

### 6.4 Validation

- [ ] Vérifier le row count dans Supabase : ~30 000 lignes pour `price`, ~3800 pour `macro_indicator`
- [ ] Faire 2-3 requêtes SQL test depuis le SQL Editor

---

## ÉTAPE 7 — Requêtes SQL documentées (compétence C2)

### 7.1 Requêtes Postgres

- [ ] Créer `data/sql/postgres/02_join_prices_macro.sql` : jointure prix × macro sur date
- [ ] Créer `data/sql/postgres/03_monthly_returns.sql` : agrégation rendements mensuels par ETF
- [ ] Créer `data/sql/postgres/04_rolling_volatility.sql` : volatilité 20j roulante (window function)
- [ ] Créer `data/sql/postgres/05_correlation_matrix.sql` : matrice corrélations entre ETF

### 7.2 Requêtes BigQuery

- [ ] Créer `data/sql/bigquery/01_partitioned_prices.sql` : table partitionnée par date
- [ ] Créer `data/sql/bigquery/02_features_aggregation.sql` : agrégation features mensuelles

### 7.3 Documentation

- [ ] Créer `data/sql/README.md` qui explique chaque requête : but, choix, optimisations

---

## ÉTAPE 8 — Notebooks d'analyse exploratoire

### 8.1 Notebook 1 : exploration des prix

- [ ] Créer `analysis/01_explore_etfs.ipynb`
- [ ] Sections :
  - Chargement données depuis Supabase (lecture SQL)
  - Visualisation prix normalisés (base 100 au début) sur les 8 ETF
  - Statistiques descriptives par ETF (moyenne, vol, skew, kurtosis)
  - Distribution des returns par ETF (histogrammes)
  - Identification des périodes de stress (drawdowns visibles)

### 8.2 Notebook 2 : corrélations

- [ ] Créer `analysis/02_correlations.ipynb`
- [ ] Sections :
  - Matrice de corrélation des returns sur 15 ans
  - Heatmap (seaborn)
  - Corrélations roulantes 60 jours (montre comment les corrélations changent en crise)
  - Mise en évidence des paires anti-corrélées (SPY/TLT, SPY/SH)

### 8.3 Notebook 3 : distributions

- [ ] Créer `analysis/03_returns_distributions.ipynb`
- [ ] Sections :
  - Returns mensuels par ETF (boxplots)
  - Test de normalité (Jarque-Bera, Shapiro)
  - Skew + Kurtosis : montre que les returns ne sont PAS gaussiens (point clé pour défense Markowitz)

### 8.4 Notebook 4 : features macro

- [ ] Créer `analysis/04_macro_features.ipynb`
- [ ] Sections :
  - Évolution VIX 15 ans + zones de stress
  - Yield curve : périodes d'inversion → ~prédicteurs de récession
  - Spread crédit HY : pics historiques (2008, 2020)
  - Corrélations VIX vs returns SPY (négatives, classique)

### 8.5 Conclusions de l'analyse exploratoire

- [ ] Créer `analysis/CONCLUSIONS.md` avec les insights clés trouvés
- [ ] Identifier les régimes de marché candidats visibles à l'œil
- [ ] Lister les features qui semblent les plus prometteuses pour le ML futur

---

## ÉTAPE 9 — Documentation & RGPD

### 9.1 Documentation technique

- [ ] Compléter `data/README.md` avec : sources, structure, comment relancer le pipeline
- [ ] Créer `docs/data_sources.md` : description de chaque source (URL, fréquence, fiabilité)
- [ ] Créer `docs/database_schema.md` : description du schéma BDD avec MCD/MPD

### 9.2 RGPD (préparatoire — sera complété en phase 2 quand on aura les utilisateurs)

- [ ] Créer `docs/rgpd/registre_traitements.md` (vide pour l'instant, à remplir phase 2)
- [ ] Créer `docs/rgpd/procedures_tri.md` (idem)

---

## ÉTAPE 10 — Tests & qualité finale Phase 1

### 10.1 Couverture tests

- [ ] `pytest --cov=data tests/` → couverture > 70% sur le module data
- [ ] Tous les tests passent

### 10.2 Lint & format

- [ ] `black data/ tests/` → format OK
- [ ] `ruff check data/ tests/` → 0 erreur

### 10.3 Reproductibilité

- [ ] Vérifier qu'un nouveau clone + `pip install -r requirements.txt` + `.env` rempli + lancement pipeline → marche bout en bout
- [ ] Documenter la procédure dans `data/README.md`

### 10.4 Commit final Phase 1

- [ ] Commit : "feat: complete data pipeline phase 1"
- [ ] Tag Git : `v0.1.0-data-phase`
- [ ] Push

---

## ✅ Définition of Done — Phase 1

La Phase 1 est terminée quand :

- [x] Les 8 ETF + 2 benchmarks ont 15 ans de données prix dans Supabase
- [x] Les 9 séries FRED sont chargées dans Supabase
- [x] Au moins 1 fichier CSV (INSEE/BCE) est intégré
- [x] BigQuery a une table partitionnée fonctionnelle
- [x] Le pipeline d'agrégation produit un dataset propre et testé
- [x] 4 requêtes SQL Postgres + 2 BigQuery documentées
- [x] 4 notebooks d'analyse exploratoire produits
- [x] Tests passent et couvrent > 70% du code data
- [x] Documentation complète

**Compétences validées en Phase 1** : C1 (extraction multi-sources), C2 (requêtes SQL), C3 (agrégation/nettoyage), C4 (BDD partiel — sans RGPD complet)

---

## 🚫 Hors scope Phase 1 — pour mémoire

Tout ce qui suit est **explicitement reporté** aux phases ultérieures :

- API REST FastAPI (Phase 2)
- Auth utilisateurs Supabase (Phase 2)
- Modèles HMM + Random Forest (Phase 3)
- MLflow + DVC + CI/CD ML (Phase 4)
- Service Mistral / sentiment (Phase 5)
- Application Next.js (Phase 6)
- Monitoring Sentry / UptimeRobot (Phase 7)
- Rapports pro (Phase 8)

**Ne commence pas ces tâches avant d'avoir terminé Phase 1.**
