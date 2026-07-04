# TODO Phase 7 — CI/CD + Monitoring + Incidents

**Status** : ✅ Terminée
**Date** : 4 juillet 2026
**Compétences à valider** : C18, C19, C20, C21

---

## Objectif

Mettre en place la chaîne CI/CD complète, le monitoring et les procédures d'incident pour l'application DeepPilot.

---

## Compétences visées

| Code | Compétence | Validation |
|------|------------|------------|
| C18 | Automatiser les tests du code source | GitHub Actions (tests frontend + backend) |
| C19 | Créer un processus de livraison continue | Vercel (auto-deploy) + Render |
| C20 | Surveiller une application | Sentry (erreurs) + UptimeRobot (uptime) |
| C21 | Résoudre les incidents techniques | Procédures + runbooks + post-mortems |

---

## Étapes

### Phase A : CI/CD Application ✅

- [x] GitHub Actions pour tests ML (`ml_tests.yml`)
- [x] GitHub Actions pour tests API (`api_tests.yml`)
- [x] GitHub Actions pour build frontend (`frontend_ci.yml`)
- [ ] Protection de branche main (require PR + checks) - optionnel

### Phase B : Monitoring Sentry ✅

- [x] Créer compte Sentry (gratuit)
- [x] Intégrer Sentry dans le backend FastAPI
- [x] Ajouter `SENTRY_DSN` sur Render
- [ ] Intégrer Sentry dans le frontend Next.js (optionnel)
- [x] Error monitoring + Tracing activés

#### Instructions Sentry Frontend

```bash
cd web
npm install @sentry/nextjs
npx @sentry/wizard@latest -i nextjs
```

Puis ajouter dans Vercel :
- `SENTRY_DSN` : ton DSN Sentry
- `SENTRY_AUTH_TOKEN` : token pour source maps

### Phase C : Monitoring Uptime ✅

- [x] Créer compte UptimeRobot (gratuit)
- [x] Monitorer `/health` du backend
- [x] Monitorer la page d'accueil frontend
- [x] Monitorer `/api/v1/ml/status`
- [x] Alertes email configurées

### Phase D : Procédures d'incident ✅

- [x] Créer `docs/incidents/README.md` (processus)
- [x] Créer `docs/incidents/runbooks/` (3 guides)
- [x] Créer template de post-mortem
- [x] Documenter les contacts et escalades

---

## Fichiers à créer

```
.github/
├── workflows/
│   ├── ml_tests.yml        # ✅ Existe
│   ├── api_tests.yml       # Tests API FastAPI
│   └── frontend_ci.yml     # Build + lint frontend

docs/
├── incidents/
│   ├── README.md           # Processus de gestion d'incident
│   ├── runbooks/
│   │   ├── api_down.md     # API ne répond pas
│   │   ├── db_error.md     # Erreur base de données
│   │   └── ml_error.md     # Erreur modèle ML
│   └── postmortems/
│       └── TEMPLATE.md     # Template post-mortem
```

---

## Services externes

| Service | Plan | Coût | Usage |
|---------|------|------|-------|
| Sentry | Developer (gratuit) | 0€ | Tracking erreurs |
| UptimeRobot | Free | 0€ | Monitoring uptime (50 monitors) |
| GitHub Actions | Free | 0€ | CI/CD (2000 min/mois) |

---

## Configuration Sentry

### Backend (FastAPI)

```python
# api/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://xxx@sentry.io/xxx",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment="production",
)
```

### Frontend (Next.js)

```bash
npm install @sentry/nextjs
npx @sentry/wizard@latest -i nextjs
```

---

## Configuration UptimeRobot

| Monitor | URL | Intervalle | Alerte |
|---------|-----|------------|--------|
| API Health | `https://deeppilote.onrender.com/health` | 5 min | Email |
| Frontend | `https://deep-pilote.vercel.app` | 5 min | Email |
| API ML | `https://deeppilote.onrender.com/api/v1/ml/status` | 15 min | Email |

---

## Livrables

1. **CI/CD** : 3 workflows GitHub Actions fonctionnels
2. **Sentry** : Dashboard avec erreurs trackées
3. **UptimeRobot** : 3 monitors configurés
4. **Documentation** : Procédures d'incident complètes
