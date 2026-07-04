'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { StatCard } from '@/components/cards/StatCard';
import { PriceChart } from '@/components/charts/PriceChart';
import { useETF, useETFPrices, useETFStats } from '@/hooks';
import { formatPercent, formatCurrency, getValueColor } from '@/lib/utils/formatters';
import { ETF_COLORS, ASSET_CLASSES } from '@/lib/utils/constants';
import { ArrowLeft, TrendingUp, TrendingDown, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function ETFDetailPage() {
  const params = useParams();
  const ticker = params.ticker as string;

  const { data: etf, isLoading: etfLoading, error: etfError } = useETF(ticker);
  const { data: pricesData, isLoading: pricesLoading } = useETFPrices(ticker, {
    limit: 500, // Derniers 500 jours (~2 ans)
  });
  const { data: stats, isLoading: statsLoading } = useETFStats(ticker);

  const color = ETF_COLORS[ticker] || '#3B82F6';
  const assetClass = ASSET_CLASSES[ticker as keyof typeof ASSET_CLASSES];

  if (etfError) {
    return (
      <div className="text-center py-10">
        <p className="text-red-500">ETF non trouvé: {ticker}</p>
        <Link href="/etfs" className="text-primary hover:underline mt-4 inline-block">
          Retour à la liste
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back link */}
      <Link
        href="/etfs"
        className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4 mr-1" />
        Retour aux ETFs
      </Link>

      {/* Header */}
      {etfLoading ? (
        <Skeleton className="h-20 w-full" />
      ) : (
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center space-x-3">
              <div
                className="w-4 h-4 rounded-full"
                style={{ backgroundColor: color }}
              />
              <h1 className="text-3xl font-bold tracking-tight">{ticker}</h1>
              {stats && (
                stats.total_return >= 0 ? (
                  <TrendingUp className="h-6 w-6 text-green-600" />
                ) : (
                  <TrendingDown className="h-6 w-6 text-red-600" />
                )
              )}
            </div>
            <p className="text-lg text-muted-foreground mt-1">{etf?.name}</p>
            {assetClass && (
              <Badge variant="secondary" className="mt-2">
                {assetClass}
              </Badge>
            )}
          </div>
          {stats && (
            <div className="text-right">
              <p className="text-3xl font-bold">
                {formatCurrency(stats.last_price)}
              </p>
              <p className={cn('text-lg', getValueColor(stats.total_return))}>
                {formatPercent(stats.total_return)}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Price Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Historique des prix</CardTitle>
        </CardHeader>
        <CardContent>
          {pricesLoading ? (
            <Skeleton className="h-[300px] w-full" />
          ) : pricesData?.prices && pricesData.prices.length > 0 ? (
            <PriceChart data={pricesData.prices} ticker={ticker} height={300} />
          ) : (
            <p className="text-center text-muted-foreground py-10">
              Pas de données disponibles
            </p>
          )}
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statsLoading ? (
          Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))
        ) : stats ? (
          <>
            <StatCard
              title="Return annualisé"
              value={formatPercent(stats.annualized_return)}
              trend={stats.annualized_return >= 0 ? 'up' : 'down'}
              icon={TrendingUp}
            />
            <StatCard
              title="Volatilité"
              value={stats.annualized_volatility.toFixed(1) + '%'}
              icon={Activity}
            />
            <StatCard
              title="Sharpe Ratio"
              value={stats.sharpe_ratio?.toFixed(2) ?? '-'}
              subtitle={
                stats.sharpe_ratio
                  ? stats.sharpe_ratio > 1
                    ? 'Excellent'
                    : stats.sharpe_ratio > 0.5
                    ? 'Bon'
                    : 'Faible'
                  : undefined
              }
            />
            <StatCard
              title="Max Drawdown"
              value={formatPercent(stats.max_drawdown)}
              trend="down"
            />
            <StatCard
              title="Jours positifs"
              value={stats.positive_days_pct.toFixed(1) + '%'}
            />
            <StatCard
              title="Meilleur jour"
              value={formatPercent(stats.best_day)}
              trend="up"
            />
            <StatCard
              title="Pire jour"
              value={formatPercent(stats.worst_day)}
              trend="down"
            />
            <StatCard
              title="Observations"
              value={stats.count.toString()}
              subtitle={`${stats.start_date} → ${stats.end_date}`}
            />
          </>
        ) : null}
      </div>

      {/* Description */}
      {etf?.description && (
        <Card>
          <CardHeader>
            <CardTitle>Description</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">{etf.description}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
