'use client';

/**
 * React Query hooks pour les indicateurs macro.
 */

import { useQuery } from '@tanstack/react-query';
import { getMacro, getMacroLatest } from '@/lib/api';
import { DateRangeParams } from '@/types/api';

/**
 * Hook pour récupérer les indicateurs macro.
 */
export function useMacro(params?: DateRangeParams) {
  return useQuery({
    queryKey: ['macro', params],
    queryFn: () => getMacro(params),
  });
}

/**
 * Hook pour récupérer les dernières valeurs macro.
 */
export function useMacroLatest() {
  return useQuery({
    queryKey: ['macro-latest'],
    queryFn: getMacroLatest,
    // Rafraîchir moins souvent (données quotidiennes)
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}
