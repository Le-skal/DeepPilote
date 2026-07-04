'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { StatCard } from '@/components/cards/StatCard';
import { RegimeBadge } from '@/components/cards/RegimeIndicator';
import { usePortfolio, useRegime } from '@/hooks';
import { PieChart, TrendingUp } from 'lucide-react';
import { ETF_COLORS } from '@/lib/utils/constants';
import { formatPercent } from '@/lib/utils/formatters';

export default function PortfolioPage() {
  const { data: portfolioData, isLoading: portfolioLoading } = usePortfolio();
  const { data: regimeData, isLoading: regimeLoading } = useRegime();

  const isLoading = portfolioLoading || regimeLoading;

  // Calculer le total des poids pour vérification
  const totalWeight = portfolioData
    ? Object.values(portfolioData.weights).reduce((a, b) => a + b, 0)
    : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Portfolio</h1>
        <p className="text-muted-foreground">
          Allocation recommandée par le modèle DeepPilot
        </p>
      </div>

      {/* Régime et métriques */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Régime actuel
            </CardTitle>
          </CardHeader>
          <CardContent>
            {regimeLoading ? (
              <Skeleton className="h-8 w-24" />
            ) : (
              <RegimeBadge regime={regimeData?.regime ?? 'stable'} />
            )}
          </CardContent>
        </Card>

        {isLoading ? (
          <>
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
          </>
        ) : (
          <>
            <StatCard
              title="Return attendu"
              value={formatPercent(portfolioData?.expected_return ?? 0)}
              subtitle="Annualisé"
              icon={TrendingUp}
              trend="up"
            />

            <StatCard
              title="Volatilité"
              value={((portfolioData?.volatility ?? 0) * 100).toFixed(1) + '%'}
              subtitle="Annualisée"
            />

            <StatCard
              title="Sharpe Ratio"
              value={(portfolioData?.sharpe_ratio ?? 0).toFixed(2)}
              subtitle={
                (portfolioData?.sharpe_ratio ?? 0) > 0.5 ? 'Bon ratio' : 'Ratio faible'
              }
            />
          </>
        )}
      </div>

      {/* Allocation visuelle */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <PieChart className="h-5 w-5" />
            Allocation Recommandée
            {portfolioData && (
              <span className="text-sm font-normal text-muted-foreground ml-auto">
                Calculée le {portfolioData.as_of_date}
              </span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <Skeleton className="h-64" />
          ) : (
            <div className="grid gap-6 md:grid-cols-2">
              {/* Barres de progression */}
              <div className="space-y-4">
                {portfolioData &&
                  Object.entries(portfolioData.weights)
                    .sort(([, a], [, b]) => b - a)
                    .map(([ticker, weight]) => {
                      const color = ETF_COLORS[ticker] || '#6B7280';
                      const percentage = (weight * 100).toFixed(1);

                      return (
                        <div key={ticker} className="space-y-1">
                          <div className="flex justify-between text-sm">
                            <span className="font-medium">{ticker}</span>
                            <span className="text-muted-foreground">
                              {percentage}%
                            </span>
                          </div>
                          <div className="h-3 bg-muted rounded-full overflow-hidden">
                            <div
                              className="h-full rounded-full transition-all"
                              style={{
                                width: `${weight * 100}%`,
                                backgroundColor: color,
                              }}
                            />
                          </div>
                        </div>
                      );
                    })}
              </div>

              {/* Contraintes */}
              <div className="space-y-4">
                <h4 className="font-medium">Contraintes d&apos;optimisation</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-center gap-2">
                    <Badge variant="outline">Min 5%</Badge>
                    Poids minimum par ETF
                  </li>
                  <li className="flex items-center gap-2">
                    <Badge variant="outline">Max 25%</Badge>
                    Poids maximum par ETF
                  </li>
                  <li className="flex items-center gap-2">
                    <Badge variant="outline">Σ = 100%</Badge>
                    Somme des poids = 100%
                  </li>
                  <li className="flex items-center gap-2">
                    <Badge variant="outline">Mensuel</Badge>
                    Rebalancement mensuel
                  </li>
                </ul>

                <div className="pt-4 border-t">
                  <h4 className="font-medium mb-2">Méthodologie</h4>
                  <p className="text-sm text-muted-foreground">
                    Optimisation Markowitz (max Sharpe ratio) via scipy.optimize
                    avec prise en compte du régime de marché détecté par le modèle
                    HMM.
                  </p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Tableau détaillé */}
      <Card>
        <CardHeader>
          <CardTitle>Détail des Allocations</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <Skeleton className="h-64" />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="p-3 text-left font-medium">ETF</th>
                    <th className="p-3 text-right font-medium">Poids</th>
                    <th className="p-3 text-center font-medium">Min</th>
                    <th className="p-3 text-center font-medium">Max</th>
                    <th className="p-3 text-right font-medium">Valeur ($10k)</th>
                  </tr>
                </thead>
                <tbody>
                  {portfolioData &&
                    Object.entries(portfolioData.weights).map(([ticker, weight]) => {
                      const isAtMin = weight <= 0.05;
                      const isAtMax = weight >= 0.25;
                      const value = weight * 10000;

                      return (
                        <tr key={ticker} className="border-b hover:bg-muted/50">
                          <td className="p-3">
                            <div className="flex items-center gap-2">
                              <div
                                className="w-3 h-3 rounded-full"
                                style={{
                                  backgroundColor: ETF_COLORS[ticker] || '#6B7280',
                                }}
                              />
                              <span className="font-medium">{ticker}</span>
                            </div>
                          </td>
                          <td className="p-3 text-right font-mono">
                            {(weight * 100).toFixed(1)}%
                          </td>
                          <td className="p-3 text-center">
                            {isAtMin && (
                              <Badge variant="secondary" className="text-xs">
                                Min
                              </Badge>
                            )}
                          </td>
                          <td className="p-3 text-center">
                            {isAtMax && (
                              <Badge variant="secondary" className="text-xs">
                                Max
                              </Badge>
                            )}
                          </td>
                          <td className="p-3 text-right font-mono">
                            ${value.toFixed(0)}
                          </td>
                        </tr>
                      );
                    })}
                  <tr className="font-medium">
                    <td className="p-3">Total</td>
                    <td className="p-3 text-right font-mono">
                      {(totalWeight * 100).toFixed(0)}%
                    </td>
                    <td className="p-3"></td>
                    <td className="p-3"></td>
                    <td className="p-3 text-right font-mono">$10,000</td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
