"""Dataset Observations, Simulation Traceability and Sobol Tasks Schema

Revision ID: 003_dataset_observations_and_traceability
Revises: 002_traceability_monitoring_evaluation
Create Date: 2026-09-18

"""
from alembic import op
import sqlalchemy as sa

revision = '003_dataset_observations_and_traceability'
down_revision = '002_traceability_monitoring_evaluation'
branch_labels = None
depends_on = None

def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # 1. Crear tabla dataset_observations
    if 'dataset_observations' not in existing_tables:
        op.create_table(
            'dataset_observations',
            sa.Column('id', sa.String(length=64), primary_key=True),
            sa.Column('dataset_id', sa.String(length=64), nullable=False),
            sa.Column('observation_date', sa.DateTime(), nullable=False),
            sa.Column('county_code', sa.Integer(), server_default='0', nullable=False),
            sa.Column('variable', sa.String(length=64), server_default='daily_cases', nullable=False),
            sa.Column('unit', sa.String(length=32), server_default='count', nullable=False),
            sa.Column('value', sa.Float(), nullable=False),
            sa.Column('aggregation_level', sa.String(length=32), server_default='NATIONAL_DAILY', nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.UniqueConstraint('dataset_id', 'observation_date', 'county_code', 'variable', name='uq_dataset_obs_date_county_var'),
            sa.CheckConstraint('county_code >= 0 AND county_code <= 47', name='chk_valid_county_code_or_national')
        )
        op.create_index('ix_obs_dataset_id', 'dataset_observations', ['dataset_id'])
        op.create_index('ix_obs_date', 'dataset_observations', ['observation_date'])
        op.create_index('ix_obs_county_code', 'dataset_observations', ['county_code'])
        op.create_index('ix_obs_variable', 'dataset_observations', ['variable'])

    # 2. Crear tabla sobol_tasks
    if 'sobol_tasks' not in existing_tables:
        op.create_table(
            'sobol_tasks',
            sa.Column('id', sa.String(length=64), primary_key=True),
            sa.Column('status', sa.String(length=32), server_default='PENDING', nullable=False),
            sa.Column('model_analyzed', sa.String(length=128), nullable=True),
            sa.Column('target_metric', sa.String(length=64), server_default='peak_infections', nullable=True),
            sa.Column('samples_per_variable', sa.Integer(), nullable=False),
            sa.Column('total_evaluations', sa.Integer(), nullable=False),
            sa.Column('seed', sa.Integer(), server_default='42', nullable=True),
            sa.Column('indices_json', sa.Text(), nullable=True),
            sa.Column('most_sensitive_parameter', sa.String(length=128), nullable=True),
            sa.Column('error', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('completed_at', sa.DateTime(), nullable=True),
            sa.Column('duration_ms', sa.Integer(), nullable=True)
        )
        op.create_index('ix_sobol_tasks_created_at', 'sobol_tasks', ['created_at'])

    # 3. Alterar simulations: trazabilidad de parámetros efectivos y fecha de inicio
    sim_cols = [c['name'] for c in inspector.get_columns('simulations')]
    with op.batch_alter_table('simulations') as batch_op:
        if 'effective_parameters_json' not in sim_cols:
            batch_op.add_column(sa.Column('effective_parameters_json', sa.Text(), server_default='{}', nullable=False))
        if 'artifact_sha256_used' not in sim_cols:
            batch_op.add_column(sa.Column('artifact_sha256_used', sa.String(length=64), nullable=True))
        if 'simulation_start_date' not in sim_cols:
            batch_op.add_column(sa.Column('simulation_start_date', sa.DateTime(), nullable=True))

    # 4. Alterar evaluation_runs: calibración vs evaluación, solapamiento y elegibilidad
    eval_cols = [c['name'] for c in inspector.get_columns('evaluation_runs')]
    with op.batch_alter_table('evaluation_runs') as batch_op:
        if 'calibration_period_start' not in eval_cols:
            batch_op.add_column(sa.Column('calibration_period_start', sa.DateTime(), nullable=True))
        if 'calibration_period_end' not in eval_cols:
            batch_op.add_column(sa.Column('calibration_period_end', sa.DateTime(), nullable=True))
        if 'evaluation_period_start' not in eval_cols:
            batch_op.add_column(sa.Column('evaluation_period_start', sa.DateTime(), nullable=True))
        if 'evaluation_period_end' not in eval_cols:
            batch_op.add_column(sa.Column('evaluation_period_end', sa.DateTime(), nullable=True))
        if 'overlap_detected' not in eval_cols:
            batch_op.add_column(sa.Column('overlap_detected', sa.Boolean(), server_default='0', nullable=False))
        if 'eligible_for_h1' not in eval_cols:
            batch_op.add_column(sa.Column('eligible_for_h1', sa.Boolean(), server_default='0', nullable=False))
        if 'data_coverage_pct' not in eval_cols:
            batch_op.add_column(sa.Column('data_coverage_pct', sa.Float(), nullable=True))

def downgrade() -> None:
    with op.batch_alter_table('evaluation_runs') as batch_op:
        batch_op.drop_column('data_coverage_pct')
        batch_op.drop_column('eligible_for_h1')
        batch_op.drop_column('overlap_detected')
        batch_op.drop_column('evaluation_period_end')
        batch_op.drop_column('evaluation_period_start')
        batch_op.drop_column('calibration_period_end')
        batch_op.drop_column('calibration_period_start')

    with op.batch_alter_table('simulations') as batch_op:
        batch_op.drop_column('simulation_start_date')
        batch_op.drop_column('artifact_sha256_used')
        batch_op.drop_column('effective_parameters_json')

    op.drop_table('sobol_tasks')
    op.drop_table('dataset_observations')
