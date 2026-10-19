import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  FileSpreadsheet, 
  Download, 
  Database,
  Cpu,
  TrendingUp,
  Activity,
  CheckCircle2, 
  RefreshCw,
  Globe,
  ShieldCheck,
  Table as TableIcon,
  Info,
  Calendar
} from 'lucide-react';
import { SimulationResult, LanguageCode } from '../types';
import { useToast } from './ToastContainer';
import { ApiClient } from '../services/apiClient';

interface ReportsViewProps {
  simulationResult: SimulationResult | null;
  lang: LanguageCode;
  darkMode: boolean;
  userEmail?: string;
}

type ReportType = 'data_provenance' | 'models_cv' | 'weekly_forecast' | 'seir_abm_scenarios';

interface SummaryMetric {
  label: string;
  value: string | number;
}

interface ReportTable {
  title: string;
  headers: string[];
  rows: (string | number)[][];
}

interface PreviewData {
  report_type: string;
  title: string;
  subtitle: string;
  generated_at: string;
  provenance_badge: string;
  summary_metrics: SummaryMetric[];
  tables: ReportTable[];
  scientific_notes: string[];
}

const repI18n = {
  es: {
    headerTitle: 'Módulo de Informes Técnicos y Evidencia Científica',
    headerDesc: 'Informes académicos oficiales con trazabilidad estricta, compilados dinámicamente con ReportLab (PDF) y OpenPyXL (Excel). Cifras vinculadas a los datos crudos y artefactos de evaluación del repositorio.',
    btnPdf: 'Exportar PDF (ReportLab)',
    btnPdfLoading: 'Generando PDF...',
    btnExcel: 'Exportar Excel (OpenPyXL)',
    btnExcelLoading: 'Generando Excel...',
    activeBadge: '● ACTIVO',
    officialDoc: 'DOCUMENTO OFICIAL',
    loadingPreview: 'Cargando vista previa...',
    pending: 'En espera',
    refreshTooltip: 'Refrescar vista previa',
    sec1Title: '1. Ficha Resumen de Indicadores y Trazabilidad',
    notesTitle: 'Notas Metodológicas, Delimitaciones y Rigor Epistemológico:',
    toastPdfSuccessTitle: 'PDF Generado (ReportLab)',
    toastPdfSuccessDesc: 'Informe institucional descargado en idioma',
    toastExcelSuccessTitle: 'Excel Generado (OpenPyXL)',
    toastExcelSuccessDesc: 'Libro de cálculo descargado con hojas estructuradas.',
    cutoffPickerLabel: 'Fecha de Corte para Pronóstico (t0):',
    cutoffExample: '(Ej. 2024-07-28 para meseta endémica, o 2021-07-11 para pico ola Delta)',
    btnApplyCutoff: 'Aplicar Corte',
    simIdLabel: 'ID de Simulación para Escenarios:',
    simPlaceholder: 'sim-xxxxxxxxxxxx (o vacío para última)',
    btnApplySim: 'Cargar Simulación',
    footerGeneratedBy: 'Gemelo Digital Epidemiológico GD_TI · Auditoría inmutable de modelos y vigilancia · Kenia'
  },
  en: {
    headerTitle: 'Scientific & Technical Reporting System',
    headerDesc: 'Official academic dossiers with mathematical rigor, compiled using ReportLab (PDF) and OpenPyXL (Excel). No mock figures: all metrics link directly to raw project datasets and FastAPI inference.',
    btnPdf: 'Export PDF (ReportLab)',
    btnPdfLoading: 'Generating PDF...',
    btnExcel: 'Export Excel (OpenPyXL)',
    btnExcelLoading: 'Generating Excel...',
    activeBadge: '● ACTIVE',
    officialDoc: 'OFFICIAL DOCUMENT',
    loadingPreview: 'Loading preview...',
    pending: 'Pending',
    refreshTooltip: 'Refresh preview',
    sec1Title: '1. Key Indicators and Traceability Summary',
    notesTitle: 'Methodological Notes, Delimitations, and Epistemological Rigor:',
    toastPdfSuccessTitle: 'PDF Generated (ReportLab)',
    toastPdfSuccessDesc: 'Institutional report downloaded in language',
    toastExcelSuccessTitle: 'Excel Generated (OpenPyXL)',
    toastExcelSuccessDesc: 'Structured workbook downloaded successfully.',
    cutoffPickerLabel: 'Forecasting Cutoff Date (t0):',
    cutoffExample: '(e.g., 2024-07-28 for endemic plateau, or 2021-07-11 for Delta wave peak)',
    btnApplyCutoff: 'Apply Cutoff',
    simIdLabel: 'Scenario Simulation ID:',
    simPlaceholder: 'sim-xxxxxxxxxxxx (or empty for latest)',
    btnApplySim: 'Load Simulation',
    footerGeneratedBy: 'GD_TI Epidemiological Digital Twin · Immutable model & surveillance audit · Kenya'
  },
  sw: {
    headerTitle: 'Moduli ya Ripoti za Kisayansi na Kiufundi',
    headerDesc: 'Ripoti rasmi za utafiti zilizo na uthibitisho wa kimahesabu, zilizokusanywa kwa kutumia ReportLab (PDF) na OpenPyXL (Excel). Hakuna data bandia: nambari zote zinatoka moja kwa moja kutoka kwa faili za mradi na API ya FastAPI.',
    btnPdf: 'Pakua PDF (ReportLab)',
    btnPdfLoading: 'Inazalisha PDF...',
    btnExcel: 'Pakua Excel (OpenPyXL)',
    btnExcelLoading: 'Inazalisha Excel...',
    activeBadge: '● IMECHAGULIWA',
    officialDoc: 'HATI RASMI',
    loadingPreview: 'Inapakia hakiki...',
    pending: 'Inasubiri',
    refreshTooltip: 'Onyesha upya hakiki',
    sec1Title: '1. Muhtasari wa Viashiria na Ufuatiliaji',
    notesTitle: 'Maelezo ya Kimbinu, Vikwazo na Uthibiti wa Kisayansi:',
    toastPdfSuccessTitle: 'PDF Imetengenezwa (ReportLab)',
    toastPdfSuccessDesc: 'Ripoti ya kitaasisi imepakuliwa kwa lugha',
    toastExcelSuccessTitle: 'Excel Imetengenezwa (OpenPyXL)',
    toastExcelSuccessDesc: 'Jedwali la hesabu limepakuliwa kwa mafanikio.',
    cutoffPickerLabel: 'Tarehe ya Kukata kwa Utabiri (t0):',
    cutoffExample: '(Mfano: 2024-07-28 kwa kipindi cha kawaida, au 2021-07-11 kwa kilele cha wimbi la Delta)',
    btnApplyCutoff: 'Tekeleza Tarehe',
    simIdLabel: 'Kitambulisho cha Uigaji:',
    simPlaceholder: 'sim-xxxxxxxxxxxx (au wazi kwa ya hivi karibuni)',
    btnApplySim: 'Pakia Uigaji',
    footerGeneratedBy: 'Pacha ya Dijiti ya Epidemiolojia GD_TI · Ukaguzi thabiti wa mifano na ufuatiliaji · Kenya'
  }
};

