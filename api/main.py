"""
Point d'entrée de l'API DeepPilot.

Lance avec: uvicorn api.main:app --reload
Docs: http://localhost:8000/docs
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from api.config import get_settings
from api.database import check_db_connection
from api.models.analysis import HealthResponse
from api.routers import analysis, etf, macro


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
        {"name": "Health", "description": "Statut de l'API"},
    ],
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET"],  # API read-only
    allow_headers=["*"],
)

# Inclure les routers
app.include_router(etf.router, prefix="/api/v1")
app.include_router(macro.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")


# Endpoints racine
@app.get("/", include_in_schema=False)
def root():
    """Redirige vers la documentation."""
    return RedirectResponse(url="/docs")


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check",
    description="Vérifie que l'API et la base de données fonctionnent.",
)
@limiter.limit("10/minute")
def health_check(request: Request) -> HealthResponse:
    """Health check endpoint."""
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
