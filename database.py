import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from config import Config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Database")

Base = declarative_base()

ACTIVE_DB_TYPE = "unknown"
ACTIVE_DB_URL = ""
engine = None
SessionLocal = None

def get_engine():
    global ACTIVE_DB_TYPE, ACTIVE_DB_URL, engine, SessionLocal
    
    postgres_url = Config.DATABASE_URL
    try:
        # Test connecting to PostgreSQL
        test_engine = create_engine(postgres_url, pool_pre_ping=True, connect_args={"connect_timeout": 3})
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"Successfully connected to PostgreSQL at {Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}")
        ACTIVE_DB_TYPE = "PostgreSQL"
        ACTIVE_DB_URL = postgres_url
        engine = test_engine
    except Exception as e:
        logger.warning(
            f"PostgreSQL connection to '{postgres_url}' failed: {e}\n"
            f"-> Switching to fallback SQLite database at: {Config.SQLITE_FALLBACK_URL}\n"
            f"-> To use PostgreSQL, ensure PostgreSQL service is running and configure credentials in backend/.env"
        )
        sqlite_engine = create_engine(
            Config.SQLITE_FALLBACK_URL,
            connect_args={"check_same_thread": False}
        )
        ACTIVE_DB_TYPE = "SQLite (Fallback - Start PostgreSQL to switch)"
        ACTIVE_DB_URL = Config.SQLITE_FALLBACK_URL
        engine = sqlite_engine

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal

engine, SessionLocal = get_engine()

def get_db_session():
    """Context manager or session provider for DB operations."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def get_db():
    return SessionLocal()
