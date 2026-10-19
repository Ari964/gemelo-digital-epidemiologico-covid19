from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict, model_validator

class ExportReportByIdRequest(BaseModel):
    simulation_id: Optional[str] = Field(None, description="ID de simulación almacenada")
    evaluation_id: Optional[str] = Field(None, description="ID de evaluación almacenada")
    title: Optional[str] = Field("Dossier Epidemiológico Oficial - Gemelo Digital de Kenia", description="Título del informe")
    include_audit_trail: Optional[bool] = Field(True, description="Incluir registro de auditoría en la exportación")

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_exactly_one_target(self):
        has_sim = bool(self.simulation_id and self.simulation_id.strip())
        has_eval = bool(self.evaluation_id and self.evaluation_id.strip())
        if not has_sim and not has_eval:
            raise ValueError("Debe proporcionar exactamente uno de: 'simulation_id' o 'evaluation_id'. Ninguno fue suministrado.")
        if has_sim and has_eval:
            raise ValueError("Debe proporcionar exactamente uno de: 'simulation_id' o 'evaluation_id'. No puede suministrar ambos simultáneamente.")
        return self

# Maintain legacy model for backward compatibility with explicit disclaimer
class ExportReportRequest(BaseModel):
    title: Optional[str] = "Informe Epidemiológico - Gemelo Digital de Kenia"
    report_type: Optional[str] = "scenarios"
    lang: Optional[str] = "es"
    language: Optional[str] = None
    cutoff_date: Optional[str] = "2024-07-28"
    county_code: Optional[int] = 0
    simulation_id: Optional[str] = None
    evaluation_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    national_summary: Optional[Dict[str, Any]] = None
    county_results: Optional[List[Dict[str, Any]]] = None
    health_economics: Optional[Dict[str, Any]] = None
    household_equity: Optional[Dict[str, Any]] = None
    is_synthetic: bool = False
    is_demo: bool = False

    @model_validator(mode="after")
    def unify_language(self):
        if self.language and not self.lang:
            self.lang = self.language
        elif self.language:
            self.lang = self.language
        return self

class ReportPreviewRequest(BaseModel):
    report_type: str = Field("data_provenance", description="data_provenance, models, prediction, scenarios")
    lang: Optional[str] = Field("es", description="es, en, sw")
    language: Optional[str] = None
    cutoff_date: Optional[str] = Field("2024-07-28", description="Fecha de corte para predicción")
    county_code: Optional[int] = Field(0, description="0 para nacional")
    simulation_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

    @model_validator(mode="after")
    def unify_language(self):
        if self.language and not self.lang:
            self.lang = self.language
        elif self.language:
            self.lang = self.language
        return self

