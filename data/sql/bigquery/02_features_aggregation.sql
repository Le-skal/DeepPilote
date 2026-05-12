-- DeepPilot - Agrégation des features mensuelles dans BigQuery
-- But: Créer une vue agrégée des features par mois pour le ML.
-- Avantage: Réduction de la volumétrie, lissage du bruit daily.

-- Vue des features mensuelles
CREATE OR REPLACE VIEW `deeppilot.v_monthly_features` AS
WITH daily_features AS (
    SELECT
        p.ticker,
        p.date,
        p.close,
        -- Return depuis le début du mois
        LAG(p.close) OVER (
            PARTITION BY p.ticker
            ORDER BY p.date
        ) AS prev_close,
        -- Première valeur du mois
        FIRST_VALUE(p.close) OVER (
            PARTITION BY p.ticker, DATE_TRUNC(p.date, MONTH)
            ORDER BY p.date
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS month_open,
        -- Dernière valeur du mois
        LAST_VALUE(p.close) OVER (
            PARTITION BY p.ticker, DATE_TRUNC(p.date, MONTH)
            ORDER BY p.date
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS month_close
    FROM `deeppilot.prices_history` p
),
monthly_stats AS (
    SELECT
        ticker,
        DATE_TRUNC(date, MONTH) AS month,
        -- Prix
        AVG(close) AS avg_price,
        MIN(close) AS min_price,
        MAX(close) AS max_price,
        ANY_VALUE(month_open) AS open_price,
        ANY_VALUE(month_close) AS close_price,
        -- Volatilité intra-mois
        STDDEV(SAFE_DIVIDE(close - prev_close, prev_close)) AS intra_month_volatility,
        -- Nombre de jours de trading
        COUNT(*) AS trading_days,
        -- Return mensuel
        SAFE_DIVIDE(
            ANY_VALUE(month_close) - ANY_VALUE(month_open),
            ANY_VALUE(month_open)
        ) AS monthly_return
    FROM daily_features
    GROUP BY ticker, DATE_TRUNC(date, MONTH)
)
SELECT
    ticker,
    month,
    avg_price,
    min_price,
    max_price,
    open_price,
    close_price,
    trading_days,
    monthly_return,
    -- Volatilité annualisée (× sqrt(12) pour mensuel → annuel)
    intra_month_volatility * SQRT(252) AS volatility_annualized,
    -- Range mensuel normalisé
    SAFE_DIVIDE(max_price - min_price, avg_price) AS price_range_pct,
    -- Indicateur de tendance
    CASE
        WHEN monthly_return > 0.05 THEN 'bullish'
        WHEN monthly_return < -0.05 THEN 'bearish'
        ELSE 'neutral'
    END AS trend
FROM monthly_stats
ORDER BY ticker, month DESC;

-- Statistiques agrégées par ticker
SELECT
    ticker,
    COUNT(*) AS total_months,
    AVG(monthly_return) AS avg_monthly_return,
    STDDEV(monthly_return) AS std_monthly_return,
    -- Sharpe ratio mensuel simplifié (sans risk-free)
    SAFE_DIVIDE(AVG(monthly_return), STDDEV(monthly_return)) AS monthly_sharpe,
    -- Meilleur et pire mois
    MAX(monthly_return) AS best_month,
    MIN(monthly_return) AS worst_month,
    -- Pourcentage de mois positifs
    COUNTIF(monthly_return > 0) / COUNT(*) AS pct_positive_months
FROM `deeppilot.v_monthly_features`
GROUP BY ticker
ORDER BY monthly_sharpe DESC;
