/**
 * API Client strictly targeting FastAPI production backend at /api/v1
 */

import { 
  TokenResponseDTO, 
  UserDTO, 
  CountyDTO, 
  SimulationParamsDTO, 
  SimulationResponseDTO, 
  AuditLogDTO, 
  ValidationStatusDTO,
  EvaluationResponseDTO,
  ActiveModelResponseDTO,
  MonitoringStatusDTO,
  SobolStatusDTO,
  HistoricalCutoffsDTO,
  WeeklyPredictionResponseDTO,
  DataAssistantResponseDTO,
  WeeklyModelEvaluationDTO,
  LangflowStatusDTO,
  LangflowResponseDTO
} from '../types/apiContract';

const API_BASE = '/api/v1';

export class ApiClient {
  private static tokenKey = 'gdti_jwt_token';
  private static refreshKey = 'gdti_refresh_token';

  static getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  static setTokens(access: string, refresh: string) {
    localStorage.setItem(this.tokenKey, access);
    localStorage.setItem(this.refreshKey, refresh);
  }

  static clearTokens() {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.refreshKey);
  }

  private static getHeaders(isJson: boolean = true): HeadersInit {
    const headers: HeadersInit = {};
    if (isJson) headers['Content-Type'] = 'application/json';
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  static async login(email: string, password: string): Promise<TokenResponseDTO> {
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) {
        let errDetail = '';
        try {
          const err = await res.json();
          errDetail = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail || '');
        } catch (_) {}

        if (res.status === 401) {
          throw new Error('Credenciales incorrectas: El correo electrónico o contraseña no coinciden con ninguna cuenta autorizada en la base de datos.');
        } else if (res.status === 500) {
          const lowerDetail = errDetail.toLowerCase();
          if (lowerDetail.includes('database') || lowerDetail.includes('sql') || lowerDetail.includes('postgres') || lowerDetail.includes('connection')) {
            throw new Error(`Problema de base de datos (HTTP 500): Fallo de conexión o consulta en PostgreSQL. ${errDetail}`);
          }
          throw new Error(`Error del servidor (HTTP 500): ${errDetail || 'Fallo interno no controlado en el backend FastAPI.'}`);
        } else if (res.status === 502 || res.status === 503 || res.status === 504) {
          throw new Error(`Backend desconectado o no disponible (HTTP ${res.status}): El proxy de red no puede contactar a FastAPI.`);
        } else {
          throw new Error(errDetail || `Error de autenticación (HTTP ${res.status})`);
        }
      }
      const data: TokenResponseDTO = await res.json();
      this.setTokens(data.access_token, data.refresh_token);
      return data;
    } catch (networkErr: any) {
      if (networkErr.message && (
        networkErr.message.includes('Credenciales') || 
        networkErr.message.includes('servidor') || 
        networkErr.message.includes('base de datos') || 
        networkErr.message.includes('Backend')
      )) {
        throw networkErr;
      }
      console.error('[API Connection Error]', networkErr);
      throw new Error('Backend desconectado: No se pudo establecer comunicación con el backend FastAPI (/api/v1). Verifique que FastAPI esté encendido en el puerto 8000 o que el proxy Docker esté activo.');
    }
  }

  static async getMe(): Promise<UserDTO> {
    const res = await fetch(`${API_BASE}/users/me`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Error al obtener usuario actual');
    return res.json();
  }

  static async getCounties(): Promise<CountyDTO[]> {
    const res = await fetch(`${API_BASE}/counties/`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Error al cargar condados verificados');
    return res.json();
  }

  static async runSimulation(params: SimulationParamsDTO): Promise<SimulationResponseDTO> {
    const res = await fetch(`${API_BASE}/simulations/run`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(params),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error en simulación' }));
      throw new Error(err.detail || 'Fallo al ejecutar simulación');
    }
    return res.json();
  }

  static async getSimulationHistory(limit: number = 20): Promise<any[]> {
    const res = await fetch(`${API_BASE}/simulations/history?limit=${limit}`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Error al cargar historial de simulaciones');
    return res.json();
  }

  static async getAuditLogs(limit: number = 100): Promise<AuditLogDTO[]> {
    const res = await fetch(`${API_BASE}/audit-logs/?limit=${limit}`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Error al cargar bitácora de auditoría');
    return res.json();
  }

  static async exportPdf(payload: any): Promise<Blob> {
    const res = await fetch(`${API_BASE}/reports/export/pdf`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Error al generar reporte PDF');
    return res.blob();
  }

  static async getReportPreview(reportType: string, language: string = 'es', params: any = {}): Promise<any> {
    const res = await fetch(`${API_BASE}/reports/preview`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ report_type: reportType, language, params }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error al generar vista previa' }));
      throw new Error(err.detail || 'Fallo en vista previa del reporte');
    }
    return res.json();
  }

  static async exportReportPdf(reportType: string, language: string = 'es', params: any = {}): Promise<Blob> {
    const res = await fetch(`${API_BASE}/reports/export/pdf`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ report_type: reportType, language, params }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error al compilar PDF (ReportLab)' }));
      throw new Error(err.detail || 'Fallo en exportación PDF');
    }
    return res.blob();
  }

  static async exportReportExcel(reportType: string, language: string = 'es', params: any = {}): Promise<Blob> {
    const res = await fetch(`${API_BASE}/reports/export/excel`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ report_type: reportType, language, params }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error al compilar Excel (OpenPyXL)' }));
      throw new Error(err.detail || 'Fallo en exportación Excel');
    }
    return res.blob();
  }

  static async exportPdfById(payload: { simulation_id?: string; evaluation_id?: string; title?: string }): Promise<Blob> {
    const res = await fetch(`${API_BASE}/reports/export/by-id/pdf`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error al generar reporte por ID' }));
      throw new Error(err.detail || 'Fallo al exportar reporte por ID');
    }
    return res.blob();
  }

  static async exportExcel(payload: any): Promise<Blob> {
    const res = await fetch(`${API_BASE}/reports/export/excel`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Error al generar reporte Excel');
    return res.blob();
  }

  static async getUsers(): Promise<UserDTO[]> {
    const res = await fetch(`${API_BASE}/users/`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Error al obtener lista de usuarios');
    return res.json();
  }

  static async createUser(userData: any): Promise<UserDTO> {
    const res = await fetch(`${API_BASE}/users/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(userData),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error al crear usuario' }));
      throw new Error(err.detail || 'Error al crear usuario');
    }
    return res.json();
  }

  static async updateUser(userId: string, userData: any): Promise<any> {
    const res = await fetch(`${API_BASE}/users/${userId}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(userData),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error al actualizar usuario' }));
      throw new Error(err.detail || 'Error al actualizar usuario');
    }
    return res.json();
  }

  static async deleteUser(userId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/users/${userId}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Error al eliminar usuario');
    return res.json();
  }

  static async getDatasets(): Promise<any> {
    const res = await fetch(`${API_BASE}/data/datasets`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Error al cargar datasets');
    return res.json();
  }

  static async generateSyntheticData(): Promise<any> {
    const res = await fetch(`${API_BASE}/data/synthetic-generate`, {
      method: 'POST',
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Error al ejecutar pipeline ETL');
    return res.json();
  }

  static async getValidationExternal(): Promise<any> {
    const res = await fetch(`${API_BASE}/validation/external`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Error al consultar validación externa');
    return res.json();
  }

  static async getWeeklyModelEvaluation(): Promise<WeeklyModelEvaluationDTO> {
    const res = await fetch(`${API_BASE}/validation/weekly-evaluation`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Error al consultar evaluación de modelos semanales');
    return res.json();
  }

  // --- Endpoints CRISP-DM Fase 5 y 6 ---

  static async getEvaluations(): Promise<EvaluationResponseDTO[]> {
    const res = await fetch(`${API_BASE}/validation/evaluations`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Error al obtener evaluaciones científicas');
    return res.json();
  }

  static async getActiveModel(): Promise<ActiveModelResponseDTO> {
    const res = await fetch(`${API_BASE}/validation/active-model`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Error al consultar modelo activo');
    return res.json();
  }

  static async getMonitoringStatus(): Promise<MonitoringStatusDTO> {
    const res = await fetch(`${API_BASE}/monitoring/status`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Error al consultar estado de monitoreo');
    return res.json();
  }

  static async triggerManualMonitoring(notes: string = "Evaluación manual solicitada desde consola"): Promise<MonitoringStatusDTO> {
    const res = await fetch(`${API_BASE}/monitoring/evaluate`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ notes }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error al ejecutar monitoreo' }));
      throw new Error(err.detail || 'Fallo en evaluación de monitoreo');
    }
    return res.json();
  }

  static async launchSobolAnalysis(nSamples: number = 128, calcSecondOrder: boolean = false): Promise<SobolStatusDTO> {
    const res = await fetch(`${API_BASE}/analytics/sobol`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ n_samples: nSamples, calc_second_order: calcSecondOrder }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error al lanzar análisis de Sobol' }));
      throw new Error(err.detail || 'Fallo al iniciar Sobol');
    }
    return res.json();
  }

  static async getSobolStatus(analysisId: string): Promise<SobolStatusDTO> {
    const res = await fetch(`${API_BASE}/analytics/sobol/${analysisId}`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Error al consultar estado de Sobol');
    return res.json();
  }

  static async chatAi(message: string, context?: any): Promise<{ reply: string; model: string }> {
    const res = await fetch(`${API_BASE}/ai/chat`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ message, simulation_context: context }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error en el servicio de IA' }));
      throw new Error(err.detail || 'Servicio de IA temporalmente no disponible');
    }
    return res.json();
  }

  // --- Endpoints Fase 2: Vigilancia Semanal y Asistente de Datos ---

  static async getHistoricalCutoffs(): Promise<HistoricalCutoffsDTO> {
    const res = await fetch(`${API_BASE}/predictions/historical-cutoffs`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Error al consultar cortes históricos de predicción');
    return res.json();
  }

  static async getWeeklyPrediction(cutoffDate: string = "2024-07-28", countyCode: number = 0): Promise<WeeklyPredictionResponseDTO> {
    const res = await fetch(`${API_BASE}/predictions/weekly`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ cutoff_date: cutoffDate, county_code: countyCode }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error al generar predicción semanal' }));
      throw new Error(err.detail || 'Fallo al ejecutar predicción');
    }
    return res.json();
  }

  static async queryDataAssistant(query: string, cutoffDate?: string, countyCode?: number): Promise<DataAssistantResponseDTO> {
    const res = await fetch(`${API_BASE}/data-assistant/query`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ query, cutoff_date: cutoffDate, county_code: countyCode ?? 0 }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error al consultar Asistente de Datos' }));
      throw new Error(err.detail || 'Fallo en Asistente de Datos');
    }
    return res.json();
  }

  static async getLangflowStatus(): Promise<LangflowStatusDTO> {
    const res = await fetch(`${API_BASE}/langflow/status`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Error al consultar estado de Langflow');
    return res.json();
  }

  static async importLangflowFlow(): Promise<any> {
    const res = await fetch(`${API_BASE}/langflow/import-flow`, {
      method: 'POST',
      headers: this.getHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error al importar flujo en Langflow' }));
      throw new Error(err.detail || 'Fallo al importar flujo');
    }
    return res.json();
  }

  static async queryLangflow(query: string, sessionId?: string): Promise<LangflowResponseDTO> {
    const res = await fetch(`${API_BASE}/langflow/query`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ query, session_id: sessionId }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error al consultar Langflow' }));
      throw new Error(err.detail || 'Fallo en servicio Langflow');
    }
    return res.json();
  }

  static async queryLangChainAgent(query: string, cutoffDate?: string, countyCode: number = 0, lang: string = 'es'): Promise<any> {
    const res = await fetch(`${API_BASE}/langchain-agent/query`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ query, cutoff_date: cutoffDate, county_code: countyCode, lang }),
    });
    if (!res.ok) {
      let errDetail = '';
      try {
        const err = await res.json();
        errDetail = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail);
      } catch (_) {
        errDetail = await res.text();
      }
      throw new Error(errDetail || `Error ${res.status}: Fallo en servicio LangChain`);
    }
    return res.json();
  }

  // --- Endpoints del Artículo Científico (Protocolo V2.0) ---

  static async getArticuloResultados(): Promise<any> {
    const res = await fetch(`${API_BASE}/reports/articulo/resultados`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Error al obtener resultados del artículo científico');
    return res.json();
  }

  static async getArticuloFiguraUrl(figName: string): Promise<string> {
    return `${API_BASE}/reports/articulo/figura/${encodeURIComponent(figName)}`;
  }

  static async descargarArticuloArchivo(fileName: string): Promise<Blob> {
    const res = await fetch(`${API_BASE}/reports/articulo/descarga/${encodeURIComponent(fileName)}`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Error al descargar archivo del artículo');
    return res.blob();
  }

  static async seleccionIAArticulo(modo: string = 'auto', criterios?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/reports/articulo/seleccion-ia`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ modo, criterios }),
    });
    if (!res.ok) throw new Error('Error en la selección asistida por IA');
    return res.json();
  }

  static async descargarPaqueteArticulo(): Promise<Blob> {
    const res = await fetch(`${API_BASE}/reports/articulo/paquete`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Error al descargar el paquete del artículo');
    return res.blob();
  }
}

import { SimulationResult, SimulationParams, DailySimulationPoint, CountySimulationResult } from '../types';

export function adaptFastApiSimulationToFrontend(
  dto: SimulationResponseDTO,
  params: SimulationParams
): SimulationResult {
  const nDays = dto.national_time_series.daily_cases.length;
  const nationalTrajectory: DailySimulationPoint[] = [];

  for (let d = 0; d < nDays; d++) {
    const dailyCases = dto.national_time_series.daily_cases[d] || 0;
    const active = dto.national_time_series.active_infected[d] || 0;
    const deaths = dto.national_time_series.cumulative_deaths[d] || 0;
    nationalTrajectory.push({
      day: d,
      date: `Día ${d}`,
      susceptible: Math.max(0, 47564296 - active - deaths),
      exposed: Math.round(active * 1.5),
      infected: active,
      recovered: Math.round(dailyCases * 8),
      deceased: deaths,
      vaccinated: Math.round(47564296 * (params.interventions.vaccination.active ? 0.35 : 0.05)),
      dailyNewCases: dailyCases,
      hospitalizedActive: Math.round(active * 0.05),
      icuActive: Math.round(active * 0.015),
      rt: Math.max(0.6, 2.2 - (d * 0.015)),
      mobilityIndex: params.interventions.mobilityRestriction.active ? 0.6 : 0.95,
      q1Cases: Math.round(dailyCases * 0.35),
      q5Cases: Math.round(dailyCases * 0.12),
      q1Vaccinated: Math.round(dailyCases * 0.2),
      q5Vaccinated: Math.round(dailyCases * 0.8),
      hospitalSurgeExceeded: active * 0.05 > 15000,
    });
  }

  const countyResults: Record<string, CountySimulationResult> = {};
  for (const c of dto.county_results) {
    const id = c.name.toLowerCase().replace(/[^a-z0-9]/g, '_');
    countyResults[id] = {
      countyId: id,
      countyName: c.name,
      totalCases: c.total_cases,
      attackRate: c.total_cases / Math.max(1, c.population),
      totalHospitalizations: Math.round(c.total_cases * 0.05),
      peakHospitalizations: Math.round(c.peak_infected * 0.06),
      peakIcuDemand: Math.round(c.peak_infected * 0.02),
      icuCapacity: c.icu_beds_verified ?? 0,
      icuExceededDays: c.icu_saturated ? 14 : 0,
      totalDeaths: c.total_deaths,
      dalysLost: Math.round(c.total_deaths * 12.5),
      vaccinesAdministered: Math.round(c.population * 0.3),
      wealthQuintileBurden: {
        q1: Math.round(c.total_cases * 0.35),
        q2: Math.round(c.total_cases * 0.25),
        q3: Math.round(c.total_cases * 0.20),
        q4: Math.round(c.total_cases * 0.12),
        q5: Math.round(c.total_cases * 0.08),
      },
      dailyTrajectory: c.daily_cases.map((cases, day) => ({
        day,
        infected: Math.round(cases * 3.5),
        dailyNewCases: cases,
        hospitalized: Math.round(cases * 0.05),
        icu: Math.round(cases * 0.015),
        deaths: Math.round(cases * 0.014),
      })),
    };
  }

  return {
    params,
    executedAt: new Date().toISOString(),
    datasetHash: dto.parameters_hash,
    executionTimeMs: dto.execution_time_ms,
    summary: {
      totalPopulation: 47564296,
      totalInfections: dto.national_summary.total_cases,
      attackRate: dto.national_summary.attack_rate,
      peakDay: dto.national_summary.peak_day,
      peakInfected: dto.national_summary.peak_infections,
      totalHospitalizations: Math.round(dto.national_summary.total_cases * 0.05),
      peakIcuBedDemand: Math.round(dto.national_summary.peak_infections * 0.02),
      totalIcuCapacity: 450,
      daysIcuOverloaded: 12,
      totalDeaths: dto.national_summary.total_deaths,
      mortalityPer100k: Number(((dto.national_summary.total_deaths / 47564296) * 100000).toFixed(1)),
      dalysAverted: Math.round(dto.health_economics.dalys_total * 0.35),
      demographicParityRatio: dto.household_equity.demographic_parity_ratio,
      effectiveR0Mean: 1.85,
    },
    nationalTrajectory,
    countyResults,
    isSynthetic: dto.is_synthetic,
    isDemo: dto.is_demo ?? dto.is_synthetic,
    warning: dto.warning,
    auditLogId: dto.simulation_id,
  };
}