export const ReportsView: React.FC<ReportsViewProps> = ({
  simulationResult,
  lang: initialLang,
  darkMode,
}) => {
  const [reportType, setReportType] = useState<ReportType>('data_provenance');
  const [reportLang, setReportLang] = useState<LanguageCode>(initialLang);
  const [cutoffDate, setCutoffDate] = useState<string>('2024-07-28');
  const [simulationId, setSimulationId] = useState<string>(simulationResult?.auditLogId || '');
  const [preview, setPreview] = useState<PreviewData | null>(null);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [isExporting, setIsExporting] = useState<'pdf' | 'excel' | null>(null);
  const { addToast } = useToast();

  const currentLang = (reportLang === 'en' || reportLang === 'sw') ? reportLang : 'es';
  const txt = repI18n[currentLang];

  // Sincronizar automáticamente con el idioma global del Header
  useEffect(() => {
    setReportLang(initialLang);
  }, [initialLang]);

  // Actualizar simulationId si cambia simulationResult
  useEffect(() => {
    if (simulationResult?.auditLogId) {
      setSimulationId(simulationResult.auditLogId);
    }
  }, [simulationResult?.auditLogId]);

  const reportTabs = [
    {
      id: 'data_provenance' as ReportType,
      icon: Database,
      name: reportLang === 'sw' ? 'Asili ya Data (OWID)' : reportLang === 'en' ? 'Data Provenance (OWID)' : 'Procedencia y Linaje de Datos',
      desc: reportLang === 'sw' ? 'Ufuatiliaji wa rekodi 1,674 na hash ya SHA-256' : reportLang === 'en' ? 'Audit of 1,674 records and SHA-256 integrity' : 'Linaje de 1,674 registros y hash criptográfico SHA-256',
    },
    {
      id: 'models_cv' as ReportType,
      icon: Cpu,
      name: reportLang === 'sw' ? 'Mafunzo na Uthibitishaji (CV)' : reportLang === 'en' ? 'Models & Cross-Validation' : 'Modelos, CV y Pruebas Estadísticas',
      desc: reportLang === 'sw' ? 'Ulinganisho wa TimeSeriesSplit, Wilcoxon na Diebold-Mariano' : reportLang === 'en' ? 'TimeSeriesSplit, Wilcoxon and Diebold-Mariano tests' : 'TimeSeriesSplit (5 folds), Wilcoxon y Diebold-Mariano HLN',
    },
    {
      id: 'weekly_forecast' as ReportType,
      icon: TrendingUp,
      name: reportLang === 'sw' ? 'Utabiri wa Kila Wiki' : reportLang === 'en' ? 'Weekly Forecasting' : 'Pronóstico Semanal e Inferencia',
      desc: reportLang === 'sw' ? 'Inferencia ya FastAPI kwa hatua ya t+1 na dirisha la wiki 4' : reportLang === 'en' ? 'FastAPI real-time inference for 1-step ahead (t+1) with 4-week lag window' : 'Inferencia operativa en FastAPI a 1 paso (t+1) con ventana de rezagos de 4 semanas',
    },
    {
      id: 'seir_abm_scenarios' as ReportType,
      icon: Activity,
      name: reportLang === 'sw' ? 'Matukio ya SEIR / Pacha ya Dijiti' : reportLang === 'en' ? 'SEIR / Digital Twin Scenarios' : 'Escenarios SEIR y Gemelo Digital',
      desc: reportLang === 'sw' ? 'Athari za NPI, DALYs, vitanda vya ICU na usawa wa kijamii' : reportLang === 'en' ? 'NPI interventions, DALYs averted and ICU capacity audit' : 'Simulación de intervenciones NPI, DALYs y saturación UCI',
    },
  ];

  const fetchPreview = async (type: ReportType, l: LanguageCode, customCutoff = cutoffDate, customSim = simulationId) => {
    setLoadingPreview(true);
    try {
      const data = await ApiClient.getReportPreview(type, l, {
        simulation_id: customSim || undefined,
        cutoff_date: customCutoff || '2024-07-28',
        county_code: 0,
      });
      setPreview(data);
    } catch (err: any) {
      console.error('Error fetching report preview:', err);
      addToast('error', 'Error', err.message || 'Error connecting to reports endpoint.');
    } finally {
      setLoadingPreview(false);
    }
  };

  useEffect(() => {
    fetchPreview(reportType, reportLang, cutoffDate, simulationId);
  }, [reportType, reportLang]);

  // Exportar a PDF usando ReportLab en backend
  const handleExportPdf = async () => {
    setIsExporting('pdf');
    try {
      const blob = await ApiClient.exportReportPdf(reportType, reportLang, {
        simulation_id: simulationId || undefined,
        cutoff_date: cutoffDate || '2024-07-28',
        county_code: 0,
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Reporte_${reportType}_${reportLang.toUpperCase()}_${new Date().toISOString().slice(0, 10)}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      addToast('success', txt.toastPdfSuccessTitle, `${txt.toastPdfSuccessDesc} ${reportLang.toUpperCase()}.`);
    } catch (err: any) {
      console.error('Error exportando PDF:', err);
      addToast('error', 'PDF Error', err.message || 'FastAPI connection failed');
    } finally {
      setIsExporting(null);
    }
  };

  // Exportar a Excel usando OpenPyXL en backend
  const handleExportExcel = async () => {
    setIsExporting('excel');
    try {
      const blob = await ApiClient.exportReportExcel(reportType, reportLang, {
        simulation_id: simulationId || undefined,
        cutoff_date: cutoffDate || '2024-07-28',
        county_code: 0,
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Reporte_${reportType}_${reportLang.toUpperCase()}_${new Date().toISOString().slice(0, 10)}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      addToast('success', txt.toastExcelSuccessTitle, txt.toastExcelSuccessDesc);
    } catch (err: any) {
      console.error('Error exportando Excel:', err);
      addToast('error', 'Excel Error', err.message || 'FastAPI connection failed');
    } finally {
      setIsExporting(null);
    }
  };

  return (
    <div id="reports_view" className="space-y-6 w-full">
      {/* Encabezado Principal y Acciones */}
      <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4`}>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <FileText size={22} className="text-blue-500" />
            <h3 className={`text-lg font-bold tracking-tight ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
              {txt.headerTitle}
            </h3>
          </div>
          <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'} max-w-2xl`}>
            {txt.headerDesc}
          </p>
        </div>

        {/* Acciones de Exportación e Idioma */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Selector de Idioma */}
          <div className={`flex items-center gap-1 p-1 rounded-xl border ${darkMode ? 'bg-slate-950 border-slate-800' : 'bg-slate-100 border-slate-200'}`}>
            <Globe size={14} className="ml-2 text-slate-400" />
            <button
              id="report_lang_es"
              onClick={() => setReportLang('es')}
              className={`px-2.5 py-1 text-xs font-bold rounded-lg transition cursor-pointer ${
                reportLang === 'es' ? 'bg-blue-600 text-white shadow' : darkMode ? 'text-slate-400 hover:text-slate-200' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              ES
            </button>
            <button
              id="report_lang_en"
              onClick={() => setReportLang('en')}
              className={`px-2.5 py-1 text-xs font-bold rounded-lg transition cursor-pointer ${
                reportLang === 'en' ? 'bg-blue-600 text-white shadow' : darkMode ? 'text-slate-400 hover:text-slate-200' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              EN
            </button>
            <button
              id="report_lang_sw"
              onClick={() => setReportLang('sw')}
              className={`px-2.5 py-1 text-xs font-bold rounded-lg transition cursor-pointer ${
                reportLang === 'sw' ? 'bg-blue-600 text-white shadow' : darkMode ? 'text-slate-400 hover:text-slate-200' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              SW
            </button>
          </div>

          {/* Botón Exportar PDF */}
          <button
            id="btn_export_pdf_reportlab"
            onClick={handleExportPdf}
            disabled={isExporting === 'pdf'}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-50 text-white text-xs font-bold shadow-lg shadow-blue-500/20 transition cursor-pointer"
          >
            {isExporting === 'pdf' ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>{txt.btnPdfLoading}</span>
              </>
            ) : (
              <>
                <FileText size={16} />
                <span>{txt.btnPdf}</span>
              </>
            )}
          </button>

          {/* Botón Exportar Excel */}
          <button
            id="btn_export_excel_openpyxl"
            onClick={handleExportExcel}
            disabled={isExporting === 'excel'}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:opacity-50 text-white text-xs font-bold shadow-lg shadow-emerald-500/20 transition cursor-pointer"
          >
            {isExporting === 'excel' ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>{txt.btnExcelLoading}</span>
              </>
            ) : (
              <>
                <FileSpreadsheet size={16} />
                <span>{txt.btnExcel}</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* 4 Pestañas de Áreas Académicas */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {reportTabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = reportType === tab.id;
          return (
            <button
              key={tab.id}
              id={`tab_report_${tab.id}`}
              onClick={() => setReportType(tab.id)}
              className={`p-4 rounded-xl border text-left transition cursor-pointer flex flex-col justify-between ${
                isActive
                  ? 'bg-blue-600/15 border-blue-500 ring-2 ring-blue-500/20 shadow-md'
                  : darkMode
                  ? 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                  : 'bg-white border-slate-200 hover:border-slate-300'
              }`}
            >
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Icon size={18} className={isActive ? 'text-blue-500' : darkMode ? 'text-slate-400' : 'text-slate-600'} />
                  <span className={`text-xs font-bold ${isActive ? 'text-blue-400' : darkMode ? 'text-slate-200' : 'text-slate-800'}`}>
                    {tab.name}
                  </span>
                </div>
                <p className={`text-[11px] leading-relaxed ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                  {tab.desc}
                </p>
              </div>
              <div className="mt-3 flex items-center justify-between pt-2 border-t border-slate-800/40 text-[10px] font-mono text-slate-400">
                <span>{tab.id.toUpperCase()}</span>
                {isActive && <span className="text-blue-400 font-bold">{txt.activeBadge}</span>}
              </div>
            </button>
          );
        })}
      </div>

      {/* Selector de Parámetros Dinámicos para Pronóstico o Escenarios */}
      {reportType === 'weekly_forecast' && (
        <div className={`p-4 rounded-xl border flex flex-col sm:flex-row items-center gap-3 ${darkMode ? 'bg-slate-900/80 border-slate-800' : 'bg-blue-50/50 border-blue-200'}`}>
          <div className="flex items-center gap-2 text-xs font-semibold">
            <Calendar size={16} className="text-blue-500" />
            <span>{txt.cutoffPickerLabel}</span>
          </div>
          <input
            type="date"
            value={cutoffDate}
            onChange={(e) => setCutoffDate(e.target.value)}
            className={`px-3 py-1.5 rounded-lg border text-xs font-mono ${darkMode ? 'bg-slate-950 border-slate-700 text-slate-200' : 'bg-white border-slate-300 text-slate-800'}`}
          />
          <button
            onClick={() => fetchPreview(reportType, reportLang, cutoffDate, simulationId)}
            className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition cursor-pointer"
          >
            {txt.btnApplyCutoff}
          </button>
          <span className="text-[11px] text-slate-400">
            {txt.cutoffExample}
          </span>
        </div>
      )}

      {reportType === 'seir_abm_scenarios' && (
        <div className={`p-4 rounded-xl border flex flex-col sm:flex-row items-center gap-3 ${darkMode ? 'bg-slate-900/80 border-slate-800' : 'bg-purple-50/50 border-purple-200'}`}>
          <div className="flex items-center gap-2 text-xs font-semibold">
            <Activity size={16} className="text-purple-500" />
            <span>{txt.simIdLabel}</span>
          </div>
          <input
            type="text"
            placeholder={txt.simPlaceholder}
            value={simulationId}
            onChange={(e) => setSimulationId(e.target.value)}
            className={`px-3 py-1.5 rounded-lg border text-xs font-mono w-64 ${darkMode ? 'bg-slate-950 border-slate-700 text-slate-200' : 'bg-white border-slate-300 text-slate-800'}`}
          />
          <button
            onClick={() => fetchPreview(reportType, reportLang, cutoffDate, simulationId)}
            className="px-3.5 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold transition cursor-pointer"
          >
            {txt.btnApplySim}
          </button>
        </div>
      )}

      {/* Vista Previa Interactiva */}
      <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl space-y-6`}>
        {/* Encabezado del Documento */}
        <div className={`flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 border-b gap-3 ${darkMode ? 'border-slate-800' : 'border-slate-200'}`}>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded font-bold ${darkMode ? 'bg-blue-950/60 text-blue-400 border border-blue-800/50' : 'bg-blue-50 text-blue-700 border border-blue-200'}`}>
                {preview?.provenance_badge || txt.officialDoc}
              </span>
              {loadingPreview && <RefreshCw size={12} className="animate-spin text-blue-400" />}
            </div>
            <h4 className={`text-lg font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
              {preview?.title || txt.loadingPreview}
            </h4>
            <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
              {preview?.subtitle}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className={`text-[11px] font-mono px-3 py-1 rounded-full border ${darkMode ? 'bg-slate-950 border-slate-800 text-slate-300' : 'bg-slate-100 border-slate-300 text-slate-700'}`}>
              {preview?.generated_at ? new Date(preview.generated_at).toLocaleString() : txt.pending}
            </span>
            <button
              onClick={() => fetchPreview(reportType, reportLang, cutoffDate, simulationId)}
              className={`p-1.5 rounded-lg border transition cursor-pointer ${darkMode ? 'bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700' : 'bg-slate-100 border-slate-300 text-slate-700 hover:bg-slate-200'}`}
              title={txt.refreshTooltip}
            >
              <RefreshCw size={14} />
            </button>
          </div>
        </div>

        {/* Ficha Resumen de Indicadores y Trazabilidad */}
        {preview && preview.summary_metrics && preview.summary_metrics.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-blue-400">
              <ShieldCheck size={16} />
              <span>{txt.sec1Title}</span>
            </div>
            <div className={`grid grid-cols-1 md:grid-cols-2 gap-2.5 p-4 rounded-xl border ${darkMode ? 'bg-slate-950/60 border-slate-800' : 'bg-slate-50 border-slate-200'}`}>
              {preview.summary_metrics.map((m, idx) => (
                <div key={idx} className="flex flex-col sm:flex-row sm:items-baseline justify-between border-b border-slate-800/30 pb-1.5 text-xs gap-1">
                  <span className={`font-semibold ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>{m.label}:</span>
                  <span className="font-mono text-blue-400 text-right font-medium">{String(m.value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tablas Estructuradas */}
        {preview && preview.tables && preview.tables.map((table, tIdx) => (
          <div key={tIdx} className="space-y-2">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-cyan-400">
              <TableIcon size={16} />
              <span>{tIdx + 2}. {table.title}</span>
            </div>
            <div className={`overflow-x-auto rounded-xl border ${darkMode ? 'border-slate-800 bg-slate-950/50' : 'border-slate-200 bg-white'}`}>
              <table className="w-full text-left text-xs">
                <thead className={`text-[10px] uppercase font-mono ${darkMode ? 'bg-slate-800/80 text-slate-300 border-b border-slate-700' : 'bg-slate-100 text-slate-700 border-b border-slate-200'}`}>
                  <tr>
                    {table.headers.map((h, i) => (
                      <th key={i} className="p-2.5 font-bold">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className={`divide-y font-mono text-[11px] ${darkMode ? 'divide-slate-800 text-slate-300' : 'divide-slate-200 text-slate-700'}`}>
                  {table.rows.map((row, rIdx) => (
                    <tr key={rIdx} className={darkMode ? 'hover:bg-slate-800/40' : 'hover:bg-slate-50'}>
                      {row.map((cell, cIdx) => (
                        <td key={cIdx} className="p-2.5">
                          {cell !== undefined && cell !== null ? String(cell) : '-'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))}

        {/* Notas Metodológicas y Delimitaciones */}
        {preview && preview.scientific_notes && preview.scientific_notes.length > 0 && (
          <div className="p-4 rounded-xl border border-blue-500/20 bg-blue-950/10 space-y-2">
            <div className="flex items-center gap-1.5 text-blue-400 font-bold text-xs">
              <Info size={16} />
              <span>{txt.notesTitle}</span>
            </div>
            <ul className={`list-disc list-inside space-y-1.5 text-xs ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
              {preview.scientific_notes.map((note, i) => (
                <li key={i} className="leading-relaxed">
                  {note}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Pie de página institucional auditado */}
        <div className={`pt-4 mt-2 border-t text-center text-[11px] font-mono ${darkMode ? 'border-slate-800 text-slate-400' : 'border-slate-200 text-slate-500'}`}>
          <p>{txt.footerGeneratedBy}</p>
        </div>
      </div>
    </div>
  );
};
