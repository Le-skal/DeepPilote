# Schéma de base de données — DeepPilot

Ce document décrit le modèle de données du projet, stocké dans Supabase (PostgreSQL).

## Modèle Conceptuel de Données (MCD)

```
┌─────────────────┐
│      ETF        │
├─────────────────┤
│ ticker (PK)     │
│ name            │
│ asset_class     │
│ inception_date  │
└────────┬────────┘
         │
         │ 1,n
         ▼
┌─────────────────┐       ┌─────────────────────┐
│     PRICE       │       │   MACRO_INDICATOR   │
├─────────────────┤       ├─────────────────────┤
│ ticker (PK,FK)  │       │ date (PK)           │
│ date (PK)       │       │ vix                 │
│ close           │       │ credit_spread_hy    │
│ open            │       │ yield_curve_10y2y   │
│ high            │       │ t3mo                │
│ low             │       │ t10y                │
│ volume          │       │ wti_oil             │
└────────┬────────┘       │ usd_eur             │
         │                │ unemployment        │
         │ 1,1            │ cpi                 │
         ▼                └─────────────────────┘
┌─────────────────┐
│    FEATURE      │
├─────────────────┤
│ ticker (PK,FK)  │
│ date (PK)       │
│ ret_1d          │
│ ret_20d         │
│ vol_20d         │
│ sma_20          │
│ rsi_14          │
│ macd            │
│ is_outlier      │
└─────────────────┘
```

## Tables

### etf
Métadonnées des ETF du portefeuille.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| ticker | VARCHAR(10) | PK | Symbole boursier (ex: SPY) |
| name | VARCHAR(100) | NOT NULL | Nom complet |
| asset_class | VARCHAR(50) | NOT NULL | Classe d'actifs |
| inception_date | DATE | - | Date de création de l'ETF |
| created_at | TIMESTAMP | DEFAULT NOW() | Date d'insertion |

**Index** : PK sur `ticker`

### price
Prix historiques journaliers des ETF.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| ticker | VARCHAR(10) | PK, FK→etf | Symbole boursier |
| date | DATE | PK | Date de cotation |
| open | NUMERIC(12,4) | - | Prix d'ouverture |
| high | NUMERIC(12,4) | - | Plus haut du jour |
| low | NUMERIC(12,4) | - | Plus bas du jour |
| close | NUMERIC(12,4) | NOT NULL, >0 | Prix de clôture ajusté |
| volume | BIGINT | - | Volume échangé |

**Clé primaire** : (ticker, date)
**Index** : `idx_price_date`, `idx_price_ticker_date`

### macro_indicator
Indicateurs macroéconomiques journaliers.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| date | DATE | PK | Date |
| vix | NUMERIC(8,4) | [0, 150] | Indice de volatilité |
| credit_spread_hy | NUMERIC(8,4) | - | Spread crédit high yield |
| yield_curve_10y2y | NUMERIC(8,4) | - | Spread 10Y-2Y (peut être <0) |
| t3mo | NUMERIC(8,4) | - | Taux 3 mois (risk-free) |
| t10y | NUMERIC(8,4) | - | Taux 10 ans |
| wti_oil | NUMERIC(10,4) | - | Prix pétrole WTI |
| usd_eur | NUMERIC(8,4) | - | Taux USD/EUR |
| unemployment | NUMERIC(6,4) | [0, 30] | Taux de chômage US |
| cpi | NUMERIC(10,4) | - | Indice des prix |

**Index** : `idx_macro_date`

### feature
Features calculées pour le ML.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| ticker | VARCHAR(10) | PK, FK→etf | Symbole boursier |
| date | DATE | PK | Date |
| ret_1d | NUMERIC(10,6) | [-0.5, 0.5] | Return 1 jour |
| ret_5d | NUMERIC(10,6) | - | Return 5 jours |
| ret_20d | NUMERIC(10,6) | - | Return 20 jours |
| ret_60d | NUMERIC(10,6) | - | Return 60 jours |
| logret_1d | NUMERIC(10,6) | - | Log return 1 jour |
| vol_20d | NUMERIC(10,6) | - | Volatilité 20j annualisée |
| vol_60d | NUMERIC(10,6) | - | Volatilité 60j annualisée |
| sma_20 | NUMERIC(12,4) | - | SMA 20 jours |
| sma_50 | NUMERIC(12,4) | - | SMA 50 jours |
| sma_200 | NUMERIC(12,4) | - | SMA 200 jours |
| rsi_14 | NUMERIC(8,4) | [0, 100] | RSI 14 jours |
| macd | NUMERIC(12,6) | - | MACD |
| macd_signal | NUMERIC(12,6) | - | Signal MACD |
| bb_position | NUMERIC(8,4) | - | Position Bollinger |
| is_outlier | BOOLEAN | DEFAULT FALSE | Flag outlier |

**Clé primaire** : (ticker, date)
**Index** : `idx_feature_ticker_date`, `idx_feature_date`

## Vues

### v_prices_with_macro
Jointure prix × macro pour faciliter les analyses.

```sql
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
```

## Volumétrie estimée

| Table | Lignes estimées | Taille estimée |
|-------|-----------------|----------------|
| etf | 10 | < 1 KB |
| price | ~38 000 (10 ETF × 15 ans × 252 jours) | ~3 MB |
| macro_indicator | ~3 800 (15 ans × 252 jours) | ~500 KB |
| feature | ~30 000 (8 ETF × 15 ans × 252 jours) | ~5 MB |

**Total** : < 10 MB (largement dans le free tier Supabase de 500 MB)

## Requêtes fréquentes

### Prix d'un ETF sur une période
```sql
SELECT date, close
FROM price
WHERE ticker = 'SPY'
  AND date BETWEEN '2020-01-01' AND '2020-12-31'
ORDER BY date;
```

### Données complètes pour ML
```sql
SELECT f.*, m.vix, m.yield_curve_10y2y
FROM feature f
JOIN macro_indicator m ON f.date = m.date
WHERE f.ticker = 'SPY'
ORDER BY f.date;
```

### Performance utilisant les index
```sql
-- Utilise idx_price_ticker_date
EXPLAIN ANALYZE
SELECT * FROM price
WHERE ticker = 'SPY' AND date >= '2024-01-01';
```

## Migration et évolution

### Ajout d'une nouvelle feature
```sql
ALTER TABLE feature ADD COLUMN new_feature NUMERIC(10,6);
```

### Ajout d'un nouvel ETF
```sql
INSERT INTO etf (ticker, name, asset_class, inception_date)
VALUES ('IWM', 'iShares Russell 2000', 'equity_us_small', '2000-05-22');
```

## Backup

Supabase effectue des backups automatiques quotidiens (7 jours de rétention sur le free tier).

Pour un export manuel :
```bash
pg_dump $SUPABASE_DB_URL > backup_$(date +%Y%m%d).sql
```
