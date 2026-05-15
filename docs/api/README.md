# DeepPilot API - Documentation

## Démarrage rapide

### Lancer l'API en local

```bash
# Depuis la racine du projet
python -m uvicorn api.main:app --reload

# Ou avec le script
python scripts/run_api.py --reload
```

L'API est disponible sur `http://localhost:8000`

### Documentation interactive

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc
- **OpenAPI JSON** : http://localhost:8000/openapi.json

---

## Endpoints disponibles

### ETF

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/etfs` | Liste des 10 ETF avec métadonnées |
| GET | `/api/v1/etfs/{ticker}` | Détails d'un ETF |
| GET | `/api/v1/etfs/{ticker}/prices` | Historique des prix |
| GET | `/api/v1/etfs/{ticker}/features` | Features ML calculées |

### Macro

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/macro` | Indicateurs macro (VIX, taux, etc.) |
| GET | `/api/v1/macro/latest` | Dernières valeurs connues |

### Analysis

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/analysis/correlations` | Matrice de corrélation |
| GET | `/api/v1/analysis/stats` | Stats par ETF |
| GET | `/api/v1/analysis/stats/{ticker}` | Stats d'un ETF |

### Health

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/health` | Status de l'API et de la DB |

---

## Exemples de requêtes

### Liste des ETF

```bash
curl http://localhost:8000/api/v1/etfs
```

Réponse :
```json
{
  "count": 10,
  "etfs": [
    {
      "ticker": "SPY",
      "name": "SPDR S&P 500 ETF Trust",
      "asset_class": "Actions US large cap",
      "description": "Cœur actions US"
    },
    ...
  ]
}
```

### Prix d'un ETF avec filtres

```bash
curl "http://localhost:8000/api/v1/etfs/SPY/prices?start_date=2024-01-01&end_date=2024-12-31&limit=100"
```

### Indicateurs macro

```bash
curl http://localhost:8000/api/v1/macro/latest
```

Réponse :
```json
{
  "as_of_date": "2026-05-05",
  "vix": 18.42,
  "t3mo": 5.21,
  "t10y": 4.35,
  "yield_curve_10y2y": -0.12,
  "credit_spread": 3.45,
  "oil_wti": 78.50
}
```

### Matrice de corrélation

```bash
curl "http://localhost:8000/api/v1/analysis/correlations?start_date=2020-01-01"
```

---

## Paramètres de requête

### Filtres de date

| Paramètre | Format | Description |
|-----------|--------|-------------|
| `start_date` | YYYY-MM-DD | Date de début (incluse) |
| `end_date` | YYYY-MM-DD | Date de fin (incluse) |

### Pagination

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `limit` | int | 1000 | Nombre max de résultats (1-10000) |

---

## Codes d'erreur

| Code | Description |
|------|-------------|
| 200 | Succès |
| 400 | Requête invalide (ex: date de fin avant date de début) |
| 404 | Ressource non trouvée (ex: ticker invalide) |
| 429 | Trop de requêtes (rate limiting: 100/minute) |
| 500 | Erreur serveur |
| 503 | Base de données indisponible |

### Exemple d'erreur

```json
{
  "detail": "ETF 'INVALID' non trouvé. Tickers valides: SPY, EFA, EEM, TLT, HYG, GLD, VNQ, SH, URTH, QQQ"
}
```

---

## Rate Limiting

L'API est limitée à **100 requêtes par minute** par IP.

En cas de dépassement, vous recevrez un code `429 Too Many Requests`.

---

## Tickers supportés

### ETF du portefeuille (8)

| Ticker | Nom | Classe d'actifs |
|--------|-----|-----------------|
| SPY | SPDR S&P 500 | Actions US |
| EFA | iShares MSCI EAFE | Actions développées |
| EEM | iShares Emerging Markets | Actions émergentes |
| TLT | iShares 20+ Year Treasury | Obligations US |
| HYG | iShares High Yield | Obligations HY |
| GLD | SPDR Gold | Or |
| VNQ | Vanguard Real Estate | Immobilier |
| SH | ProShares Short S&P 500 | Inverse S&P 500 |

### Benchmarks (2)

| Ticker | Nom |
|--------|-----|
| URTH | iShares MSCI World |
| QQQ | Invesco NASDAQ 100 |

---

## Configuration

### Variables d'environnement

L'API utilise les variables suivantes (fichier `.env`) :

```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
SUPABASE_DB_URL=postgresql://...
```

### CORS

Origins autorisées par défaut :
- `http://localhost:3000` (Next.js)
- `http://localhost:8000` (FastAPI)

---

## Développement

### Lancer les tests

```bash
python -m pytest tests/api/ -v
```

### Structure du code

```
api/
├── main.py           # Point d'entrée FastAPI
├── config.py         # Settings (Pydantic)
├── database.py       # Connexion Supabase
├── exceptions.py     # Erreurs custom
├── models/           # Schemas Pydantic
├── repositories/     # Accès données
└── routers/          # Endpoints
```
