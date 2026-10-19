/**
 * API Contract Types matching FastAPI /api/v1 schemas (CRISP-DM Fases 1-6)
 */

export interface UserDTO {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'epidemiologist' | 'analyst';
  status: 'active' | 'suspended';
  created_at: string;
}

export interface TokenResponseDTO {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user_id: string;
  email: string;
  name: string;
  role: 'admin' | 'epidemiologist' | 'analyst';
}

export interface CountyDTO {
  code: number;
  iso_code: string;
  name: string;
  capital: string;
  population_2019: number;
  area_sq_km: number;
  latitude: number;
  longitude: number;
  poverty_quintiles: {
    q1: number;
    q2: number;
    q3: number;
    q4: number;
    q5: number;
  };
  icu_beds_verified: number | null;
  icu_source: string | null;
  data_quality_flags: string[];
}

export interface SimulationParamsDTO {
  days: number;
  npi_stringency: number;
  vaccine_coverage: number;
  school_closure: boolean;
  border_screening: boolean;
  initial_infected_county: number;
  initial_cases: number;
  use_empirical_mobility: boolean;
  seed: number;
  run_mode?: 'EXPERIMENTAL' | 'OPERATIONAL';
  model_version?: string;
}

export interface SimulationResponseDTO {
  simulation_id: string;
  model_type: string;
  is_synthetic: boolean;
  is_demo?: boolean;
  run_mode?: string;
  model_version?: string;
  is_operational?: boolean;
  warning: string | null;
  execution_time_ms: number;
  parameters_hash: string;
  seed: number;
  national_summary: {
    total_cases: number;
    total_deaths: number;
    peak_infections: number;
    peak_day: number;
    attack_rate: number;
  };
  national_time_series: {
    daily_cases: number[];
    active_infected: number[];
    cumulative_deaths: number[];
  };
  county_results: Array<{
    code: number;
    name: string;
    population: number;
    total_cases: number;
    total_deaths: number;
    peak_infected: number;
    peak_day: number;
    icu_beds_verified: number | null;
    icu_saturated: boolean;
    daily_cases: number[];
  }>;
  household_equity: {
    demographic_parity_ratio: number;
    attack_rate_by_quintile: Record<string, number>;
    equity_assessment: string;
  };
  health_economics: {
    dalys_total: number;
    yll: number;
    yld: number;
    intervention_cost_usd: number;
    intervention_cost_kes: number;
    currency_rates: { USD_KES: number };
  };
}

export interface AuditLogDTO {
  id: string;
  timestamp: string;
  user_id: string;
  user_email: string;
  user_role: string;
  action: string;
  parameters_hash: string;
  seed: number;
  execution_time_ms: number;
  details?: string;
}

export interface ValidationStatusDTO {
  external_validation_2023_2024: {
    period: string;
    status: 'PENDING' | 'AVAILABLE';
    dataset_available: boolean;
    note: string;
    mape: number | null;
    rmse: number | null;
    r2: number | null;
    records_count: number;
  };
  datasets: Array<{
    name: string;
    source: string;
    source_type?: string;
    quality_status?: string;
    is_synthetic: boolean;
    records_count: number;
    coverage_pct: number;
    sha256_hash?: string;
  }>;
  h1_criteria: {
    hypothesis: string;
    condition: string;
    benchmark: string;
  };
  technical_approval_gate: {
    min_coverage_pct: number;
    prohibit_synthetic: boolean;
    min_r2: number;
  };
}

export interface EvaluationResponseDTO {
  id: string;
  candidate_sim_id: string;
  baseline_sim_id: string;
  candidate_model_name: string;
  candidate_model_version: string;
  baseline_model_name: string;
  baseline_model_version: string;
  observed_dataset_id: string;
  observed_dataset_version: string;
  observed_dataset_hash: string | null;
  sources_used: string[];
  period_start: string | null;
  period_end: string | null;
  territory_scope: string;
  aggregation_level: string;
  target_variable: string;
  target_unit: string;
  observations_count: number;
  zero_policy: string;
  exclusions_count: number;
  is_demo: boolean;
  unavailability_reason: string | null;
  mape: number | null;
  rmse: number | null;
  r2: number | null;
  wilcoxon_p_value: number | null;
  wilcoxon_statistic: number | null;
  psi_value: number | null;
  psi_status: string | null;
  ks_statistic: number | null;
  ks_p_value: number | null;
  h1_status: string;
  h1_supported: boolean;
  technical_approval_status: string;
  created_at: string;
}

export interface ActiveModelResponseDTO {
  is_active: boolean;
  model_name?: string;
  model_version?: string;
  artifact_sha256?: string;
  activated_at?: string;
  activated_by?: string;
  candidate_eval_id?: string;
  parameters?: Record<string, any>;
  message?: string;
}

export interface MonitoringStatusDTO {
  active_model_name: string | null;
  active_model_version: string | null;
  is_active: boolean;
  overall_status: 'HEALTHY' | 'WARNING' | 'CRITICAL' | 'PENDING';
  last_evaluated_at: string | null;
  unavailability_reason: string | null;
  psi_value: number | null;
  psi_status: string | null;
  ks_p_value: number | null;
  ks_status: string | null;
}

