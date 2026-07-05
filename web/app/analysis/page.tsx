'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { useCorrelations, useAllStats } from '@/hooks';
import { formatPercent, getValueColor } from '@/lib/utils/formatters';
import { cn } from '@/lib/utils';
import { HelpCircle, Grid3X3 } from 'lucide-react';

export default function AnalysisPage() {
  const { data: correlations, isLoading: correlationsLoading } = useCorrelations();
  const { data: statsData, isLoading: statsLoading } = useAllStats();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
          <Grid3X3 className="h-8 w-8 text-primary" />
          Analyse
        </h1>
        <p className="text-muted-foreground">
          Corrélations et statistiques comparatives des ETFs
        </p>
      </div>

      {/* Correlation Matrix */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <CardTitle>Matrice de Corrélation</CardTitle>
            <Tooltip>
              <TooltipTrigger className="cursor-help">
                <HelpCircle className="h-4 w-4 text-muted-foreground/50" />
              </TooltipTrigger>
              <TooltipContent className="max-w-xs">
                <p className="font-medium">Comment lire cette matrice ?</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Les corrélations vont de -1 à +1. Proche de +1 = les actifs bougent ensemble.
                  Proche de -1 = ils bougent en sens inverse (bon pour diversifier).
                  Proche de 0 = pas de relation.
                </p>
              </TooltipContent>
            </Tooltip>
          </div>
        </CardHeader>
        <CardContent>
          {correlationsLoading ? (
            <Skeleton className="h-[400px] w-full" />
          ) : correlations ? (
            <div className="overflow-x-auto">
              <div className="inline-block min-w-full">
                <table className="w-full border-collapse">
                  <thead>
                    <tr>
                      <th className="p-0 w-16"></th>
                      {correlations.tickers.map((ticker) => (
                        <th
                          key={ticker}
                          className="p-2 text-center font-mono text-xs font-bold text-primary min-w-[56px]"
                        >
                          {ticker}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {correlations.tickers.map((rowTicker, rowIndex) => (
                      <tr key={rowTicker}>
                        <td className="p-2 font-mono text-xs font-bold text-primary">
                          {rowTicker}
                        </td>
                        {correlations.matrix[rowIndex].map((value, colIndex) => {
                          const bgColor = getCorrelationBgColor(value);
                          const textColor = getCorrelationTextColor(value);
                          const isDiagonal = rowIndex === colIndex;
                          return (
                            <td
                              key={colIndex}
                              className="p-0"
                            >
                              <div
                                className={cn(
                                  'w-14 h-10 flex items-center justify-center font-mono text-xs font-medium transition-all',
                                  isDiagonal && 'opacity-50'
                                )}
                                style={{
                                  backgroundColor: bgColor,
                                  color: textColor,
                                }}
                              >
                                {isDiagonal ? '1.00' : value.toFixed(2)}
                              </div>
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {/* Légende */}
              <div className="flex items-center justify-center gap-6 mt-6 text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4" style={{ backgroundColor: 'hsl(145, 80%, 35%)' }} />
                  <span className="text-muted-foreground">-1.0 (Inverse)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4" style={{ backgroundColor: 'hsl(260, 20%, 20%)' }} />
                  <span className="text-muted-foreground">0 (Neutre)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4" style={{ backgroundColor: 'hsl(0, 80%, 45%)' }} />
                  <span className="text-muted-foreground">+1.0 (Corrélé)</span>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-10">
              Pas de données disponibles
            </p>
          )}
        </CardContent>
      </Card>

      {/* Stats Table */}
      <Card>
        <CardHeader>
          <CardTitle>Statistiques Comparatives</CardTitle>
        </CardHeader>
        <CardContent>
          {statsLoading ? (
            <Skeleton className="h-[300px] w-full" />
          ) : statsData ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="p-3 text-left font-medium">ETF</th>
                    <th className="p-3 text-right font-medium">Return</th>
                    <th className="p-3 text-right font-medium">Volatilité</th>
                    <th className="p-3 text-right font-medium">Sharpe</th>
                    <th className="p-3 text-right font-medium">Max DD</th>
                    <th className="p-3 text-right font-medium">Jours +</th>
                  </tr>
                </thead>
                <tbody>
                  {statsData.stats.map((stat) => (
                    <tr key={stat.ticker} className="border-b hover:bg-muted/50">
                      <td className="p-3 font-medium">{stat.ticker}</td>
                      <td
                        className={cn(
                          'p-3 text-right',
                          getValueColor(stat.total_return)
                        )}
                      >
                        {formatPercent(stat.total_return)}
                      </td>
                      <td className="p-3 text-right">
                        {stat.annualized_volatility.toFixed(1)}%
                      </td>
                      <td className="p-3 text-right">
                        {stat.sharpe_ratio?.toFixed(2) ?? '-'}
                      </td>
                      <td className="p-3 text-right text-red-600">
                        {formatPercent(stat.max_drawdown)}
                      </td>
                      <td className="p-3 text-right">
                        {stat.positive_days_pct.toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-10">
              Pas de données disponibles
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * Calcule la couleur de fond pour une valeur de corrélation.
 * Rouge = corrélation positive (mauvais pour diversification)
 * Vert = corrélation négative (bon pour diversification)
 */
function getCorrelationBgColor(value: number): string {
  // Normaliser entre -1 et 1
  const normalized = Math.max(-1, Math.min(1, value));

  if (normalized > 0) {
    // Rouge pour corrélation positive
    const intensity = Math.abs(normalized);
    const lightness = 45 - intensity * 20; // 45% -> 25%
    return `hsl(0, 80%, ${lightness}%)`;
  } else if (normalized < 0) {
    // Vert pour corrélation négative
    const intensity = Math.abs(normalized);
    const lightness = 35 - intensity * 15; // 35% -> 20%
    return `hsl(145, 80%, ${lightness}%)`;
  }
  // Neutre
  return 'hsl(260, 20%, 20%)';
}

/**
 * Couleur du texte pour contraste.
 */
function getCorrelationTextColor(value: number): string {
  const normalized = Math.abs(value);
  if (normalized > 0.5) {
    return 'white';
  }
  return 'hsl(0, 0%, 80%)';
}
