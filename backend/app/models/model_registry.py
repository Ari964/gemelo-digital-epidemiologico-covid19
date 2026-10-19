from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text
from backend.app.db.session import Base

class ModelRegistryDB(Base):
    """
    Registro inmutable de versiones de modelos epidemiológicos (CRISP-DM Fase 5-6).
    Vincula versión con evaluación formal almacenada, artefacto físico e integridad SHA-256.
    """
    __tablename__ = "model_registry"

    id = Column(String(64), primary_key=True, index=True)
    version = Column(String(32), unique=True, index=True, nullable=False)  # e.g. "v1.0.0"
    name = Column(String(128), nullable=False)
    file_path = Column(String(256), nullable=False)
    file_sha256 = Column(String(64), nullable=False)  # Hash SHA-256 para comprobación de integridad
    
    # Vinculación con evaluación formal
    evaluation_id = Column(String(64), nullable=True)
    parameters_json = Column(Text, default="{}")
    metrics_json = Column(Text, default="{}")
    
    # Aprobación Técnica de Ingeniería
    technical_approval = Column(Boolean, default=False)
    technical_approved_by = Column(String(128), nullable=True)
    technical_approved_at = Column(DateTime, nullable=True)
    
    # Contraste de Hipótesis H1
    h1_status = Column(String(32), default="PENDING")  # PENDING, SUPPORTED, REJECTED, BLOCKED_SYNTHETIC
    h1_evaluation_json = Column(Text, default="{}")
    
    # Estado de activación
    is_active = Column(Boolean, default=False, nullable=False)
    activated_at = Column(DateTime, nullable=True)
    activated_by = Column(String(128), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class ModelActivationDB(Base):
    """
    Historial auditable de activaciones y reversiones de versiones (CRISP-DM Fase 6).
    """
    __tablename__ = "model_activations"

    id = Column(String(64), primary_key=True, index=True)
    version = Column(String(32), nullable=False, index=True)
    action = Column(String(32), default="ACTIVATE", nullable=False)  # ACTIVATE, REVERT, DEACTIVATE
    previous_version = Column(String(32), nullable=True)
    activated_by = Column(String(128), nullable=False)
    activated_at = Column(DateTime, default=datetime.utcnow, index=True)
    notes = Column(Text, nullable=True)
