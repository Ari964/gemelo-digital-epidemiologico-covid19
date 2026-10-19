from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
from backend.app.db.session import Base

class SobolTaskDB(Base):
    """
    Persistencia de tareas de análisis global de sensibilidad de Sobol.
    Garantiza trazabilidad y persistencia de resultados tras reinicios del servidor.
    """
    __tablename__ = "sobol_tasks"

    id = Column(String(64), primary_key=True, index=True)
    status = Column(String(32), nullable=False, default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED, INTERRUPTED
    model_analyzed = Column(String(128), default="SEIR Classical Baseline Model (Compartmental Aggregated)")
    target_metric = Column(String(64), default="peak_infections")
    samples_per_variable = Column(Integer, nullable=False)
    total_evaluations = Column(Integer, nullable=False)
    seed = Column(Integer, default=42)
    indices_json = Column(Text, nullable=True)
    most_sensitive_parameter = Column(String(128), nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
