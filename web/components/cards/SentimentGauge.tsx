'use client';

/**
 * Jauge de sentiment du marché.
 * Affiche le score de sentiment de -1 (peur) à +1 (euphorie).
 */

import { Smile, Frown, Meh, HelpCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { MarketSentiment } from '@/types/api';

interface SentimentGaugeProps {
  sentiment: MarketSentiment | null;
  isLoading?: boolean;
}

export function SentimentGauge({ sentiment, isLoading }: SentimentGaugeProps) {
  if (isLoading) {
    return (
      <Card className="border-violet-500/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Smile className="h-5 w-5 text-violet-400" />
            <Skeleton className="h-6 w-40" />
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-8 w-full mb-4" />
          <Skeleton className="h-4 w-3/4" />
        </CardContent>
      </Card>
    );
  }

  if (!sentiment) {
    return (
      <Card className="border-violet-500/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Meh className="h-5 w-5 text-muted-foreground" />
            Humeur du marché
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Données non disponibles
          </p>
        </CardContent>
      </Card>
    );
  }

  // Calculer la position sur la jauge (0% = -1, 50% = 0, 100% = +1)
  const gaugePosition = ((sentiment.score + 1) / 2) * 100;

  // Couleur selon le sentiment
  const getColor = () => {
    if (sentiment.score >= 0.3) return 'text-green-500';
    if (sentiment.score <= -0.3) return 'text-red-500';
    return 'text-amber-400';
  };

  const getIcon = () => {
    if (sentiment.score >= 0.3) return <Smile className={`h-6 w-6 ${getColor()}`} />;
    if (sentiment.score <= -0.3) return <Frown className={`h-6 w-6 ${getColor()}`} />;
    return <Meh className={`h-6 w-6 ${getColor()}`} />;
  };

  const getLabel = () => {
    if (sentiment.label === 'optimiste') return 'Optimiste';
    if (sentiment.label === 'pessimiste') return 'Pessimiste';
    return 'Neutre';
  };

  return (
    <Card className="border-violet-500/20">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            {getIcon()}
            Humeur du marché
          </CardTitle>
          <Tooltip>
            <TooltipTrigger className="cursor-help">
              <HelpCircle className="h-4 w-4 text-muted-foreground/50" />
            </TooltipTrigger>
            <TooltipContent side="left" className="max-w-xs">
              <p className="text-sm">
                Analyse du sentiment des news financières récentes via IA.
                Un sentiment positif indique que les investisseurs sont confiants.
              </p>
            </TooltipContent>
          </Tooltip>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Jauge visuelle */}
        <div className="relative">
          <div className="h-3 bg-gradient-to-r from-red-500 via-amber-400 to-green-500 opacity-30" />
          <div
            className="absolute top-0 w-3 h-3 bg-white border-2 border-violet-500 -translate-x-1/2"
            style={{ left: `${gaugePosition}%` }}
          />
        </div>

        {/* Labels de la jauge */}
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>Peur</span>
          <span>Neutre</span>
          <span>Euphorie</span>
        </div>

        {/* Score et label */}
        <div className="flex items-center justify-between">
          <div>
            <p className={`text-2xl font-mono font-bold ${getColor()}`}>
              {sentiment.score > 0 ? '+' : ''}{sentiment.score.toFixed(2)}
            </p>
            <p className={`text-sm font-medium ${getColor()}`}>{getLabel()}</p>
          </div>
          <ConfidenceBadge confidence={sentiment.confidence} />
        </div>

        {/* Interprétation */}
        <p className="text-sm text-muted-foreground">
          {sentiment.interpretation}
        </p>

        <p className="text-xs text-muted-foreground/70">
          Mis à jour : {sentiment.as_of}
        </p>
      </CardContent>
    </Card>
  );
}

function ConfidenceBadge({ confidence }: { confidence: 'high' | 'medium' | 'low' }) {
  const config = {
    high: { label: 'Fiable', color: 'text-green-400 bg-green-400/10' },
    medium: { label: 'Modéré', color: 'text-amber-400 bg-amber-400/10' },
    low: { label: 'Incertain', color: 'text-red-400 bg-red-400/10' },
  };

  const { label, color } = config[confidence];

  return (
    <Tooltip>
      <TooltipTrigger>
        <span className={`text-xs px-2 py-1 ${color}`}>
          {label}
        </span>
      </TooltipTrigger>
      <TooltipContent>
        <p className="text-sm">
          Niveau de confiance dans cette analyse.
        </p>
      </TooltipContent>
    </Tooltip>
  );
}

export function SentimentGaugeSkeleton() {
  return (
    <Card className="border-violet-500/20">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Skeleton className="h-6 w-6 rounded-full" />
          <Skeleton className="h-6 w-40" />
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Skeleton className="h-3 w-full mb-4" />
        <Skeleton className="h-8 w-20 mb-2" />
        <Skeleton className="h-4 w-3/4" />
      </CardContent>
    </Card>
  );
}
