/**
 * Client API pour les endpoints ML.
 */

import { fetchAPI } from './client';
import { RegimeResponse, PortfolioResponse } from '@/types/api';

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
