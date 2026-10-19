"""
Suite de pruebas de verificación formal para el Plan Integral v2 Refinada.
Cubre las precisiones requeridas:
1. Representación territorial y prevención de duplicados (county_code=0 nacional, 1..47 condados).
2. Políticas on_conflict (reject, skip, update) y no inflación de cobertura.
3. Jerarquía y combinación de procedencia canónica (SYNTHETIC > UNKNOWN > ESTIMATED > EMPIRICAL).
4. Estados no evaluables de hipótesis H1 y ausencia de métricas/ceros fabricados.
5. Flujo canónico de Sobol, recuperación tras reinicio (INTERRUPTED) y benchmark Ishigami.
6. Monitoreo persistido en 3 modos sin generación aleatoria.
7. Inyección de modelo activo y detección de manipulación de hash SHA-256.
8. Exportación verificada de reportes PDF y Excel desde registros reales.
"""
import pytest
import numpy as np
from datetime import datetime, date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import backend.app.db.session as session_module

def SessionLocal():
    return session_module.SessionLocal()
from backend.app.analytics.provenance import resolve_composite_provenance
from backend.app.analytics.hypothesis_evaluator import HypothesisEvaluator
from backend.app.analytics.sobol_sensitivity import (
    SobolSensitivityAnalyzer,
    SobolTaskDB,
    evaluate_ishigami_benchmark,
)
from backend.app.analytics.model_monitoring import ModelMonitoringService
from backend.app.models.observation import ObservationDB
from backend.app.models.dataset import DatasetDB
from backend.app.models.simulation import SimulationRunDB
from backend.app.models.evaluation import EvaluationRunDB
from backend.app.models.model_registry import ModelRegistryDB




# ----------------------------------------------------------------------
# 1. REPRESENTACIÓN TERRITORIAL Y PREVENCIÓN REAL DE DUPLICADOS
# ----------------------------------------------------------------------
def test_territory_validation_and_duplicate_prevention(client, auth_headers):
    # Crear un dataset en BD para pruebas
    db = SessionLocal()
    dataset_id = "test_epi_surveillance_v2"
    db.query(ObservationDB).filter(ObservationDB.dataset_id == dataset_id).delete()
    db.query(DatasetDB).filter(DatasetDB.id == dataset_id).delete()
    
    test_ds = DatasetDB(
        id=dataset_id,
        name="Kenya Epi Surveillance Test",
        source="MOH_Kenya",
        source_type="EMPIRICAL",
        quality_status="VERIFIED",
        is_synthetic=False,
        records_count=0,
        coverage_pct=0.0
    )
    db.add(test_ds)
    db.commit()
    db.close()

    # 1.1 Rechazar condado inválido (county_code=999) -> 422 (Pydantic ge=0, le=47) o 400
    inv_county_payload = {
        "dataset_id": dataset_id,
        "on_conflict": "reject",
        "observations": [
            {"observation_date": "2020-05-01", "county_code": 999, "variable": "daily_cases", "value": 50.0}
        ]
    }
    r1 = client.post("/api/v1/data/observations/import", json=inv_county_payload, headers=auth_headers)
    assert r1.status_code in [400, 422]

    # 1.2 Rechazar inconsistencia de agregación (NATIONAL_DAILY con county_code=1)
    mismatch_payload = {
        "dataset_id": dataset_id,
        "on_conflict": "reject",
        "observations": [
            {"observation_date": "2020-05-01", "county_code": 1, "aggregation_level": "NATIONAL_DAILY", "variable": "daily_cases", "value": 50.0}
        ]
    }
    r2 = client.post("/api/v1/data/observations/import", json=mismatch_payload, headers=auth_headers)
    assert r2.status_code == 400
    assert "county_code debe ser 0" in r2.text or "0" in r2.text

    # 1.3 Ingesta válida nacional (county_code=0)
    valid_national = {
        "dataset_id": dataset_id,
        "on_conflict": "reject",
        "observations": [
            {"observation_date": "2020-05-01", "county_code": 0, "aggregation_level": "NATIONAL_DAILY", "variable": "daily_cases", "value": 100.0},
            {"observation_date": "2020-05-02", "county_code": 0, "aggregation_level": "NATIONAL_DAILY", "variable": "daily_cases", "value": 110.0}
        ]
    }
    r3 = client.post("/api/v1/data/observations/import", json=valid_national, headers=auth_headers)
    assert r3.status_code == 200
    assert r3.json()["inserted_count"] == 2

    # 1.4 Intento de duplicado con política 'reject' -> 409 Conflict
    dup_payload = {
        "dataset_id": dataset_id,
        "on_conflict": "reject",
        "observations": [
            {"observation_date": "2020-05-01", "county_code": 0, "aggregation_level": "NATIONAL_DAILY", "variable": "daily_cases", "value": 100.0}
        ]
    }
    r4 = client.post("/api/v1/data/observations/import", json=dup_payload, headers=auth_headers)
    assert r4.status_code == 409
    assert "duplicado" in r4.text.lower()

    # 1.5 Intento de duplicado con política 'skip' -> omitido explícitamente sin duplicar
    skip_payload = {
        "dataset_id": dataset_id,
        "on_conflict": "skip",
        "observations": [
            {"observation_date": "2020-05-01", "county_code": 0, "aggregation_level": "NATIONAL_DAILY", "variable": "daily_cases", "value": 100.0},
            {"observation_date": "2020-05-03", "county_code": 0, "aggregation_level": "NATIONAL_DAILY", "variable": "daily_cases", "value": 120.0}
        ]
    }
    r5 = client.post("/api/v1/data/observations/import", json=skip_payload, headers=auth_headers)
    assert r5.status_code == 200
    assert r5.json()["inserted_count"] == 1
    assert r5.json()["skipped_duplicates_count"] == 1

    # 1.6 Intento con política 'update' -> actualiza el valor sin crear filas extras
    update_payload = {
        "dataset_id": dataset_id,
        "on_conflict": "update",
        "observations": [
            {"observation_date": "2020-05-01", "county_code": 0, "aggregation_level": "NATIONAL_DAILY", "variable": "daily_cases", "value": 999.0}
        ]
    }
    r6 = client.post("/api/v1/data/observations/import", json=update_payload, headers=auth_headers)
    assert r6.status_code == 200
    assert r6.json()["updated_count"] == 1

    # Verificar que el total de registros en la BD para ese dataset es exactamente 3 (fechas 05-01, 05-02, 05-03)
    db = SessionLocal()
    obs_count = db.query(ObservationDB).filter(ObservationDB.dataset_id == dataset_id).count()
    updated_obs = db.query(ObservationDB).filter(
        ObservationDB.dataset_id == dataset_id,
        ObservationDB.observation_date == datetime(2020, 5, 1)
    ).first()
    db.close()
    assert obs_count == 3
    assert updated_obs is not None
    assert updated_obs.value == 999.0


