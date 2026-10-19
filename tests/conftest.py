import os
import sys
import tempfile
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config

# Ensure root directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.main import app
from backend.app.db.session import get_db, Base
import backend.app.db.session as session_module
from backend.app.core.config import settings
from backend.app.scripts.seed_verified_data import seed_data


@pytest.fixture(scope="session")
def test_env_setup(tmp_path_factory):
    """
    Fixture de sesión que crea un entorno de prueba 100% aislado:
    1. Base de datos SQLite temporal migrada vía Alembic (001 -> 004).
    2. Datos iniciales sembrados (usuarios RBAC, 47 condados, datasets de linaje).
    3. Directorio de modelos (MODELS_DIR) temporal para no polucionar el entorno real.
    """
    # 1. Directorio y DB temporal
    temp_dir = tmp_path_factory.mktemp("isolated_test_env")
    temp_db_path = temp_dir / "isolated_test.db"
    temp_db_url = f"sqlite:///{temp_db_path.as_posix()}"

    # 2. Configurar variables de entorno y settings
    os.environ["DATABASE_URL"] = temp_db_url
    settings.DATABASE_URL = temp_db_url

    temp_models_dir = temp_dir / "models"
    temp_models_dir.mkdir(parents=True, exist_ok=True)
    settings.MODELS_DIR = str(temp_models_dir)

    # 3. Ejecutar migraciones Alembic reales
    alembic_ini_path = ROOT_DIR / "backend" / "alembic.ini"
    cfg = Config(str(alembic_ini_path))
    cfg.set_main_option("script_location", str(ROOT_DIR / "backend" / "alembic"))
    command.upgrade(cfg, "head")

    # 4. Configurar engine y SessionLocal global en backend.app.db.session
    test_engine = create_engine(temp_db_url, connect_args={"check_same_thread": False})
    test_session_factory = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    original_engine = session_module.engine
    original_session_local = session_module.SessionLocal

    session_module.engine = test_engine
    session_module.SessionLocal = test_session_factory

    # 5. Sembrar datos verificados requeridos por las pruebas
    seed_data()

    yield {
        "db_url": temp_db_url,
        "engine": test_engine,
        "session_factory": test_session_factory,
        "models_dir": str(temp_models_dir)
    }

    # Restaurar entorno
    session_module.engine = original_engine
    session_module.SessionLocal = original_session_local


@pytest.fixture
def db(test_env_setup):
    """Proporciona una sesión de base de datos aislada para cada prueba."""
    session = test_env_setup["session_factory"]()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(test_env_setup):
    """Proporciona un TestClient de FastAPI conectado a la base de datos temporal aislada."""
    session_factory = test_env_setup["session_factory"]

    def override_get_db():
        db_s = session_factory()
        try:
            yield db_s
        finally:
            db_s.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def auth_headers(client):
    """Encabezados con token JWT de Administrador oficial."""
    res = client.post("/api/v1/auth/login", json={"email": "admin@epidemic-twin.ke", "password": "AdminSecure2026!"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def epi_auth_headers(client):
    """Encabezados con token JWT de Epidemiólogo oficial."""
    res = client.post("/api/v1/auth/login", json={"email": "dr.wanjiku@health.go.ke", "password": "EpiChief2026!"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
