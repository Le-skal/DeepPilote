# DeepPilot Web

Application Next.js 14 pour visualiser les donnees du projet DeepPilot.

## Stack technique

- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS** + **shadcn/ui**
- **React Query** (@tanstack/react-query)
- **Recharts** (graphiques)

## Installation

```bash
cd web
npm install
```

## Configuration

Creer un fichier `.env.local` :

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Lancement

```bash
# Lancer l'API backend (dans un autre terminal)
python scripts/run_api.py

# Lancer le frontend
npm run dev
```

Ouvrir http://localhost:3000

## Pages

| Route | Description |
|-------|-------------|
| `/` | Dashboard (regime, VIX, stats) |
| `/etfs` | Liste des 8 ETF + benchmarks |
| `/etfs/[ticker]` | Detail ETF (prix, stats, features) |
| `/market` | Indicateurs macroeconomiques |
| `/analysis` | Correlations et statistiques |
| `/portfolio` | Allocations recommandees |
| `/about` | Disclaimer legal |

## Structure

```
web/
├── app/              # Pages (App Router)
├── components/
│   ├── layout/       # Header, Footer
│   ├── cards/        # StatCard, ETFCard, RegimeIndicator
│   ├── charts/       # PriceChart
│   └── ui/           # shadcn/ui
├── hooks/            # React Query hooks
├── lib/
│   ├── api/          # Client API
│   └── utils/        # Formatters, constantes
├── types/            # Types TypeScript
└── providers/        # QueryProvider
```

## Build

```bash
npm run build
```

## Deploiement

Le deploiement sur Vercel sera configure en Phase 7.
