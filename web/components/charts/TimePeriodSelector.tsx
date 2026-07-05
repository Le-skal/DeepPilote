'use client';

import { cn } from '@/lib/utils';
import { TIME_PERIODS, TimePeriod } from '@/lib/utils/constants';

interface TimePeriodSelectorProps {
  selected: TimePeriod;
  onChange: (period: TimePeriod) => void;
  className?: string;
}

/**
 * Sélecteur de période pour les charts.
 * Boutons: 7D | 1M | 3M | 1Y | MAX
 */
export function TimePeriodSelector({
  selected,
  onChange,
  className,
}: TimePeriodSelectorProps) {
  return (
    <div
      className={cn(
        'inline-flex items-center gap-0.5 p-1 rounded-lg bg-muted/50',
        className
      )}
    >
      {TIME_PERIODS.map((period) => (
        <button
          key={period}
          onClick={() => onChange(period)}
          className={cn(
            'px-3 py-1.5 text-xs font-medium rounded-md transition-all duration-200',
            selected === period
              ? 'bg-primary text-primary-foreground shadow-glow'
              : 'text-muted-foreground hover:text-foreground hover:bg-muted'
          )}
        >
          {period}
        </button>
      ))}
    </div>
  );
}
