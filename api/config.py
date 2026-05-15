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

    # CORS - origines autorisées
    cors_origins: list[str] = [
        "http://localhost:3000",  # Next.js dev
        "http://localhost:8000",  # FastAPI docs
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    # Rate limiting
    rate_limit: str = "100/minute"  # 100 requêtes par minute


@lru_cache
def get_settings() -> Settings:
    """
    Retourne les settings (cached).

    Returns:
        Instance Settings avec les valeurs de .env
    """
    return Settings()
