'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { TrendingUp, BarChart2, PieChart, Activity, Info, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/', label: 'Dashboard', icon: TrendingUp },
  { href: '/etfs', label: 'ETFs', icon: BarChart2 },
  { href: '/portfolio', label: 'Portfolio', icon: PieChart },
  { href: '/market', label: 'Marché', icon: Activity },
  { href: '/analysis', label: 'Analyse', icon: BarChart2 },
  { href: '/about', label: 'À propos', icon: Info },
];

export function Header() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/50 bg-background/80 backdrop-blur-xl">
      <div className="container flex h-16 items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center space-x-3 group">
          <div className="relative">
            <Zap className="h-7 w-7 text-primary transition-all group-hover:drop-shadow-[0_0_8px_hsl(180,100%,50%)]" />
          </div>
          <span className="font-bold text-xl tracking-tight">
            <span className="text-primary">Deep</span>
            <span className="text-foreground">Pilot</span>
          </span>
        </Link>

        {/* Navigation */}
        <nav className="flex items-center space-x-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive =
              pathname === item.href ||
              (item.href !== '/' && pathname.startsWith(item.href));

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex items-center space-x-2 px-3 py-2 text-sm font-medium transition-all',
                  isActive
                    ? 'text-primary bg-primary/10 border-b-2 border-primary'
                    : 'text-muted-foreground hover:text-foreground hover:bg-secondary/50'
                )}
              >
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
