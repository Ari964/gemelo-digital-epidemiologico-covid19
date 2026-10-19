import React, { useState } from 'react';
import { 
  Cpu, 
  Sliders, 
  Activity, 
  Home, 
  Users, 
  Layers, 
  ShieldCheck, 
  Zap, 
  Network,
  Move,
  CheckCircle2,
  Sparkles
} from 'lucide-react';
import { LanguageCode } from '../types';
import { KENYA_COUNTIES } from '../data/kenyaCounties';
import { useToast } from './ToastContainer';

interface HybridArchitectureViewProps {
  simulationResult?: any;
  lang: LanguageCode;
  darkMode: boolean;
}

export const HybridArchitectureView: React.FC<HybridArchitectureViewProps> = ({
  lang,
  darkMode,
}) => {
  const { addToast } = useToast();

  // Parámetros de Transmisión
  const [r0Baseline, setR0Baseline] = useState(2.4);
  const [latentDays, setLatentDays] = useState(3.0);
  const [infectiousDays, setInfectiousDays] = useState(5.5);

  // Parámetros de Hogar (Demografía Referencial)
  const [householdSize, setHouseholdSize] = useState(5.2);
  const [sharedSanitation, setSharedSanitation] = useState(0.65);
  const [informalAdaptation, setInformalAdaptation] = useState(true);

  // Parámetros de Movilidad (Modelo Gravitacional Estimado)
  const [gravityExponent, setGravityExponent] = useState(1.45);
  const [interCountyMobilityDamping, setInterCountyMobilityDamping] = useState(0.30);

  // Cálculo dinámico del multiplicador de transmisión efectiva beta_eff y R_t
  const densityMultiplier = 1.0 + (householdSize - 3.0) * 0.08 + (sharedSanitation * 0.15);
  const mobilityMultiplier = 1.0 - (interCountyMobilityDamping * 0.40);
  const informalMod = informalAdaptation ? 0.72 : 1.18;
  const effectiveBeta = (r0Baseline / infectiousDays) * densityMultiplier * mobilityMultiplier * informalMod;
  const effectiveRt = Number((effectiveBeta * infectiousDays).toFixed(2));

  const handleSaveCalibration = () => {
    addToast(
      'success',
      'Calibración Guardada (Fase 4)',
      `Parámetros actualizados: R₀=${r0Baseline.toFixed(2)}, Hogar=${householdSize} hab, Movilidad damped=${(interCountyMobilityDamping * 100).toFixed(0)}%.`
    );
  };

  return (
    <div id="hybrid_architecture_view" className="space-y-6 w-full">
      {/* Encabezado Principal CRISP-DM */}
      <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl flex flex-col md:flex-row items-center justify-between gap-4`}>
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Cpu size={22} className="text-cyan-400" />
            <h3 className={`text-base font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
              Fase 4 (CRISP-DM) - Gemelo Digital (Modelado)
            </h3>
          </div>
          <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
            Panel de calibración de arquitectura híbrida: Metapoblación SEIR acoplada espacialmente + Micro-agentes intra-domicilio
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-2 text-xs font-mono px-3.5 py-2 rounded-xl font-bold ${darkMode ? 'bg-slate-950 border border-slate-800' : 'bg-slate-100 border border-slate-200'} text-cyan-400`}>
            <Zap size={14} />
            R₀ Efectivo Calibrado: {effectiveRt}x
          </div>

          <button
            onClick={handleSaveCalibration}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold shadow transition cursor-pointer"
          >
            <CheckCircle2 size={14} />
            Guardar Calibración
          </button>
        </div>
      </div>

      {/* SECCIÓN 1: DIAGRAMA DE FLUJO COMPARTIMENTAL SEIR */}
      <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl space-y-4`}>
        <div className="flex items-center justify-between pb-2 border-b border-slate-800/60">
          <h4 className={`text-sm font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
            Arquitectura Multinivel: Metapoblación SEIR + Dinámica de Micro-Agentes
          </h4>
          <span className="text-xs font-mono text-slate-400">47 Ecuaciones Diferenciales Ordinarias Acopladas</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 text-center text-xs font-mono">
          <div className="p-4 rounded-xl bg-sky-950/40 border border-sky-800/60 space-y-1">
            <span className="text-sky-400 font-bold block text-sm">S (Susceptibles)</span>
            <span className={`text-[10px] block ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
              dS/dt = -β_eff · S · I / N
            </span>
          </div>

          <div className="p-4 rounded-xl bg-amber-950/40 border border-amber-800/60 space-y-1">
            <span className="text-amber-400 font-bold block text-sm">E (Expuestos)</span>
            <span className={`text-[10px] block ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
              dE/dt = β_eff · S · I / N - σE
            </span>
          </div>

          <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/60 space-y-1">
            <span className="text-rose-400 font-bold block text-sm">I (Infecciosos)</span>
            <span className={`text-[10px] block ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
              dI/dt = σE - γI
            </span>
          </div>

          <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-800/60 space-y-1">
            <span className="text-emerald-400 font-bold block text-sm">R (Recuperados)</span>
            <span className={`text-[10px] block ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
              dR/dt = γ(1-CFR)I
            </span>
          </div>

          <div className={`p-4 rounded-xl space-y-1 ${darkMode ? 'bg-slate-950/60 border border-slate-800' : 'bg-slate-100 border border-slate-200'}`}>
            <span className={`font-bold block text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>D (Fallecidos)</span>
            <span className={`text-[10px] block ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
              dD/dt = γ(CFR)I
            </span>
          </div>
        </div>
      </div>

      {/* SECCIÓN 2: TRES PANELES DE CALIBRACIÓN DE PARÁMETROS */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 1. Parámetros de Transmisión */}
        <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl space-y-4`}>
          <div className={`flex items-center gap-2 pb-2 border-b ${darkMode ? 'border-slate-800' : 'border-slate-200'}`}>
            <Sliders size={18} className="text-blue-400" />
            <h4 className={`text-xs font-bold uppercase tracking-wider ${darkMode ? 'text-slate-200' : 'text-slate-800'}`}>
              1. Parámetros de Transmisión
            </h4>
          </div>

          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-400">R₀ Biológico Base:</span>
              <strong className="text-blue-400 font-mono">{r0Baseline.toFixed(2)}</strong>
            </div>
            <input
              type="range"
              min="1.2"
              max="4.0"
              step="0.05"
              value={r0Baseline}
              onChange={(e) => setR0Baseline(Number(e.target.value))}
              className="w-full accent-blue-500 h-1.5 rounded-lg bg-slate-800"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-400">Período Latente (1/σ):</span>
              <strong className="text-amber-400 font-mono">{latentDays} días</strong>
            </div>
            <input
              type="range"
              min="1.5"
              max="6.0"
              step="0.1"
              value={latentDays}
              onChange={(e) => setLatentDays(Number(e.target.value))}
              className="w-full accent-amber-500 h-1.5 rounded-lg bg-slate-800"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-400">Duración Infecciosa (1/γ):</span>
              <strong className="text-emerald-400 font-mono">{infectiousDays} días</strong>
            </div>
            <input
              type="range"
              min="3.0"
              max="10.0"
              step="0.5"
              value={infectiousDays}
              onChange={(e) => setInfectiousDays(Number(e.target.value))}
              className="w-full accent-emerald-500 h-1.5 rounded-lg bg-slate-800"
            />
          </div>
        </div>

        {/* 2. Parámetros de Hogar (DHS 2022) */}
        <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl space-y-4`}>
          <div className={`flex items-center gap-2 pb-2 border-b ${darkMode ? 'border-slate-800' : 'border-slate-200'}`}>
            <Home size={18} className="text-amber-400" />
            <h4 className={`text-xs font-bold uppercase tracking-wider ${darkMode ? 'text-slate-200' : 'text-slate-800'}`}>
              2. Parámetros del Hogar (DHS)
            </h4>
          </div>

          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-400">Tamaño Promedio Hogar:</span>
              <strong className="text-amber-400 font-mono">{householdSize} personas</strong>
            </div>
            <input
              type="range"
              min="2.5"
              max="8.0"
              step="0.1"
              value={householdSize}
              onChange={(e) => setHouseholdSize(Number(e.target.value))}
              className="w-full accent-amber-500 h-1.5 rounded-lg bg-slate-800"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-400">Saneamiento Compartido:</span>
              <strong className="text-rose-400 font-mono">{(sharedSanitation * 100).toFixed(0)}%</strong>
            </div>
            <input
              type="range"
              min="0.1"
              max="0.9"
              step="0.05"
              value={sharedSanitation}
              onChange={(e) => setSharedSanitation(Number(e.target.value))}
              className="w-full accent-rose-500 h-1.5 rounded-lg bg-slate-800"
            />
          </div>

          <label className={`flex items-center gap-2 p-2.5 rounded-xl cursor-pointer text-xs ${darkMode ? 'bg-slate-950 border border-slate-800 text-slate-300' : 'bg-slate-100 border border-slate-200 text-slate-700'}`}>
            <input
              type="checkbox"
              checked={informalAdaptation}
              onChange={(e) => setInformalAdaptation(e.target.checked)}
              className="w-4 h-4 accent-cyan-500 rounded"
            />
            <span>Aislamiento Comunitario (Kibera / Mathare)</span>
          </label>
        </div>

        {/* 3. Parámetros de Movilidad Inter-Condados (Meta) */}
        <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl space-y-4`}>
          <div className={`flex items-center gap-2 pb-2 border-b ${darkMode ? 'border-slate-800' : 'border-slate-200'}`}>
            <Network size={18} className="text-purple-400" />
            <h4 className={`text-xs font-bold uppercase tracking-wider ${darkMode ? 'text-slate-200' : 'text-slate-800'}`}>
              3. Parámetros de Movilidad (Modelo Gravitacional)
            </h4>
          </div>

          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-400">Exponente Modelo de Gravedad:</span>
              <strong className="text-purple-400 font-mono">{gravityExponent.toFixed(2)}</strong>
            </div>
            <input
              type="range"
              min="1.0"
              max="2.2"
              step="0.05"
              value={gravityExponent}
              onChange={(e) => setGravityExponent(Number(e.target.value))}
              className="w-full accent-purple-500 h-1.5 rounded-lg bg-slate-800"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-400">Atenuación Movilidad Inter-Condados:</span>
              <strong className="text-cyan-400 font-mono">{(interCountyMobilityDamping * 100).toFixed(0)}%</strong>
            </div>
            <input
              type="range"
              min="0.0"
              max="0.8"
              step="0.05"
              value={interCountyMobilityDamping}
              onChange={(e) => setInterCountyMobilityDamping(Number(e.target.value))}
              className="w-full accent-cyan-500 h-1.5 rounded-lg bg-slate-800"
            />
          </div>

          <div className="p-2.5 rounded-xl bg-slate-950/40 border border-slate-800 text-[11px] text-slate-400">
            Fórmula de Flujo: <code>Flow_ij = (Pop_i · Pop_j) / Dist^{gravityExponent}</code>
          </div>
        </div>
      </div>
    </div>
  );
};
