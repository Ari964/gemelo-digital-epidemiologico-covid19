/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { Activity, Shield, LogOut, AlertCircle, RefreshCw } from 'lucide-react';
import { 
  SimulationParams, 
  SimulationResult, 
  LanguageCode, 
  UserRole 
} from './types';
import { getDefaultParams } from './utils/epidemicParams';
import { translations } from './i18n/translations';
import { Sidebar } from './components/Sidebar';
import { ToastProvider, useToast } from './components/ToastContainer';
import { DashboardView } from './components/DashboardView';
import { DataIntegrationView } from './components/DataIntegrationView';
import { HybridArchitectureView } from './components/HybridArchitectureView';
import { ValidationView } from './components/ValidationView';
import { SimulationControls } from './components/SimulationControls';
import { ScenarioComparator } from './components/ScenarioComparator';
import { SensitivityView } from './components/SensitivityView';
import { Map3DView } from './components/Map3DView';
import { ReportsView } from './components/ReportsView';
import { ApiDocsView } from './components/ApiDocsView';
import { AdminAuditView } from './components/AdminAuditView';
import { ModelMonitoringView } from './components/ModelMonitoringView';
import { WeeklyForecastingView } from './components/WeeklyForecastingView';
import { DataAssistantView } from './components/DataAssistantView';
import { LangChainAgentView } from './components/LangChainAgentView';
import { LangflowAssistantView } from './components/LangflowAssistantView';
import { EvidenceRouteView } from './components/EvidenceRouteView';
import { ArticleScientificView } from './components/ArticleScientificView';
import { FloatingChatbot } from './components/FloatingChatbot';
import { Login, AuthUser } from './components/Login';
import { canAccessModule, canAccessAction } from './permissions';
import { ApiClient, adaptFastApiSimulationToFrontend } from './services/apiClient';

function cap(s: string) { return s.charAt(0).toUpperCase() + s.slice(1); }

function NoAccess({ darkMode }: { darkMode: boolean }) {
  const t = translations[(localStorage.getItem('gdti_lang') as LanguageCode) || 'es'];
  return (
    <div className={`flex flex-col items-center justify-center py-24 text-center ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
      <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4 ${darkMode ? 'bg-rose-500/10 text-rose-400' : 'bg-rose-100 text-rose-600'}`}>
        <svg xmlns="http://www.w3.org/2000/svg" className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
      </div>
      <h3 className={`text-lg font-bold mb-1 ${darkMode ? 'text-slate-200' : 'text-slate-800'}`}>{t.noAccessTitle || 'Acceso restringido'}</h3>
      <p className="text-sm max-w-md">{t.noAccessMsg || 'Su rol no tiene permisos para acceder a este módulo. Contacte al administrador del sistema.'}</p>
    </div>
  );
}

