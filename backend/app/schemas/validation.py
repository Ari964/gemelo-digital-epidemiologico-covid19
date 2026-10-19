from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from backend.app.schemas.data import DataSourceType

class EvaluationCreateRequest(BaseModel):
    candidate_simulation_id: str = Field(..., description="ID de la simulación del modelo candidato")
    baseline_simulation_id: Optional[str] = Field(None, description="ID de la simulación del modelo base comparativo")
    observed_dataset_id: str = Field(..., description="ID del dataset observado de referencia")
    target_variable: str = Field("daily_cases", description="Variable objetivo analizada")
    aggregation_level: str = Field("NATIONAL_DAILY", description="Nivel de agregación: NATIONAL_DAILY o COUNTY_DAILY")
    county_code: int = Field(0, ge=0, le=47, description="0 para Nacional Agregado, 1 a 47 para condado específico")
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    calibration_period_start: Optional[datetime] = None
    calibration_period_end: Optional[datetime] = None

    model_config = ConfigDict(extra="forbid")

class EvaluationResponse(BaseModel):
    evaluation_id: str
    candidate_simulation_id: str
    baseline_simulation_id: Optional[str] = None
    observed_dataset_id: str
    source_type: DataSourceType
    observations_count: int
    data_coverage_pct: Optional[float] = None
    zeros_count: int
    missing_count: int
    exclusions_count: int
    zero_handling_method: str
    overlap_detected: bool = False
    eligible_for_h1: bool = False
    
    # Nullable metrics when insufficient data or uncalculable
    mape_candidate: Optional[float] = None
    mape_baseline: Optional[float] = None
    delta_mape_pp: Optional[float] = None
    rmse_candidate: Optional[float] = None
    rmse_baseline: Optional[float] = None
    r2_candidate: Optional[float] = None
    r2_baseline: Optional[float] = None
    wilcoxon_stat: Optional[float] = None
    wilcoxon_p_value: Optional[float] = None
    
    h1_supported: bool
    h1_status: str  # SUPPORTED, REJECTED, PENDING_OBSERVATIONS, PENDING_BASELINE, PENDING_INDEPENDENT_EVALUATION, BLOCKED_NON_EMPIRICAL
    scientific_conclusion: Optional[str] = None
    is_demo: bool
    unavailability_reason: Optional[str] = None
    evaluated_by: str
    created_at: datetime

class TechnicalApprovalRequest(BaseModel):
    evaluation_id: str = Field(..., description="ID inmutable de la evaluación almacenada en base de datos")
    notes: Optional[str] = Field(None, description="Notas u observaciones del revisor técnico")

    # Forbid any manual metrics injection (e.g. r2_fit, mape, is_synthetic)
    model_config = ConfigDict(extra="forbid")

class TechnicalApprovalResponse(BaseModel):
    is_approved: bool
    evaluation_id: str
    version: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    artifact_file: Optional[str] = None
    sha256_checksum: Optional[str] = None
    rejection_reasons: List[str] = Field(default_factory=list)
    audit_criteria: Dict[str, Any] = Field(default_factory=dict)

class ModelActivationRequest(BaseModel):
    version: str = Field(..., description="Versión del modelo aprobado a activar")
    notes: Optional[str] = Field(None, description="Motivo o contexto de la activación")

    model_config = ConfigDict(extra="forbid")

class ModelActivationResponse(BaseModel):
    version: str
    action: str
    activated_at: datetime
    activated_by: str
    previous_version: Optional[str] = None
    artifact_sha256: str
    status: str
    notes: Optional[str] = None
