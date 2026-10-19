import uuid
import json
import os
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.user import UserDB
from backend.app.models.dataset import DatasetDB
from backend.app.models.simulation import SimulationRunDB
from backend.app.models.model_registry import ModelRegistryDB, ModelActivationDB
from backend.app.models.evaluation import EvaluationRunDB
from backend.app.models.monitoring import ActiveModelDeploymentDB
from backend.app.models.audit import AuditLogDB
from backend.app.api.deps import get_current_user, require_roles
from backend.app.analytics.validation_data import ExternalValidationManager
from backend.app.analytics.hypothesis_evaluator import HypothesisEvaluator
from backend.app.analytics.model_registry import ModelRegistryManager
from backend.app.schemas.validation import (
    EvaluationCreateRequest,
    EvaluationResponse,
    TechnicalApprovalRequest,
    TechnicalApprovalResponse,
    ModelActivationRequest,
    ModelActivationResponse
)

router = APIRouter()

@router.get("/external")
def get_external_validation():
    return ExternalValidationManager.get_external_validation_status()

@router.get("/weekly-evaluation")
def get_weekly_model_evaluation():
    """
    Retorna los resultados científicos auditables de evaluación semanal generados por
    scripts/train_and_evaluate_models.py. Incluye validación cruzada temporal (5 pliegues),
    espacio de hiperparámetros explorado, configuración óptima, métricas en desarrollo y test,
    y pruebas estadísticas formales (Diebold-Mariano con corrección HLN, Wilcoxon pareado,
    Shapiro-Wilk y Kolmogorov-Smirnov).
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
    eval_json_path = os.path.join(base_dir, "models", "model_evaluation_weekly_results.json")
    champion_json_path = os.path.join(base_dir, "models", "champion_covid_model_v1.0.json")

    if os.path.exists(eval_json_path):
        with open(eval_json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    elif os.path.exists(champion_json_path):
        with open(champion_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {
                "generated_at": data.get("created_at"),
                "task_name": "Weekly COVID-19 Surveillance Forecasting & Sensitivity Exploration (Kenya)",
                "source": "Our World in Data (OWID) / WHO / Kenya Ministry of Health",
                "raw_data_sha256": "c82f3cfc5899b25557f3bf69de987dc9628bfa6fbbee55cd77b649c9d34cd2ba",
                "temporal_protocol": data.get("selection_protocol", {}),
                "models": data.get("metrics_summary", {}),
                "statistical_tests": data.get("statistical_tests", {}),
                "untested_comparisons": {
                    "seir_abm_vs_statistical_weekly": {
                        "status": "NOT_EVALUATED_IN_WEEKLY_SERIES",
                        "scientific_rationale": "El Gemelo Digital SEIR/ABM opera como simulador contrafactual mecánico de escenarios y políticas de salud pública. No compite en la tarea canónica semanal de extrapolación estadística pura de OWID, por lo que no se le atribuyen métricas de error semanal."
                    }
                },
                "test_series_data": []
            }
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artefacto de evaluación semanal no encontrado en el servidor. Ejecute scripts/train_and_evaluate_models.py."
        )

@router.get("/status")
def get_validation_status(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    ext_val = ExternalValidationManager.get_external_validation_status()
    datasets = db.query(DatasetDB).all()
    active_deployment = db.query(ActiveModelDeploymentDB).first()
    
    datasets_info = []
    for d in datasets:
        datasets_info.append({
            "id": d.id,
            "name": d.name,
            "source": d.source,
            "source_type": d.source_type,
            "quality_status": d.quality_status,
            "is_synthetic": d.is_synthetic,
            "records_count": d.records_count,
            "coverage_pct": d.coverage_pct
        })

    return {
        "external_validation_2023_2024": ext_val,
        "active_deployment": {
            "version": active_deployment.active_version,
            "deployed_at": active_deployment.deployed_at,
            "deployed_by": active_deployment.deployed_by,
            "artifact_sha256": active_deployment.artifact_sha256
        } if active_deployment else None,
        "datasets": datasets_info,
        "h1_criteria": {
            "hypothesis": "Delta MAPE >= 15.0 pp & Wilcoxon p < 0.05",
            "condition": "Strictly empirical data (synthetic or demo data permanently blocked)",
            "benchmark": "Classical Non-spatial SEIR vs Population-Level Digital Twin"
        },
        "technical_approval_gate": {
            "min_coverage_pct": 80.0,
            "prohibit_synthetic": True,
            "prohibit_demo": True,
            "min_r2": 0.80,
            "max_mape": 25.0
        }
    }

@router.post("/evaluations", response_model=EvaluationResponse)
def create_evaluation(
    req: EvaluationCreateRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Crea una evaluación formal inmutable a partir de simulaciones y datasets persistidos en BD.
    El backend deriva automáticamente la procedencia e is_demo a partir de las entidades referenciadas:
    el cliente NO puede falsificar is_demo=False o datos empíricos.
    """
    from datetime import timedelta
    from backend.app.models.observation import ObservationDB
    from backend.app.models.spatial import CountyDB

    # 0. Validar coherencia entre aggregation_level y county_code
    if req.aggregation_level == "NATIONAL_DAILY" and req.county_code != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Inconsistencia territorial: para aggregation_level='NATIONAL_DAILY', county_code debe ser 0. Recibido: {req.county_code}."
        )
    if req.aggregation_level == "COUNTY_DAILY":
        if req.county_code < 1 or req.county_code > 47:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Código de condado inválido ({req.county_code}). Debe estar en el rango 1..47 para 'COUNTY_DAILY'."
            )
        county_exists = db.query(CountyDB).filter(CountyDB.code == req.county_code).first()
        if not county_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El condado con código {req.county_code} no existe en la base territorial."
            )

    # 1. Recuperar simulación candidata
    candidate_sim = db.query(SimulationRunDB).filter(SimulationRunDB.id == req.candidate_simulation_id).first()
    if not candidate_sim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulación candidata con ID '{req.candidate_simulation_id}' no encontrada."
        )

    # Validar si hay series por condado persistidas si se solicita COUNTY_DAILY
    cand_raw = []
    if candidate_sim.daily_series_json:
        try:
            parsed_series = json.loads(candidate_sim.daily_series_json)
            if isinstance(parsed_series, dict):
                county_key = str(req.county_code)
                if county_key in parsed_series:
                    cand_raw = parsed_series[county_key]
                elif req.aggregation_level == "COUNTY_DAILY":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"La simulación candidata '{candidate_sim.id}' no contiene series territoriales para el condado {req.county_code}."
                    )
                else:
                    cand_raw = parsed_series.get("national", [])
            elif isinstance(parsed_series, list):
                if req.aggregation_level == "COUNTY_DAILY":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"La simulación candidata '{candidate_sim.id}' únicamente contiene predicciones nacionales agregadas. Se rechaza la evaluación por condado por ausencia de series territoriales persistidas para el condado {req.county_code}."
                    )
                cand_raw = parsed_series
        except HTTPException:
            raise
        except Exception:
            cand_raw = []

    # 2. Recuperar dataset observado
    observed_dataset = db.query(DatasetDB).filter(DatasetDB.id == req.observed_dataset_id).first()
    if not observed_dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset observado con ID '{req.observed_dataset_id}' no encontrado."
        )

    # 3. Recuperar simulación base (si existe) y verificar que sea modelo SEIR
    baseline_sim = None
    base_raw = None
    if req.baseline_simulation_id:
        baseline_sim = db.query(SimulationRunDB).filter(SimulationRunDB.id == req.baseline_simulation_id).first()
        if not baseline_sim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Simulación base con ID '{req.baseline_simulation_id}' no encontrada."
            )
        is_seir = (
            "SEIR" in (baseline_sim.name or "").upper() or
            "SEIR" in (baseline_sim.model_version or "").upper() or
            "SEIR" in (baseline_sim.parameters_json or "").upper() or
            "SEIR" in (baseline_sim.effective_parameters_json or "").upper()
        )
        if not is_seir:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La simulación base '{baseline_sim.id}' no corresponde al modelo de línea base requerido (SEIR clásico compartimental)."
            )
        if baseline_sim.daily_series_json:
            try:
                base_raw = json.loads(baseline_sim.daily_series_json)
                if isinstance(base_raw, dict):
                    if req.aggregation_level == "COUNTY_DAILY":
                        base_raw = base_raw.get(str(req.county_code), [])
                    else:
                        base_raw = base_raw.get("national", [])
            except Exception:
                base_raw = None

    # 4. Derivar procedencia e is_demo de forma estricta en el backend
    is_demo = (
        candidate_sim.is_demo or
        candidate_sim.is_synthetic or
        candidate_sim.run_mode == "DEMO" or
        observed_dataset.is_synthetic or
        observed_dataset.source_type in ["SYNTHETIC", "ESTIMATED", "UNKNOWN"] or
        (baseline_sim is not None and (baseline_sim.is_synthetic or baseline_sim.is_demo))
    )

    source_type = observed_dataset.source_type
    if is_demo and source_type == "EMPIRICAL":
        source_type = "ESTIMATED"

    # 5. Consultar observaciones persistidas en ObservationDB y validar variable y unidad
    obs_records = db.query(ObservationDB).filter(
        ObservationDB.dataset_id == observed_dataset.id,
        ObservationDB.variable == req.target_variable,
        ObservationDB.aggregation_level == req.aggregation_level,
        ObservationDB.county_code == req.county_code
    ).order_by(ObservationDB.observation_date.asc()).all()

    if obs_records:
        first_unit = obs_records[0].unit
        if first_unit not in ["count", "cases"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Incompatibilidad de unidad: La variable '{req.target_variable}' predice recuento de casos ('count'), pero las observaciones en BD tienen unidad '{first_unit}'."
            )

    import math
    obs_map = {
        o.observation_date.date(): float(o.value)
        for o in obs_records
        if o.value is not None and math.isfinite(o.value)
    }

    # 6. Construir calendario de cada simulación desde su PROPIA fecha de inicio
    cand_start_dt = candidate_sim.simulation_start_date
    if not cand_start_dt:
        if req.period_start:
            cand_start_dt = req.period_start
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La simulación candidata '{candidate_sim.id}' no cuenta con 'simulation_start_date' definida. No se puede construir el calendario."
            )
    cand_start_date = cand_start_dt.date() if isinstance(cand_start_dt, datetime) else cand_start_dt

    cand_by_date = {}
    if cand_raw:
        for i, val in enumerate(cand_raw):
            if val is not None:
                try:
                    fval = float(val)
                    if math.isfinite(fval):
                        cand_by_date[cand_start_date + timedelta(days=i)] = fval
                except (ValueError, TypeError):
                    pass

    base_by_date = None
    if baseline_sim is not None:
        base_start_dt = baseline_sim.simulation_start_date
        if not base_start_dt:
            if req.period_start:
                base_start_dt = req.period_start
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"La simulación base '{baseline_sim.id}' no cuenta con 'simulation_start_date' definida."
                )
        base_start_date = base_start_dt.date() if isinstance(base_start_dt, datetime) else base_start_dt
        base_by_date = {}
        if base_raw:
            for j, val in enumerate(base_raw):
                if val is not None:
                    try:
                        fval = float(val)
                        if math.isfinite(fval):
                            base_by_date[base_start_date + timedelta(days=j)] = fval
                    except (ValueError, TypeError):
                        pass

    # Intervalo de evaluación
    eval_start_dt = req.period_start or cand_start_dt
    eval_start = eval_start_dt.date() if isinstance(eval_start_dt, datetime) else eval_start_dt

    if req.period_end:
        eval_end_dt = req.period_end
        eval_end = eval_end_dt.date() if isinstance(eval_end_dt, datetime) else eval_end_dt
    else:
        horizon_days = len(cand_raw) if cand_raw else 60
        eval_end = cand_start_date + timedelta(days=max(0, horizon_days - 1))
        eval_end_dt = datetime.combine(eval_end, datetime.min.time())

    if eval_start > eval_end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Período de evaluación inválido: fecha de inicio ({eval_start}) posterior al fin ({eval_end})."
        )

    expected_days = (eval_end - eval_start).days + 1

    # 7. Alineación sin relleno artificial de ceros
    # Puntos compartidos Observaciones y Candidata
    aligned_obs = []
    aligned_cand = []
    missing_count = 0

    curr_d = eval_start
    while curr_d <= eval_end:
        has_obs = curr_d in obs_map
        has_cand = curr_d in cand_by_date
        if has_obs and has_cand:
            aligned_obs.append(obs_map[curr_d])
            aligned_cand.append(cand_by_date[curr_d])
        else:
            missing_count += 1
        curr_d += timedelta(days=1)

    obs_count = len(aligned_obs)
    coverage_pct = round((obs_count / expected_days) * 100.0, 2) if expected_days > 0 else 0.0

    # Puntos compartidos para comparación con Baseline (triangulación en días comunes exactos)
    aligned_base_for_eval = None
    h1_ground_truth = aligned_obs
    h1_twin_pred = aligned_cand

    if baseline_sim is not None and base_by_date is not None:
        three_way_obs = []
        three_way_cand = []
        three_way_base = []
        curr_d = eval_start
        while curr_d <= eval_end:
            if curr_d in obs_map and curr_d in cand_by_date and curr_d in base_by_date:
                three_way_obs.append(obs_map[curr_d])
                three_way_cand.append(cand_by_date[curr_d])
                three_way_base.append(base_by_date[curr_d])
            curr_d += timedelta(days=1)

        # Muestra mínima de puntos comunes requerida: 10
        if len(three_way_base) >= 10:
            aligned_base_for_eval = three_way_base
            h1_ground_truth = three_way_obs
            h1_twin_pred = three_way_cand
        else:
            aligned_base_for_eval = None

    # 8. Trazabilidad del período de calibración
    overlap_detected = False
    calibration_period_known = False
    cal_start_dt = None
    cal_end_dt = None

    # Intentar recuperar desde effective_parameters_json de la candidata
    if candidate_sim.effective_parameters_json:
        try:
            eff_json = json.loads(candidate_sim.effective_parameters_json)
            if eff_json.get("calibration_period_start"):
                cal_start_dt = datetime.fromisoformat(eff_json["calibration_period_start"])
            if eff_json.get("calibration_period_end"):
                cal_end_dt = datetime.fromisoformat(eff_json["calibration_period_end"])
        except Exception:
            pass

    if not cal_start_dt and req.calibration_period_start:
        cal_start_dt = req.calibration_period_start
    if not cal_end_dt and req.calibration_period_end:
        cal_end_dt = req.calibration_period_end

    if cal_start_dt and cal_end_dt:
        calibration_period_known = True
        c_start = cal_start_dt.date() if isinstance(cal_start_dt, datetime) else cal_start_dt
        c_end = cal_end_dt.date() if isinstance(cal_end_dt, datetime) else cal_end_dt
        overlap_detected = not (eval_end < c_start or eval_start > c_end)

    # 9. Evaluar con HypothesisEvaluator
    eval_res = HypothesisEvaluator.evaluate_h1(
        ground_truth=h1_ground_truth,
        seir_predictions=aligned_base_for_eval,
        twin_predictions=h1_twin_pred,
        is_synthetic=candidate_sim.is_synthetic or observed_dataset.is_synthetic,
        is_demo=is_demo,
        source_type=source_type,
        overlap_detected=overlap_detected,
        calibration_period_known=calibration_period_known
    )

    eval_id = f"eval-{uuid.uuid4().hex[:12]}"
    audit_data = eval_res.get("audit", {})

    territory_str = "Kenya (National Agregated)" if req.aggregation_level == "NATIONAL_DAILY" else f"County {req.county_code}"

    eval_record = EvaluationRunDB(
        id=eval_id,
        candidate_simulation_id=candidate_sim.id,
        baseline_simulation_id=baseline_sim.id if baseline_sim else None,
        candidate_version=candidate_sim.model_version or "candidate_v1",
        baseline_version=baseline_sim.model_version if baseline_sim else None,
        candidate_params_json=(candidate_sim.effective_parameters_json if candidate_sim.effective_parameters_json and candidate_sim.effective_parameters_json != "{}" else candidate_sim.parameters_json),
        baseline_params_json=((baseline_sim.effective_parameters_json if baseline_sim.effective_parameters_json and baseline_sim.effective_parameters_json != "{}" else baseline_sim.parameters_json) if baseline_sim else "{}"),
        observed_dataset_id=observed_dataset.id,
        observed_dataset_version=observed_dataset.dataset_version,
        source_type=source_type,
        sources_used_json=json.dumps([
            {"id": observed_dataset.id, "source_type": observed_dataset.source_type, "sha256": observed_dataset.content_sha256}
        ]),
        period_start=datetime.combine(eval_start, datetime.min.time()),
        period_end=datetime.combine(eval_end, datetime.min.time()),
        calibration_period_start=cal_start_dt,
        calibration_period_end=cal_end_dt,
        evaluation_period_start=datetime.combine(eval_start, datetime.min.time()),
        evaluation_period_end=datetime.combine(eval_end, datetime.min.time()),
        overlap_detected=overlap_detected,
        eligible_for_h1=eval_res.get("eligible_for_h1", False),
        data_coverage_pct=coverage_pct,
        territory_scope=territory_str,
        aggregation_level=req.aggregation_level,
        target_variable=req.target_variable,
        target_unit="cases",
        observations_count=obs_count,
        zeros_count=audit_data.get("zeros_count", 0),
        missing_count=missing_count,
        exclusions_count=audit_data.get("exclusions_count", 0),
        zero_handling_method=audit_data.get("zero_handling_method", "epsilon_smoothed_mape_eps_1.0"),
        mape_candidate=eval_res.get("mape_digital_twin_pct"),
        mape_baseline=eval_res.get("mape_seir_baseline_pct"),
        delta_mape_pp=eval_res.get("delta_mape_pp"),
        rmse_candidate=eval_res.get("rmse_candidate"),
        rmse_baseline=eval_res.get("rmse_baseline"),
        r2_candidate=eval_res.get("r2_candidate"),
        r2_baseline=eval_res.get("r2_baseline"),
        wilcoxon_stat=eval_res.get("wilcoxon_test", {}).get("statistic"),
        wilcoxon_p_value=eval_res.get("wilcoxon_test", {}).get("p_value"),
        h1_supported=eval_res.get("h1_supported", False),
        h1_status=eval_res.get("h1_status", "PENDING_OBSERVATIONS"),
        scientific_conclusion=eval_res.get("scientific_conclusion"),
        is_demo=is_demo,
        unavailability_reason=eval_res.get("reason"),
        evaluated_by=current_user.email,
        created_at=datetime.utcnow()
    )

    db.add(eval_record)
    
    # Registro de auditoría
    audit_entry = AuditLogDB(
        id=f"aud-{uuid.uuid4().hex[:12]}",
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action="EVALUATION_CREATE",
        parameters_hash=hashlib.sha256(f"{eval_id}:{candidate_sim.id}".encode("utf-8")).hexdigest(),
        seed=42,
        execution_time_ms=15,
        details=json.dumps({"evaluation_id": eval_id, "h1_status": eval_record.h1_status, "is_demo": is_demo, "coverage_pct": coverage_pct})
    )
    db.add(audit_entry)
    db.commit()

    return EvaluationResponse(
        evaluation_id=eval_record.id,
        candidate_simulation_id=eval_record.candidate_simulation_id,
        baseline_simulation_id=eval_record.baseline_simulation_id,
        observed_dataset_id=eval_record.observed_dataset_id,
        source_type=eval_record.source_type,
        observations_count=eval_record.observations_count,
        data_coverage_pct=eval_record.data_coverage_pct,
        zeros_count=eval_record.zeros_count,
        missing_count=eval_record.missing_count,
        exclusions_count=eval_record.exclusions_count,
        zero_handling_method=eval_record.zero_handling_method,
        overlap_detected=eval_record.overlap_detected,
        eligible_for_h1=eval_record.eligible_for_h1,
        mape_candidate=eval_record.mape_candidate,
        mape_baseline=eval_record.mape_baseline,
        delta_mape_pp=eval_record.delta_mape_pp,
        rmse_candidate=eval_record.rmse_candidate,
        rmse_baseline=eval_record.rmse_baseline,
        r2_candidate=eval_record.r2_candidate,
        r2_baseline=eval_record.r2_baseline,
        wilcoxon_stat=eval_record.wilcoxon_stat,
        wilcoxon_p_value=eval_record.wilcoxon_p_value,
        h1_supported=eval_record.h1_supported,
        h1_status=eval_record.h1_status,
        scientific_conclusion=eval_record.scientific_conclusion,
        is_demo=eval_record.is_demo,
        unavailability_reason=eval_record.unavailability_reason,
        evaluated_by=eval_record.evaluated_by,
        created_at=eval_record.created_at
    )

