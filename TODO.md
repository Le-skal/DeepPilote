# DeepPilot — TODO Principal

> **Phase actuelle : Phase 8 à faire** (mise à jour: 5 juillet 2026)
> Prochaine étape : Rapports professionnels + soutenance

---

## Progression globale

| Phase | Focus | Status | Compétences |
|-------|-------|--------|-------------|
| Phase 1 | Data + Analyse exploratoire | ✅ Terminée | C1, C2, C3, C4 |
| Phase 2 | API REST + RGPD | ✅ Terminée | C4, C5 |
| Phase 3 | Modèles ML (HMM + RF) | ✅ Terminée | C9, C12 |
| Phase 4 | MLOps (MLflow, monitoring) | ✅ Terminée | C11, C13 |
| Phase 4.5 | Validation HMM améliorée | ✅ Terminée | C13 |
| Phase 5 | Service IA tiers (Mistral) | ✅ Terminée | C6, C7, C8 |
| Phase 6 | Application Next.js | ✅ Terminée | C10, C14, C15, C17 |
| Phase 7 | CI/CD + monitoring app | ✅ Terminée | C18, C19, C20, C21 |
| **Phase 8** | **Rapports + soutenance** | ⏳ À faire | C16 |

---

## Fichiers TODO par phase

- `TODO_PHASE2.md` - API REST + RGPD (terminée)
- `TODO_PHASE3.md` - Modèles ML (terminée)
- `TODO_PHASE4.md` - MLOps (terminée)
- `TODO_PHASE6.md` - Application Next.js + ML endpoints (terminée)
- `TODO_PHASE7.md` - CI/CD + monitoring (terminée)

---

## Résumé des résultats

### Phase 3 - ML
- **HMM** : 4 régimes, stabilité 97.9%, détecte correctement les crises
- **Random Forest** : accuracy 55-58%, AUC ~0.51
- **DeepPilot Portfolio** : CAGR 5.59%, Sharpe 0.41, Max DD -17.2%
- **61 tests ML passent**

### Phase 4 - MLOps
- **MLflow tracking** : 4 expériences configurées
- **Model Registry** : versioning des modèles HMM et RF
- **Drift Detection** : PSI + KS test fonctionnels
- **Monitoring** : alertes de performance avec seuils
- **30 tests MLOps passent**
- **182 tests totaux**

---

## Phase 4.5 — Validation HMM améliorée ✅

Remplacement du silhouette score par des métriques économiques. **Terminée le 4 juillet 2026.**

### Métriques économiques implémentées

| Métrique | Description | Seuil |
|----------|-------------|-------|
| `crisis_recall` | % des 7 crises historiques détectées | ≥ 0.80 |
| `regime_return_separation` | Rendement(bull) > Rendement(bear) | True |
| `regime_vol_separation` | Volatilité(volatile) > Volatilité(stable) | True |
| `stability` | % jours sans changement | ≥ 0.90 |

### Fichiers créés

- `ml/evaluation/regime_validation.py` : 6 fonctions de validation
- `tests/ml/test_regime_validation.py` : 20 tests
- `TODO_PHASE4.5.md` et `CHECKPOINT_PHASE4.5.md`

### Résultats

- **81 tests ML passent** (61 existants + 20 nouveaux)
- Compétence C13 renforcée

---

## Phase 5 — Service IA tiers (Mistral) ✅

Intégration de Mistral API pour l'analyse de sentiment sur les news financières. **Terminée le 4 juillet 2026.**

### Fichiers créés

- `ml/sentiment/mistral_client.py` : Client Mistral avec rate limiting
- `ml/sentiment/news_fetcher.py` : Extraction de news via NewsAPI
- `ml/sentiment/analyzer.py` : Pipeline complet d'analyse
- `tests/ml/test_sentiment.py` : Tests unitaires

### Résultats

- Analyse de sentiment par ETF (bullish/bearish/neutral)
- Score de confiance par analyse
- Intégration prête pour les features ML

---

## Phase 6 — Application Next.js ✅

Application web pour visualiser les données DeepPilot avec endpoints ML. **Terminée le 4 juillet 2026.**

### Stack technique

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS + shadcn/ui (theme Cyberpunk Finance)
- React Query (@tanstack/react-query)
- Recharts (graphiques)

### Pages créées (toutes dynamiques, pas de données mockées)

| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/` | Vue d'ensemble (régime ML, VIX, stats) |
| ETFs | `/etfs` | Liste des 8 ETF + benchmarks |
| Détail ETF | `/etfs/[ticker]` | Prix, stats, features |
| Market | `/market` | Indicateurs macro, régimes ML, probabilités |
| Analysis | `/analysis` | Corrélations, statistiques |
| Portfolio | `/portfolio` | Allocations optimales ML (Markowitz) |
| About | `/about` | Disclaimer légal |

### Nouveaux endpoints ML

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/ml/regime` | Régime HMM actuel (bull/bear/volatile/stable) |
| `GET /api/v1/ml/portfolio` | Poids optimaux Markowitz en temps réel |
| `GET /api/v1/ml/status` | État du cache ML |
| `POST /api/v1/ml/refresh` | Forcer réentraînement |

**Réentraînement automatique** : Le modèle HMM est réentraîné toutes les 6h (cache TTL) ou au cold start Render.

### Déploiement

- **Frontend** : https://deep-pilote.vercel.app (Vercel)
- **Backend** : https://deeppilote.onrender.com (Render)

### Lancement local

```bash
# Backend (terminal 1)
python scripts/run_api.py

# Frontend (terminal 2)
cd web && npm run dev
# → http://localhost:3000
```

---

## Phase 7 — CI/CD + Monitoring ✅

**Terminée le 5 juillet 2026.**

### CI/CD GitHub Actions (4 workflows)
- `ml_tests.yml` - Tests ML + MLOps
- `api_tests.yml` - Tests API + lint Python
- `frontend_ci.yml` - Build + lint Next.js
- `data_refresh.yml` - **Extraction automatique quotidienne** (22h UTC, Lun-Ven)

### Extraction automatique
Le workflow `data_refresh.yml` extrait les données fraîches chaque jour ouvré :
- yfinance (prix ETF) → FRED (indicateurs macro) → Supabase
- Les modèles ML utilisent automatiquement les nouvelles données (TTL 6h)

### Monitoring
- **Sentry** : Tracking erreurs backend (FastAPI)
- **UptimeRobot** : 3 monitors (API health, frontend, ML status)

### Procédures d'incident
- `docs/incidents/README.md` - Processus complet
- `docs/incidents/runbooks/` - 3 guides de résolution
- `docs/incidents/postmortems/TEMPLATE.md`

---

## Prochaines étapes (Phase 8)

1. Rapports professionnels
2. Préparation soutenance
3. Documentation finale

---

## Documentation clé

- `CLAUDE.md` - Instructions projet pour Claude Code
- `CHECKPOINT_PHASE*.md` - Résumé de chaque phase
- `docs/mlops/README.md` - Guide MLOps complet
- `web/README.md` - Documentation frontend
