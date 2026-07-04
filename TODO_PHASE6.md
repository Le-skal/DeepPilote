# TODO Phase 6 — Application Next.js

**Status** : ✅ Terminée
**Date** : 4 juillet 2026
**Compétences validées** : C10, C14, C15, C17

---

## Objectif

Créer une application Next.js 14 pour visualiser les données du projet DeepPilot (ETF, macro, régimes ML, portfolio).

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

## Étapes réalisées

### Phase A : Setup ✅
- [x] `npx create-next-app@14 web --typescript --tailwind --app`
- [x] Installer deps : `@tanstack/react-query recharts lucide-react`
- [x] Init shadcn/ui avec theme cyberpunk
- [x] Configurer `.env.local` avec `NEXT_PUBLIC_API_URL`

### Phase B : Infrastructure ✅
- [x] Types TypeScript (`types/api.ts`) miroir des schemas Pydantic
- [x] Client API (`lib/api/client.ts`, `etfs.ts`, `macro.ts`, `analysis.ts`, `ml.ts`)
- [x] Setup React Query provider
- [x] Hooks (`useETFs`, `useMacro`, `useAnalysis`, `useRegime`, `usePortfolio`)
- [x] Layout (Header, Footer) avec design cyberpunk

### Phase C : Dashboard ✅
- [x] StatCard component avec glow effects
- [x] RegimeIndicator component (dynamique depuis API ML)
- [x] Page Dashboard assemblée avec données réelles

### Phase D : ETF Pages ✅
- [x] ETFCard + ETFTable components
- [x] Page liste ETF `/etfs`
- [x] PriceChart component (Recharts LineChart)
- [x] Page détail ETF `/etfs/[ticker]`

### Phase E : Analysis ✅
- [x] CorrelationHeatmap (CSS Grid coloré)
- [x] StatsTable component
- [x] Page Analysis

### Phase F : Market + Portfolio ✅
- [x] RegimeIndicator avec probabilités
- [x] Page Market (régime ML + indicateurs macro)
- [x] Page Portfolio (poids optimaux calculés par API ML)
- [x] Plus de données mockées !

### Phase G : API ML ✅
- [x] Endpoint `/api/v1/ml/regime` (régime HMM en temps réel)
- [x] Endpoint `/api/v1/ml/portfolio` (poids optimaux Markowitz)
- [x] Service ML (`api/services/ml_service.py`)
- [x] Hooks React Query (`useRegime`, `usePortfolio`)

### Phase H : Finitions ✅
- [x] Page About (disclaimer légal)
- [x] Loading/error states avec Skeleton
- [x] Design Cyberpunk Finance (dark, cyan/magenta accents, minimal border-radius)
- [x] Déploiement Vercel + Render
- [x] CORS configuré pour production

---

## Pages créées

| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/` | Vue d'ensemble (régime ML, VIX, stats ETF) |
| ETFs | `/etfs` | Liste des 8 ETF + 2 benchmarks |
| Détail ETF | `/etfs/[ticker]` | Prix historique, stats, features ML |
| Market | `/market` | Indicateurs macro, régimes ML, probabilités |
| Analysis | `/analysis` | Matrice de corrélation, statistiques |
| Portfolio | `/portfolio` | Allocations optimales (API ML Markowitz) |
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
│   └── ui/                # shadcn/ui
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
│   │   ├── etfs.ts        # ETF API
│   │   ├── macro.ts       # Macro API
│   │   ├── analysis.ts    # Analysis API
│   │   └── ml.ts          # ML API (régime, portfolio)
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

## Endpoints API utilisés

| Endpoint | Hook | Usage |
|----------|------|-------|
| `GET /api/v1/etfs` | `useETFs()` | Liste des ETF |
| `GET /api/v1/etfs/{ticker}` | `useETF(ticker)` | Détail ETF |
| `GET /api/v1/etfs/{ticker}/prices` | `useETFPrices(ticker)` | Prix historiques |
| `GET /api/v1/etfs/{ticker}/features` | `useETFFeatures(ticker)` | Features ML |
| `GET /api/v1/macro/latest` | `useMacroLatest()` | Derniers indicateurs |
| `GET /api/v1/analysis/correlations` | `useCorrelations()` | Matrice corrélation |
| `GET /api/v1/analysis/stats` | `useAllStats()` | Stats tous ETF |
| `GET /api/v1/ml/regime` | `useRegime()` | Régime HMM actuel |
| `GET /api/v1/ml/portfolio` | `usePortfolio()` | Poids optimaux Markowitz |

---

## Déploiement

### Frontend (Vercel)
- URL: https://deep-pilote.vercel.app
- Root Directory: `web`
- Framework: Next.js (auto-détecté)
- Variable: `NEXT_PUBLIC_API_URL=https://deeppilote.onrender.com`

### Backend (Render)
- URL: https://deeppilote.onrender.com
- Build: `pip install -r requirements.txt`
- Start: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- Variables: `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_DB_URL`

---

## Design

**Theme Cyberpunk Finance** :
- Palette sombre avec accents cyan/magenta
- Effets glow sur les cartes
- Font mono pour les valeurs numériques
- Border-radius minimal (style finance pro)
- Couleurs sémantiques : vert (bull), rouge (bear), jaune (volatile), bleu (stable)

---

## Tests

```bash
# Build local
cd web && npm run build

# Dev
npm run dev
# → http://localhost:3000
```

---

## Compétences validées

| Code | Compétence | Validation |
|------|------------|------------|
| C10 | Intégrer l'API d'un modèle d'IA dans une application | React Query + FastAPI ML endpoints |
| C14 | Analyser le besoin d'application | Pages et fonctionnalités définies |
| C15 | Concevoir le cadre technique | Architecture Next.js + FastAPI |
| C17 | Développer les composants et interfaces | 7 pages + composants réutilisables |