function AppContent({ darkMode, setDarkMode, token, user, onLogout, lang, setLang }: {
  darkMode: boolean;
  setDarkMode: (v: boolean) => void;
  token: string;
  user: AuthUser;
  onLogout: () => void;
  lang: LanguageCode;
  setLang: (l: LanguageCode) => void;
}) {
  const { addToast } = useToast();
  const userRole = user.role;
  const [activeTab, setActiveTab] = useState<string>('scenario_deployment');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);
  const [selectedCountyId, setSelectedCountyId] = useState<string>('nairobi');
  const [isLoadingSim, setIsLoadingSim] = useState<boolean>(false);
  const [simError, setSimError] = useState<string | null>(null);

  // Parámetros base y estado de simulación (null por defecto, nunca resultados inventados)
  const [simParams, setSimParams] = useState<SimulationParams>(getDefaultParams('covid19'));
  const [simResult, setSimResult] = useState<SimulationResult | null>(null);

  const t = translations[lang];

  useEffect(() => {
    localStorage.setItem('gdti_lang', lang);
  }, [lang]);

  // Ejecución de la simulación mediante FastAPI (/api/v1/simulations/run)
  const handleRunSimulation = async (newParams: SimulationParams) => {
    if (!canAccessAction(userRole, 'run_simulation')) {
      addToast('error', 'Permiso Denegado', 'Su rol no posee permisos para ejecutar simulaciones epidemiológicas.');
      return;
    }
    setIsLoadingSim(true);
    setSimError(null);
    setSimParams(newParams);

    try {
      const respDTO = await ApiClient.runSimulation({
        days: newParams.durationDays,
        npi_stringency: newParams.interventions.schoolClosure.active ? 0.35 : 0.1,
        vaccine_coverage: newParams.interventions.vaccination.active ? 0.35 : 0.0,
        school_closure: newParams.interventions.schoolClosure.active,
        border_screening: newParams.interventions.mobilityRestriction.active,
        initial_infected_county: 47,
        initial_cases: 50,
        use_empirical_mobility: true,
        seed: newParams.randomSeed || 42,
        run_mode: newParams.runMode || 'EXPERIMENTAL',
        model_version: newParams.modelVersion,
      });

      const adapted = adaptFastApiSimulationToFrontend(respDTO, newParams);
      setSimResult(adapted);
      setSimError(null);
      addToast(
        'success', 
        'Simulación Auditada con Éxito (FastAPI Backend)', 
        `Escenario "${newParams.name}" ejecutado en servidor. Log ID: ${respDTO.simulation_id}`
      );
    } catch (err: any) {
      const msg = err.message || 'Error de conexión con el backend FastAPI';
      setSimError(msg);
      setSimResult(null); // Conservar estado nulo: jamás presentar ceros, 450 camas ni hashes ficticios
      addToast('error', 'Error en Backend FastAPI', msg);
    } finally {
      setIsLoadingSim(false);
    }
  };

  // Cargar simulación inicial desde el backend en el montaje
  useEffect(() => {
    handleRunSimulation(simParams);
  }, []);

  return (
    <div className={`min-h-screen flex ${darkMode ? 'bg-slate-950 text-slate-100 dark-mode' : 'bg-slate-50 text-slate-900 light-mode'} transition-colors duration-200`}>
      {/* 1. Sidebar Fijo a la Izquierda con Módulos CRISP-DM */}
      <Sidebar
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        darkMode={darkMode}
        onToggleTheme={() => setDarkMode(!darkMode)}
        lang={lang}
        role={userRole}
      />

      {/* 2. Contenedor Principal del Workspace */}
      <div className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ${isSidebarCollapsed ? 'md:ml-[72px]' : 'md:ml-[280px]'}`}>
        {/* Barra Superior */}
        <header className={`sticky top-0 z-40 border-b ${darkMode ? 'bg-slate-950/90 border-slate-800/80' : 'bg-white/90 border-slate-200'} backdrop-blur-md px-4 lg:px-6 py-3 flex items-center justify-between shadow-sm`}>
          <div>
            <h2 className={`text-xs sm:text-sm font-extrabold tracking-tight flex items-center gap-2 ${darkMode ? 'text-slate-100' : 'text-slate-800'}`}>
              {lang === 'en' ? 'Epidemiological Digital Twin (Kenya)' : lang === 'sw' ? 'Pacha wa Kidijitali wa Magonjwa (Kenya)' : 'Gemelo Digital Epidemiológico (Kenia)'}
              <span className="hidden sm:inline-block text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-500 dark:text-blue-400 border border-blue-500/30">
                CRISP-DM Standard • FastAPI :8000
              </span>
            </h2>
            <p className={`text-[11px] hidden sm:block ${darkMode ? 'text-slate-400' : 'text-slate-600 font-medium'}`}>
              {lang === 'en' 
                ? 'Pandemic Intervention Simulation & Management System (47 Counties)' 
                : lang === 'sw' 
                ? 'Mfumo wa Usimamizi na Uigaji wa Hatua za Janga (Kaunti 47)' 
                : 'Sistema de Gestión y Simulación de Intervenciones Pandémicas (47 Condados)'}
            </p>
          </div>

          <div className="flex items-center gap-2.5">
            {/* Selector de Idioma */}
            <div className={`flex items-center border rounded-xl p-1 text-xs ${darkMode ? 'bg-slate-900 border-slate-800' : 'bg-slate-100 border-slate-200'}`}>
              <button
                onClick={() => setLang('es')}
                className={`px-2 py-1 rounded-lg font-medium transition cursor-pointer ${lang === 'es' ? 'bg-blue-600 text-white shadow-sm' : darkMode ? 'text-slate-400' : 'text-slate-700'}`}
              >
                ES
              </button>
              <button
                onClick={() => setLang('en')}
                className={`px-2 py-1 rounded-lg font-medium transition cursor-pointer ${lang === 'en' ? 'bg-blue-600 text-white shadow-sm' : darkMode ? 'text-slate-400' : 'text-slate-700'}`}
              >
                EN
              </button>
              <button
                onClick={() => setLang('sw')}
                className={`px-2 py-1 rounded-lg font-medium transition cursor-pointer ${lang === 'sw' ? 'bg-blue-600 text-white shadow-sm' : darkMode ? 'text-slate-400' : 'text-slate-700'}`}
              >
                SW
              </button>
            </div>

            {/* Credencial del Usuario Activo */}
            <div className={`hidden md:flex items-center gap-2 text-xs font-mono px-3 py-1.5 rounded-xl border ${darkMode ? 'bg-slate-900 border-slate-800 text-slate-300' : 'bg-slate-100 border-slate-200 text-slate-700'}`}>
              <Shield size={13} className="text-blue-500" />
              <span className="font-bold text-blue-600 dark:text-blue-400">{user.name}</span>
              <span className={`text-[10px] ${darkMode ? 'text-slate-400' : 'text-slate-600 font-medium'}`}>({cap(userRole)})</span>
            </div>

            {/* Botón de Cierre de Sesión */}
            <button
              onClick={onLogout}
              className={`p-2 rounded-xl border text-xs font-semibold flex items-center gap-1 transition cursor-pointer ${
                darkMode ? 'bg-slate-900 hover:bg-slate-800 border-slate-800 text-slate-400 hover:text-rose-400' : 'bg-slate-100 hover:bg-slate-200 border-slate-200 text-slate-700 hover:text-rose-600'
              }`}
              title={lang === 'en' ? 'Sign Out' : lang === 'sw' ? 'Toka kwenye mfumo' : 'Cerrar Sesión'}
            >
              <LogOut size={15} />
            </button>
          </div>
        </header>

        {/* CONTENEDOR DINÁMICO DE VISTAS (METODOLOGÍA CRISP-DM) */}
        <main className="flex-1 max-w-7xl w-full mx-auto p-4 lg:p-6">
          {/* Alerta de Error Persistente si el Backend está fuera de línea */}
          {simError && (
            <div id="sim_backend_error_banner" className="mb-6 p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-lg">
              <div className="flex items-start gap-3">
                <AlertCircle className="text-rose-400 shrink-0 mt-0.5" size={20} />
                <div>
                  <h4 className="text-xs font-bold text-rose-200 uppercase tracking-wide">
                    {t.backendOfflineTitle || 'Error de Conexión: Backend Fuera de Línea'}
                  </h4>
                  <p className="text-xs text-rose-300/90 mt-0.5">
                    {simError}. {t.backendOfflineDesc || 'No se presentan cifras por defecto, 450 camas UCI ni resultados simulados ficticios.'}
                  </p>
                </div>
              </div>
              <button
                id="btn_retry_sim_backend"
                onClick={() => handleRunSimulation(simParams)}
                disabled={isLoadingSim}
                className="px-3.5 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold transition flex items-center justify-center gap-1.5 shrink-0 cursor-pointer shadow"
              >
                <RefreshCw size={13} className={isLoadingSim ? 'animate-spin' : ''} />
                <span>Reintentar Conexión</span>
              </button>
            </div>
          )}

          {/* MÓDULO 1: GESTIÓN DE USUARIOS Y SEGURIDAD */}
          {(activeTab === 'user_security' || activeTab === 'admin') && (
            canAccessModule(userRole, 'user_security') ? (
              <AdminAuditView
                currentRole={userRole}
                lang={lang}
                darkMode={darkMode}
                token={token}
              />
            ) : <NoAccess darkMode={darkMode} />
          )}

          {/* MÓDULO 2: FASE 1, 2 Y 3 (CRISP-DM) - INTEGRACIÓN Y PREPARACIÓN DE DATOS */}
          {(activeTab === 'data_preparation' || activeTab === 'data') && (
            canAccessModule(userRole, 'data_preparation') ? (
              <DataIntegrationView
                lang={lang}
                darkMode={darkMode}
              />
            ) : <NoAccess darkMode={darkMode} />
          )}

          {/* MÓDULO 3: FASE 4 (CRISP-DM) - GEMELO DIGITAL (MODELADO) */}
          {(activeTab === 'digital_twin_model' || activeTab === 'model') && (
            canAccessModule(userRole, 'digital_twin_model') ? (
              <HybridArchitectureView
                simulationResult={simResult}
                lang={lang}
                darkMode={darkMode}
              />
            ) : <NoAccess darkMode={darkMode} />
          )}

          {/* MÓDULO 4: FASE 5 (CRISP-DM) - EVALUACIÓN Y VALIDACIÓN */}
          {(activeTab === 'evaluation_validation' || activeTab === 'validation') && (
            canAccessModule(userRole, 'evaluation_validation') ? (
              <ValidationView
                lang={lang}
                darkMode={darkMode}
              />
            ) : <NoAccess darkMode={darkMode} />
          )}

          {/* MÓDULO 5: FASE 6 (CRISP-DM) - DESPLIEGUE DE ESCENARIOS (TOMA DE DECISIONES) */}
          {(activeTab === 'scenario_deployment' || activeTab === 'simulation') && (
            canAccessModule(userRole, 'scenario_deployment') ? (
              <SimulationControls
                currentParams={simParams}
                onRunSimulation={handleRunSimulation}
                isLoading={isLoadingSim}
                lang={lang}
                darkMode={darkMode}
              />
            ) : <NoAccess darkMode={darkMode} />
          )}

          {/* MÓDULO RUTA DE EVIDENCIA */}
          {activeTab === 'evidence_route' && (
            canAccessModule(userRole, 'evidence_route') ? (
              <EvidenceRouteView
                darkMode={darkMode}
                lang={lang}
                onNavigateToTab={(tab) => setActiveTab(tab)}
              />
            ) : <NoAccess darkMode={darkMode} />
          )}

          {/* MÓDULO 5B: FASE 6 (CRISP-DM) - MONITOREO DE MODELOS (ON-DEMAND) */}
          {activeTab === 'model_monitoring' && (
            canAccessModule(userRole, 'model_monitoring') ? (
              <ModelMonitoringView
                darkMode={darkMode}
                lang={lang}
              />
            ) : <NoAccess darkMode={darkMode} />
          )}

          {/* MÓDULO PREDICCIÓN SEMANAL & SENSIBILIDAD */}
          {activeTab === 'weekly_forecasting' && (
            canAccessModule(userRole, 'weekly_forecasting') ? (
              <WeeklyForecastingView
                darkMode={darkMode}
                lang={lang}
              />
            ) : <NoAccess darkMode={darkMode} />
          )}

          {/* MÓDULO AGENTE INTEGRADOR LANGCHAIN */}
          {activeTab === 'langchain_agent' && (
            canAccessModule(userRole, 'langchain_agent') ? (
              <LangChainAgentView
                darkMode={darkMode}
                lang={lang}
              />
            ) : <NoAccess darkMode={darkMode} />
          )}

          {/* MÓDULO FLÚJO LANGFLOW */}
          {activeTab === 'langflow_assistant' && (
            canAccessModule(userRole, 'langflow_assistant') ? (
              <LangflowAssistantView
                darkMode={darkMode}
                lang={lang}
              />
            ) : <NoAccess darkMode={darkMode} />
          )}

          {/* MÓDULO ASISTENTE DE DATOS DEL GEMELO DIGITAL */}
          {activeTab === 'data_assistant' && (
            canAccessModule(userRole, 'data_assistant') ? (
              <DataAssistantView
                darkMode={darkMode}
                lang={lang}
              />
            ) : <NoAccess darkMode={darkMode} />
          )}

          {/* MÓDULO 6: GENERACIÓN DE INFORMES (REPORTING) */}
          {activeTab === 'reporting' || activeTab === 'reports'
            ? (canAccessModule(userRole, 'reporting')
                ? <ReportsView
                    simulationResult={simResult}
                    lang={lang}
                    darkMode={darkMode}
                    userEmail={user.email}
                  />
                : <NoAccess darkMode={darkMode} />)
            : null}

          {/* MÓDULO ARTÍCULO CIENTÍFICO (Fase 13) */}
          {activeTab === 'articulo_cientifico'
            ? (canAccessModule(userRole, 'reporting')
                ? <ArticleScientificView
                    lang={lang}
                    darkMode={darkMode}
                  />
                : <NoAccess darkMode={darkMode} />)
            : null}

          {/* VISTAS DE SOPORTE ADICIONAL */}
          {activeTab === 'dashboard' && (
            <DashboardView
              simulationResult={simResult}
              selectedCountyId={selectedCountyId}
              onSelectCounty={(id) => {
                setSelectedCountyId(id);
                setActiveTab('3d_view');
              }}
              lang={lang}
              darkMode={darkMode}
            />
          )}

          {activeTab === 'comparator' && (
            <ScenarioComparator
              primaryResult={simResult}
              lang={lang}
              darkMode={darkMode}
            />
          )}

          {activeTab === 'sensitivity' && (
            <SensitivityView
              simulationResult={simResult}
              lang={lang}
              darkMode={darkMode}
            />
          )}

          {activeTab === '3d_view' && (
            <Map3DView
              simulationResult={simResult}
              selectedCountyId={selectedCountyId}
              onSelectCounty={setSelectedCountyId}
              lang={lang}
              darkMode={darkMode}
            />
          )}

          {activeTab === 'api_docs' && (
            <ApiDocsView
              lang={lang}
              darkMode={darkMode}
            />
          )}
        </main>

        {/* Copiloto Epidemiológico IA: ÚNICO PUNTO DE ACCESO PERMANENTE EN LA ESQUINA INFERIOR DERECHA */}
        <FloatingChatbot
          darkMode={darkMode}
          simulationContext={simResult}
        />

        {/* Pie de Página */}
        <footer className={`border-t ${darkMode ? 'bg-slate-950 border-slate-800' : 'bg-white border-slate-200'} py-4 px-6 text-center text-xs flex flex-col sm:flex-row items-center justify-between gap-2 ${darkMode ? 'text-slate-500' : 'text-slate-600'}`}>
          <span>
            Gemelo Digital Epidemiológico Kenia • Metodología CRISP-DM v2.5 (FastAPI :8000 + React)
          </span>
          <span className={`font-mono text-[11px] ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
            {simResult ? (
              <>Semilla: #{simResult.params.randomSeed} | Hash: {simResult.datasetHash.slice(0, 10)}</>
            ) : (
              <span className="text-amber-500 font-semibold">
                ● Estado: Sin simulación activa («{t.executeSimPrompt || 'Ejecute una simulación'}»)
              </span>
            )}
          </span>
        </footer>
      </div>
    </div>
  );
}

