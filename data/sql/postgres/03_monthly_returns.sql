-- DeepPilot - Agrégation des rendements mensuels par ETF
-- But: Calculer les rendements mensuels pour analyse de performance.
-- Méthode: Comparer le premier et dernier prix du mois.

-- Rendements mensuels par ETF
WITH monthly_prices AS (
    SELECT
        ticker,
        DATE_TRUNC('month', date) AS month,
        -- Premier prix du mois (ordre croissant)
        FIRST_VALUE(close) OVER (
            PARTITION BY ticker, DATE_TRUNC('month', date)
            ORDER BY date ASC
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS first_price,
        -- Dernier prix du mois
        LAST_VALUE(close) OVER (
            PARTITION BY ticker, DATE_TRUNC('month', date)
            ORDER BY date ASC
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS last_price,
        -- Nombre de jours de trading
        COUNT(*) OVER (
            PARTITION BY ticker, DATE_TRUNC('month', date)
        ) AS trading_days
    FROM price
)
SELECT DISTINCT
    ticker,
    month,
    first_price,
    last_price,
    trading_days,
    -- Rendement mensuel simple
    (last_price - first_price) / first_price AS monthly_return,
    -- Rendement mensuel en pourcentage
    ROUND(((last_price - first_price) / first_price) * 100, 2) AS monthly_return_pct
FROM monthly_prices
ORDER BY ticker, month DESC;

-- Statistiques mensuelles agrégées par ETF
SELECT
    ticker,
    COUNT(DISTINCT DATE_TRUNC('month', date)) AS total_months,
    AVG((
        SELECT (p2.close - p1.close) / p1.close
        FROM price p1, price p2
        WHERE p1.ticker = price.ticker
          AND p2.ticker = price.ticker
          AND DATE_TRUNC('month', p1.date) = DATE_TRUNC('month', price.date)
          AND DATE_TRUNC('month', p2.date) = DATE_TRUNC('month', price.date)
          AND p1.date = (SELECT MIN(date) FROM price WHERE ticker = price.ticker AND DATE_TRUNC('month', date) = DATE_TRUNC('month', price.date))
          AND p2.date = (SELECT MAX(date) FROM price WHERE ticker = price.ticker AND DATE_TRUNC('month', date) = DATE_TRUNC('month', price.date))
    )) AS avg_monthly_return
FROM price
GROUP BY ticker
ORDER BY ticker;
