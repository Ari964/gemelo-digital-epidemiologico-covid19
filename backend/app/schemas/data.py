from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class DataSourceType(str, Enum):
    EMPIRICAL = "EMPIRICAL"       # Observaciones directas verificadas con fuente, fechas y estructura comprobada
    ESTIMATED = "ESTIMATED"       # Derivado mediante fórmulas o supuestos (e.g. gravedad intercondado)
    SYNTHETIC = "SYNTHETIC"       # Generación artificial para pruebas o docencia
    UNKNOWN = "UNKNOWN"           # Linaje aún no verificado

class DataQualityStatus(str, Enum):
    VERIFIED = "VERIFIED"
    WARNING = "WARNING"
    REJECTED = "REJECTED"
    PENDING = "PENDING"

class DataProvenanceContract(BaseModel):
    dataset_id: str = Field(..., max_length=64)
    dataset_version: str = Field("v1.0.0", max_length=32)
    source_type: DataSourceType
    source_name: Optional[str] = Field(None, max_length=128)
    source_reference: Optional[str] = Field(None, max_length=256)
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    ingested_at: Optional[datetime] = None
    content_sha256: Optional[str] = Field(None, pattern=r"^[a-f0-9]{64}$")
    coverage_pct: float = Field(..., ge=0.0, le=100.0)
    quality_status: DataQualityStatus
    validation_issues: List[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")

class DatasetResponse(BaseModel):
    id: str
    name: str
    source: str
    source_type: DataSourceType
    source_name: Optional[str] = None
    source_reference: Optional[str] = None
    dataset_version: str
    isSynthetic: bool
    is_synthetic: bool
    recordsCount: int
    coveragePct: float
    coverage: str
    quality_status: DataQualityStatus
    status: str
    lastUpdated: str
    description: str
    content_sha256: Optional[str] = None
    disclaimer: Optional[str] = None

class ETLRunResponse(BaseModel):
    status: str
    message: str
    input_datasets: List[str] = Field(default_factory=list)
    rows_read: int
    rows_valid: int
    rows_rejected: int
    duplicates_count: int
    missing_count: int
    transformations_applied: List[str] = Field(default_factory=list)
    coverage_pct: float
    coverage_denominator: str = "47 constitutional counties of Kenya"
    duration_ms: int
    warnings: List[str] = Field(default_factory=list)
    datasets: List[DatasetResponse] = Field(default_factory=list)

class ObservationItemSchema(BaseModel):
    observation_date: datetime = Field(..., description="Fecha de la observación")
    county_code: int = Field(0, ge=0, le=47, description="0 para Nacional Agregado, 1 a 47 para condados")
    variable: str = Field("daily_cases", max_length=64)
    unit: str = Field("count", max_length=32)
    value: float = Field(..., ge=0.0)
    aggregation_level: str = Field("NATIONAL_DAILY", max_length=32)

    model_config = ConfigDict(extra="forbid")

class ObservationImportRequest(BaseModel):
    dataset_id: str = Field(..., description="ID del dataset al que pertenecen las observaciones")
    on_conflict: str = Field("reject", description="Política de conflicto: reject, skip, update")
    observations: List[ObservationItemSchema] = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")

class ObservationImportResponse(BaseModel):
    dataset_id: str
    total_received: int
    inserted_count: int
    updated_count: int
    skipped_duplicates_count: int
    rejected_count: int
    unique_dates_count: int
    unique_territories_count: int
    dataset_total_records: int
    dataset_coverage_pct: float
    message: str
