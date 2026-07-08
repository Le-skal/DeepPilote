/**
 * Client API pour les endpoints ML.
 */

import { fetchAPI } from './client';
import {
  RegimeResponse,
  PortfolioResponse,
  BacktestResponse,
  YearlyReturnsResponse,
  PredictionsResponse,
  MarketSentiment,
  TrackRecordResponse,
} from '@/types/api';

/**
 * Récupère le régime de marché actuel.
 */
export async function getRegime(): Promise<RegimeResponse> {
  return fetchAPI<RegimeResponse>('/api/v1/ml/regime');
}

/**
 * Récupère les poids optimaux du portefeuille.
 */
export async function getPortfolio(): Promise<PortfolioResponse> {
  return fetchAPI<PortfolioResponse>('/api/v1/ml/portfolio');
}

/**
 * Récupère la comparaison aux benchmarks.
 */
export async function getBacktest(years: number = 5): Promise<BacktestResponse> {
  return fetchAPI<BacktestResponse>(`/api/v1/ml/backtest?years=${years}`);
}

/**
 * Récupère les returns annuels par benchmark.
 */
export async function getYearlyReturns(years: number = 10): Promise<YearlyReturnsResponse> {
  return fetchAPI<YearlyReturnsResponse>(`/api/v1/ml/yearly-returns?years=${years}`);
}

/**
 * Récupère les prédictions et signaux par ETF.
 */
export async function getPredictions(): Promise<PredictionsResponse> {
  return fetchAPI<PredictionsResponse>('/api/v1/ml/predictions');
}

/**
 * Récupère le sentiment global du marché.
 */
export async function getMarketSentiment(): Promise<MarketSentiment> {
  return fetchAPI<MarketSentiment>('/api/v1/sentiment/market');
}

/**
 * Récupère le track record (fiabilité historique) du modèle.
 */
export async function getTrackRecord(): Promise<TrackRecordResponse> {
  return fetchAPI<TrackRecordResponse>('/api/v1/ml/track-record');
}