export interface SobolStatusDTO {
  analysis_id: string;
  status: 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'INTERRUPTED';
  progress_pct: number;
  model_engine: string;
  n_samples: number;
  calc_second_order: boolean;
  seed: number;
  sobol_indices: Array<{
    parameter: string;
    S1: number;
    S1_conf: number;
    ST: number;
    ST_conf: number;
  }>;
  second_order_indices?: Array<{
    param1: string;
    param2: string;
    S2: number;
    S2_conf: number;
  }>;
  most_sensitive_parameter?: string;
  error_message?: string;
}

export interface HistoricalCutoffItemDTO {
  date: string;
  new_cases_reported: number;
  new_cases_smoothed: number;
  new_deaths: number;
  target_next_week_cases?: number;
}

export interface HistoricalCutoffsDTO {
  dataset_source: string;
  count: number;
  available_cutoffs: HistoricalCutoffItemDTO[];
  recommended_test_case: {
    cutoff_date: string;
    next_week_observed: number;
    naive_persistence_prediction: number;
    random_forest_prediction: number;
    explanation: string;
  };
}

export interface WeeklyPredictionResponseDTO {
  cutoff_date: string;
  target_week: string;
  geographic_scope: string;
  primary_model_name: string;
  primary_forecast_cases: number;
  primary_forecast_source: string;
  target_observed_actual: number | null;
  forecast_error_mae: number | null;
  hypothetical_rf_prediction: number | null;
  sensitivity_disclaimer: string;
  validation_details: Record<string, any>;
}

export interface DataAssistantResponseDTO {
  query: string;
  database_observations: Record<string, any>;
  model_forecasts: Record<string, any>;
  ai_interpretation: string;
  tools_used: string[];
  sources_consulted: string[];
}

export interface FoldMetricDTO {
  fold: number;
  train_start_date: string;
  train_end_date: string;
  val_start_date: string;
  val_end_date: string;
  train_samples: number;
  val_samples: number;
  val_rmse: number;
  val_mae: number;
}

export interface ModelEvaluationDetailDTO {
  model_name: string;
  role: 'PREDICTIVE_CHAMPION' | 'SENSITIVITY_EXPLORATION' | 'TEST_BENCHMARK' | 'COMPARATIVE';
  cv_rmse_5fold: number;
  hyperparameter_space: Record<string, any>;
  best_params: Record<string, any>;
  fold_metrics: FoldMetricDTO[];
  dev_metrics: {
    rmse: number;
    mae: number;
    mape: number;
    r2: number;
  };
  test_metrics: {
    rmse: number;
    mae: number;
    mape: number;
    r2: number;
  };
  training_time_sec: number;
  inference_time_ms: number;
  allows_npi_simulation: boolean;
}

export interface StatisticalTestDTO {
  test_name: string;
  h0: string;
  h1?: string;
  h1_two_sided?: string;
  h1_one_sided?: string;
  statistic?: number;
  statistic_w?: number;
  statistic_dm_hln?: number;
  statistic_ks?: number;
  mean_loss_diff_mae?: number;
  p_value?: number;
  p_value_two_sided?: number;
  p_value_two_sided_formatted?: string;
  p_value_one_sided?: number;
  p_value_one_sided_formatted?: string;
  is_normal?: boolean;
  conclusion?: string;
  interpretation?: string;
  caveat?: string;
  sample_size?: number;
}

export interface WeeklyModelEvaluationDTO {
  generated_at: string;
  task_name: string;
  source: string;
  raw_data_sha256: string;
  temporal_protocol: {
    canonical_frequency: string;
    forecast_horizon: string;
    dev_period: string;
    test_period: string;
    cv_method: string;
    selection_rule: string;
  };
  models: Record<string, ModelEvaluationDetailDTO>;
  statistical_tests: {
    shapiro_wilk: StatisticalTestDTO;
    diebold_mariano_hln: StatisticalTestDTO;
    wilcoxon_paired: StatisticalTestDTO;
    kolmogorov_smirnov: StatisticalTestDTO;
  };
  untested_comparisons: Record<string, {
    status: string;
    scientific_rationale: string;
  }>;
  test_series_data: Array<{
    date: string;
    observed: number;
    naive_persistence: number;
    candidate_random_forest: number;
    baseline_ridge: number;
  }>;
}

export interface LangflowStatusDTO {
  status: 'ONLINE' | 'OFFLINE' | 'DEGRADED' | 'NO_FLOW' | string;
  connected: boolean;
  service_available?: boolean;
  flow_imported?: boolean;
  url: string;
  flow_id: string;
  flow_name: string;
  provider: string;
  latency_ms: number | null;
  error: string | null;
}

export interface LangflowResponseDTO {
  reply: string;
  flow_id: string;
  flow_name: string;
  session_id: string;
  execution_time_ms: number;
  status: string;
}


