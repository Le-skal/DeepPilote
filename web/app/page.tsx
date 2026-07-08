'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { ETFCard } from '@/components/cards/ETFCard';
import { TrackRecordCard } from '@/components/cards/TrackRecordCard';
import { Skeleton } from '@/components/ui/skeleton';
import {
  useETFs,
  useMacroLatest,
  useRegime,
  usePredictions,
  useMarketSentiment,
  useTrackRecord,
} from '@/hooks';
import {
  TrendingUp,
  Activity,
  ChevronDown,
  Zap,
  AlertTriangle,
  Shield,
  HelpCircle,
  ArrowRight,
} from 'lucide-react';
import {
  formatDateReadable,
} from '@/lib/utils/formatters';
import {
  ETF_TICKERS,
  REGIME_EXPLANATIONS,
} from '@/lib/utils/constants';
import { cn } from '@/lib/utils';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';

/**
 * Carte héros pour les métriques principales.
 */
function HeroCard({
  title,
  value,
  explanation,
  subtitle,
  icon: Icon,
  trend,
  helpText,
}: {
  title: string;
  value: string | React.ReactNode;
  explanation: string;
  subtitle?: string;
  icon: React.ElementType;
  trend?: 'positive' | 'negative' | 'neutral';
  helpText?: string;
}) {
  return (
    <Card className="relative overflow-hidden border-border/50 bg-card/80 backdrop-blur-sm">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <p className="text-sm font-medium text-muted-foreground">
                {title}
              </p>
              {helpText && (
                <Tooltip>
                  <TooltipTrigger className="cursor-help">
                    <HelpCircle className="h-3.5 w-3.5 text-muted-foreground/50" />
                  </TooltipTrigger>
                  <TooltipContent side="top" className="max-w-xs">
                    <p className="text-sm">{helpText}</p>
                  </TooltipContent>
                </Tooltip>
              )}
            </div>
            <div
              className={cn(
                'text-3xl font-bold',
                trend === 'positive' && 'text-green-500',
                trend === 'negative' && 'text-red-500'
              )}
            >
              {value}
            </div>
            <p className="text-sm text-muted-foreground">{explanation}</p>
            {subtitle && (
              <p className="text-xs text-muted-foreground/70">{subtitle}</p>
            )}
          </div>
          <div className="p-3  bg-primary/10">
            <Icon className="h-6 w-6 text-primary" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { data: etfsData, isLoading: etfsLoading } = useETFs();
  const { data: macroData, isLoading: macroLoading } = useMacroLatest();
  const { data: regimeData, isLoading: regimeLoading } = useRegime();
  const { data: predictionsData, isLoading: predictionsLoading } = usePredictions();
  const { data: sentimentData, isLoading: sentimentLoading } = useMarketSentiment();
  const { data: trackRecordData, isLoading: trackRecordLoading } = useTrackRecord();

  const [showMacro, setShowMacro] = useState(false);

  return (
    <div className="space-y-8">
      {/* Header avec explication */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
          <Zap className="h-8 w-8 text-primary" />
          DeepPilot
        </h1>
        <p className="text-muted-foreground max-w-2xl">
          Ton copilote d&apos;investissement. L&apos;IA analyse le marché et
          te suggère comment répartir ton argent entre 8 ETF diversifiés.
        </p>
      </div>

      {/* 3 Hero Cards - L'essentiel */}
      <div className="grid gap-6 md:grid-cols-3">
        {/* Humeur du marché */}
        {regimeLoading ? (
          <Skeleton className="h-44" />
        ) : (
          <Card className="relative overflow-hidden border-border/50 bg-card/80 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-muted-foreground">
                      Humeur du marché
                    </p>
                    <Tooltip>
                      <TooltipTrigger className="cursor-help">
                        <HelpCircle className="h-3.5 w-3.5 text-muted-foreground/50" />
                      </TooltipTrigger>
                      <TooltipContent side="top" className="max-w-xs">
                        <p className="text-sm">
                          L&apos;IA détecte 4 états de marché : haussier (bull),
                          baissier (bear), volatile, ou stable.
                        </p>
                      </TooltipContent>
                    </Tooltip>
                  </div>
                  <div
                    className={cn(
                      'text-2xl font-bold capitalize',
                      regimeData?.regime === 'bull' && 'text-green-500',
                      regimeData?.regime === 'bear' && 'text-red-500',
                      regimeData?.regime === 'volatile' && 'text-amber-500',
                      regimeData?.regime === 'stable' && 'text-violet-500'
                    )}
                  >
                    {regimeData?.regime === 'bull' && 'Haussier'}
                    {regimeData?.regime === 'bear' && 'Baissier'}
                    {regimeData?.regime === 'volatile' && 'Volatile'}
                    {regimeData?.regime === 'stable' && 'Stable'}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {regimeData?.regime &&
                      REGIME_EXPLANATIONS[regimeData.regime]}
                  </p>
                  <p className="text-xs text-muted-foreground/70">
                    Confiance: {((regimeData?.confidence ?? 0) * 100).toFixed(0)}
                    %
                  </p>
                </div>
                <div
                  className={cn(
                    'p-3 ',
                    regimeData?.regime === 'bull' && 'bg-green-500/10',
                    regimeData?.regime === 'bear' && 'bg-red-500/10',
                    regimeData?.regime === 'volatile' && 'bg-amber-500/10',
                    regimeData?.regime === 'stable' && 'bg-violet-500/10'
                  )}
                >
                  {regimeData?.regime === 'bull' && (
                    <TrendingUp className="h-6 w-6 text-green-500" />
                  )}
                  {regimeData?.regime === 'bear' && (
                    <AlertTriangle className="h-6 w-6 text-red-500" />
                  )}
                  {regimeData?.regime === 'volatile' && (
                    <Activity className="h-6 w-6 text-amber-500" />
                  )}
                  {regimeData?.regime === 'stable' && (
                    <Shield className="h-6 w-6 text-violet-500" />
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Prédictions IA */}
        {predictionsLoading ? (
          <Skeleton className="h-44" />
        ) : predictionsData ? (
          <Card className="relative overflow-hidden border-border/50 bg-card/80 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium text-muted-foreground">
                    Top recommandations
                  </p>
                  <Tooltip>
                    <TooltipTrigger className="cursor-help">
                      <HelpCircle className="h-3.5 w-3.5 text-muted-foreground/50" />
                    </TooltipTrigger>
                    <TooltipContent side="top" className="max-w-xs">
                      <p className="text-sm">
                        L&apos;IA analyse le marché et identifie les meilleurs ETF à privilégier ce mois-ci.
                      </p>
                    </TooltipContent>
                  </Tooltip>
                </div>
                <div className="space-y-2">
                  {predictionsData.top_picks.slice(0, 3).map((ticker, idx) => {
                    const pred = predictionsData.predictions.find(p => p.ticker === ticker);
                    if (!pred) return null;
                    return (
                      <div key={ticker} className="flex items-center justify-between">
                        <span className="text-sm font-medium">
                          #{idx + 1} {pred.display_name}
                        </span>
                        <span className={cn(
                          'text-xs px-2 py-0.5 rounded',
                          pred.signal === 'STRONG_BUY' && 'bg-green-500/20 text-green-500',
                          pred.signal === 'BUY' && 'bg-green-400/20 text-green-400',
                          pred.signal === 'HOLD' && 'bg-amber-400/20 text-amber-400',
                          pred.signal === 'SELL' && 'bg-red-400/20 text-red-400',
                          pred.signal === 'STRONG_SELL' && 'bg-red-500/20 text-red-500'
                        )}>
                          {pred.signal_emoji} {pred.signal_label}
                        </span>
                      </div>
                    );
                  })}
                </div>
                <p className="text-xs text-muted-foreground/70">
                  Mis à jour : {predictionsData.as_of}
                </p>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Skeleton className="h-44" />
        )}

        {/* Sentiment du marché */}
        {sentimentLoading ? (
          <Skeleton className="h-44" />
        ) : sentimentData ? (
          <Card className="relative overflow-hidden border-border/50 bg-card/80 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-muted-foreground">
                      Sentiment du marché
                    </p>
                    <Tooltip>
                      <TooltipTrigger className="cursor-help">
                        <HelpCircle className="h-3.5 w-3.5 text-muted-foreground/50" />
                      </TooltipTrigger>
                      <TooltipContent side="top" className="max-w-xs">
                        <p className="text-sm">
                          L&apos;IA analyse les news financières pour mesurer l&apos;humeur générale des investisseurs.
                        </p>
                      </TooltipContent>
                    </Tooltip>
                  </div>
                  <div
                    className={cn(
                      'text-2xl font-bold',
                      sentimentData.score >= 0.3 && 'text-green-500',
                      sentimentData.score <= -0.3 && 'text-red-500',
                      sentimentData.score > -0.3 && sentimentData.score < 0.3 && 'text-amber-400'
                    )}
                  >
                    {sentimentData.label === 'optimiste' && 'Optimiste'}
                    {sentimentData.label === 'pessimiste' && 'Pessimiste'}
                    {sentimentData.label === 'neutre' && 'Neutre'}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {sentimentData.interpretation}
                  </p>
                  <p className="text-xs text-muted-foreground/70">
                    Confiance: {sentimentData.confidence}
                  </p>
                </div>
                <div
                  className={cn(
                    'p-3',
                    sentimentData.score >= 0.3 && 'bg-green-500/10',
                    sentimentData.score <= -0.3 && 'bg-red-500/10',
                    sentimentData.score > -0.3 && sentimentData.score < 0.3 && 'bg-amber-400/10'
                  )}
                >
                  <Activity className="h-6 w-6 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>
        ) : (
          <HeroCard
            title="Niveau de peur (VIX)"
            value={macroData?.vix?.toFixed(1) ?? '-'}
            explanation={macroData?.vix ? (macroData.vix < 20 ? 'Marché calme et confiant' : macroData.vix > 30 ? 'Forte inquiétude des investisseurs' : 'Tension modérée') : 'Données non disponibles'}
            subtitle={
              macroData?.as_of_date
                ? `Au ${formatDateReadable(macroData.as_of_date)}`
                : undefined
            }
            icon={Activity}
            trend={
              macroData?.vix
                ? macroData.vix < 20
                  ? 'positive'
                  : macroData.vix > 30
                  ? 'negative'
                  : 'neutral'
                : 'neutral'
            }
            helpText="Le VIX mesure l'inquiétude des investisseurs. Bas = calme, élevé = peur."
          />
        )}
      </div>

      {/* Lien vers portfolio */}
      <Card className="border-primary/30 bg-primary/5">
        <CardContent className="p-4 flex items-center justify-between">
          <div>
            <p className="font-medium">Voir l&apos;allocation recommandée</p>
            <p className="text-sm text-muted-foreground">
              L&apos;IA calcule les poids optimaux pour chaque ETF selon le
              marché actuel.
            </p>
          </div>
          <Link
            href="/portfolio"
            className="flex items-center gap-2 px-4 py-2  bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            Portfolio
            <ArrowRight className="h-4 w-4" />
          </Link>
        </CardContent>
      </Card>

      {/* Track Record - Fiabilité du modèle */}
      <TrackRecordCard
        trackRecord={trackRecordData ?? null}
        isLoading={trackRecordLoading}
      />

      {/* Indicateurs macro - Collapsible */}
      <div>
        <button
          onClick={() => setShowMacro(!showMacro)}
          className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors mb-4"
        >
          <ChevronDown
            className={cn(
              'h-4 w-4 transition-transform',
              showMacro && 'rotate-180'
            )}
          />
          {showMacro ? 'Masquer' : 'Voir'} les indicateurs macro (avancé)
        </button>

        {showMacro && (
          <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-5">
            {macroLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-24" />
              ))
            ) : (
              <>
                <Card>
                  <CardContent className="p-4">
                    <p className="text-xs text-muted-foreground mb-1">
                      Taux 10 ans
                    </p>
                    <p className="text-xl font-bold font-mono">
                      {macroData?.t10y ? `${macroData.t10y.toFixed(2)}%` : '-'}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Rendement des obligations US
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <p className="text-xs text-muted-foreground mb-1">
                      Yield Curve
                    </p>
                    <p
                      className={cn(
                        'text-xl font-bold font-mono',
                        macroData?.yield_curve_10y2y &&
                          macroData.yield_curve_10y2y < 0 &&
                          'text-red-500'
                      )}
                    >
                      {macroData?.yield_curve_10y2y
                        ? `${macroData.yield_curve_10y2y.toFixed(2)}%`
                        : '-'}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {macroData?.yield_curve_10y2y &&
                      macroData.yield_curve_10y2y < 0
                        ? 'Inversée (signal récession)'
                        : 'Normale'}
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <p className="text-xs text-muted-foreground mb-1">
                      Credit Spread
                    </p>
                    <p className="text-xl font-bold font-mono">
                      {macroData?.credit_spread
                        ? `${macroData.credit_spread.toFixed(0)} bps`
                        : '-'}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Stress des entreprises
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <p className="text-xs text-muted-foreground mb-1">
                      Pétrole WTI
                    </p>
                    <p className="text-xl font-bold font-mono">
                      {macroData?.oil_wti
                        ? `$${macroData.oil_wti.toFixed(0)}`
                        : '-'}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      USD par baril
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <p className="text-xs text-muted-foreground mb-1">
                      Taux 3 mois
                    </p>
                    <p className="text-xl font-bold font-mono">
                      {macroData?.t3mo ? `${macroData.t3mo.toFixed(2)}%` : '-'}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Taux sans risque
                    </p>
                  </CardContent>
                </Card>
              </>
            )}
          </div>
        )}
      </div>

      {/* Liste des ETFs */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Les 8 ETF du portefeuille</h2>
          <Link
            href="/etfs"
            className="text-sm text-primary hover:underline flex items-center gap-1"
          >
            Voir tous les détails
            <ArrowRight className="h-3 w-3" />
          </Link>
        </div>
        {etfsLoading ? (
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
              .map((etf) => (
                <ETFCard key={etf.ticker} etf={etf} />
              ))}
          </div>
        )}
      </div>
    </div>
  );
}
