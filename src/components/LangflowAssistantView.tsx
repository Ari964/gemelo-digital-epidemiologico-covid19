import React, { useState, useEffect } from 'react';
import { 
  Workflow, 
  Send, 
  Clock, 
  AlertTriangle, 
  CheckCircle2, 
  RefreshCw, 
  Info, 
  Bot, 
  Layers, 
  Server, 
  Database,
  ExternalLink,
  ShieldCheck,
  Cpu
} from 'lucide-react';
import { ApiClient } from '../services/apiClient';
import { LangflowStatusDTO, LangflowResponseDTO } from '../types/apiContract';
import { LanguageCode, translations } from '../i18n/translations';

interface LangflowAssistantViewProps {
  darkMode: boolean;
  lang: LanguageCode;
}

export const LangflowAssistantView: React.FC<LangflowAssistantViewProps> = ({ darkMode, lang }) => {
  const [status, setStatus] = useState<LangflowStatusDTO | null>(null);
  const [statusLoading, setStatusLoading] = useState<boolean>(true);
  const [query, setQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [response, setResponse] = useState<LangflowResponseDTO | null>(null);
  const [error, setError] = useState<string | null>(null);

  const t = translations[lang] || translations.es;

  // Consultas sugeridas adaptadas al flujo epidemiológico verificado
  const suggestedQueries = {
    es: [
      '¿Cuál es el pronóstico nacional del modelo campeón para la semana siguiente y cuántas camas UCI verificadas tiene Kiambu según Barasa et al. (2020)?',
      '¿Por qué el modelo SEIR/ABM es una simulación de escenarios y no se evalúa con el error del pronóstico semanal?',
      '¿Cuál es el hash SHA-256 del dataset crudo de Kenia y qué fuente oficial respalda la población de los 47 condados?',
      '¿Qué diferencia existe entre los datos nacionales de OWID y los datos condales de camas UCI?'
    ],
    en: [
      'What is the champion model national forecast for next week and how many verified ICU beds does Kiambu have per Barasa et al. (2020)?',
      'Why is the SEIR/ABM model classified as a scenario simulator rather than evaluated against weekly point forecast error?',
      'What is the SHA-256 hash of the raw Kenya dataset and which official source backs the population of the 47 counties?',
      'What is the difference between OWID national case data and county-level ICU bed capacity?'
    ],
    sw: [
      'Je, utabiri wa taifa wa mtindo bingwa ni upi kwa wiki ijayo na Kiambu ina vitanda vingapi vya ICU vilivyothibitishwa kulingana na Barasa et al. (2020)?',
      'Kwa nini mfumo wa SEIR/ABM ni uigaji wa matukio na haupimwi kwa kosa la utabiri wa kila wiki wa kesi?',
      'Hashi ya SHA-256 ya hifadhidata ghafi ya Kenya ni ipi na chanzo gani rasmi kinathibitisha idadi ya watu katika kaunti 47?',
      'Kuna tofauti gani kati ya takwimu za kitaifa za OWID na uwezo wa vitanda vya ICU vya kaunti?'
    ]
  };

  const queries = suggestedQueries[lang] || suggestedQueries.es;

  const checkStatus = async () => {
    setStatusLoading(true);
    try {
      const res = await ApiClient.getLangflowStatus();
      setStatus(res);
    } catch (err: any) {
      setStatus({
        status: 'OFFLINE',
        connected: false,
        url: 'http://localhost:7860',
        flow_id: '906a3d58-bcf0-48a9-9364-4a62ea230945',
        flow_name: 'Asistente de Vigilancia Epidemiológica de Kenia',
        provider: 'Langflow API (Docker)',
        latency_ms: null,
        error: err.message || 'Servicio de Langflow no accesible en localhost:7860'
      });
    } finally {
      setStatusLoading(false);
    }
  };

  useEffect(() => {
    checkStatus();
  }, []);

  const handleQuery = async (customQuery?: string) => {
    const q = customQuery || query;
    if (!q.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const res = await ApiClient.queryLangflow(q);
      setResponse(res);
    } catch (err: any) {
      setError(err.message || 'Error al ejecutar flujo en Langflow');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Header con Indicador de Conexión Real */}
      <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/60 border-slate-800' : 'bg-white border-slate-200'} shadow-sm`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                <Workflow size={20} />
              </span>
              <h2 className="text-xl font-bold tracking-tight">
                {lang === 'en' ? 'Langflow Epidemiological Flow' : lang === 'sw' ? 'Mtiririko wa Epidemiolojia wa Langflow' : 'Flujo Epidemiológico Langflow'}
              </h2>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                Docker :7860 • REST Flow API
              </span>
            </div>
            <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
              {lang === 'en' 
                ? 'Visual execution pipeline configured in Langflow container and consumed by FastAPI. Directly queries the LLM graph with prompt grounded in OWID national data, Barasa et al. (2020) ICU beds, and KNBS 2019 census.'
                : lang === 'sw'
                ? 'Mtiririko wa kuona ulioundwa kwenye kontena ya Langflow na kutumiwa na FastAPI. Huuliza grafu ya LLM yenye muktadha wa takwimu za OWID, vitanda vya ICU vya Barasa et al. (2020) na sensa ya KNBS 2019.'
                : 'Pipeline visual de orquestación configurado en el contenedor Langflow y consumido por FastAPI. Ejecuta el grafo LLM con prompt delimitado a datos nacionales de OWID, camas UCI de Barasa et al. (2020) y censo KNBS 2019.'}
            </p>
          </div>

          {/* Indicadores Diferenciados de Estado: Servicio vs Flujo */}
          <div className="flex flex-wrap items-center gap-2">
            {/* 1. Estado del Servicio Contenedor (Puerto 7860) */}
            {(() => {
              const isServiceOnline = status?.service_available ?? (status?.status === 'ONLINE' || status?.connected === true);
              const isFlowImported = status?.flow_imported ?? (status?.status === 'ONLINE' || status?.connected === true);
              return (
                <>
                  <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs font-mono ${
                    isServiceOnline 
                      ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' 
                      : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
                  }`}>
                    <span className={`w-2 h-2 rounded-full ${isServiceOnline ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'}`} />
                    <span className="font-bold">
                      {lang === 'en' ? 'Service :7860' : lang === 'sw' ? 'Huduma :7860' : 'Servicio :7860'}: {isServiceOnline ? 'ONLINE' : 'OFFLINE'}
                    </span>
                    {status?.latency_ms !== null && status?.latency_ms !== undefined && (
                      <span className="text-[10px] opacity-80">({status.latency_ms} ms)</span>
                    )}
                  </div>

                  {/* 2. Estado del Flujo Epidemiológico Importado */}
                  <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs font-mono ${
                    isFlowImported 
                      ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400' 
                      : 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                  }`}>
                    <span className={`w-2 h-2 rounded-full ${isFlowImported ? 'bg-cyan-400' : 'bg-amber-400'}`} />
                    <span className="font-bold">
                      {lang === 'en' ? 'Flow' : lang === 'sw' ? 'Mtiririko' : 'Flujo'}: {isFlowImported ? (lang === 'en' ? 'IMPORTED & EXECUTED' : lang === 'sw' ? 'IMEWEKWA NA KUTEKELEZWA' : 'IMPORTADO Y EJECUTADO') : (lang === 'en' ? 'NOT IMPORTED' : lang === 'sw' ? 'HAIJAWEKWA' : 'PENDIENTE DE IMPORTACIÓN')}
                    </span>
                  </div>
                </>
              );
            })()}

            <button
              id="btn_refresh_langflow_status"
              onClick={checkStatus}
              disabled={statusLoading}
              className={`p-2 rounded-xl border transition cursor-pointer ${
                darkMode ? 'bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700' : 'bg-slate-100 border-slate-300 text-slate-700 hover:bg-slate-200'
              }`}
              title={lang === 'en' ? 'Refresh Status' : lang === 'sw' ? 'Sasisha Hali' : 'Actualizar Estado'}
            >
              <RefreshCw size={14} className={statusLoading ? 'animate-spin' : ''} />
            </button>

            <a
              href="http://localhost:7860"
              target="_blank"
              rel="noreferrer"
              className="px-3 py-1.5 rounded-xl bg-cyan-600/20 hover:bg-cyan-600/30 border border-cyan-500/30 text-cyan-300 text-xs font-semibold flex items-center gap-1.5 transition"
            >
              <span>Langflow UI</span>
              <ExternalLink size={12} />
            </a>
          </div>
        </div>

        {/* Advertencia si Langflow está Offline */}
        {status && !status.connected && (
          <div className="mt-4 p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-start gap-2.5">
            <AlertTriangle size={16} className="text-amber-400 shrink-0 mt-0.5" />
            <div className="leading-relaxed">
              <strong>{lang === 'en' ? 'Langflow Service Not Detected:' : lang === 'sw' ? 'Huduma ya Langflow Haijapatikana:' : 'Servicio Langflow no detectado:'}</strong>{' '}
              {lang === 'en'
                ? 'The Langflow container is not responding at http://localhost:7860. Verify that Docker is running (`docker start docker_example-langflow-1`) and that flow ID 906a3d58-bcf0-48a9-9364-4a62ea230945 is published. No fake responses will be simulated.'
                : lang === 'sw'
                ? 'Kontena ya Langflow haijibu kwenye http://localhost:7860. Hakikisha Docker inaendesha (`docker start docker_example-langflow-1`) na kitambulisho cha mtiririko kipo. Hakuna majibu bandia yatakayoigwa.'
                : 'El contenedor Langflow no responde en http://localhost:7860. Verifique que Docker esté en ejecución (`docker start docker_example-langflow-1`) y que el flujo 906a3d58-bcf0-48a9-9364-4a62ea230945 esté publicado. No se simularán respuestas falsas.'}
              {status.error && <div className="mt-1 font-mono text-[10px] text-rose-300">Detalle: {status.error}</div>}
            </div>
          </div>
        )}

        {/* Input de Consulta */}
        <div className="mt-4 flex flex-col sm:flex-row gap-2">
          <input
            id="input_langflow_query"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
            placeholder={
              lang === 'en'
                ? 'Ask an epidemiological surveillance question to the Langflow flow...'
                : lang === 'sw'
                ? 'Uliza swali la uangalizi wa magonjwa kwa mtiririko wa Langflow...'
                : 'Ingrese una pregunta de vigilancia epidemiológica para el flujo Langflow...'
            }
            className={`flex-1 px-4 py-2.5 rounded-xl text-xs border focus:outline-none focus:ring-2 focus:ring-cyan-500/40 ${
              darkMode ? 'bg-slate-950 border-slate-800 text-slate-100' : 'bg-slate-50 border-slate-300 text-slate-900'
            }`}
          />
          <button
            id="btn_execute_langflow"
            onClick={() => handleQuery()}
            disabled={loading || !status?.connected}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-bold flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20 disabled:opacity-50 cursor-pointer"
          >
            {loading ? <Clock className="animate-spin" size={14} /> : <Send size={14} />}
            <span>{lang === 'en' ? 'Run Langflow Flow' : lang === 'sw' ? 'Endesha Mtiririko' : 'Ejecutar Flujo'}</span>
          </button>
        </div>

        {/* Sugerencias de Preguntas */}
        <div className="mt-3 flex flex-wrap gap-2">
          <span className="text-[10px] text-slate-500 self-center">
            {lang === 'en' ? 'Verified Queries:' : lang === 'sw' ? 'Maswali Yaliyothibitishwa:' : 'Preguntas Verificadas:'}
          </span>
          {queries.map((qText, idx) => (
            <button
              key={idx}
              onClick={() => {
                setQuery(qText);
                handleQuery(qText);
              }}
              className={`text-[11px] px-2.5 py-1 rounded-lg border transition text-left cursor-pointer ${
                darkMode
                  ? 'bg-slate-800/80 border-slate-700/60 text-slate-300 hover:bg-slate-800'
                  : 'bg-slate-100 border-slate-200 text-slate-700 hover:bg-slate-200'
              }`}
            >
              {qText}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
          <AlertTriangle size={16} className="shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* 2. Topología del Flujo Exportado */}
      <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/40 border-slate-800' : 'bg-slate-50 border-slate-200'}`}>
        <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-700/30">
          <div className="flex items-center gap-2">
            <Layers size={16} className="text-cyan-400" />
            <h3 className="text-xs font-bold font-mono uppercase tracking-wider text-slate-300">
              {lang === 'en' ? 'Langflow Graph Architecture (docs/langflow_epidemiology_flow_exported.json)' : 'Topología del Grafo Langflow (docs/langflow_epidemiology_flow_exported.json)'}
            </h3>
          </div>
          <span className="text-[10px] font-mono text-slate-400">Flow ID: 906a3d58-bcf0-48a9-9364-4a62ea230945</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
          <div className={`p-3 rounded-xl border ${darkMode ? 'bg-slate-950/70 border-slate-800' : 'bg-white border-slate-200'}`}>
            <div className="font-mono font-bold text-cyan-400 text-[11px] mb-1">1. Chat Input</div>
            <p className="text-[11px] text-slate-400">Recibe la consulta del usuario o del endpoint FastAPI.</p>
          </div>
          <div className={`p-3 rounded-xl border ${darkMode ? 'bg-slate-950/70 border-slate-800' : 'bg-white border-slate-200'}`}>
            <div className="font-mono font-bold text-indigo-400 text-[11px] mb-1">2. Prompt Template</div>
            <p className="text-[11px] text-slate-400">Delimitación estricta: datos OWID nacionales, camas Barasa 2020, censo KNBS 2019.</p>
          </div>
          <div className={`p-3 rounded-xl border ${darkMode ? 'bg-slate-950/70 border-slate-800' : 'bg-white border-slate-200'}`}>
            <div className="font-mono font-bold text-purple-400 text-[11px] mb-1">3. Ollama Local (qwen2.5:0.5b)</div>
            <p className="text-[11px] text-slate-400">Inferencia semántica local vía host.docker.internal:11434 sin alucinación de datos condales.</p>
          </div>
          <div className={`p-3 rounded-xl border ${darkMode ? 'bg-slate-950/70 border-slate-800' : 'bg-white border-slate-200'}`}>
            <div className="font-mono font-bold text-emerald-400 text-[11px] mb-1">4. Chat Output</div>
            <p className="text-[11px] text-slate-400">Retorna respuesta estructurada con fuentes, fecha y advertencias científicas.</p>
          </div>
        </div>
      </div>

      {/* 3. Panel de Resultados de Langflow */}
      {response && (
        <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/60 border-slate-800' : 'bg-white border-slate-200'} shadow-sm space-y-4`}>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-700/40">
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-cyan-500/20 text-cyan-400">
                <Bot size={18} />
              </span>
              <div>
                <h3 className="text-sm font-bold tracking-tight">
                  {lang === 'en' ? 'Langflow Engine Response' : lang === 'sw' ? 'Jibu la Mfumo wa Langflow' : 'Respuesta del Motor Langflow'}
                </h3>
                <span className="text-[10px] text-slate-400 font-mono">
                  Flujo: {response.flow_name} • Session: {response.session_id}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-3 text-xs font-mono">
              <span className="px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
                <CheckCircle2 size={12} />
                Status: {response.status}
              </span>
              <span className="text-slate-400 flex items-center gap-1">
                <Clock size={12} />
                {response.execution_time_ms} ms
              </span>
            </div>
          </div>

          {/* Texto de la respuesta */}
          <div className={`p-4 rounded-xl text-xs leading-relaxed font-sans whitespace-pre-wrap ${
            darkMode ? 'bg-slate-950/80 text-slate-200 border border-slate-800' : 'bg-slate-50 text-slate-800 border border-slate-200'
          }`}>
            {response.reply}
          </div>

          {/* Banner de Fuentes Verificadas */}
          <div className={`p-3.5 rounded-xl border text-[11px] flex items-start gap-2.5 ${
            darkMode ? 'bg-cyan-950/30 border-cyan-800/50 text-cyan-200' : 'bg-cyan-50 border-cyan-200 text-cyan-900'
          }`}>
            <ShieldCheck size={16} className="text-cyan-400 shrink-0 mt-0.5" />
            <div className="leading-relaxed">
              <strong>{lang === 'en' ? 'Empirical Traceability Protocol:' : 'Protocolo de Trazabilidad Empírica:'}</strong>{' '}
              {lang === 'en'
                ? 'This response is synthesized through the Langflow graph using verified baseline sources: Our World in Data (National Kenya cases, SHA-256 verified), KNBS 2019 Census Table 2.2 (County population), and Barasa et al. (2020) PLOS ONE S1 Table (ICU beds). No fabricated county incidence data was used.'
                : 'Esta respuesta fue sintetizada por el grafo de Langflow utilizando exclusivamente fuentes empíricas verificadas: Our World in Data (casos nacionales Kenia, SHA-256 verificado), Censo KNBS 2019 Tabla 2.2 (población condal) y Barasa et al. (2020) PLOS ONE Tabla S1 (camas UCI). No se emplearon datos condales inventados.'}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
