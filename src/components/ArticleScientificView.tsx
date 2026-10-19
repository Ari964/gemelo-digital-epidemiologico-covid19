/**
 * Vista del Artículo Científico (Fase 13 - GD_TI).
 *
 * Muestra las tablas y figuras del protocolo de evaluación temporal v2.0
 * con sus apartados de Interpretabilidad y Explicabilidad, descargas
 * individuales (PNG 500 dpi, CSV) y paquete ZIP conjunto, más la selección
 * asistida por IA (Ollama local, con fallback manual explícito).
 */
import React, { useState, useEffect } from 'react';
import {
  Download, Image, FileText, BarChart3, Activity, AlertTriangle, Info,
  Zap, Package, CheckCircle2, Layout, Save, ExternalLink,
} from 'lucide-react';
import { LanguageCode } from '../types';
import { useToast } from './ToastContainer';
import { ApiClient } from '../services/apiClient';

interface ArticuloFiguraElemento {
  id: string;
  titulo: string;
  interpretabilidad: {
    que_representa: string;
    variables_unidades_periodo_poblacion: string;
    como_leer: string;
    hallazgo_concreto: string;
    alcance_y_limites: string;
  };
  explicabilidad: {
    datos_y_transformaciones: string;
    metodo_modelo_prueba: string;
    parametros_y_supuestos: string;
    procedimiento_genera_resultado: string;
    limitaciones_y_fuentes_error: string;
  };
}

const FIGURAS_IMG: Record<string, string> = {
  particion_80_20: 'particion_temporal_80_20.png',
  observados_vs_predicciones: 'observados_vs_predicciones_test.png',
  residuos: 'residuos_distribucion_errores.png',
  mapa_calor: 'mapa_calor_correlaciones_desarrollo.png',
};

const CSV_EXPORT: Record<string, string> = {
  observados_vs_predicciones: 'observados_vs_predicciones_test.csv',
  residuos: 'residuos_campeon_test.csv',
  mapa_calor: 'correlaciones_pearson_desarrollo.csv',
  auditoria_temporal: 'auditoria_temporal_predicciones.csv',
};

const esFigura = (id: string): boolean => id in FIGURAS_IMG;

const artI18n = {
  es: {
    title: 'Artículo Científico - Tablas y Figuras',
    subtitle: 'Elementos del protocolo de evaluación temporal v2.0 (Kenia, OWID/OMS) listos para el artículo.',
    intro: 'Cada elemento incluye su imagen (cuando aplica), los apartados de Interpretabilidad (qué representa, cómo leerlo, hallazgo, alcance y límites) y Explicabilidad (datos, método, parámetros, procedimiento, limitaciones), generados desde los resultados y metadatos reales de la ejecución. Ninguna cifra es inventada.',
    cargando: 'Cargando resultados científicos...',
    error: 'Error al cargar resultados:',
    verMas: 'Ver detalle',
    verMenos: 'Ocultar detalle',
    descargarPng: 'Descargar PNG (500 dpi)',
    descargarCsv: 'Descargar CSV de datos',
    descargarPaquete: 'Descargar paquete ZIP (artículo completo)',
    iaSeleccion: 'Selección asistida por IA',
    iaModoAuto: 'Automático (Ollama local)',
    iaModoManual: 'Manual (criterios explícitos)',
    iaEjecutar: 'Ejecutar selección',
    iaOpcionManual: 'Usar selección manual',
    iaNoDisponible: 'Ollama no disponible: se usó selección manual por criterios explícitos.',
    iaSeleccionados: 'Elementos seleccionados para el artículo:',
    iaJustificacion: 'Justificación:',
    notaDescarte: 'Nota: la selección de la IA solo recomienda elementos ya disponibles; no altera cifras ni inventa evidencia.',
    tabla: 'Tabla',
    figura: 'Figura',
    modelo: 'Modelo',
    rol: 'Rol',
    parteA: 'A. Interpretabilidad',
    parteB: 'B. Explicabilidad',
    qr: '¿Qué representa?',
    vu: 'Variables, unidad, periodo y población',
    leer: 'Cómo leerlo',
    hallazgo: 'Hallazgo concreto',
    alcance: 'Alcance y límites',
    dt: 'Datos y transformaciones',
    metodo: 'Método, modelo o prueba',
    parametros: 'Parámetros y supuestos',
    proc: 'Procedimiento que genera el resultado',
    lim: 'Limitaciones y fuentes de error',
    disponible: 'Disponible',
    noDisponible: 'No disponible',
  },
  en: {
    title: 'Scientific Article - Tables and Figures',
    subtitle: 'Elements of the temporal evaluation protocol v2.0 (Kenya, OWID/WHO) ready for the article.',
    intro: 'Each element includes its image (when applicable), Interpretability (what it represents, how to read it, finding, scope and limits) and Explainability (data, method, parameters, procedure, limitations) sections, generated from real execution results and metadata. No figure is invented.',
    cargando: 'Loading scientific results...',
    error: 'Error loading results:',
    verMas: 'View detail',
    verMenos: 'Hide detail',
    descargarPng: 'Download PNG (500 dpi)',
    descargarCsv: 'Download data CSV',
    descargarPaquete: 'Download ZIP package (full article)',
    iaSeleccion: 'AI-assisted selection',
    iaModoAuto: 'Automatic (local Ollama)',
    iaModoManual: 'Manual (explicit criteria)',
    iaEjecutar: 'Run selection',
    iaOpcionManual: 'Use manual selection',
    iaNoDisponible: 'Ollama unavailable: manual selection by explicit criteria was used.',
    iaSeleccionados: 'Elements selected for the article:',
    iaJustificacion: 'Justification:',
    notaDescarte: 'Note: AI selection only recommends already-available elements; it does not alter figures or invent evidence.',
    tabla: 'Table',
    figura: 'Figure',
    modelo: 'Model',
    rol: 'Role',
    parteA: 'A. Interpretability',
    parteB: 'B. Explainability',
    qr: 'What it represents?',
    vu: 'Variables, unit, period and population',
    leer: 'How to read it',
    hallazgo: 'Concrete finding',
    alcance: 'Scope and limits',
    dt: 'Data and transformations',
    metodo: 'Method, model or test',
    parametros: 'Parameters and assumptions',
    proc: 'Procedure that generates the result',
    lim: 'Limitations and sources of error',
    disponible: 'Available',
    noDisponible: 'Not available',
  },
};

