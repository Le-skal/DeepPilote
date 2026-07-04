# Checkpoint Phase 7 — CI/CD + Monitoring + Incidents

**Date** : 4 juillet 2026
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

### Structure

```
.github/workflows/
├── ml_tests.yml      # Tests ML (Phase 4)
├── api_tests.yml     # Tests API + lint Python
└── frontend_ci.yml   # Build + lint Next.js
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
┌─────────────────────────────────────────────────────────────┐
│                        GitHub                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ ml_tests.yml│  │api_tests.yml│  │frontend_ci  │          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
└─────────┼────────────────┼────────────────┼─────────────────┘
          │                │                │
          ▼                ▼                ▼
    ┌───────────┐    ┌───────────┐    ┌───────────┐
    │  Render   │    │  Render   │    │  Vercel   │
    │ (Backend) │    │ (Backend) │    │(Frontend) │
    └─────┬─────┘    └─────┬─────┘    └─────┬─────┘
          │                │                │
          ▼                ▼                ▼
    ┌───────────┐    ┌───────────┐    ┌───────────┐
    │  Sentry   │    │ Supabase  │    │UptimeRobot│
    │ (Erreurs) │    │   (DB)    │    │ (Uptime)  │
    └───────────┘    └───────────┘    └───────────┘
```

---

## Prochaines étapes (Phase 8)

1. Rapports professionnels
2. Préparation soutenance
3. Documentation finale
