/**
 * Hooks React Query pour les endpoints ML.
 */

import { useQuery } from '@tanstack/react-query';
import { getRegime, getPortfolio } from '@/lib/api/ml';
import { RegimeResponse, PortfolioResponse } from '@/types/api';

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
