import React, { useState } from 'react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  Legend 
} from 'recharts';
import { Columns, ArrowRight, TrendingDown, Award, HeartPulse, Bed, ShieldCheck } from 'lucide-react';
import { SimulationResult, SimulationParams, LanguageCode } from '../types';
import { getDefaultParams } from '../utils/epidemicParams';
import { translations } from '../i18n/translations';

interface ScenarioComparatorProps {
  primaryResult: SimulationResult | null;
  lang: LanguageCode;
  darkMode: boolean;
}

export const ScenarioComparator: React.FC<ScenarioComparatorProps> = ({
  primaryResult,
  lang,
  darkMode,
}) => {
  const t = translations[lang];
  const [scenarioBType, setScenarioBType] = useState<'unmitigated' | 'occupation_vax' | 'strict_lockdown' | 'equity_targeted'>('unmitigated');

  if (!primaryResult) {
    return (
      <div id="scenario_comparator_view" className="space-y-6 w-full">
        <div className={`p-8 rounded-2xl border ${darkMode ? 'bg-slate-900/80 border-slate-800' : 'bg-white border-slate-200'} shadow-md text-center space-y-3`}>
          <div className="w-12 h-12 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center mx-auto">
            <Columns size={26} />
          </div>
          <h2 className={`text-base font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
            {lang === 'en' ? 'No Base Scenario to Compare' : lang === 'sw' ? 'Hakuna Uigaji wa Msingi wa Kulinganisha' : 'Sin Escenario Base para Comparar'}
          </h2>
          <p className={`text-xs max-w-md mx-auto ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
            {lang === 'en' ? 'Please execute a baseline simulation first from the Scenario Deployment tab.' : lang === 'sw' ? 'Tafadhali kwanza tekeleza uigaji wa msingi kutoka kwenye kichupo cha Utekelezaji wa Mazingira.' : 'Por favor ejecute primero una simulación base desde el módulo de Despliegue de Escenarios.'}
          </p>
          <div className="pt-2">
            <span className="inline-block px-4 py-1.5 rounded-full text-xs font-mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
              «{t.executeSimPrompt || 'Ejecute una simulación'}»
            </span>
          </div>
        </div>
      </div>
    );
  }

  // Compute Scenario B projection analytically based on intervention multipliers
  const multiplier = scenarioBType === 'unmitigated' ? 1.45 : (scenarioBType === 'strict_lockdown' ? 0.70 : 0.85);
  const sumA = primaryResult.summary;
  const sumB = {
    ...sumA,
    totalInfections: Math.round(sumA.totalInfections * multiplier),
    totalDeaths: Math.round(sumA.totalDeaths * multiplier),
    peakInfected: Math.round(sumA.peakInfected * multiplier),
    peakIcuBedDemand: Math.round(sumA.peakIcuBedDemand * multiplier),
  };

  // Merged comparative timeseries
  const mergedData = primaryResult.nationalTrajectory.map((pointA) => {
    return {
      day: pointA.day,
      infectedA: pointA.infected,
      infectedB: Math.round(pointA.infected * multiplier),
      icua: pointA.icuActive,
      icub: Math.round(pointA.icuActive * multiplier),
      q1a: pointA.q1Cases,
      q1b: Math.round(pointA.q1Cases * multiplier),
    };
  });

  const infectionsAverted = sumB.totalInfections - sumA.totalInfections;
  const deathsAverted = sumB.totalDeaths - sumA.totalDeaths;
  const icuPeakReduction = ((sumB.peakIcuBedDemand - sumA.peakIcuBedDemand) / Math.max(1, sumB.peakIcuBedDemand)) * 100;

  return (
    <div id="scenario_comparator_view" className="space-y-6 w-full">
      {/* Header & Scenario B Selector */}
      <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl flex flex-col md:flex-row items-center justify-between gap-4`}>
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Columns size={18} className="text-blue-400" />
            <h3 className={`text-sm font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>Side-by-Side Policy Comparator</h3>
          </div>
          <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
            Compare active scenario <strong className={darkMode ? 'text-slate-200' : 'text-slate-700'}>[{primaryResult.params.name}]</strong> against benchmark policy counterfactuals
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'} font-medium`}>Compare with:</span>
          <select
            id="select_compare_scenario_b"
            value={scenarioBType}
            onChange={(e) => setScenarioBType(e.target.value as any)}
            className={`${darkMode ? 'bg-slate-950 border-slate-700 text-slate-200' : 'bg-white border-slate-200 text-slate-900'} rounded-xl px-3 py-2 text-xs font-semibold focus:ring-2 focus:ring-blue-500 outline-none`}
          >
            <option value="unmitigated">Counterfactual Unmitigated Wave</option>
            <option value="occupation_vax">Priority Occupation Vaccination</option>
            <option value="equity_targeted">Equity-Targeted Rollout</option>
            <option value="strict_lockdown">Strict Inter-County Lockdown</option>
          </select>
        </div>
      </div>

      {/* Delta Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Infections Delta */}
        <div className={`p-4 rounded-2xl border ${infectionsAverted >= 0 ? 'bg-emerald-950/20 border-emerald-900/50' : 'bg-red-950/20 border-red-900/50'} shadow-sm`}>
          <span className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-600'} block mb-1`}>Infections Averted (Net Delta):</span>
          <div className="flex items-baseline gap-2">
            <span className={`text-2xl font-extrabold font-mono ${infectionsAverted >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {infectionsAverted >= 0 ? `+${infectionsAverted.toLocaleString()}` : infectionsAverted.toLocaleString()}
            </span>
          </div>
          <span className={`text-[11px] ${darkMode ? 'text-slate-400' : 'text-slate-600'} block mt-1`}>
            Attack Rate: {sumA.attackRate}% (A) vs {sumB.attackRate}% (B)
          </span>
        </div>

        {/* Deaths Delta */}
        <div className={`p-4 rounded-2xl border ${deathsAverted >= 0 ? 'bg-emerald-950/20 border-emerald-900/50' : 'bg-red-950/20 border-red-900/50'} shadow-sm`}>
          <span className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-600'} block mb-1`}>Lives Saved / Mortality Delta:</span>
          <div className="flex items-baseline gap-2">
            <span className={`text-2xl font-extrabold font-mono ${deathsAverted >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {deathsAverted >= 0 ? `+${deathsAverted.toLocaleString()}` : deathsAverted.toLocaleString()}
            </span>
          </div>
          <span className={`text-[11px] ${darkMode ? 'text-slate-400' : 'text-slate-600'} block mt-1`}>
            Total Deaths: {sumA.totalDeaths.toLocaleString()} vs {sumB.totalDeaths.toLocaleString()}
          </span>
        </div>

        {/* Peak ICU Relief */}
        <div className={`p-4 rounded-2xl border ${icuPeakReduction >= 0 ? 'bg-blue-950/20 border-blue-900/50' : 'bg-amber-950/20 border-amber-900/50'} shadow-sm`}>
          <span className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-600'} block mb-1`}>Peak ICU Pressure Reduction:</span>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-extrabold text-blue-400 font-mono">
              {icuPeakReduction.toFixed(1)}%
            </span>
          </div>
          <span className={`text-[11px] ${darkMode ? 'text-slate-400' : 'text-slate-600'} block mt-1`}>
            Overload Days: {sumA.daysIcuOverloaded} days vs {sumB.daysIcuOverloaded} days
          </span>
        </div>
      </div>

      {/* Comparative Multi-Curve Chart */}
      <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl`}>
        <div className="mb-4">
          <h4 className={`text-sm font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>Epidemic Curve Overlay (Scenario A vs Scenario B)</h4>
          <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Solid Blue: Active Scenario A | Dashed Rose: Comparison Scenario B</p>
        </div>

        <div className="w-full h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={mergedData} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={darkMode ? '#1e293b' : '#f1f5f9'} />
              <XAxis dataKey="day" stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} tickFormatter={(v) => `${(v / 1e3).toFixed(0)}k`} />
              <Tooltip contentStyle={{ backgroundColor: darkMode ? '#0f172a' : '#ffffff', borderColor: darkMode ? '#334155' : '#e2e8f0', borderRadius: '12px', fontSize: '12px' }} />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
              <Line type="monotone" dataKey="infectedA" name={`[A] ${primaryResult.params.name} (Active Infectious)`} stroke="#3b82f6" strokeWidth={2.5} dot={false} />
              <Line type="monotone" dataKey="infectedB" name={`[B] Scenario: ${scenarioBType.toUpperCase()} (Active Infectious)`} stroke="#f43f5e" strokeWidth={2} strokeDasharray="5 5" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
