import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { AlertTriangle, GraduationCap, Shield, Database } from 'lucide-react';

export default function AboutPage() {
  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">À propos</h1>
        <p className="text-muted-foreground">
          Informations sur le projet DeepPilot et mentions légales
        </p>
      </div>

      {/* Disclaimer - IMPORTANT */}
      <Card className="border-amber-500 bg-amber-50 dark:bg-amber-950/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-amber-700 dark:text-amber-500">
            <AlertTriangle className="h-5 w-5" />
            Avertissement Important
          </CardTitle>
        </CardHeader>
        <CardContent className="text-amber-800 dark:text-amber-400 space-y-3">
          <p>
            <strong>Ce projet est purement éducatif.</strong> Il ne constitue pas un
            conseil en investissement au sens de l&apos;article L321-1 du Code
            monétaire et financier.
          </p>
          <p>
            Les performances passées ne préjugent pas des performances futures.
            Les données présentées sont fournies à titre indicatif et ne
            constituent en aucun cas une recommandation d&apos;achat ou de vente
            d&apos;instruments financiers.
          </p>
          <p>
            L&apos;utilisateur est seul responsable de ses décisions
            d&apos;investissement. Consultez un conseiller financier agréé avant
            toute décision d&apos;investissement.
          </p>
        </CardContent>
      </Card>

      {/* Projet */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <GraduationCap className="h-5 w-5" />
            Le Projet
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p>
            <strong>DeepPilot</strong> est un projet de fin d&apos;études pour le
            Bachelor Data & IA de l&apos;ECE Paris (RNCP37827 - Développeur en
            Intelligence Artificielle, certification Simplon).
          </p>
          <p>
            Le projet consiste en un copilote d&apos;allocation d&apos;actifs qui
            investit dans un panier de 8 ETFs diversifiés avec réallocation
            mensuelle, en utilisant deux modèles ML pour détecter le régime de
            marché et optimiser les poids.
          </p>

          <Separator className="my-4" />

          <h3 className="font-semibold">Objectif</h3>
          <p>
            Battre les benchmarks passifs (Buy & Hold MSCI World, 60/40 classique,
            NASDAQ 100, S&P 500) en tenant compte des frais de transaction, sur la
            période de backtest 2010-2025.
          </p>

          <Separator className="my-4" />

          <h3 className="font-semibold">Les 8 ETFs</h3>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground">
            <li>
              <strong>SPY</strong> - SPDR S&P 500 (Actions US)
            </li>
            <li>
              <strong>EFA</strong> - iShares MSCI EAFE (Actions internationales)
            </li>
            <li>
              <strong>EEM</strong> - iShares Emerging Markets (Marchés émergents)
            </li>
            <li>
              <strong>TLT</strong> - iShares 20+ Year Treasury (Obligations US)
            </li>
            <li>
              <strong>HYG</strong> - iShares High Yield Corporate (High Yield)
            </li>
            <li>
              <strong>GLD</strong> - SPDR Gold Shares (Or)
            </li>
            <li>
              <strong>VNQ</strong> - Vanguard Real Estate (Immobilier)
            </li>
            <li>
              <strong>SH</strong> - ProShares Short S&P 500 (Inverse)
            </li>
          </ul>
        </CardContent>
      </Card>

      {/* RGPD */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Protection des Données (RGPD)
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p>
            Cette application ne collecte aucune donnée personnelle des
            utilisateurs. Toutes les données affichées sont des données
            financières publiques :
          </p>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground">
            <li>Prix historiques des ETFs (via Yahoo Finance)</li>
            <li>Indicateurs macroéconomiques (via FRED - Federal Reserve)</li>
            <li>Taux et spreads publics</li>
          </ul>

          <Separator className="my-4" />

          <h3 className="font-semibold">Sous-traitants</h3>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground">
            <li>
              <strong>Supabase</strong> - Base de données PostgreSQL (hébergement
              EU)
            </li>
            <li>
              <strong>Google Cloud</strong> - BigQuery (hébergement EU)
            </li>
            <li>
              <strong>Vercel</strong> - Hébergement frontend
            </li>
          </ul>
        </CardContent>
      </Card>

      {/* Données */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Sources de Données
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <ul className="list-disc list-inside space-y-2 text-muted-foreground">
            <li>
              <strong>Yahoo Finance</strong> - Prix historiques des ETFs (API
              gratuite via yfinance)
            </li>
            <li>
              <strong>FRED</strong> - Indicateurs macroéconomiques de la Federal
              Reserve
            </li>
            <li>
              <strong>INSEE / BCE</strong> - Données d&apos;inflation zone euro
            </li>
          </ul>

          <Separator className="my-4" />

          <p className="text-sm text-muted-foreground">
            Les données sont mises à jour quotidiennement et stockées dans une
            base PostgreSQL. L&apos;historique couvre la période du 1er janvier
            2010 à aujourd&apos;hui.
          </p>
        </CardContent>
      </Card>

      {/* Auteur */}
      <Card>
        <CardHeader>
          <CardTitle>Auteur</CardTitle>
        </CardHeader>
        <CardContent>
          <p>
            <strong>Raphaël Martin</strong>
            <br />
            <span className="text-muted-foreground">
              3e année Bachelor Data & IA - ECE Paris
              <br />
              Alternant Data Engineering - L&apos;AGEFI (Groupe Bey Médias)
            </span>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
