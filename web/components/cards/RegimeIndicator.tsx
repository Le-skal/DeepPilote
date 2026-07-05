import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { RegimeName } from '@/types/api';
import { REGIME_LABELS } from '@/lib/utils/constants';
import { cn } from '@/lib/utils';
import { Signal, TrendingUp, TrendingDown, Zap, Shield } from 'lucide-react';

// Couleurs cyberpunk violet pour les régimes
const REGIME_GLOW: Record<RegimeName, string> = {
  bull: 'shadow-[0_0_25px_-5px_hsl(145,80%,42%)]',
  bear: 'shadow-[0_0_25px_-5px_hsl(0,85%,55%)]',
  volatile: 'shadow-[0_0_25px_-5px_hsl(38,95%,50%)]',
  stable: 'shadow-[0_0_25px_-5px_hsl(271,91%,65%)]', // Violet glow
};

const REGIME_BG: Record<RegimeName, string> = {
  bull: 'bg-green-500/10 border-green-500/30',
  bear: 'bg-red-500/10 border-red-500/30',
  volatile: 'bg-amber-500/10 border-amber-500/30',
  stable: 'bg-violet-500/10 border-violet-500/30', // Violet
};

const REGIME_TEXT: Record<RegimeName, string> = {
  bull: 'text-green-500',
  bear: 'text-red-500',
  volatile: 'text-amber-500',
  stable: 'text-violet-500', // Violet
};

const REGIME_ICONS: Record<RegimeName, typeof TrendingUp> = {
  bull: TrendingUp,
  bear: TrendingDown,
  volatile: Zap,
  stable: Shield,
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
  const Icon = REGIME_ICONS[regime];

  return (
    <Card className={cn(
      'border-border/50 bg-card/80 backdrop-blur-sm transition-all duration-300',
      REGIME_GLOW[regime],
      'hover:scale-[1.02]',
      className
    )}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
          Régime de marché
        </CardTitle>
        <div className={cn('p-1.5 rounded-md', REGIME_BG[regime])}>
          <Signal className={cn('h-4 w-4', REGIME_TEXT[regime])} />
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4">
          <div className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-md border font-bold text-lg',
            REGIME_BG[regime],
            REGIME_TEXT[regime]
          )}>
            <Icon className="h-5 w-5" />
            {label}
          </div>
          {confidence !== undefined && (
            <div className="flex flex-col">
              <span className="text-xs text-muted-foreground">Confiance</span>
              <span className={cn('text-2xl font-mono font-bold', REGIME_TEXT[regime])}>
                {(confidence * 100).toFixed(0)}%
              </span>
            </div>
          )}
        </div>
        {/* Barre de confiance avec animation */}
        {confidence !== undefined && (
          <div className="mt-4 h-2 bg-secondary/50 rounded-full overflow-hidden">
            <div
              className={cn(
                'h-full rounded-full transition-all duration-1000 ease-out',
                regime === 'bull' && 'bg-green-500',
                regime === 'bear' && 'bg-red-500',
                regime === 'volatile' && 'bg-amber-500',
                regime === 'stable' && 'bg-violet-500'
              )}
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
export function RegimeBadge({ regime, showIcon = true }: { regime: RegimeName; showIcon?: boolean }) {
  const label = REGIME_LABELS[regime];
  const Icon = REGIME_ICONS[regime];

  return (
    <Badge
      variant="outline"
      className={cn(
        'gap-1.5 font-mono font-medium',
        REGIME_BG[regime],
        REGIME_TEXT[regime]
      )}
    >
      {showIcon && <Icon className="h-3 w-3" />}
      {label}
    </Badge>
  );
}

/**
 * Small regime dot indicator.
 */
export function RegimeDot({ regime }: { regime: RegimeName }) {
  return (
    <span
      className={cn(
        'inline-block w-2.5 h-2.5 rounded-full animate-pulse',
        regime === 'bull' && 'bg-green-500',
        regime === 'bear' && 'bg-red-500',
        regime === 'volatile' && 'bg-amber-500',
        regime === 'stable' && 'bg-violet-500'
      )}
    />
  );
}
