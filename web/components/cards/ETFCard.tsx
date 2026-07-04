import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ETFBase, ETFStats } from '@/types/api';
import { formatPercent } from '@/lib/utils/formatters';
import { ETF_COLORS, ASSET_CLASSES } from '@/lib/utils/constants';
import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown, ArrowRight } from 'lucide-react';

interface ETFCardProps {
  etf: ETFBase;
  stats?: ETFStats;
  className?: string;
}

export function ETFCard({ etf, stats, className }: ETFCardProps) {
  const color = ETF_COLORS[etf.ticker] || '#6B7280';
  const assetClass = ASSET_CLASSES[etf.ticker as keyof typeof ASSET_CLASSES];
  const isPositive = stats && stats.total_return >= 0;

  return (
    <Link href={`/etfs/${etf.ticker}`}>
      <Card
        className={cn(
          'group border-border/50 bg-card/50 backdrop-blur-sm transition-all cursor-pointer',
          'hover:border-primary/50 hover:shadow-glow',
          className
        )}
      >
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div
                className="w-2 h-8 rounded-sm"
                style={{ backgroundColor: color }}
              />
              <div>
                <CardTitle className="text-xl font-bold font-mono">{etf.ticker}</CardTitle>
                <p className="text-xs text-muted-foreground truncate max-w-[180px]">{etf.name}</p>
              </div>
            </div>
            <ArrowRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 group-hover:text-primary transition-all" />
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          {assetClass && (
            <Badge variant="outline" className="mb-3 text-xs bg-secondary/50">
              {assetClass}
            </Badge>
          )}

          {stats && (
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="space-y-0.5">
                <p className="text-xs text-muted-foreground uppercase tracking-wider">Return</p>
                <div className="flex items-center gap-1">
                  {isPositive ? (
                    <TrendingUp className="h-3 w-3 text-success" />
                  ) : (
                    <TrendingDown className="h-3 w-3 text-destructive" />
                  )}
                  <p className={cn('font-mono font-bold', isPositive ? 'text-success' : 'text-destructive')}>
                    {formatPercent(stats.total_return)}
                  </p>
                </div>
              </div>
              <div className="space-y-0.5">
                <p className="text-xs text-muted-foreground uppercase tracking-wider">Sharpe</p>
                <p className="font-mono font-bold">
                  {stats.sharpe_ratio?.toFixed(2) ?? '-'}
                </p>
              </div>
              <div className="space-y-0.5">
                <p className="text-xs text-muted-foreground uppercase tracking-wider">Vol.</p>
                <p className="font-mono">
                  {stats.annualized_volatility.toFixed(1)}%
                </p>
              </div>
              <div className="space-y-0.5">
                <p className="text-xs text-muted-foreground uppercase tracking-wider">Max DD</p>
                <p className="font-mono text-destructive">
                  {formatPercent(stats.max_drawdown)}
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}
