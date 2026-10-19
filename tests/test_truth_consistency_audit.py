import json
import os
import re
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def test_truth_consistency_descriptor_vs_evaluation_json():
    """Compara automáticamente descriptor de persistencia y el JSON de evaluación semanal (fuente de verdad)."""
    eval_path = os.path.join(BASE_DIR, "models", "model_evaluation_weekly_results.json")
    desc_path = os.path.join(BASE_DIR, "models", "official_naive_persistence_v1.0.json")

    assert os.path.exists(eval_path), f"Falta {eval_path}"
    assert os.path.exists(desc_path), f"Falta {desc_path}"

    with open(eval_path, "r", encoding="utf-8") as f:
        eval_data = json.load(f)

    with open(desc_path, "r", encoding="utf-8") as f:
        desc_data = json.load(f)

    naive_eval = eval_data["models"]["Baseline_Naive_Persistence"]
    desc_perf = desc_data["test_performance"]
    desc_proto = desc_data["selection_protocol"]

    # Coincidencia matemática exacta sin sustitución de números
    assert desc_perf["test_rmse"] == naive_eval["test_metrics"]["rmse"], "RMSE de test no coincide"
    assert desc_perf["test_mae"] == naive_eval["test_metrics"]["mae"], "MAE de test no coincide"
    assert desc_perf["test_mape"] == naive_eval["test_metrics"]["mape"], "MAPE de test no coincide"
    assert desc_proto["dev_cv_rmse"] == naive_eval["cv_rmse_5fold"], "CV RMSE en dev no coincide"

    # Verificar que el MAPE de test es 515.49 y MAE es 19.23
    assert desc_perf["test_mae"] == 19.23
    assert desc_perf["test_mape"] == 515.49
    assert desc_perf["test_rmse"] == 55.64


def test_walkthrough_documentation_metrics_truth():
    """Verifica que docs/walkthrough.md contiene las cifras exactas y ninguna cifra desactualizada."""
    doc_path = os.path.join(BASE_DIR, "docs", "walkthrough.md")
    assert os.path.exists(doc_path)

    with open(doc_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Cifras exactas obligatorias
    assert "19.23" in content, "Falta MAE 19.23 en walkthrough.md"
    assert "55.64" in content, "Falta RMSE 55.64 en walkthrough.md"
    assert "515.49" in content, "Falta MAPE 515.49 en walkthrough.md"
    assert "1,183.64" in content, "Falta CV RMSE 1,183.64 en walkthrough.md"
    assert "145.0" in content, "Falta estadístico Wilcoxon W=145.0 en walkthrough.md"
    assert "-14.324" in content, "Falta estadístico Diebold-Mariano DM*=-14.324 en walkthrough.md"

    # Cifras antiguas prohibidas
    assert "28.53%" not in content, "Cifra antigua '28.53%' no eliminada de walkthrough.md"
    assert "MAE: 11.75" not in content, "Cifra antigua 'MAE: 11.75' no eliminada de walkthrough.md"
    assert "W = 100.0" not in content, "Estadístico antiguo 'W = 100.0' no corregido a 145.0"


def test_validation_api_endpoint_matches_evaluation_json():
    """Verifica que el endpoint GET /api/v1/validation/weekly-evaluation sirve las métricas sin alteración."""
    client = TestClient(app)
    res = client.get("/api/v1/validation/weekly-evaluation")
    assert res.status_code == 200
    data = res.json()

    eval_path = os.path.join(BASE_DIR, "models", "model_evaluation_weekly_results.json")
    with open(eval_path, "r", encoding="utf-8") as f:
        expected = json.load(f)

    assert data["raw_data_sha256"] == expected["raw_data_sha256"]
    assert data["models"]["Baseline_Naive_Persistence"]["test_metrics"] == expected["models"]["Baseline_Naive_Persistence"]["test_metrics"]
    assert data["models"]["Candidate_Random_Forest"]["test_metrics"] == expected["models"]["Candidate_Random_Forest"]["test_metrics"]


def test_reports_prediction_identifies_both_descriptor_and_joblib():
    """Verifica que el reporte de predicción identifica por separado el descriptor oficial y el joblib de sensibilidad."""
    client = TestClient(app)
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@epidemic-twin.ke", "password": "AdminSecure2026!"}
    )
    assert login_res.status_code == 200, f"Login falló: {login_res.text}"
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(
        "/api/v1/reports/preview",
        json={"report_type": "prediction", "cutoff_date": "2024-07-28", "lang": "es"},
        headers=headers
    )
    assert res.status_code == 200
    data = res.json()

    summary_labels_values = {m["label"]: m["value"] for m in data["summary_metrics"]}
    
    # Debe existir el descriptor del modelo oficial
    assert any("Descriptor" in k and "models/official_naive_persistence_v1.0.json" in str(v) for k, v in summary_labels_values.items()), \
        "No se identificó models/official_naive_persistence_v1.0.json en summary_metrics"

    # Debe existir el archivo joblib de Random Forest para sensibilidad
    assert any("champion_covid_model_v1.0.joblib" in str(v) for k, v in summary_labels_values.items()), \
        "No se identificó models/champion_covid_model_v1.0.joblib en summary_metrics"


def test_langchain_agent_tools_no_numeric_fallback_on_empty_db():
    """Verifica que tool_query_hospital_capacity no usa fallback de 47564296 cuando no hay población."""
    from backend.app.api.v1.endpoints.langchain_agent import tool_query_hospital_capacity
    from unittest.mock import patch, MagicMock

    mock_db = MagicMock()
    mock_db.query.return_value.scalar.return_value = None

    with patch("backend.app.db.session.SessionLocal", return_value=mock_db):
        res = tool_query_hospital_capacity.invoke({"county_code": 0})
        # Debe retornar ausencia explícita sin 47564296
        assert res.get("total_population_2019") is None
        assert res.get("verification_status") == "DATO_AUSENTE_BD"


def test_langchain_agent_unifies_default_ollama_model():
    """Verifica que el modelo predeterminado de Ollama en langchain_agent.py es qwen2.5:0.5b."""
    import inspect
    from backend.app.api.v1.endpoints import langchain_agent

    source = inspect.getsource(langchain_agent)
    assert 'os.getenv("OLLAMA_MODEL") or "qwen2.5:0.5b"' in source
    assert 'llama3.2:3b' not in source
