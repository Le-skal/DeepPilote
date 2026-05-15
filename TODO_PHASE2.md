# DeepPilot — TODO Phase 2 : API REST + RGPD

> **Phase actuelle : Phase 2**
> Focus : créer une API REST FastAPI pour exposer les données + conformité RGPD complète.
> Compétences visées : C4 (complet), C5

---

## ÉTAPE 0 — Setup API

### 0.1 Nouvelles dépendances

- [ ] Ajouter au `requirements.txt` :
```
# API
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
pydantic>=2.6.0
pydantic-settings>=2.2.0

# Auth & sécurité
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4

# CORS
starlette>=0.36.0
```

- [ ] `pip install -r requirements.txt`

### 0.2 Structure dossiers API

- [ ] Créer `api/__init__.py`
- [ ] Créer `api/main.py` (point d'entrée FastAPI)
- [ ] Créer `api/config.py` (settings Pydantic)
- [ ] Créer `api/routers/__init__.py`
- [ ] Créer `api/models/__init__.py` (schemas Pydantic)
- [ ] Créer `api/dependencies.py` (dépendances communes)

---

## ÉTAPE 1 — Configuration FastAPI de base

### 1.1 App de base

- [ ] Dans `api/main.py` :
  - Créer l'app FastAPI avec metadata (title, description, version)
  - Configurer CORS (origins autorisées)
  - Endpoint `/health` → retourne `{"status": "ok"}`
  - Endpoint `/` → redirect vers `/docs`

### 1.2 Config settings

- [ ] Dans `api/config.py` :
  - Class `Settings(BaseSettings)` avec :
    - `SUPABASE_URL`
    - `SUPABASE_KEY`
    - `SUPABASE_DB_URL`
    - `API_VERSION = "1.0.0"`
    - `DEBUG = False`
  - Charger depuis `.env`

### 1.3 Test manuel

- [ ] Lancer `uvicorn api.main:app --reload`
- [ ] Vérifier `http://localhost:8000/health`
- [ ] Vérifier `http://localhost:8000/docs` (Swagger UI)

---

## ÉTAPE 2 — Schemas Pydantic (modèles de réponse)

### 2.1 Schemas ETF

- [ ] Créer `api/models/etf.py` :
```python
class ETFBase(BaseModel):
    ticker: str
    name: str
    asset_class: str

class ETFPrice(BaseModel):
    date: date
    ticker: str
    close: float
    volume: int | None

class ETFPriceHistory(BaseModel):
    ticker: str
    prices: list[ETFPrice]
    count: int
```

### 2.2 Schemas Macro

- [ ] Créer `api/models/macro.py` :
```python
class MacroIndicator(BaseModel):
    date: date
    vix: float | None
    credit_spread: float | None
    yield_curve_10y2y: float | None
    # ... autres champs
```

### 2.3 Schemas Features

- [ ] Créer `api/models/features.py` :
```python
class ETFFeatures(BaseModel):
    date: date
    ticker: str
    return_1d: float | None
    return_20d: float | None
    volatility_20d: float | None
    sma_20: float | None
    rsi_14: float | None
    # ...
```

---

## ÉTAPE 3 — Connexion base de données

### 3.1 Database dependency

- [ ] Créer `api/database.py` :
  - Fonction `get_db_connection()` avec SQLAlchemy
  - Context manager pour les sessions
  - Pool de connexions configuré

### 3.2 Repository pattern

- [ ] Créer `api/repositories/__init__.py`
- [ ] Créer `api/repositories/etf_repository.py` :
  - `get_all_etfs() -> list[ETF]`
  - `get_etf_by_ticker(ticker: str) -> ETF | None`
  - `get_prices(ticker: str, start_date, end_date) -> list[ETFPrice]`
- [ ] Créer `api/repositories/macro_repository.py` :
  - `get_macro_indicators(start_date, end_date) -> list[MacroIndicator]`
- [ ] Créer `api/repositories/features_repository.py` :
  - `get_features(ticker: str, start_date, end_date) -> list[ETFFeatures]`

---

## ÉTAPE 4 — Endpoints REST

### 4.1 Router ETF

- [ ] Créer `api/routers/etf.py` :
  - `GET /etfs` → liste des 10 ETF (metadata)
  - `GET /etfs/{ticker}` → détails d'un ETF
  - `GET /etfs/{ticker}/prices` → historique prix
    - Query params : `start_date`, `end_date`, `limit`
  - `GET /etfs/{ticker}/features` → features calculées
    - Query params : `start_date`, `end_date`

### 4.2 Router Macro

- [ ] Créer `api/routers/macro.py` :
  - `GET /macro` → indicateurs macro
    - Query params : `start_date`, `end_date`, `indicators` (liste)
  - `GET /macro/latest` → dernières valeurs connues

### 4.3 Router Analysis (lecture seule)

- [ ] Créer `api/routers/analysis.py` :
  - `GET /analysis/correlations` → matrice corrélation (calculée à la volée ou cache)
  - `GET /analysis/stats` → stats descriptives par ETF

### 4.4 Inclusion des routers

- [ ] Dans `api/main.py`, inclure tous les routers avec préfixes :
  - `/api/v1/etfs`
  - `/api/v1/macro`
  - `/api/v1/analysis`

---

## ÉTAPE 5 — Validation et gestion d'erreurs

### 5.1 Validation inputs

- [ ] Valider les tickers (doit être dans la liste des 10)
- [ ] Valider les dates (format ISO, pas dans le futur)
- [ ] Valider les ranges (start_date < end_date)

### 5.2 Gestion erreurs

- [ ] Créer `api/exceptions.py` :
  - `ETFNotFoundError`
  - `InvalidDateRangeError`
  - `DatabaseConnectionError`
- [ ] Exception handlers dans `main.py`
- [ ] Réponses HTTP standardisées (404, 400, 500)

---

## ÉTAPE 6 — Tests API

### 6.1 Tests unitaires

- [ ] Créer `tests/api/__init__.py`
- [ ] Créer `tests/api/test_etf_endpoints.py` :
  - Test `GET /etfs` retourne 10 ETF
  - Test `GET /etfs/SPY` retourne SPY
  - Test `GET /etfs/INVALID` retourne 404
  - Test `GET /etfs/SPY/prices` avec params
- [ ] Créer `tests/api/test_macro_endpoints.py`

### 6.2 Tests d'intégration

- [ ] Utiliser `TestClient` de FastAPI
- [ ] Tester le flow complet : request → DB → response

### 6.3 Lancer les tests

- [ ] `python -m pytest tests/api/ -v`
- [ ] Tous les tests passent

---

## ÉTAPE 7 — Documentation API

### 7.1 OpenAPI enrichi

- [ ] Ajouter descriptions aux endpoints (docstrings)
- [ ] Ajouter exemples dans les schemas Pydantic
- [ ] Tags pour grouper les endpoints dans Swagger

### 7.2 Documentation externe

- [ ] Créer `docs/api/README.md` :
  - Comment lancer l'API
  - Liste des endpoints
  - Exemples de requêtes curl
  - Codes d'erreur

---

## ÉTAPE 8 — RGPD Complet

### 8.1 Registre des traitements

- [ ] Compléter `docs/rgpd/registre_traitements.md` :
  - Finalité : analyse financière éducative
  - Base légale : intérêt légitime (pas de données perso pour l'instant)
  - Catégories de données : données financières publiques (ETF, macro)
  - Destinataires : utilisateurs de l'API
  - Durée de conservation : illimitée (données publiques)
  - Mesures de sécurité : HTTPS, auth future

### 8.2 Procédures

- [ ] Compléter `docs/rgpd/procedures_tri.md` :
  - Procédure de réponse aux demandes (droit d'accès, rectification, suppression)
  - Note : actuellement pas de données personnelles collectées

### 8.3 Mentions légales (pour l'app future)

- [ ] Créer `docs/rgpd/mentions_legales.md` :
  - Identité du responsable de traitement
  - Coordonnées DPO (toi pour le projet)
  - Finalités
  - Droits des personnes
  - Disclaimer investissement (cf. CLAUDE.md section 11)

### 8.4 Sécurité API (préparation)

- [ ] Rate limiting : ajouter `slowapi` pour limiter les requêtes
- [ ] Logging : logger les accès (sans données personnelles)
- [ ] Headers sécurité : X-Content-Type-Options, X-Frame-Options

---

## ÉTAPE 9 — Déploiement local / test final

### 9.1 Script de lancement

- [ ] Créer `scripts/run_api.py` ou `scripts/run_api.sh` :
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 9.2 Test complet

- [ ] Lancer l'API
- [ ] Tester tous les endpoints via Swagger UI
- [ ] Vérifier les temps de réponse (< 500ms)
- [ ] Vérifier les logs

### 9.3 Lint & format

- [ ] `black api/ tests/api/`
- [ ] `ruff check api/ tests/api/`

---

## ÉTAPE 10 — Commit final Phase 2

- [ ] Commit : "feat: REST API with FastAPI + RGPD compliance"
- [ ] Tag Git : `v0.2.0-api-phase`
- [ ] Push

---

## ✅ Definition of Done — Phase 2

La Phase 2 est terminée quand :

- [ ] API FastAPI fonctionnelle avec endpoints ETF, macro, analysis
- [ ] Schemas Pydantic pour toutes les réponses
- [ ] Validation des inputs + gestion d'erreurs propre
- [ ] Tests API passent (couverture > 70%)
- [ ] Documentation OpenAPI enrichie
- [ ] RGPD : registre des traitements complet
- [ ] RGPD : procédures documentées
- [ ] RGPD : mentions légales prêtes
- [ ] Rate limiting configuré
- [ ] API testable en local

**Compétences validées en Phase 2** : C4 (complet avec RGPD), C5 (API REST)

---

## 🚫 Hors scope Phase 2

- Auth utilisateurs (sera ajouté quand on aura l'app Next.js)
- Déploiement cloud (Render) — Phase 6-7
- Endpoints d'écriture (POST/PUT/DELETE) — pas nécessaire pour l'instant
- Cache Redis — pas nécessaire pour l'instant

