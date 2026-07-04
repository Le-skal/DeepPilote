import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { cn } from '@/lib/utils';
import { QueryProvider } from '@/providers/QueryProvider';
import { TooltipProvider } from '@/components/ui/tooltip';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';

const inter = Inter({ subsets: ['latin'], variable: '--font-sans' });

export const metadata: Metadata = {
  title: 'DeepPilot - Copilote d\'allocation d\'actifs',
  description:
    'Application ML pour l\'allocation dynamique d\'un portefeuille de 8 ETFs diversifiés.',
  keywords: ['ETF', 'portfolio', 'machine learning', 'allocation', 'finance'],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr" className={cn('font-sans', inter.variable)}>
      <body className="min-h-screen bg-background antialiased">
        <QueryProvider>
          <TooltipProvider>
            <div className="relative flex min-h-screen flex-col">
              <Header />
              <main className="flex-1 container py-6">{children}</main>
              <Footer />
            </div>
          </TooltipProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
