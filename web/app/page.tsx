'use client';

import { StatCard } from '@/components/cards/StatCard';
import { RegimeIndicator } from '@/components/cards/RegimeIndicator';
import { ETFCard } from '@/components/cards/ETFCard';
import { Skeleton } from '@/components/ui/skeleton';
import { useETFs, useAllStats, useMacroLatest, useRegime } from '@/hooks';
import { TrendingUp, Activity, BarChart2 } from 'lucide-react';
import { formatPercent } from '@/lib/utils/formatters';
import { ETF_TICKERS } from '@/lib/utils/constants';

export default function DashboardPage() {
  const { data: etfsData, isLoading: etfsLoading } = useETFs();
  const { data: statsData, isLoading: statsLoading } = useAllStats();
  const { data: macroData, isLoading: macroLoading } = useMacroLatest();
  const { data: regimeData, isLoading: regimeLoading } = useRegime();

  // Trouver les stats pour les ETFs principaux
  const portfolioStats = statsData?.stats.filter((s) =>
    ETF_TICKERS.includes(s.ticker as (typeof ETF_TICKERS)[number])
  );

  // Calculer les métriques agrégées
  const avgReturn =
    portfolioStats && portfolioStats.length > 0
      ? portfolioStats.reduce((sum, s) => sum + s.total_return, 0) /
        portfolioStats.length
      : null;

  const avgSharpe =
    portfolioStats && portfolioStats.length > 0
      ? portfolioStats.reduce((sum, s) => sum + (s.sharpe_ratio ?? 0), 0) /
        portfolioStats.length
      : null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Vue d&apos;ensemble du portefeuille DeepPilot
        </p>
      </div>

      {/* Stats principales */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* Régime de marché */}
        {regimeLoading ? (
          <Skeleton className="h-32" />
        ) : (
          <RegimeIndicator
            regime={regimeData?.regime ?? 'stable'}
            confidence={regimeData?.confidence ?? 0}
          />
        )}

        {/* VIX */}
        {macroLoading ? (
          <Skeleton className="h-32" />
        ) : (
          <StatCard
            title="VIX"
            value={macroData?.vix?.toFixed(1) ?? '-'}
            subtitle={
              macroData?.vix && macroData.vix < 20
                ? 'Marché calme'
                : macroData?.vix && macroData.vix < 30
                ? 'Volatilité modérée'
                : 'Volatilité élevée'
            }
            icon={Activity}
            trend={
              macroData?.vix
                ? macroData.vix < 20
                  ? 'up'
                  : macroData.vix > 30
                  ? 'down'
                  : 'neutral'
                : undefined
            }
          />
        )}

        {/* Return moyen */}
        {statsLoading ? (
          <Skeleton className="h-32" />
        ) : (
          <StatCard
            title="Return moyen (ETFs)"
            value={avgReturn !== null ? formatPercent(avgReturn) : '-'}
            subtitle="Sur la période"
            icon={TrendingUp}
            trend={
              avgReturn !== null
                ? avgReturn > 0
                  ? 'up'
                  : avgReturn < 0
                  ? 'down'
                  : 'neutral'
                : undefined
            }
          />
        )}

        {/* Sharpe moyen */}
        {statsLoading ? (
          <Skeleton className="h-32" />
        ) : (
          <StatCard
            title="Sharpe moyen"
            value={avgSharpe !== null ? avgSharpe.toFixed(2) : '-'}
            subtitle={
              avgSharpe !== null
                ? avgSharpe > 1
                  ? 'Excellent'
                  : avgSharpe > 0.5
                  ? 'Bon'
                  : 'Faible'
                : undefined
            }
            icon={BarChart2}
          />
        )}
      </div>

      {/* Indicateurs macro */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Indicateurs Macro</h2>
        <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
          {macroLoading ? (
            Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-24" />
            ))
          ) : (
            <>
              <StatCard
                title="Taux 10Y"
                value={macroData?.t10y ? `${macroData.t10y.toFixed(2)}%` : '-'}
              />
              <StatCard
                title="Taux 3M"
                value={macroData?.t3mo ? `${macroData.t3mo.toFixed(2)}%` : '-'}
              />
              <StatCard
                title="Yield Curve"
                value={macroData?.yield_curve_10y2y ? `${macroData.yield_curve_10y2y.toFixed(2)}%` : '-'}
                trend={
                  macroData?.yield_curve_10y2y
                    ? macroData.yield_curve_10y2y < 0
                      ? 'down'
                      : 'up'
                    : undefined
                }
              />
              <StatCard
                title="Credit Spread"
                value={macroData?.credit_spread ? `${macroData.credit_spread.toFixed(0)} bps` : '-'}
              />
              <StatCard
                title="WTI Oil"
                value={macroData?.oil_wti ? `$${macroData.oil_wti.toFixed(0)}` : '-'}
              />
              <StatCard
                title="Date"
                value={macroData?.as_of_date ?? '-'}
              />
            </>
          )}
        </div>
      </div>

      {/* Liste des ETFs */}
      <div>
        <h2 className="text-xl font-semibold mb-4">ETFs du Portefeuille</h2>
        {etfsLoading || statsLoading ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <Skeleton key={i} className="h-48" />
            ))}
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {etfsData?.etfs
              .filter((etf) =>
                ETF_TICKERS.includes(etf.ticker as (typeof ETF_TICKERS)[number])
              )
              .map((etf) => {
                const stats = statsData?.stats.find(
                  (s) => s.ticker === etf.ticker
                );
                return <ETFCard key={etf.ticker} etf={etf} stats={stats} />;
              })}
          </div>
        )}
      </div>
    </div>
  );
}
