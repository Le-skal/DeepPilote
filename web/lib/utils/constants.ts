/**
 * Constantes de l'application DeepPilot.
 *
 * Phase 7 - CI/CD validated (4 juillet 2026)
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
 * Couleurs par ETF.
 */
export const ETF_COLORS: Record<string, string> = {
  SPY: '#3B82F6', // blue
  EFA: '#10B981', // green
  EEM: '#F59E0B', // amber
  TLT: '#8B5CF6', // violet
  HYG: '#EF4444', // red
  GLD: '#F59E0B', // yellow
  VNQ: '#EC4899', // pink
  SH: '#6B7280', // gray
  URTH: '#14B8A6', // teal
  QQQ: '#6366F1', // indigo
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
 * Couleurs des régimes.
 */
export const REGIME_COLORS: Record<RegimeName, string> = {
  bull: 'bg-green-500',
  bear: 'bg-red-500',
  volatile: 'bg-amber-500',
  stable: 'bg-blue-500',
};

/**
 * Couleurs des régimes (texte).
 */
export const REGIME_TEXT_COLORS: Record<RegimeName, string> = {
  bull: 'text-green-600',
  bear: 'text-red-600',
  volatile: 'text-amber-600',
  stable: 'text-blue-600',
};

/**
 * Classes d'actifs.
 */
export const ASSET_CLASSES = {
  SPY: 'Actions US',
  EFA: 'Actions Internationales',
  EEM: 'Actions Émergentes',
  TLT: 'Obligations US',
  HYG: 'High Yield',
  GLD: 'Or',
  VNQ: 'Immobilier',
  SH: 'Short S&P 500',
};
