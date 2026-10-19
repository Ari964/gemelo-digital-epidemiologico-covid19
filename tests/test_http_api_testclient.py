import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.schemas.report import ExportReportByIdRequest

client = TestClient(app)

def test_root_endpoint():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["system"] == "Population-Level Digital Twin for Pandemic Preparedness"
    assert data["jurisdiction"] == "Kenya (47 Counties)"

def test_auth_unauthorized_endpoints():
    # Intento de acceso sin token JWT
    resp = client.get("/api/v1/users/me")
    assert resp.status_code == 401

    resp = client.get("/api/v1/monitoring/status")
    assert resp.status_code == 401

def test_login_flow():
    resp = client.post("/api/v1/auth/login", json={
        "email": "admin@epidemic-twin.ke",
        "password": "AdminSecure2026!"
    })
    assert resp.status_code == 200
    token_data = resp.json()
    assert "access_token" in token_data
    assert token_data["role"] == "admin"

def test_pydantic_forbid_extra_on_technical_approval():
    # Login as admin
    login_res = client.post("/api/v1/auth/login", json={
        "email": "admin@epidemic-twin.ke",
        "password": "AdminSecure2026!"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Intento de enviar métricas manuales prohibidas (extra='forbid')
    bad_payload = {
        "evaluation_id": "eval-12345",
        "notes": "Intento fraudulento",
        "r2_fit": 0.99,  # Campo prohibido
        "mape": 2.1      # Campo prohibido
    }
    resp = client.post("/api/v1/validation/technical-approval", json=bad_payload, headers=headers)
    # Debe ser rechazado con 422 Unprocessable Entity
    assert resp.status_code == 422

def test_operational_simulation_without_active_model_returns_409():
    from backend.app.db.session import SessionLocal
    from backend.app.models.monitoring import ActiveModelDeploymentDB
    
    # Asegurar que no haya modelo activo desplegado
    db = SessionLocal()
    db.query(ActiveModelDeploymentDB).delete()
    db.commit()
    db.close()

    login_res = client.post("/api/v1/auth/login", json={
        "email": "admin@epidemic-twin.ke",
        "password": "AdminSecure2026!"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Solicitar simulación OPERATIONAL
    sim_payload = {
        "days": 60,
        "npi_stringency": 0.3,
        "vaccine_coverage": 0.2,
        "run_mode": "OPERATIONAL"
    }
    resp = client.post("/api/v1/simulations/run", json=sim_payload, headers=headers)
    # Al no haber modelo activo desplegado, DEBE retornar estrictamente 409 Conflict
    assert resp.status_code == 409
    assert "NO_ACTIVE_MODEL_DEPLOYED" in resp.json()["detail"]

def test_export_by_id_exactly_one_contract():
    # 1. Ni simulation_id ni evaluation_id -> Rechazado por Pydantic
    with pytest.raises(ValueError):
        ExportReportByIdRequest()

    # 2. Ambos provistos -> Rechazado por Pydantic
    with pytest.raises(ValueError):
        ExportReportByIdRequest(simulation_id="sim-001", evaluation_id="eval-001")

    # 3. Solo simulation_id -> Válido
    req = ExportReportByIdRequest(simulation_id="sim-001")
    assert req.simulation_id == "sim-001"
    assert req.evaluation_id is None
