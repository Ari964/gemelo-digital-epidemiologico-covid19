"""Traceability, Monitoring, Evaluation and Active Deployment Schema

Revision ID: 002_traceability_monitoring_evaluation
Revises: 001_initial_schema
Create Date: 2026-09-17

"""
from alembic import op
import sqlalchemy as sa

revision = '002_traceability_monitoring_evaluation'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None

def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # 1. Datasets: Add provenance fields with conservative defaults (PENDING, UNKNOWN)
    dataset_cols = [c['name'] for c in inspector.get_columns('datasets')]
    with op.batch_alter_table('datasets') as batch_op:
        if 'dataset_version' not in dataset_cols:
            batch_op.add_column(sa.Column('dataset_version', sa.String(length=32), server_default='v1.0.0', nullable=False))
        if 'source_type' not in dataset_cols:
            batch_op.add_column(sa.Column('source_type', sa.String(length=32), server_default='UNKNOWN', nullable=False))
        if 'source_name' not in dataset_cols:
            batch_op.add_column(sa.Column('source_name', sa.String(length=128), nullable=True))
        if 'source_reference' not in dataset_cols:
            batch_op.add_column(sa.Column('source_reference', sa.String(length=256), nullable=True))
        if 'period_start' not in dataset_cols:
            batch_op.add_column(sa.Column('period_start', sa.DateTime(), nullable=True))
        if 'period_end' not in dataset_cols:
            batch_op.add_column(sa.Column('period_end', sa.DateTime(), nullable=True))
        if 'ingested_at' not in dataset_cols:
            batch_op.add_column(sa.Column('ingested_at', sa.DateTime(), server_default=sa.func.now(), nullable=True))
        if 'content_sha256' not in dataset_cols:
            batch_op.add_column(sa.Column('content_sha256', sa.String(length=64), nullable=True))
        if 'quality_status' not in dataset_cols:
            batch_op.add_column(sa.Column('quality_status', sa.String(length=32), server_default='PENDING', nullable=False))
        if 'validation_issues_json' not in dataset_cols:
            batch_op.add_column(sa.Column('validation_issues_json', sa.Text(), server_default='[]', nullable=True))

    # 2. Simulation Runs: Add operational vs experimental traceability
    sim_cols = [c['name'] for c in inspector.get_columns('simulations')]
    with op.batch_alter_table('simulations') as batch_op:
        if 'model_version' not in sim_cols:
            batch_op.add_column(sa.Column('model_version', sa.String(length=32), nullable=True))
        if 'dataset_id' not in sim_cols:
            batch_op.add_column(sa.Column('dataset_id', sa.String(length=64), nullable=True))
        if 'run_mode' not in sim_cols:
            batch_op.add_column(sa.Column('run_mode', sa.String(length=32), server_default='EXPERIMENTAL', nullable=False))
        if 'is_operational' not in sim_cols:
            batch_op.add_column(sa.Column('is_operational', sa.Boolean(), server_default='0', nullable=False))
        if 'is_demo' not in sim_cols:
            batch_op.add_column(sa.Column('is_demo', sa.Boolean(), server_default='0', nullable=False))
        if 'daily_series_json' not in sim_cols:
            batch_op.add_column(sa.Column('daily_series_json', sa.Text(), nullable=True))

    # 3. Model Registry Table: create if missing, or alter if exists
    if 'model_registry' not in existing_tables:
        op.create_table(
            'model_registry',
            sa.Column('id', sa.String(length=64), primary_key=True),
            sa.Column('version', sa.String(length=32), unique=True, nullable=False),
            sa.Column('name', sa.String(length=128), nullable=False),
            sa.Column('file_path', sa.String(length=256), nullable=False),
            sa.Column('file_sha256', sa.String(length=64), nullable=False),
            sa.Column('technical_approval', sa.Boolean(), server_default='0', nullable=False),
            sa.Column('technical_approved_by', sa.String(length=128), nullable=True),
            sa.Column('technical_approved_at', sa.DateTime(), nullable=True),
            sa.Column('h1_status', sa.String(length=32), server_default='PENDING', nullable=False),
            sa.Column('h1_evaluation_json', sa.Text(), server_default='{}', nullable=True),
            sa.Column('metrics_json', sa.Text(), server_default='{}', nullable=True),
            sa.Column('evaluation_id', sa.String(length=64), nullable=True),
            sa.Column('parameters_json', sa.Text(), server_default='{}', nullable=True),
            sa.Column('is_active', sa.Boolean(), server_default='0', nullable=False),
            sa.Column('activated_at', sa.DateTime(), nullable=True),
            sa.Column('activated_by', sa.String(length=128), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False)
        )
    else:
        mr_cols = [c['name'] for c in inspector.get_columns('model_registry')]
        with op.batch_alter_table('model_registry') as batch_op:
            if 'evaluation_id' not in mr_cols:
                batch_op.add_column(sa.Column('evaluation_id', sa.String(length=64), nullable=True))
            if 'parameters_json' not in mr_cols:
                batch_op.add_column(sa.Column('parameters_json', sa.Text(), server_default='{}', nullable=True))
            if 'is_active' not in mr_cols:
                batch_op.add_column(sa.Column('is_active', sa.Boolean(), server_default='0', nullable=False))
            if 'activated_at' not in mr_cols:
                batch_op.add_column(sa.Column('activated_at', sa.DateTime(), nullable=True))
            if 'activated_by' not in mr_cols:
                batch_op.add_column(sa.Column('activated_by', sa.String(length=128), nullable=True))

    # 4. Evaluation Runs Table
    if 'evaluation_runs' not in existing_tables:
        op.create_table(
            'evaluation_runs',
            sa.Column('id', sa.String(length=64), primary_key=True),
            sa.Column('candidate_simulation_id', sa.String(length=64), nullable=False),
            sa.Column('baseline_simulation_id', sa.String(length=64), nullable=True),
            sa.Column('candidate_version', sa.String(length=32), nullable=True),
            sa.Column('baseline_version', sa.String(length=32), nullable=True),
            sa.Column('candidate_params_json', sa.Text(), server_default='{}', nullable=True),
            sa.Column('baseline_params_json', sa.Text(), server_default='{}', nullable=True),
            sa.Column('observed_dataset_id', sa.String(length=64), nullable=False),
            sa.Column('observed_dataset_version', sa.String(length=32), server_default='v1.0.0', nullable=True),
            sa.Column('source_type', sa.String(length=32), nullable=False),
            sa.Column('sources_used_json', sa.Text(), server_default='[]', nullable=True),
            sa.Column('period_start', sa.DateTime(), nullable=True),
            sa.Column('period_end', sa.DateTime(), nullable=True),
            sa.Column('territory_scope', sa.String(length=64), server_default='Kenya (47 Counties)', nullable=True),
            sa.Column('aggregation_level', sa.String(length=32), server_default='National Daily Aggregated', nullable=True),
            sa.Column('target_variable', sa.String(length=64), server_default='daily_cases', nullable=True),
            sa.Column('target_unit', sa.String(length=32), server_default='count', nullable=True),
            sa.Column('observations_count', sa.Integer(), server_default='0', nullable=False),
            sa.Column('zeros_count', sa.Integer(), server_default='0', nullable=False),
            sa.Column('missing_count', sa.Integer(), server_default='0', nullable=False),
            sa.Column('exclusions_count', sa.Integer(), server_default='0', nullable=False),
            sa.Column('zero_handling_method', sa.String(length=64), server_default='epsilon_zero_avoidance_documented', nullable=True),
            sa.Column('mape_candidate', sa.Float(), nullable=True),
            sa.Column('mape_baseline', sa.Float(), nullable=True),
            sa.Column('delta_mape_pp', sa.Float(), nullable=True),
            sa.Column('rmse_candidate', sa.Float(), nullable=True),
            sa.Column('rmse_baseline', sa.Float(), nullable=True),
            sa.Column('r2_candidate', sa.Float(), nullable=True),
            sa.Column('r2_baseline', sa.Float(), nullable=True),
            sa.Column('wilcoxon_stat', sa.Float(), nullable=True),
            sa.Column('wilcoxon_p_value', sa.Float(), nullable=True),
            sa.Column('h1_supported', sa.Boolean(), server_default='0', nullable=False),
            sa.Column('h1_status', sa.String(length=32), server_default='PENDING', nullable=False),
            sa.Column('scientific_conclusion', sa.Text(), nullable=True),
            sa.Column('is_demo', sa.Boolean(), server_default='0', nullable=False),
            sa.Column('unavailability_reason', sa.Text(), nullable=True),
            sa.Column('evaluated_by', sa.String(length=128), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False)
        )
        op.create_index('ix_evaluation_runs_candidate', 'evaluation_runs', ['candidate_simulation_id'])
        op.create_index('ix_evaluation_runs_created_at', 'evaluation_runs', ['created_at'])

    # 5. Active Model Deployment Singleton Table
    if 'active_model_deployment' not in existing_tables:
        op.create_table(
            'active_model_deployment',
            sa.Column('singleton_id', sa.Integer(), primary_key=True, server_default='1'),
            sa.Column('active_version', sa.String(length=32), nullable=False),
            sa.Column('model_name', sa.String(length=128), nullable=False),
            sa.Column('artifact_sha256', sa.String(length=64), nullable=False),
            sa.Column('deployed_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('deployed_by', sa.String(length=128), nullable=False),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.CheckConstraint('singleton_id = 1', name='chk_single_active_model_deployment')
        )

    # 6. Model Activations History Table
    if 'model_activations' not in existing_tables:
        op.create_table(
            'model_activations',
            sa.Column('id', sa.String(length=64), primary_key=True),
            sa.Column('version', sa.String(length=32), nullable=False),
            sa.Column('action', sa.String(length=32), server_default='ACTIVATE', nullable=False),
            sa.Column('previous_version', sa.String(length=32), nullable=True),
            sa.Column('activated_by', sa.String(length=128), nullable=False),
            sa.Column('activated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('notes', sa.Text(), nullable=True)
        )
        op.create_index('ix_model_activations_version', 'model_activations', ['version'])
        op.create_index('ix_model_activations_activated_at', 'model_activations', ['activated_at'])

    # 7. Model Monitoring Logs Table
    if 'model_monitoring_logs' not in existing_tables:
        op.create_table(
            'model_monitoring_logs',
            sa.Column('id', sa.String(length=64), primary_key=True),
            sa.Column('model_version', sa.String(length=32), nullable=False),
            sa.Column('reference_dataset_id', sa.String(length=64), nullable=False),
            sa.Column('current_dataset_id', sa.String(length=64), nullable=False),
            sa.Column('time_window_start', sa.DateTime(), nullable=True),
            sa.Column('time_window_end', sa.DateTime(), nullable=True),
            sa.Column('availability_status', sa.String(length=32), server_default='PENDING', nullable=False),
            sa.Column('severity_status', sa.String(length=32), nullable=True),
            sa.Column('unavailability_reason', sa.Text(), nullable=True),
            sa.Column('variables_analyzed_json', sa.Text(), server_default='[]', nullable=True),
            sa.Column('sample_size_reference', sa.Integer(), nullable=True),
            sa.Column('sample_size_current', sa.Integer(), nullable=True),
            sa.Column('psi_metrics_json', sa.Text(), server_default='[]', nullable=True),
            sa.Column('ks_metrics_json', sa.Text(), server_default='[]', nullable=True),
            sa.Column('performance_metrics_json', sa.Text(), server_default='{}', nullable=True),
            sa.Column('alerts_json', sa.Text(), server_default='[]', nullable=True),
            sa.Column('recommendation', sa.Text(), nullable=True),
            sa.Column('evaluated_by', sa.String(length=128), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False)
        )
        op.create_index('ix_monitoring_version', 'model_monitoring_logs', ['model_version'])
        op.create_index('ix_monitoring_created_at', 'model_monitoring_logs', ['created_at'])

def downgrade() -> None:
    op.drop_table('model_monitoring_logs')
    op.drop_table('model_activations')
    op.drop_table('active_model_deployment')
    op.drop_table('evaluation_runs')
    with op.batch_alter_table('model_registry') as batch_op:
        batch_op.drop_column('activated_by')
        batch_op.drop_column('activated_at')
        batch_op.drop_column('is_active')
        batch_op.drop_column('parameters_json')
        batch_op.drop_column('evaluation_id')
    with op.batch_alter_table('simulations') as batch_op:
        batch_op.drop_column('daily_series_json')
        batch_op.drop_column('is_demo')
        batch_op.drop_column('is_operational')
        batch_op.drop_column('run_mode')
        batch_op.drop_column('dataset_id')
        batch_op.drop_column('model_version')
    with op.batch_alter_table('datasets') as batch_op:
        batch_op.drop_column('validation_issues_json')
        batch_op.drop_column('quality_status')
        batch_op.drop_column('content_sha256')
        batch_op.drop_column('ingested_at')
        batch_op.drop_column('period_end')
        batch_op.drop_column('period_start')
        batch_op.drop_column('source_reference')
        batch_op.drop_column('source_name')
        batch_op.drop_column('source_type')
        batch_op.drop_column('dataset_version')
