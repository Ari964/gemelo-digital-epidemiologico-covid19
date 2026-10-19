from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict

class AuditLogResponse(BaseModel):
    id: str
    timestamp: datetime
    user_id: str
    user_email: str
    user_role: str
    action: str
    parameters_hash: str
    seed: int
    execution_time_ms: int
    details: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
