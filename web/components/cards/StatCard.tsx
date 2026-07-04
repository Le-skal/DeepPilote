import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string;
  subtitle?: string;
  icon?: LucideIcon;
  trend?: 'up' | 'down' | 'neutral';
  className?: string;
}

export function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  className,
}: StatCardProps) {
  return (
    <Card className={cn(
      'border-border/50 bg-card/50 backdrop-blur-sm transition-all hover:border-primary/30',
      trend === 'up' && 'hover:shadow-glow-success',
      trend === 'down' && 'hover:shadow-glow-danger',
      className
    )}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
          {title}
        </CardTitle>
        {Icon && (
          <div className={cn(
            'p-1.5 rounded-sm',
            trend === 'up' && 'bg-success/10 text-success',
            trend === 'down' && 'bg-destructive/10 text-destructive',
            !trend && 'bg-primary/10 text-primary'
          )}>
            <Icon className="h-4 w-4" />
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline gap-2">
          <span
            className={cn(
              'text-2xl font-bold font-mono tracking-tight',
              trend === 'up' && 'text-success',
              trend === 'down' && 'text-destructive'
            )}
          >
            {value}
          </span>
          {trend && trend !== 'neutral' && (
            <span className={cn(
              'flex items-center text-xs',
              trend === 'up' && 'text-success',
              trend === 'down' && 'text-destructive'
            )}>
              {trend === 'up' ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
            </span>
          )}
        </div>
        {subtitle && (
          <p className="text-xs text-muted-foreground mt-1.5">{subtitle}</p>
        )}
      </CardContent>
    </Card>
  );
}
