# DeepPilot — Documentation projet pour Claude Code

> **Lis ce fichier en premier à chaque session.**
> Il contient le contexte, les conventions, les contraintes et les décisions techniques du projet.
> Ne propose pas de solutions qui contredisent ce document sans m'avoir demandé d'abord.

---

## 1. Contexte du projet

### 1.1 Pitch

**DeepPilot** est un copilote d'allocation d'actifs qui investit dans un panier de 8 ETF diversifiés avec réallocation mensuelle, en utilisant deux modèles ML pour détecter le régime de marché et optimiser les poids.

### 1.2 Objectif business

Battre les benchmarks passifs (Buy & Hold MSCI World, 60/40 classique, NASDAQ 100, S&P 500) **en tenant compte des frais de transaction**, sur la période de backtest 2010-2025.

### 1.3 Contexte académique

Projet de fin d'études Bachelor Data & IA à l'ECE Paris (RNCP37827 - Développeur en Intelligence Artificielle, certif Simplon).
Le projet doit valider 21 compétences (C1 à C21) réparties sur 3 blocs :
- Bloc 1 (C1-C5) : collecte, stockage, mise à disposition des données
- Bloc 2 (C6-C13) : modèles et services d'IA
- Bloc 3 (C14-C21) : application intégrant un service d'IA

### 1.4 Auteur

Raphaël Martin (alias Skal / Le-skal), 3e année Bachelor Data & IA à l'ECE Paris, en alternance à L'AGEFI (Groupe Bey Médias) comme alternant data engineering.

---

## 2. Univers d'investissement — les 8 ETF

| Ticker | Nom complet | Classe d'actifs | Rôle dans le portefeuille |
|--------|-------------|-----------------|---------------------------|
| SPY | SPDR S&P 500 ETF Trust | Actions US large cap | Cœur actions US |
| EFA | iShares MSCI EAFE | Actions développées hors US | Diversification géographique |
| EEM | iShares MSCI Emerging Markets | Actions émergents | Beta émergent |
| TLT | iShares 20+ Year Treasury Bond | Obligations US longue durée | Anti-corrélation actions |
| HYG | iShares iBoxx High Yield Corporate | Obligations corporate haut rendement | Exposition spread crédit |
| GLD | SPDR Gold Shares | Or / matières premières | Refuge inflation et crise |
| VNQ | Vanguard Real Estate ETF | REIT US (immobilier coté) | Diversification actifs réels |
| SH | ProShares Short S&P 500 | Inverse S&P 500 (-1x) | Exposition à un marché baissier |

### Pourquoi ce choix

- Tous ont 15+ ans d'historique disponible (SH lancé 2006)
- Tous très liquides, données yfinance fiables
- Couvre 6 classes d'actifs distinctes (pas un panier mono-thématique)
- Corrélations variées entre eux = vraie matière à optimisation
- SH permet une exposition baissière réelle en bear market

### Benchmarks de comparaison

- Buy & Hold MSCI World (proxy : ACWI ou URTH)
- 60/40 classique (60% SPY + 40% TLT, rebalancé annuellement)
- NASDAQ 100 (QQQ)
- S&P 500 pur (SPY)

---

## 3. Stack technique

### 3.1 Décisions arrêtées

| Couche | Techno | Notes |
|--------|--------|-------|
| Langage principal | Python 3.11+ | |
| Manipulation data | pandas + numpy | |
| Source prix ETF | yfinance | API REST gratuite, pas de scraping |
| Source macro | fredapi (FRED, Federal Reserve) | VIX, courbe taux, spread crédit |
| Base de données | PostgreSQL via Supabase | Free tier 500MB, auth Google native, RGPD EU |
| Big data (pour C1) | Google BigQuery | Free tier 1TB requêtes/mois |
| Versioning data | DVC | Standard ML |
| ML classique | scikit-learn | Random Forest |
| HMM | hmmlearn | Détection de régime |
| Optimisation portefeuille | scipy.optimize.minimize | Plus simple que cvxpy, suffisant pour Markowitz contraint |
| Tracking ML | MLflow | Registry + métriques |
| API | FastAPI | À venir, pas dans la phase actuelle |
| Front | Next.js 14 + Tailwind + shadcn/ui | À venir, pas dans la phase actuelle |
| CI/CD | GitHub Actions | Gratuit |
| Monitoring | Sentry + UptimeRobot | Gratuit |
| Service IA tiers | Mistral API | Sentiment news, EU-based, pas cher |

### 3.2 Anti-bloat — ce qu'on n'utilise PAS