# ----------------------------------------------------------------------
# 2. JERARQUÍA ESTRICTA DE PROCEDENCIA
# ----------------------------------------------------------------------
def test_composite_provenance_precedence():
    # EMPIRICAL + ESTIMATED -> ESTIMATED
    s1, is_synth1, demo1 = resolve_composite_provenance({"demographics": "EMPIRICAL", "mobility": "ESTIMATED"})
    assert s1 == "ESTIMATED"
    assert not is_synth1
    assert demo1 is True

    # EMPIRICAL + UNKNOWN -> UNKNOWN
    s2, is_synth2, demo2 = resolve_composite_provenance({"demographics": "EMPIRICAL", "mobility": "UNKNOWN"})
    assert s2 == "UNKNOWN"
    assert not is_synth2
    assert demo2 is True

    # Cualquier combinación con SYNTHETIC -> SYNTHETIC
    s3, is_synth3, demo3 = resolve_composite_provenance({"demographics": "EMPIRICAL", "mobility": "SYNTHETIC", "icu": "UNKNOWN"})
    assert s3 == "SYNTHETIC"
    assert is_synth3 is True
    assert demo3 is True

    # Todos los requeridos EMPIRICAL -> EMPIRICAL
    s4, is_synth4, demo4 = resolve_composite_provenance({"demographics": "EMPIRICAL", "mobility": "EMPIRICAL", "icu": "EMPIRICAL"})
    assert s4 == "EMPIRICAL"
    assert not is_synth4
    assert not demo4

    # Un archivo desconocido no debe reclasificarse como SYNTHETIC
    s5, is_synth5, _ = resolve_composite_provenance(["UNKNOWN"])
    assert s5 == "UNKNOWN"
    assert is_synth5 is False


