from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class SobolRunRequest(BaseModel):
    samples_n: Optional[int] = Field(None, ge=64, le=1024, description="Número de muestras por parámetro")
    n_samples: Optional[int] = Field(None, ge=64, le=1024, description="Alias para samples_n desde clientes frontend")
    target_metric: str = Field("peak_infections", description="Métrica objetivo (e.g. peak_infections, total_cases)")
    seed: int = Field(42, description="Semilla de reproducibilidad del generador pseudoaleatorio")
    calc_second_order: bool = Field(False, description="Cálculo de segundo orden")

    model_config = ConfigDict(extra="ignore")

class SobolIndexItem(BaseModel):
    parameter: str
    parameter_name: str
    S1: float
    S1_conf: Optional[float] = None
    ST: float
    ST_conf: Optional[float] = None
    confidence_interval: Optional[List[float]] = None

class SobolStatusResponse(BaseModel):
    analysis_id: str
    status: str  # PENDING, RUNNING, COMPLETED, FAILED, INTERRUPTED
    progress_pct: int = 0
    model_engine: str = "SEIR_CLASSICAL_BASELINE"
    model_analyzed: str = "SEIR Classical Baseline Model (Compartmental Aggregated)"
    target_metric: str = "peak_infections"
    samples_per_variable: int
    n_samples: int = 128
    total_evaluations: int
    seed: int = 42
    calc_second_order: bool = False
    method: str = "Sobol Global Sensitivity Analysis (Saltelli Variance Decomposition)"
    indices: Optional[List[SobolIndexItem]] = None
    sobol_indices: Optional[List[SobolIndexItem]] = None
    most_sensitive_parameter: Optional[str] = None
    error: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
