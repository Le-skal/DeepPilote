/**
 * Client API pour DeepPilot.
 * Wrapper fetch avec gestion des erreurs.
 */

import { APIError } from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Fetch wrapper avec gestion des erreurs.
 */
export async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!res.ok) {
    const error: APIError = await res.json().catch(() => ({
      detail: `Erreur API: ${res.status} ${res.statusText}`,
    }));
    throw new Error(error.detail);
  }

  return res.json();
}

/**
 * Construit les query params pour une URL.
 */
export function buildQueryString(params: Record<string, string | number | undefined>): string {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, String(value));
    }
  });

  const queryString = searchParams.toString();
  return queryString ? `?${queryString}` : '';
}
