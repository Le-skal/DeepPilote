'use client';

/**
 * Carte affichant les prédictions de trading avec signaux.
 */

import { TrendingUp, HelpCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { TickerPrediction } from '@/types/api';
import { SIGNAL_CONFIG, SignalType } from '@/lib/utils/constants';

interface PredictionCardProps {
  predictions: TickerPrediction[];
  topPicks: string[];
  regimeExplanation: string;
  asOf: string;
  isLoading?: boolean;
}

export function PredictionCard({
  predictions,
  topPicks,
  regimeExplanation,
  asOf,
  isLoading,
}: PredictionCardProps) {
  if (isLoading) {
    return (
      <Card className="border-violet-500/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-violet-400" />
            <Skeleton className="h-6 w-48" />
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  // Top 3 picks only
  const topPredictions = predictions.filter((p) => topPicks.includes(p.ticker));

  return (
    <Card className="border-violet-500/20">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-violet-400" />
            Recommandations du mois
          </CardTitle>
          <Tooltip>
            <TooltipTrigger className="cursor-help">
              <HelpCircle className="h-4 w-4 text-muted-foreground/50" />
            </TooltipTrigger>
            <TooltipContent side="left" className="max-w-xs">
              <p className="text-sm">
                Basé sur le régime de marché actuel et le momentum des ETF.
                Ce ne sont pas des conseils financiers.
              </p>
            </TooltipContent>
          </Tooltip>
        </div>
        <p className="text-sm text-muted-foreground mt-1">
          {regimeExplanation}
        </p>
      </CardHeader>
      <CardContent className="space-y-3">
        {topPredictions.map((prediction, index) => (
          <PredictionRow key={prediction.ticker} prediction={prediction} rank={index + 1} />
        ))}
        <p className="text-xs text-muted-foreground/70 pt-2">
          Mis à jour : {asOf}
        </p>
      </CardContent>
    </Card>
  );
}

interface PredictionRowProps {
  prediction: TickerPrediction;
  rank: number;
}

function PredictionRow({ prediction, rank }: PredictionRowProps) {
  const signalConfig = SIGNAL_CONFIG[prediction.signal as SignalType];

  return (
    <div className="flex items-center justify-between p-3 bg-card/50 border border-border/50">
      <div className="flex items-center gap-3">
        <span className="text-lg font-mono text-muted-foreground">#{rank}</span>
        <div>
          <p className="font-medium">{prediction.display_name}</p>
          <p className="text-xs text-muted-foreground">{prediction.ticker}</p>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <Tooltip>
          <TooltipTrigger>
            <Badge className={`${signalConfig.bgColor} ${signalConfig.color} border-0`}>
              {signalConfig.emoji} {signalConfig.label}
            </Badge>
          </TooltipTrigger>
          <TooltipContent>
            <p className="text-sm">{signalConfig.explanation}</p>
            <p className="text-xs text-muted-foreground mt-1">
              Probabilité de hausse : {Math.round(prediction.probability * 100)}%
            </p>
          </TooltipContent>
        </Tooltip>
      </div>
    </div>
  );
}

export function PredictionCardSkeleton() {
  return (
    <Card className="border-violet-500/20">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-violet-400" />
          <Skeleton className="h-6 w-48" />
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </CardContent>
    </Card>
  );
}
