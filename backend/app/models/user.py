from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime
from backend.app.db.session import Base

class UserRole(str, Enum):
    ADMINISTRADOR = "admin"
    EPIDEMIOLOGO = "epidemiologist"
    ANALISTA = "analyst"
    ADMIN = "admin"
    EPIDEMIOLOGIST = "epidemiologist"
    ANALYST = "analyst"

class UserDB(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    role = Column(String(32), nullable=False)  # admin, epidemiologist, analyst
    status = Column(String(32), default="active")  # active, suspended
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
