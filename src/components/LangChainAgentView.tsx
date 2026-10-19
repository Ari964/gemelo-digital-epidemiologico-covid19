import React, { useState } from 'react';
import { 
  Sparkles, 
  Send, 
  Database, 
  TrendingUp, 
  Bot, 
  Layers, 
  CheckCircle2, 
  AlertTriangle, 
  Clock, 
  Cpu, 
  FileCode2, 
  Wrench,
  Info
} from 'lucide-react';

import { LanguageCode } from '../i18n/translations';
import { ApiClient } from '../services/apiClient';

interface LangChainToolCall {
  tool_name: string;
  args: Record<string, any>;
  output_summary: string;
}

interface LangChainMetadata {
  framework: string;
  execution_mode: string;
  orchestration_type: string;
  components_executed: string[];
  tools_invoked: LangChainToolCall[];
  provider: string;
  execution_time_ms: number;
}

interface LangChainResponse {
  query: string;
  cutoff_date: string;
  database_observations: Record<string, any>;
  model_forecasts: Record<string, any>;
  hospital_capacity: Record<string, any>;
  generated_text: string;
  langchain_metadata: LangChainMetadata;
}

interface LangChainAgentViewProps {
  lang: LanguageCode;
  darkMode: boolean;
}

export const LangChainAgentView: React.FC<LangChainAgentViewProps> = ({ lang, darkMode }) => {
  const [query, setQuery] = useState('');
  const [cutoffDate, setCutoffDate] = useState('2024-07-28');
  const [countyCode, setCountyCode] = useState(0);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<LangChainResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const t = {
    es: {
      title: 'Agente Integrador LangChain',
      badge: 'LCEL Pipeline • Tools @tool • Ollama Local',
      description: 'Caso integrador verificable en Python con componentes de LangChain (langchain_core y langchain_ollama). Ejecuta herramientas estructuradas, prompt templates y LCEL sobre Ollama local, con estricta segregación de observaciones empíricas, pronósticos y síntesis estructurada.',
      scope: 'Ámbito:',
      scopeNational: 'Nacional (KEN)',
      cutoff: 'Corte:',
      placeholder: 'Ingrese una consulta epidemiológica para el agente LangChain...',
      btnExecute: 'Ejecutar LangChain',
      suggestionsLabel: 'Sugerencias:',
      delimitationTitle: 'Delimitación Epidemiológica y Hospitalaria:',
      delimitationBody: 'Las cifras de incidencia observadas y pronósticos corresponden exclusivamente al total NACIONAL agregado de Kenia (KEN, county_code=0). Las camas UCI corresponden al inventario estático descriptivo de Barasa et al. (2020) S1 Table. No existe desagregación condal de casos ni tasa de conversión a demanda UCI clínica que permita inferir saturación.',
      panel1Title: '1. Observaciones SQLite (Nacional KEN, @tool)',
      panel2Title: '2. Pronósticos Estadísticos (Nacional KEN, @tool)',
      panel3Title: '3. Síntesis LangChain Core (Ollama)',
      panelMetaTitle: 'Trazabilidad de Ejecución LangChain (Backend FastAPI)',
      invokedTag: '✓ Invocado:',
      cutoffLabel: 'Fecha de Corte:',
      casesObsLabel: 'Casos Nacionales (yt):',
      deathsObsLabel: 'Muertes Nacionales:',
      stringencyLabel: 'Índice Rigurosidad:',
      targetWeekLabel: 'Semana Proyectada (t+1):',
      persistenceLabel: 'Persistencia Naive (Campeón t+1):',
      actualObsLabel: 'Observado Real Nacional (t+1):',
      rfLabel: 'RF Nacional (Sensibilidad):',
      rfWarning: '⚠ Sensibilidad no causal sobre variables congeladas',
      notAvailable: 'No disponible',
      casesUnit: 'casos',
      modeLabel: 'Modo:',
      orchestrationLabel: 'Orquestación:',
      executorLabel: 'Ejecutor:',
      toolsNotice: 'Las herramientas están estructuradas mediante @tool de LangChain Core y son invocadas de forma orquestada por el pipeline.',
      componentsLabel: 'Componentes LangChain Ejecutados en Pipeline LCEL:',
      toolsInvokedLabel: 'Herramientas Estructuradas (@tool) Invocadas:',
      errConnection: 'Error al consultar el agente LangChain:'
    },
    en: {
      title: 'LangChain Integrator Agent',
      badge: 'LCEL Pipeline • Tools @tool • Local Ollama',
      description: 'Verifiable Python integration case using LangChain components (langchain_core and langchain_ollama). Executes structured tools, prompt templates, and LCEL on local Ollama, strictly separating empirical observations, statistical forecasts, and synthesized text.',
      scope: 'Scope:',
      scopeNational: 'National (KEN)',
      cutoff: 'Cutoff:',
      placeholder: 'Enter an epidemiological query for the LangChain agent...',
      btnExecute: 'Execute LangChain',
      suggestionsLabel: 'Suggestions:',
      delimitationTitle: 'Epidemiological & Hospital Delimitation:',
      delimitationBody: 'Observed cases and forecasts strictly correspond to the NATIONAL Kenya aggregate (KEN, county_code=0). ICU beds represent descriptive static inventory from Barasa et al. (2020) S1 Table. No county case disaggregation or clinical ICU conversion model exists to infer saturation.',
      panel1Title: '1. SQLite Observations (National KEN, @tool)',
      panel2Title: '2. Statistical Forecasts (National KEN, @tool)',
      panel3Title: '3. LangChain Core Synthesis (Ollama)',
      panelMetaTitle: 'LangChain Execution Traceability (FastAPI Backend)',
      invokedTag: '✓ Invoked:',
      cutoffLabel: 'Cutoff Date:',
      casesObsLabel: 'National Cases (yt):',
      deathsObsLabel: 'National Deaths:',
      stringencyLabel: 'Stringency Index:',
      targetWeekLabel: 'Target Week (t+1):',
      persistenceLabel: 'Naive Persistence (Champion t+1):',
      actualObsLabel: 'National Actual Observed (t+1):',
      rfLabel: 'National RF (Sensitivity):',
      rfWarning: '⚠ Non-causal sensitivity on frozen covariates',
      notAvailable: 'Not available',
      casesUnit: 'cases',
      modeLabel: 'Mode:',
      orchestrationLabel: 'Orchestration:',
      executorLabel: 'Executor:',
      toolsNotice: 'Tools are structured using LangChain Core @tool and invoked in an orchestrated LCEL pipeline.',
      componentsLabel: 'LangChain Components Executed in LCEL Pipeline:',
      toolsInvokedLabel: 'Structured Tools (@tool) Invoked:',
      errConnection: 'Error querying LangChain agent:'
    },
    sw: {
      title: 'Wakala wa Ushirikiano wa LangChain',
      badge: 'Bomba la LCEL • Vyombo @tool • Ollama ya Ndani',
      description: 'Mfano wa ushirikiano unaoweza kuthibitishwa katika Python ukitumia LangChain (langchain_core na langchain_ollama). Hutekeleza vyombo maalum, violezo vya prompt, na LCEL juu ya Ollama ya ndani, ikitenganisha wazi takwimu halisi, utabiri, na muhtasari.',
      scope: 'Eneo:',
      scopeNational: 'Kitaifa (KEN)',
      cutoff: 'Kipindi:',
      placeholder: 'Andika swali la magonjwa kwa ajili ya wakala wa LangChain...',
      btnExecute: 'Tekeleza LangChain',
      suggestionsLabel: 'Mapendekezo:',
      delimitationTitle: 'Mipaka ya Magonjwa na Hospitali:',
      delimitationBody: 'Takwimu za visa na utabiri zinahusu jumla ya KITAIFA ya Kenya (KEN, county_code=0). Vitanda vya ICU vinatokana na orodha ya Barasa et al. (2020) S1 Table. Hakuna muundo wa kugawa visa kwa kaunti wala kubaini msongamano wa vitanda vya ICU.',
      panel1Title: '1. Takwimu Halisi za SQLite (Kitaifa KEN, @tool)',
      panel2Title: '2. Utabiri wa Kitakwimu (Kitaifa KEN, @tool)',
      panel3Title: '3. Muhtasari wa LangChain Core (Ollama)',
      panelMetaTitle: 'Ufuatiliaji wa Utekelezaji wa LangChain (FastAPI Backend)',
      invokedTag: '✓ Imetumika:',
      cutoffLabel: 'Tarehe ya Kukata:',
      casesObsLabel: 'Visa vya Kitaifa (yt):',
      deathsObsLabel: 'Vifo vya Kitaifa:',
      stringencyLabel: 'Kiwango cha Kuzuia:',
      targetWeekLabel: 'Wiki Inayolengwa (t+1):',
      persistenceLabel: 'Persistence Naive (Bingwa t+1):',
      actualObsLabel: 'Visa Halisi Vilivyoonekana (t+1):',
      rfLabel: 'RF ya Kitaifa (Usikivu):',
      rfWarning: '⚠ Usikivu usio wa sababu juu ya vigezo vilivyogandishwa',
      notAvailable: 'Haipatikani',
      casesUnit: 'visa',
      modeLabel: 'Hali:',
      orchestrationLabel: 'Upangaji:',
      executorLabel: 'Mtekelezaji:',
      toolsNotice: 'Vyombo vimepangwa kupitia @tool ya LangChain Core na huendeshwa kwa mpangilio katika bomba la LCEL.',
      componentsLabel: 'Vipengele vya LangChain Vilivyotekelezwa:',
      toolsInvokedLabel: 'Vyombo Maalum (@tool) Vilivyotumika:',
      errConnection: 'Hitilafu wakati wa kuwasiliana na wakala wa LangChain:'
    }
  }[lang] || {
    title: 'Agente Integrador LangChain',
    badge: 'LCEL Pipeline • Tools @tool • Ollama Local',
    description: 'Caso integrador verificable en Python con componentes de LangChain.',
    scope: 'Ámbito:',
    scopeNational: 'Nacional (KEN)',
    cutoff: 'Corte:',
    placeholder: 'Ingrese una consulta epidemiológica para el agente LangChain...',
    btnExecute: 'Ejecutar LangChain',
    suggestionsLabel: 'Sugerencias:',
    delimitationTitle: 'Delimitación Epidemiológica y Hospitalaria:',
    delimitationBody: 'Cifras agregadas de nivel nacional.',
    panel1Title: '1. Observaciones SQLite (Nacional KEN, @tool)',
    panel2Title: '2. Pronósticos Estadísticos (Nacional KEN, @tool)',
    panel3Title: '3. Síntesis LangChain Core (Ollama)',
    panelMetaTitle: 'Trazabilidad de Ejecución LangChain (Backend FastAPI)',
    invokedTag: '✓ Invocado:',
    cutoffLabel: 'Fecha de Corte:',
    casesObsLabel: 'Casos Nacionales (yt):',
    deathsObsLabel: 'Muertes Nacionales:',
    stringencyLabel: 'Índice Rigurosidad:',
    targetWeekLabel: 'Semana Proyectada (t+1):',
    persistenceLabel: 'Persistencia Naive (Campeón t+1):',
    actualObsLabel: 'Observado Real Nacional (t+1):',
    rfLabel: 'RF Nacional (Sensibilidad):',
    rfWarning: '⚠ Sensibilidad no causal',
    notAvailable: 'No disponible',
    casesUnit: 'casos',
    modeLabel: 'Modo:',
    orchestrationLabel: 'Orquestación:',
    executorLabel: 'Ejecutor:',
    toolsNotice: 'Herramientas estructuradas @tool.',
    componentsLabel: 'Componentes LangChain Ejecutados:',
    toolsInvokedLabel: 'Herramientas Invocadas:',
    errConnection: 'Error:'
  };

  const suggestedQueriesMap = {
    es: [
      '¿Cuál es el pronóstico nacional para la semana siguiente y qué camas UCI están registradas?',
      'Compara la persistencia nacional con la sensibilidad de Random Forest para este corte',
      '¿Qué capacidad descriptiva de camas UCI registra Kiambu frente al total nacional?',
    ],
    en: [
      'What is the national forecast for next week and what ICU beds are registered?',
      'Compare national naive persistence with Random Forest sensitivity for this cutoff',
      'What descriptive ICU bed capacity is recorded for Kiambu versus the national total?',
    ],
    sw: [
      'Utabiri wa kitaifa kwa wiki ijayo ni upi na ni vitanda vingapi vya ICU vimesajiliwa?',
      'Linganisha persistence ya kitaifa na usikivu wa Random Forest kwa tarehe hii',
      'Uwezo gani wa vitanda vya ICU umesajiliwa Kiambu kulinganisha na taifa?',
    ]
  };

  const suggestedQueries = suggestedQueriesMap[lang] || suggestedQueriesMap.es;

  const handleQuery = async (customQuery?: string) => {
    const q = customQuery || query;
    if (!q.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const data = await ApiClient.queryLangChainAgent(q, cutoffDate, countyCode, lang);
      setResult(data);
    } catch (err: any) {
      setError(`${t.errConnection} ${err.message || err}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Encabezado */}
      <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/60 border-slate-800' : 'bg-white border-slate-200'} shadow-sm`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
                <Sparkles size={20} />
              </span>
              <h2 className={`text-xl font-bold tracking-tight ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
                {t.title}
              </h2>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                {t.badge}
              </span>
            </div>
            <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
              {t.description}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Selector de Condado */}
            <div className="flex items-center gap-1.5">
              <span className={`text-xs font-medium ${darkMode ? 'text-slate-400' : 'text-slate-700'}`}>{t.scope}</span>
              <select
                id="select_langchain_county"
                value={countyCode}
                onChange={(e) => setCountyCode(Number(e.target.value))}
                className={`text-xs px-2.5 py-1.5 rounded-xl border font-mono ${
                  darkMode ? 'bg-slate-800 border-slate-700 text-slate-200' : 'bg-slate-100 border-slate-300 text-slate-900 font-semibold'
                }`}
              >
                <option value={0}>{t.scopeNational}</option>
                <option value={47}>Nairobi City (47)</option>
                <option value={22}>Kiambu (22)</option>
                <option value={32}>Nakuru (32)</option>
                <option value={28}>Mombasa (28)</option>
              </select>
            </div>

            {/* Selector de Fecha */}
            <div className="flex items-center gap-1.5">
              <span className={`text-xs font-medium ${darkMode ? 'text-slate-400' : 'text-slate-700'}`}>{t.cutoff}</span>
              <select
                id="select_langchain_cutoff"
                value={cutoffDate}
                onChange={(e) => setCutoffDate(e.target.value)}
                className={`text-xs px-2.5 py-1.5 rounded-xl border font-mono ${
                  darkMode ? 'bg-slate-800 border-slate-700 text-slate-200' : 'bg-slate-100 border-slate-300 text-slate-900 font-semibold'
                }`}
              >
                <option value="2024-07-28">2024-07-28 (Test Final)</option>
                <option value="2024-07-21">2024-07-21 (Test Penúltimo)</option>
                <option value="2023-04-02">2023-04-02 (Inicio Test)</option>
                <option value="2022-12-18">2022-12-18 (Validación)</option>
                <option value="2021-07-11">2021-07-11 (Entrenamiento)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Input de Consulta */}
        <div className="mt-4 flex flex-col sm:flex-row gap-2">
          <input
            id="input_langchain_query"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
            placeholder={t.placeholder}
            className={`flex-1 px-4 py-2.5 rounded-xl text-xs border focus:outline-none focus:ring-2 focus:ring-purple-500/40 ${
              darkMode ? 'bg-slate-950 border-slate-800 text-slate-100 placeholder-slate-500' : 'bg-slate-50 border-slate-300 text-slate-900 placeholder-slate-400 font-medium'
            }`}
          />
          <button
            id="btn_execute_langchain_agent"
            onClick={() => handleQuery()}
            disabled={loading}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-bold flex items-center justify-center gap-2 shadow-lg shadow-purple-500/20 disabled:opacity-50 cursor-pointer"
          >
            {loading ? <Clock className="animate-spin" size={14} /> : <Send size={14} />}
            <span>{t.btnExecute}</span>
          </button>
        </div>

        {/* Consultas Sugeridas */}
        <div className="mt-3 flex flex-wrap gap-2">
          <span className={`text-[10px] self-center ${darkMode ? 'text-slate-400' : 'text-slate-600 font-medium'}`}>{t.suggestionsLabel}</span>
          {suggestedQueries.map((sq, idx) => (
            <button
              key={idx}
              onClick={() => {
                setQuery(sq);
                handleQuery(sq);
              }}
              className={`text-[11px] px-2.5 py-1 rounded-lg border transition cursor-pointer ${
                darkMode
                  ? 'bg-slate-800/80 border-slate-700/60 text-slate-300 hover:bg-slate-800'
                  : 'bg-slate-100 border-slate-300 text-slate-800 hover:bg-slate-200 font-medium'
              }`}
            >
              {sq}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-500 dark:text-rose-400 text-xs flex items-center gap-2 font-medium">
          <AlertTriangle size={16} className="shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* RESULTADOS EN 3 PANELES SEGREGADOS + PANEL DE METADATOS LANGCHAIN */}
      {result && (
        <div className="space-y-4">
          {/* Banner Metodológico: Delimitación Nacional vs Capacidad Condal Descriptiva */}
          <div className={`p-3.5 rounded-xl border text-[11px] flex items-start gap-2.5 ${
            darkMode ? 'bg-indigo-950/30 border-indigo-800/50 text-indigo-200' : 'bg-indigo-50 border-indigo-200 text-indigo-950 font-medium'
          }`}>
            <Info size={16} className="text-indigo-500 shrink-0 mt-0.5" />
            <div className="leading-relaxed">
              <strong>{t.delimitationTitle}</strong> {t.delimitationBody}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Panel 1: Observaciones de la Base (Azul) */}
            <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-blue-950/20 border-blue-900/50' : 'bg-blue-50/70 border-blue-200'}`}>
              <div className="flex items-center gap-2 mb-3">
                <span className="p-1.5 rounded-lg bg-blue-500/20 text-blue-500 dark:text-blue-400">
                  <Database size={16} />
                </span>
                <h3 className="text-xs font-bold text-blue-600 dark:text-blue-400 uppercase tracking-wider font-mono">
                  {t.panel1Title}
                </h3>
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between border-b border-blue-200 dark:border-blue-800/20 pb-1">
                  <span className={darkMode ? 'text-slate-400' : 'text-slate-600 font-medium'}>{t.cutoffLabel}</span>
                  <span className={`font-mono font-bold ${darkMode ? 'text-slate-200' : 'text-slate-900'}`}>{result.database_observations.date}</span>
                </div>
                <div className="flex justify-between border-b border-blue-200 dark:border-blue-800/20 pb-1">
                  <span className={darkMode ? 'text-slate-400' : 'text-slate-600 font-medium'}>{t.casesObsLabel}</span>
                  <span className="font-mono font-bold text-blue-600 dark:text-blue-300">{result.database_observations.observed_weekly_cases} {t.casesUnit}</span>
                </div>
                <div className="flex justify-between border-b border-blue-200 dark:border-blue-800/20 pb-1">
                  <span className={darkMode ? 'text-slate-400' : 'text-slate-600 font-medium'}>{t.deathsObsLabel}</span>
                  <span className={`font-mono ${darkMode ? 'text-slate-200' : 'text-slate-900 font-semibold'}`}>{result.database_observations.observed_weekly_deaths}</span>
                </div>
                <div className="flex justify-between border-b border-blue-200 dark:border-blue-800/20 pb-1">
                  <span className={darkMode ? 'text-slate-400' : 'text-slate-600 font-medium'}>{t.stringencyLabel}</span>
                  <span className={`font-mono ${darkMode ? 'text-slate-200' : 'text-slate-900 font-semibold'}`}>{result.database_observations.stringency_index_lag1}</span>
                </div>
                <div className="pt-1">
                  <span className="text-[10px] text-blue-600 dark:text-blue-400/80 font-mono font-bold">
                    {t.invokedTag} tool_query_observations
                  </span>
                </div>
              </div>
            </div>

            {/* Panel 2: Pronósticos del Modelo (Verde/Ámbar) */}
            <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-emerald-950/20 border-emerald-900/50' : 'bg-emerald-50/70 border-emerald-200'}`}>
              <div className="flex items-center gap-2 mb-3">
                <span className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-500 dark:text-emerald-400">
                  <TrendingUp size={16} />
                </span>
                <h3 className="text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider font-mono">
                  {t.panel2Title}
                </h3>
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between border-b border-emerald-200 dark:border-emerald-800/20 pb-1">
                  <span className={darkMode ? 'text-slate-400' : 'text-slate-600 font-medium'}>{t.targetWeekLabel}</span>
                  <span className={`font-mono font-bold ${darkMode ? 'text-slate-200' : 'text-slate-900'}`}>{result.model_forecasts.target_week}</span>
                </div>
                <div className="flex justify-between border-b border-emerald-200 dark:border-emerald-800/20 pb-1">
                  <span className={darkMode ? 'text-slate-400' : 'text-slate-600 font-medium'}>{t.persistenceLabel}</span>
                  <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400">
                    {result.model_forecasts.persistence_prediction_cases} {t.casesUnit}
                  </span>
                </div>
                <div className="flex justify-between border-b border-emerald-200 dark:border-emerald-800/20 pb-1">
                  <span className={darkMode ? 'text-slate-400' : 'text-slate-600 font-medium'}>{t.actualObsLabel}</span>
                  <span className={`font-mono font-bold ${darkMode ? 'text-slate-200' : 'text-slate-900'}`}>
                    {result.model_forecasts.observed_target_actual !== null 
                      ? `${result.model_forecasts.observed_target_actual} ${t.casesUnit}` 
                      : t.notAvailable}
                  </span>
                </div>
                <div className="flex justify-between border-b border-emerald-200 dark:border-emerald-800/20 pb-1">
                  <span className={darkMode ? 'text-slate-400' : 'text-slate-600 font-medium'}>{t.rfLabel}</span>
                  <span className="font-mono font-bold text-amber-600 dark:text-amber-400">
                    {result.model_forecasts.random_forest_sensitivity_cases} {t.casesUnit}
                  </span>
                </div>
                <div className="pt-1">
                  <span className="text-[10px] text-amber-700 dark:text-amber-400/80 font-mono font-bold">
                    {t.rfWarning}
                  </span>
                </div>
              </div>
            </div>

            {/* Panel 3: Texto Generado por LangChain (Púrpura) */}
            <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-purple-950/20 border-purple-900/50' : 'bg-purple-50/70 border-purple-200'}`}>
              <div className="flex items-center gap-2 mb-3">
                <span className="p-1.5 rounded-lg bg-purple-500/20 text-purple-500 dark:text-purple-400">
                  <Bot size={16} />
                </span>
                <h3 className="text-xs font-bold text-purple-600 dark:text-purple-400 uppercase tracking-wider font-mono">
                  {t.panel3Title}
                </h3>
              </div>
              <div className={`text-xs space-y-2 whitespace-pre-wrap leading-relaxed font-sans max-h-56 overflow-y-auto pr-1 ${darkMode ? 'text-slate-200' : 'text-slate-800 font-medium'}`}>
                {result.generated_text}
              </div>
            </div>
          </div>

          {/* Panel 4: Metadatos Transparentes de LangChain */}
          <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/80 border-slate-800' : 'bg-slate-100 border-slate-300'}`}>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4 pb-2 border-b border-slate-300 dark:border-slate-700/40">
              <div className="flex items-center gap-2">
                <Cpu size={16} className="text-purple-500 dark:text-purple-400" />
                <h3 className={`text-xs font-bold font-mono uppercase tracking-wider ${darkMode ? 'text-slate-300' : 'text-slate-800'}`}>
                  {t.panelMetaTitle}
                </h3>
              </div>
              <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
                <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-700 dark:text-purple-300 border border-purple-500/30 font-bold">
                  {t.modeLabel} {result.langchain_metadata.execution_mode}
                </span>
                <span className={`flex items-center gap-1 font-semibold ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                  <Clock size={12} /> {result.langchain_metadata.execution_time_ms} ms
                </span>
              </div>
            </div>

            {/* Explicación Técnica del Modo */}
            <div className={`p-3 rounded-xl mb-4 text-[11px] flex items-start gap-2 ${
              darkMode ? 'bg-slate-950/50 text-slate-300 border border-slate-800' : 'bg-white text-slate-800 border border-slate-300 shadow-xs'
            }`}>
              <Info size={15} className="text-purple-500 dark:text-purple-400 shrink-0 mt-0.5" />
              <div>
                <strong>{t.orchestrationLabel}</strong> {result.langchain_metadata.orchestration_type}.<br />
                <strong>{t.executorLabel}</strong> {result.langchain_metadata.provider}. {t.toolsNotice}
              </div>
            </div>

            {/* Componentes de LangChain Ejecutados */}
            <div className="mb-4">
              <span className={`text-[11px] font-mono block mb-1.5 font-bold ${darkMode ? 'text-slate-400' : 'text-slate-700'}`}>
                {t.componentsLabel}
              </span>
              <div className="flex flex-wrap gap-1.5">
                {result.langchain_metadata.components_executed.map((comp, idx) => (
                  <span
                    key={idx}
                    className={`text-[10px] font-mono px-2 py-0.5 rounded-lg border flex items-center gap-1 font-medium ${
                      darkMode ? 'bg-slate-800 text-slate-300 border-slate-700/80' : 'bg-white text-slate-800 border-slate-300'
                    }`}
                  >
                    <FileCode2 size={11} className="text-purple-500 dark:text-purple-400" />
                    {comp}
                  </span>
                ))}
              </div>
            </div>

            {/* Herramientas Invocadas */}
            <div>
              <span className={`text-[11px] font-mono block mb-1.5 font-bold ${darkMode ? 'text-slate-400' : 'text-slate-700'}`}>
                {t.toolsInvokedLabel}
              </span>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                {result.langchain_metadata.tools_invoked.map((toolCall, idx) => (
                  <div
                    key={idx}
                    className={`p-2.5 rounded-xl border text-[11px] ${
                      darkMode ? 'bg-slate-950/60 border-slate-800' : 'bg-white border-slate-300 shadow-xs'
                    }`}
                  >
                    <div className="font-mono font-bold text-purple-600 dark:text-purple-400 flex items-center gap-1 mb-1">
                      <Wrench size={12} />
                      {toolCall.tool_name}
                    </div>
                    <div className={`text-[10px] font-mono mb-1 truncate ${darkMode ? 'text-slate-400' : 'text-slate-600 font-medium'}`}>
                      Args: {JSON.stringify(toolCall.args)}
                    </div>
                    <div className={`text-[10px] ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                      {toolCall.output_summary}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
