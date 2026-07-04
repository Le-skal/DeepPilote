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
  if (value > 0) return 'text-green-600';
  if (value < 0) return 'text-red-600';
  return 'text-muted-foreground';
}
