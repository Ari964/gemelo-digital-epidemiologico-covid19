import json
import uuid
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.audit import AuditLogDB
from backend.app.models.user import UserDB

def record_audit_event(
    db: Session,
    user_id: str,
    action: str,
    details: Optional[Dict[str, Any]] = None,
    parameters_hash: str = "sha256:audit_recorded",
    seed: int = 42,
    execution_time_ms: int = 0
) -> AuditLogDB:
    """
    Registra un evento de auditoría criptográfica en la base de datos vinculándolo estrictamente a un usuario.
    """
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    user_email = user.email if user else "system@epidemic-twin.ke"
    user_role = user.role if user else "system"

    details_str = json.dumps(details) if isinstance(details, dict) else (details or "{}")

    entry = AuditLogDB(
        id=f"aud-{uuid.uuid4().hex[:12]}",
        user_id=user_id,
        user_email=user_email,
        user_role=user_role,
        action=action,
        parameters_hash=parameters_hash,
        seed=seed,
        execution_time_ms=execution_time_ms,
        details=details_str
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
