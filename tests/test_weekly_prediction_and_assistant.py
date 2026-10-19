"""
Pruebas Automatizadas de Predicción Semanal y Asistente de Datos (Fase 2).

Verifica:
1. Modelo campeón Baseline_Naive_Persistence como predicción principal.
2. Random Forest como exploración hipotética de sensibilidad.
3. Integridad temporal sin desfase (weekly_lag_1 es exactamente el valor de corte t_0).
4. Dinamismo en diferentes cortes históricos (2024-07-28 de referencia y 2024-07-21 alternativo).
5. Asistente de datos con tripartición estricta (observaciones, pronósticos, IA) sin traza de pensamiento.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_get_historical_cutoffs():
    response = client.get("/api/v1/predictions/historical-cutoffs")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] > 0
    assert len(data["available_cutoffs"]) > 0
    
    # Verificar caso de referencia 2024-07-28 (t0=2024-07-28 obs=0, t1=2024-08-04 obs=0)
    ref = data["recommended_test_case"]
    assert ref["cutoff_date"] == "2024-07-28"
    assert ref["naive_persistence_prediction"] == 0.0
    assert ref["random_forest_prediction"] == 70.76
    assert ref["next_week_observed"] == 0.0


def test_weekly_prediction_reference_case_2024_07_28():
    response = client.post(
        "/api/v1/predictions/weekly",
        json={"cutoff_date": "2024-07-28", "county_code": 0}
    )
    assert response.status_code == 200
    data = response.json()
    
    # 1. Modelo principal es la persistencia (t0=0.0 -> predice 0.0)
    assert data["primary_model_name"] == "Baseline_Naive_Persistence"
    assert data["primary_forecast_cases"] == 0.0
    assert data["target_week"] == "2024-08-04"
    assert data["target_observed_actual"] == 0.0
    assert data["forecast_error_mae"] == 0.0
    
    # 2. Random Forest es sensibilidad hipotética
    assert round(data["hypothetical_rf_prediction"], 2) == 70.76
    assert "No causal" in data["sensitivity_disclaimer"] or "no debe interpretarse" in data["sensitivity_disclaimer"]
    
    # 3. Verificación de retardo temporal (weekly_lag_1 = 0.0 en fila 2024-08-04 correspondiente a t0 2024-07-28)
    details = data["validation_details"]
    assert details["weekly_lag_1_used"] == 0.0
    assert details["horizon_days"] == 7
    assert details["date_alignment_verified"] is True
    assert details["imputed_stringency_index"] == 22.77
    assert details["imputed_reproduction_rate"] == 0.54


def test_weekly_prediction_alternative_cutoff_2024_07_21():
    """
    Prueba que el sistema genere dinámicamente la predicción para 2024-07-21.
    En t0 = 2024-07-21, casos observados = 1.0.
    Semana objetivo t1 = 2024-07-28, casos observados = 0.0.
    Persistencia = 1.0, Error MAE = 1.0.
    """
    response = client.post(
        "/api/v1/predictions/weekly",
        json={"cutoff_date": "2024-07-21", "county_code": 0}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["cutoff_date"] == "2024-07-21"
    assert data["target_week"] == "2024-07-28"
    assert data["primary_model_name"] == "Baseline_Naive_Persistence"
    
    # weekly_lag_1 de t1 coincide con los casos conocidos en t0 (1.0)
    details = data["validation_details"]
    assert details["date_alignment_verified"] is True
    assert data["primary_forecast_cases"] == details["weekly_lag_1_used"]
    assert data["primary_forecast_cases"] == 1.0
    # El valor observado en target_week (2024-07-28) es 0.0
    assert data["target_observed_actual"] == 0.0
    assert data["forecast_error_mae"] == 1.0


def test_data_assistant_structured_response():
    response = client.post(
        "/api/v1/data-assistant/query",
        json={
            "query": "¿Cuál es la predicción para el corte de julio 2024 y qué datos empíricos la respaldan?",
            "cutoff_date": "2024-07-28",
            "county_code": 0
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    # 1. Distinción estricta de componentes
    assert "database_observations" in data
    assert "model_forecasts" in data
    assert "ai_interpretation" in data
    assert "tools_used" in data
    assert "sources_consulted" in data
    
    # 2. NO contiene traza de pensamiento
    assert "thought_trace" not in data
    assert "chain_of_thought" not in data
    
    # 3. Observaciones empíricas: en corte 2024-07-28, casos observados son 0.0
    obs = data["database_observations"]
    assert obs["total_counties_registered"] == 47
    assert obs["total_historical_records"] > 0
    assert "cutoff_observation" in obs
    assert obs["cutoff_observation"]["weekly_cases"] == 0.0
    
    # 4. Pronósticos del modelo: persistencia desde t0=0.0 da 0.0
    forecasts = data["model_forecasts"]
    assert forecasts["cutoff_date"] == "2024-07-28"
    assert forecasts["target_week_predicted"] == "2024-08-04"
    assert forecasts["main_forecast_persistence"]["predicted_weekly_cases"] == 0.0
    assert round(forecasts["hypothetical_sensitivity_rf"]["predicted_cases"], 2) == 70.76
    
    # 5. Herramientas y fuentes reportadas
    assert any("sql" in t.lower() or "db" in t.lower() or "csv" in t.lower() for t in data["tools_used"])
    assert any("Baseline_Naive_Persistence" in s or "persistencia" in s.lower() for s in data["sources_consulted"])

