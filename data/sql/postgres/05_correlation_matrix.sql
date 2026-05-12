-- DeepPilot - Matrice de corrélations entre ETF
-- But: Calculer les corrélations des returns entre les 8 ETF.
-- Méthode: Corrélation de Pearson sur les returns journaliers.

-- Note: PostgreSQL ne dispose pas de fonction CORR() multi-colonnes native.
-- On utilise une approche avec auto-jointures.

-- Étape 1: Créer une table temporaire des returns pivotés
WITH returns_wide AS (
    SELECT
        date,
        MAX(CASE WHEN ticker = 'SPY' THEN ret_1d END) AS spy,
        MAX(CASE WHEN ticker = 'EFA' THEN ret_1d END) AS efa,
        MAX(CASE WHEN ticker = 'EEM' THEN ret_1d END) AS eem,
        MAX(CASE WHEN ticker = 'TLT' THEN ret_1d END) AS tlt,
        MAX(CASE WHEN ticker = 'HYG' THEN ret_1d END) AS hyg,
        MAX(CASE WHEN ticker = 'GLD' THEN ret_1d END) AS gld,
        MAX(CASE WHEN ticker = 'VNQ' THEN ret_1d END) AS vnq,
        MAX(CASE WHEN ticker = 'SH' THEN ret_1d END) AS sh
    FROM feature
    WHERE ret_1d IS NOT NULL
    GROUP BY date
)
-- Étape 2: Calculer les corrélations par paires
SELECT
    'SPY' AS ticker_1,
    'TLT' AS ticker_2,
    CORR(spy, tlt) AS correlation,
    COUNT(*) AS n_observations
FROM returns_wide
WHERE spy IS NOT NULL AND tlt IS NOT NULL

UNION ALL

SELECT 'SPY', 'GLD', CORR(spy, gld), COUNT(*)
FROM returns_wide WHERE spy IS NOT NULL AND gld IS NOT NULL

UNION ALL

SELECT 'SPY', 'SH', CORR(spy, sh), COUNT(*)
FROM returns_wide WHERE spy IS NOT NULL AND sh IS NOT NULL

UNION ALL

SELECT 'SPY', 'EEM', CORR(spy, eem), COUNT(*)
FROM returns_wide WHERE spy IS NOT NULL AND eem IS NOT NULL

UNION ALL

SELECT 'SPY', 'VNQ', CORR(spy, vnq), COUNT(*)
FROM returns_wide WHERE spy IS NOT NULL AND vnq IS NOT NULL

UNION ALL

SELECT 'TLT', 'GLD', CORR(tlt, gld), COUNT(*)
FROM returns_wide WHERE tlt IS NOT NULL AND gld IS NOT NULL

UNION ALL

SELECT 'TLT', 'HYG', CORR(tlt, hyg), COUNT(*)
FROM returns_wide WHERE tlt IS NOT NULL AND hyg IS NOT NULL

UNION ALL

SELECT 'GLD', 'SH', CORR(gld, sh), COUNT(*)
FROM returns_wide WHERE gld IS NOT NULL AND sh IS NOT NULL

ORDER BY ABS(correlation) DESC;

-- Résultats attendus:
-- SPY/SH: corrélation ~ -0.99 (inverse parfait)
-- SPY/TLT: corrélation négative (flight to quality)
-- SPY/VNQ: corrélation positive forte (actions/immobilier)
-- GLD/SPY: corrélation faible (diversification)
