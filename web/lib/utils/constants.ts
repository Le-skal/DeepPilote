/**
 * Constantes de l'application DeepPilot.
 *
 * Theme: Cyberpunk Violet
 * Dernière mise à jour: 5 juillet 2026
 */

import { RegimeName } from '@/types/api';

/**
 * Liste des ETFs du portefeuille.
 */
export const ETF_TICKERS = [
  'SPY',
  'EFA',
  'EEM',
  'TLT',
  'HYG',
  'GLD',
  'VNQ',
  'SH',
] as const;

/**
 * Benchmarks pour comparaison.
 */
export const BENCHMARK_TICKERS = ['URTH', 'QQQ'] as const;

/**
 * Tous les tickers disponibles.
 */
export const ALL_TICKERS = [...ETF_TICKERS, ...BENCHMARK_TICKERS] as const;

/**
 * Couleurs par ETF - Palette Cyberpunk Violet.
 * Couleurs choisies pour contraster sur fond sombre violet.
 */
export const ETF_COLORS: Record<string, string> = {
  SPY: '#A855F7', // violet-500 (primary)
  EFA: '#22C55E', // green-500 (contrast)
  EEM: '#F59E0B', // amber-500 (warm accent)
  TLT: '#C084FC', // violet-400 (secondary violet)
  HYG: '#F43F5E', // rose-500 (warm)
  GLD: '#FBBF24', // yellow-400 (gold)
  VNQ: '#E879F9', // fuchsia-400 (neon)
  SH: '#94A3B8', // slate-400 (neutral)
  URTH: '#2DD4BF', // teal-400 (cool accent)
  QQQ: '#818CF8', // indigo-400 (blue-violet)
};

/**
 * Couleurs HEX pour les charts (avec variations).
 */
export const CHART_COLORS = {
  primary: '#A855F7',
  secondary: '#C084FC',
  accent: '#E879F9',
  success: '#22C55E',
  danger: '#EF4444',
  warning: '#F59E0B',
  neutral: '#64748B',
  grid: 'rgba(168, 85, 247, 0.1)',
  gridLight: 'rgba(168, 85, 247, 0.05)',
};

/**
 * Noms des régimes de marché.
 */
export const REGIME_NAMES: Record<number, RegimeName> = {
  0: 'bull',
  1: 'bear',
  2: 'volatile',
  3: 'stable',
};

/**
 * Labels des régimes en français.
 */
export const REGIME_LABELS: Record<RegimeName, string> = {
  bull: 'Haussier',
  bear: 'Baissier',
  volatile: 'Volatile',
  stable: 'Stable',
};

/**
 * Couleurs des régimes (Tailwind classes).
 * Vert/Rouge pour bull/bear (sémantique financière universelle).
 * Violet pour stable (thème principal).
 */
export const REGIME_COLORS: Record<RegimeName, string> = {
  bull: 'bg-green-500',
  bear: 'bg-red-500',
  volatile: 'bg-amber-500',
  stable: 'bg-violet-500',
};

/**
 * Couleurs des régimes (texte).
 */
export const REGIME_TEXT_COLORS: Record<RegimeName, string> = {
  bull: 'text-green-500',
  bear: 'text-red-500',
  volatile: 'text-amber-500',
  stable: 'text-violet-500',
};

/**
 * Couleurs HEX des régimes (pour charts).
 */
export const REGIME_HEX_COLORS: Record<RegimeName, string> = {
  bull: '#22C55E',
  bear: '#EF4444',
  volatile: '#F59E0B',
  stable: '#A855F7',
};

/**
 * Classes d'actifs.
 */
export const ASSET_CLASSES: Record<string, string> = {
  SPY: 'Actions US',
  EFA: 'Actions Internationales',
  EEM: 'Actions Émergentes',
  TLT: 'Obligations US',
  HYG: 'High Yield',
  GLD: 'Or',
  VNQ: 'Immobilier',
  SH: 'Short S&P 500',
  URTH: 'Actions Monde',
  QQQ: 'Tech US',
};

/**
 * Configuration des charts.
 */
export const CHART_CONFIG = {
  strokeWidth: 2,
  dotRadius: 4,
  activeDotRadius: 6,
  gridOpacity: 0.1,
  tooltipBg: '#19152A',
  tooltipBorder: 'rgba(168, 85, 247, 0.3)',
  axisColor: '#64748B',
  gradientStart: 0.3,
  gradientEnd: 0,
};

/**
 * Périodes disponibles pour les charts.
 */
export type TimePeriod = '7D' | '1M' | '3M' | '1Y' | 'MAX';

export const TIME_PERIODS: TimePeriod[] = ['7D', '1M', '3M', '1Y', 'MAX'];

export const PERIOD_DAYS: Record<TimePeriod, number | null> = {
  '7D': 7,
  '1M': 30,
  '3M': 90,
  '1Y': 365,
  'MAX': null,
};

