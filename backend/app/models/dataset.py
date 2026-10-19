from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text
from backend.app.db.session import Base

class DatasetDB(Base):
    """
    Control de procedencia, calidad y linaje de datos (CRISP-DM Fase 1-3).
    Clasificación estricta: EMPIRICAL, ESTIMATED, SYNTHETIC, UNKNOWN.
    Estado de calidad conservador: PENDING hasta verificación explícita.
    """
    __tablename__ = "datasets"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    source = Column(String(128), nullable=False)
    dataset_version = Column(String(32), default="v1.0.0", nullable=False)
    source_type = Column(String(32), default="UNKNOWN", nullable=False)  # EMPIRICAL, ESTIMATED, SYNTHETIC, UNKNOWN
    source_name = Column(String(128), nullable=True)
    source_reference = Column(String(256), nullable=True)
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    ingested_at = Column(DateTime, default=datetime.utcnow)
    content_sha256 = Column(String(64), nullable=True)
    records_count = Column(Integer, default=0)
    coverage_pct = Column(Float, default=100.0)
    quality_status = Column(String(32), default="PENDING", nullable=False)  # PENDING, VERIFIED, WARNING, REJECTED
    validation_issues_json = Column(Text, default="[]")
    is_synthetic = Column(Boolean, default=False, nullable=False)
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)
