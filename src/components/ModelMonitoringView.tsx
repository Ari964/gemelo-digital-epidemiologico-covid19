import React, { useState, useEffect } from 'react';
import { Activity, RefreshCw, CheckCircle2, AlertTriangle, AlertCircle, Info, ShieldCheck, Database } from 'lucide-react';
import { ApiClient } from '../services/apiClient';
import { MonitoringStatusDTO, ActiveModelResponseDTO } from '../types/apiContract';
import { LanguageCode } from '../i18n/translations';

interface ModelMonitoringViewProps {
  darkMode: boolean;
  lang?: LanguageCode;
}

export const ModelMonitoringView: React.FC<ModelMonitoringViewProps> = ({ darkMode, lang = 'es' }) => {
  const [monitoring, setMonitoring] = useState<MonitoringStatusDTO | null>(null);
  const [activeModel, setActiveModel] = useState<ActiveModelResponseDTO | null>(null);
  const [loading, setLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(false);
  const [notes, setNotes] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const [monRes, actRes] = await Promise.all([
        ApiClient.getMonitoringStatus().catch(() => null),
        ApiClient.getActiveModel().catch(() => null)
      ]);
      setMonitoring(monRes);
      setActiveModel(actRes);
    } catch (e: any) {
      setErrorMsg(e.message || 'Error al consultar monitoreo');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleTriggerEvaluation = async () => {
    setEvaluating(true);
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      const result = await ApiClient.triggerManualMonitoring(notes || 'Evaluación manual solicitada desde panel React');
      setMonitoring(result);
      setSuccessMsg('Evaluación de estabilidad y drift completada con éxito.');
      setNotes('');
    } catch (e: any) {
      setErrorMsg(e.message || 'Error al ejecutar evaluación manual');
    } finally {
      setEvaluating(false);
    }
  };

  const getStatusBadge = (status: string | undefined) => {
    switch (status) {
      case 'HEALTHY':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1"><CheckCircle2 size={13} /> Estable (Saludable)</span>;
      case 'WARNING':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center gap-1"><AlertTriangle size={13} /> Alerta de Deriva</span>;
      case 'CRITICAL':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30 flex items-center gap-1"><AlertCircle size={13} /> Deriva Crítica</span>;
      default:
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-slate-500/20 text-slate-400 border border-slate-500/30 flex items-center gap-1"><Info size={13} /> Pendiente / Sin Evaluar</span>;
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold flex items-center gap-2">
            <Activity className="text-blue-500" size={24} />
            Fase 6 (CRISP-DM) — Monitoreo Operativo y Despliegue
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Supervisión manual / bajo demanda del Population Stability Index (PSI) y Kolmogorov-Smirnov sobre el modelo activo.
          </p>
        </div>
        <button
          id="btn_refresh_monitoring"
          onClick={fetchData}
          disabled={loading}
          className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition cursor-pointer border ${
            darkMode ? 'bg-slate-900 border-slate-800 text-slate-300 hover:bg-slate-800' : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
          }`}
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Actualizar Estado
        </button>
      </div>

      {/* Honest Scientific Disclaimer */}
      <div className="p-4 rounded-xl border border-blue-500/30 bg-blue-500/10 text-slate-300 text-xs flex items-start gap-3">
        <Info className="text-blue-400 shrink-0 mt-0.5" size={16} />
        <div>
          <strong className="text-blue-300">Aviso Metodológico de Monitoreo:</strong> Las evaluaciones se realizan <em>bajo demanda / de forma manual</em>.
          No se declaran capacidades de monitoreo continuo en tiempo real no soportadas por la infraestructura actual.
          Los artefactos cuentan con hash SHA-256 para comprobar integridad y trazabilidad de versiones.
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle size={16} className="shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {successMsg && (
        <div className="p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 size={16} className="shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Cards de Estado */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Modelo Desplegado */}
        <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/60 border-slate-800/80' : 'bg-white border-slate-200'} shadow-sm`}>
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Modelo Activo</span>
            <ShieldCheck className="text-indigo-400" size={18} />
          </div>
          {activeModel?.is_active ? (
            <div>
              <h3 className="text-lg font-bold text-slate-100">{activeModel.model_name}</h3>
              <p className="text-xs font-mono text-indigo-400 mt-0.5">Versión: {activeModel.model_version}</p>
              <div className="mt-3 pt-3 border-t border-slate-800/80 text-[11px] text-slate-400 space-y-1">
                <div>Activado por: <span className="text-slate-200">{activeModel.activated_by}</span></div>
                <div className="truncate" title={activeModel.artifact_sha256}>
                  Hash SHA-256: <span className="font-mono text-[10px] text-slate-300">{activeModel.artifact_sha256?.substring(0, 16)}...</span>
                </div>
              </div>
            </div>
          ) : (
            <div>
              <p className="text-sm font-semibold text-amber-400">NO_ACTIVE_MODEL_DEPLOYED</p>
              <p className="text-xs text-slate-400 mt-1">
                No hay un modelo operativo activo en producción. Las simulaciones deben ejecutarse en modo EXPERIMENTAL.
              </p>
            </div>
          )}
        </div>

        {/* Estabilidad Poblacional (PSI) */}
        <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/60 border-slate-800/80' : 'bg-white border-slate-200'} shadow-sm`}>
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Estabilidad (PSI)</span>
            {getStatusBadge(monitoring?.overall_status)}
          </div>
          <div className="text-2xl font-extrabold text-slate-100">
            {monitoring?.psi_value !== null && monitoring?.psi_value !== undefined
              ? monitoring.psi_value.toFixed(4)
              : 'Pendiente / N/D'}
          </div>
          <p className="text-xs text-slate-400 mt-1">
            {monitoring?.psi_status ? `Estado: ${monitoring.psi_status}` : 'Sin cálculo de deriva disponible'}
          </p>
          <div className="mt-3 text-[10px] text-slate-500">
            Umbrales: PSI &lt; 0.10 (Estable) | 0.10-0.25 (Alerta) | &gt; 0.25 (Drift)
          </div>
        </div>

        {/* Kolmogorov-Smirnov */}
        <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/60 border-slate-800/80' : 'bg-white border-slate-200'} shadow-sm`}>
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Test KS (2 Muestras)</span>
            <Database className="text-cyan-400" size={18} />
          </div>
          <div className="text-2xl font-extrabold text-slate-100">
            {monitoring?.ks_p_value !== null && monitoring?.ks_p_value !== undefined
              ? `p = ${monitoring.ks_p_value.toFixed(4)}`
              : 'Pendiente / N/D'}
          </div>
          <p className="text-xs text-slate-400 mt-1">
            {monitoring?.unavailability_reason || 'Monitoreo de distribuciones observadas vs proyectadas'}
          </p>
          <div className="mt-3 text-[10px] text-slate-500">
            Criterio: p &ge; 0.05 no rechaza equivalencia distributiva.
          </div>
        </div>
      </div>

      {/* Disparador de Evaluación Manual */}
      <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/60 border-slate-800/80' : 'bg-white border-slate-200'} space-y-4`}>
        <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
          <RefreshCw size={16} className="text-blue-400" />
          Ejecutar Ciclo de Monitoreo Manual (Bajo Demanda)
        </h3>
        <p className="text-xs text-slate-400">
          Compara la última simulación operativa generada contra la línea base de evaluación del modelo activo,
          calculando el índice PSI por deciles y el test Kolmogorov-Smirnov sin fabricar datos artificiales.
        </p>
        <div className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            id="input_monitoring_notes"
            placeholder="Notas de auditoría (ej. Revisión post-semana epidemiológica 14)..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className={`flex-1 px-4 py-2.5 rounded-xl text-xs border focus:outline-none focus:ring-2 focus:ring-blue-500/50 ${
              darkMode ? 'bg-slate-950 border-slate-800 text-slate-200' : 'bg-slate-50 border-slate-200 text-slate-800'
            }`}
          />
          <button
            id="btn_trigger_monitoring"
            onClick={handleTriggerEvaluation}
            disabled={evaluating || !activeModel?.is_active}
            className={`px-5 py-2.5 rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 cursor-pointer ${
              activeModel?.is_active
                ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:opacity-90 shadow-lg shadow-blue-500/20'
                : 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
            }`}
          >
            {evaluating ? (
              <>
                <RefreshCw size={14} className="animate-spin" />
                Calculando Drift...
              </>
            ) : (
              'Ejecutar Monitoreo On-Demand'
            )}
          </button>
        </div>
        {!activeModel?.is_active && (
          <p className="text-[11px] text-amber-400">
            * Se requiere un modelo activo en despliegue para registrar ciclos de monitoreo.
          </p>
        )}
      </div>
    </div>
  );
};