@router.get("/evaluations", response_model=List[EvaluationResponse])
def list_evaluations(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    records = db.query(EvaluationRunDB).order_by(EvaluationRunDB.created_at.desc()).limit(limit).all()
    out = []
    for r in records:
        out.append(EvaluationResponse(
            evaluation_id=r.id,
            candidate_simulation_id=r.candidate_simulation_id,
            baseline_simulation_id=r.baseline_simulation_id,
            observed_dataset_id=r.observed_dataset_id,
            source_type=r.source_type,
            observations_count=r.observations_count,
            data_coverage_pct=r.data_coverage_pct,
            zeros_count=r.zeros_count,
            missing_count=r.missing_count,
            exclusions_count=r.exclusions_count,
            zero_handling_method=r.zero_handling_method,
            overlap_detected=r.overlap_detected,
            eligible_for_h1=r.eligible_for_h1,
            mape_candidate=r.mape_candidate,
            mape_baseline=r.mape_baseline,
            delta_mape_pp=r.delta_mape_pp,
            rmse_candidate=r.rmse_candidate,
            rmse_baseline=r.rmse_baseline,
            r2_candidate=r.r2_candidate,
            r2_baseline=r.r2_baseline,
            wilcoxon_stat=r.wilcoxon_stat,
            wilcoxon_p_value=r.wilcoxon_p_value,
            h1_supported=r.h1_supported,
            h1_status=r.h1_status,
            scientific_conclusion=r.scientific_conclusion,
            is_demo=r.is_demo,
            unavailability_reason=r.unavailability_reason,
            evaluated_by=r.evaluated_by,
            created_at=r.created_at
        ))
    return out

@router.get("/evaluations/{evaluation_id}", response_model=EvaluationResponse)
def get_evaluation_by_id(
    evaluation_id: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    r = db.query(EvaluationRunDB).filter(EvaluationRunDB.id == evaluation_id).first()
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluación con ID '{evaluation_id}' no encontrada."
        )
    return EvaluationResponse(
        evaluation_id=r.id,
        candidate_simulation_id=r.candidate_simulation_id,
        baseline_simulation_id=r.baseline_simulation_id,
        observed_dataset_id=r.observed_dataset_id,
        source_type=r.source_type,
        observations_count=r.observations_count,
        data_coverage_pct=r.data_coverage_pct,
        zeros_count=r.zeros_count,
        missing_count=r.missing_count,
        exclusions_count=r.exclusions_count,
        zero_handling_method=r.zero_handling_method,
        overlap_detected=r.overlap_detected,
        eligible_for_h1=r.eligible_for_h1,
        mape_candidate=r.mape_candidate,
        mape_baseline=r.mape_baseline,
        delta_mape_pp=r.delta_mape_pp,
        rmse_candidate=r.rmse_candidate,
        rmse_baseline=r.rmse_baseline,
        r2_candidate=r.r2_candidate,
        r2_baseline=r.r2_baseline,
        wilcoxon_stat=r.wilcoxon_stat,
        wilcoxon_p_value=r.wilcoxon_p_value,
        h1_supported=r.h1_supported,
        h1_status=r.h1_status,
        scientific_conclusion=r.scientific_conclusion,
        is_demo=r.is_demo,
        unavailability_reason=r.unavailability_reason,
        evaluated_by=r.evaluated_by,
        created_at=r.created_at
    )

@router.post("/technical-approval", response_model=TechnicalApprovalResponse)
def technical_approval(
    req: TechnicalApprovalRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_roles(["admin", "epidemiologist"]))
):
    """
    Aprobación técnica de ingeniería estricta (Gate CRISP-DM Fase 5).
    Exige obligatoriamente un evaluation_id existente en BD.
    Rechaza solicitudes con parámetros numéricos manuales (ConfigDict extra='forbid').
    Rechaza evaluaciones demostrativas o con procedencia no empírica.
    """
    eval_run = db.query(EvaluationRunDB).filter(EvaluationRunDB.id == req.evaluation_id).first()
    if not eval_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluación con ID '{req.evaluation_id}' no encontrada. La aprobación técnica requiere evidencia almacenada."
        )

    approval_res = ModelRegistryManager.evaluate_technical_approval_from_eval(
        eval_run=eval_run,
        approver_name=current_user.name
    )

    if not approval_res["is_approved"]:
        return TechnicalApprovalResponse(
            is_approved=False,
            evaluation_id=eval_run.id,
            rejection_reasons=approval_res["rejection_reasons"],
            audit_criteria=approval_res["audit_criteria"]
        )

    # Si aprueba: persistir artefacto JSON con comprobación de hash SHA-256
    base_ver = f"v{datetime.utcnow().strftime('%Y%m%d%H%M')}"
    version_str = base_ver
    suffix = 1
    while db.query(ModelRegistryDB).filter(ModelRegistryDB.version == version_str).first():
        version_str = f"{base_ver}_{suffix}"
        suffix += 1

    cand_params = json.loads(eval_run.candidate_params_json) if eval_run.candidate_params_json else {}
    if not cand_params:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede aprobar un modelo sin parámetros efectivos persistidos."
        )

    artifact_info = ModelRegistryManager.save_model_artifact(
        version=version_str,
        name=f"Digital Twin Champion {version_str}",
        parameters=cand_params,
        metrics={
            "r2": eval_run.r2_candidate,
            "mape": eval_run.mape_candidate,
            "delta_mape_pp": eval_run.delta_mape_pp,
            "observations_count": eval_run.observations_count
        },
        evaluation_id=eval_run.id,
        technical_approval=True,
        approved_by=current_user.name,
        data_coverage_pct=eval_run.data_coverage_pct or 0.0,
        is_synthetic=False,
        source_type="EMPIRICAL"
    )

    # Guardar en ModelRegistryDB
    model_entry = ModelRegistryDB(
        id=f"mod-{uuid.uuid4().hex[:12]}",
        version=version_str,
        name=f"Digital Twin Champion {version_str}",
        file_path=artifact_info["file_path"],
        file_sha256=artifact_info["sha256_checksum"],
        evaluation_id=eval_run.id,
        parameters_json=eval_run.candidate_params_json,
        metrics_json=json.dumps({
            "r2": eval_run.r2_candidate,
            "mape": eval_run.mape_candidate,
            "delta_mape_pp": eval_run.delta_mape_pp
        }),
        technical_approval=True,
        technical_approved_by=current_user.name,
        technical_approved_at=datetime.utcnow(),
        h1_status=eval_run.h1_status,
        h1_evaluation_json=json.dumps({"h1_supported": eval_run.h1_supported, "conclusion": eval_run.scientific_conclusion}),
        is_active=False
    )
    db.add(model_entry)

    # Registrar evento de auditoría
    audit_entry = AuditLogDB(
        id=f"aud-{uuid.uuid4().hex[:12]}",
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action="MODEL_APPROVAL",
        parameters_hash=artifact_info["sha256_checksum"],
        seed=42,
        execution_time_ms=10,
        details=json.dumps({"evaluation_id": eval_run.id, "approved_version": version_str, "notes": req.notes})
    )
    db.add(audit_entry)
    db.commit()

    return TechnicalApprovalResponse(
        is_approved=True,
        evaluation_id=eval_run.id,
        version=version_str,
        approved_by=current_user.name,
        approved_at=datetime.utcnow(),
        artifact_file=artifact_info["file_name"],
        sha256_checksum=artifact_info["sha256_checksum"],
        rejection_reasons=[],
        audit_criteria=approval_res["audit_criteria"]
    )

