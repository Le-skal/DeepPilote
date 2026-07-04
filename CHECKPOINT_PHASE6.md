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

Créer une application Next.js 14 pour visualiser les données du projet DeepPilot (ETF, indicateurs macro, régimes ML, portfolio optimisé).

**Important** : Toutes les données sont dynamiques (pas de hardcoding/mock). L'application consomme les endpoints API en temps réel.

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
| Dashboard | `/` | Vue d'ensemble (régime ML, VIX, stats ETF) |
| ETFs | `/etfs` | Liste des 8 ETF + 2 benchmarks |
| Détail ETF | `/etfs/[ticker]` | Prix historique, stats, features ML |
| Market | `/market` | Indicateurs macro, régimes de marché, probabilités |
| Analysis | `/analysis` | Matrice de corrélation, statistiques |
| Portfolio | `/portfolio` | Allocations optimales (calculées par ML) |
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
│   ├── market/page.tsx    # Indicateurs macro + régime
│   ├── analysis/page.tsx  # Corrélations
│   ├── portfolio/page.tsx # Allocations ML
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
│   ├── useAnalysis.ts     # Stats/correlations hooks
│   └── useML.ts           # Régime + Portfolio hooks
│
├── lib/
│   ├── api/
│   │   ├── client.ts      # Fetch wrapper
│   │   ├── etfs.ts        # ETF API functions
│   │   ├── macro.ts       # Macro API functions
│   │   ├── analysis.ts    # Analysis API functions
│   │   └── ml.ts          # ML API functions (régime, portfolio)
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

## Nouveaux endpoints ML (backend)

### `GET /api/v1/ml/regime`

Retourne le régime de marché détecté par le modèle HMM :

```json
{
  "regime": "bull",
  "regime_id": 0,
  "confidence": 0.87,
  "as_of_date": "2026-07-04",
  "probabilities": {
    "bull": 0.87,
    "bear": 0.05,
    "volatile": 0.03,
    "stable": 0.05
  }
}
```

### `GET /api/v1/ml/portfolio`

Retourne les poids optimaux calculés par Markowitz :

```json
{
  "weights": {
    "SPY": 0.25,
    "TLT": 0.20,
    "GLD": 0.15,
    "EFA": 0.12,
    "VNQ": 0.10,
    "EEM": 0.08,
    "HYG": 0.05,
    "SH": 0.05
  },
  "expected_return": 0.0847,
  "volatility": 0.1256,
  "sharpe_ratio": 0.62,
  "regime": "bull",
  "as_of_date": "2026-07-04"
}
```

---

## Fichiers API créés

| Fichier | Description |
|---------|-------------|
| `api/models/ml.py` | Schemas Pydantic (RegimeResponse, PortfolioWeights) |
| `api/routers/ml.py` | Router FastAPI pour `/api/v1/ml/*` |
| `api/services/ml_service.py` | Service ML (charge données, entraîne HMM, optimise) |

---

## Intégration API

L'application consomme l'API FastAPI via React Query :

| Endpoint | Hook | Usage |
|----------|------|-------|
| `GET /api/v1/etfs` | `useETFs()` | Liste des ETF |
| `GET /api/v1/etfs/{ticker}` | `useETF(ticker)` | Détail ETF |
| `GET /api/v1/etfs/{ticker}/prices` | `useETFPrices(ticker)` | Prix historiques |
| `GET /api/v1/etfs/{ticker}/features` | `useETFFeatures(ticker)` | Features ML |
| `GET /api/v1/macro/latest` | `useMacroLatest()` | Derniers indicateurs |
| `GET /api/v1/analysis/correlations` | `useCorrelations()` | Matrice corrélation |
| `GET /api/v1/analysis/stats` | `useAllStats()` | Stats tous ETF |
| `GET /api/v1/ml/regime` | `useRegime()` | Régime actuel (HMM) |
| `GET /api/v1/ml/portfolio` | `usePortfolio()` | Poids optimaux (Markowitz) |

---

## Configuration

### Variables d'environnement

```env
# web/.env.local (développement)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Vercel (production)
NEXT_PUBLIC_API_URL=https://deeppilote.onrender.com
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

## Déploiement

### Frontend : Vercel

1. Connecter le repo GitHub
2. Root Directory : `web`
3. Variable : `NEXT_PUBLIC_API_URL=https://deeppilote.onrender.com`
4. Deploy

**URL** : https://deep-pilote.vercel.app

### Backend : Render

1. Connecter le repo GitHub
2. Build Command : `pip install -r requirements.txt`
3. Start Command : `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
4. Variables :
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SUPABASE_DB_URL`

**URL** : https://deeppilote.onrender.com

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
2. Monitoring Sentry
3. UptimeRobot pour surveillance
4. Procédures d'incident

---

## Compétences validées

| Code | Compétence | Validation |
|------|------------|------------|
| C10 | Intégrer l'API d'un modèle d'IA dans une application | React Query + FastAPI ML endpoints |
| C14 | Analyser le besoin d'application | Pages et fonctionnalités définies |
| C15 | Concevoir le cadre technique | Architecture Next.js + API |
| C17 | Développer les composants et interfaces | 7 pages + composants réutilisables |
