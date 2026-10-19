from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.audit import AuditLogDB
from backend.app.models.user import UserDB
from backend.app.schemas.audit import AuditLogResponse
from backend.app.api.deps import get_current_user

router = APIRouter()

@router.get("", response_model=List[AuditLogResponse])
def list_audit_logs(
    limit: int = Query(default=100, ge=1, le=500),
    action: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    query = db.query(AuditLogDB)
    if action:
        query = query.filter(AuditLogDB.action == action)
    logs = query.order_by(AuditLogDB.timestamp.desc()).limit(limit).all()
    return logs
