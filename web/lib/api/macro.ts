/**
 * Fonctions API pour les indicateurs macro.
 */

import { fetchAPI, buildQueryString } from './client';
import { MacroIndicatorList, MacroLatest, DateRangeParams } from '@/types/api';

/**
 * Récupère les indicateurs macro sur une période.
 */
export async function getMacro(params?: DateRangeParams): Promise<MacroIndicatorList> {
  const query = buildQueryString({
    start_date: params?.start_date,
    end_date: params?.end_date,
    limit: params?.limit,
  });
  return fetchAPI<MacroIndicatorList>(`/api/v1/macro${query}`);
}

/**
 * Récupère les dernières valeurs macro.
 */
export async function getMacroLatest(): Promise<MacroLatest> {
  return fetchAPI<MacroLatest>('/api/v1/macro/latest');
}