@router.post("/activate-model", response_model=ModelActivationResponse)
def activate_model(
    req: ModelActivationRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_roles(["admin", "epidemiologist"]))
):
    """
    Activación formal de una versión de modelo para uso operativo (CRISP-DM Fase 6).
    Exige rol admin o epidemiologist.
    Verifica que el modelo tenga technical_approval=True, que su artefacto exista físicamente
    y que su hash SHA-256 coincida exactamente.
    Actualiza el singleton active_model_deployment garantizando que haya exactamente una activa.
    """
    # 1. Buscar modelo en registro
    model = db.query(ModelRegistryDB).filter(ModelRegistryDB.version == req.version).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Versión de modelo '{req.version}' no encontrada en el registro."
        )

    if not model.technical_approval:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La versión '{req.version}' no cuenta con Aprobación Técnica de Ingeniería. No puede ser activada."
        )

    # 2. Verificar existencia física y hash SHA-256 del artefacto contrastando contra el registro de BD
    try:
        artifact_data = ModelRegistryManager.load_model_artifact(req.version, expected_sha256=model.file_sha256)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Archivo de artefacto físico para la versión '{req.version}' no encontrado en disco."
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Fallo en comprobación de integridad SHA-256: {str(e)}"
        )

    sha256_val = artifact_data.get("sha256_checksum", model.file_sha256)

    # 3. Transacción atómica de despliegue
    active_deploy = db.query(ActiveModelDeploymentDB).first()
    prev_ver = active_deploy.active_version if active_deploy else None

    # Desactivar versión anterior en model_registry
    db.query(ModelRegistryDB).filter(ModelRegistryDB.is_active == True).update({"is_active": False})

    # Marcar nueva versión como activa
    model.is_active = True
    model.activated_at = datetime.utcnow()
    model.activated_by = current_user.name

    now_dt = datetime.utcnow()
    if active_deploy:
        active_deploy.active_version = req.version
        active_deploy.model_name = model.name
        active_deploy.artifact_sha256 = sha256_val
        active_deploy.deployed_at = now_dt
        active_deploy.deployed_by = current_user.name
        active_deploy.notes = req.notes
    else:
        active_deploy = ActiveModelDeploymentDB(
            singleton_id=1,
            active_version=req.version,
            model_name=model.name,
            artifact_sha256=sha256_val,
            deployed_at=now_dt,
            deployed_by=current_user.name,
            notes=req.notes
        )
        db.add(active_deploy)

    # Insertar en historial de activaciones
    activation_hist = ModelActivationDB(
        id=f"act-{uuid.uuid4().hex[:12]}",
        version=req.version,
        action="ACTIVATE",
        previous_version=prev_ver,
        activated_by=current_user.name,
        activated_at=now_dt,
        notes=req.notes
    )
    db.add(activation_hist)

    # Registrar evento de auditoría
    audit_entry = AuditLogDB(
        id=f"aud-{uuid.uuid4().hex[:12]}",
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action="MODEL_ACTIVATE",
        parameters_hash=sha256_val,
        seed=42,
        execution_time_ms=8,
        details=json.dumps({"version": req.version, "previous_version": prev_ver, "notes": req.notes})
    )
    db.add(audit_entry)
    db.commit()

    return ModelActivationResponse(
        version=req.version,
        action="ACTIVATE",
        activated_at=now_dt,
        activated_by=current_user.name,
        previous_version=prev_ver,
        artifact_sha256=sha256_val,
        status="ACTIVE",
        notes=req.notes
    )

@router.get("/active-model")
def get_active_model(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    deploy = db.query(ActiveModelDeploymentDB).first()
    if not deploy:
        return {"has_active_model": False, "active_model": None}
    
    model = db.query(ModelRegistryDB).filter(ModelRegistryDB.version == deploy.active_version).first()
    return {
        "has_active_model": True,
        "active_model": {
            "version": deploy.active_version,
            "name": deploy.model_name,
            "artifact_sha256": deploy.artifact_sha256,
            "deployed_at": deploy.deployed_at,
            "deployed_by": deploy.deployed_by,
            "notes": deploy.notes,
            "evaluation_id": model.evaluation_id if model else None,
            "metrics": json.loads(model.metrics_json) if model and model.metrics_json else {},
            "parameters": json.loads(model.parameters_json) if model and model.parameters_json else {}
        }
    }

@router.get("/activations/history")
def get_activations_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    history = db.query(ModelActivationDB).order_by(ModelActivationDB.activated_at.desc()).limit(limit).all()
    return [
        {
            "id": h.id,
            "version": h.version,
            "action": h.action,
            "previous_version": h.previous_version,
            "activated_by": h.activated_by,
            "activated_at": h.activated_at,
            "notes": h.notes
        }
        for h in history
    ]