export const PERIOD_LABELS: Record<TimePeriod, string> = {
  '7D': '7 derniers jours',
  '1M': 'Dernier mois',
  '3M': '3 derniers mois',
  '1Y': 'Dernière année',
  'MAX': 'Depuis le début',
};

/**
 * Explications des métriques financières en français simple.
 * Pour quelqu'un qui ne connaît RIEN à la finance.
 */
export interface MetricExplanation {
  short: string;
  long: string;
  example?: string;
  warning?: string;
}

export const METRIC_EXPLANATIONS: Record<string, MetricExplanation> = {
  total_return: {
    short: 'Gain total sur la période',
    long: 'Si tu avais investi 100€ au début de cette période, voici combien tu aurais gagné ou perdu.',
    example: '+50% signifie que tes 100€ seraient devenus 150€',
  },
  annualized_return: {
    short: 'Gain moyen par an',
    long: 'Le rendement annuel moyen. Permet de comparer des investissements sur différentes durées.',
    example: '8% = en moyenne, +8% par an',
  },
  sharpe_ratio: {
    short: 'Rendement vs risque',
    long: 'Mesure si les gains valent le risque pris. Plus c\'est élevé, mieux c\'est.',
    example: '< 0.5 = faible, 0.5-1 = correct, > 1 = bon, > 2 = excellent',
  },
  volatility: {
    short: 'Amplitude des variations',
    long: 'Comment le prix bouge au quotidien. Plus c\'est élevé, plus ça monte ET descend fort.',
    example: '20% = le prix varie typiquement de ±20% dans l\'année',
    warning: 'Volatilité élevée = émotions fortes, pas forcément mauvais',
  },
  max_drawdown: {
    short: 'Pire chute depuis un sommet',
    long: 'La perte maximale que tu aurais subie si tu avais acheté au plus haut et vendu au plus bas.',
    example: '-30% = au pire moment, tu aurais perdu 30%',
    warning: 'Montre le pire scénario historique',
  },
  positive_days_pct: {
    short: 'Jours de hausse',
    long: 'Pourcentage de jours où le prix a monté. Autour de 53% est normal pour les actions.',
    example: '55% = le prix monte un peu plus souvent qu\'il ne baisse',
  },
  best_day: {
    short: 'Meilleur jour',
    long: 'La plus grosse hausse en une seule journée. Les jours extrêmes arrivent souvent en période volatile.',
  },
  worst_day: {
    short: 'Pire jour',
    long: 'La plus grosse baisse en une seule journée. Montre la pire surprise possible.',
  },
  vix: {
    short: 'Indice de peur des marchés',
    long: 'Mesure l\'inquiétude des investisseurs. Quand il est haut, les gens ont peur.',
    example: '< 15 = calme, 15-20 = normal, 20-30 = nerveux, > 30 = panique',
  },
  yield_curve: {
    short: 'Indicateur de récession',
    long: 'Quand il est négatif (inversé), une récession arrive souvent dans les 6-18 mois.',
    warning: 'Négatif = signal d\'alerte économique',
  },
  credit_spread: {
    short: 'Stress des entreprises',
    long: 'Combien les entreprises paient en plus pour emprunter. Plus c\'est élevé, plus elles sont en difficulté.',
    example: '< 300 = normal, 300-500 = tendu, > 500 = stress élevé',
  },
  expected_return: {
    short: 'Rendement attendu',
    long: 'Ce que le modèle ML prédit comme rendement annuel pour ce portefeuille.',
  },
  portfolio_volatility: {
    short: 'Risque du portefeuille',
    long: 'Amplitude des variations attendues. Un portefeuille diversifié a moins de volatilité.',
  },
};

/**
 * Labels pour interpréter le Sharpe Ratio.
 */
export function getSharpeLabel(sharpe: number | null | undefined): string {
  if (sharpe === null || sharpe === undefined) return 'Non calculé';
  if (sharpe < 0) return 'Négatif (perte)';
  if (sharpe < 0.5) return 'Faible';
  if (sharpe < 1) return 'Correct';
  if (sharpe < 2) return 'Bon';
  return 'Excellent';
}

/**
 * Labels pour interpréter le VIX.
 */
export function getVIXLabel(vix: number | null | undefined): string {
  if (vix === null || vix === undefined) return 'Non disponible';
  if (vix < 15) return 'Marché très calme';
  if (vix < 20) return 'Marché normal';
  if (vix < 30) return 'Marché nerveux';
  return 'Marché en panique';
}

/**
 * Explications des régimes de marché pour débutants.
 */
export const REGIME_EXPLANATIONS: Record<RegimeName, string> = {
  bull: 'Le marché monte. Bon moment pour être investi en actions.',
  bear: 'Le marché baisse. Prudence recommandée, favoriser les valeurs refuges.',
  volatile: 'Le marché est imprévisible. Grosse incertitude, rester prudent.',
  stable: 'Le marché est calme. Peu de mouvements, situation normale.',
};
