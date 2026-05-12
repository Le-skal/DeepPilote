# Requêtes SQL — DeepPilot

Ce dossier contient les requêtes SQL utilisées dans le projet, organisées par base de données.

## Structure

```
sql/
├── postgres/           # Requêtes pour Supabase (PostgreSQL)
│   ├── 01_init_schema.sql
│   ├── 02_join_prices_macro.sql
│   ├── 03_monthly_returns.sql
│   ├── 04_rolling_volatility.sql
│   └── 05_correlation_matrix.sql
│
└── bigquery/           # Requêtes pour Google BigQuery
    ├── 01_partitioned_prices.sql
    └── 02_features_aggregation.sql
```

## PostgreSQL (Supabase)

### 01_init_schema.sql
**But**: Créer le schéma initial de la base de données.

Tables créées:
- `etf`: Métadonnées des ETF (ticker, nom, classe d'actifs)
- `price`: Prix historiques journaliers
- `macro_indicator`: Indicateurs macroéconomiques (VIX, courbe taux, etc.)
- `feature`: Features calculées pour le ML

Optimisations:
- Index composites sur (ticker, date) pour les jointures rapides
- Contraintes CHECK pour la validation des données
- Vue `v_prices_with_macro` pour simplifier les requêtes d'analyse

### 02_join_prices_macro.sql
**But**: Joindre les prix ETF avec les indicateurs macro.

Utilisation: Analyse exploratoire, calcul de corrélations prix/macro.

### 03_monthly_returns.sql
**But**: Calculer les rendements mensuels par ETF.

Méthode: Window functions `FIRST_VALUE` / `LAST_VALUE` pour obtenir prix de début et fin de mois.

### 04_rolling_volatility.sql
**But**: Calculer la volatilité rolling 20 jours.

Méthode:
1. Calcul des log returns avec `LAG()`
2. Écart-type rolling avec `STDDEV() OVER (ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)`
3. Annualisation: × √252

### 05_correlation_matrix.sql
**But**: Calculer la matrice de corrélations entre ETF.

Méthode: Pivot des returns puis `CORR()` par paires.

Résultats attendus:
- SPY/SH: ~-0.99 (inverse parfait)
- SPY/TLT: négative (flight to quality)
- SPY/VNQ: positive forte
- GLD/SPY: faible (diversification)

## BigQuery

### 01_partitioned_prices.sql
**But**: Créer une table partitionnée par date pour les prix.

Avantages du partitionnement:
- Requêtes sur une période = scan partiel seulement
- Coûts réduits (facturation au volume scanné)
- Maintenance facilitée (suppression par partition)

Options:
- `PARTITION BY date`: Partitionnement par jour
- `CLUSTER BY ticker`: Tri physique par ticker (améliore les filtres)

### 02_features_aggregation.sql
**But**: Agréger les features au niveau mensuel.

Utilisation: Préparation des données pour le ML (granularité mensuelle = réduction bruit).

## Bonnes pratiques

### Performance
- Toujours utiliser les index existants (filtrer sur ticker ET date)
- Éviter `SELECT *`, lister les colonnes explicitement
- Utiliser `EXPLAIN ANALYZE` pour optimiser les requêtes lentes

### Sécurité
- Les credentials sont dans `.env`, jamais hardcodées
- Utiliser des paramètres préparés en Python (pas de f-strings avec SQL)

### Idempotence
- Les scripts utilisent `CREATE TABLE IF NOT EXISTS`
- Les insertions utilisent `ON CONFLICT DO UPDATE`
- Relancer un script ne crée pas de doublons

## Exécution

### Via Python
```python
from data.pipeline.load_to_db import execute_sql_file, connect_supabase

engine = connect_supabase()
execute_sql_file(engine, Path("data/sql/postgres/01_init_schema.sql"))
```

### Via Supabase SQL Editor
1. Aller sur https://app.supabase.com
2. Sélectionner le projet `deeppilot`
3. Onglet "SQL Editor"
4. Copier-coller le contenu du fichier
5. Exécuter

### Via BigQuery Console
1. Aller sur https://console.cloud.google.com/bigquery
2. Sélectionner le projet
3. Créer une nouvelle requête
4. Copier-coller et exécuter
