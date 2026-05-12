-- DeepPilot - Table partitionnée des prix dans BigQuery
-- But: Stocker les prix historiques avec partitionnement par date.
-- Avantage: Requêtes plus rapides et coûts réduits (scan partiel).

-- Création de la table partitionnée
CREATE TABLE IF NOT EXISTS `deeppilot.prices_history` (
    date DATE NOT NULL,
    ticker STRING NOT NULL,
    open FLOAT64,
    high FLOAT64,
    low FLOAT64,
    close FLOAT64 NOT NULL,
    volume INT64,
    -- Métadonnées
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY date
CLUSTER BY ticker
OPTIONS (
    description = 'Prix historiques des ETF, partitionné par date',
    labels = [('project', 'deeppilot'), ('type', 'prices')],
    require_partition_filter = false  -- Optionnel mais recommandé pour prod
);

-- Insertion depuis un fichier CSV (exemple)
-- À exécuter via bq load ou la console BigQuery
/*
LOAD DATA INTO `deeppilot.prices_history`
FROM FILES (
    format = 'CSV',
    uris = ['gs://bucket/prices_*.csv'],
    skip_leading_rows = 1
);
*/

-- Requête de vérification après chargement
SELECT
    ticker,
    MIN(date) AS first_date,
    MAX(date) AS last_date,
    COUNT(*) AS row_count,
    COUNT(DISTINCT date) AS trading_days
FROM `deeppilot.prices_history`
GROUP BY ticker
ORDER BY ticker;

-- Statistiques sur les partitions
SELECT
    partition_id,
    total_rows,
    total_logical_bytes / 1024 / 1024 AS size_mb
FROM `deeppilot.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'prices_history'
ORDER BY partition_id DESC
LIMIT 20;
