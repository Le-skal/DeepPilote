"""
Point d'entrée de l'API DeepPilot.

Lance avec: uvicorn api.main:app --reload
Docs: http://localhost:8000/docs
"""

from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

from api.config import get_settings
from api.database import check_db_connection
from api.models.analysis import HealthResponse
from api.routers import analysis, etf, macro, ml


# Initialiser Sentry (si DSN configuré)
_settings = get_settings()
if _settings.sentry_dsn:
    sentry_sdk.init(
        dsn=_settings.sentry_dsn,
        environment=_settings.sentry_environment,
        traces_sample_rate=0.1,  # 10% des requêtes tracées
        profiles_sample_rate=0.1,
    )
    print(f"[OK] Sentry initialized ({_settings.sentry_environment})")


class CORSErrorMiddleware(BaseHTTPMiddleware):
    """Middleware pour ajouter CORS headers meme sur les erreurs 500."""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Log l'erreur
            print(f"[ERROR] {request.method} {request.url.path}: {e}")
            # Retourner une reponse JSON avec headers CORS
            return JSONResponse(
                status_code=500,
                content={"detail": str(e)},
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, OPTIONS",
                    "Access-Control-Allow-Headers": "*",
                },
            )


# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events de l'application."""
    # Startup
    settings = get_settings()
    print(f"[START] DeepPilot API v{settings.api_version} starting...")
    print(f"[INFO] Debug mode: {settings.debug}")

    # Vérifier la connexion DB
    if check_db_connection():
        print("[OK] Database connection OK")
    else:
        print("[WARN] Database connection FAILED - some endpoints may not work")

    yield

    # Shutdown
    print("[STOP] DeepPilot API shutting down...")


# Créer l'application
settings = get_settings()
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "ETF", "description": "Données des ETF (prix, features)"},
        {"name": "Macro", "description": "Indicateurs macro-économiques"},
        {"name": "Analysis", "description": "Analyses (corrélations, statistiques)"},
        {"name": "ML", "description": "Modèles ML (régime, portfolio)"},
        {"name": "Health", "description": "Statut de l'API"},
    ],
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middleware pour CORS sur les erreurs (doit etre avant CORSMiddleware)
app.add_middleware(CORSErrorMiddleware)

# CORS (API publique en lecture seule - pas de credentials)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "HEAD", "OPTIONS"],  # API read-only + HEAD pour monitoring
    allow_headers=["*"],
)

# Inclure les routers
app.include_router(etf.router, prefix="/api/v1")
app.include_router(macro.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(ml.router, prefix="/api/v1")


# Endpoints racine
@app.get("/", include_in_schema=False)
def root():
    """Redirige vers la documentation."""
    return RedirectResponse(url="/docs")


@app.api_route(
    "/health",
    methods=["GET", "HEAD"],
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check",
    description="Vérifie que l'API et la base de données fonctionnent. Supporte GET et HEAD.",
)
@limiter.limit("30/minute")
def health_check(request: Request) -> HealthResponse:
    """Health check endpoint (GET et HEAD pour monitoring UptimeRobot)."""
    db_status = "ok" if check_db_connection() else "error"
    return HealthResponse(
        status="ok",
        database=db_status,
        version=settings.api_version,
    )


# Pour debug/dev
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
