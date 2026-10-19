from sqlalchemy import Column, Integer, String, Float, Text, Boolean
from backend.app.db.session import Base

try:
    from geoalchemy2 import Geometry
    HAS_GEOALCHEMY = True
except ImportError:
    HAS_GEOALCHEMY = False
    Geometry = None

from sqlalchemy.types import TypeDecorator

class SafeGeometry(TypeDecorator):
    """
    Tipo de columna espacial seguro:
    - En PostgreSQL/PostGIS: Se compila e interactúa como Geometry(geometry_type, srid) de GeoAlchemy2.
    - En SQLite: Se compila como Text, evitando llamadas fallidas a funciones C de SpatiaLite
      como RecoverGeometryColumn o InitSpatialMetaData cuando no está cargada la extensión dinámica.
    """
    impl = Text
    cache_ok = True

    def __init__(self, geometry_type='GEOMETRY', srid=4326, **kwargs):
        super().__init__()
        self.geometry_type = geometry_type
        self.srid = srid

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql' and HAS_GEOALCHEMY and Geometry is not None:
            return dialect.type_descriptor(Geometry(geometry_type=self.geometry_type, srid=self.srid))
        return dialect.type_descriptor(Text())

class CountyDB(Base):
    """
    Entidad Condado (47 condados de Kenia - Constitución 2010).
    Integra censo KNBS 2019, quintiles DHS 2022 y camas UCI KMFL verificadas.
    """
    __tablename__ = "counties"

    code = Column(Integer, primary_key=True, index=True)
    iso_code = Column(String(16), unique=True, index=True, nullable=False)
    name = Column(String(128), unique=True, nullable=False)
    capital = Column(String(128), nullable=False)
    population_2019 = Column(Integer, nullable=False)
    area_sq_km = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Quintiles de riqueza condales (null si no existe fuente pública verificable en el repositorio)
    q1_pct = Column(Float, nullable=True, default=None)
    q2_pct = Column(Float, nullable=True, default=None)
    q3_pct = Column(Float, nullable=True, default=None)
    q4_pct = Column(Float, nullable=True, default=None)
    q5_pct = Column(Float, nullable=True, default=None)
    
    # Camas UCI oficiales Barasa et al. (2020) PLOS ONE S1 Table (null si no verificado)
    icu_beds_verified = Column(Integer, nullable=True)
    icu_source = Column(String(512), nullable=True)
    data_quality_flags = Column(Text, default="[]")
    
    # Geometría espacial PostGIS SRID 4326 (MULTIPOLYGON) / WKT en SQLite
    geom = Column(SafeGeometry(geometry_type='MULTIPOLYGON', srid=4326), nullable=True)
    geom_wkt = Column(Text, nullable=True)

class SubcountyDB(Base):
    """Subcondados para modelado de granularidad fina"""
    __tablename__ = "subcounties"

    id = Column(String(64), primary_key=True, index=True)
    county_code = Column(Integer, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    population = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    geom = Column(SafeGeometry(geometry_type='POLYGON', srid=4326), nullable=True)
    geom_wkt = Column(Text, nullable=True)
