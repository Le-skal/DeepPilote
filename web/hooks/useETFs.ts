'use client';

/**
 * React Query hooks pour les ETFs.
 */

import { useQuery } from '@tanstack/react-query';
import { getETFs, getETF, getETFPrices, getETFFeatures } from '@/lib/api';
import { DateRangeParams } from '@/types/api';

/**
 * Hook pour récupérer la liste des ETFs.
 */
export function useETFs() {
  return useQuery({
    queryKey: ['etfs'],
    queryFn: getETFs,
  });
}

/**
 * Hook pour récupérer un ETF spécifique.
 */
export function useETF(ticker: string) {
  return useQuery({
    queryKey: ['etf', ticker],
    queryFn: () => getETF(ticker),
    enabled: !!ticker,
  });
}

/**
 * Hook pour récupérer les prix d'un ETF.
 */
export function useETFPrices(ticker: string, params?: DateRangeParams) {
  return useQuery({
    queryKey: ['etf-prices', ticker, params],
    queryFn: () => getETFPrices(ticker, params),
    enabled: !!ticker,
  });
}

/**
 * Hook pour récupérer les features d'un ETF.
 */
export function useETFFeatures(ticker: string, params?: DateRangeParams) {
  return useQuery({
    queryKey: ['etf-features', ticker, params],
    queryFn: () => getETFFeatures(ticker, params),
    enabled: !!ticker,
  });
}
