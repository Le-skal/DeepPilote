'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { StatCard } from '@/components/cards/StatCard';
import { RegimeIndicator } from '@/components/cards/RegimeIndicator';
import { useMacroLatest, useRegime } from '@/hooks';
import {
  Activity,
  TrendingUp,
  DollarSign,
  Percent,
} from 'lucide-react';

export default function MarketPage() {
  const { data: macroLatest, isLoading: latestLoading } = useMacroLatest();
  const { data: regimeData, isLoading: regimeLoading } = useRegime();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Marché</h1>
        <p className="text-muted-foreground">
          Indicateurs macroéconomiques et régime de marché
        </p>
      </div>

      {/* Régime actuel */}
      <div className="grid gap-4 md:grid-cols-4">
        {regimeLoading ? (
          <Skeleton className="h-32 md:col-span-2" />
        ) : (
          <RegimeIndicator
            regime={regimeData?.regime ?? 'stable'}
            confidence={regimeData?.confidence ?? 0}
            className="md:col-span-2"
          />
        )}

        {latestLoading ? (
          <>
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
          </>
        ) : (
          <>
            <StatCard
              title="VIX (Volatilité)"
              value={macroLatest?.vix?.toFixed(1) ?? '-'}
              subtitle={
                macroLatest?.vix && macroLatest.vix < 15
                  ? 'Très calme'
                  : macroLatest?.vix && macroLatest.vix < 20
                  ? 'Normal'
                  : macroLatest?.vix && macroLatest.vix < 30
                  ? 'Élevé'
                  : 'Extrême'
              }
              icon={Activity}
              trend={
                macroLatest?.vix
                  ? macroLatest.vix < 20
                    ? 'up'
                    : macroLatest.vix > 30
                    ? 'down'
                    : 'neutral'
                  : undefined
              }
            />
            <StatCard
              title="Dernière mise à jour"
              value={regimeData?.as_of_date ?? macroLatest?.as_of_date ?? '-'}
            />
          </>
        )}
      </div>

      {/* Probabilités des régimes */}
      {regimeData && (
        <Card>
          <CardHeader>
            <CardTitle>Probabilités des Régimes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-4">
              {Object.entries(regimeData.probabilities).map(([regime, prob]) => (
                <div key={regime} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="capitalize font-medium">{regime}</span>
                    <span className="text-muted-foreground">
                      {(prob * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        regime === 'bull' ? 'bg-green-500' :
                        regime === 'bear' ? 'bg-red-500' :
                        regime === 'volatile' ? 'bg-amber-500' :
                        'bg-blue-500'
                      }`}
                      style={{ width: `${prob * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Taux d'intérêt */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Percent className="h-5 w-5" />
            Taux d&apos;intérêt
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            {latestLoading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-24" />
              ))
            ) : (
              <>
                <StatCard
                  title="Treasury 3 mois"
                  value={macroLatest?.t3mo ? `${macroLatest.t3mo.toFixed(2)}%` : '-'}
                  icon={TrendingUp}
                />
                <StatCard
                  title="Treasury 10 ans"
                  value={macroLatest?.t10y ? `${macroLatest.t10y.toFixed(2)}%` : '-'}
                  icon={TrendingUp}
                />
                <StatCard
                  title="Yield Curve (10Y-2Y)"
                  value={macroLatest?.yield_curve_10y2y ? `${macroLatest.yield_curve_10y2y.toFixed(2)}%` : '-'}
                  subtitle={
                    macroLatest?.yield_curve_10y2y &&
                    macroLatest.yield_curve_10y2y < 0
                      ? 'Courbe inversée (signal de récession)'
                      : 'Courbe normale'
                  }
                  trend={
                    macroLatest?.yield_curve_10y2y
                      ? macroLatest.yield_curve_10y2y < 0
                        ? 'down'
                        : 'up'
                      : undefined
                  }
                />
                <StatCard
                  title="Credit Spread HY"
                  value={macroLatest?.credit_spread ? `${macroLatest.credit_spread.toFixed(0)} bps` : '-'}
                  subtitle={
                    macroLatest?.credit_spread &&
                    macroLatest.credit_spread > 500
                      ? 'Stress crédit élevé'
                      : macroLatest?.credit_spread &&
                        macroLatest.credit_spread > 300
                      ? 'Stress modéré'
                      : 'Normal'
                  }
                />
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Matières premières */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Matières Premières
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            {latestLoading ? (
              Array.from({ length: 2 }).map((_, i) => (
                <Skeleton key={i} className="h-24" />
              ))
            ) : (
              <>
                <StatCard
                  title="Pétrole WTI"
                  value={macroLatest?.oil_wti ? `$${macroLatest.oil_wti.toFixed(2)}` : '-'}
                  subtitle="USD par baril"
                />
                <StatCard
                  title="Date des données"
                  value={macroLatest?.as_of_date ?? '-'}
                />
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Explication des régimes */}
      <Card>
        <CardHeader>
          <CardTitle>Régimes de Marché</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">
            Le modèle HMM (Hidden Markov Model) détecte 4 régimes de marché
            distincts :
          </p>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="flex items-start space-x-3">
              <div className="w-4 h-4 rounded-full bg-green-500 mt-1" />
              <div>
                <p className="font-medium">Haussier (Bull)</p>
                <p className="text-sm text-muted-foreground">
                  Rendements positifs, volatilité normale. Surpondérer les
                  actions.
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-4 h-4 rounded-full bg-red-500 mt-1" />
              <div>
                <p className="font-medium">Baissier (Bear)</p>
                <p className="text-sm text-muted-foreground">
                  Rendements négatifs, volatilité élevée. Réduire les actions,
                  favoriser TLT/GLD.
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-4 h-4 rounded-full bg-amber-500 mt-1" />
              <div>
                <p className="font-medium">Volatile</p>
                <p className="text-sm text-muted-foreground">
                  Haute volatilité, direction incertaine. Position défensive,
                  activer SH.
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-4 h-4 rounded-full bg-blue-500 mt-1" />
              <div>
                <p className="font-medium">Stable</p>
                <p className="text-sm text-muted-foreground">
                  Faible volatilité, marché calme. Allocation équilibrée.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
