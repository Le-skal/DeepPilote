-- DeepPilot - Jointure prix × macro
-- But: Combiner les prix des ETF avec les indicateurs macro pour analyse.
-- Optimisation: Utilise les index sur (ticker, date) et (date).

-- Requête principale: prix journaliers avec indicateurs macro
SELECT
    p.ticker,
    p.date,
    p.close AS price,

    -- Indicateurs de volatilité et risque
    m.vix,
    m.credit_spread_hy,

    -- Indicateurs de politique monétaire
    m.yield_curve_10y2y,
    m.t3mo AS risk_free_rate,
    m.t10y,

    -- Autres indicateurs
    m.wti_oil,
    m.usd_eur,
    m.unemployment,
    m.cpi

FROM price p
LEFT JOIN macro_indicator m ON p.date = m.date

-- Filtrer sur une période si besoin
WHERE p.date >= '2010-01-01'
  AND p.date <= CURRENT_DATE

ORDER BY p.ticker, p.date;

-- Note: LEFT JOIN car les données macro peuvent avoir des gaps (jours fériés différents)
-- Les valeurs NULL seront forward-fillées en post-traitement Python
