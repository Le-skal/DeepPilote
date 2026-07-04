# Checkpoint Phase 6 — Application Next.js

**Date** : 4 juillet 2026
**Status** : ✅ Terminée
**Compétences validées** : C10, C14, C15, C17

## Design

Theme **Cyberpunk Finance** :
- Palette sombre avec accents cyan/magenta
- Effets glow sur les cartes
- Font mono pour les valeurs numériques
- Border-radius minimal (style finance pro)
- Couleurs sémantiques : vert (bull), rouge (bear), jaune (volatile), bleu (stable)

---

## Objectif

Créer une application Next.js 14 pour visualiser les données du projet DeepPilot (ETF, indicateurs macro, portfolio).

---

## Stack technique

| Techno | Version | Usage |
|--------|---------|-------|
| Next.js | 14.2.x | Framework React (App Router) |
| TypeScript | 5.x | Typage statique |
| Tailwind CSS | 3.x | Styling utilitaire |
| shadcn/ui | latest | Composants UI |
| React Query | 5.x | Data fetching + cache |
| Recharts | 2.x | Graphiques |
| Lucide React | latest | Icônes |

---

## Pages créées

| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/` | Vue d'ensemble (régime, VIX, stats ETF) |
| ETFs | `/etfs` | Liste des 8 ETF + 2 benchmarks |
| Détail ETF | `/etfs/[ticker]` | Prix historique, stats, features ML |
| Market | `/market` | Indicateurs macro, régimes de marché |
| Analysis | `/analysis` | Matrice de corrélation, statistiques |
| Portfolio | `/portfolio` | Allocations recommandées (mock) |
| About | `/about` | Disclaimer légal obligatoire |

---

## Architecture

```
web/
├── app/                    # Pages (App Router)
│   ├── page.tsx           # Dashboard
│   ├── etfs/
│   │   ├── page.tsx       # Liste ETF
│   │   └── [ticker]/page.tsx  # Détail ETF
│   ├── market/page.tsx    # Indicateurs macro
│   ├── analysis/page.tsx  # Corrélations
│   ├── portfolio/page.tsx # Allocations
│   └── about/page.tsx     # Disclaimer
│
├── components/
│   ├── layout/            # Header, Footer
│   ├── cards/             # StatCard, ETFCard, RegimeIndicator
│   ├── charts/            # PriceChart (Recharts)
│   └── ui/                # shadcn/ui (Button, Card, etc.)
│
├── hooks/
│   ├── useETFs.ts         # ETF data hooks
│   ├── useMacro.ts        # Macro indicators hooks
│   └── useAnalysis.ts     # Stats/correlations hooks
│
├── lib/
│   ├── api/
│   │   ├── client.ts      # Fetch wrapper
│   │   ├── etfs.ts        # ETF API functions
│   │   ├── macro.ts       # Macro API functions
│   │   └── analysis.ts    # Analysis API functions
│   └── utils/
│       ├── constants.ts   # ETF_TICKERS, REGIME_COLORS
│       └── formatters.ts  # formatPercent, formatCurrency
│
├── types/
│   └── api.ts             # Types miroir des schemas Pydantic
│
└── providers/
    └── QueryProvider.tsx  # React Query provider