- ❌ Pas de scraping (consigne explicite)
- ❌ Pas de LSTM ou deep learning (LSTM sur prix d'actifs ne marche pas, prouvé par littérature académique + vidéos analysées)
- ❌ Pas de cvxpy (scipy.minimize suffit, plus simple)
- ❌ Pas d'Airflow / Prefect (overkill)
- ❌ Pas de Spark (BigQuery suffit)
- ❌ Pas de Redis (postgres + lru_cache suffisent)
- ❌ Pas de Docker en phase data-only (on l'introduira en phase API)

### 3.3 Hébergement (phase ultérieure)

| Service | Plan | Coût |
|---------|------|------|
| Supabase | Free | 0€ |
| BigQuery | Free | 0€ |
| Vercel | Hobby | 0€ |
| Render | Free (sleep) | 0€ |
| GitHub Actions | Free | 0€ |
| Sentry | Hobby | 0€ |
| Mistral API | Pay-as-you-go | ~5€ projet entier |

---

## 4. Conventions de code

### 4.1 Python

- **Formatter** : `black` (ligne max 100 caractères)
- **Linter** : `ruff`
- **Type hints** : obligatoires sur toutes les fonctions publiques
- **Docstrings** : Google style, en français
- **Imports** : groupés stdlib / third-party / local, séparés par une ligne blanche
- **Tests** : `pytest`, fichiers `test_*.py` à côté du code testé ou dans `/tests/`
- **Logger** : `logging` standard, pas de `print` en code de prod (OK en script d'analyse)

### 4.2 Commits Git

- Format Conventional Commits : `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Messages en français OK (le code est commenté en français)
- Un commit = une intention claire

### 4.3 Naming

- Modules : `snake_case`
- Classes : `PascalCase`
- Fonctions/variables : `snake_case`
- Constantes : `UPPER_SNAKE_CASE`
- Fichiers ETF en majuscules (SPY, TLT) — ce sont des tickers

---

## 5. Conventions data

### 5.1 Format dates

- Toujours `YYYY-MM-DD` (ISO 8601)
- Timezone : on stocke en UTC, on affiche en EU/Paris
- Attention aux jours fériés US (NYSE) vs FR (différents)

### 5.2 Format prix

- Toujours en USD (les ETF sont US-listed)
- Adjusted close (gère splits + dividendes), JAMAIS le close brut
- yfinance >= 0.2.x retourne déjà l'adjusted close dans la colonne "Close"

### 5.3 Returns

- Returns simples : `(P_t - P_{t-1}) / P_{t-1}`
- Log returns pour les calculs ML (additivité temporelle)
- Annualisation : `mean_daily * 252` pour returns, `std_daily * sqrt(252)` pour vol

### 5.4 Métriques portefeuille

- **Sharpe ratio** : `(return_annualized - risk_free_rate) / vol_annualized`
- **Risk-free rate** : 3-month T-Bill (FRED série `DGS3MO`), JAMAIS zéro
- **Max Drawdown** : pic-à-creux maximal sur la période
- **Frais transaction** : 0.1% par rebalancement (réaliste pour ETF chez courtier discount)

---

## 6. Architecture du projet

### 6.1 Structure dossiers (phase 1 — data + analyse)

```
deeppilot/
├── CLAUDE.md                  # ce fichier
├── TODO.md                    # liste des tâches ordonnées
├── README.md                  # description publique
├── .env.example
├── .env                       # local, gitignored
├── .gitignore
├── .python-version            # 3.11
├── pyproject.toml             # config black/ruff/pytest
├── requirements.txt
│
├── data/
│   ├── extractors/            # scripts d'extraction depuis sources
│   │   ├── __init__.py
│   │   ├── extract_yfinance.py
│   │   ├── extract_fred.py
│   │   ├── extract_files.py        # CSV INSEE/BCE
│   │   └── extract_bigquery.py
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── aggregate.py
│   │   ├── cleaning_rules.py
│   │   └── load_to_db.py           # CSV → Supabase
│   ├── sql/
│   │   ├── postgres/
│   │   │   ├── 01_init_schema.sql
│   │   │   └── ...
│   │   └── bigquery/
│   ├── raw/                        # données brutes téléchargées (gitignored si volumineux)
│   ├── processed/                  # données nettoyées
│   └── README.md
│
├── analysis/                       # notebooks d'exploration
│   ├── 01_explore_etfs.ipynb
│   ├── 02_correlations.ipynb
│   ├── 03_returns_distributions.ipynb
│   └── 04_macro_features.ipynb
│
├── tests/
│   ├── test_extractors.py
│   ├── test_aggregate.py
│   └── test_data_quality.py
│
└── docs/
    ├── data_sources.md
    ├── database_schema.md
    └── ...
```

### 6.2 Structure dossiers (phases ultérieures, à anticiper)

Quand on passera aux modèles ML : ajout de `/ml/`
Quand on passera à l'API : ajout de `/api/`
Quand on passera au front : ajout de `/web/`

**Ne crée pas ces dossiers maintenant**, ils seront ajoutés en temps voulu.

---

## 7. Variables d'environnement

Toutes les variables sensibles doivent être dans `.env` (gitignored).
Le fichier `.env.example` contient les noms des variables sans valeurs.

```
# Supabase
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_DB_URL=

# FRED (Federal Reserve Economic Data)
FRED_API_KEY=

# Google Cloud (BigQuery)
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
GCP_PROJECT_ID=

# Mistral (phase ML, plus tard)
MISTRAL_API_KEY=
```

---

## 8. Règles importantes pour Claude Code

### 8.1 Principes généraux

- **Avant de proposer une solution complexe**, propose la version simple d'abord
- **Avant de créer un fichier**, vérifie qu'il n'existe pas déjà
- **Avant d'installer une dépendance**, vérifie si une déjà installée fait le job
- **Si une consigne contredit CLAUDE.md**, demande confirmation au lieu de procéder
- **Pas de scraping** — consigne explicite, ne propose pas de BeautifulSoup/Selenium
- **Pas de LSTM / deep learning** — décision arrêtée, ne propose pas de PyTorch/TensorFlow
- **Code commenté en français**, mais variables/fonctions en anglais (snake_case)

### 8.2 Quand modifier CLAUDE.md

Tu peux suggérer une modif de CLAUDE.md si :
- Une décision change après discussion
- Une convention manque et provoque des incohérences
- Une nouvelle dépendance importante est ajoutée

Tu ne dois PAS modifier CLAUDE.md sans validation.

### 8.3 Format des réponses

- Réponses en français
- Code commenté en français
- Si tu rédiges de la doc, markdown propre avec headers H2/H3
- Évite les emojis dans le code, OK dans les conversations

---

## 9. Roadmap globale (vision long terme)

| Phase | Période | Focus | Compétences validées |
|-------|---------|-------|----------------------|
| **Phase 1** | Maintenant | **Data + analyse exploratoire** | C1, C2, C3, C4 (partiel) |
| Phase 2 | Sprint 2 | API REST data + RGPD | C4 (complet), C5 |
| Phase 3 | Sprint 3 | Modèles ML (HMM + RF) + tests | C9, C12 |
| Phase 4 | Sprint 4 | MLOps (MLflow, CI/CD ML) + monitoring | C11, C13 |
| Phase 5 | Sprint 5 | Service IA tiers (Mistral) + benchmark | C6, C7, C8 |
| Phase 6 | Sprint 6 | Application Next.js | C14, C15, C17 |
| Phase 7 | Sprint 7 | CI/CD app + monitoring + incidents | C18, C19, C20, C21 |
| Phase 8 | Sprint 8 | Rapports pro + soutenance | C16 transverse |

**Phase actuelle : Phase 1.** Tout ce qui n'est pas dans cette phase est hors scope pour l'instant.

---

## 10. Décisions ML arrêtées (pour mémoire)

### 10.1 Modèle 1 — Détection de régime de marché

- **Algorithme** : Hidden Markov Model (HMM, lib `hmmlearn`)
- **États** : 4 régimes (bull / bear / volatile / stable)
- **Features d'entrée** : VIX, spread crédit haut rendement, courbe taux 10Y-2Y, returns S&P500, volatilité réalisée
- **Validation** : labels rétrospectifs (NBER recessions + drawdowns SP500)

### 10.2 Modèle 2 — Prédiction de rendement

- **Algorithme** : Random Forest Classifier (binaire : rendement positif/négatif à 1 mois)
- **Features** : indicateurs techniques (SMA 20/50/200, RSI, MACD, Bollinger), volume, returns lagged, **régime sortant du modèle 1**
- **Validation** : walk-forward roulant TimeSeriesSplit
- **Métrique principale** : directional accuracy (signe correct du rendement)

### 10.3 Optimisation portefeuille

- **Méthode** : Markowitz contraint (max Sharpe ratio)
- **Lib** : `scipy.optimize.minimize` (méthode SLSQP)
- **Contraintes** : poids min 5% / max 25% par ETF, somme = 1, pas de short
- **Fréquence rebalancement** : mensuelle
- **Frais inclus** : 0.1% par trade
- **Risk-free rate** : 3-month T-Bill (FRED `DGS3MO`)

### 10.4 Validation rigoureuse

- Walk-forward roulant : optim sur N années glissantes, test sur année suivante
- Pas de look-ahead bias : assertions strictes sur les indices temporels en tests
- Comparaison à 4 benchmarks systématique
- Métriques : Sharpe, max drawdown, CAGR, vol annualisée, Calmar ratio

---

## 11. Disclaimer juridique

Le projet est purement éducatif. Il ne constitue pas un conseil en investissement au sens de l'article L321-1 du Code monétaire et financier. Tout document utilisateur (page about, README, app future) doit afficher ce disclaimer.

---

**Dernière mise à jour : 6 mai 2026**
