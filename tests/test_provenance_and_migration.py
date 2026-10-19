import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.db.base import Base
from backend.app.models.dataset import DatasetDB

def test_conservative_migration_and_defaults():
    """
    Prueba que un dataset antiguo sin procedencia explícita o verificación
    tenga por defecto quality_status = 'PENDING' y source_type = 'UNKNOWN'.
    Nunca debe promoverse automáticamente a 'VERIFIED' ni 'EMPIRICAL'.
    """
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(test_engine)
    Session = sessionmaker(bind=test_engine)
    session = Session()

    # Simular inserción de dataset antiguo sin metadatos de procedencia
    legacy_dataset = DatasetDB(
        id="legacy_unverified_records_2021",
        name="Registros Antiguos Sin Auditoría",
        source="Archivo Local Antiguo",
        is_synthetic=False,
        records_count=500,
        coverage_pct=50.0
    )
    session.add(legacy_dataset)
    session.commit()

    saved = session.query(DatasetDB).filter(DatasetDB.id == "legacy_unverified_records_2021").first()
    assert saved is not None
    # Regla 1: quality_status DEFAULT 'PENDING', source_type DEFAULT 'UNKNOWN'
    assert saved.quality_status == "PENDING"
    assert saved.source_type == "UNKNOWN"
    assert saved.quality_status != "VERIFIED"
    assert saved.source_type != "EMPIRICAL"

    session.close()
