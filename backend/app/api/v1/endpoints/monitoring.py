"""
Endpoints para monitoreo de modelos desplegados (CRISP-DM Fase 6).
Permite evaluar drift y estabilidad poblacional de forma manual/on-demand.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.api.deps import get_current_user, require_roles
from backend.app.models.user import UserDB
from backend.app.schemas.monitoring import (
    MonitoringEvaluationRequest,
    MonitoringStatusResponse,
    MonitoringLogResponse
)
from backend.app.analytics.model_monitoring import ModelMonitoringService
from backend.app.services.audit import record_audit_event

router = APIRouter()


@router.get("/status", response_model=MonitoringStatusResponse)
def get_monitoring_status(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Obtiene el estado de monitoreo del modelo actualmente activo (o null si no hay despliegue).
    """
    service = ModelMonitoringService(db)
    status_data = service.get_monitoring_status()
    return status_data


@router.post("/evaluate", response_model=MonitoringStatusResponse)
def trigger_manual_evaluation(
    request: MonitoringEvaluationRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_roles(["admin", "epidemiologist"]))
):
    """
    Ejecuta un ciclo manual/on-demand de evaluación de estabilidad y drift para el modelo activo.
    """
    service = ModelMonitoringService(db)
    try:
        result = service.run_monitoring_evaluation(
            notes=request.notes,
            monitoring_mode=request.monitoring_mode or "DATA_DRIFT",
            reference_dataset_id=request.reference_dataset_id or request.baseline_eval_id,
            current_dataset_id=request.current_dataset_id,
            recent_sim_id=request.recent_sim_id,
            variables=request.variables,
            evaluated_by=current_user.email if current_user and current_user.email else "operator"
        )
        record_audit_event(
            db=db,
            user_id=current_user.id,
            action="MONITORING_MANUAL_EVALUATION",
            details={
                "model_name": result.active_model_name,
                "version": result.active_model_version,
                "overall_status": result.overall_status,
                "psi_status": result.psi_status,
                "unavailability_reason": result.unavailability_reason
            }
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en evaluación de monitoreo: {str(e)}"
        )


@router.get("/history", response_model=List[MonitoringLogResponse])
def get_monitoring_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Obtiene el historial de ciclos de monitoreo registrados.
    """
    service = ModelMonitoringService(db)
    return service.get_monitoring_history(limit=limit)
