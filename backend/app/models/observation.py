from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, UniqueConstraint, CheckConstraint
from backend.app.db.session import Base

class ObservationDB(Base):
    """
    Registro inmutable de observaciones epidemiológicas reales/verificadas o de prueba.
    
    Representación territorial unificada y rigurosa:
    - county_code = 0: Representa el ámbito Nacional Agregado ('NATIONAL_DAILY').
    - county_code entre 1 y 47: Representa un Condado específico de Kenia ('COUNTY_DAILY').
    
    Restricción de unicidad:
    Al no permitir NULL en county_code (usando 0 para nacional), la restricción UNIQUE
    opera de manera idéntica y estricta tanto en SQLite como en PostgreSQL/PostGIS.
    """
    __tablename__ = "dataset_observations"

    id = Column(String(64), primary_key=True, index=True)
    dataset_id = Column(String(64), nullable=False, index=True)
    observation_date = Column(DateTime, nullable=False, index=True)
    county_code = Column(Integer, default=0, nullable=False, index=True)
    variable = Column(String(64), default="daily_cases", nullable=False, index=True)
    unit = Column(String(32), default="count", nullable=False)
    value = Column(Float, nullable=False)
    aggregation_level = Column(String(32), default="NATIONAL_DAILY", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('dataset_id', 'observation_date', 'county_code', 'variable', name='uq_dataset_obs_date_county_var'),
        CheckConstraint('county_code >= 0 AND county_code <= 47', name='chk_valid_county_code_or_national'),
    )
