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

### 6.1 Structure dossiers (Phase 4 — complète)

```
deeppilot/
├── CLAUDE.md                  # ce fichier
├── TODO.md                    # liste des tâches ordonnées
├── README.md                  # description publique
├── .env.example
├── .env                       # local, gitignored
├── .gitignore
├── pyproject.toml             # config black/ruff/pytest
├── requirements.txt
│
├── data/
│   ├── extractors/            # scripts d'extraction (yfinance, FRED, BigQuery)
│   ├── pipeline/              # agrégation et nettoyage
│   ├── sql/                   # requêtes SQL (Postgres, BigQuery)
│   └── processed/             # données nettoyées
│
├── ml/
│   ├── models/                # modèles ML (HMM, GMM, K-Means, RF, XGBoost)
│   ├── features/              # feature engineering
│   ├── portfolio/             # optimisation Markowitz, backtesting
│   └── evaluation/            # métriques et comparaisons
│
├── mlops/
│   ├── config.py              # configuration MLflow
│   ├── tracking.py            # wrapper MLflow
│   ├── registry.py            # model registry
│   └── monitoring.py          # drift detection (PSI, KS)
│
├── api/                       # API FastAPI RGPD-compliant
│
├── analysis/                  # notebooks d'exploration (01-09)
│   ├── 01-04                  # exploration données
│   ├── 05-07                  # modèles ML et backtest
│   └── 08-09                  # MLOps (tracking, monitoring)
│
├── tests/                     # 182 tests (data, ML, MLOps, API)
│
├── scripts/                   # scripts utilitaires
│
└── docs/                      # documentation
```

### 6.2 Dossiers ajoutés (Phases 2-4)

Les dossiers suivants ont été créés au fil des phases :
- `/ml/` : modèles ML (HMM, RF), features, portfolio, backtest (Phase 3)
- `/mlops/` : tracking MLflow, registry, monitoring (Phase 4)
- `/api/` : API FastAPI RGPD-compliant (Phase 2)

**À venir (Phase 6)** : `/web/` pour l'application Next.js

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
| Phase 1 | ✅ Terminé | Data + analyse exploratoire | C1, C2, C3, C4 (partiel) |
| Phase 2 | ✅ Terminé | API REST data + RGPD | C4 (complet), C5 |
| Phase 3 | ✅ Terminé | Modèles ML (HMM, RF, backtest) | C9, C12 |
| Phase 4 | ✅ Terminé | MLOps (MLflow, CI/CD ML) + monitoring | C11, C13 |
| **Phase 4.5** | **À faire** | **Validation HMM améliorée (métriques éco.)** | C13 (renforcement) |
| Phase 5 | À faire | Service IA tiers (Mistral) + sentiment | C6, C7, C8 |
| Phase 6 | À faire | Application Next.js + intégration API ML | C10, C14, C15, C17 |
| Phase 7 | À faire | CI/CD app + monitoring + incidents | C18, C19, C20, C21 |
| Phase 8 | À faire | Rapports pro + soutenance | C16 transverse |

**Phase actuelle : Phase 4.5 à faire.** Prochaine étape : Améliorer validation HMM, puis Phase 5.

### 9.1 Détail des compétences par bloc

**Bloc 1 — Collecte, stockage, mise à disposition des données (C1-C5)**
- C1 : Automatiser l'extraction de données (yfinance, FRED, BigQuery, fichiers CSV)
- C2 : Développer des requêtes SQL d'extraction (PostgreSQL, BigQuery)
- C3 : Développer des règles d'agrégation de données (pipeline, nettoyage)
- C4 : Créer une base de données RGPD-compliant (Supabase + registre traitements)
- C5 : Développer une API REST mettant à disposition les données (FastAPI)

**Bloc 2 — Modèles et services d'IA (C6-C13)**
- C6 : Organiser et réaliser une veille technique et réglementaire
- C7 : Identifier des services d'IA préexistants (benchmark Mistral vs autres)
- C8 : Paramétrer un service d'IA (configuration Mistral API)
- C9 : Développer une API exposant un modèle d'IA (FastAPI + HMM/RF)
- C10 : Intégrer l'API d'un modèle d'IA dans une application (Next.js consomme FastAPI)
- C11 : Monitorer un modèle d'IA (MLflow, drift detection PSI/KS)
- C12 : Programmer les tests automatisés d'un modèle d'IA (pytest ML)
- C13 : Créer une chaîne de livraison continue d'un modèle d'IA (GitHub Actions ML)

