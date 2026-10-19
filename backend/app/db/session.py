import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.core.config import settings

db_url = settings.DATABASE_URL

def create_active_engine(url: str):
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    else:
        try:
            # Test actual connection to postgres
            eng = create_engine(url, pool_pre_ping=True)
            with eng.connect() as conn:
                pass
            return eng
        except Exception as e:
            is_production = settings.ENVIRONMENT == "production"
            allow_fallback = os.getenv("ALLOW_SQLITE_FALLBACK", "false" if is_production else "true").lower() == "true"
            
            if is_production or not allow_fallback:
                raise RuntimeError(
                    f"CRITICAL: No se pudo conectar a la base de datos PostgreSQL en entorno '{settings.ENVIRONMENT}': {e}. "
                    "La sustitución silenciosa por SQLite está terminantemente prohibida en producción."
                ) from e
            
            # Entorno no productivo con fallback explícitamente permitido
            print(f"[DB Session] AVISO: PostgreSQL no alcanzable ({e}). Utilizando SQLite para desarrollo/pruebas locales.")
            fallback_url = "sqlite:///./epidemic_twin.db"
            return create_engine(fallback_url, connect_args={"check_same_thread": False})

engine = create_active_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
