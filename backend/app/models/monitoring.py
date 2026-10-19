from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, CheckConstraint
from backend.app.db.session import Base

class ActiveModelDeploymentDB(Base):
    """
    Singleton de despliegue en base de datos (CRISP-DM Fase 6).
    Garantiza a nivel de esquema relacional que existe exactamente
    una única versión activa en producción mediante CHECK (singleton_id = 1).
    """
    __tablename__ = "active_model_deployment"

    singleton_id = Column(Integer, primary_key=True, default=1)
    active_version = Column(String(32), nullable=False)
    model_name = Column(String(128), nullable=False)
    artifact_sha256 = Column(String(64), nullable=False)
    deployed_at = Column(DateTime, default=datetime.utcnow)
    deployed_by = Column(String(128), nullable=False)
    notes = Column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint('singleton_id = 1', name='chk_single_active_model_deployment'),
    )

class ModelMonitoringLogDB(Base):
    """
    Bitácora de monitoreo manual y bajo demanda de modelos (CRISP-DM Fase 6).
    Registra evaluaciones de deriva de datos (PSI, KS) y degradación predictiva.
    Métricas estrictamente nullables cuando los datos sean insuficientes o no disponibles.
    """
    __tablename__ = "model_monitoring_logs"

    id = Column(String(64), primary_key=True, index=True)
    model_version = Column(String(32), nullable=False, index=True)
    reference_dataset_id = Column(String(64), nullable=False)
    current_dataset_id = Column(String(64), nullable=False)
    
    time_window_start = Column(DateTime, nullable=True)
    time_window_end = Column(DateTime, nullable=True)
    
    # Status separation
    availability_status = Column(String(32), default="PENDING", nullable=False)  # AVAILABLE, PENDING, ERROR
    severity_status = Column(String(32), nullable=True)                          # STABLE, WARNING, CRITICAL (None if pending/insufficient)
    unavailability_reason = Column(Text, nullable=True)
    
    # Drift Metrics (Nullable)
    variables_analyzed_json = Column(Text, default="[]")
    sample_size_reference = Column(Integer, nullable=True)
    sample_size_current = Column(Integer, nullable=True)
    psi_metrics_json = Column(Text, default="[]")
    ks_metrics_json = Column(Text, default="[]")
    
    # Performance Degradation (Nullable)
    performance_metrics_json = Column(Text, default="{}")
    alerts_json = Column(Text, default="[]")
    recommendation = Column(Text, nullable=True)
    
    evaluated_by = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
