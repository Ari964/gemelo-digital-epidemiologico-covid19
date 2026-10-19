"""Initial Schema for Epidemiological Digital Twin

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-06

"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Users Table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('email', sa.String(length=128), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(length=256), nullable=False),
        sa.Column('role', sa.String(length=32), nullable=False),
        sa.Column('status', sa.String(length=32), server_default='active'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now())
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Audit Logs Table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('user_id', sa.String(length=64), nullable=False),
        sa.Column('user_email', sa.String(length=128), nullable=False),
        sa.Column('user_role', sa.String(length=32), nullable=False),
        sa.Column('action', sa.String(length=64), nullable=False),
        sa.Column('parameters_hash', sa.String(length=128), nullable=False),
        sa.Column('seed', sa.Integer(), server_default='42'),
        sa.Column('execution_time_ms', sa.Integer(), server_default='0'),
        sa.Column('details', sa.Text(), nullable=True)
    )
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])

    # Counties Table
    op.create_table(
        'counties',
        sa.Column('code', sa.Integer(), primary_key=True),
        sa.Column('iso_code', sa.String(length=16), unique=True, nullable=False),
        sa.Column('name', sa.String(length=128), unique=True, nullable=False),
        sa.Column('capital', sa.String(length=128), nullable=False),
        sa.Column('population_2019', sa.Integer(), nullable=False),
        sa.Column('area_sq_km', sa.Float(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('q1_pct', sa.Float(), server_default='0.20'),
        sa.Column('q2_pct', sa.Float(), server_default='0.20'),
        sa.Column('q3_pct', sa.Float(), server_default='0.20'),
        sa.Column('q4_pct', sa.Float(), server_default='0.20'),
        sa.Column('q5_pct', sa.Float(), server_default='0.20'),
        sa.Column('icu_beds_verified', sa.Integer(), nullable=True),
        sa.Column('icu_source', sa.String(length=256), nullable=True),
        sa.Column('data_quality_flags', sa.Text(), server_default='[]'),
        sa.Column('geom_wkt', sa.Text(), nullable=True)
    )

    # Subcounties Table
    op.create_table(
        'subcounties',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('county_code', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('population', sa.Integer(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('geom_wkt', sa.Text(), nullable=True)
    )

    # Datasets Table
    op.create_table(
        'datasets',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('source', sa.String(length=128), nullable=False),
        sa.Column('is_synthetic', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('records_count', sa.Integer(), server_default='0'),
        sa.Column('coverage_pct', sa.Float(), server_default='100.0'),
        sa.Column('metadata_json', sa.Text(), server_default='{}'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )

    # Model Registry Table
    op.create_table(
        'model_registry',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('version', sa.String(length=32), unique=True, nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('file_path', sa.String(length=256), nullable=False),
        sa.Column('file_sha256', sa.String(length=64), nullable=False),
        sa.Column('technical_approval', sa.Boolean(), server_default='0'),
        sa.Column('technical_approved_by', sa.String(length=128), nullable=True),
        sa.Column('technical_approved_at', sa.DateTime(), nullable=True),
        sa.Column('h1_status', sa.String(length=32), server_default='PENDING'),
        sa.Column('h1_evaluation_json', sa.Text(), server_default='{}'),
        sa.Column('metrics_json', sa.Text(), server_default='{}'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )

    # Simulations Table
    op.create_table(
        'simulations',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('user_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('parameters_json', sa.Text(), nullable=False),
        sa.Column('results_summary_json', sa.Text(), nullable=False),
        sa.Column('execution_time_ms', sa.Integer(), server_default='0'),
        sa.Column('is_synthetic', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )

def downgrade() -> None:
    op.drop_table('simulations')
    op.drop_table('model_registry')
    op.drop_table('datasets')
    op.drop_table('subcounties')
    op.drop_table('counties')
    op.drop_table('audit_logs')
    op.drop_table('users')
