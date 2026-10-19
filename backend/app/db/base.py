# Import all models so that Base has them before being imported by Alembic
from backend.app.db.session import Base
from backend.app.models.user import UserDB
from backend.app.models.audit import AuditLogDB
from backend.app.models.spatial import CountyDB, SubcountyDB
from backend.app.models.dataset import DatasetDB
from backend.app.models.model_registry import ModelRegistryDB, ModelActivationDB
from backend.app.models.simulation import SimulationRunDB
from backend.app.models.evaluation import EvaluationRunDB
from backend.app.models.monitoring import ActiveModelDeploymentDB, ModelMonitoringLogDB

__all__ = [
    "Base",
    "UserDB",
    "AuditLogDB",
    "CountyDB",
    "SubcountyDB",
    "DatasetDB",
    "ModelRegistryDB",
    "ModelActivationDB",
    "SimulationRunDB",
    "EvaluationRunDB",
    "ActiveModelDeploymentDB",
    "ModelMonitoringLogDB",
]
