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
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/90 backdrop-blur-xl">
      <div className="container flex h-16 items-center justify-between">
        {/* Logo avec glow violet */}
        <Link href="/" className="flex items-center space-x-3 group">
          <div className="relative">
            <Zap
              className={cn(
                'h-7 w-7 text-primary transition-all duration-300',
                'group-hover:drop-shadow-[0_0_12px_hsl(271,91%,65%)]',
                'group-hover:scale-110'
              )}
            />
            {/* Subtle glow background */}
            <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          </div>
          <span className="font-bold text-xl tracking-tight">
            <span className="text-gradient">Deep</span>
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
                  'flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200',
                  isActive
                    ? 'text-primary bg-primary/10 shadow-[0_0_15px_-5px_hsl(271,91%,65%)]'
                    : 'text-muted-foreground hover:text-foreground hover:bg-secondary/60'
                )}
              >
                <Icon className={cn('h-4 w-4', isActive && 'text-primary')} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
