# Checkpoint Phase 7 — CI/CD + Monitoring + Incidents

**Date** : 5 juillet 2026
**Status** : ✅ Terminée
**Compétences validées** : C18, C19, C20, C21

---

## Objectif

Mettre en place la chaîne CI/CD complète, le monitoring et les procédures d'incident pour l'application DeepPilot.

---

## CI/CD GitHub Actions

### Workflows créés

| Workflow | Fichier | Trigger | Actions |
|----------|---------|---------|---------|
| ML Tests | `ml_tests.yml` | Push sur `ml/`, `tests/ml/` | Tests pytest ML + MLOps |
| API Tests | `api_tests.yml` | Push sur `api/`, `tests/api/` | Tests pytest API + lint |
| Frontend CI | `frontend_ci.yml` | Push sur `web/` | Lint + type-check + build |
| Data Refresh | `data_refresh.yml` | Cron 22h UTC (Lun-Ven) | Extraction données + Backtest |

### Structure

```
.github/workflows/
├── ml_tests.yml      # Tests ML (Phase 4)
├── api_tests.yml     # Tests API + lint Python
├── frontend_ci.yml   # Build + lint Next.js
└── data_refresh.yml  # Extraction yfinance/FRED + Backtest quotidien
```

### Data Refresh Workflow

Le workflow `data_refresh.yml` s'exécute automatiquement chaque jour ouvré (Lun-Ven) à 22h UTC :

1. **Job extract-data** : Extrait les prix ETF (SPY, QQQ, etc.) via yfinance + données macro via FRED
2. **Job regenerate-backtest** : Régénère le backtest DeepPilot avec les nouvelles données
3. **Auto-commit** : Le fichier `data/backtest_results.json` est commité automatiquement

```yaml
on:
  schedule:
    - cron: '0 22 * * 1-5'  # Lun-Ven à 22h UTC
```

---

## Monitoring Sentry

### Configuration Backend (FastAPI)

```python
# api/main.py
import sentry_sdk

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment,
        traces_sample_rate=0.1,
    )
```

### Variables d'environnement

| Variable | Où | Valeur |
|----------|-----|--------|
| `SENTRY_DSN` | Render | `https://xxx@sentry.io/xxx` |
| `SENTRY_ENVIRONMENT` | Render | `production` |

### Fonctionnalités activées

- ✅ Error monitoring (capture automatique des exceptions)
- ✅ Tracing (suivi des requêtes lentes)

---

## Monitoring UptimeRobot

### Monitors configurés

| Monitor | URL | Intervalle |
|---------|-----|------------|
| API Health | `https://deeppilote.onrender.com/health` | 5 min |
| Frontend | `https://deep-pilote.vercel.app` | 5 min |
| ML Status | `https://deeppilote.onrender.com/api/v1/ml/status` | 15 min |

### Alertes

- Email en cas de downtime
- Notification quand le service revient UP

---

## Procédures d'incident

### Documentation créée

```
docs/incidents/
├── README.md              # Processus de gestion d'incident
├── runbooks/
│   ├── api_down.md       # Guide : API ne répond pas
│   ├── db_error.md       # Guide : Erreur base de données
│   └── ml_error.md       # Guide : Erreur modèle ML
└── postmortems/
    └── TEMPLATE.md       # Template post-mortem
```

### Niveaux d'incident

| Niveau | Description | Temps de réponse |
|--------|-------------|------------------|
| P1 | Service totalement down | < 15 min |
| P2 | Fonctionnalité majeure dégradée | < 1h |
| P3 | Fonctionnalité secondaire affectée | < 4h |
| P4 | Problème cosmétique | < 24h |

---

## Dépendances ajoutées

| Package | Version | Usage |
|---------|---------|-------|
| `sentry-sdk[fastapi]` | >=2.0.0 | Monitoring erreurs |

---

## Page Performance (Backtest Comparison)

### Nouvelle page `/performance`

Compare DeepPilot ML aux benchmarks classiques :
- **DeepPilot** : Notre stratégie ML (HMM + RF + Markowitz)
- **SPY** : S&P 500
- **QQQ** : NASDAQ 100
- **60/40** : 60% SPY + 40% TLT
- **Equal Weight** : 12.5% chaque ETF

### Fonctionnalités

- Sélecteur de période (1Y, 3Y, 5Y, 10Y)
- Métriques par benchmark : Total Return, CAGR, Sharpe, Volatilité, Max Drawdown
- Graphique performance cumulée (base 100)
- Tableau des returns annuels

### Endpoints API

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/backtest/compare?years=5` | Métriques + courbes cumulées |
| `GET /api/v1/backtest/yearly?years=10` | Returns annuels par benchmark |

### Fichiers

```
api/services/backtest_service.py   # Service backtest
api/routers/backtest.py            # Endpoints API
web/app/performance/page.tsx       # Page frontend
scripts/run_backtest.py            # Script génération backtest
data/backtest_results.json         # Résultats pré-calculés
```

---

## Compétences validées

| Code | Compétence | Validation |
|------|------------|------------|
| C18 | Automatiser les tests du code source | 3 workflows GitHub Actions |
| C19 | Créer un processus de livraison continue | Vercel + Render auto-deploy |
| C20 | Surveiller une application | Sentry + UptimeRobot |
| C21 | Résoudre les incidents techniques | Runbooks + template post-mortem |

---

## Architecture finale

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              GitHub Actions                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐ │
│  │ ml_tests.yml│  │api_tests.yml│  │frontend_ci  │  │ data_refresh.yml │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └────────┬─────────┘ │
└─────────┼────────────────┼────────────────┼──────────────────┼───────────┘
          │                │                │                  │
          ▼                ▼                ▼                  ▼
    ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌──────────────┐
    │  Render   │    │  Render   │    │  Vercel   │    │  yfinance +  │
    │ (Backend) │    │ (Backend) │    │(Frontend) │    │  FRED API    │
    └─────┬─────┘    └─────┬─────┘    └─────┬─────┘    └──────┬───────┘
          │                │                │                  │
          ▼                ▼                ▼                  ▼
    ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌──────────────┐
    │  Sentry   │    │ Supabase  │    │UptimeRobot│    │  Backtest    │
    │ (Erreurs) │    │   (DB)    │    │ (Uptime)  │    │  (JSON)      │
    └───────────┘    └───────────┘    └───────────┘    └──────────────┘
```

### Cycle quotidien automatisé (Lun-Ven 22h UTC)

```
yfinance/FRED → Supabase DB → run_backtest.py → backtest_results.json → git push
```

---

## Prochaines étapes (Phase 8)

1. Rapports professionnels
2. Préparation soutenance
3. Documentation finale
