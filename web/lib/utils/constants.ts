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
