"""Add spatial geom columns to counties and subcounties

Revision ID: 004_spatial_geom_columns
Revises: 003_dataset_observations_and_traceability
Create Date: 2026-09-18

"""
from alembic import op
import sqlalchemy as sa

revision = '004_spatial_geom_columns'
down_revision = '003_dataset_observations_and_traceability'
branch_labels = None
depends_on = None

def get_geom_types(dialect_name: str):
    if dialect_name == 'postgresql':
        try:
            from geoalchemy2 import Geometry
            return (
                Geometry(geometry_type='MULTIPOLYGON', srid=4326),
                Geometry(geometry_type='POLYGON', srid=4326)
            )
        except ImportError:
            return sa.Text(), sa.Text()
    return sa.Text(), sa.Text()

def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()
    dialect_name = conn.dialect.name

    county_geom_type, subcounty_geom_type = get_geom_types(dialect_name)

    # 1. Alter counties: add geom if missing
    if 'counties' in existing_tables:
        county_cols = [c['name'] for c in inspector.get_columns('counties')]
        if 'geom' not in county_cols:
            with op.batch_alter_table('counties') as batch_op:
                batch_op.add_column(sa.Column('geom', county_geom_type, nullable=True))

    # 2. Alter subcounties: add geom if missing
    if 'subcounties' in existing_tables:
        subcounty_cols = [c['name'] for c in inspector.get_columns('subcounties')]
        if 'geom' not in subcounty_cols:
            with op.batch_alter_table('subcounties') as batch_op:
                batch_op.add_column(sa.Column('geom', subcounty_geom_type, nullable=True))

def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if 'subcounties' in existing_tables:
        subcounty_cols = [c['name'] for c in inspector.get_columns('subcounties')]
        if 'geom' in subcounty_cols:
            with op.batch_alter_table('subcounties') as batch_op:
                batch_op.drop_column('geom')

    if 'counties' in existing_tables:
        county_cols = [c['name'] for c in inspector.get_columns('counties')]
        if 'geom' in county_cols:
            with op.batch_alter_table('counties') as batch_op:
                batch_op.drop_column('geom')
