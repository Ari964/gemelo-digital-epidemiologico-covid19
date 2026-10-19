import React, { useState } from 'react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  Legend, 
  BarChart, 
  Bar 
} from 'recharts';
import { 
  Activity, 
  ShieldAlert, 
  HeartPulse, 
  Users, 
  Bed, 
  TrendingDown, 
  Award, 
  Scale, 
  Clock, 
  AlertTriangle,
  ArrowUpRight,
  Sparkles
} from 'lucide-react';
import { SimulationResult, LanguageCode } from '../types';
import { translations } from '../i18n/translations';
import { KENYA_COUNTIES } from '../data/kenyaCounties';

interface DashboardViewProps {
  simulationResult: SimulationResult | null;
  selectedCountyId: string;
  onSelectCounty: (countyId: string) => void;
  lang: LanguageCode;
  darkMode: boolean;
  onOpenCopilot: () => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  simulationResult,
  selectedCountyId,
  onSelectCounty,
  lang,
  darkMode,
  onOpenCopilot,
}) => {
  const t = translations[lang];
  const [activeChartTab, setActiveChartTab] = useState<'seir' | 'hospital_icu' | 'equity_strata' | 'rt_mobility'>('seir');

  if (!simulationResult) {
    return (
      <div id="dashboard_view" className="space-y-6 w-full">
        {/* Banner de Estado No Simulado */}
        <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/80 border-slate-800' : 'bg-white border-slate-200'} shadow-md text-center space-y-3`}>
          <div className="w-12 h-12 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center mx-auto">
            <Activity size={26} />
          </div>
          <h2 className={`text-lg font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
            {t.noSimulationTitle || 'Sin Simulación Ejecutada'}
          </h2>
          <p className={`text-xs max-w-lg mx-auto ${darkMode ? 'text-slate-400' : 'text-slate-600 font-medium'}`}>
            {t.noSimulationDesc || 'No hay proyecciones disponibles en este momento. Diríjase a «Fase 6: Despliegue de Escenarios» y presione «Ejecutar Gemelo Digital Calibrado» para calcular trayectorias y demanda hospitalaria.'}
          </p>
          <div className="pt-2">
            <span className="inline-block px-4 py-1.5 rounded-full text-xs font-mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
              «{t.executeSimPrompt || 'Ejecute una simulación'}»
            </span>
          </div>
        </div>

        {/* Tarjetas KPI en Estado Pendiente (Sin cifras de cero ni 450 camas) */}
        <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-4 gap-4 opacity-60">
          <div className={`p-4 rounded-2xl border ${darkMode ? 'bg-slate-900/60 border-slate-800' : 'bg-slate-100 border-slate-200'}`}>
            <span className="text-xs text-slate-500 block mb-1">{t.totalCases}</span>
            <span className="text-sm font-bold text-slate-400 font-mono">—</span>
            <span className="text-[10px] text-slate-500 block mt-1">«{t.executeSimPrompt || 'Ejecute una simulación'}»</span>
          </div>
          <div className={`p-4 rounded-2xl border ${darkMode ? 'bg-slate-900/60 border-slate-800' : 'bg-slate-100 border-slate-200'}`}>
            <span className="text-xs text-slate-500 block mb-1">{t.peakIcuBedDemand}</span>
            <span className="text-sm font-bold text-slate-400 font-mono">—</span>
            <span className="text-[10px] text-slate-500 block mt-1">«{t.executeSimPrompt || 'Ejecute una simulación'}»</span>
          </div>
          <div className={`p-4 rounded-2xl border ${darkMode ? 'bg-slate-900/60 border-slate-800' : 'bg-slate-100 border-slate-200'}`}>
            <span className="text-xs text-slate-500 block mb-1">{t.totalDeaths}</span>
            <span className="text-sm font-bold text-slate-400 font-mono">—</span>
            <span className="text-[10px] text-slate-500 block mt-1">«{t.executeSimPrompt || 'Ejecute una simulación'}»</span>
          </div>
          <div className={`p-4 rounded-2xl border ${darkMode ? 'bg-slate-900/60 border-slate-800' : 'bg-slate-100 border-slate-200'}`}>
            <span className="text-xs text-slate-500 block mb-1">{t.dalysAverted}</span>
            <span className="text-sm font-bold text-slate-400 font-mono">—</span>
            <span className="text-[10px] text-slate-500 block mt-1">«{t.executeSimPrompt || 'Ejecute una simulación'}»</span>
          </div>
        </div>
      </div>
    );
  }

  const summary = simulationResult.summary;
  const trajectory = simulationResult.nationalTrajectory;

  const icuCapacity = summary.totalIcuCapacity;
  const icuOverload = summary.peakIcuBedDemand > icuCapacity;

  return (
    <div id="dashboard_view" className="space-y-6 w-full">
      {/* Top Banner with Alert & AI Copilot Callout */}
      <div className={`p-4 rounded-2xl border ${darkMode ? 'bg-gradient-to-r from-slate-900 via-blue-950/40 to-slate-900 border-slate-800' : 'bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-100'} flex flex-col md:flex-row items-center justify-between gap-4 shadow-md`}>
        <div className="flex items-center gap-3.5">
          <div className="p-2.5 rounded-xl bg-blue-600 text-white shadow-md">
            <Activity size={22} />
          </div>
          <div>
            <h2 className={`text-base font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'} flex items-center gap-2`}>
              {simulationResult.params.name}
              <span className="text-[11px] font-mono px-2 py-0.5 rounded-md bg-blue-500/20 text-blue-300 border border-blue-400/30">
                {simulationResult.params.pathogen.toUpperCase()}
              </span>
            </h2>
            <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
              Simulación de escenarios (47 Condados de Kenia, {summary.totalPopulation.toLocaleString()} hab Censo KNBS) | Semilla: #{simulationResult.params.randomSeed} | Hash: <span className={`font-mono ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>{simulationResult.datasetHash.slice(0, 14)}...</span>
            </p>
          </div>
        </div>

        <button
          id="btn_open_ai_copilot_banner"
          onClick={onOpenCopilot}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-blue-500/20 transition cursor-pointer"
        >
          <Sparkles size={16} />
          Ask AI Epidemiologist
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-4 gap-4">
        {/* Total Cases */}
        <div className={`p-4 rounded-2xl border ${darkMode ? 'bg-slate-900/80 border-slate-800' : 'bg-white border-slate-200'} shadow-sm`}>
          <div className={`flex items-center justify-between ${darkMode ? 'text-slate-400' : 'text-slate-500'} mb-1.5`}>
            <span className="text-xs font-medium">{t.totalCases}</span>
            <Users size={16} className="text-blue-400" />
          </div>
          <div className={`text-2xl font-extrabold ${darkMode ? 'text-slate-100' : 'text-slate-900'} font-mono`}>
            {summary.totalInfections.toLocaleString()}
          </div>
          <div className={`mt-1 text-[11px] ${darkMode ? 'text-slate-400' : 'text-slate-500'} flex items-center gap-1`}>
            <span>{t.attackRate}:</span>
            <strong className="text-blue-400 font-mono">{summary.attackRate}%</strong>
          </div>
        </div>

        {/* Peak ICU vs Capacity */}
        <div className={`p-4 rounded-2xl border ${icuOverload ? 'bg-red-950/20 border-red-900/50' : (darkMode ? 'bg-slate-900/80 border-slate-800' : 'bg-white border-slate-200')} shadow-sm`}>
          <div className={`flex items-center justify-between ${darkMode ? 'text-slate-400' : 'text-slate-500'} mb-1.5`}>
            <span className="text-xs font-medium">{t.peakIcuBedDemand}</span>
            <Bed size={16} className={icuOverload ? 'text-red-400' : 'text-emerald-400'} />
          </div>
          <div className="flex items-baseline gap-2">
            <span className={`text-2xl font-extrabold font-mono ${icuOverload ? 'text-red-400' : (darkMode ? 'text-slate-100' : 'text-slate-900')}`}>
              {summary.peakIcuBedDemand.toLocaleString()}
            </span>
            <span className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'} font-mono`}>/ {icuCapacity} beds</span>
          </div>
          <div className={`mt-1 text-[11px] ${darkMode ? 'text-slate-400' : 'text-slate-500'} flex items-center gap-1`}>
            {icuOverload ? (
              <span className="text-red-400 font-medium flex items-center gap-0.5">
                <AlertTriangle size={12} /> {summary.daysIcuOverloaded} days surge exceedance
              </span>
            ) : (
              <span className="text-emerald-400 font-medium">Within safe surge limits</span>
            )}
          </div>
        </div>

        {/* Total Mortality & Rate */}
        <div className={`p-4 rounded-2xl border ${darkMode ? 'bg-slate-900/80 border-slate-800' : 'bg-white border-slate-200'} shadow-sm`}>
          <div className={`flex items-center justify-between ${darkMode ? 'text-slate-400' : 'text-slate-500'} mb-1.5`}>
            <span className="text-xs font-medium">{t.totalDeaths}</span>
            <HeartPulse size={16} className="text-rose-400" />
          </div>
          <div className={`text-2xl font-extrabold ${darkMode ? 'text-slate-100' : 'text-slate-900'} font-mono`}>
            {summary.totalDeaths.toLocaleString()}
          </div>
          <div className={`mt-1 text-[11px] ${darkMode ? 'text-slate-400' : 'text-slate-500'} flex items-center gap-1`}>
            <span>{t.mortalityRate}:</span>
            <strong className="text-rose-400 font-mono">{summary.mortalityPer100k}</strong>
          </div>
        </div>

        {/* DALYs Averted & Equity */}
        <div className={`p-4 rounded-2xl border ${darkMode ? 'bg-slate-900/80 border-slate-800' : 'bg-white border-slate-200'} shadow-sm`}>
          <div className={`flex items-center justify-between ${darkMode ? 'text-slate-400' : 'text-slate-500'} mb-1.5`}>
            <span className="text-xs font-medium">{t.dalysAverted}</span>
            <Award size={16} className="text-amber-400" />
          </div>
          <div className="text-2xl font-extrabold text-amber-400 font-mono">
            {summary.dalysAverted.toLocaleString()}
          </div>
          <div className={`mt-1 text-[11px] ${darkMode ? 'text-slate-400' : 'text-slate-500'} flex items-center gap-1`}>
            <span>{t.demographicParity}:</span>
            <strong className="text-emerald-400 font-mono">{summary.demographicParityRatio}x</strong>
          </div>
        </div>
      </div>

      {/* Interactive Charts Panel */}
      <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl`}>
        <div className={`flex flex-wrap items-center justify-between gap-3 mb-4 pb-3 border-b ${darkMode ? 'border-slate-800' : 'border-slate-200'}`}>
          <div>
            <h3 className={`text-sm font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>National Epidemiological Trajectory</h3>
            <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Daily compartmental states and health system stress over {simulationResult.params.durationDays} days</p>
          </div>

          {/* Chart View Selector */}
          <div className={`flex ${darkMode ? 'bg-slate-950' : 'bg-slate-100'} p-1 rounded-xl border ${darkMode ? 'border-slate-800' : 'border-slate-200'} text-xs`}>
            <button
              id="tab_chart_seir"
              onClick={() => setActiveChartTab('seir')}
              className={`px-3 py-1.5 rounded-lg font-medium transition ${activeChartTab === 'seir' ? 'bg-blue-600 text-white shadow' : (darkMode ? 'text-slate-400 hover:text-slate-200' : 'text-slate-500 hover:text-slate-700')}`}
            >
              SEIR Curves
            </button>
            <button
              id="tab_chart_hospital"
              onClick={() => setActiveChartTab('hospital_icu')}
              className={`px-3 py-1.5 rounded-lg font-medium transition ${activeChartTab === 'hospital_icu' ? 'bg-blue-600 text-white shadow' : (darkMode ? 'text-slate-400 hover:text-slate-200' : 'text-slate-500 hover:text-slate-700')}`}
            >
              Hospital & ICU Demand
            </button>
            <button
              id="tab_chart_equity"
              onClick={() => setActiveChartTab('equity_strata')}
              className={`px-3 py-1.5 rounded-lg font-medium transition ${activeChartTab === 'equity_strata' ? 'bg-blue-600 text-white shadow' : (darkMode ? 'text-slate-400 hover:text-slate-200' : 'text-slate-500 hover:text-slate-700')}`}
            >
              DHS Wealth Strata (Q1 vs Q5)
            </button>
            <button
              id="tab_chart_rt"
              onClick={() => setActiveChartTab('rt_mobility')}
              className={`px-3 py-1.5 rounded-lg font-medium transition ${activeChartTab === 'rt_mobility' ? 'bg-blue-600 text-white shadow' : (darkMode ? 'text-slate-400 hover:text-slate-200' : 'text-slate-500 hover:text-slate-700')}`}
            >
              Effective Rt & Mobility
            </button>
          </div>
        </div>

        {/* Chart Content Area */}
        <div className="w-full h-80">
          {activeChartTab === 'seir' && (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trajectory} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorInf" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#f43f5e" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorExp" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#fbbf24" stopOpacity={0.7}/>
                    <stop offset="95%" stopColor="#fbbf24" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorRec" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.6}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke={darkMode ? '#1e293b' : '#f1f5f9'} />
                <XAxis dataKey="day" stroke="#94a3b8" tick={{ fontSize: 11 }} label={{ value: 'Simulation Day', position: 'insideBottom', offset: -5, fill: '#64748b', fontSize: 11 }} />
                <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} tickFormatter={(val) => (val >= 1e6 ? `${(val / 1e6).toFixed(1)}M` : `${(val / 1e3).toFixed(0)}k`)} />
                <Tooltip
                  contentStyle={{ backgroundColor: darkMode ? '#0f172a' : '#ffffff', borderColor: darkMode ? '#334155' : '#e2e8f0', borderRadius: '12px', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
                <Area type="monotone" dataKey="infected" name="Infectious (I)" stroke="#f43f5e" fillOpacity={1} fill="url(#colorInf)" />
                <Area type="monotone" dataKey="exposed" name="Exposed (E)" stroke="#fbbf24" fillOpacity={1} fill="url(#colorExp)" />
                <Area type="monotone" dataKey="recovered" name="Recovered (R)" stroke="#10b981" fillOpacity={1} fill="url(#colorRec)" />
                <Line type="monotone" dataKey="vaccinated" name="Vaccinated (V)" stroke="#8b5cf6" strokeWidth={2} dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          )}

          {activeChartTab === 'hospital_icu' && (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trajectory} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={darkMode ? '#1e293b' : '#f1f5f9'} />
                <XAxis dataKey="day" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ backgroundColor: darkMode ? '#0f172a' : '#ffffff', borderColor: darkMode ? '#334155' : '#e2e8f0', borderRadius: '12px', fontSize: '12px' }} />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
                <Line type="monotone" dataKey="hospitalizedActive" name="Active General Hospitalizations" stroke="#38bdf8" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="icuActive" name="Active ICU Occupancy" stroke="#f43f5e" strokeWidth={2.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          )}

          {activeChartTab === 'equity_strata' && (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trajectory} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={darkMode ? '#1e293b' : '#f1f5f9'} />
                <XAxis dataKey="day" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ backgroundColor: darkMode ? '#0f172a' : '#ffffff', borderColor: darkMode ? '#334155' : '#e2e8f0', borderRadius: '12px', fontSize: '12px' }} />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
                <Line type="monotone" dataKey="q1Cases" name="Q1 Poorest (Lowest 20%) Daily Incidence" stroke="#ef4444" strokeWidth={2.5} dot={false} />
                <Line type="monotone" dataKey="q5Cases" name="Q5 Wealthiest (Top 20%) Daily Incidence" stroke="#3b82f6" strokeWidth={2} strokeDasharray="5 5" dot={false} />
                <Line type="monotone" dataKey="q1Vaccinated" name="Q1 Cumulative Vaccines" stroke="#f59e0b" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="q5Vaccinated" name="Q5 Cumulative Vaccines" stroke="#10b981" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          )}

          {activeChartTab === 'rt_mobility' && (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trajectory} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={darkMode ? '#1e293b' : '#f1f5f9'} />
                <XAxis dataKey="day" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                <YAxis yAxisId="left" stroke="#94a3b8" tick={{ fontSize: 11 }} domain={[0, 3.5]} label={{ value: 'Effective Rt', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 11 }} />
                <YAxis yAxisId="right" orientation="right" stroke="#94a3b8" tick={{ fontSize: 11 }} domain={[0, 1.2]} label={{ value: 'Meta Mobility Index', angle: 90, position: 'insideRight', fill: '#94a3b8', fontSize: 11 }} />
                <Tooltip contentStyle={{ backgroundColor: darkMode ? '#0f172a' : '#ffffff', borderColor: darkMode ? '#334155' : '#e2e8f0', borderRadius: '12px', fontSize: '12px' }} />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
                <Line yAxisId="left" type="monotone" dataKey="rt" name="Effective Reproduction (Rt)" stroke="#ec4899" strokeWidth={2.5} dot={false} />
                <Line yAxisId="right" type="monotone" dataKey="mobilityIndex" name="Community Mobility Index" stroke="#06b6d4" strokeWidth={2} strokeDasharray="4 4" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Panel de Interpretación Metodológica Específica de la Figura */}
        <div className={`mt-4 p-4 rounded-xl border text-xs leading-relaxed space-y-1.5 ${darkMode ? 'bg-slate-950/60 border-slate-800 text-slate-300' : 'bg-slate-50 border-slate-200 text-slate-700'}`}>
          <div className="flex items-center gap-2 font-bold text-blue-500 dark:text-blue-400">
            <Info size={14} />
            <span>
              {lang === 'en' ? 'Methodological Interpretation of Current Simulation Run:' : lang === 'sw' ? 'Ufafanuzi wa Metodolojia wa Uigaji Huu:' : 'Interpretación Metodológica de la Corrida Actual:'}
            </span>
          </div>
          <p>
            <strong>{lang === 'en' ? 'Axes & Units:' : lang === 'sw' ? 'Mihimili na Vipimo:' : 'Ejes y Unidades:'}</strong>{' '}
            {lang === 'en'
              ? 'X-axis: Simulation Day (0 to ' + simulationResult.params.durationDays + ' days). Y-axis: Headcount (Individuals in compartment).'
              : lang === 'sw'
              ? 'Mhimili wa X: Siku ya uigaji (0 hadi ' + simulationResult.params.durationDays + '). Mhimili wa Y: Idadi ya watu katika kundi.'
              : 'Eje X: Día de simulación (0 a ' + simulationResult.params.durationDays + ' días). Eje Y: Personas en cada compartimento epidemiológico.'}
          </p>
          <p>
            <strong>{lang === 'en' ? 'Observed in this run:' : lang === 'sw' ? 'Kilichoonekana kwenye jaribio hili:' : 'Observado en esta corrida:'}</strong>{' '}
            {lang === 'en'
              ? `Scenario "${simulationResult.params.name}" projects ${summary.totalInfections.toLocaleString()} cumulative infections (${summary.attackRate}% attack rate) and a peak ICU demand of ${summary.peakIcuBedDemand.toLocaleString()} beds (${icuOverload ? summary.daysIcuOverloaded + ' days exceeding capacity' : 'within national capacity'}).`
              : lang === 'sw'
              ? `Hali ya "${simulationResult.params.name}" inakadiria maambukizi ${summary.totalInfections.toLocaleString()} (${summary.attackRate}%) na mahitaji ya juu ya vitanda vya ICU ${summary.peakIcuBedDemand.toLocaleString()} (${icuOverload ? 'kuzidi uwezo kwa siku ' + summary.daysIcuOverloaded : 'ndani ya uwezo wa kitaifa'}).`
              : `El escenario "${simulationResult.params.name}" proyecta ${summary.totalInfections.toLocaleString()} infecciones acumuladas (${summary.attackRate}% tasa de ataque) y un pico de demanda UCI de ${summary.peakIcuBedDemand.toLocaleString()} camas (${icuOverload ? summary.daysIcuOverloaded + ' días sobrepasando la capacidad' : 'dentro de la capacidad nacional'}).`}
          </p>
          <p>
            <strong>{lang === 'en' ? 'Decision Impact & Comparison:' : lang === 'sw' ? 'Athari ya Uamuzi:' : 'Impacto en Decisiones y Comparación:'}</strong>{' '}
            {lang === 'en'
              ? `Permits counterfactual comparison against unmitigated baseline, evaluating if NPI stringency (${(simulationResult.params.interventions.schoolClosure.active ? 0.35 : 0.1) * 100}%) and vaccination delay hospital surge exceedance.`
              : lang === 'sw'
              ? `Inaruhusu kulinganisha sera za NPI na chanjo ili kutathmini kama mzigo wa hospitali unadhibitiwa.`
              : `Permite contrastar contrafactualmente si la combinación de NPIs (${(simulationResult.params.interventions.schoolClosure.active ? 0.35 : 0.1) * 100}%) y vacunación previene o posterga el colapso hospitalario.`}
          </p>
          <p>
            <strong>{lang === 'en' ? 'Data Provenance:' : lang === 'sw' ? 'Asili ya Data:' : 'Procedencia del Dato/Parámetro:'}</strong>{' '}
            {lang === 'en'
              ? 'Population: KNBS 2019 Census Table 2.2. ICU Capacity: Barasa et al. (2020) PLOS ONE Table S1 (537 total verified beds).'
              : lang === 'sw'
              ? 'Watu: Sensa ya KNBS 2019. Vitanda vya ICU: Utafiti wa Barasa na wenzake (2020) PLOS ONE Jedwali S1 (vitanda 537 vilivyothibitishwa).'
              : 'Población: Censo KNBS 2019 Tabla 2.2. Capacidad UCI: Estudio Barasa et al. (2020) PLOS ONE Tabla S1 (537 camas verificadas).'}
          </p>
          <p className="text-amber-500 dark:text-amber-400 font-medium">
            ⚠️ <strong>{lang === 'en' ? 'Interpretation Boundary:' : lang === 'sw' ? 'Kikomo cha Ufafanuzi:' : 'Límite de Interpretación:'}</strong>{' '}
            {lang === 'en'
              ? 'Counterfactual mathematical simulation based on metapopulation differential equations. It does NOT represent observed clinical cases nor a proven causal effect of interventions.'
              : lang === 'sw'
              ? 'Uigaji wa kimahesabu wa kisayansi. HAUWAKILISHI kesi halisi zilizothibitishwa kliniki wala ushahidi kamili wa kisababishi.'
              : 'Simulación matemática contrafactual basada en ecuaciones diferenciales metapoblacionales. NO equivale a casos clínicos observados ni a un efecto causal comprobado de las políticas implementadas.'}
          </p>
        </div>
      </div>

      {/* Subcounty Ranking & Health System Stress Table */}
      <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl`}>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className={`text-sm font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>County & Subcounty Impact Breakdown</h3>
            <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Risk stratification, attack rates, ICU bed headroom across Kenya's decentralized health system</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className={`border-b ${darkMode ? 'border-slate-800 text-slate-400' : 'border-slate-200 text-slate-500'} font-mono uppercase tracking-wider`}>
                <th className="pb-3 font-semibold">County</th>
                <th className="pb-3 font-semibold">Population</th>
                <th className="pb-3 font-semibold">DHS Q1 Poverty</th>
                <th className="pb-3 font-semibold">Simulated Cases</th>
                <th className="pb-3 font-semibold">Attack Rate</th>
                <th className="pb-3 font-semibold">Peak ICU Need</th>
                <th className="pb-3 font-semibold">ICU Capacity</th>
                <th className="pb-3 font-semibold">Mortality</th>
                <th className="pb-3 font-semibold">Action</th>
              </tr>
            </thead>
            <tbody className={`divide-y ${darkMode ? 'divide-slate-800/60' : 'divide-slate-200'}`}>
              {KENYA_COUNTIES.slice(0, 8).map((c) => {
                const res = simulationResult.countyResults[c.id];
                const isOver = res && res.peakIcuDemand > c.icuBeds;

                return (
                  <tr key={c.id} className={`transition ${darkMode ? 'hover:bg-slate-800/30' : 'hover:bg-slate-100'}`}>
                    <td className={`py-3 font-semibold ${darkMode ? 'text-slate-200' : 'text-slate-900'} flex items-center gap-2`}>
                      <span className={`w-2 h-2 rounded-full ${isOver ? 'bg-red-500' : 'bg-emerald-500'}`} />
                      {c.name}
                    </td>
                    <td className={`py-3 ${darkMode ? 'text-slate-300' : 'text-slate-700'} font-mono`}>{(c.population).toLocaleString()}</td>
                    <td className="py-3 text-amber-400 font-mono">{(c.wealthQuintiles.q1_poorest * 100).toFixed(0)}%</td>
                    <td className={`py-3 ${darkMode ? 'text-slate-200' : 'text-slate-900'} font-mono font-bold`}>{res?.totalCases.toLocaleString() || '--'}</td>
                    <td className="py-3 text-blue-400 font-mono">{res?.attackRate || '--'}%</td>
                    <td className={`py-3 font-mono font-bold ${isOver ? 'text-red-400' : (darkMode ? 'text-slate-200' : 'text-slate-900')}`}>
                      {res?.peakIcuDemand || '--'}
                    </td>
                    <td className={`py-3 ${darkMode ? 'text-slate-400' : 'text-slate-500'} font-mono`}>{c.icuBeds} beds</td>
                    <td className="py-3 text-rose-400 font-mono">{res?.totalDeaths.toLocaleString() || '--'}</td>
                    <td className="py-3">
                      <button
                        id={`btn_inspect_county_${c.id}`}
                        onClick={() => onSelectCounty(c.id)}
                        className={`px-2.5 py-1 rounded-lg bg-blue-600/20 hover:bg-blue-600 ${darkMode ? 'text-blue-300 hover:text-white' : 'text-blue-700 hover:text-white'} transition font-medium text-[11px]`}
                      >
                        Inspect 3D
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Explicación Metodológica de la Tabla */}
        <div className={`mt-4 p-3 rounded-xl border text-[11px] leading-relaxed ${darkMode ? 'bg-slate-950/60 border-slate-800 text-slate-400' : 'bg-slate-50 border-slate-200 text-slate-600'}`}>
          <p>
            <strong>{lang === 'en' ? 'Reading the Table:' : lang === 'sw' ? 'Kusoma Jedwali:' : 'Lectura de la Tabla:'}</strong>{' '}
            {lang === 'en'
              ? 'Each row represents one of Kenya\'s 47 counties. ICU Capacity reflects Barasa et al. (2020) S1 Table. Simulated cases and peak ICU demand are computed by the metapopulation engine based on county population density and transmission kinetics.'
              : lang === 'sw'
              ? 'Kila safu inawakilisha moja ya kaunti 47 za Kenya. Uwezo wa ICU unatokana na jedwali la Barasa (2020) S1. Mahitaji ya ICU yanatokana na uigaji wa kimatawi.'
              : 'Cada fila representa uno de los 47 condados de Kenia. La capacidad UCI refleja la Tabla S1 de Barasa et al. (2020). Los casos y demanda máxima de UCI provienen de la simulación metapoblacional con base en densidad censal y cinética de transmisión.'}
          </p>
          <p className="mt-1 text-amber-500 dark:text-amber-400">
            ⚠️ <strong>{lang === 'en' ? 'Boundary:' : lang === 'sw' ? 'Kikomo:' : 'Límite:'}</strong>{' '}
            {lang === 'en'
              ? 'No clinical transfer function exists to convert national weekly cases to county ICU demand. Red dots indicate counterfactual surge exceedance under current model parameters, not observed hospital admissions.'
              : lang === 'sw'
              ? 'Hakuna mfumo halisi wa kubadilisha kesi za kitaifa kuwa wagonjwa wa ICU wa kaunti. Alama nyekundu inaonyesha mzigo wa mfano wa kimahesabu tu.'
              : 'No existe una función de transferencia clínica validada para convertir casos semanales nacionales en admisiones UCI por condado. Los puntos rojos indican sobrecarga contrafactual del modelo, no ingresos clínicos empíricos.'}
          </p>
        </div>
      </div>
    </div>
  );
};
