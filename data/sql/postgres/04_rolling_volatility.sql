-- DeepPilot - Calcul de la volatilité rolling avec window functions
-- But: Calculer la volatilité réalisée sur fenêtre glissante.
-- Méthode: Écart-type des log returns sur 20 jours, annualisé.

-- Volatilité rolling 20 jours
WITH daily_returns AS (
    SELECT
        ticker,
        date,
        close,
        -- Log return = ln(P_t / P_{t-1})
        LN(close / LAG(close) OVER (PARTITION BY ticker ORDER BY date)) AS log_return
    FROM price
),
rolling_stats AS (
    SELECT
        ticker,
        date,
        close,
        log_return,
        -- Écart-type sur 20 jours glissants
        STDDEV(log_return) OVER (
            PARTITION BY ticker
            ORDER BY date
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS rolling_std_20d,
        -- Nombre de jours dans la fenêtre (pour filtrer les débuts)
        COUNT(log_return) OVER (
            PARTITION BY ticker
            ORDER BY date
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS window_size
    FROM daily_returns
)
SELECT
    ticker,
    date,
    close,
    log_return,
    rolling_std_20d,
    -- Annualisation: volatilité × sqrt(252)
    rolling_std_20d * SQRT(252) AS volatility_20d_annualized,
    window_size
FROM rolling_stats
-- Filtrer les premières lignes où la fenêtre n'est pas complète
WHERE window_size >= 20
ORDER BY ticker, date DESC;

-- Volatilité moyenne par ETF et par année
SELECT
    ticker,
    EXTRACT(YEAR FROM date) AS year,
    AVG(f.vol_20d) AS avg_volatility,
    MIN(f.vol_20d) AS min_volatility,
    MAX(f.vol_20d) AS max_volatility
FROM feature f
WHERE f.vol_20d IS NOT NULL
GROUP BY ticker, EXTRACT(YEAR FROM date)
ORDER BY ticker, year DESC;
