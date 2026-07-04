'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useCorrelations, useAllStats } from '@/hooks';
import { formatPercent, getValueColor } from '@/lib/utils/formatters';
import { cn } from '@/lib/utils';

export default function AnalysisPage() {
  const { data: correlations, isLoading: correlationsLoading } = useCorrelations();
  const { data: statsData, isLoading: statsLoading } = useAllStats();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Analyse</h1>
        <p className="text-muted-foreground">
          Corrélations et statistiques comparatives des ETFs
        </p>
      </div>

      {/* Correlation Matrix */}
      <Card>
        <CardHeader>
          <CardTitle>Matrice de Corrélation</CardTitle>
        </CardHeader>
        <CardContent>
          {correlationsLoading ? (
            <Skeleton className="h-[400px] w-full" />
          ) : correlations ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr>
                    <th className="p-2 text-left font-medium"></th>
                    {correlations.tickers.map((ticker) => (
                      <th
                        key={ticker}
                        className="p-2 text-center font-medium min-w-[60px]"
                      >
                        {ticker}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {correlations.tickers.map((rowTicker, rowIndex) => (
                    <tr key={rowTicker}>
                      <td className="p-2 font-medium">{rowTicker}</td>
                      {correlations.matrix[rowIndex].map((value, colIndex) => {
                        const color = getCorrelationColor(value);
                        return (
                          <td
                            key={colIndex}
                            className={cn(
                              'p-2 text-center text-xs font-mono',
                              color
                            )}
                          >
                            {value.toFixed(2)}
                          </td>
                        );
                      })}
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
          <p className="text-xs text-muted-foreground mt-4">
            Légende: Vert = corrélation négative (diversification), Rouge =
            corrélation positive
          </p>
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
 * Détermine la couleur de fond selon la corrélation.
 */
function getCorrelationColor(value: number): string {
  if (value >= 0.8) return 'bg-red-200 dark:bg-red-900/50';
  if (value >= 0.5) return 'bg-red-100 dark:bg-red-900/30';
  if (value >= 0.2) return 'bg-orange-100 dark:bg-orange-900/30';
  if (value >= -0.2) return 'bg-gray-100 dark:bg-gray-800';
  if (value >= -0.5) return 'bg-green-100 dark:bg-green-900/30';
  return 'bg-green-200 dark:bg-green-900/50';
}