export default function App() {
  const [darkMode, setDarkMode] = useState<boolean>(() => localStorage.getItem('gdti_dark') !== 'false');
  const [lang, setLang] = useState<LanguageCode>(() => (localStorage.getItem('gdti_lang') as LanguageCode) || 'es');
  const [token, setToken] = useState<string>(() => localStorage.getItem('gdti_jwt_token') || '');
  const [user, setUser] = useState<AuthUser | null>(() => {
    try {
      const raw = localStorage.getItem('gdti_user');
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });

  useEffect(() => {
    localStorage.setItem('gdti_dark', String(darkMode));
  }, [darkMode]);

  useEffect(() => {
    localStorage.setItem('gdti_lang', lang);
  }, [lang]);

  // Validar sesión activa en FastAPI /api/v1/auth/me
  useEffect(() => {
    if (!token) return;
    ApiClient.getMe()
      .then((me) => {
        const authUser: AuthUser = {
          id: me.id,
          name: me.name,
          email: me.email,
          role: me.role as any,
        };
        setUser(authUser);
        localStorage.setItem('gdti_user', JSON.stringify(authUser));
      })
      .catch(() => {
        ApiClient.clearTokens();
        localStorage.removeItem('gdti_user');
        setToken('');
        setUser(null);
      });
  }, [token]);

  const handleLogin = (newToken: string, newUser: AuthUser) => {
    localStorage.setItem('gdti_user', JSON.stringify(newUser));
    setToken(newToken);
    setUser(newUser);
  };

  const handleLogout = () => {
    ApiClient.clearTokens();
    localStorage.removeItem('gdti_user');
    setToken('');
    setUser(null);
  };

  if (!user || !token) {
    return (
      <ToastProvider darkMode={darkMode}>
        <Login 
          onLogin={handleLogin} 
          darkMode={darkMode} 
          currentLang={lang} 
          onLanguageChange={setLang} 
        />
      </ToastProvider>
    );
  }

  return (
    <ToastProvider darkMode={darkMode}>
      <AppContent 
        darkMode={darkMode} 
        setDarkMode={setDarkMode} 
        token={token} 
        user={user} 
        onLogout={handleLogout} 
        lang={lang} 
        setLang={setLang} 
      />
    </ToastProvider>
  );
}