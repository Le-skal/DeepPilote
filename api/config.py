"""
Configuration de l'API via Pydantic Settings.

Charge les variables d'environnement depuis .env
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration de l'API DeepPilot."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore les variables d'env non définies dans la classe
    )

    # API
    api_title: str = "DeepPilot API"
    api_description: str = "API REST pour les données ETF et indicateurs macro"
    api_version: str = "1.0.0"
    debug: bool = False

    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_db_url: str

    # CORS - origines autorisées (API publique en lecture seule)
    cors_origins: list[str] = ["*"]

    # Rate limiting
    rate_limit: str = "100/minute"  # 100 requêtes par minute

    # Sentry (monitoring erreurs) - optionnel
    sentry_dsn: str | None = None
    sentry_environment: str = "production"


@lru_cache
def get_settings() -> Settings:
    """
    Retourne les settings (cached).

    Returns:
        Instance Settings avec les valeurs de .env
    """
    return Settings()
