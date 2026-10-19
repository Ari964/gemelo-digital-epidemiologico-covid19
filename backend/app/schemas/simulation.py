from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class SimulationParameters(BaseModel):
    model_config = {"protected_namespaces": ()}
    name: str = Field(default="Epidemiological Simulation", description="Nombre descriptivo de la simulación")
    days: int = Field(default=120, ge=10, le=365)
    simulation_start_date: Optional[datetime] = Field(default=None, description="Fecha de calendario correspondiente al día 0")
    npi_stringency: float = Field(default=0.0, ge=0.0, le=1.0)
    vaccine_coverage: float = Field(default=0.0, ge=0.0, le=1.0)
    school_closure: bool = False
    border_screening: bool = False
    initial_infected_county: int = Field(default=47, ge=1, le=47)
    initial_cases: int = Field(default=50, ge=1)
    use_empirical_mobility: bool = False  # Default to False because true empirical mobility requires validated dataset
    seed: int = 42
    run_mode: str = Field(default="EXPERIMENTAL", description="Modo de ejecución: OPERATIONAL, EXPERIMENTAL o DEMO")
    model_version: Optional[str] = Field(default=None, description="Versión del modelo de referencia o candidato")
    candidate_version: Optional[str] = None
    dataset_id: Optional[str] = None

class SimulationResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    simulation_id: str
    model_type: str
    model_version: Optional[str] = None
    run_mode: str = "EXPERIMENTAL"
    source_type: str = "ESTIMATED"
    components_provenance: Optional[Dict[str, str]] = None
    is_operational: bool = False
    is_demo: bool = False
    is_synthetic: bool
    mobility_source_type: str = "ESTIMATED"
    artifact_sha256_used: Optional[str] = None
    effective_parameters: Optional[Dict[str, Any]] = None
    warning: Optional[str] = None
    execution_time_ms: int
    parameters_hash: str
    seed: int
    national_summary: Dict[str, Any]
    national_time_series: Dict[str, Any]
    county_results: List[Dict[str, Any]]
    household_equity: Dict[str, Any]
    health_economics: Dict[str, Any]

    def __getitem__(self, item):
        return getattr(self, item)

    def __contains__(self, item):
        return hasattr(self, item)

