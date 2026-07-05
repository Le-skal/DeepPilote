/**
 * Fonctions de formatage pour l'affichage.
 */

/**
 * Formate un nombre en pourcentage.
 */
export function formatPercent(value: number | null | undefined, decimals = 2): string {
  if (value === null || value === undefined) return '-';
  return `${value >= 0 ? '+' : ''}${value.toFixed(decimals)}%`;
}

/**
 * Formate un nombre en devise.
 */
export function formatCurrency(value: number | null | undefined, decimals = 2): string {
  if (value === null || value === undefined) return '-';
  return `$${value.toFixed(decimals)}`;
}

/**
 * Formate un nombre avec séparateur de milliers.
 */
export function formatNumber(value: number | null | undefined, decimals = 2): string {
  if (value === null || value === undefined) return '-';
  return value.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/**
 * Formate une date en format lisible.
 */
export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('fr-FR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Formate une date en format court.
 */
export function formatDateShort(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('fr-FR', {
    month: '2-digit',
    day: '2-digit',
  });
}

/**
 * Détermine la couleur selon la valeur (positif/négatif).
 */
export function getValueColor(value: number | null | undefined): string {
  if (value === null || value === undefined) return 'text-muted-foreground';
  if (value > 0) return 'text-green-500';
  if (value < 0) return 'text-red-500';
  return 'text-muted-foreground';
}

/**
 * Formate une date en format lisible pour contexte.
 * "2010-01-04" -> "janv. 2010"
 */
export function formatDateReadable(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('fr-FR', {
    year: 'numeric',
    month: 'short',
  });
}

/**
 * Formate un return avec contexte de date.
 * Exemple: "+780.58% depuis janv. 2010"
 */
export function formatReturnWithContext(
  value: number | null | undefined,
  startDate: string | null | undefined,
  decimals = 2
): string {
  if (value === null || value === undefined) return '-';
  const formattedReturn = formatPercent(value, decimals);
  if (!startDate) return formattedReturn;
  const formattedDate = formatDateReadable(startDate);
  return `${formattedReturn} depuis ${formattedDate}`;
}

/**
 * Calcule la plage de dates pour une période donnée.
 */
export function getDateRangeFromPeriod(
  period: '7D' | '1M' | '3M' | '1Y' | 'MAX'
): { start_date?: string; end_date?: string } {
  if (period === 'MAX') return {}; // Pas de filtre

  const daysMap: Record<Exclude<typeof period, 'MAX'>, number> = {
    '7D': 7,
    '1M': 30,
    '3M': 90,
    '1Y': 365,
  };

  const endDate = new Date();
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - daysMap[period]);

  return {
    start_date: startDate.toISOString().split('T')[0],
    end_date: endDate.toISOString().split('T')[0],
  };
}

/**
 * Formate un grand nombre de façon compacte.
 * 1234567 -> "1.23M"
 */
export function formatCompact(value: number | null | undefined): string {
  if (value === null || value === undefined) return '-';
  if (Math.abs(value) >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(2)}M`;
  }
  if (Math.abs(value) >= 1_000) {
    return `${(value / 1_000).toFixed(1)}k`;
  }
  return value.toFixed(2);
}
