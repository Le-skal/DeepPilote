/**
 * Fonctions API pour les ETFs.
 */

import { fetchAPI, buildQueryString } from './client';
import {
  ETFBase,
  ETFListResponse,
  ETFPriceList,
  ETFFeatureList,
  DateRangeParams,
} from '@/types/api';

/**
 * Récupère la liste des ETFs.
 */
export async function getETFs(): Promise<ETFListResponse> {
  return fetchAPI<ETFListResponse>('/api/v1/etfs');
}

/**
 * Récupère les détails d'un ETF.
 */
export async function getETF(ticker: string): Promise<ETFBase> {
  return fetchAPI<ETFBase>(`/api/v1/etfs/${ticker}`);
}

/**
 * Récupère l'historique des prix d'un ETF.
 */
export async function getETFPrices(
  ticker: string,
  params?: DateRangeParams
): Promise<ETFPriceList> {
  const query = buildQueryString({
    start_date: params?.start_date,
    end_date: params?.end_date,
    limit: params?.limit,
  });
  return fetchAPI<ETFPriceList>(`/api/v1/etfs/${ticker}/prices${query}`);
}

/**
 * Récupère les features ML d'un ETF.
 */
export async function getETFFeatures(
  ticker: string,
  params?: DateRangeParams
): Promise<ETFFeatureList> {
  const query = buildQueryString({
    start_date: params?.start_date,
    end_date: params?.end_date,
    limit: params?.limit,
  });
  return fetchAPI<ETFFeatureList>(`/api/v1/etfs/${ticker}/features${query}`);
}
