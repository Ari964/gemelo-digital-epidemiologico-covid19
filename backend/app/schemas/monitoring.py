from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AvailabilityStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    PENDING = "PENDING"
    ERROR = "ERROR"

class SeverityStatus(str, Enum):
    HEALTHY = "HEALTHY"
    STABLE = "STABLE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class MonitoringEvaluationRequest(BaseModel):
    model_version: Optional[str] = Field(None, description="Versión del modelo a evaluar. Si es nula, se usa la versión activa.")
    monitoring_mode: str = Field("DATA_DRIFT", description="Modalidad: DATA_DRIFT, OUTPUT_STABILITY, PREDICTIVE_DEGRADATION")
    reference_dataset_id: Optional[str] = Field(None, description="Dataset de referencia histórico")
    current_dataset_id: Optional[str] = Field(None, description="Dataset actual o reciente para detectar drift")
    variables: List[str] = Field(
        default_factory=lambda: ["daily_cases"],
        description="Variables a auditar para estabilidad poblacional"
    )
    notes: Optional[str] = Field(None, description="Notas u observaciones de la evaluación de monitoreo")
    baseline_eval_id: Optional[str] = Field(None, description="ID de evaluación base")
    recent_sim_id: Optional[str] = Field(None, description="ID de simulación reciente")

    model_config = ConfigDict(extra="ignore")

class DriftMetric(BaseModel):
    variable: str
    psi_value: Optional[float] = None
    psi_status: Optional[str] = None
    ks_statistic: Optional[float] = None
    ks_p_value: Optional[float] = None
    sample_size_ref: Optional[int] = None
    sample_size_curr: Optional[int] = None
    warning_message: Optional[str] = None

class MonitoringStatusResponse(BaseModel):
    active_model_name: Optional[str] = None
    active_model_version: Optional[str] = None
    is_active: bool = False
    monitoring_mode: str = "DATA_DRIFT"  # DATA_DRIFT, OUTPUT_STABILITY, PREDICTIVE_DEGRADATION
    overall_status: str = "PENDING"  # HEALTHY, WARNING, CRITICAL, PENDING
    last_evaluated_at: Optional[datetime] = None
    unavailability_reason: Optional[str] = None
    psi_value: Optional[float] = None
    psi_status: Optional[str] = None
    ks_p_value: Optional[float] = None
    ks_status: Optional[str] = None
    metrics: List[DriftMetric] = Field(default_factory=list)
    performance_metrics: Optional[Dict[str, Any]] = None
    alerts: List[str] = Field(default_factory=list)
    recommendation: Optional[str] = None
    is_manual_run: bool = True

class MonitoringLogResponse(BaseModel):
    id: str
    model_version: str
    evaluated_at: Optional[datetime] = None
    psi_value: Optional[float] = None
    psi_status: Optional[str] = None
    ks_p_value: Optional[float] = None
    ks_status: Optional[str] = None
    overall_status: str = "PENDING"
    notes: Optional[str] = None
    unavailability_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
