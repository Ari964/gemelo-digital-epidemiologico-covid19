import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_weekly_evaluation_endpoint_contract():
    """Verifica que /api/v1/validation/weekly-evaluation sirva los resultados serializados por scripts/train_and_evaluate_models.py"""
    response = client.get("/api/v1/validation/weekly-evaluation")
    assert response.status_code == 200
    data = response.json()
    
    # 1. Metadatos generales
    assert "generated_at" in data
    assert "temporal_protocol" in data
    assert "Sunday" in data["temporal_protocol"]["canonical_frequency"]
    assert "TimeSeriesSplit" in data["temporal_protocol"]["cv_method"]
    
    # 2. Modelos evaluados
    assert "models" in data
    models = data["models"]
    assert "Baseline_Naive_Persistence" in models
    assert "Candidate_Random_Forest" in models
    assert "Baseline_Ridge_Regression" in models
    assert "Candidate_HistGradientBoosting" in models
    
    # Campeón verificado
    naive = models["Baseline_Naive_Persistence"]
    assert naive["role"] == "PREDICTIVE_CHAMPION"
    assert "mae" in naive["test_metrics"]
    assert len(naive["fold_metrics"]) == 5
    
    # Random Forest con 5 pliegues registrados
    rf = models["Candidate_Random_Forest"]
    assert len(rf["fold_metrics"]) == 5
    assert "best_params" in rf
    
    # 3. Pruebas bioestadísticas
    assert "statistical_tests" in data
    tests = data["statistical_tests"]
    assert "wilcoxon_paired" in tests
    assert "diebold_mariano_hln" in tests
    assert "shapiro_wilk" in tests
    assert "kolmogorov_smirnov" in tests
    
    # Wilcoxon y Diebold-Mariano con p-value significativo
    assert tests["wilcoxon_paired"]["p_value_two_sided"] < 0.001
    assert tests["diebold_mariano_hln"]["statistic_dm_hln"] < 0
    
    # 4. Deslinde formal de SEIR/ABM (no evaluado para pronóstico puntual semanal)
    assert "untested_comparisons" in data
    assert "seir_abm_vs_statistical_weekly" in data["untested_comparisons"]
    seir_disclaimer = data["untested_comparisons"]["seir_abm_vs_statistical_weekly"]
    assert seir_disclaimer["status"] == "NOT_EVALUATED_IN_WEEKLY_SERIES"
    
    # 5. Puntos de la serie de prueba (71 semanas)
    assert "test_series_data" in data
    assert len(data["test_series_data"]) == 71

def test_langflow_status_endpoint():
    """Verifica que /api/v1/langflow/status inspeccione el contenedor Docker sin fallos 500"""
    response = client.get("/api/v1/langflow/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "connected" in data
    assert "url" in data
    assert "flow_id" in data
    assert data["flow_id"] == "906a3d58-bcf0-48a9-9364-4a62ea230945"

def test_langflow_query_endpoint_live_or_handled():
    """Verifica que /api/v1/langflow/query procese la consulta o retorne un error HTTP controlado sin romper FastAPI"""
    payload = {
        "query": "¿Cuál es el modelo campeón para la vigilancia semanal de Kenia?",
        "session_id": "test-session-pytest"
    }
    response = client.post("/api/v1/langflow/query", json=payload)
    # Si Docker está arriba responderá 200; si el contenedor estuviera apagado devolvería 503
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        data = response.json()
        assert "reply" in data
        assert "flow_name" in data
        assert "execution_time_ms" in data
