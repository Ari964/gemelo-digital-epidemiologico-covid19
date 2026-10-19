from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from backend.app.db.session import Base

class SimulationRunDB(Base):
    """
    Registro inmutable de simulaciones epidemiológicas ejecutadas.
    Distingue modo operativo (con versión activa aprobada) de modo experimental y demo.
    Almacena series temporales para evaluación reproducible sin duplicación.
    """
    __tablename__ = "simulations"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    
    # Traceability & Versioning
    model_version = Column(String(32), nullable=True, index=True)
    dataset_id = Column(String(64), nullable=True, index=True)
    run_mode = Column(String(32), default="EXPERIMENTAL", nullable=False)  # OPERATIONAL, EXPERIMENTAL, DEMO
    is_operational = Column(Boolean, default=False, nullable=False)
    is_demo = Column(Boolean, default=False, nullable=False)
    is_synthetic = Column(Boolean, default=False, nullable=False)
    
    parameters_json = Column(Text, nullable=False)
    effective_parameters_json = Column(Text, default="{}", nullable=False)  # Effective parameters actually passed to engine
    artifact_sha256_used = Column(String(64), nullable=True)               # Active artifact hash if operational
    simulation_start_date = Column(DateTime, nullable=True)                # Day 0 alignment with calendar date
    results_summary_json = Column(Text, nullable=False)
    daily_series_json = Column(Text, nullable=True)  # JSON with national daily infections/deaths/cases
    
    execution_time_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
