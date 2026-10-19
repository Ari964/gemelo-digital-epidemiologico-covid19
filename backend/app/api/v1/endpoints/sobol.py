from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.api.deps import get_current_user, require_roles
from backend.app.models.user import UserDB
from backend.app.schemas.sobol import SobolRunRequest, SobolStatusResponse
from backend.app.analytics.sobol_sensitivity import SobolSensitivityAnalyzer
from backend.app.services.audit import record_audit_event

router = APIRouter()


@router.post("/sobol", response_model=SobolStatusResponse, status_code=status.HTTP_202_ACCEPTED)
def launch_sobol_analysis(
    request: SobolRunRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_roles(["admin", "epidemiologist", "data_scientist"]))
):
    """
    Inicia un análisis global de sensibilidad de Sobol de forma asíncrona.
    Retorna 202 Accepted con el analysis_id para sondeo.
    """
    n_samples = request.samples_n or request.n_samples or 128
    try:
        analysis_id = SobolSensitivityAnalyzer.start_analysis_task(
            samples_n=n_samples,
            target_metric=request.target_metric,
            seed=request.seed
        )
        task_data = SobolSensitivityAnalyzer.get_analysis_status(analysis_id)
        
        record_audit_event(
            db=db,
            user_id=current_user.id,
            action="SOBOL_ANALYSIS_LAUNCHED",
            details={
                "analysis_id": analysis_id,
                "samples_n": n_samples,
                "seed": request.seed,
                "model_engine": "SEIR_CLASSICAL_BASELINE"
            }
        )
        return task_data
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al iniciar análisis de Sobol: {str(e)}"
        )


@router.get("/sobol", response_model=List[SobolStatusResponse])
def list_sobol_analyses(
    limit: int = 10,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Lista los análisis de Sobol registrados y persistidos en el sistema.
    """
    return SobolSensitivityAnalyzer.list_analyses(limit=limit)


@router.get("/sobol/{analysis_id}", response_model=SobolStatusResponse)
def get_sobol_status(
    analysis_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Consulta el estado y resultados de un análisis de Sobol por su ID.
    """
    status_data = SobolSensitivityAnalyzer.get_analysis_status(analysis_id)
    if not status_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Análisis de Sobol con ID '{analysis_id}' no encontrado."
        )
    return status_data