export const ArticleScientificView: React.FC<{
  lang: LanguageCode;
  darkMode: boolean;
}> = ({ lang, darkMode }) => {
  const t = (lang === 'en' ? artI18n.en : artI18n.es);
  const { addToast } = useToast();
  const [resultados, setResultados] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [openDetail, setOpenDetail] = useState<Record<string, boolean>>({});
  const [seleccionIA, setSeleccionIA] = useState<any>(null);
  const [seleccionando, setSeleccionando] = useState<boolean>(false);
  const [modoIA, setModoIA] = useState<'auto' | 'manual'>('auto');

  useEffect(() => {
    ApiClient.getArticuloResultados()
      .then((data) => {
        setResultados(data);
        setError(null);
      })
      .catch((err: any) => {
        setError(err.message || 'Error desconocido');
        setResultados(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const ie = resultados?.interpretabilidad_explicabilidad || {};
  const ids = Object.keys(ie);

  const toggleDetail = (id: string) => {
    setOpenDetail((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const isOpen = (id: string) => !!openDetail[id];
  const isSelected = (id: string) => !!seleccionIA?.seleccion?.includes(id);

  const handleDescargarArchivo = async (fileName: string, label: string) => {
    try {
      const blob = await ApiClient.descargarArticuloArchivo(fileName);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      addToast('success', 'Descarga', `${label} descargado.`);
    } catch (err: any) {
      addToast('error', 'Descarga', err.message || 'Error al descargar');
    }
  };

  const handleDescargarPaquete = async () => {
    try {
      const blob = await ApiClient.descargarPaqueteArticulo();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `GD_TI_Articulo_Paquete_${new Date().toISOString().slice(0, 10)}.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      addToast('success', 'Paquete', 'Paquete ZIP del artículo descargado.');
    } catch (err: any) {
      addToast('error', 'Paquete', err.message || 'Error al descargar paquete');
    }
  };

  const handleEjecutarIA = async () => {
    setSeleccionando(true);
    try {
      const data = await ApiClient.seleccionIAArticulo(modoIA, seleccionIA?.criterios_usados || undefined);
      setSeleccionIA(data);
      if (data.origen === 'fallback_manual' || data.origen === 'manual_explícito') {
        addToast('info', t.iaSeleccion, t.iaNoDisponible);
      } else {
        addToast('success', t.iaSeleccion, 'Selección asistida por IA completada.');
      }
    } catch (err: any) {
      addToast('error', t.iaSeleccion, err.message || 'Error en selección IA');
    } finally {
      setSeleccionando(false);
    }
  };

  const figuraUrl = (id: string) => {
    const file = FIGURAS_IMG[id];
    if (!file) return null;
    return `/api/v1/reports/articulo/figura/${encodeURIComponent(file)}`;
  };

  const renderSection = (title: string, content: string, icon: React.ReactNode) => (
    <div className={`p-3 rounded-lg border mb-2 ${darkMode ? 'bg-slate-800/50 border-slate-700 text-slate-200' : 'bg-slate-50 border-slate-200 text-slate-900'}`}>
      <div className="flex items-center gap-1.5 mb-1">
        {icon}
        <span className="text-xs font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400">{title}</span>
      </div>
      <div className="text-sm leading-relaxed">{content}</div>
    </div>
  );

  if (loading) {
    return (
      <div className="p-6 text-center text-slate-500 dark:text-slate-400">{t.cargando}</div>
    );
  }

  if (error || !resultados) {
    return (
      <div className="p-6 rounded-2xl border bg-rose-50 dark:bg-rose-900/20 border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300">
        <AlertTriangle size={20} className="mb-2" />
        <div className="font-bold">{t.error}</div>
        <div className="text-sm mt-1">{error}</div>
        <div className="text-xs mt-2 text-slate-500">
          Ejecute primero: <code className="font-mono">python scripts/protocolo_temporal_v2.py</code>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-4">
      {/* Header */}
      <div className={`rounded-2xl border p-6 ${darkMode ? 'bg-slate-900 border-slate-800 text-slate-100' : 'bg-white border-slate-200 text-slate-900'}`}>
        <div className="flex items-center gap-3 mb-2">
          <Layout size={24} className="text-blue-600 dark:text-blue-400" />
          <div>
            <h2 className="text-xl font-bold">{t.title}</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">{t.subtitle}</p>
          </div>
        </div>
        <p className="text-sm leading-relaxed">{t.intro}</p>
        <div className="mt-4 flex flex-wrap gap-2 text-xs">
          <span className="px-2 py-1 rounded bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 border border-blue-200 dark:border-blue-800">
            <Info size={12} /> Protocolo v2.0 · 80/20 temporal · 5 folds
          </span>
          <span className="px-2 py-1 rounded bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
            <CheckCircle2 size={12} /> Campeón: {resultados.campeon}
          </span>
          <span className="px-2 py-1 rounded bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
            <Activity size={12} /> Test: {resultados.particion_80_20.n_test} semanas
          </span>
        </div>
      </div>

      {/* Selección asistida por IA */}
      <div className={`rounded-2xl border p-5 ${darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-slate-50 border-slate-200'}`}>
        <div className="flex items-center gap-2 mb-3">
          <Zap size={18} className="text-amber-500" />
          <h3 className="font-bold text-sm">{t.iaSeleccion}</h3>
        </div>
        <div className="flex items-center gap-3 mb-3">
          <label className="text-xs font-medium text-slate-600 dark:text-slate-300">Modo:</label>
          <div className="flex gap-1">
            <button
              onClick={() => setModoIA('auto')}
              className={`px-3 py-1.5 rounded text-xs font-medium transition ${modoIA === 'auto' ? 'bg-amber-500 text-white' : 'bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-300'}`}
            >
              {t.iaModoAuto}
            </button>
            <button
              onClick={() => setModoIA('manual')}
              className={`px-3 py-1.5 rounded text-xs font-medium transition ${modoIA === 'manual' ? 'bg-blue-500 text-white' : 'bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-300'}`}
            >
              {t.iaModoManual}
            </button>
          </div>
        </div>
        <button
          id="btn_ejecutar_ia_seleccion"
          onClick={handleEjecutarIA}
          disabled={seleccionando}
          className="w-full py-2.5 rounded-lg text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white transition disabled:opacity-60 flex items-center justify-center gap-2"
        >
          {seleccionando ? (
            <>
              <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 2 5.373 2 12h4zm2 5.373V4a6 6 0 0111.447 3.411L16.533 15.94A8 8 0 015.806 17.373z"></path>
              </svg>
              <span>Cargando...</span>
            </>
          ) : (
            t.iaEjecutar
          )}
        </button>
        {seleccionIA && (
          <div className="mt-4 p-3 rounded-lg border border-amber-200 dark:border-amber-800/50 bg-amber-50 dark:bg-amber-900/20 text-xs">
            <div className="font-bold mb-1">{t.iaSeleccionados}</div>
            <div className="mb-1">{seleccionIA.seleccion?.join(', ') || '(ninguno)'}</div>
            <div className="font-bold mt-2 mb-1">{t.iaJustificacion}</div>
            <div className="text-slate-700 dark:text-slate-300">{seleccionIA.justificacion || ''}</div>
            {seleccionIA.origen === 'fallback_manual' && (
              <div className="mt-2 text-amber-600 dark:text-amber-400 font-semibold">{t.iaNoDisponible}</div>
            )}
            <div className="mt-2 text-[10px] text-slate-500 dark:text-slate-400">{t.notaDescarte}</div>
          </div>
        )}
      </div>

      {/* Elementos del artículo */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {ids.map((id) => {
          const sec = ie[id];
          const esFig = esFigura(id);
          return (
            <div
              key={id}
              className={`rounded-2xl border p-5 ${darkMode ? 'bg-slate-800 border-slate-700 text-slate-100' : 'bg-white border-slate-200 text-slate-900 shadow-sm hover:shadow-md transition'}`}
            >
              <div className="flex justify-between items-start mb-3">
                <div>
                  <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${esFig ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 border border-blue-200 dark:border-blue-800' : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'}`}>
                    {esFig ? t.figura : t.tabla}
                  </span>
                  <span className="ml-2 text-[10px] font-mono text-slate-400 dark:text-slate-500">{id}</span>
                </div>
                <button
                  onClick={() => toggleDetail(id)}
                  className="text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline"
                >
                  {isOpen(id) ? t.verMenos : t.verMas}
                </button>
              </div>

              {esFig && (
                <div className="mb-3 rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900">
                  <img
                    src={figuraUrl(id)}
                    alt={sec.titulo}
                    className="w-full h-48 object-cover"
                    loading="lazy"
                  />
                </div>
              )}

              <h4 className="text-sm font-bold mb-2 leading-snug">{sec.titulo}</h4>
              <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">
                {sec.interpretabilidad.que_representa}
              </p>

              {/* Descargas de la figura */}
              {esFig && (
                <div className="flex gap-2 mb-3">
                  <button
                    onClick={() => handleDescargarArchivo(FIGURAS_IMG[id], sec.titulo)}
                    className="flex-1 py-1.5 rounded border text-[10px] font-bold transition"
                    style={{ borderColor: darkMode ? '#4b5563' : '#e5e7eb', color: darkMode ? '#9ca3af' : '#374151' }}
                  >
                    <Download size={12} /> {t.descargarPng}
                  </button>
                  <button
                    onClick={() => {
                      const csv = CSV_EXPORT[id];
                      if (csv) handleDescargarArchivo(csv, sec.titulo);
                    }}
                    className="flex-1 py-1.5 rounded border text-[10px] font-bold transition"
                    style={{ borderColor: darkMode ? '#4b5563' : '#e5e7eb', color: darkMode ? '#9ca3af' : '#374151' }}
                  >
                    <FileText size={12} /> {t.descargarCsv}
                  </button>
                </div>
              )}

              {isOpen(id) && (
                <div className="space-y-3 pt-3 border-t border-slate-200 dark:border-slate-700">
                  {renderSection(t.parteA, sec.interpretabilidad.que_representa, <FileText size={14} />)}
                  {renderSection(t.qr, sec.interpretabilidad.variables_unidades_periodo_poblacion, <Activity size={14} />)}
                  {renderSection(t.leer, sec.interpretabilidad.como_leer, <BarChart3 size={14} />)}
                  {renderSection(t.hallazgo, sec.interpretabilidad.hallazgo_concreto, <CheckCircle2 size={14} />)}
                  {renderSection(t.alcance, sec.interpretabilidad.alcance_y_limites, <AlertTriangle size={14} />)}
                  {renderSection(t.parteB, sec.explicabilidad.datos_y_transformaciones, <Layout size={14} />)}
                  {renderSection(t.metodo, sec.explicabilidad.metodo_modelo_prueba, <Save size={14} />)}
                  {renderSection(t.parametros, sec.explicabilidad.parametros_y_supuestos, <Zap size={14} />)}
                  {renderSection(t.proc, sec.explicabilidad.procedimiento_genera_resultado, <ExternalLink size={14} />)}
                  {renderSection(t.lim, sec.explicabilidad.limitaciones_y_fuentes_error, <Info size={14} />)}
                </div>
              )}

              <div className={`mt-3 pt-3 border-t border-slate-200 dark:border-slate-700 text-[10px] font-bold ${isSelected(id) ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-500'}`}>
                {isSelected(id) ? '✓ Seleccionado para el artículo' : 'No seleccionado'}
              </div>
            </div>
          );
        })}
      </div>

      {/* Paquete conjunto */}
      <div className={`rounded-2xl border p-5 ${darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-slate-50 border-slate-200'}`}>
        <div className="flex items-center gap-3 mb-3">
          <Package size={20} className="text-blue-600 dark:text-blue-400" />
          <h3 className="font-bold text-sm">Descarga conjunta del artículo</h3>
        </div>
        <p className="text-xs text-slate-600 dark:text-slate-400 mb-3">
          ZIP con el JSON de resultados, todas las figuras (PNG + SVG a 500 dpi) y los CSV de exportación.
        </p>
        <button
          id="btn_descargar_paquete_articulo"
          onClick={handleDescargarPaquete}
          className="w-full py-2.5 rounded-lg text-xs font-bold border transition"
          style={{ borderColor: darkMode ? '#4b5563' : '#cbd5e1', color: darkMode ? '#e5e7eb' : '#374151' }}
        >
          <Save size={16} /> {t.descargarPaquete}
        </button>
      </div>
    </div>
  );
};
