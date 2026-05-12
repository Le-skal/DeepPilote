-- DeepPilot - Schéma initial PostgreSQL (Supabase)
-- Ce script crée les tables principales pour stocker les données du projet.

-- =============================================================================
-- Table: etf
-- Métadonnées des ETF du portefeuille
-- =============================================================================
CREATE TABLE IF NOT EXISTS etf (
    ticker VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    asset_class VARCHAR(50) NOT NULL,
    inception_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Contraintes
    CONSTRAINT etf_ticker_uppercase CHECK (ticker = UPPER(ticker))
);

COMMENT ON TABLE etf IS 'Métadonnées des ETF du portefeuille DeepPilot';
COMMENT ON COLUMN etf.ticker IS 'Symbole boursier (ex: SPY, TLT)';
COMMENT ON COLUMN etf.asset_class IS 'Classe d''actifs (equity_us, bond_us, etc.)';

-- =============================================================================
-- Table: price
-- Prix historiques des ETF (adjusted close)
-- =============================================================================
CREATE TABLE IF NOT EXISTS price (
    ticker VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open NUMERIC(12, 4),
    high NUMERIC(12, 4),
    low NUMERIC(12, 4),
    close NUMERIC(12, 4) NOT NULL,
    volume BIGINT,

    -- Clé primaire composite
    PRIMARY KEY (ticker, date),

    -- Clé étrangère vers etf
    CONSTRAINT fk_price_etf FOREIGN KEY (ticker) REFERENCES etf(ticker),

    -- Contraintes de validité
    CONSTRAINT price_positive CHECK (close > 0),
    CONSTRAINT price_ohlc_order CHECK (
        (low IS NULL OR high IS NULL OR low <= high) AND
        (open IS NULL OR low IS NULL OR open >= low) AND
        (open IS NULL OR high IS NULL OR open <= high) AND
        (close >= low OR low IS NULL) AND
        (close <= high OR high IS NULL)
    )
);

-- Index pour les requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_price_date ON price(date);
CREATE INDEX IF NOT EXISTS idx_price_ticker_date ON price(ticker, date DESC);

COMMENT ON TABLE price IS 'Prix historiques journaliers des ETF (adjusted close)';
COMMENT ON COLUMN price.close IS 'Prix de clôture ajusté (splits + dividendes)';

-- =============================================================================
-- Table: macro_indicator
-- Indicateurs macroéconomiques (FRED)
-- =============================================================================
CREATE TABLE IF NOT EXISTS macro_indicator (
    date DATE PRIMARY KEY,
    vix NUMERIC(8, 4),                    -- CBOE Volatility Index
    credit_spread_hy NUMERIC(8, 4),       -- High Yield credit spread
    yield_curve_10y2y NUMERIC(8, 4),      -- 10Y-2Y spread (peut être négatif)
    t3mo NUMERIC(8, 4),                   -- 3-month Treasury (risk-free rate)
    t10y NUMERIC(8, 4),                   -- 10-year Treasury
    wti_oil NUMERIC(10, 4),               -- WTI crude oil price
    usd_eur NUMERIC(8, 4),                -- USD/EUR exchange rate
    unemployment NUMERIC(6, 4),           -- US unemployment rate
    cpi NUMERIC(10, 4),                   -- US CPI index
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Contraintes de validité
    CONSTRAINT macro_vix_range CHECK (vix IS NULL OR (vix >= 0 AND vix <= 150)),
    CONSTRAINT macro_unemployment_range CHECK (unemployment IS NULL OR (unemployment >= 0 AND unemployment <= 30))
);

-- Index pour les jointures avec price
CREATE INDEX IF NOT EXISTS idx_macro_date ON macro_indicator(date DESC);

COMMENT ON TABLE macro_indicator IS 'Indicateurs macroéconomiques journaliers (source: FRED)';
COMMENT ON COLUMN macro_indicator.yield_curve_10y2y IS 'Spread 10Y-2Y, négatif = inversion';

-- =============================================================================
-- Table: feature
-- Features calculées pour le ML
-- =============================================================================
CREATE TABLE IF NOT EXISTS feature (
    ticker VARCHAR(10) NOT NULL,
    date DATE NOT NULL,

    -- Returns
    ret_1d NUMERIC(10, 6),      -- Return 1 jour
    ret_5d NUMERIC(10, 6),      -- Return 5 jours
    ret_20d NUMERIC(10, 6),     -- Return 20 jours (1 mois)
    ret_60d NUMERIC(10, 6),     -- Return 60 jours (3 mois)
    logret_1d NUMERIC(10, 6),   -- Log return 1 jour

    -- Volatilité
    vol_20d NUMERIC(10, 6),     -- Volatilité 20 jours annualisée
    vol_60d NUMERIC(10, 6),     -- Volatilité 60 jours annualisée

    -- Indicateurs techniques
    sma_20 NUMERIC(12, 4),      -- SMA 20 jours
    sma_50 NUMERIC(12, 4),      -- SMA 50 jours
    sma_200 NUMERIC(12, 4),     -- SMA 200 jours
    rsi_14 NUMERIC(8, 4),       -- RSI 14 jours
    macd NUMERIC(12, 6),        -- MACD
    macd_signal NUMERIC(12, 6), -- MACD signal line
    bb_position NUMERIC(8, 4),  -- Position dans les bandes de Bollinger (0-1)

    -- Métadonnées
    is_outlier BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Clé primaire composite
    PRIMARY KEY (ticker, date),

    -- Clé étrangère
    CONSTRAINT fk_feature_etf FOREIGN KEY (ticker) REFERENCES etf(ticker),

    -- Contraintes
    CONSTRAINT feature_rsi_range CHECK (rsi_14 IS NULL OR (rsi_14 >= 0 AND rsi_14 <= 100)),
    CONSTRAINT feature_return_range CHECK (ret_1d IS NULL OR (ret_1d >= -0.5 AND ret_1d <= 0.5))
);

-- Index pour les requêtes ML
CREATE INDEX IF NOT EXISTS idx_feature_ticker_date ON feature(ticker, date DESC);
CREATE INDEX IF NOT EXISTS idx_feature_date ON feature(date DESC);

COMMENT ON TABLE feature IS 'Features calculées pour les modèles ML';
COMMENT ON COLUMN feature.vol_20d IS 'Volatilité rolling 20j, annualisée (* sqrt(252))';
COMMENT ON COLUMN feature.is_outlier IS 'True si return journalier > |10%|';

-- =============================================================================
-- Vue: v_prices_with_macro
-- Vue joignant prix et macro pour les analyses
-- =============================================================================
CREATE OR REPLACE VIEW v_prices_with_macro AS
SELECT
    p.ticker,
    p.date,
    p.close,
    m.vix,
    m.credit_spread_hy,
    m.yield_curve_10y2y,
    m.t3mo
FROM price p
LEFT JOIN macro_indicator m ON p.date = m.date
ORDER BY p.ticker, p.date;

COMMENT ON VIEW v_prices_with_macro IS 'Jointure prix × macro pour analyses';