```

---

## Composants clés

### StatCard
Carte réutilisable pour afficher une métrique avec titre, valeur, sous-titre et tendance optionnelle.

### RegimeIndicator
Badge coloré indiquant le régime de marché actuel (bull/bear/volatile/stable) avec niveau de confiance.

### ETFCard
Carte résumé d'un ETF avec ticker, nom, classe d'actifs et stats principales.

### PriceChart
Graphique Recharts (LineChart) pour afficher l'historique des prix d'un ETF.

---

## Intégration API

L'application consomme l'API FastAPI existante via React Query :

| Endpoint | Hook | Usage |
|----------|------|-------|
| `GET /api/v1/etfs` | `useETFs()` | Liste des ETF |
| `GET /api/v1/etfs/{ticker}` | `useETF(ticker)` | Détail ETF |
| `GET /api/v1/etfs/{ticker}/prices` | `useETFPrices(ticker)` | Prix historiques |
| `GET /api/v1/etfs/{ticker}/features` | `useETFFeatures(ticker)` | Features ML |
| `GET /api/v1/macro/latest` | `useMacroLatest()` | Derniers indicateurs |
| `GET /api/v1/analysis/correlations` | `useCorrelations()` | Matrice corrélation |
| `GET /api/v1/analysis/stats` | `useAllStats()` | Stats tous ETF |

---

## Configuration

### Variables d'environnement

```env
# web/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Lancement

```bash
# Terminal 1 - Backend
python scripts/run_api.py

# Terminal 2 - Frontend
cd web
npm run dev
# → http://localhost:3000
```

---

## Points d'attention

1. **Mock data** : La page Portfolio utilise des données mock car les endpoints ML (`/api/v1/ml/portfolio/weights`) ne sont pas encore exposés.

2. **Régime de marché** : Affiché avec valeur mock (bull, 87% confiance). L'intégration réelle viendra avec l'exposition de l'endpoint HMM.

3. **Disclaimer légal** : Page `/about` obligatoire (voir CLAUDE.md section 11).

4. **Responsive** : L'application utilise les breakpoints Tailwind (md, lg) pour s'adapter aux différentes tailles d'écran.

---

## Build

```bash
cd web
npm run build
```

Build réussi avec 7 pages :
- 6 pages statiques (pre-rendered)
- 1 page dynamique (`/etfs/[ticker]`)

---

---

## Déploiement

### Option 1 : Vercel (Recommandé - Gratuit)

1. **Push ton code sur GitHub** (si pas déjà fait)

2. **Va sur https://vercel.com** et connecte-toi avec GitHub

3. **Import le projet** :
   - "Add New Project"
   - Sélectionne le repo `deepilot`
   - Root Directory : `web`
   - Framework : Next.js (auto-détecté)

4. **Configure les variables d'environnement** :
   ```
   NEXT_PUBLIC_API_URL=https://ton-api.onrender.com
   ```

5. **Deploy** - Vercel build et déploie automatiquement

**URL** : `https://deepilot.vercel.app` (ou custom domain)

### Option 2 : API Backend sur Render

Pour que le frontend fonctionne en prod, l'API doit être accessible publiquement.

1. **Va sur https://render.com**

2. **New Web Service** :
   - Connecte ton repo GitHub
   - Root Directory : `.` (racine)
   - Build Command : `pip install -r requirements.txt`
   - Start Command : `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

3. **Variables d'environnement** :
   ```
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_KEY=eyJ...
   SUPABASE_DB_URL=postgresql://postgres.xxx:password@aws-0-eu-west-1.pooler.supabase.com:5432/postgres
   ```

4. **Free tier** : L'API dort après 15min d'inactivité (cold start ~30s)

### Architecture Production

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Vercel    │────▶│   Render    │────▶│  Supabase   │
│  (Next.js)  │     │  (FastAPI)  │     │ (PostgreSQL)│
└─────────────┘     └─────────────┘     └─────────────┘
     Front              API                  DB
```

---

## Prochaines étapes (Phase 7)

1. CI/CD avec GitHub Actions
2. Déploiement Vercel + Render
3. Monitoring Sentry
4. UptimeRobot pour surveillance
5. Procédures d'incident

---

## Compétences validées

| Code | Compétence | Validation |
|------|------------|------------|
| C10 | Intégrer l'API d'un modèle d'IA dans une application | React Query + FastAPI |
| C14 | Analyser le besoin d'application | Pages et fonctionnalités définies |
| C15 | Concevoir le cadre technique | Architecture Next.js + API |
| C17 | Développer les composants et interfaces | 7 pages + composants réutilisables |
