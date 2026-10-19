from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
from backend.app.db.session import Base

class AuditLogDB(Base):
    """
    Bitácora de Auditoría para trazabilidad de simulaciones y acciones críticas.
    Identidad obtenida estrictamente desde JWT validado.
    """
    __tablename__ = "audit_logs"

    id = Column(String(64), primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    user_email = Column(String(128), nullable=False)
    user_role = Column(String(32), nullable=False)
    action = Column(String(64), nullable=False)  # SIMULATION_RUN, EXPORT_PDF, EXPORT_EXCEL, ETL_SYNC, MODEL_APPROVAL
    parameters_hash = Column(String(128), nullable=False)
    seed = Column(Integer, default=42)
    execution_time_ms = Column(Integer, default=0)
    details = Column(Text, nullable=True)
