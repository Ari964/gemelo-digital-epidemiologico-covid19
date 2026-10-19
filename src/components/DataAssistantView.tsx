import React, { useState } from 'react';
import { 
  Bot, 
  Database, 
  TrendingUp, 
  Sparkles, 
  Wrench, 
  BookOpen, 
  Send, 
  AlertCircle,
  HelpCircle,
  CheckCircle2,
  Calendar,
  Layers
} from 'lucide-react';
import { ApiClient } from '../services/apiClient';
import { DataAssistantResponseDTO } from '../types/apiContract';
import { LanguageCode } from '../i18n/translations';

interface DataAssistantViewProps {
  darkMode: boolean;
  lang?: LanguageCode;
}

export const DataAssistantView: React.FC<DataAssistantViewProps> = ({ darkMode, lang = 'es' }) => {
  const [query, setQuery] = useState<string>('');
  const [cutoffDate, setCutoffDate] = useState<string>('2024-07-28');
  const [loading, setLoading] = useState<boolean>(false);
  const [response, setResponse] = useState<DataAssistantResponseDTO | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Consultas sugeridas adaptadas según el idioma seleccionado
  const suggestedQueriesMap = {
    es: [
      {
        label: 'Corte 28-Jul-2024 y pronóstico',
        query: '¿Qué casos observados hay para el corte del 28 de julio de 2024 y qué pronostica la persistencia para la semana siguiente?'
      },
      {
        label: 'Corte 21-Jul-2024 (Fecha alternativa)',
        query: 'Consultar el corte histórico del 21 de julio de 2024 y comparar la persistencia con el valor observado en la base de datos.'
      },
      {
        label: 'Capacidad hospitalaria condados',
        query: '¿Qué información empírica de población y camas UCI registra el gemelo digital para los principales condados de Kenia?'
      },
      {
        label: 'Superioridad de la persistencia',
        query: '¿Por qué el modelo de persistencia supera a Random Forest en el periodo de prueba 2023-2024?'
      }
    ],
    en: [
      {
        label: 'Cutoff 28-Jul-2024 and forecast',
        query: 'What observed cases exist for the July 28 2024 cutoff and what does naive persistence forecast for next week?'
      },
      {
        label: 'Cutoff 21-Jul-2024 (Alternative date)',
        query: 'Check historical cutoff July 21 2024 and compare naive persistence against observed value in database.'
      },
      {
        label: 'County hospital capacity',
        query: 'What empirical population and ICU bed capacity data does the digital twin store for Kenya counties?'
      },
      {
        label: 'Persistence baseline superiority',
        query: 'Why does naive persistence outperform Random Forest during the 2023-2024 blind test period?'
      }
    ],
    sw: [
      {
        label: 'Tarehe 28-Jul-2024 na utabiri',
        query: 'Kesi gani zilizopimwa zipo tarehe 28 Julai 2024 na mtindo wa mwendelezo unatabiri nini kwa wiki ijayo?'
      },
      {
        label: 'Tarehe 21-Jul-2024 (Mbadala)',
        query: 'Angalia tarehe ya kihistoria ya 21 Julai 2024 na ulinganishe mwendelezo na thamani iliyopimwa.'
      },
      {
        label: 'Uwezo wa hospitali za kaunti',
        query: 'Takwimu gani za idadi ya watu na vitanda vya ICU pacha wa kidijitali anahifadhi kwa kaunti za Kenya?'
      },
      {
        label: 'Ubora wa mwendelezo',
        query: 'Kwa nini mtindo wa mwendelezo unashinda Random Forest katika kipindi cha jaribio cha 2023-2024?'
      }
    ]
  };

  const suggestedQueries = suggestedQueriesMap[lang] || suggestedQueriesMap.es;

  const handleExecuteQuery = async (customQuery?: string) => {
    const q = customQuery || query;
    if (!q.trim()) return;
    
    setLoading(true);
    setError(null);
    try {
      const res = await ApiClient.queryDataAssistant(q, cutoffDate, 0);
      setResponse(res);
    } catch (err: any) {
      setError('Error al consultar el Asistente de Datos: ' + (err.message || 'Error del servidor'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Encabezado del Módulo */}
      <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-sm`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                Módulo Asistente
              </span>
              <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Trazabilidad Factual
              </span>
            </div>
            <h2 className="text-xl font-bold tracking-tight flex items-center gap-2">
              <Bot size={24} className="text-indigo-400" />
              Asistente de datos del gemelo digital
            </h2>
            <p className={`text-sm mt-1 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
              Consulta unificada con separación estricta entre observaciones de la base (SQLite), pronósticos del modelo (Persistencia / Sensibilidad) y síntesis explicativa generada por IA.
            </p>
          </div>
        </div>

        {/* Formulario de Entrada */}
        <div className="mt-5 space-y-3">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <div className="flex-1 relative">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleExecuteQuery()}
                placeholder="Escriba su consulta epidemiológica o elija una sugerida abajo..."
                className={`w-full px-4 py-2.5 rounded-xl border text-sm transition outline-none ${
                  darkMode 
                    ? 'bg-slate-800/80 border-slate-700 text-slate-100 placeholder-slate-500 focus:border-indigo-500' 
                    : 'bg-slate-50 border-slate-300 text-slate-900 placeholder-slate-400 focus:border-indigo-500'
                }`}
              />
            </div>

            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-slate-700/60 bg-slate-800/50">
                <Calendar size={14} className="text-slate-400" />
                <span className="text-xs text-slate-400">Corte:</span>
                <input
                  type="date"
                  value={cutoffDate}
                  onChange={(e) => setCutoffDate(e.target.value)}
                  className={`bg-transparent text-xs font-mono outline-none ${darkMode ? 'text-slate-200' : 'text-slate-800'}`}
                />
              </div>

              <button
                onClick={() => handleExecuteQuery()}
                disabled={loading || !query.trim()}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition cursor-pointer ${
                  loading || !query.trim()
                    ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                    : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/20'
                }`}
              >
                <Send size={15} />
                {loading ? 'Consultando...' : 'Consultar'}
              </button>
            </div>
          </div>

          {/* Consultas Sugeridas */}
          <div className="flex flex-wrap items-center gap-2 pt-1">
            <span className="text-[11px] text-slate-500 flex items-center gap-1">
              <HelpCircle size={12} /> Sugerencias de prueba:
            </span>
            {suggestedQueries.map((item, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setQuery(item.query);
                  handleExecuteQuery(item.query);
                }}
                className={`text-xs px-2.5 py-1 rounded-lg border transition cursor-pointer ${
                  darkMode 
                    ? 'bg-slate-800/60 hover:bg-slate-800 border-slate-700/60 text-slate-300' 
                    : 'bg-slate-100 hover:bg-slate-200 border-slate-200 text-slate-700'
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center gap-2">
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      {/* RESULTADO ESTRUCTURADO EN 3 NIVELES RIGUROSOS + METADATOS DE TRAZABILIDAD */}
      {response && (
        <div className="space-y-6">
          {/* BARRA DE HERRAMIENTAS Y FUENTES CONSULTADAS (REQUERIMIENTO 2: NO TRAZA DE PENSAMIENTO) */}
          <div className={`p-4 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-sm`}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div className="flex items-center gap-2 text-xs font-bold text-indigo-400 mb-2">
                  <Wrench size={15} />
                  Herramientas Utilizadas (Pipeline Interno)
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {response.tools_used.map((tool, i) => (
                    <span
                      key={i}
                      className="px-2.5 py-1 rounded-md text-[11px] font-mono bg-indigo-500/10 text-indigo-300 border border-indigo-500/20"
                    >
                      {tool}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <div className="flex items-center gap-2 text-xs font-bold text-emerald-400 mb-2">
                  <BookOpen size={15} />
                  Fuentes Consultadas (Comprobables)
                </div>
                <ul className="space-y-1">
                  {response.sources_consulted.map((source, i) => (
                    <li key={i} className="text-xs text-slate-400 flex items-start gap-1.5">
                      <CheckCircle2 size={12} className="text-emerald-400 shrink-0 mt-0.5" />
                      <span>{source}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* 3 PANELES CON DISTINCIÓN COGNITIVA ESTRICTA */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* PANEL 1: OBSERVACIONES DE LA BASE DE DATOS (EMPÍRICO) */}
            <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-blue-500/30' : 'bg-white border-blue-200'} shadow-md`}>
              <div className="flex items-center gap-2 pb-3 mb-3 border-b border-slate-800/60">
                <Database size={18} className="text-blue-400" />
                <h3 className="text-sm font-bold text-blue-400">
                  1. Observaciones de la Base (SQLite)
                </h3>
              </div>
              <div className="space-y-3 text-xs">
                <div className="p-3 rounded-xl bg-slate-800/50 border border-slate-700/50">
                  <div className="text-slate-400 font-medium">Registros Históricos Nacionales:</div>
                  <div className="text-base font-bold font-mono text-white mt-0.5">
                    {response.database_observations.total_historical_records} semanas
                  </div>
                  <div className="text-[10px] text-slate-400 mt-1">
                    Periodo: {response.database_observations.date_range?.earliest} al {response.database_observations.date_range?.latest}
                  </div>
                </div>

                {response.database_observations.cutoff_observation && (
                  <div className="p-3 rounded-xl bg-slate-800/50 border border-slate-700/50 space-y-1">
                    <div className="font-semibold text-slate-300">
                      Corte Evaluado: {response.database_observations.cutoff_observation.date}
                    </div>
                    {response.database_observations.cutoff_observation.weekly_cases !== undefined && (
                      <>
                        <div className="flex justify-between text-slate-300">
                          <span>Casos positivos semanales:</span>
                          <span className="font-mono font-bold text-blue-300">
                            {response.database_observations.cutoff_observation.weekly_cases}
                          </span>
                        </div>
                        <div className="flex justify-between text-slate-300">
                          <span>Casos suavizados:</span>
                          <span className="font-mono text-slate-300">
                            {response.database_observations.cutoff_observation.weekly_cases_smoothed}
                          </span>
                        </div>
                        <div className="flex justify-between text-slate-300">
                          <span>Fallecidos semanales:</span>
                          <span className="font-mono text-slate-300">
                            {response.database_observations.cutoff_observation.weekly_deaths}
                          </span>
                        </div>
                      </>
                    )}
                  </div>
                )}

                {response.database_observations.top_counties_by_population && (
                  <div className="p-3 rounded-xl bg-slate-800/50 border border-slate-700/50 space-y-1.5">
                    <div className="font-semibold text-slate-300">Top Condados (Demografía KNBS):</div>
                    {response.database_observations.top_counties_by_population.map((c: any, idx: number) => (
                      <div key={idx} className="flex justify-between text-[11px] text-slate-300">
                        <span>{c.name}:</span>
                        <span className="font-mono">{c.population.toLocaleString()} hab ({c.icu_beds} camas UCI descriptivas no verif.)</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* PANEL 2: PRONÓSTICOS DEL MODELO (MATEMÁTICO/ESTADÍSTICO) */}
            <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-emerald-500/30' : 'bg-white border-emerald-200'} shadow-md`}>
              <div className="flex items-center gap-2 pb-3 mb-3 border-b border-slate-800/60">
                <TrendingUp size={18} className="text-emerald-400" />
                <h3 className="text-sm font-bold text-emerald-400">
                  2. Pronósticos del Modelo Estadístico
                </h3>
              </div>
              <div className="space-y-3 text-xs">
                {/* Persistencia Principal */}
                <div className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-500/30 space-y-1">
                  <div className="text-[11px] uppercase tracking-wider text-emerald-300 font-bold">
                    Modelo Principal (Persistencia)
                  </div>
                  <div className="text-xl font-extrabold font-mono text-white">
                    {response.model_forecasts.main_forecast_persistence?.predicted_weekly_cases?.toFixed(1)} casos
                  </div>
                  <div className="text-[10px] text-slate-400">
                    Semana objetivo: {response.model_forecasts.target_week_predicted}
                  </div>
                  <div className="text-[10px] text-emerald-300/80">
                    Regla: y_{'{t+1}'} = y_t ({response.model_forecasts.main_forecast_persistence?.lag_value_used} casos)
                  </div>
                </div>

                {/* Random Forest Sensibilidad */}
                <div className="p-3 rounded-xl bg-amber-950/20 border border-amber-500/30 space-y-1">
                  <div className="text-[11px] uppercase tracking-wider text-amber-300 font-bold">
                    Sensibilidad Hipotética (RF v1.0)
                  </div>
                  <div className="text-lg font-mono font-bold text-amber-300">
                    {response.model_forecasts.hypothetical_sensitivity_rf?.predicted_cases?.toFixed(2)} casos
                  </div>
                  <div className="text-[10px] text-slate-400">
                    {response.model_forecasts.hypothetical_sensitivity_rf?.caution}
                  </div>
                </div>

                <div className="text-[10px] text-slate-400 italic">
                  Ámbito: {response.model_forecasts.scope}
                </div>
              </div>
            </div>

            {/* PANEL 3: TEXTO GENERADO POR IA (SÍNTESIS ANALÍTICA) */}
            <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-purple-500/30' : 'bg-white border-purple-200'} shadow-md`}>
              <div className="flex items-center gap-2 pb-3 mb-3 border-b border-slate-800/60">
                <Sparkles size={18} className="text-purple-400" />
                <h3 className="text-sm font-bold text-purple-400">
                  3. Texto Generado por IA (Síntesis)
                </h3>
              </div>
              <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50 text-xs text-slate-200 leading-relaxed whitespace-pre-line">
                {response.ai_interpretation}
              </div>
              <div className="mt-3 text-[10px] text-slate-500 italic">
                Nota: Esta síntesis no contiene alucinaciones; está generada automáticamente a partir de los datos exactos del SQLite y del motor de persistencia.
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
