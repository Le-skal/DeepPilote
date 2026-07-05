'use client';

import { useState, useMemo } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { PriceChart } from '@/components/charts/PriceChart';
import { useETF, useETFPrices, useETFStats } from '@/hooks';
import {
  formatPercent,
  formatCurrency,
  formatDateReadable,
  getDateRangeFromPeriod,
} from '@/lib/utils/formatters';
import {
  ETF_COLORS,
  ASSET_CLASSES,
  TimePeriod,
  METRIC_EXPLANATIONS,
  getSharpeLabel,
} from '@/lib/utils/constants';
import {
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  Activity,
  HelpCircle,
  ChevronDown,
  Shield,
  BarChart3,
  Calendar,
} from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Card de statistique avec explication intégrée.
 */
function StatCardWithExplanation({
  title,
  value,
  subtitle,
  metricKey,
  trend,
  icon: Icon,
}: {
  title: string;
  value: string;
  subtitle?: string;
  metricKey?: string;
  trend?: 'up' | 'down' | 'neutral';
  icon?: React.ElementType;
}) {
  const explanation = metricKey ? METRIC_EXPLANATIONS[metricKey] : null;

  return (
    <Card className="relative overflow-hidden">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-1">
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                {title}
              </p>
              {explanation && (
                <Tooltip>
                  <TooltipTrigger className="cursor-help">
                    <HelpCircle className="h-3 w-3 text-muted-foreground/50" />
                  </TooltipTrigger>
                  <TooltipContent side="top" className="max-w-xs">
                    <p className="font-medium text-sm">{explanation.short}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {explanation.long}
                    </p>
                    {explanation.example && (
                      <p className="text-xs text-muted-foreground/80 mt-1 italic">
                        {explanation.example}
                      </p>
                    )}
                  </TooltipContent>
                </Tooltip>
              )}
            </div>
            <p
              className={cn(
                'text-2xl font-bold font-mono',
                trend === 'up' && 'text-green-500',
                trend === 'down' && 'text-red-500'
              )}
            >
              {value}
            </p>
            {subtitle && (
              <p className="text-xs text-muted-foreground">{subtitle}</p>
            )}
          </div>
          {Icon && (
            <div className="p-2  bg-primary/10">
              <Icon className="h-4 w-4 text-primary" />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default function ETFDetailPage() {
  const params = useParams();
  const ticker = params.ticker as string;

  // État pour la période sélectionnée
  const [period, setPeriod] = useState<TimePeriod>('MAX');

  // Calculer la plage de dates
  const dateRange = useMemo(() => getDateRangeFromPeriod(period), [period]);

  // Récupérer les données avec la plage de dates
  const { data: etf, isLoading: etfLoading, error: etfError } = useETF(ticker);
  const { data: pricesData, isLoading: pricesLoading } = useETFPrices(
    ticker,
    dateRange
  );
  const { data: stats, isLoading: statsLoading } = useETFStats(ticker, dateRange);

  // État pour les stats avancées
  const [showAdvanced, setShowAdvanced] = useState(false);

  const color = ETF_COLORS[ticker] || '#A855F7';
  const assetClass = ASSET_CLASSES[ticker as keyof typeof ASSET_CLASSES];

  if (etfError) {
    return (
      <div className="text-center py-10">
        <p className="text-red-500">ETF non trouvé: {ticker}</p>
        <Link
          href="/etfs"
          className="text-primary hover:underline mt-4 inline-block"
        >
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
        className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="h-4 w-4 mr-1" />
        Retour aux ETFs
      </Link>

      {/* Header */}
      {etfLoading ? (
        <Skeleton className="h-24 w-full" />
      ) : (
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div>
            <div className="flex items-center space-x-3">
              <div
                className="w-4 h-4 rounded-full shadow-glow"
                style={{ backgroundColor: color }}
              />
              <h1 className="text-3xl font-bold tracking-tight">{ticker}</h1>
              {stats &&
                (stats.total_return >= 0 ? (
                  <TrendingUp className="h-6 w-6 text-green-500" />
                ) : (
                  <TrendingDown className="h-6 w-6 text-red-500" />
                ))}
            </div>
            <p className="text-lg text-muted-foreground mt-1">{etf?.name}</p>
            {assetClass && (
              <Badge variant="secondary" className="mt-2">
                {assetClass}
              </Badge>
            )}
          </div>
          {stats && (
            <div className="text-left sm:text-right">
              <p className="text-3xl font-bold font-mono">
                {formatCurrency(stats.last_price)}
              </p>
              <p className="text-sm text-muted-foreground mt-1">
                Prix actuel au {formatDateReadable(stats.end_date)}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Price Chart with Period Selector */}
      <Card>
        <CardContent className="pt-6">
          {pricesLoading ? (
            <Skeleton className="h-[400px] w-full" />
          ) : pricesData?.prices && pricesData.prices.length > 0 ? (
            <PriceChart
              data={pricesData.prices}
              ticker={ticker}
              height={400}
              showHeader
              period={period}
              onPeriodChange={setPeriod}
              periodReturn={stats?.total_return}
              periodStartDate={stats?.start_date}
              title="Performance"
            />
          ) : (
            <p className="text-center text-muted-foreground py-10">
              Pas de données disponibles pour cette période
            </p>
          )}
        </CardContent>
      </Card>

      {/* Stats essentielles - Toujours visibles */}
      <div>
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-primary" />
          Métriques essentielles
        </h2>
        <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
          {statsLoading ? (
            Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-24" />
            ))
          ) : stats ? (
            <>
              <StatCardWithExplanation
                title="Return total"
                metricKey="total_return"
                value={formatPercent(stats.total_return)}
                subtitle={`Depuis ${formatDateReadable(stats.start_date)}`}
                trend={stats.total_return >= 0 ? 'up' : 'down'}
                icon={TrendingUp}
              />
              <StatCardWithExplanation
                title="Return annualisé"
                metricKey="annualized_return"
                value={formatPercent(stats.annualized_return)}
                subtitle="Moyenne par an"
                trend={stats.annualized_return >= 0 ? 'up' : 'down'}
              />
              <StatCardWithExplanation
                title="Sharpe Ratio"
                metricKey="sharpe_ratio"
                value={stats.sharpe_ratio?.toFixed(2) ?? '-'}
                subtitle={getSharpeLabel(stats.sharpe_ratio)}
              />
              <StatCardWithExplanation
                title="Volatilité"
                metricKey="volatility"
                value={stats.annualized_volatility.toFixed(1) + '%'}
                subtitle="Variation annuelle"
                icon={Activity}
              />
            </>
          ) : null}
        </div>
      </div>

      {/* Stats de risque */}
      <div>
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Shield className="h-5 w-5 text-primary" />
          Indicateurs de risque
        </h2>
        <div className="grid gap-4 grid-cols-2 lg:grid-cols-3">
          {statsLoading ? (
            Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-24" />
            ))
          ) : stats ? (
            <>
              <StatCardWithExplanation
                title="Pire chute (Max Drawdown)"
                metricKey="max_drawdown"
                value={formatPercent(stats.max_drawdown)}
                subtitle="Perte maximale depuis un sommet"
                trend="down"
              />
              <StatCardWithExplanation
                title="Pire jour"
                metricKey="worst_day"
                value={formatPercent(stats.worst_day)}
                subtitle="Plus grosse baisse en un jour"
                trend="down"
              />
              <StatCardWithExplanation
                title="Meilleur jour"
                metricKey="best_day"
                value={formatPercent(stats.best_day)}
                subtitle="Plus grosse hausse en un jour"
                trend="up"
              />
            </>
          ) : null}
        </div>
      </div>

      {/* Stats avancées - Collapsible */}
      <div>
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ChevronDown
            className={cn(
              'h-4 w-4 transition-transform',
              showAdvanced && 'rotate-180'
            )}
          />
          {showAdvanced ? 'Masquer' : 'Voir'} les statistiques avancées
        </button>

        {showAdvanced && stats && (
          <div className="grid gap-4 grid-cols-2 lg:grid-cols-4 mt-4">
            <StatCardWithExplanation
              title="Jours positifs"
              metricKey="positive_days_pct"
              value={stats.positive_days_pct.toFixed(1) + '%'}
              subtitle="Jours où le prix a monté"
            />
            <StatCardWithExplanation
              title="Observations"
              value={stats.count.toLocaleString()}
              subtitle="Nombre de jours de données"
              icon={Calendar}
            />
            <StatCardWithExplanation
              title="Prix minimum"
              value={formatCurrency(stats.min_price)}
              subtitle="Plus bas sur la période"
            />
            <StatCardWithExplanation
              title="Prix maximum"
              value={formatCurrency(stats.max_price)}
              subtitle="Plus haut sur la période"
            />
          </div>
        )}
      </div>

      {/* Description */}
      {etf?.description && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <HelpCircle className="h-5 w-5 text-primary" />
              À propos de {ticker}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground leading-relaxed">
              {etf.description}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
