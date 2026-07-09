import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ETFBase } from '@/types/api';
import { ETF_COLORS, ASSET_CLASSES, getTickerDisplayName } from '@/lib/utils/constants';
import { cn } from '@/lib/utils';
import { ArrowRight } from 'lucide-react';

// Descriptions claires de ce que chaque ETF investit
const ETF_DESCRIPTIONS: Record<string, string> = {
  URTH: 'Les plus grandes entreprises mondiales : USA, Europe, Japon, Australie. Diversification globale.',
  SPY: 'Les 500 plus grandes entreprises américaines : Apple, Microsoft, Amazon, Google, etc.',
  QQQ: 'Les 100 géants de la tech : Apple, Nvidia, Microsoft, Meta, Tesla, etc.',
  EFA: 'Grandes entreprises d\'Europe, Japon et Australie. Diversification hors USA.',
  EEM: 'Entreprises des pays émergents : Chine, Inde, Brésil, Taiwan, etc.',
  TLT: 'Obligations d\'État américaines à 20+ ans. Valeur refuge quand les actions chutent.',
  HYG: 'Obligations d\'entreprises à haut rendement. Plus de risque, plus de rendement.',
  GLD: 'Or physique stocké dans des coffres. Protection contre l\'inflation et les crises.',
  VNQ: 'Immobilier américain coté : centres commerciaux, bureaux, appartements.',
  SH: 'Inverse du S&P 500. Monte quand le marché baisse. Outil de couverture.',
};

interface ETFCardProps {
  etf: ETFBase;
  className?: string;
}

export function ETFCard({ etf, className }: ETFCardProps) {
  const color = ETF_COLORS[etf.ticker] || '#6B7280';
  const assetClass = ASSET_CLASSES[etf.ticker as keyof typeof ASSET_CLASSES];
  const description = ETF_DESCRIPTIONS[etf.ticker] || etf.name;

  return (
    <Link href={`/etfs/${etf.ticker}`}>
      <Card
        className={cn(
          'group border-border/50 bg-card/50 backdrop-blur-sm transition-all cursor-pointer h-full',
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
                <CardTitle className="text-lg font-bold">{getTickerDisplayName(etf.ticker)}</CardTitle>
                <p className="text-xs text-muted-foreground font-mono">{etf.ticker}</p>
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
          <p className="text-sm text-muted-foreground leading-relaxed">
            {description}
          </p>
        </CardContent>
      </Card>
    </Link>
  );
}
