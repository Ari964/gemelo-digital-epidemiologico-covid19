import pytest
import time
from backend.app.analytics.sobol_sensitivity import SobolSensitivityAnalyzer

def test_sobol_sensitivity_analyzer_execution():
    """
    Prueba que el analizador de Sobol ejecute la descomposición de Saltelli
    sobre el modelo SEIR clásico de referencia sin inventar intervalos del 5%.
    """
    analysis_id = SobolSensitivityAnalyzer.start_analysis_task(
        samples_n=64,
        target_metric="peak_infections",
        seed=42
    )
    assert analysis_id.startswith("sobol-")

    # Esperar finalización del hilo de fondo
    max_wait = 15
    start = time.time()
    task = None
    while time.time() - start < max_wait:
        task = SobolSensitivityAnalyzer.get_analysis_status(analysis_id)
        if task and task["status"] in ["COMPLETED", "FAILED"]:
            break
        time.sleep(0.5)

    assert task is not None
    assert task["status"] == "COMPLETED"
    assert task["total_evaluations"] > 0
    assert "SEIR" in task["model_analyzed"]
    assert task["most_sensitive_parameter"] is not None

    indices = task["indices"]
    assert len(indices) == 5  # 5 variables biológicas
    for idx in indices:
        assert "S1" in idx
        assert "ST" in idx
        assert idx["ST"] >= -0.10  # Índices acotados
        assert idx["S1"] <= 1.10

def test_sobol_async_queue_and_status():
    analysis_id = SobolSensitivityAnalyzer.start_analysis_task(samples_n=64, seed=123)
    status_resp = SobolSensitivityAnalyzer.get_analysis_status(analysis_id)

    assert status_resp["analysis_id"].startswith("sobol-")
    assert status_resp["status"] in ["PENDING", "RUNNING", "COMPLETED"]
    assert "SEIR" in status_resp["model_analyzed"]
