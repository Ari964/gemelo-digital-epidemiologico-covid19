import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  Calendar, 
  AlertTriangle, 
  CheckCircle, 
  Info, 
  Layers, 
  ArrowRight,
  Database,
  Sliders,
  ShieldCheck,
  RefreshCw
} from 'lucide-react';
import { ApiClient } from '../services/apiClient';
import { HistoricalCutoffsDTO, WeeklyPredictionResponseDTO } from '../types/apiContract';
import { LanguageCode } from '../i18n/translations';

interface WeeklyForecastingViewProps {
  darkMode: boolean;
  lang?: LanguageCode;
}

const forecastI18n = {
  es: {
    badgeCrisp: 'CRISP-DM Fase 5 & 6',
    badgeScope: 'Ámbito: Nacional (Kenia, country_code=0)',
    badgeHistory: 'Histórico: 2020 a Agosto 2024',
    title: 'Vigilancia Epidemiológica Semanal & Exploración de Sensibilidad',
    desc: 'Predicción semanal verificada mediante persistencia ingenua (modelo campeón) con separación estricta entre pronóstico estadístico y análisis de sensibilidad.',
    btnUpdate: 'Actualizar Predicción',
    lagRuleTitle: 'Regla de Frecuencia Semanal y Verificación de Retardo:',
    lagRuleText: 'Cada domingo de corte t0 provee weekly_lag_1 (casos positivos reportados durante esa semana). El horizonte de pronóstico es estrictamente la semana posterior t+1 = t0 + 7 días. No existe desfase temporal artificial ni datos futuros filtrados.',
    cutoffSelectTitle: 'Seleccionar Fecha de Corte Histórica (Domingo de Reporte OMS)',
    cutoffsCountSuffix: 'cortes disponibles en base',
    loadingCutoffs: 'Cargando cortes...',
    casesSuffix: 'casos',
    caseSuffix: 'caso',
    manualInputLabel: 'O ingrese corte manual (YYYY-MM-DD):',
    btnEvalCutoff: 'Evaluar Corte',
    panel1Title: 'Predicción Principal (Modelo Seleccionado)',
    panel1Badge: 'Campeón CV & Diebold-Mariano',
    prodModelLabel: 'Modelo en Producción:',
    cutoffLabel: 'Fecha de Corte (t0):',
    targetWeekLabel: 'Semana Pronosticada (t+1):',
    forecastCardTitle: 'Pronóstico de Casos Semanales (ŷ_t+1)',
    forecastBasedOn: 'Basado en:',
    casesAtCutoff: 'casos en la semana de corte',
    actualObservedLabel: 'Valor Realmente Observado en',
    unrecordedOrFuture: 'No registrado / Futuro',
    maeLabel: 'Error Absoluto (MAE):',
    panel2Title: 'Exploración Hipotética de Sensibilidad',
    panel2Badge: 'Random Forest v1.0 (No causal)',
    epistWarnTitle: 'Advertencia Epistemológica:',
    epistWarnText: 'Esta sección es únicamente exploratoria. Los cambios ante variaciones de variables de control no representan efectos causales comprobados de políticas públicas.',
    rfCardTitle: 'Predicción del Modelo Multivariado (RF)',
    overpredictsNotice: 'Sobrepredice significativamente en periodos de baja incidencia reportada.',
    inputValuesTitle: 'Valores de Entrada Utilizados (Post-2022 Imputados):',
    imputedLabel: '(imputado)',
    discrepancyTitle: 'Causa de la discrepancia:',
    refCasesTitle: 'Casos de Referencia Docente: Alineación Temporal y Evaluación Empírica',
    refCasesDesc: 'Bajo la convención temporal canónica unificada (t0 → t1 = t0 + 7 días), la persistencia utiliza los casos reales de t0 para pronosticar t1. En la fase endémica plana de baja transmisión, la persistencia simple es empíricamente superior al Random Forest:',
    card1Title: 'Corte 2024-07-28 (Cierre endémico plano)',
    card1Badge: 'Persistencia Óptima',
    card2Title: 'Corte 2024-07-21 (Corte con 1 caso reportado)',
    card2Badge: 'Transición',
    cellCutoff: 'Corte t0',
    cellNaive: 'Naive (ŷ)',
    cellRf: 'RF (ŷ)',
    cellReal: 'Real t+1',
    errorLabel: 'Error'
  },
  en: {
    badgeCrisp: 'CRISP-DM Phase 5 & 6',
    badgeScope: 'Scope: National (Kenya, country_code=0)',
    badgeHistory: 'Historical: 2020 to August 2024',
    title: 'Weekly Epidemiological Surveillance & Sensitivity Exploration',
    desc: 'Verified weekly forecasting via naive persistence (champion model) with strict separation between statistical point forecast and sensitivity analysis.',
    btnUpdate: 'Update Forecast',
    lagRuleTitle: 'Weekly Frequency Rule & Lag Verification:',
    lagRuleText: 'Each Sunday cutoff t0 provides weekly_lag_1 (positive cases reported during that week). The forecast horizon is strictly the subsequent week t+1 = t0 + 7 days. There is no artificial time lag or future data leakage.',
    cutoffSelectTitle: 'Select Historical Cutoff Date (WHO Reporting Sunday)',
    cutoffsCountSuffix: 'cutoffs available in database',
    loadingCutoffs: 'Loading cutoffs...',
    casesSuffix: 'cases',
    caseSuffix: 'case',
    manualInputLabel: 'Or enter manual cutoff (YYYY-MM-DD):',
    btnEvalCutoff: 'Evaluate Cutoff',
    panel1Title: 'Primary Forecast (Selected Model)',
    panel1Badge: 'Champion CV & Diebold-Mariano',
    prodModelLabel: 'Production Model:',
    cutoffLabel: 'Cutoff Date (t0):',
    targetWeekLabel: 'Forecasted Week (t+1):',
    forecastCardTitle: 'Weekly Case Forecast (ŷ_t+1)',
    forecastBasedOn: 'Based on:',
    casesAtCutoff: 'cases at cutoff week',
    actualObservedLabel: 'Actual Observed Value at',
    unrecordedOrFuture: 'Unrecorded / Future',
    maeLabel: 'Absolute Error (MAE):',
    panel2Title: 'Hypothetical Sensitivity Exploration',
    panel2Badge: 'Random Forest v1.0 (Non-causal)',
    epistWarnTitle: 'Epistemological Warning:',
    epistWarnText: 'This section is strictly exploratory. Variations in control variables do not represent proven causal public policy effects.',
    rfCardTitle: 'Multivariate Model Prediction (RF)',
    overpredictsNotice: 'Significantly overpredicts during low reported incidence periods.',
    inputValuesTitle: 'Input Feature Values (Post-2022 Imputed):',
    imputedLabel: '(imputed)',
    discrepancyTitle: 'Cause of discrepancy:',
    refCasesTitle: 'Teaching Reference Cases: Temporal Alignment & Empirical Evaluation',
    refCasesDesc: 'Under the canonical unified temporal convention (t0 → t1 = t0 + 7 days), persistence utilizes the actual cases of t0 to forecast t1. In the flat endemic phase of low transmission, simple persistence is empirically superior to Random Forest:',
    card1Title: 'Cutoff 2024-07-28 (Flat endemic closure)',
    card1Badge: 'Optimal Persistence',
    card2Title: 'Cutoff 2024-07-21 (Cutoff with 1 reported case)',
    card2Badge: 'Transition',
    cellCutoff: 'Cutoff t0',
    cellNaive: 'Naive (ŷ)',
    cellRf: 'RF (ŷ)',
    cellReal: 'Actual t+1',
    errorLabel: 'Error'
  },
  sw: {
    badgeCrisp: 'CRISP-DM Awamu ya 5 & 6',
    badgeScope: 'Eneo: Kitaifa (Kenya, country_code=0)',
    badgeHistory: 'Kihistoria: 2020 hadi Agosti 2024',
    title: 'Ufuatiliaji wa Magonjwa wa Kila Wiki na Uchunguzi wa Usikivu',
    desc: 'Utabiri wa kila wiki uliothibitishwa kupitia mwendelezo wa naive (muundo bingwa) na utengano wa wazi kati ya utabiri na uchunguzi wa usikivu.',
    btnUpdate: 'Sasisha Utabiri',
    lagRuleTitle: 'Kanuni ya Kila Wiki na Uthibitisho wa Retardo:',
    lagRuleText: 'Kila Jumapili ya tarehe ya kukata t0 inatoa weekly_lag_1 (kesi zilizorekodiwa katika wiki hiyo). Upeo wa utabiri ni wiki inayofuata t+1 = t0 + siku 7. Hakuna kuvuja kwa data ya baadaye.',
    cutoffSelectTitle: 'Chagua Tarehe ya Kihistoria ya Kukata (Jumapili ya Ripoti ya WHO)',
    cutoffsCountSuffix: 'tarehe zilizopo kwenye hifadhidata',
    loadingCutoffs: 'Inapakia tarehe...',
    casesSuffix: 'kesi',
    caseSuffix: 'kesi',
    manualInputLabel: 'Au weka tarehe mwenyewe (YYYY-MM-DD):',
    btnEvalCutoff: 'Tathmini Tarehe',
    panel1Title: 'Utabiri Mkuu (Muundo Uliochaguliwa)',
    panel1Badge: 'Bingwa CV & Diebold-Mariano',
    prodModelLabel: 'Muundo Kazini:',
    cutoffLabel: 'Tarehe ya Kukata (t0):',
    targetWeekLabel: 'Wiki Iliyotabiriwa (t+1):',
    forecastCardTitle: 'Utabiri wa Kesi za Kila Wiki (ŷ_t+1)',
    forecastBasedOn: 'Kulingana na:',
    casesAtCutoff: 'kesi katika wiki ya kukata',
    actualObservedLabel: 'Thamani Halisi Iliyorekodiwa katika',
    unrecordedOrFuture: 'Haijarekodiwa / Baadaye',
    maeLabel: 'Kosa Halisi (MAE):',
    panel2Title: 'Uchunguzi wa Kinadharia wa Usikivu',
    panel2Badge: 'Random Forest v1.0 (Sio ya sababu)',
    epistWarnTitle: 'Onyo la Kitaalamu:',
    epistWarnText: 'Sehemu hii ni ya uchunguzi tu. Mabadiliko ya vigezo vya kudhibiti hayawakilishi matokeo ya moja kwa moja ya sera za umma.',
    rfCardTitle: 'Utabiri wa Muundo wa Vigezo Vingi (RF)',
    overpredictsNotice: 'Inatabiri kupita kiasi wakati wa maambukizi madogo.',
    inputValuesTitle: 'Vigezo Vilivyotumika (Baada ya 2022 Vimekisiwa):',
    imputedLabel: '(imekisiwa)',
    discrepancyTitle: 'Sababu ya tofauti:',
    refCasesTitle: 'Mifano ya Kufundishia: Mfuatano wa Muda na Tathmini ya Kisayansi',
    refCasesDesc: 'Chini ya mpangilio rasmi wa muda (t0 → t1 = t0 + siku 7), mwendelezo unatumia kesi halisi za t0 kutabiri t1. Katika kipindi tulivu cha maambukizi madogo, mwendelezo ni bora kuliko Random Forest:',
    card1Title: 'Tarehe 2024-07-28 (Mwisho tulivu wa janga)',
    card1Badge: 'Mwendelezo Bora',
    card2Title: 'Tarehe 2024-07-21 (Tarehe yenye kesi 1 iliyorekodiwa)',
    card2Badge: 'Mpito',
    cellCutoff: 'Tarehe t0',
    cellNaive: 'Naive (ŷ)',
    cellRf: 'RF (ŷ)',
    cellReal: 'Halisi t+1',
    errorLabel: 'Kosa'
  }
};

