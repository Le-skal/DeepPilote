"""Vérification des données BigQuery."""
from dotenv import load_dotenv
load_dotenv()
from google.cloud import bigquery

client = bigquery.Client()
table_id = "n8n-credentials-475110.deeppilot.prices_simple"

# Stats
query = f"""
SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT ticker) as tickers,
    COUNT(DISTINCT date) as days,
    MIN(date) as date_min,
    MAX(date) as date_max
FROM `{table_id}`
"""

print("=== Stats BigQuery ===")
result = client.query(query).result()
for row in result:
    print(f"Lignes: {row.total_rows}")
    print(f"Tickers: {row.tickers}")
    print(f"Jours: {row.days}")
    print(f"Periode: {row.date_min} -> {row.date_max}")

# Échantillon
query2 = f"""
SELECT * FROM `{table_id}`
ORDER BY date DESC, ticker
LIMIT 5
"""
print("\nÉchantillon:")
for row in client.query(query2).result():
    print(f"  {row.date} | {row.ticker} | {row.close:.2f}")