**Bloc 3 — Application intégrant un service d'IA (C14-C21)**
- C14 : Analyser le besoin d'application (spécifications fonctionnelles)
- C15 : Concevoir le cadre technique (architecture Next.js + FastAPI)
- C16 : Coordonner la réalisation technique (gestion agile, rapport)
- C17 : Développer les composants et interfaces (Next.js + shadcn/ui)
- C18 : Automatiser les tests du code source (CI/CD app)
- C19 : Créer un processus de livraison continue (Vercel)
- C20 : Surveiller une application (Sentry + UptimeRobot)
- C21 : Résoudre les incidents techniques (procédures, post-mortems)

---

## 10. Décisions ML (avec comparaisons)

### 10.1 Modèle 1 — Détection de régime de marché

**Modèles comparés :**
| Modèle | Lib | Pourquoi le tester |
|--------|-----|-------------------|
| **HMM** (choix final) | `hmmlearn` | Standard pour séries temporelles à états cachés |
| K-Means | `sklearn` | Baseline simple, clustering sur features |
| GMM | `sklearn` | Comme K-Means mais probabiliste |

- **États** : 4 régimes (bull / bear / volatile / stable)
- **Features d'entrée** : VIX, spread crédit HY, courbe taux 10Y-2Y, returns S&P500, volatilité réalisée
- **Validation** : labels rétrospectifs (NBER recessions + drawdowns SP500 > 20%)
- **Métrique** : Adjusted Rand Index vs labels historiques

### 10.2 Modèle 2 — Prédiction de rendement

**Modèles comparés :**
| Modèle | Lib | Pourquoi le tester |
|--------|-----|-------------------|
| **Random Forest** (choix final) | `sklearn` | Robuste, gère bien les features hétérogènes |
| XGBoost | `xgboost` | Souvent meilleur en compétition |
| Logistic Regression | `sklearn` | Baseline interprétable |

- **Cible** : Binaire (rendement positif/négatif à 1 mois)
- **Features** : indicateurs techniques (SMA, RSI, MACD, Bollinger), returns lagged, **régime du modèle 1**
- **Validation** : walk-forward roulant TimeSeriesSplit
- **Métriques** : Accuracy, Precision, Recall, F1, AUC-ROC

### 10.3 Stratégies de portefeuille comparées

**Stratégies benchmark :**
| Stratégie | Description |
|-----------|-------------|
| Buy & Hold SPY | 100% SPY tout le temps |
| Buy & Hold URTH | 100% MSCI World |
| 60/40 | 60% SPY + 40% TLT, rebalancé annuellement |
| Equal Weight | 12.5% chaque ETF, rebalancé mensuellement |
| **DeepPilot** | Notre stratégie ML |

**Optimisation :**
- **Méthode** : Markowitz contraint (max Sharpe ratio)
- **Lib** : `scipy.optimize.minimize` (méthode SLSQP)
- **Contraintes** : poids min 5% / max 25% par ETF, somme = 1, pas de short
- **Fréquence rebalancement** : mensuelle
- **Frais inclus** : 0.1% par trade
- **Risk-free rate** : 3-month T-Bill (FRED `DGS3MO`)

### 10.4 Validation rigoureuse

- **Walk-forward roulant** : train sur 5 ans glissants, test sur 1 an suivant
- **Pas de look-ahead bias** : assertions strictes sur les indices temporels
- **Métriques de comparaison** :
  - Sharpe ratio
  - CAGR (Compound Annual Growth Rate)
  - Max Drawdown
  - Volatilité annualisée
  - Calmar ratio (CAGR / Max DD)
  - Win rate (% mois positifs)

---

## 11. Disclaimer juridique

Le projet est purement éducatif. Il ne constitue pas un conseil en investissement au sens de l'article L321-1 du Code monétaire et financier. Tout document utilisateur (page about, README, app future) doit afficher ce disclaimer.

---

**Dernière mise à jour : 16 mai 2026**
