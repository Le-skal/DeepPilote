import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { RegimeName } from '@/types/api';
import { REGIME_LABELS } from '@/lib/utils/constants';
import { cn } from '@/lib/utils';
import { Activity, Signal } from 'lucide-react';

// Couleurs cyberpunk pour les régimes
const REGIME_GLOW: Record<RegimeName, string> = {
  bull: 'shadow-[0_0_20px_-5px_hsl(145,80%,42%)]',
  bear: 'shadow-[0_0_20px_-5px_hsl(0,85%,55%)]',
  volatile: 'shadow-[0_0_20px_-5px_hsl(38,95%,50%)]',
  stable: 'shadow-[0_0_20px_-5px_hsl(200,100%,50%)]',
};

const REGIME_BG: Record<RegimeName, string> = {
  bull: 'bg-success/10 border-success/30',
  bear: 'bg-destructive/10 border-destructive/30',
  volatile: 'bg-warning/10 border-warning/30',
  stable: 'bg-primary/10 border-primary/30',
};

const REGIME_TEXT: Record<RegimeName, string> = {
  bull: 'text-success',
  bear: 'text-destructive',
  volatile: 'text-warning',
  stable: 'text-primary',
};

interface RegimeIndicatorProps {
  regime: RegimeName;
  confidence?: number;
  className?: string;
}

export function RegimeIndicator({
  regime,
  confidence,
  className,
}: RegimeIndicatorProps) {
  const label = REGIME_LABELS[regime];

  return (
    <Card className={cn(
      'border-border/50 bg-card/50 backdrop-blur-sm transition-all',
      REGIME_GLOW[regime],
      className
    )}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
          Régime de marché
        </CardTitle>
        <div className="p-1.5 rounded-sm bg-primary/10">
          <Signal className="h-4 w-4 text-primary" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-3">
          <div className={cn(
            'px-3 py-1.5 rounded-sm border font-bold text-lg',
            REGIME_BG[regime],
            REGIME_TEXT[regime]
          )}>
            {label}
          </div>
          {confidence !== undefined && (
            <div className="flex flex-col">
              <span className="text-xs text-muted-foreground">Confiance</span>
              <span className={cn('text-lg font-mono font-bold', REGIME_TEXT[regime])}>
                {(confidence * 100).toFixed(0)}%
              </span>
            </div>
          )}
        </div>
        {/* Barre de confiance */}
        {confidence !== undefined && (
          <div className="mt-3 h-1.5 bg-secondary rounded-sm overflow-hidden">
            <div
              className={cn('h-full transition-all', REGIME_BG[regime].replace('/10', ''))}
              style={{ width: `${confidence * 100}%` }}
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * Badge version du régime (pour inline usage).
 */
export function RegimeBadge({ regime }: { regime: RegimeName }) {
  const label = REGIME_LABELS[regime];

  return (
    <Badge
      variant="outline"
      className={cn(
        'gap-1.5 font-mono',
        REGIME_BG[regime],
        REGIME_TEXT[regime]
      )}
    >
      <Activity className="h-3 w-3" />
      {label}
    </Badge>
  );
}
