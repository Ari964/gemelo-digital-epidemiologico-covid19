"""
Pruebas automatizadas de regresión para el endpoint de integración con LangChain.
Verifica:
1. Respuesta HTTP 200.
2. Ejecución real de herramientas StructuredTool de LangChain.
3. Separación estricta de observaciones, pronósticos y texto generado.
4. Presencia de metadatos de LangChain (componentes, herramientas y framework).
"""

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_langchain_agent_query():
    payload = {
        "query": "¿Cuál es la proyección de vigilancia y la capacidad hospitalaria para el corte dominical?",
        "cutoff_date": "2024-07-28",
        "county_code": 0
    }
    response = client.post("/api/v1/langchain-agent/query", json=payload)
    assert response.status_code == 200, f"Error en endpoint LangChain: {response.text}"
    
    data = response.json()
    assert "database_observations" in data
    assert "model_forecasts" in data
    assert "generated_text" in data
    assert "langchain_metadata" in data
    
    # Verificar observaciones (en t0 = 2024-07-28, casos observados reales = 0.0)
    obs = data["database_observations"]
    assert obs["date"] == "2024-07-28"
    assert "observed_weekly_cases" in obs
    assert obs["observed_weekly_cases"] == 0.0
    
    # Verificar pronósticos (persistencia desde t0=0.0 predice 0.0 para 2024-08-04)
    forecasts = data["model_forecasts"]
    assert forecasts["primary_model"] == "Baseline_Naive_Persistence"
    assert forecasts["persistence_prediction_cases"] == 0.0
    assert forecasts["random_forest_sensitivity_cases"] == 70.76
    
    # Verificar componentes LangChain
    metadata = data["langchain_metadata"]
    assert "LangChain" in metadata["framework"]
    assert len(metadata["components_executed"]) >= 4
    assert any("StructuredTool" in c for c in metadata["components_executed"])
    assert any("ChatPromptTemplate" in c for c in metadata["components_executed"])
    assert len(metadata["tools_invoked"]) == 3
    valid_modes = [
        "LLM_LOCAL_OLLAMA (Generativo Trazable)",
        "RUNNABLE_LAMBDA_LOCAL (Determinista Acotado)",
        "LLM_EXTERNO (Generativo)"
    ]
    assert metadata["execution_mode"] in valid_modes


def test_langchain_agent_kiambu_validation_query():
    payload = {
        "query": "¿Cuál es la proyección de vigilancia y la infraestructura hospitalaria de Kiambu para el corte de diciembre 2022?",
        "cutoff_date": "2022-12-18",
        "county_code": 22
    }
    response = client.post("/api/v1/langchain-agent/query", json=payload)
    assert response.status_code == 200, f"Error en endpoint LangChain: {response.text}"
    
    data = response.json()
    assert data["cutoff_date"] == "2022-12-18"
    # En corte 2022-12-18, casos observados en t0 son 183.0 (y no 288.0, que era weekly_lag_1 en el CSV)
    assert data["database_observations"]["observed_weekly_cases"] == 183.0
    assert data["model_forecasts"]["persistence_prediction_cases"] == 183.0
    assert data["model_forecasts"]["random_forest_sensitivity_cases"] == 276.28
    assert data["hospital_capacity"]["county_name"] == "Kiambu"
    assert data["hospital_capacity"]["icu_beds"] == 16
    assert data["langchain_metadata"]["execution_mode"] in [
        "LLM_LOCAL_OLLAMA (Generativo Trazable)",
        "RUNNABLE_LAMBDA_LOCAL (Determinista Acotado)",
        "LLM_EXTERNO (Generativo)"
    ]

