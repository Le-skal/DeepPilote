'use client';

/**
 * React Query hooks pour l'analyse.
 */

import { useQuery } from '@tanstack/react-query';
import { getCorrelations, getAllStats, getETFStats } from '@/lib/api';
import { DateRangeParams } from '@/types/api';

/**
 * Hook pour récupérer la matrice de corrélation.
 */
export function useCorrelations(params?: DateRangeParams) {
  return useQuery({
    queryKey: ['correlations', params],
    queryFn: () => getCorrelations(params),
  });
}

/**
 * Hook pour récupérer les stats de tous les ETFs.
 */
export function useAllStats(params?: DateRangeParams) {
  return useQuery({
    queryKey: ['all-stats', params],
    queryFn: () => getAllStats(params),
  });
}

/**
 * Hook pour récupérer les stats d'un ETF.
 */
export function useETFStats(ticker: string, params?: DateRangeParams) {
  return useQuery({
    queryKey: ['etf-stats', ticker, params],
    queryFn: () => getETFStats(ticker, params),
    enabled: !!ticker,
  });
}
