from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Generator
import logging

from backend.app.core.config import settings

logger = logging.getLogger("agentfleet.database")

DB_URL = settings.SUPABASE_DB_URL

# Fallback database URL to prevent crashes during configuration stages
if not DB_URL:
    logger.warning("SUPABASE_DB_URL is not set. Falling back to local SQLite database.")
    DB_URL = "sqlite:///./agentfleet.db"

# Configure connection pooling rules for production-readiness
engine_kwargs = {}
if DB_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update({
        "pool_size": 5,          # Maintain up to 5 connections
        "max_overflow": 10,      # Allow up to 10 overflow connections
        "pool_recycle": 3600,    # Recycle connections after an hour
        "pool_pre_ping": True    # Verify connection health prior to executing checkout queries
    })

try:
    engine = create_engine(DB_URL, **engine_kwargs)
    
    # Listen for SQLite connection events to register PostgreSQL compatibility functions
    if DB_URL.startswith("sqlite"):
        from sqlalchemy import event
        import uuid
        from datetime import datetime
        
        @event.listens_for(engine, "connect")
        def register_sqlite_udfs(dbapi_connection, connection_record):
            dbapi_connection.create_function("gen_random_uuid", 0, lambda: str(uuid.uuid4()))
            dbapi_connection.create_function("now", 0, lambda: datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
            
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    logger.info("Database engine and session factory created successfully.")
except Exception as e:
    logger.critical(f"Failed to create database engine: {e}")
    raise e

# Supabase API Client initialization
supabase_client = None
if settings.SUPABASE_URL and settings.SUPABASE_KEY:
    try:
        from supabase import create_client, Client
        supabase_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("Supabase API SDK Client successfully initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase SDK Client: {e}")
else:
    logger.warning("Supabase credentials not set. Supabase SDK features will be unavailable.")

def get_db() -> Generator:
    """
    FastAPI dependency yielding a thread-safe database session.
    Automatically closes session after request lifecycle ends.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        try:
            db.close()
        except Exception as close_err:
            logger.warning(f"Error closing database session: {close_err}")

def get_supabase_client():
    """
    Returns the initialized Supabase Python SDK client.
    Raises RuntimeError if the client was not configured.
    """
    if supabase_client is None:
        raise RuntimeError("Supabase client is not configured. Check SUPABASE_URL and SUPABASE_KEY.")
    return supabase_client

def health_check() -> bool:
    """
    Executes a SELECT 1 query to confirm active database connection.
    Returns True if connection is operational.
    Raises Exception if connection fails.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection health check failed: {e}")
        raise e
