from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Generator
import logging

from backend.app.core.config import settings

logger = logging.getLogger("agentfleet.database")

DATABASE_URL = settings.DATABASE_URL

# Safe fallback for database engine configuration
if not DATABASE_URL:
    logger.warning("DATABASE_URL is not set. Falling back to local SQLite database.")
    DATABASE_URL = "sqlite:///./agentfleet.db"

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Supabase Client Initialization
supabase = None
if settings.SUPABASE_URL and settings.SUPABASE_KEY:
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("Supabase client successfully initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
else:
    logger.warning("Supabase URL or Key not set. Supabase client will be unavailable.")

def get_db() -> Generator:
    """
    FastAPI dependency to yield a database session.
    Guarantees the session is closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
