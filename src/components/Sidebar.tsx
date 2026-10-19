import React from 'react';
import { 
  Shield, 
  Database, 
  Cpu, 
  CheckCircle2, 
  Sliders, 
  FileText, 
  Activity, 
  Columns, 
  Box, 
  Code2, 
  Layout,
  Sun, 
  Moon, 
  Menu, 
  X,
  Sparkles,
  Users,
  TrendingUp,
  Bot,
  Workflow,
  Compass
} from 'lucide-react';
import { LanguageCode, UserRole } from '../types';
import { canAccessModule } from '../permissions';

interface SidebarProps {
  activeTab: string;
  onSelectTab: (tabId: string) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  darkMode: boolean;
  onToggleTheme: () => void;
  lang: LanguageCode;
  role: UserRole;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onSelectTab,
  isCollapsed,
  onToggleCollapse,
  darkMode,
  onToggleTheme,
  lang,
  role,
}) => {
  // Módulos Base estructurados estrictamente según la metodología CRISP-DM
  // y los módulos transversales del sistema de gestión empresarial
  const crispDmModules = [
    {
      id: 'evidence_route',
      label: lang === 'en' ? 'Evidence Route (Audit)' : lang === 'sw' ? 'Njia ya Ushahidi (Ukaguzi)' : 'Ruta de Evidencia (Auditoría)',
      shortLabel: lang === 'en' ? 'Evidence Route' : lang === 'sw' ? 'Njia Ushahidi' : 'Ruta Evidencia',
      icon: Compass,
      tag: 'Audit',
      description: lang === 'en' ? '15 verifiable stations from raw OWID data to Langflow' : '15 estaciones auditables de datos crudos a Langflow',
    },
    {
      id: 'user_security',
      label: lang === 'en' ? 'User & Security Management' : lang === 'sw' ? 'Usimamizi wa Watumiaji na Usalama' : 'Gestión de Usuarios y Seguridad',
      shortLabel: lang === 'en' ? 'Security & Users' : lang === 'sw' ? 'Usalama na Watumiaji' : 'Seguridad & Usuarios',
      icon: Shield,
      tag: 'CRUD / Audit',
      description: lang === 'en' ? 'User CRUD, roles (Admin, Epidemiologist, Analyst) and Audit Log' : 'CRUD de usuarios, roles (Administrador, Epidemiólogo, Analista) y Bitácora de Auditoría',
    },
    {
      id: 'data_preparation',
      label: lang === 'en' ? 'Phase 1-3 (CRISP-DM) - Data Integration' : lang === 'sw' ? 'Awamu 1-3 (CRISP-DM) - Muunganisho wa Data' : 'Fase 1, 2 y 3 (CRISP-DM) - Integración y Preparación de Datos',
      shortLabel: lang === 'en' ? 'Phase 1-3: ETL' : lang === 'sw' ? 'Awamu 1-3: ETL' : 'Fase 1-3: Integración ETL',
      icon: Database,
      tag: 'ETL / Calidad',
      description: lang === 'en' ? 'ETL pipeline (OWID, KNBS 2019, Barasa 2020), cleaning, imputation and data quality' : 'Pipeline ETL (OWID, KNBS 2019, Barasa 2020), limpieza, imputación y calidad de datos',
    },
    {
      id: 'digital_twin_model',
      label: lang === 'en' ? 'Phase 4 (CRISP-DM) - Digital Twin (Modeling)' : lang === 'sw' ? 'Awamu 4 (CRISP-DM) - Pacha wa Kidijitali (Uundaji)' : 'Fase 4 (CRISP-DM) - Gemelo Digital (Modelado)',
      shortLabel: lang === 'en' ? 'Phase 4: Digital Twin' : lang === 'sw' ? 'Awamu 4: Pacha' : 'Fase 4: Gemelo Digital',
      icon: Cpu,
      tag: 'SEIR + ABM',
      description: lang === 'en' ? 'Hybrid architecture calibration (Metapopulation SEIR + Intra-household agents)' : 'Calibración de arquitectura híbrida (Metapoblación SEIR + Agentes intra-hogar)',
    },
    {
      id: 'evaluation_validation',
      label: lang === 'en' ? 'Phase 5 (CRISP-DM) - Evaluation & Validation' : lang === 'sw' ? 'Awamu 5 (CRISP-DM) - Tathmini na Uthibitishaji' : 'Fase 5 (CRISP-DM) - Evaluación y Validación',
      shortLabel: lang === 'en' ? 'Phase 5: Validation' : lang === 'sw' ? 'Awamu 5: Uthibitishaji' : 'Fase 5: Validación',
      icon: CheckCircle2,
      tag: 'CV Folds / Tests',
      description: lang === 'en' ? '5 temporal folds, parameter grid, Wilcoxon & Diebold-Mariano biostatistical tests' : '5 pliegues temporales, espacio de hiperparámetros, pruebas Wilcoxon y Diebold-Mariano',
    },
    {
      id: 'scenario_deployment',
      label: lang === 'en' ? 'Phase 6 (CRISP-DM) - Scenario Deployment' : lang === 'sw' ? 'Awamu 6 (CRISP-DM) - Upelekaji wa Matukio' : 'Fase 6 (CRISP-DM) - Despliegue de Escenarios (Toma de Decisiones)',
      shortLabel: lang === 'en' ? 'Phase 6: NPI Scenarios' : lang === 'sw' ? 'Awamu 6: Matukio ya NPI' : 'Fase 6: Despliegue NPIs',
      icon: Sliders,
      tag: 'NPIs / DALYs',
      description: lang === 'en' ? 'Simulation of closures, restrictions, vaccines, ICU demand and averted DALYs' : 'Simulación de cierres, restricciones, vacunación, saturación UCI y DALYs evitados',
    },
    {
      id: 'model_monitoring',
      label: lang === 'en' ? 'Phase 6 (CRISP-DM) - Model Monitoring' : lang === 'sw' ? 'Awamu 6 (CRISP-DM) - Ufuatiliaji wa Mtindo' : 'Fase 6 (CRISP-DM) - Monitoreo de Modelos (On-Demand)',
      shortLabel: lang === 'en' ? 'Phase 6: Monitoring' : lang === 'sw' ? 'Awamu 6: Ufuatiliaji' : 'Fase 6: Monitoreo Modelo',
      icon: Activity,
      tag: 'PSI / Drift',
      description: lang === 'en' ? 'Population Stability Index (PSI), Kolmogorov-Smirnov and champion model health' : 'Supervisión de estabilidad poblacional (PSI), Kolmogorov-Smirnov y salud del modelo activo',
    },
    {
      id: 'weekly_forecasting',
      label: lang === 'en' ? 'Weekly Forecasting & Sensitivity' : lang === 'sw' ? 'Utabiri wa Kila Wiki na Usikivu' : 'Predicción Semanal & Sensibilidad',
      shortLabel: lang === 'en' ? 'Weekly Forecast' : lang === 'sw' ? 'Utabiri wa Wiki' : 'Predicción Semanal',
      icon: TrendingUp,
      tag: 'Persistencia / RF',
      description: lang === 'en' ? 'Weekly case surveillance with persistence baseline and Random Forest sensitivity exploration' : 'Vigilancia semanal de casos con modelo persistente (campeón) y exploración hipotética de sensibilidad',
    },
    {
      id: 'reporting',
      label: lang === 'en' ? 'Reporting & Export' : lang === 'sw' ? 'Ripoti na Usafirishaji' : 'Generación de Informes (Reporting)',
      shortLabel: lang === 'en' ? 'Reports' : lang === 'sw' ? 'Ripoti' : 'Informes (ReportLab/OpenPyXL)',
      icon: FileText,
      tag: 'PDF & Excel',
      description: lang === 'en' ? 'Consolidated report generation in PDF (ReportLab) and Excel (OpenPyXL)' : 'Módulo transversal consolidado para exportación a PDF (ReportLab) y Excel (OpenPyXL)',
    },
    {
      id: 'articulo_cientifico',
      label: lang === 'en' ? 'Scientific Article' : lang === 'sw' ? 'Makala ya Sayansi' : 'Artículo Científico',
      shortLabel: lang === 'en' ? 'Article' : lang === 'sw' ? 'Makala' : 'Artículo',
      icon: Layout,
      tag: 'Artículo',
      description: lang === 'en' ? 'Tables and figures with interpretability and explainability for the research article' : 'Tablas y figuras con interprétabilidad y explicabilidad para el artículo científico',
    },
  ].filter((m) => canAccessModule(role, m.id as any));

  // Herramientas de Soporte & Análisis Complementario
  const auxiliaryTools = [
    { id: 'langchain_agent', label: lang === 'en' ? 'LangChain Integrator Agent' : lang === 'sw' ? 'Wakala wa LangChain' : 'Agente Integrador LangChain', icon: Sparkles },
    { id: 'langflow_assistant', label: lang === 'en' ? 'Langflow Assistant (API)' : lang === 'sw' ? 'Msaidizi wa Langflow (API)' : 'Flujo Langflow (Servicio API)', icon: Workflow },
    { id: 'data_assistant', label: lang === 'en' ? 'Digital Twin Data Assistant' : lang === 'sw' ? 'Msaidizi wa Takwimu wa Pacha' : 'Asistente de datos del gemelo digital', icon: Bot },
    { id: 'dashboard', label: lang === 'en' ? 'General Dashboard (Overview)' : lang === 'sw' ? 'Dashibodi Kuu' : 'Dashboard General (Overview)', icon: Activity },
    { id: 'comparator', label: lang === 'en' ? 'Comparative Analysis (Trade-offs)' : lang === 'sw' ? 'Uchambuzi Linganishi' : 'Análisis Comparativo (Trade-offs)', icon: Columns },
    { id: '3d_view', label: lang === 'en' ? '3D Spatial & GIS View' : lang === 'sw' ? 'Mwonekano wa 3D na GIS' : 'Visualización Espacial 3D & GIS', icon: Box },
    { id: 'api_docs', label: lang === 'en' ? 'API Documentation (OpenAPI)' : lang === 'sw' ? 'Hati za API (OpenAPI)' : 'Documentación API (OpenAPI)', icon: Code2 },
  ].filter((m) => canAccessModule(role, m.id as any));

  return (
    <aside
      id="app_sidebar_left"
      className={`fixed top-0 left-0 bottom-0 z-50 flex flex-col justify-between transition-all duration-300 ease-in-out border-r ${
        darkMode ? 'bg-slate-950/95 border-slate-800/80 text-slate-200' : 'bg-white/95 border-slate-200 text-slate-800'
      } backdrop-blur-md shadow-2xl ${isCollapsed ? 'w-[72px]' : 'w-[280px]'}`}
    >
      {/* Sección Superior: Branding & Botón Toggle Colapsar/Expandir */}
      <div className="p-4 flex items-center justify-between border-b border-slate-800/60">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-500 flex items-center justify-center text-white shadow-lg shadow-blue-500/25 shrink-0">
            <Activity size={20} />
          </div>
          {!isCollapsed && (
            <div className="truncate">
              <h1 className="text-xs font-extrabold tracking-tight flex items-center gap-1.5 truncate">
                Digital Twin
                <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-500 dark:text-blue-400 border border-blue-500/30">
                  CRISP-DM
                </span>
              </h1>
              <p className={`text-[10px] truncate ${darkMode ? 'text-slate-400' : 'text-slate-600 font-medium'}`}>
                {lang === 'en' ? 'Kenya 47 Counties' : lang === 'sw' ? 'Kaunti 47 za Kenya' : 'Kenia 47 Condados'}
              </p>
            </div>
          )}
        </div>

        {/* Botón de Hamburguesa para Colapsar / Expandir Sidebar */}
        <button
          id="btn_toggle_sidebar"
          onClick={onToggleCollapse}
          className={`p-2 rounded-xl transition shrink-0 cursor-pointer ${
            darkMode ? 'bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-800' : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300'
          }`}
          title={isCollapsed ? (lang === 'en' ? 'Expand Sidebar' : lang === 'sw' ? 'Panua Menyu' : 'Expandir Sidebar') : (lang === 'en' ? 'Collapse Sidebar' : lang === 'sw' ? 'Kunja Menyu' : 'Colapsar Sidebar')}
        >
          {isCollapsed ? <Menu size={18} /> : <X size={18} />}
        </button>
      </div>

      {/* Centro: Navegación de Módulos Base CRISP-DM */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6 scrollbar-none">
        {/* Grupo 1: Módulos Base Metodología CRISP-DM */}
        <div>
          {!isCollapsed && (
            <div className="px-2 mb-2.5">
              <span className="text-[10px] font-mono uppercase tracking-wider text-blue-600 dark:text-blue-400 block font-bold">
                {lang === 'en' ? 'Core Modules (CRISP-DM)' : lang === 'sw' ? 'Moduli za Msingi (CRISP-DM)' : 'Módulos Base (CRISP-DM)'}
              </span>
              <span className={`text-[9px] block ${darkMode ? 'text-slate-400' : 'text-slate-600 font-medium'}`}>
                {lang === 'en' ? 'Enterprise Management System' : lang === 'sw' ? 'Mfumo wa Usimamizi wa Biashara' : 'Arquitectura de Gestión Empresarial'}
              </span>
            </div>
          )}
          <nav className="space-y-1.5">
            {crispDmModules.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  id={`sidebar_item_${item.id}`}
                  key={item.id}
                  onClick={() => onSelectTab(item.id)}
                  title={isCollapsed ? item.label : item.description}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                    isActive
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/25'
                      : darkMode
                      ? 'text-slate-300 hover:text-white hover:bg-slate-900/90 border border-transparent hover:border-slate-800'
                      : 'text-slate-700 hover:text-slate-950 hover:bg-slate-100 border border-transparent'
                  }`}
                >
                  <Icon size={18} className="shrink-0" />
                  {!isCollapsed && (
                    <div className="flex-1 text-left truncate flex items-center justify-between gap-1">
                      <span className="truncate text-[11px] leading-tight font-medium">
                        {item.shortLabel || item.label}
                      </span>
                      {item.tag && (
                        <span className={`text-[8px] font-mono shrink-0 px-1.5 py-0.5 rounded font-bold ${
                          isActive ? 'bg-white/20 text-white' : darkMode ? 'bg-slate-800/80 text-slate-300 border border-slate-700/50' : 'bg-slate-200 text-slate-800 border border-slate-300'
                        }`}>
                          {item.tag}
                        </span>
                      )}
                    </div>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Grupo 2: Herramientas de Soporte & Análisis */}
        <div>
          {!isCollapsed && (
            <span className={`text-[10px] font-mono uppercase tracking-wider block px-2 mb-2 font-bold ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
              {lang === 'en' ? 'Support Tools' : lang === 'sw' ? 'Vyombo vya Usaidizi' : 'Herramientas de Soporte'}
            </span>
          )}
          <nav className="space-y-1">
            {auxiliaryTools.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  id={`sidebar_item_${item.id}`}
                  key={item.id}
                  onClick={() => onSelectTab(item.id)}
                  title={isCollapsed ? item.label : undefined}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                    isActive
                      ? 'bg-blue-600/20 border border-blue-500/40 text-blue-600 dark:text-blue-400 font-semibold'
                      : darkMode
                      ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                      : 'text-slate-700 hover:text-slate-950 hover:bg-slate-100 font-medium'
                  }`}
                >
                  <Icon size={16} className="shrink-0" />
                  {!isCollapsed && <span className="truncate text-[11px]">{item.label}</span>}
                </button>
              );
            })}
          </nav>
        </div>

      </div>

      {/* Sección Inferior: Selector de Tema & Metadatos */}
      <div className={`p-3 border-t space-y-2 ${darkMode ? 'border-slate-800/60' : 'border-slate-200'}`}>
        {/* Toggle de Tema Claro / Oscuro */}
        <button
          id="btn_sidebar_theme_toggle"
          onClick={onToggleTheme}
          className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold transition cursor-pointer ${
            darkMode ? 'bg-slate-900 text-slate-200 hover:bg-slate-800' : 'bg-slate-100 text-slate-800 hover:bg-slate-200 border border-slate-300'
          }`}
          title={lang === 'en' ? 'Toggle Light / Dark Mode' : lang === 'sw' ? 'Badilisha Mwanga / Giza' : 'Alternar Modo Claro / Oscuro'}
        >
          <div className="flex items-center gap-2">
            {darkMode ? <Sun size={15} className="text-amber-400" /> : <Moon size={15} className="text-indigo-600" />}
            {!isCollapsed && (
              <span>
                {darkMode 
                  ? (lang === 'en' ? 'Light Mode' : lang === 'sw' ? 'Mwanga' : 'Modo Claro') 
                  : (lang === 'en' ? 'Dark Mode' : lang === 'sw' ? 'Giza' : 'Modo Oscuro')}
              </span>
            )}
          </div>
          {!isCollapsed && (
            <span className={`text-[10px] font-mono ${darkMode ? 'text-slate-400' : 'text-slate-600 font-bold'}`}>
              {darkMode ? 'Dark' : 'Light'}
            </span>
          )}
        </button>

        {!isCollapsed && (
          <div className={`text-[9px] text-center font-mono pt-1 ${darkMode ? 'text-slate-400' : 'text-slate-600 font-medium'}`}>
            CRISP-DM Standard • FastAPI + React
          </div>
        )}
      </div>
    </aside>
  );
};
