'use client';

import { ETFCard } from '@/components/cards/ETFCard';
import { Skeleton } from '@/components/ui/skeleton';
import { useETFs, useAllStats } from '@/hooks';
import { ETF_TICKERS, BENCHMARK_TICKERS } from '@/lib/utils/constants';

export default function ETFsPage() {
  const { data: etfsData, isLoading: etfsLoading, error: etfsError } = useETFs();
  const { data: statsData, isLoading: statsLoading } = useAllStats();

  const isLoading = etfsLoading || statsLoading;

  // Séparer les ETFs du portefeuille et les benchmarks
  const portfolioETFs = etfsData?.etfs.filter((etf) =>
    ETF_TICKERS.includes(etf.ticker as (typeof ETF_TICKERS)[number])
  );

  const benchmarkETFs = etfsData?.etfs.filter((etf) =>
    BENCHMARK_TICKERS.includes(etf.ticker as (typeof BENCHMARK_TICKERS)[number])
  );

  if (etfsError) {
    return (
      <div className="text-center py-10">
        <p className="text-red-500">Erreur de chargement des données</p>
        <p className="text-muted-foreground text-sm mt-2">
          Vérifiez que l&apos;API backend est lancée (python scripts/run_api.py)
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">ETFs</h1>
        <p className="text-muted-foreground">
          Les 8 ETFs du portefeuille DeepPilot + benchmarks de comparaison
        </p>
      </div>

      {/* ETFs du portefeuille */}
      <section>
        <h2 className="text-xl font-semibold mb-4">Portefeuille (8 ETFs)</h2>
        {isLoading ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <Skeleton key={i} className="h-48" />
            ))}
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {portfolioETFs?.map((etf) => {
              const stats = statsData?.stats.find((s) => s.ticker === etf.ticker);
              return <ETFCard key={etf.ticker} etf={etf} stats={stats} />;
            })}
          </div>
        )}
      </section>

      {/* Benchmarks */}
      <section>
        <h2 className="text-xl font-semibold mb-4">Benchmarks</h2>
        {isLoading ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 2 }).map((_, i) => (
              <Skeleton key={i} className="h-48" />
            ))}
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {benchmarkETFs?.map((etf) => {
              const stats = statsData?.stats.find((s) => s.ticker === etf.ticker);
              return <ETFCard key={etf.ticker} etf={etf} stats={stats} />;
            })}
          </div>
        )}
      </section>
    </div>
  );
}
