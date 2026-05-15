"""
Connexion à la base de données Supabase/PostgreSQL.

Utilise SQLAlchemy pour les requêtes et un pool de connexions.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from api.config import get_settings


def get_engine() -> Engine:
    """
    Crée le moteur SQLAlchemy avec pool de connexions.

    Returns:
        Engine SQLAlchemy configuré pour Supabase
    """
    settings = get_settings()

    # Pool de connexions : 5 connexions par défaut, max 10
    engine = create_engine(
        settings.supabase_db_url,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,  # Recycle les connexions après 30 min
        echo=settings.debug,  # Log SQL si debug=True
    )

    return engine


# Session factory
_engine = None
_SessionLocal = None


def get_session_factory() -> sessionmaker:
    """
    Retourne la factory de sessions (lazy init).

    Returns:
        sessionmaker configuré
    """
    global _engine, _SessionLocal

    if _SessionLocal is None:
        _engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency FastAPI pour obtenir une session DB.

    Yields:
        Session SQLAlchemy

    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    session_factory = get_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager pour les scripts (hors FastAPI).

    Yields:
        Session SQLAlchemy

    Usage:
        with get_db_context() as db:
            db.execute(...)
    """
    session_factory = get_session_factory()
    db = session_factory()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def check_db_connection() -> bool:
    """
    Vérifie que la connexion à la DB fonctionne.

    Returns:
        True si la connexion est OK, False sinon
    """
    try:
        with get_db_context() as db:
            db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
