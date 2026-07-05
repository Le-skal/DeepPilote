'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { useBacktest, useYearlyReturns } from '@/hooks';
import { formatPercent } from '@/lib/utils/formatters';
import { cn } from '@/lib/utils';
import {
  Trophy,
  TrendingUp,
  Activity,
  Shield,
  HelpCircle,
  BarChart3,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

// Couleurs pour les benchmarks
const BENCHMARK_COLORS: Record<string, string> = {
  SPY: '#22C55E', // Vert
  QQQ: '#3B82F6', // Bleu
  '60/40': '#F59E0B', // Orange
  'Equal Weight': '#A855F7', // Violet
};

/**
 * Carte de métriques pour un benchmark.
 */
function BenchmarkCard({
  name,
  metrics,
  rank,
}: {
  name: string;
  metrics: {
    total_return: number;
    cagr: number;
    volatility: number;
    sharpe: number;
    max_drawdown: number;
    win_rate: number;
  };
  rank: number;
}) {
  const color = BENCHMARK_COLORS[name] || '#A855F7';
  const isTopPerformer = rank === 1;

  return (
    <Card
      className={cn(
        'relative overflow-hidden transition-all',
        isTopPerformer && 'ring-2 ring-primary'
      )}
    >
      {isTopPerformer && (
        <div className="absolute top-2 right-2">
          <Trophy className="h-5 w-5 text-yellow-500" />
        </div>
      )}
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-sm"
            style={{ backgroundColor: color }}
          />
          <CardTitle className="text-lg">{name}</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Return total */}
        <div className="flex justify-between items-center">
          <span className="text-sm text-muted-foreground">Return Total</span>
          <span
            className={cn(
              'font-mono font-bold',
              metrics.total_return >= 0 ? 'text-green-500' : 'text-red-500'
            )}
          >
            {formatPercent(metrics.total_return)}
          </span>
        </div>

        {/* CAGR */}
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-1">
            <span className="text-sm text-muted-foreground">CAGR</span>
            <Tooltip>
              <TooltipTrigger className="cursor-help">
                <HelpCircle className="h-3 w-3 text-muted-foreground/50" />
              </TooltipTrigger>
              <TooltipContent>
                Rendement annualisé moyen (Compound Annual Growth Rate)
              </TooltipContent>
            </Tooltip>
          </div>
          <span className="font-mono">{formatPercent(metrics.cagr)}</span>
        </div>

        {/* Sharpe */}
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-1">
            <span className="text-sm text-muted-foreground">Sharpe</span>
            <Tooltip>
              <TooltipTrigger className="cursor-help">
                <HelpCircle className="h-3 w-3 text-muted-foreground/50" />
              </TooltipTrigger>
              <TooltipContent>
                Rendement ajusté du risque. Plus c&apos;est haut, mieux c&apos;est. &gt;1 = bon
              </TooltipContent>
            </Tooltip>
          </div>
          <span
            className={cn(
              'font-mono font-bold',
              metrics.sharpe >= 1
                ? 'text-green-500'
                : metrics.sharpe >= 0.5
                ? 'text-yellow-500'
                : 'text-red-500'
            )}
          >
            {metrics.sharpe.toFixed(2)}
          </span>
        </div>

        {/* Volatilité */}
        <div className="flex justify-between items-center">
          <span className="text-sm text-muted-foreground">Volatilité</span>
          <span className="font-mono">{metrics.volatility.toFixed(1)}%</span>
        </div>

        {/* Max Drawdown */}
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-1">
            <span className="text-sm text-muted-foreground">Max Drawdown</span>
            <Tooltip>
              <TooltipTrigger className="cursor-help">
                <HelpCircle className="h-3 w-3 text-muted-foreground/50" />
              </TooltipTrigger>
              <TooltipContent>
                Pire chute depuis un sommet. C&apos;est le pire moment possible.
              </TooltipContent>
            </Tooltip>
          </div>
          <span className="font-mono text-red-500">
            {formatPercent(metrics.max_drawdown)}
          </span>
        </div>

        {/* Win Rate */}
        <div className="flex justify-between items-center">
          <span className="text-sm text-muted-foreground">Jours positifs</span>
          <span className="font-mono">{metrics.win_rate}%</span>
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Graphique de comparaison des performances cumulées.
 */
function PerformanceChart({
  data,
}: {
  data: Record<string, { date: string; value: number }[]>;
}) {
  // Transformer les données pour Recharts
  const chartData: { date: string; [key: string]: string | number }[] = [];
  const allDates = new Set<string>();

  // Collecter toutes les dates
  Object.values(data).forEach((series) => {
    series.forEach((point) => allDates.add(point.date));
  });

  // Créer les points de données
  Array.from(allDates)
    .sort()
    .forEach((date) => {
      const point: { date: string; [key: string]: string | number } = { date };
      Object.entries(data).forEach(([name, series]) => {
        const found = series.find((p) => p.date === date);
        if (found) {
          point[name] = found.value;
        }
      });
      chartData.push(point);
    });

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#333" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 11, fill: '#888' }}
          tickFormatter={(value) => {
            const date = new Date(value);
            return date.toLocaleDateString('fr-FR', {
              month: 'short',
              year: '2-digit',
            });
          }}
        />
        <YAxis
          tick={{ fontSize: 11, fill: '#888' }}
          tickFormatter={(value) => `${value}`}
          domain={['auto', 'auto']}
        />
        <RechartsTooltip
          contentStyle={{
            backgroundColor: 'rgba(20, 20, 30, 0.95)',
            border: '1px solid rgba(168, 85, 247, 0.3)',
            borderRadius: '0',
          }}
          labelFormatter={(label) =>
            new Date(label).toLocaleDateString('fr-FR', {
              year: 'numeric',
              month: 'long',
            })
          }
          formatter={(value) => [
            typeof value === 'number' ? value.toFixed(0) : String(value),
          ]}
        />
        <Legend />
        {Object.keys(data).map((name) => (
          <Line
            key={name}
            type="monotone"
            dataKey={name}
            stroke={BENCHMARK_COLORS[name] || '#A855F7'}
            strokeWidth={2}
            dot={false}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

/**
 * Tableau des returns annuels.
 */
function YearlyReturnsTable({
  years,
  benchmarks,
}: {
  years: string[];
  benchmarks: Record<string, Record<string, number>>;
}) {
  const benchmarkNames = Object.keys(benchmarks);

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border">
            <th className="p-3 text-left font-medium">Année</th>
            {benchmarkNames.map((name) => (
              <th key={name} className="p-3 text-right font-medium">
                <div className="flex items-center justify-end gap-2">
                  <div
                    className="w-2 h-2 rounded-sm"
                    style={{ backgroundColor: BENCHMARK_COLORS[name] || '#A855F7' }}
                  />
                  {name}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {years.map((year) => (
            <tr key={year} className="border-b border-border/50 hover:bg-muted/30">
              <td className="p-3 font-medium">{year}</td>
              {benchmarkNames.map((name) => {
                const value = benchmarks[name]?.[year];
                return (
                  <td
                    key={name}
                    className={cn(
                      'p-3 text-right font-mono',
                      value !== undefined && value >= 0
                        ? 'text-green-500'
                        : 'text-red-500'
                    )}
                  >
                    {value !== undefined ? formatPercent(value) : '-'}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function PerformancePage() {
  const [years, setYears] = useState(5);
  const { data: backtest, isLoading: backtestLoading } = useBacktest(years);
  const { data: yearlyData, isLoading: yearlyLoading } = useYearlyReturns(10);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
          <BarChart3 className="h-8 w-8 text-primary" />
          Performance vs Benchmarks
        </h1>
        <p className="text-muted-foreground max-w-2xl">
          Compare les stratégies d&apos;investissement. L&apos;objectif : battre le S&amp;P 500
          et le NASDAQ avec un meilleur ratio rendement/risque.
        </p>
      </div>

      {/* Sélecteur de période */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-muted-foreground">Période :</span>
        <div className="inline-flex items-center gap-0.5 p-1 bg-muted/50">
          {[1, 3, 5, 10].map((y) => (
            <button
              key={y}
              onClick={() => setYears(y)}
              className={cn(
                'px-3 py-1.5 text-xs font-medium transition-all',
                years === y
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted'
              )}
            >
              {y} an{y > 1 ? 's' : ''}
            </button>
          ))}
        </div>
      </div>

      {/* Période */}
      {backtest?.period && (
        <p className="text-sm text-muted-foreground">
          Données du {backtest.period.start} au {backtest.period.end} (
          {backtest.period.days?.toLocaleString()} jours de trading)
        </p>
      )}

      {/* Cartes de benchmarks */}
      {backtestLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-64" />
          ))}
        </div>
      ) : backtest?.benchmarks ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {backtest.benchmarks.map((bm, index) => (
            <BenchmarkCard key={bm.name} name={bm.name} metrics={bm} rank={index + 1} />
          ))}
        </div>
      ) : (
        <p className="text-muted-foreground">Pas de données disponibles</p>
      )}

      {/* Graphique de performance cumulée */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            Performance Cumulée (Base 100)
          </CardTitle>
        </CardHeader>
        <CardContent>
          {backtestLoading ? (
            <Skeleton className="h-[400px] w-full" />
          ) : backtest?.cumulative_returns &&
            Object.keys(backtest.cumulative_returns).length > 0 ? (
            <PerformanceChart data={backtest.cumulative_returns} />
          ) : (
            <p className="text-center text-muted-foreground py-10">
              Pas de données disponibles
            </p>
          )}
        </CardContent>
      </Card>

      {/* Tableau des returns annuels */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-primary" />
            Returns Annuels
          </CardTitle>
        </CardHeader>
        <CardContent>
          {yearlyLoading ? (
            <Skeleton className="h-[300px] w-full" />
          ) : yearlyData?.years && yearlyData.years.length > 0 ? (
            <YearlyReturnsTable
              years={yearlyData.years}
              benchmarks={yearlyData.benchmarks}
            />
          ) : (
            <p className="text-center text-muted-foreground py-10">
              Pas de données disponibles
            </p>
          )}
        </CardContent>
      </Card>

      {/* Explication */}
      <Card className="border-primary/30 bg-primary/5">
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <Shield className="h-6 w-6 text-primary flex-shrink-0 mt-1" />
            <div className="space-y-2">
              <h3 className="font-semibold">Comment lire ces résultats ?</h3>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>
                  <strong>Sharpe Ratio</strong> : Le meilleur indicateur. &gt;1 =
                  bon, &gt;1.5 = excellent. Il mesure le rendement par unité de
                  risque.
                </li>
                <li>
                  <strong>CAGR</strong> : Le rendement annuel moyen. C&apos;est ce que
                  tu gagnes par an en moyenne.
                </li>
                <li>
                  <strong>Max Drawdown</strong> : La pire chute. Si tu avais
                  investi au pire moment, voici ce que tu aurais perdu.
                </li>
                <li>
                  <strong>60/40</strong> : La stratégie classique (60% actions, 40%
                  obligations). C&apos;est le benchmark classique.
                </li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
