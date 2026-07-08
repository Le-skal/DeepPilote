'use client';

/**
 * Carte affichant la fiabilité historique du modèle.
 * Montre l'accuracy par régime et les dernières prédictions vs réalité.
 */

import { CheckCircle, XCircle, AlertTriangle, HelpCircle, BarChart3 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { TrackRecordResponse, RegimeName } from '@/types/api';
import { cn } from '@/lib/utils';

interface TrackRecordCardProps {
  trackRecord: TrackRecordResponse | null;
  isLoading?: boolean;
}

// Couleurs par régime
const REGIME_COLORS: Record<RegimeName, string> = {
  bull: 'text-green-500',
  bear: 'text-red-500',
  volatile: 'text-amber-500',
  stable: 'text-violet-500',
};

const REGIME_LABELS: Record<RegimeName, string> = {
  bull: 'Haussier',
  bear: 'Baissier',
  volatile: 'Volatile',
  stable: 'Stable',
};

export function TrackRecordCard({ trackRecord, isLoading }: TrackRecordCardProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-primary" />
            <Skeleton className="h-6 w-48" />
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-32 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (!trackRecord || trackRecord.overall_accuracy === null) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-primary" />
            Fiabilité du modèle
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            {trackRecord?.disclaimer || 'Données non disponibles pour évaluer la fiabilité.'}
          </p>
        </CardContent>
      </Card>
    );
  }

  const accuracyColor = trackRecord.overall_accuracy >= 60
    ? 'text-green-500'
    : trackRecord.overall_accuracy >= 50
    ? 'text-amber-500'
    : 'text-red-500';

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-primary" />
            Fiabilité du modèle
          </CardTitle>
          <Tooltip>
            <TooltipTrigger className="cursor-help">
              <HelpCircle className="h-4 w-4 text-muted-foreground/50" />
            </TooltipTrigger>
            <TooltipContent side="left" className="max-w-xs">
              <p className="text-sm">
                Compare les prédictions passées du modèle avec ce qui s&apos;est réellement passé.
                Une accuracy de 60% signifie que 6 fois sur 10, la prédiction était correcte.
              </p>
            </TooltipContent>
          </Tooltip>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Accuracy globale */}
        <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
          <div>
            <p className="text-sm text-muted-foreground">Précision globale</p>
            <p className={cn('text-2xl font-bold font-mono', accuracyColor)}>
              {trackRecord.overall_accuracy}%
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs text-muted-foreground">Sur {trackRecord.sample_size} prédictions</p>
            {trackRecord.evaluation_period && (
              <p className="text-xs text-muted-foreground">
                {trackRecord.evaluation_period.start} → {trackRecord.evaluation_period.end}
              </p>
            )}
          </div>
        </div>

        {/* Accuracy par régime */}
        <div>
          <p className="text-sm font-medium mb-2">Par type de marché :</p>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(trackRecord.regime_accuracy).map(([regime, stats]) => (
              <div key={regime} className="flex items-center justify-between p-2 bg-muted/20 rounded">
                <span className={cn('text-sm font-medium', REGIME_COLORS[regime as RegimeName])}>
                  {REGIME_LABELS[regime as RegimeName] || regime}
                </span>
                <Badge variant={stats.accuracy >= 60 ? 'default' : 'secondary'} className="font-mono">
                  {stats.accuracy}%
                </Badge>
              </div>
            ))}
          </div>
        </div>

        {/* Dernières prédictions */}
        {trackRecord.recent_predictions.length > 0 && (
          <div>
            <p className="text-sm font-medium mb-2">Dernières prédictions :</p>
            <div className="space-y-1 max-h-40 overflow-y-auto">
              {trackRecord.recent_predictions.slice(0, 6).map((pred, idx) => (
                <div key={idx} className="flex items-center justify-between text-xs p-1.5 bg-muted/10 rounded">
                  <div className="flex items-center gap-2">
                    {pred.was_correct ? (
                      <CheckCircle className="h-3.5 w-3.5 text-green-500" />
                    ) : (
                      <XCircle className="h-3.5 w-3.5 text-red-500" />
                    )}
                    <span className="text-muted-foreground">{pred.date}</span>
                    <span className={REGIME_COLORS[pred.predicted_regime]}>
                      {REGIME_LABELS[pred.predicted_regime]}
                    </span>
                  </div>
                  <span className={cn(
                    'font-mono',
                    pred.actual_return_pct >= 0 ? 'text-green-500' : 'text-red-500'
                  )}>
                    {pred.actual_return_pct >= 0 ? '+' : ''}{pred.actual_return_pct}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Disclaimer */}
        <div className="flex items-start gap-2 p-2 bg-amber-500/10 rounded text-xs">
          <AlertTriangle className="h-4 w-4 text-amber-500 flex-shrink-0 mt-0.5" />
          <p className="text-muted-foreground">
            {trackRecord.disclaimer}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

export function TrackRecordCardSkeleton() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-primary" />
          <Skeleton className="h-6 w-48" />
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Skeleton className="h-24 w-full mb-4" />
        <Skeleton className="h-16 w-full" />
      </CardContent>
    </Card>
  );
}
