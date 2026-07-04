import Link from 'next/link';
import { Zap, Code2 } from 'lucide-react';

export function Footer() {
  return (
    <footer className="border-t border-border/50 bg-background/50 backdrop-blur-sm">
      <div className="container py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Logo & Description */}
          <div className="flex flex-col items-center md:items-start gap-2">
            <div className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-primary" />
              <span className="font-bold">
                <span className="text-primary">Deep</span>Pilot
              </span>
            </div>
            <p className="text-xs text-muted-foreground text-center md:text-left">
              Copilote d&apos;allocation d&apos;actifs ML
            </p>
          </div>

          {/* Links */}
          <div className="flex items-center gap-6 text-sm">
            <Link
              href="/about"
              className="text-muted-foreground hover:text-primary transition-colors"
            >
              Mentions légales
            </Link>
            <Link
              href="https://github.com"
              target="_blank"
              className="flex items-center gap-1 text-muted-foreground hover:text-primary transition-colors"
            >
              <Code2 className="h-4 w-4" />
              <span>GitHub</span>
            </Link>
          </div>

          {/* Credits */}
          <div className="text-xs text-muted-foreground text-center md:text-right">
            <p>Projet Bachelor Data & IA</p>
            <p className="text-primary/70">ECE Paris 2026</p>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mt-6 pt-4 border-t border-border/30">
          <p className="text-[10px] text-muted-foreground/60 text-center">
            Projet éducatif - Ne constitue pas un conseil en investissement (Art. L321-1 CMF)
          </p>
        </div>
      </div>
    </footer>
  );
}
