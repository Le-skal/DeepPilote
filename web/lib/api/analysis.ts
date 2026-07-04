/**
 * Fonctions API pour l'analyse.
 */

import { fetchAPI, buildQueryString } from './client';
import {
  CorrelationMatrix,
  StatsResponse,
  ETFStats,
  DateRangeParams,
} from '@/types/api';

/**
 * Récupère la matrice de corrélation.
 */
export async function getCorrelations(
  params?: DateRangeParams
): Promise<CorrelationMatrix> {
  const query = buildQueryString({
    start_date: params?.start_date,
    end_date: params?.end_date,
  });
  return fetchAPI<CorrelationMatrix>(`/api/v1/analysis/correlations${query}`);
}

/**
 * Récupère les stats de tous les ETFs.
 */
export async function getAllStats(params?: DateRangeParams): Promise<StatsResponse> {
  const query = buildQueryString({
    start_date: params?.start_date,
    end_date: params?.end_date,
  });
  return fetchAPI<StatsResponse>(`/api/v1/analysis/stats${query}`);
}

/**
 * Récupère les stats d'un ETF spécifique.
 */
export async function getETFStats(
  ticker: string,
  params?: DateRangeParams
): Promise<ETFStats> {
  const query = buildQueryString({
    start_date: params?.start_date,
    end_date: params?.end_date,
  });
  return fetchAPI<ETFStats>(`/api/v1/analysis/stats/${ticker}${query}`);
}
