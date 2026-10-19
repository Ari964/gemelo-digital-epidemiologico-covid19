import uuid
import json
import time
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.user import UserDB
from backend.app.models.spatial import CountyDB
from backend.app.models.audit import AuditLogDB
from backend.app.models.simulation import SimulationRunDB
from backend.app.models.model_registry import ModelRegistryDB
from backend.app.models.monitoring import ActiveModelDeploymentDB
from backend.app.analytics.model_registry import ModelRegistryManager
from backend.app.schemas.simulation import SimulationParameters, SimulationResponse
from backend.app.api.deps import get_current_user
from backend.app.epidemiology.hybrid_engine import EpidemiologicalDigitalTwin

router = APIRouter()

@router.post("/run", response_model=SimulationResponse)
def run_simulation(
    params: SimulationParameters,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    # 1. Separación estricta entre Operación y Experimentación
    run_mode = (params.run_mode or "EXPERIMENTAL").upper()
    active_deployment = None
    calibrated_params = None

    if run_mode == "OPERATIONAL":
        active_deployment = db.query(ActiveModelDeploymentDB).filter(
            ActiveModelDeploymentDB.singleton_id == 1
        ).first()
        if not active_deployment:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="NO_ACTIVE_MODEL_DEPLOYED: No existe un modelo activo y aprobado técnicamente en producción. Para experimentar con configuraciones candidatas, utilice el modo 'EXPERIMENTAL'."
            )
        
        # Comprobar aprobación técnica en registro
        model_entry = db.query(ModelRegistryDB).filter(
            ModelRegistryDB.version == active_deployment.active_version
        ).first()
        if not model_entry or not model_entry.technical_approval:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"MODEL_NOT_APPROVED: La versión activa '{active_deployment.active_version}' no cuenta con aprobación técnica válida en el registro."
            )

        # Cargar artefacto físico y verificar integridad criptográfica SHA-256 contrastando con el despliegue
        try:
            artifact_data = ModelRegistryManager.load_model_artifact(
                active_deployment.active_version,
                expected_sha256=active_deployment.artifact_sha256
            )
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"ARTIFACT_FILE_NOT_FOUND: El artefacto físico para la versión activa '{active_deployment.active_version}' no existe en disco."
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"ARTIFACT_INTEGRITY_VIOLATION: Artefacto modificado o corrupto en disco ({str(e)})."
            )

        # Validar compatibilidad de motor
        engine_type = artifact_data.get("engine_type", "")
        if engine_type and engine_type != "Hybrid_SpatialSEIR_HouseholdABM":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"ARTIFACT_INCOMPATIBLE: El artefacto requiere el motor '{engine_type}', incompatible con este sistema."
            )

        # Parámetros calibrados aprobados (no pueden ser sobreescritos silenciosamente por el cliente)
        calibrated_params = artifact_data.get("parameters", {})
        model_version = active_deployment.active_version
        is_operational = True
    else:
        model_version = params.model_version or "candidate-experimental"
        is_operational = False

    # 2. Cargar condados verificados
    counties_db = db.query(CountyDB).order_by(CountyDB.code.asc()).all()
    if not counties_db:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No hay condados registrados en la base de datos."
        )

    counties = []
    for c in counties_db:
        counties.append({
            "code": c.code,
            "iso_code": c.iso_code,
            "name": c.name,
            "population_2019": c.population_2019,
            "latitude": c.latitude,
            "longitude": c.longitude,
            "icu_beds_verified": c.icu_beds_verified,
            "poverty_quintiles": {
                "q1": c.q1_pct, "q2": c.q2_pct, "q3": c.q3_pct, "q4": c.q4_pct, "q5": c.q5_pct
            }
        })

    # 3. Instanciar y ejecutar el Gemelo Digital Epidemiológico
    twin = EpidemiologicalDigitalTwin(
        counties=counties,
        use_empirical_mobility=params.use_empirical_mobility,
        seed=params.seed,
        calibrated_params=calibrated_params
    )

    results = twin.run_simulation(
        days=params.days,
        npi_stringency=params.npi_stringency,
        vaccine_coverage=params.vaccine_coverage,
        school_closure=params.school_closure,
        border_screening=params.border_screening,
        initial_infected_county=params.initial_infected_county,
        initial_cases=params.initial_cases
    )

    # 4. Derivación estricta de procedencia en Backend:
    # Si la movilidad es ESTIMATED o use_empirical_mobility no fue verificado, is_demo es True.
    # El cliente NO puede forzar is_demo=False
    is_demo_derived = results.get("is_demo", True)

    sim_id = f"sim-{uuid.uuid4().hex[:12]}"

    # Extraer trayectoria nacional diaria para reproducibilidad de evaluaciones
    ts_data = results.get("national_time_series", {})
    daily_cases = ts_data.get("daily_cases", []) if isinstance(ts_data, dict) else []
    daily_series_json_str = json.dumps(daily_cases)

    # Configuración efectiva empleada
    effective_params = dict(results.get("effective_calibrated_parameters", {}))
    effective_params.update({
        "days": params.days,
        "npi_stringency": params.npi_stringency,
        "vaccine_coverage": params.vaccine_coverage,
        "school_closure": params.school_closure,
        "border_screening": params.border_screening,
        "initial_infected_county": params.initial_infected_county,
        "initial_cases": params.initial_cases,
        "seed": params.seed
    })

    sim_name = params.name if params.name and params.name != "Epidemiological Simulation" else f"[{run_mode}] Simulación {params.days}d - NPI {params.npi_stringency*100:.0f}% (v{model_version})"

    # 5. REGISTRO DE AUDITORÍA CRIPTOGRÁFICA
    audit_entry = AuditLogDB(
        id=f"aud-{uuid.uuid4().hex[:12]}",
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action="SIMULATION_RUN",
        parameters_hash=results["parameters_hash"],
        seed=params.seed,
        execution_time_ms=results["execution_time_ms"],
        details=json.dumps({
            "sim_id": sim_id,
            "run_mode": run_mode,
            "model_version": model_version,
            "days": params.days,
            "npi_stringency": params.npi_stringency,
            "vaccine_coverage": params.vaccine_coverage,
            "is_synthetic": results["is_synthetic"],
            "is_demo": is_demo_derived,
            "is_operational": is_operational,
            "total_cases": results["national_summary"]["total_cases"],
            "total_deaths": results["national_summary"]["total_deaths"]
        })
    )
    db.add(audit_entry)

    # 6. Guardar histórico de simulación con evidencia completa y parámetros efectivos
    sim_record = SimulationRunDB(
        id=sim_id,
        user_id=current_user.id,
        name=sim_name,
        parameters_json=params.model_dump_json(),
        effective_parameters_json=json.dumps(effective_params),
        artifact_sha256_used=active_deployment.artifact_sha256 if active_deployment else None,
        simulation_start_date=getattr(params, "simulation_start_date", None) or datetime.utcnow(),
        results_summary_json=json.dumps(results["national_summary"]),
        execution_time_ms=results["execution_time_ms"],
        is_synthetic=results["is_synthetic"],
        run_mode=run_mode,
        model_version=model_version,
        is_operational=is_operational,
        is_demo=is_demo_derived,
        daily_series_json=daily_series_json_str
    )
    db.add(sim_record)
    db.commit()

    return SimulationResponse(
        simulation_id=sim_id,
        model_type=results["model_type"],
        model_version=model_version,
        run_mode=run_mode,
        source_type=results.get("source_type", "ESTIMATED"),
        components_provenance=results.get("components_provenance"),
        is_operational=is_operational,
        is_demo=is_demo_derived,
        is_synthetic=results["is_synthetic"],
        mobility_source_type=results["mobility_source_type"],
        artifact_sha256_used=active_deployment.artifact_sha256 if active_deployment else None,
        effective_parameters=effective_params,
        warning=results.get("warning"),
        execution_time_ms=results["execution_time_ms"],
        parameters_hash=results["parameters_hash"],
        seed=params.seed,
        national_summary=results["national_summary"],
        national_time_series=results["national_time_series"],
        county_results=results["county_results"],
        household_equity=results["household_equity"],
        health_economics=results["health_economics"]
    )

@router.get("/history")
def get_simulation_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    sims = db.query(SimulationRunDB).order_by(SimulationRunDB.created_at.desc()).limit(limit).all()
    results = []
    for s in sims:
        summary = {}
        if s.results_summary_json:
            try:
                summary = json.loads(s.results_summary_json)
            except Exception:
                summary = {}
        results.append({
            "id": s.id,
            "user_id": s.user_id,
            "name": s.name,
            "execution_time_ms": s.execution_time_ms,
            "is_synthetic": s.is_synthetic,
            "is_demo": getattr(s, "is_demo", True),
            "run_mode": getattr(s, "run_mode", "EXPERIMENTAL"),
            "model_version": getattr(s, "model_version", "1.0.0"),
            "is_operational": getattr(s, "is_operational", False),
            "created_at": s.created_at,
            "summary": summary
        })
    return results
