/**
 * Hooks React Query pour les endpoints ML.
 */

import { useQuery } from '@tanstack/react-query';
import {
  getRegime,
  getPortfolio,
  getBacktest,
  getYearlyReturns,
  getPredictions,
  getMarketSentiment,
  getTrackRecord,
} from '@/lib/api/ml';
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
 * Hook pour le régime de marché actuel.
 */
export function useRegime() {
  return useQuery<RegimeResponse>({
    queryKey: ['regime'],
    queryFn: getRegime,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 10 * 60 * 1000, // Refresh toutes les 10 minutes
  });
}

/**
 * Hook pour les poids du portefeuille.
 */
export function usePortfolio() {
  return useQuery<PortfolioResponse>({
    queryKey: ['portfolio'],
    queryFn: getPortfolio,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 10 * 60 * 1000, // Refresh toutes les 10 minutes
  });
}

/**
 * Hook pour la comparaison aux benchmarks (backtest).
 */
export function useBacktest(years: number = 5) {
  return useQuery<BacktestResponse>({
    queryKey: ['backtest', years],
    queryFn: () => getBacktest(years),
    staleTime: 30 * 60 * 1000, // 30 minutes (données historiques)
  });
}

/**
 * Hook pour les returns annuels.
 */
export function useYearlyReturns(years: number = 10) {
  return useQuery<YearlyReturnsResponse>({
    queryKey: ['yearly-returns', years],
    queryFn: () => getYearlyReturns(years),
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
}

/**
 * Hook pour les prédictions et signaux par ETF.
 */
export function usePredictions() {
  return useQuery<PredictionsResponse>({
    queryKey: ['predictions'],
    queryFn: getPredictions,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 10 * 60 * 1000, // Refresh toutes les 10 minutes
  });
}

/**
 * Hook pour le sentiment global du marché.
 */
export function useMarketSentiment() {
  return useQuery<MarketSentiment>({
    queryKey: ['market-sentiment'],
    queryFn: getMarketSentiment,
    staleTime: 30 * 60 * 1000, // 30 minutes (sentiment change lentement)
    refetchInterval: 60 * 60 * 1000, // Refresh toutes les heures
  });
}

/**
 * Hook pour le track record (fiabilité historique) du modèle.
 */
export function useTrackRecord() {
  return useQuery<TrackRecordResponse>({
    queryKey: ['track-record'],
    queryFn: getTrackRecord,
    staleTime: 60 * 60 * 1000, // 1 heure (données historiques)
  });
}
