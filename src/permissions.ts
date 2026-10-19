import { UserRole } from './types';

export type ModuleId =
  | 'user_security'
  | 'data_preparation'
  | 'digital_twin_model'
  | 'evaluation_validation'
  | 'scenario_deployment'
  | 'reporting'
  | 'dashboard'
  | 'data_integration'
  | 'hybrid_arch'
  | 'validation'
  | 'simulation'
  | 'comparator'
  | 'sensitivity'
  | '3d_view'
  | 'reports'
  | 'api_docs'
  | 'admin'
  | 'model_monitoring'
  | 'weekly_forecasting'
  | 'data_assistant'
  | 'langchain_agent'
  | 'langflow_assistant'
  | 'evidence_route'
  | 'articulo_cientifico';

export type ActionId =
  | 'run_simulation'
  | 'export_report'
  | 'modify_params'
  | 'admin_audit'
  | 'ai_copilot';

// Module access per role
export const MODULE_ACCESS: Record<ModuleId, UserRole[]> = {
  // Metodología CRISP-DM & Módulos Transversales
  user_security: ['admin', 'epidemiologist', 'analyst', 'policy_analyst'],
  data_preparation: ['admin', 'epidemiologist'],
  digital_twin_model: ['admin', 'epidemiologist', 'analyst', 'policy_analyst'],
  evaluation_validation: ['admin', 'epidemiologist', 'analyst', 'policy_analyst'],
  scenario_deployment: ['admin', 'epidemiologist', 'analyst', 'policy_analyst'],
  reporting: ['admin', 'epidemiologist', 'analyst', 'policy_analyst', 'viewer'],
  model_monitoring: ['admin', 'epidemiologist', 'analyst', 'policy_analyst'],
  weekly_forecasting: ['admin', 'epidemiologist', 'analyst', 'policy_analyst', 'viewer'],
  data_assistant: ['admin', 'epidemiologist', 'analyst', 'policy_analyst', 'viewer'],
  langchain_agent: ['admin', 'epidemiologist', 'analyst', 'policy_analyst', 'viewer'],
  langflow_assistant: ['admin', 'epidemiologist', 'analyst', 'policy_analyst', 'viewer'],
  evidence_route: ['admin', 'epidemiologist', 'analyst', 'policy_analyst', 'viewer'],
  articulo_cientifico: ['admin', 'epidemiologist', 'analyst', 'policy_analyst', 'viewer'],

  // Vistas auxiliares
  dashboard: ['admin', 'epidemiologist', 'analyst', 'policy_analyst', 'viewer'],
  data_integration: ['admin', 'epidemiologist'],
  hybrid_arch: ['admin', 'epidemiologist', 'analyst', 'policy_analyst'],
  validation: ['admin', 'epidemiologist', 'analyst', 'policy_analyst'],
  simulation: ['admin', 'epidemiologist', 'analyst', 'policy_analyst'],
  comparator: ['admin', 'epidemiologist', 'analyst', 'policy_analyst'],
  sensitivity: ['admin', 'epidemiologist'],
  '3d_view': ['admin', 'epidemiologist', 'analyst', 'policy_analyst', 'viewer'],
  reports: ['admin', 'epidemiologist', 'analyst', 'policy_analyst'],
  api_docs: ['admin', 'epidemiologist'],
  admin: ['admin'],
};

// Action access per role
export const ACTION_ACCESS: Record<ActionId, UserRole[]> = {
  run_simulation: ['admin', 'epidemiologist', 'analyst', 'policy_analyst'],
  export_report: ['admin', 'epidemiologist', 'analyst', 'policy_analyst'],
  modify_params: ['admin', 'epidemiologist'],
  admin_audit: ['admin'],
  ai_copilot: ['admin', 'epidemiologist', 'analyst', 'policy_analyst', 'viewer'],
};

export function canAccessModule(role: UserRole, module: ModuleId): boolean {
  return MODULE_ACCESS[module]?.includes(role) ?? false;
}

export function canAccessAction(role: UserRole, action: ActionId): boolean {
  return ACTION_ACCESS[action]?.includes(role) ?? false;
}