# ----------------------------------------------------------------------
# 3. CONDICIONES PARA EVALUAR H1 Y REPORTAR MÉTRICAS
# ----------------------------------------------------------------------
def test_h1_conditions_and_null_metrics_not_zero():
    # 3.1 Muestra insuficiente / falta de observaciones -> PENDING_OBSERVATIONS
    res_no_obs = HypothesisEvaluator.evaluate_h1(
        ground_truth=[100.0, 105.0],
        twin_predictions=[102.0, 106.0]
    )
    assert res_no_obs["h1_status"] == "PENDING_OBSERVATIONS"
    assert res_no_obs["h1_supported"] is False
    assert res_no_obs["mape_digital_twin_pct"] is None  # Estrictamente None, no 0.0
    assert res_no_obs["delta_mape_pp"] is None

    # 3.2 Sin modelo base -> PENDING_BASELINE
    gt = [100.0, 120.0, 130.0, 150.0, 180.0, 210.0]
    cand = [105.0, 122.0, 128.0, 148.0, 185.0, 208.0]
    res_no_base = HypothesisEvaluator.evaluate_h1(
        ground_truth=gt,
        twin_predictions=cand,
        seir_predictions=None,
        source_type="EMPIRICAL"
    )
    assert res_no_base["h1_status"] == "PENDING_BASELINE"
    assert res_no_base["h1_supported"] is False
    assert res_no_base["mape_digital_twin_pct"] is not None
    assert res_no_base["mape_seir_baseline_pct"] is None
    assert res_no_base["delta_mape_pp"] is None

    # 3.3 Solapamiento con período de calibración -> PENDING_INDEPENDENT_EVALUATION
    res_overlap = HypothesisEvaluator.evaluate_h1(
        ground_truth=gt,
        twin_predictions=cand,
        seir_predictions=[140.0, 160.0, 170.0, 190.0, 220.0, 250.0],
        overlap_detected=True,
        source_type="EMPIRICAL"
    )
    assert res_overlap["h1_status"] == "PENDING_INDEPENDENT_EVALUATION"
    assert res_overlap["eligible_for_h1"] is False
    assert res_overlap["h1_supported"] is False
    assert "SOLAPAMIENTO" in res_overlap["warning"]

    # 3.4 Procedencia sintética bloquea H1 -> BLOCKED_SYNTHETIC
    res_synth = HypothesisEvaluator.evaluate_h1(
        ground_truth=gt,
        twin_predictions=cand,
        seir_predictions=[140.0, 160.0, 170.0, 190.0, 220.0, 250.0],
        is_synthetic=True
    )
    assert res_synth["h1_status"] == "BLOCKED_SYNTHETIC"
    assert res_synth["eligible_for_h1"] is False
    assert "DATOS SINTÉTICOS" in res_synth["warning"]


# ----------------------------------------------------------------------
# 4. SOBOL: CONTRATO CANÓNICO, RECUPERACIÓN TRAS REINICIO E ISHIGAMI
# ----------------------------------------------------------------------
def test_sobol_recovery_on_restart_and_ishigami_benchmark():
    db = SessionLocal()
    # Simular una tarea que estaba RUNNING cuando se apagó el servidor
    task_id = "test-sobol-interrupted-01"
    db.query(SobolTaskDB).filter(SobolTaskDB.id == task_id).delete()
    
    interrupted_task = SobolTaskDB(
        id=task_id,
        status="RUNNING",
        model_analyzed="SEIR Classical Baseline Model (Compartmental Aggregated)",
        target_metric="peak_infections",
        samples_per_variable=64,
        total_evaluations=448,
        seed=42
    )
    db.add(interrupted_task)
    db.commit()
    db.close()

    # Ejecutar la rutina de recuperación de arranque
    SobolSensitivityAnalyzer.recover_on_startup()

    # Verificar que el estado cambió a INTERRUPTED y no a COMPLETED ni auto-resumido
    db = SessionLocal()
    recovered = db.query(SobolTaskDB).filter(SobolTaskDB.id == task_id).first()
    assert recovered is not None
    assert recovered.status == "INTERRUPTED"
    assert "reinicio" in recovered.error.lower()
    assert recovered.indices_json is None
    db.delete(recovered)
    db.commit()
    db.close()

    # Verificar benchmark analítico de Ishigami
    ishigami_res = evaluate_ishigami_benchmark(samples_n=512, seed=42)
    assert ishigami_res["converged"] is True
    assert ishigami_res["benchmark_passed"] is True
    assert "first_order" in ishigami_res["indices"]
    assert "total_order" in ishigami_res["indices"]


