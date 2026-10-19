import React, { useState } from 'react';
import { 
  Sliders, 
  Play, 
  RotateCcw, 
  School, 
  Syringe, 
  Home, 
  ShieldCheck, 
  Navigation, 
  Sparkles,
  Layers,
  HelpCircle
} from 'lucide-react';
import { SimulationParams, PathogenType, LanguageCode } from '../types';
import { getDefaultParams } from '../utils/epidemicParams';
import { SyntheticDataBanner } from './SyntheticDataBanner';
import { translations } from '../i18n/translations';
import { useToast } from './ToastContainer';

interface SimulationControlsProps {
  currentParams: SimulationParams;
  onRunSimulation: (params: SimulationParams) => void;
  isLoading: boolean;
  lang: LanguageCode;
  darkMode: boolean;
}

export const SimulationControls: React.FC<SimulationControlsProps> = ({
  currentParams,
  onRunSimulation,
  isLoading,
  lang,
  darkMode,
}) => {
  const t = translations[lang];
  const { addToast } = useToast();
  const [params, setParams] = useState<SimulationParams>(currentParams);
  const [isSynthetic, setIsSynthetic] = useState<boolean>(false);

  const handlePathogenChange = (pathogen: PathogenType) => {
    const defaults = getDefaultParams(pathogen);
    setParams(defaults);
    addToast('info', 'Patógeno Actualizado', `Cargados parámetros base para ${pathogen.toUpperCase()}`);
  };

  const applyPreset = (presetName: string) => {
    const base = { ...params };
    if (presetName === 'unmitigated') {
      base.name = 'Unmitigated Counterfactual Baseline';
      base.interventions.schoolClosure.active = false;
      base.interventions.vaccination.active = false;
      base.interventions.householdDistancing.active = false;
      base.interventions.mobilityRestriction.active = false;
      base.interventions.faceMasks.active = false;
      addToast('warning', 'Escenario Aplicado', 'Cargada ola contrafactual sin intervenciones (NPIs desactivados).');
    } else if (presetName === 'optimal_lmic') {
      base.name = 'Optimal LMIC: Occupation Vax + Informal Settlement Isolation';
      base.interventions.schoolClosure.active = true;
      base.interventions.schoolClosure.startDay = 12;
      base.interventions.schoolClosure.durationDays = 30;
      base.interventions.vaccination.active = true;
      base.interventions.vaccination.strategy = 'occupation_prioritized';
      base.interventions.vaccination.dailyDosesPer10k = 40;
      base.interventions.householdDistancing.active = true;
      base.interventions.householdDistancing.adaptationForInformalSettlements = true;
      base.interventions.faceMasks.active = true;
      base.interventions.faceMasks.coverage = 0.75;
      addToast('success', 'Escenario Híbrido Óptimo', 'Vacunación ocupacional + Aislamiento adaptado a asentamientos informales.');
    } else if (presetName === 'equity_first') {
      base.name = 'Equity-First: Q1/Q2 Focused Mobile Vax Delivery';
      base.interventions.vaccination.active = true;
      base.interventions.vaccination.strategy = 'equity_targeted';
      base.interventions.vaccination.dailyDosesPer10k = 45;
      base.interventions.householdDistancing.adaptationForInformalSettlements = true;
      base.interventions.faceMasks.active = true;
      addToast('success', 'Escenario Enfocado en Equidad', 'Entrega móvil priorizada en quintiles de menores ingresos Q1/Q2.');
    } else if (presetName === 'strict_lockdown') {
      base.name = 'Strict Lockdown & Inter-County Cordon Sanitaire';
      base.interventions.schoolClosure.active = true;
      base.interventions.schoolClosure.durationDays = 60;
      base.interventions.mobilityRestriction.active = true;
      base.interventions.mobilityRestriction.interCountyReduction = 0.70;
      base.interventions.faceMasks.active = true;
      addToast('warning', 'Escenario de Cuarentena Estricta', 'Restricción del 70% de movilidad inter-condados cargada.');
    }
    setParams(base);
  };

  return (
    <div id="simulation_controls_panel" className="space-y-6 w-full">
      {/* Encabezado Principal CRISP-DM Fase 6 */}
      <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl flex flex-col md:flex-row items-center justify-between gap-4`}>
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Sliders size={22} className="text-blue-400" />
            <h3 className={`text-base font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
              Fase 6 (CRISP-DM) - Despliegue de Escenarios (Toma de Decisiones)
            </h3>
          </div>
          <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
            Entorno principal de simulación: Cierres de escuelas, NPIs y estrategias de vacunación para evaluar saturación de camas UCI y DALYs evitados
          </p>
        </div>

        <button
          id="btn_run_simulation_top"
          onClick={() => onRunSimulation(params)}
          disabled={isLoading}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 disabled:opacity-50 text-white text-xs font-bold shadow-lg shadow-blue-500/25 transition cursor-pointer"
        >
          {isLoading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Simulando Gemelo Digital...
            </>
          ) : (
            <>
              <Play size={15} />
              Ejecutar Simulación (CRISP-DM)
            </>
          )}
        </button>
      </div>

      {/* Banner de Advertencia de Datos Sintéticos */}
      <SyntheticDataBanner isSynthetic={isSynthetic} />

      {/* Selector de Modo de Ejecución (Operacional vs Experimental) */}
      <div className={`p-4 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-md flex flex-col sm:flex-row items-center justify-between gap-3`}>
        <div>
          <span className={`text-xs font-bold ${darkMode ? 'text-slate-200' : 'text-slate-800'} block`}>
            Modo de Ejecución de la Simulación:
          </span>
          <span className={`text-[11px] ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
            {(params.runMode || 'EXPERIMENTAL') === 'OPERATIONAL'
              ? 'OPERACIONAL: Requiere un modelo activo y aprobado técnicamente en el Singleton de producción.'
              : 'EXPERIMENTAL: Permite explorar escenarios y calibrar candidatos sin afectar la línea base operativa.'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            id="btn_mode_experimental"
            type="button"
            onClick={() => setParams({ ...params, runMode: 'EXPERIMENTAL' })}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer ${
              (params.runMode || 'EXPERIMENTAL') === 'EXPERIMENTAL'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/30'
                : darkMode
                ? 'bg-slate-800 text-slate-400 hover:text-slate-200'
                : 'bg-slate-100 text-slate-600 hover:text-slate-900'
            }`}
          >
            Experimental (Candidato)
          </button>
          <button
            id="btn_mode_operational"
            type="button"
            onClick={() => setParams({ ...params, runMode: 'OPERATIONAL' })}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer ${
              params.runMode === 'OPERATIONAL'
                ? 'bg-emerald-600 text-white shadow-md shadow-emerald-500/30'
                : darkMode
                ? 'bg-slate-800 text-slate-400 hover:text-slate-200'
                : 'bg-slate-100 text-slate-600 hover:text-slate-900'
            }`}
          >
            Operacional (Producción)
          </button>
        </div>
      </div>

      {/* Selector de Fuente de Movilidad (Empírica vs Sintética) */}
      <div className={`p-4 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-md flex flex-col sm:flex-row items-center justify-between gap-3`}>
        <div>
          <span className={`text-xs font-bold ${darkMode ? 'text-slate-200' : 'text-slate-800'} block`}>
            Fuente de Movilidad Espacial Inter-Condados:
          </span>
          <span className={`text-[11px] ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
            {isSynthetic
              ? 'Modelo gravitacional sintético (Invalida aprobación de H1).'
              : 'Meta Data for Good Movement Range (Empírica real, válida para H1).'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            id="btn_mobility_empirical"
            type="button"
            onClick={() => setIsSynthetic(false)}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer ${
              !isSynthetic
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/30'
                : darkMode
                ? 'bg-slate-800 text-slate-400 hover:text-slate-200'
                : 'bg-slate-100 text-slate-600 hover:text-slate-900'
            }`}
          >
            Empírica (Meta)
          </button>
          <button
            id="btn_mobility_synthetic"
            type="button"
            onClick={() => setIsSynthetic(true)}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer ${
              isSynthetic
                ? 'bg-amber-600 text-white shadow-md shadow-amber-500/30'
                : darkMode
                ? 'bg-slate-800 text-slate-400 hover:text-slate-200'
                : 'bg-slate-100 text-slate-600 hover:text-slate-900'
            }`}
          >
            Sintética (Gravity)
          </button>
        </div>
      </div>

      {/* Preset Strategy Bar */}
      <div className={`p-4 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-md`}>
        <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
          <span className={`text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
            <Layers size={14} className="text-blue-400" />
            Empirical Scenario Presets
          </span>
          <span className={`text-[11px] ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Click to load calibrated intervention bundles</span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
          <button
            id="btn_preset_unmitigated"
            onClick={() => applyPreset('unmitigated')}
            className={`p-2.5 rounded-xl border border-red-500/30 text-left transition ${darkMode ? 'bg-red-950/20 hover:bg-red-950/40' : 'bg-red-50 hover:bg-red-100'}`}
          >
            <span className={`text-xs font-semibold block ${darkMode ? 'text-red-300' : 'text-red-700'}`}>Unmitigated Baseline</span>
            <span className={`text-[10px] ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>No NPIs / Natural Wave</span>
          </button>

          <button
            id="btn_preset_optimal_lmic"
            onClick={() => applyPreset('optimal_lmic')}
            className={`p-2.5 rounded-xl border border-blue-500/30 text-left transition ring-1 ring-blue-500/30 ${darkMode ? 'bg-blue-950/20 hover:bg-blue-950/40' : 'bg-blue-50 hover:bg-blue-100'}`}
          >
            <span className={`text-xs font-semibold block ${darkMode ? 'text-blue-300' : 'text-blue-700'}`}>Optimal LMIC Hybrid</span>
            <span className={`text-[10px] ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Occupation Vax + Isolation</span>
          </button>

          <button
            id="btn_preset_equity_first"
            onClick={() => applyPreset('equity_first')}
            className={`p-2.5 rounded-xl border border-emerald-500/30 text-left transition ${darkMode ? 'bg-emerald-950/20 hover:bg-emerald-950/40' : 'bg-emerald-50 hover:bg-emerald-100'}`}
          >
            <span className={`text-xs font-semibold block ${darkMode ? 'text-emerald-300' : 'text-emerald-700'}`}>Equity-Targeted Rollout</span>
            <span className={`text-[10px] ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Q1/Q2 Focused Delivery</span>
          </button>

          <button
            id="btn_preset_strict_lockdown"
            onClick={() => applyPreset('strict_lockdown')}
            className={`p-2.5 rounded-xl border border-amber-500/30 text-left transition ${darkMode ? 'bg-amber-950/20 hover:bg-amber-950/40' : 'bg-amber-50 hover:bg-amber-100'}`}
          >
            <span className={`text-xs font-semibold block ${darkMode ? 'text-amber-300' : 'text-amber-700'}`}>Strict Mobility Cordon</span>
            <span className={`text-[10px] ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>High Economic Cost</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Biological & Pathogen Parameters */}
        <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl space-y-4`}>
          <div className={`flex items-center gap-2 pb-3 border-b ${darkMode ? 'border-slate-800' : 'border-slate-200'}`}>
            <Sliders size={18} className="text-blue-400" />
            <h3 className={`text-sm font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>Epidemiological & Virus Dynamics</h3>
          </div>

          <div>
            <label className={`text-xs mb-1 block ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Scenario Name:</label>
            <input
              id="input_scenario_name"
              type="text"
              value={params.name}
              onChange={(e) => setParams({ ...params, name: e.target.value })}
              className={`w-full rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 outline-none ${darkMode ? 'bg-slate-950 border border-slate-700 text-slate-200' : 'bg-white border border-slate-300 text-slate-800 hover:border-slate-400'}`}
            />
          </div>

          <div>
            <label className={`text-xs mb-1 block ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Pathogen Archetype:</label>
            <div className={`grid grid-cols-3 gap-1.5 p-1 rounded-xl text-xs ${darkMode ? 'bg-slate-950 border border-slate-800' : 'bg-slate-100 border border-slate-200'}`}>
              <button
                id="btn_select_covid19"
                onClick={() => handlePathogenChange('covid19')}
                className={`py-1.5 rounded-lg font-medium transition ${params.pathogen === 'covid19' ? 'bg-blue-600 text-white' : darkMode ? 'text-slate-400' : 'text-slate-500'}`}
              >
                COVID-19
              </button>
              <button
                id="btn_select_influenza"
                onClick={() => handlePathogenChange('influenza_h5n1')}
                className={`py-1.5 rounded-lg font-medium transition ${params.pathogen === 'influenza_h5n1' ? 'bg-blue-600 text-white' : darkMode ? 'text-slate-400' : 'text-slate-500'}`}
              >
                Influenza H5N1
              </button>
              <button
                id="btn_select_rsv"
                onClick={() => handlePathogenChange('rsv')}
                className={`py-1.5 rounded-lg font-medium transition ${params.pathogen === 'rsv' ? 'bg-blue-600 text-white' : darkMode ? 'text-slate-400' : 'text-slate-500'}`}
              >
                RSV
              </button>
            </div>
          </div>

          {/* R0 Baseline Slider */}
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className={`${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Basic Reproduction Number (R₀):</span>
              <strong className="text-blue-400 font-mono">{params.r0_baseline.toFixed(2)}</strong>
            </div>
            <input
              id="slider_r0_baseline"
              type="range"
              min="1.2"
              max="4.5"
              step="0.05"
              value={params.r0_baseline}
              onChange={(e) => setParams({ ...params, r0_baseline: Number(e.target.value) })}
              className={`w-full accent-blue-500 h-1.5 rounded-lg ${darkMode ? 'bg-slate-800' : 'bg-slate-200'}`}
            />
          </div>

          {/* Latent & Infectious Periods */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={`text-[11px] block mb-1 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Latent Period (1/σ):</label>
              <input
                id="input_latent_period"
                type="number"
                step="0.5"
                min="1"
                max="10"
                value={params.latentPeriodDays}
                onChange={(e) => setParams({ ...params, latentPeriodDays: Number(e.target.value) })}
                className={`w-full rounded-xl px-2.5 py-1.5 text-xs font-mono ${darkMode ? 'bg-slate-950 border border-slate-700 text-slate-200' : 'bg-white border border-slate-300 text-slate-800 hover:border-slate-400'}`}
              />
            </div>
            <div>
              <label className={`text-[11px] block mb-1 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Infectious Period (1/γ):</label>
              <input
                id="input_infectious_period"
                type="number"
                step="0.5"
                min="2"
                max="14"
                value={params.infectiousPeriodDays}
                onChange={(e) => setParams({ ...params, infectiousPeriodDays: Number(e.target.value) })}
                className={`w-full rounded-xl px-2.5 py-1.5 text-xs font-mono ${darkMode ? 'bg-slate-950 border border-slate-700 text-slate-200' : 'bg-white border border-slate-300 text-slate-800 hover:border-slate-400'}`}
              />
            </div>
          </div>

          {/* Hospitalization Rate & ICU Fraction */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={`text-[11px] block mb-1 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Hospitalization Rate:</label>
              <input
                id="input_hosp_rate"
                type="number"
                step="0.005"
                min="0.01"
                max="0.20"
                value={params.hospitalizationRate}
                onChange={(e) => setParams({ ...params, hospitalizationRate: Number(e.target.value) })}
                className={`w-full rounded-xl px-2.5 py-1.5 text-xs font-mono ${darkMode ? 'bg-slate-950 border border-slate-700 text-slate-200' : 'bg-white border border-slate-300 text-slate-800 hover:border-slate-400'}`}
              />
            </div>
            <div>
              <label className={`text-[11px] block mb-1 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Case Fatality (CFR):</label>
              <input
                id="input_cfr"
                type="number"
                step="0.002"
                min="0.001"
                max="0.10"
                value={params.caseFatalityRatio}
                onChange={(e) => setParams({ ...params, caseFatalityRatio: Number(e.target.value) })}
                className={`w-full rounded-xl px-2.5 py-1.5 text-xs font-mono ${darkMode ? 'bg-slate-950 border border-slate-700 text-slate-200' : 'bg-white border border-slate-300 text-slate-800 hover:border-slate-400'}`}
              />
            </div>
          </div>

          {/* Seed & Duration */}
          <div className={`grid grid-cols-2 gap-3 pt-2 border-t ${darkMode ? 'border-slate-800' : 'border-slate-200'}`}>
            <div>
              <label className={`text-[11px] block mb-1 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t.reproducibleSeed}:</label>
              <input
                id="input_random_seed"
                type="number"
                value={params.randomSeed}
                onChange={(e) => setParams({ ...params, randomSeed: Number(e.target.value) })}
                className={`w-full rounded-xl px-2.5 py-1.5 text-xs font-mono ${darkMode ? 'bg-slate-950 border border-slate-700 text-slate-200' : 'bg-white border border-slate-300 text-slate-800 hover:border-slate-400'}`}
              />
            </div>
            <div>
              <label className={`text-[11px] block mb-1 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Horizon (Days):</label>
              <input
                id="input_duration_days"
                type="number"
                min="30"
                max="180"
                value={params.durationDays}
                onChange={(e) => setParams({ ...params, durationDays: Number(e.target.value) })}
                className={`w-full rounded-xl px-2.5 py-1.5 text-xs font-mono ${darkMode ? 'bg-slate-950 border border-slate-700 text-slate-200' : 'bg-white border border-slate-300 text-slate-800 hover:border-slate-400'}`}
              />
            </div>
          </div>
        </div>

        {/* Right 2 Columns: Interventions (NPIs & Vaccination) */}
        <div className={`lg:col-span-2 p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl space-y-5`}>
          <div className={`flex items-center justify-between pb-3 border-b ${darkMode ? 'border-slate-800' : 'border-slate-200'}`}>
            <div className="flex items-center gap-2">
              <ShieldCheck size={18} className="text-emerald-400" />
              <h3 className={`text-sm font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>{t.interventionsTitle}</h3>
            </div>
            <span className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Context-adapted for LMIC environments</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* 1. Vaccination Strategy */}
            <div className={`p-4 rounded-xl space-y-3 ${darkMode ? 'bg-slate-950/60 border border-slate-800' : 'bg-slate-50 border border-slate-200'}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Syringe size={16} className="text-violet-400" />
                  <span className={`text-xs font-bold ${darkMode ? 'text-slate-200' : 'text-slate-800'}`}>{t.vaccinationStrategy}</span>
                </div>
                <input
                  id="toggle_vax_active"
                  type="checkbox"
                  checked={params.interventions.vaccination.active}
                  onChange={(e) => setParams({
                    ...params,
                    interventions: {
                      ...params.interventions,
                      vaccination: { ...params.interventions.vaccination, active: e.target.checked }
                    }
                  })}
                  className="w-4 h-4 accent-violet-600 rounded cursor-pointer"
                />
              </div>

              {params.interventions.vaccination.active && (
                <div className="space-y-2.5 text-xs pt-1">
                  <div>
                    <label className={`text-[11px] mb-1 block ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Allocation Strategy:</label>
                    <select
                      id="select_vax_strategy"
                      value={params.interventions.vaccination.strategy}
                      onChange={(e) => setParams({
                        ...params,
                        interventions: {
                          ...params.interventions,
                          vaccination: { ...params.interventions.vaccination, strategy: e.target.value as any }
                        }
                      })}
                      className={`w-full rounded-lg px-2.5 py-1.5 text-xs ${darkMode ? 'bg-slate-900 border border-slate-700 text-slate-200' : 'bg-white border border-slate-300 text-slate-800 hover:border-slate-400'}`}
                    >
                      <option value="age_prioritized">{t.agePrioritized}</option>
                      <option value="occupation_prioritized">{t.occupationPrioritized}</option>
                      <option value="equity_targeted">{t.equityTargeted}</option>
                      <option value="random">{t.randomStrategy}</option>
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <span className={`text-[10px] block ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Daily Doses/10k:</span>
                      <input
                        id="input_daily_doses"
                        type="number"
                        min="5"
                        max="100"
                        value={params.interventions.vaccination.dailyDosesPer10k}
                        onChange={(e) => setParams({
                          ...params,
                          interventions: {
                            ...params.interventions,
                            vaccination: { ...params.interventions.vaccination, dailyDosesPer10k: Number(e.target.value) }
                          }
                        })}
                        className={`w-full rounded-lg px-2 py-1 text-xs font-mono ${darkMode ? 'bg-slate-900 border border-slate-700 text-slate-200' : 'bg-white border border-slate-300 text-slate-800 hover:border-slate-400'}`}
                      />
                    </div>
                    <div>
                      <span className={`text-[10px] block ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Start Day:</span>
                      <input
                        id="input_vax_start_day"
                        type="number"
                        min="1"
                        max="60"
                        value={params.interventions.vaccination.startDay}
                        onChange={(e) => setParams({
                          ...params,
                          interventions: {
                            ...params.interventions,
                            vaccination: { ...params.interventions.vaccination, startDay: Number(e.target.value) }
                          }
                        })}
                        className={`w-full rounded-lg px-2 py-1 text-xs font-mono ${darkMode ? 'bg-slate-900 border border-slate-700 text-slate-200' : 'bg-white border border-slate-300 text-slate-800 hover:border-slate-400'}`}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* 2. School Closure */}
            <div className={`p-4 rounded-xl space-y-3 ${darkMode ? 'bg-slate-950/60 border border-slate-800' : 'bg-slate-50 border border-slate-200'}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <School size={16} className="text-blue-400" />
                  <span className={`text-xs font-bold ${darkMode ? 'text-slate-200' : 'text-slate-800'}`}>{t.schoolClosure}</span>
                </div>
                <input
                  id="toggle_school_active"
                  type="checkbox"
                  checked={params.interventions.schoolClosure.active}
                  onChange={(e) => setParams({
                    ...params,
                    interventions: {
                      ...params.interventions,
                      schoolClosure: { ...params.interventions.schoolClosure, active: e.target.checked }
                    }
                  })}
                  className="w-4 h-4 accent-blue-600 rounded cursor-pointer"
                />
              </div>

              {params.interventions.schoolClosure.active && (
                <div className="space-y-2.5 text-xs pt-1">
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <span className={`text-[10px] block ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Start Day:</span>
                      <input
                        id="input_school_start"
                        type="number"
                        min="1"
                        max="60"
                        value={params.interventions.schoolClosure.startDay}
                        onChange={(e) => setParams({
                          ...params,
                          interventions: {
                            ...params.interventions,
                            schoolClosure: { ...params.interventions.schoolClosure, startDay: Number(e.target.value) }
                          }
                        })}
                        className={`w-full rounded-lg px-2 py-1 text-xs font-mono ${darkMode ? 'bg-slate-900 border border-slate-700 text-slate-200' : 'bg-white border border-slate-300 text-slate-800 hover:border-slate-400'}`}
                      />
                    </div>
                    <div>
                      <span className={`text-[10px] block ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Duration (Days):</span>
                      <input
                        id="input_school_duration"
                        type="number"
                        min="7"
                        max="90"
                        value={params.interventions.schoolClosure.durationDays}
                        onChange={(e) => setParams({
                          ...params,
                          interventions: {
                            ...params.interventions,
                            schoolClosure: { ...params.interventions.schoolClosure, durationDays: Number(e.target.value) }
                          }
                        })}
                        className={`w-full rounded-lg px-2 py-1 text-xs font-mono ${darkMode ? 'bg-slate-900 border border-slate-700 text-slate-200' : 'bg-white border border-slate-300 text-slate-800 hover:border-slate-400'}`}
                      />
                    </div>
                  </div>
                  <div>
                    <div className={`flex justify-between text-[11px] mb-1 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                      <span>Compliance Rate:</span>
                      <strong className="text-blue-400 font-mono">{(params.interventions.schoolClosure.complianceRate * 100).toFixed(0)}%</strong>
                    </div>
                    <input
                      id="slider_school_compliance"
                      type="range"
                      min="0.3"
                      max="1.0"
                      step="0.05"
                      value={params.interventions.schoolClosure.complianceRate}
                      onChange={(e) => setParams({
                        ...params,
                        interventions: {
                          ...params.interventions,
                          schoolClosure: { ...params.interventions.schoolClosure, complianceRate: Number(e.target.value) }
                        }
                      })}
                      className={`w-full accent-blue-500 h-1 rounded ${darkMode ? 'bg-slate-800' : 'bg-slate-200'}`}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* 3. Household Physical Distancing & Informal Settlement Adaptation */}
            <div className={`p-4 rounded-xl space-y-3 ${darkMode ? 'bg-slate-950/60 border border-slate-800' : 'bg-slate-50 border border-slate-200'}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Home size={16} className="text-amber-400" />
                  <span className={`text-xs font-bold ${darkMode ? 'text-slate-200' : 'text-slate-800'}`}>{t.householdDistancing}</span>
                </div>
                <input
                  id="toggle_hh_active"
                  type="checkbox"
                  checked={params.interventions.householdDistancing.active}
                  onChange={(e) => setParams({
                    ...params,
                    interventions: {
                      ...params.interventions,
                      householdDistancing: { ...params.interventions.householdDistancing, active: e.target.checked }
                    }
                  })}
                  className="w-4 h-4 accent-amber-600 rounded cursor-pointer"
                />
              </div>

              {params.interventions.householdDistancing.active && (
                <div className="space-y-2.5 text-xs pt-1">
                  <label className={`flex items-start gap-2 p-2 rounded-lg cursor-pointer ${darkMode ? 'bg-amber-950/20 border border-amber-900/40' : 'bg-amber-50 border border-amber-200'}`}>
                    <input
                      id="toggle_informal_adaptation"
                      type="checkbox"
                      checked={params.interventions.householdDistancing.adaptationForInformalSettlements}
                      onChange={(e) => setParams({
                        ...params,
                        interventions: {
                          ...params.interventions,
                          householdDistancing: { ...params.interventions.householdDistancing, adaptationForInformalSettlements: e.target.checked }
                        }
                      })}
                      className="w-3.5 h-3.5 accent-amber-500 mt-0.5"
                    />
                    <span className={`text-[11px] leading-tight ${darkMode ? 'text-amber-300' : 'text-amber-700'}`}>
                      {t.informalSettlementAdaptation}
                    </span>
                  </label>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <span className={`text-[10px] block ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Start Day:</span>
                      <input
                        id="input_hh_start"
                        type="number"
                        min="1"
                        max="60"
                        value={params.interventions.householdDistancing.startDay}
                        onChange={(e) => setParams({
                          ...params,
                          interventions: {
                            ...params.interventions,
                            householdDistancing: { ...params.interventions.householdDistancing, startDay: Number(e.target.value) }
                          }
                        })}
                        className={`w-full rounded-lg px-2 py-1 text-xs font-mono ${darkMode ? 'bg-slate-900 border border-slate-700 text-slate-200' : 'bg-white border border-slate-300 text-slate-800 hover:border-slate-400'}`}
                      />
                    </div>
                    <div>
                      <span className={`text-[10px] block ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Duration (Days):</span>
                      <input
                        id="input_hh_duration"
                        type="number"
                        min="7"
                        max="90"
                        value={params.interventions.householdDistancing.durationDays}
                        onChange={(e) => setParams({
                          ...params,
                          interventions: {
                            ...params.interventions,
                            householdDistancing: { ...params.interventions.householdDistancing, durationDays: Number(e.target.value) }
                          }
                        })}
                        className={`w-full rounded-lg px-2 py-1 text-xs font-mono ${darkMode ? 'bg-slate-900 border border-slate-700 text-slate-200' : 'bg-white border border-slate-300 text-slate-800 hover:border-slate-400'}`}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* 4. Inter-County Mobility Controls */}
            <div className={`p-4 rounded-xl space-y-3 ${darkMode ? 'bg-slate-950/60 border border-slate-800' : 'bg-slate-50 border border-slate-200'}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Navigation size={16} className="text-cyan-400" />
                  <span className={`text-xs font-bold ${darkMode ? 'text-slate-200' : 'text-slate-800'}`}>{t.mobilityRestriction}</span>
                </div>
                <input
                  id="toggle_mobility_active"
                  type="checkbox"
                  checked={params.interventions.mobilityRestriction.active}
                  onChange={(e) => setParams({
                    ...params,
                    interventions: {
                      ...params.interventions,
                      mobilityRestriction: { ...params.interventions.mobilityRestriction, active: e.target.checked }
                    }
                  })}
                  className="w-4 h-4 accent-cyan-600 rounded cursor-pointer"
                />
              </div>

              {params.interventions.mobilityRestriction.active && (
                <div className="space-y-2.5 text-xs pt-1">
                  <div>
                    <div className={`flex justify-between text-[11px] mb-1 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                      <span>Inter-County Reduction:</span>
                      <strong className="text-cyan-400 font-mono">{(params.interventions.mobilityRestriction.interCountyReduction * 100).toFixed(0)}%</strong>
                    </div>
                    <input
                      id="slider_mobility_reduction"
                      type="range"
                      min="0.2"
                      max="0.9"
                      step="0.05"
                      value={params.interventions.mobilityRestriction.interCountyReduction}
                      onChange={(e) => setParams({
                        ...params,
                        interventions: {
                          ...params.interventions,
                          mobilityRestriction: { ...params.interventions.mobilityRestriction, interCountyReduction: Number(e.target.value) }
                        }
                      })}
                      className={`w-full accent-cyan-500 h-1 rounded ${darkMode ? 'bg-slate-800' : 'bg-slate-200'}`}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Action Trigger Button */}
          <div className={`pt-4 border-t flex items-center justify-between ${darkMode ? 'border-slate-800' : 'border-slate-200'}`}>
            <button
              id="btn_reset_defaults"
              onClick={() => setParams(getDefaultParams(params.pathogen))}
              className={`px-3.5 py-2 rounded-xl text-xs font-medium transition flex items-center gap-1.5 ${darkMode ? 'bg-slate-800 hover:bg-slate-700 text-slate-300' : 'bg-slate-100 hover:bg-slate-200 text-slate-600'}`}
            >
              <RotateCcw size={14} /> Reset Defaults
            </button>

            <button
              id="btn_execute_simulation_run"
              onClick={() => onRunSimulation(params)}
              disabled={isLoading}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-50 text-white text-xs font-bold shadow-lg shadow-blue-500/25 transition flex items-center gap-2 cursor-pointer"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  {t.runningSimulation}
                </>
              ) : (
                <>
                  <Play size={16} />
                  {t.runSimulationBtn}
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
