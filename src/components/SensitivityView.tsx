import React, { useState, useEffect } from 'react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  Legend 
} from 'recharts';
import { BarChart3, Scale, Play, RefreshCw, AlertCircle, CheckCircle2, Info } from 'lucide-react';
import { SimulationResult, LanguageCode } from '../types';
import { ApiClient } from '../services/apiClient';
import { SobolStatusDTO } from '../types/apiContract';

interface SensitivityViewProps {
  simulationResult: SimulationResult | null;
  lang: LanguageCode;
  darkMode: boolean;
}

export const SensitivityView: React.FC<SensitivityViewProps> = ({
  simulationResult,
  lang,
  darkMode,
}) => {
  const summary = simulationResult ? simulationResult.summary : null;
  const [sobolResult, setSobolResult] = useState<SobolStatusDTO | null>(null);
  const [loading, setLoading] = useState(false);
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [nSamples, setNSamples] = useState<number>(128);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Iniciar cálculo asíncrono
  const handleLaunchSobol = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const resp = await ApiClient.launchSobolAnalysis(nSamples, false);
      setAnalysisId(resp.analysis_id);
      setSobolResult(resp);
    } catch (err: any) {
      setErrorMsg(err.message || 'Error al iniciar análisis de Sobol');
      setLoading(false);
    }
  };

  // Sondeo periódico cuando el análisis está en cola o ejecutándose
  useEffect(() => {
    if (!analysisId) return;
    if (sobolResult?.status === 'COMPLETED' || sobolResult?.status === 'FAILED' || sobolResult?.status === 'INTERRUPTED') {
      setLoading(false);
      return;
    }

    const timer = setInterval(async () => {
      try {
        const status = await ApiClient.getSobolStatus(analysisId);
        setSobolResult(status);
        if (status.status === 'COMPLETED' || status.status === 'FAILED' || status.status === 'INTERRUPTED') {
          setLoading(false);
          clearInterval(timer);
        }
      } catch (err: any) {
        setLoading(false);
        clearInterval(timer);
      }
    }, 1500);

    return () => clearInterval(timer);
  }, [analysisId, sobolResult?.status]);

  // Si no hay cálculo activo, cargar un análisis inicial de baseline
  useEffect(() => {
    handleLaunchSobol();
  }, []);

  const chartData = sobolResult?.sobol_indices?.map((s) => ({
    parameter: s.parameter,
    firstOrderIndex: Number(s.S1.toFixed(3)),
    totalOrderIndex: Number(s.ST.toFixed(3)),
    s1Conf: Number(s.S1_conf.toFixed(3)),
    stConf: Number(s.ST_conf.toFixed(3))
  })) || [];

  return (
    <div id="sensitivity_sobol_view" className="space-y-6 w-full pb-12">
      {/* Header Banner */}
      <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl flex flex-col md:flex-row items-center justify-between gap-4`}>
        <div>
          <div className="flex items-center gap-2 mb-1">
            <BarChart3 size={20} className="text-amber-400" />
            <h3 className="text-sm font-bold text-slate-100">Análisis de Sensibilidad Global de Sobol (Fase 4 CRISP-DM)</h3>
          </div>
          <p className="text-xs text-slate-400">
            Descomposición de varianza por muestreo de Saltelli sobre el modelo de referencia <strong className="text-slate-200">SEIR Clásico (Línea Base)</strong>.
          </p>
        </div>

        <div className={`flex items-center gap-3 ${darkMode ? 'bg-slate-950 border-slate-800' : 'bg-slate-100 border-slate-200'} px-3.5 py-2 rounded-xl border text-xs font-mono`}>
          <Scale size={16} className="text-emerald-400" />
          <span>Demographic Parity Ratio: {summary ? <strong className="text-emerald-400 text-sm">{summary.demographicParityRatio}x</strong> : <span className="text-slate-400 italic">Ejecute una simulación</span>}</span>
        </div>
      </div>

      {/* Honest Scientific Disclaimer */}
      <div className="p-4 rounded-xl border border-amber-500/30 bg-amber-500/10 text-slate-300 text-xs flex items-start gap-3">
        <Info className="text-amber-400 shrink-0 mt-0.5" size={16} />
        <div>
          <strong className="text-amber-300">Ámbito Científico del Análisis de Sobol:</strong> El motor analizado actualmente corresponde al
          <strong> SEIR Clásico Compartimental</strong> (modelo de referencia). Los intervalos de confianza reportados provienen de remuestreo bootstrap real de SALib
          y no de porcentajes simétricos ficticios.
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle size={16} className="shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Control de Ejecución Asíncrona */}
      <div className={`p-4 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-md flex flex-wrap items-center justify-between gap-4`}>
        <div className="flex items-center gap-3">
          <label className="text-xs font-semibold text-slate-300">Muestras Saltelli (N):</label>
          <select
            value={nSamples}
            onChange={(e) => setNSamples(Number(e.target.value))}
            disabled={loading}
            className={`px-3 py-1.5 rounded-xl text-xs border ${darkMode ? 'bg-slate-950 border-slate-800 text-slate-200' : 'bg-slate-50 border-slate-200 text-slate-800'}`}
          >
            <option value={64}>64 (Rápido - 384 eval)</option>
            <option value={128}>128 (Equilibrado - 768 eval)</option>
            <option value={256}>256 (Alta Precisión - 1,536 eval)</option>
          </select>
        </div>

        <div className="flex items-center gap-3">
          {sobolResult && (
            <span className="text-xs font-mono text-slate-400">
              Estado: <strong className={sobolResult.status === 'COMPLETED' ? 'text-emerald-400' : sobolResult.status === 'RUNNING' ? 'text-blue-400' : 'text-amber-400'}>
                {sobolResult.status} ({sobolResult.progress_pct}%)
              </strong>
            </span>
          )}
          <button
            id="btn_launch_sobol"
            onClick={handleLaunchSobol}
            disabled={loading}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-2 transition disabled:opacity-50 cursor-pointer"
          >
            {loading ? <RefreshCw size={14} className="animate-spin" /> : <Play size={14} />}
            {loading ? 'Calculando Saltelli...' : 'Lanzar Análisis Sobol'}
          </button>
        </div>
      </div>

      {/* Sobol Sensitivity Bar Chart */}
      <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl space-y-4`}>
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-bold text-slate-100">Índices de Sensibilidad de Sobol (S1 vs ST)</h4>
            <p className="text-xs text-slate-400">
              Motor: {sobolResult?.model_engine || 'SEIR_CLASSICAL_BASELINE'} | Parámetro más influyente: <strong>{sobolResult?.most_sensitive_parameter || 'Pendiente'}</strong>
            </p>
          </div>
        </div>

        <div className="w-full h-80">
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={darkMode ? '#1e293b' : '#f1f5f9'} />
                <XAxis dataKey="parameter" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} domain={[0, 1.0]} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }} />
                <Legend verticalAlign="top" wrapperStyle={{ fontSize: '12px', paddingBottom: '12px' }} />
                <Bar dataKey="firstOrderIndex" name="Índice Primer Orden (S1)" fill="#3b82f6" radius={[6, 6, 0, 0]} />
                <Bar dataKey="totalOrderIndex" name="Índice Orden Total (ST)" fill="#8b5cf6" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-xs text-slate-500">
              {loading ? 'Calculando índices de sensibilidad...' : 'Sin datos de Sobol calculados.'}
            </div>
          )}
        </div>
      </div>

      {/* Sobol Parameter Detail Table */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl space-y-3`}>
          <h4 className="text-sm font-bold text-slate-100">Descomposición Numérica de Sobol (SALib)</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="py-2">Parámetro</th>
                  <th className="py-2">S1 (Directo)</th>
                  <th className="py-2">ST (Total)</th>
                  <th className="py-2">Conf. S1</th>
                  <th className="py-2">Conf. ST</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {sobolResult?.sobol_indices?.map((s) => (
                  <tr key={s.parameter} className="hover:bg-slate-800/30">
                    <td className="py-2.5 font-semibold text-slate-200 font-sans">{s.parameter}</td>
                    <td className="py-2.5 text-blue-400 font-bold">{s.S1.toFixed(4)}</td>
                    <td className="py-2.5 text-violet-400 font-bold">{s.ST.toFixed(4)}</td>
                    <td className="py-2.5 text-slate-400">±{s.S1_conf.toFixed(4)}</td>
                    <td className="py-2.5 text-slate-400">±{s.ST_conf.toFixed(4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Demographic Parity & Fairness Audit */}
        <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl space-y-3`}>
          <div className="flex items-center gap-2">
            <Scale size={18} className="text-emerald-400" />
            <h4 className="text-sm font-bold text-slate-100">Evaluación de Equidad & Paridad Demográfica</h4>
          </div>
          <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Comparación del acceso a vacunación entre el Quintil 1 más pobre y el Quintil 5 más rico</p>
 
          <div className="space-y-2.5 text-xs font-mono">
            <div className={`p-3 rounded-xl ${darkMode ? 'bg-slate-950 border-slate-800' : 'bg-slate-50 border-slate-200'} border flex justify-between items-center`}>
              <span className={darkMode ? 'text-slate-400' : 'text-slate-600'}>Paridad Demográfica Simulada (Q1 / Q5):</span>
              {summary ? (
                <span className="text-emerald-400 font-bold text-sm">{summary.demographicParityRatio}x</span>
              ) : (
                <span className="text-amber-500 font-medium">Ejecute una simulación</span>
              )}
            </div>
            <div className={`p-3 rounded-xl ${darkMode ? 'bg-slate-950 border-slate-800' : 'bg-slate-50 border-slate-200'} border flex justify-between items-center`}>
              <span className={darkMode ? 'text-slate-400' : 'text-slate-600'}>Criterio de Paridad Equitativa (Regla del 80%):</span>
              <span className="text-cyan-400 font-bold text-sm">[0.80x – 1.20x]</span>
            </div>
            <div className={`p-3 rounded-xl ${darkMode ? 'bg-slate-950 border-slate-800' : 'bg-slate-50 border-slate-200'} border flex justify-between items-center`}>
              <span className={darkMode ? 'text-slate-400' : 'text-slate-600'}>Clasificación Ética del Escenario:</span>
              {summary ? (
                <span className={`font-bold text-sm ${summary.demographicParityRatio >= 0.8 && summary.demographicParityRatio <= 1.2 ? 'text-emerald-400' : (summary.demographicParityRatio > 1.2 ? 'text-blue-400' : 'text-rose-400')}`}>
                  {summary.demographicParityRatio >= 0.8 && summary.demographicParityRatio <= 1.2 ? 'Paridad Aceptable' : (summary.demographicParityRatio > 1.2 ? 'Focalización Pro-Equidad' : 'Disparidad Desfavorable Q1')}
                </span>
              ) : (
                <span className="text-slate-400 italic">Pendiente de ejecución</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