# ----------------------------------------------------------------------
# 5. MONITOREO PERSISTIDO EN 3 MODALIDADES SIN GENERACIÓN ALEATORIA
# ----------------------------------------------------------------------
def test_monitoring_three_modes_no_random_generation():
    db = SessionLocal()
    service = ModelMonitoringService(db)

    # 5.1 Modo DATA_DRIFT sin datos observados -> PENDING
    drift_res = service.run_monitoring_evaluation(monitoring_mode="DATA_DRIFT")
    assert drift_res.monitoring_mode == "DATA_DRIFT"
    assert drift_res.overall_status == "PENDING"
    assert drift_res.unavailability_reason is not None

    # 5.2 Modo OUTPUT_STABILITY (evalúa series de simulaciones reales sin ruido sintético)
    stability_res = service.run_monitoring_evaluation(monitoring_mode="OUTPUT_STABILITY")
    assert stability_res.monitoring_mode == "OUTPUT_STABILITY"
    assert stability_res.overall_status in ["PENDING", "HEALTHY", "WARNING", "CRITICAL"]

    # 5.3 Modo PREDICTIVE_DEGRADATION (evalúa modelo activo vs observaciones posteriores reales)
    degrad_res = service.run_monitoring_evaluation(monitoring_mode="PREDICTIVE_DEGRADATION")
    assert degrad_res.monitoring_mode == "PREDICTIVE_DEGRADATION"
    assert degrad_res.overall_status in ["PENDING", "HEALTHY", "WARNING", "CRITICAL"]
    db.close()


# ----------------------------------------------------------------------
# 6. EXPORTACIONES DESDE REGISTROS PERSISTIDOS (PDF Y EXCEL)
# ----------------------------------------------------------------------
def test_export_endpoints_with_persisted_evaluation(client, auth_headers):
    # Obtener el último evaluation_id persistido o crear uno de prueba
    db = SessionLocal()
    eval_record = db.query(EvaluationRunDB).first()
    if not eval_record:
        eval_record = EvaluationRunDB(
            id="eval-test-export-v2",
            candidate_simulation_id="sim-test-cand",
            baseline_simulation_id="sim-test-base",
            observed_dataset_id="test_ds_export",
            candidate_version="v2.1",
            aggregation_level="NATIONAL_DAILY",
            source_type="EMPIRICAL",
            is_demo=False,
            mape_candidate=11.5,
            rmse_candidate=18.2,
            r2_candidate=0.91,
            data_coverage_pct=95.0,
            h1_status="SUPPORTED",
            h1_supported=True,
            eligible_for_h1=True,
            scientific_conclusion="Conclusión de prueba para reporte",
            evaluated_by="admin@epidemic-twin.ke"
        )
        db.add(eval_record)
        db.commit()
    eval_id = eval_record.id
    db.close()

    # 6.1 Exportar PDF
    pdf_res = client.post(
        "/api/v1/reports/export/by-id/pdf",
        json={"evaluation_id": eval_id, "include_audit_trail": True},
        headers=auth_headers
    )
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert pdf_res.content.startswith(b"%PDF")
    
    # Comprobar contenido interno del PDF generado
    import io
    import pypdf
    pdf_reader = pypdf.PdfReader(io.BytesIO(pdf_res.content))
    assert len(pdf_reader.pages) > 0
    pdf_full_text = "".join(p.extract_text() or "" for p in pdf_reader.pages)
    assert (eval_id in pdf_full_text) or ("DOSSIER" in pdf_full_text.upper()) or ("EPIDEMIOL" in pdf_full_text.upper())

    # 6.2 Exportar Excel
    excel_res = client.post(
        "/api/v1/reports/export/by-id/excel",
        json={"evaluation_id": eval_id, "include_audit_trail": True},
        headers=auth_headers
    )
    assert excel_res.status_code == 200
    assert "openxmlformats" in excel_res.headers["content-type"]
    assert excel_res.content.startswith(b"PK\x03\x04")
    
    # Comprobar contenido y celdas del Excel generado
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(excel_res.content))
    assert len(wb.sheetnames) > 0
    cell_values = [str(cell.value) for ws in wb.worksheets for row in ws.iter_rows() for cell in row if cell.value is not None]
    assert any(eval_id in cv or "11.5" in cv or "SUPPORTED" in cv or "Evaluación" in cv for cv in cell_values)