export const WeeklyForecastingView: React.FC<WeeklyForecastingViewProps> = ({ darkMode, lang = 'es' }) => {
  const currentLang = (lang === 'en' || lang === 'sw') ? lang : 'es';
  const txt = forecastI18n[currentLang];

  const [cutoffsData, setCutoffsData] = useState<HistoricalCutoffsDTO | null>(null);
  const [selectedCutoff, setSelectedCutoff] = useState<string>('2024-07-28');
  const [prediction, setPrediction] = useState<WeeklyPredictionResponseDTO | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Cargar lista dinámica de cortes históricos disponibles
  useEffect(() => {
    loadCutoffs();
  }, []);

  const loadCutoffs = async () => {
    try {
      const data = await ApiClient.getHistoricalCutoffs();
      setCutoffsData(data);
      if (data.available_cutoffs.length > 0) {
        const exists = data.available_cutoffs.some(c => c.date === '2024-07-28');
        const defaultDate = exists ? '2024-07-28' : data.available_cutoffs[0].date;
        setSelectedCutoff(defaultDate);
        executePrediction(defaultDate);
      }
    } catch (err: any) {
      setError('Error loading cutoffs: ' + (err.message || 'Connection error'));
    }
  };

  const executePrediction = async (cutoffDate: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await ApiClient.getWeeklyPrediction(cutoffDate, 0);
      setPrediction(res);
    } catch (err: any) {
      setError('Error calculating prediction: ' + (err.message || 'Server error'));
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCutoff = (date: string) => {
    setSelectedCutoff(date);
    executePrediction(date);
  };

  return (
    <div className="space-y-6">
      {/* Encabezado y Avisos de Alcance */}
      <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-sm`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                {txt.badgeCrisp}
              </span>
              <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
                {txt.badgeScope}
              </span>
              <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">
                {txt.badgeHistory}
              </span>
            </div>
            <h2 className="text-xl font-bold tracking-tight">
              {txt.title}
            </h2>
            <p className={`text-sm mt-1 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
              {txt.desc}
            </p>
          </div>

          <button
            onClick={() => executePrediction(selectedCutoff)}
            disabled={loading}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition cursor-pointer ${
              darkMode ? 'bg-blue-600 hover:bg-blue-500 text-white' : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            {txt.btnUpdate}
          </button>
        </div>

        {/* Banner de Verificación de Integridad Temporal */}
        <div className="mt-4 p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-start gap-3">
          <ShieldCheck size={20} className="text-blue-400 shrink-0 mt-0.5" />
          <div className="text-xs">
            <span className="font-semibold text-blue-300">{txt.lagRuleTitle} </span>
            <p className={`mt-0.5 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
              {txt.lagRuleText}
            </p>
          </div>
        </div>
      </div>

      {/* Selector Dinámico de Cortes Históricos */}
      <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-sm`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Calendar size={18} className="text-blue-400" />
            <h3 className="text-base font-semibold">{txt.cutoffSelectTitle}</h3>
          </div>
          <span className="text-xs font-mono text-slate-400">
            {cutoffsData ? `${cutoffsData.count} ${txt.cutoffsCountSuffix}` : txt.loadingCutoffs}
          </span>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center gap-2">
            <AlertTriangle size={16} />
            {error}
          </div>
        )}

        {/* Botones de Selección Rápida de Fechas */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2 mb-4">
          {cutoffsData?.available_cutoffs.slice(0, 12).map((item) => {
            const isSelected = selectedCutoff === item.date;
            const isReferenceCase = item.date === '2024-07-28';
            return (
              <button
                key={item.date}
                onClick={() => handleSelectCutoff(item.date)}
                className={`p-2.5 rounded-xl text-left border transition cursor-pointer relative ${
                  isSelected
                    ? 'bg-blue-600/20 border-blue-500 text-blue-300 font-bold shadow-md shadow-blue-500/10'
                    : darkMode
                    ? 'bg-slate-800/60 border-slate-700/60 hover:bg-slate-800 text-slate-300'
                    : 'bg-slate-50 border-slate-200 hover:bg-slate-100 text-slate-700'
                }`}
              >
                {isReferenceCase && (
                  <span className="absolute -top-2 -right-1 px-1.5 py-0.2 text-[9px] font-bold rounded bg-amber-500 text-slate-950 shadow">
                    Ref 28-Jul
                  </span>
                )}
                <div className="text-xs font-mono">{item.date}</div>
                <div className="text-[11px] text-slate-400 mt-1">
                  Obs: <span className="font-semibold text-slate-200">{item.new_cases_reported}</span> {item.new_cases_reported === 1 ? txt.caseSuffix : txt.casesSuffix}
                </div>
              </button>
            );
          })}
        </div>

        {/* Input libre para ingresar cualquier fecha de corte */}
        <div className="flex flex-col sm:flex-row items-center gap-3 pt-2 border-t border-slate-800/40">
          <label className="text-xs text-slate-400 whitespace-nowrap">
            {txt.manualInputLabel}
          </label>
          <input
            type="date"
            value={selectedCutoff}
            onChange={(e) => setSelectedCutoff(e.target.value)}
            className={`px-3 py-1.5 rounded-xl border text-xs font-mono ${
              darkMode ? 'bg-slate-800 border-slate-700 text-slate-200' : 'bg-white border-slate-300 text-slate-800'
            }`}
          />
          <button
            onClick={() => executePrediction(selectedCutoff)}
            className="px-3 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold cursor-pointer"
          >
            {txt.btnEvalCutoff}
          </button>
        </div>
      </div>

      {/* RESULTADO: 2 COLUMNAS (PREDICCIÓN PRINCIPAL vs SENSIBILIDAD HIPOTÉTICA) */}
      {prediction && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* PANEL 1: PREDICCIÓN PRINCIPAL (PERSISTENCIA INGENUA - CAMPEÓN) */}
          <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-blue-500/40' : 'bg-white border-blue-400'} shadow-lg shadow-blue-500/5`}>
            <div className="flex items-center justify-between pb-3 border-b border-slate-800/60">
              <div className="flex items-center gap-2">
                <CheckCircle size={20} className="text-emerald-400" />
                <h3 className="text-base font-bold text-emerald-400">
                  {txt.panel1Title}
                </h3>
              </div>
              <span className="px-2 py-0.5 text-xs font-bold rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                {txt.panel1Badge}
              </span>
            </div>

            <div className="mt-4 space-y-4">
              <div>
                <span className="text-xs text-slate-400">{txt.prodModelLabel}</span>
                <div className="text-sm font-mono font-semibold text-slate-200">
                  {prediction.primary_model_name}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
                <div>
                  <div className="text-[11px] text-slate-400">{txt.cutoffLabel}</div>
                  <div className="text-sm font-mono font-bold text-slate-200">{prediction.cutoff_date}</div>
                </div>
                <div>
                  <div className="text-[11px] text-slate-400">{txt.targetWeekLabel}</div>
                  <div className="text-sm font-mono font-bold text-blue-400">{prediction.target_week}</div>
                </div>
              </div>

              {/* Gran Tarjeta de Predicción */}
              <div className="p-5 rounded-xl bg-gradient-to-br from-blue-900/30 via-slate-800/50 to-slate-900/80 border border-blue-500/30 text-center">
                <div className="text-xs uppercase tracking-wider text-slate-400 font-semibold">
                  {txt.forecastCardTitle}
                </div>
                <div className="text-4xl font-extrabold font-mono text-white my-2">
                  {prediction.primary_forecast_cases.toFixed(1)}{' '}
                  <span className="text-sm font-normal text-slate-400">{txt.casesSuffix}</span>
                </div>
                <div className="text-xs text-slate-400">
                  {txt.forecastBasedOn} <code className="text-blue-300 font-mono">weekly_lag_1 = {prediction.validation_details.weekly_lag_1_used}</code> {txt.casesAtCutoff}
                </div>
              </div>

              {/* Comparación con el valor observado real */}
              <div className="p-3.5 rounded-xl bg-slate-800/40 border border-slate-700/60 flex items-center justify-between">
                <div>
                  <div className="text-[11px] text-slate-400">{txt.actualObservedLabel} {prediction.target_week}:</div>
                  <div className="text-lg font-mono font-bold text-white">
                    {prediction.target_observed_actual !== null 
                      ? `${prediction.target_observed_actual} ${txt.casesSuffix}` 
                      : txt.unrecordedOrFuture}
                  </div>
                </div>
                {prediction.forecast_error_mae !== null && (
                  <div className="text-right">
                    <div className="text-[11px] text-slate-400">{txt.maeLabel}</div>
                    <div className="text-base font-mono font-bold text-emerald-400">
                      {prediction.forecast_error_mae.toFixed(1)} {txt.casesSuffix}
                    </div>
                  </div>
                )}
              </div>

              <p className="text-xs text-slate-400 leading-relaxed">
                {prediction.primary_forecast_source}
              </p>
            </div>
          </div>

          {/* PANEL 2: EXPLORACIÓN HIPOTÉTICA DE SENSIBILIDAD (RANDOM FOREST) */}
          <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-amber-500/40' : 'bg-white border-amber-400'} shadow-lg shadow-amber-500/5`}>
            <div className="flex items-center justify-between pb-3 border-b border-slate-800/60">
              <div className="flex items-center gap-2">
                <Sliders size={20} className="text-amber-400" />
                <h3 className="text-base font-bold text-amber-400">
                  {txt.panel2Title}
                </h3>
              </div>
              <span className="px-2 py-0.5 text-xs font-bold rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                {txt.panel2Badge}
              </span>
            </div>

            <div className="mt-4 space-y-4">
              <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs">
                <span className="font-semibold block mb-1">{txt.epistWarnTitle}</span>
                {txt.epistWarnText}
              </div>

              {/* Gran Tarjeta de Predicción RF */}
              <div className="p-5 rounded-xl bg-gradient-to-br from-amber-950/20 via-slate-800/50 to-slate-900/80 border border-amber-500/30 text-center">
                <div className="text-xs uppercase tracking-wider text-slate-400 font-semibold">
                  {txt.rfCardTitle}
                </div>
                <div className="text-4xl font-extrabold font-mono text-amber-300 my-2">
                  {prediction.hypothetical_rf_prediction !== null
                    ? prediction.hypothetical_rf_prediction.toFixed(2)
                    : 'N/A'}{' '}
                  <span className="text-sm font-normal text-slate-400">{txt.casesSuffix}</span>
                </div>
                <div className="text-xs text-slate-400">
                  {txt.overpredictsNotice}
                </div>
              </div>

              {/* Imputaciones Críticas Post-2022 */}
              <div className="p-3.5 rounded-xl bg-slate-800/50 border border-slate-700/60 space-y-2">
                <div className="text-xs font-semibold text-slate-300">
                  {txt.inputValuesTitle}
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                  <div className="p-2 rounded bg-slate-900/80 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">stringency_index:</span>
                    <span className="text-amber-400 font-bold">
                      {prediction.validation_details.imputed_stringency_index ?? '22.77'} {txt.imputedLabel}
                    </span>
                  </div>
                  <div className="p-2 rounded bg-slate-900/80 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">reproduction_rate:</span>
                    <span className="text-amber-400 font-bold">
                      {prediction.validation_details.imputed_reproduction_rate ?? '0.54'} {txt.imputedLabel}
                    </span>
                  </div>
                </div>
              </div>

              {/* Explicación de la diferencia */}
              <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/50 text-xs text-slate-400 leading-relaxed">
                <span className="text-slate-300 font-semibold block mb-1">{txt.discrepancyTitle}</span>
                {prediction.sensitivity_disclaimer}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* CASO DE REFERENCIA OBLIGATORIO: 2024-07-28 & 2024-07-21 */}
      <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-sm`}>
        <div className="flex items-center gap-2 mb-3">
          <Info size={18} className="text-blue-400" />
          <h3 className="text-base font-bold">
            {txt.refCasesTitle}
          </h3>
        </div>

        <p className={`text-xs mb-4 leading-relaxed ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
          {txt.refCasesDesc}
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Tarjeta Caso 2024-07-28 */}
          <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-blue-400">{txt.card1Title}</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono">{txt.card1Badge}</span>
            </div>
            <div className="grid grid-cols-4 gap-2 text-center text-xs">
              <div className="p-2 rounded bg-slate-900/50">
                <span className="text-[10px] text-slate-400 block">{txt.cellCutoff}</span>
                <span className="font-bold text-white">0 {txt.casesSuffix}</span>
                <span className="text-[9px] text-slate-500 block">2024-07-28</span>
              </div>
              <div className="p-2 rounded bg-blue-950/40 border border-blue-500/30">
                <span className="text-[10px] text-blue-300 block">{txt.cellNaive}</span>
                <span className="font-bold text-white">0.0</span>
                <span className="text-[9px] text-emerald-400 block">{txt.errorLabel}: 0.0</span>
              </div>
              <div className="p-2 rounded bg-amber-950/40 border border-amber-500/30">
                <span className="text-[10px] text-amber-300 block">{txt.cellRf}</span>
                <span className="font-bold text-amber-400">70.76</span>
                <span className="text-[9px] text-red-400 block">{txt.errorLabel}: 70.76</span>
              </div>
              <div className="p-2 rounded bg-emerald-950/40 border border-emerald-500/30">
                <span className="text-[10px] text-emerald-300 block">{txt.cellReal}</span>
                <span className="font-bold text-emerald-300">0 {txt.casesSuffix}</span>
                <span className="text-[9px] text-slate-500 block">2024-08-04</span>
              </div>
            </div>
          </div>

          {/* Tarjeta Caso 2024-07-21 */}
          <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-indigo-400">{txt.card2Title}</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-mono">{txt.card2Badge}</span>
            </div>
            <div className="grid grid-cols-4 gap-2 text-center text-xs">
              <div className="p-2 rounded bg-slate-900/50">
                <span className="text-[10px] text-slate-400 block">{txt.cellCutoff}</span>
                <span className="font-bold text-white">1 {txt.caseSuffix}</span>
                <span className="text-[9px] text-slate-500 block">2024-07-21</span>
              </div>
              <div className="p-2 rounded bg-blue-950/40 border border-blue-500/30">
                <span className="text-[10px] text-blue-300 block">{txt.cellNaive}</span>
                <span className="font-bold text-white">1.0</span>
                <span className="text-[9px] text-emerald-400 block">{txt.errorLabel}: 1.0</span>
              </div>
              <div className="p-2 rounded bg-amber-950/40 border border-amber-500/30">
                <span className="text-[10px] text-amber-300 block">{txt.cellRf}</span>
                <span className="font-bold text-amber-400">70.76</span>
                <span className="text-[9px] text-red-400 block">{txt.errorLabel}: 70.76</span>
              </div>
              <div className="p-2 rounded bg-emerald-950/40 border border-emerald-500/30">
                <span className="text-[10px] text-emerald-300 block">{txt.cellReal}</span>
                <span className="font-bold text-emerald-300">0 {txt.casesSuffix}</span>
                <span className="text-[9px] text-slate-500 block">2024-07-28</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
