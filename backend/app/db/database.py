"""Database connection and session management."""

import os
from typing import Generator
from sqlalchemy.orm import Session


# Lazily initialized on first use
_engine = None
_SessionLocal = None


def _get_engine():
    """Create engine on first access to avoid heavy initialization at import time."""
    global _engine
    if _engine is not None:
        return _engine
    
    from sqlalchemy import create_engine
    
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./candidate_screening.db")
    
    if "sqlite" in DATABASE_URL:
        _engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
    else:
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    
    return _engine


def _get_session_factory():
    """Get or create session factory lazily."""
    global _SessionLocal
    if _SessionLocal is not None:
        return _SessionLocal
    
    from sqlalchemy.orm import sessionmaker
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_get_engine())
    
    return _SessionLocal


def init_db():
    """Initialize database tables."""
    from .models import Base
    Base.metadata.create_all(bind=_get_engine())


def get_db() -> Generator[Session, None, None]:
    """Get database session dependency for FastAPI."""
    SessionLocal = _get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()