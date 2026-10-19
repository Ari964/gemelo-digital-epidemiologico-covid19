from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text
from backend.app.db.session import Base

class EvaluationRunDB(Base):
    """
    Registro inmutable de evaluación científica formal (CRISP-DM Fase 5).
    Conserva linaje reproducible completo: modelos, datasets observados,
    parámetros calibrados, métricas calculadas y contraste de H1.
    """
    __tablename__ = "evaluation_runs"

    id = Column(String(64), primary_key=True, index=True)
    candidate_simulation_id = Column(String(64), nullable=False, index=True)
    baseline_simulation_id = Column(String(64), nullable=True, index=True)
    
    # Model configs & versions
    candidate_version = Column(String(32), nullable=True)
    baseline_version = Column(String(32), nullable=True)
    candidate_params_json = Column(Text, default="{}")
    baseline_params_json = Column(Text, default="{}")
    
    # Observed Dataset & Lineage
    observed_dataset_id = Column(String(64), nullable=False, index=True)
    observed_dataset_version = Column(String(32), default="v1.0.0")
    source_type = Column(String(32), nullable=False)  # EMPIRICAL, ESTIMATED, SYNTHETIC, UNKNOWN
    sources_used_json = Column(Text, default="[]")    # Details of each source and available hashes
    
    # Temporal & Spatial scope
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    calibration_period_start = Column(DateTime, nullable=True)
    calibration_period_end = Column(DateTime, nullable=True)
    evaluation_period_start = Column(DateTime, nullable=True)
    evaluation_period_end = Column(DateTime, nullable=True)
    overlap_detected = Column(Boolean, default=False, nullable=False)
    eligible_for_h1 = Column(Boolean, default=False, nullable=False)
    
    territory_scope = Column(String(64), default="Kenya (47 Counties)")
    aggregation_level = Column(String(32), default="National Daily Aggregated")
    target_variable = Column(String(64), default="daily_cases")
    target_unit = Column(String(32), default="count")
    
    # Observations audit
    observations_count = Column(Integer, default=0)
    zeros_count = Column(Integer, default=0)
    missing_count = Column(Integer, default=0)
    exclusions_count = Column(Integer, default=0)
    data_coverage_pct = Column(Float, nullable=True)
    zero_handling_method = Column(String(64), default="epsilon_smoothed_mape_eps_1.0")
    
    # Calculated metrics (Strictly nullable to avoid fabricating zeros)
    mape_candidate = Column(Float, nullable=True)
    mape_baseline = Column(Float, nullable=True)
    delta_mape_pp = Column(Float, nullable=True)
    rmse_candidate = Column(Float, nullable=True)
    rmse_baseline = Column(Float, nullable=True)
    r2_candidate = Column(Float, nullable=True)
    r2_baseline = Column(Float, nullable=True)
    wilcoxon_stat = Column(Float, nullable=True)
    wilcoxon_p_value = Column(Float, nullable=True)
    
    # H1 hypothesis outcome
    h1_supported = Column(Boolean, default=False, nullable=False)
    h1_status = Column(String(48), default="PENDING", nullable=False)  # SUPPORTED, REJECTED, PENDING_OBSERVATIONS, PENDING_BASELINE, PENDING_INDEPENDENT_EVALUATION, BLOCKED_NON_EMPIRICAL
    scientific_conclusion = Column(Text, nullable=True)
    
    # Demo & Audit flags
    is_demo = Column(Boolean, default=False, nullable=False)
    unavailability_reason = Column(Text, nullable=True)
    evaluated_by = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
