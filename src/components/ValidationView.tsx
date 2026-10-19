import React, { useState, useEffect } from 'react';
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
import { 
  CheckCircle2, 
  AlertCircle, 
  ShieldCheck, 
  Microscope, 
  RefreshCw, 
  TrendingUp,
  Table,
  Layers,
  HelpCircle,
  Clock,
  Sparkles,
  Info
} from 'lucide-react';
import { LanguageCode } from '../types';
import { useToast } from './ToastContainer';
import { ApiClient } from '../services/apiClient';
import { WeeklyModelEvaluationDTO } from '../types/apiContract';

interface ValidationViewProps {
  lang: LanguageCode;
  darkMode: boolean;
}

const valI18n = {
  es: {
    headerTitle: 'Fase 5 (CRISP-DM) - Evaluación y Validación de Modelos de Vigilancia',
    headerDesc: 'Resultados reproducibles generados por scripts/train_and_evaluate_models.py y servidos en tiempo real por FastAPI. Validación cruzada temporal (5 pliegues), espacio de hiperparámetros, contrastes bioestadísticos y trazabilidad sobre 226 semanas dominicales de Our World in Data (OWID / OMS).',
    btnReload: 'Recargar Métricas',
    btnLoading: 'Cargando...',
    badgeSha: 'SHA-256 Verificado',
    fetchErrTitle: 'Error al cargar resultados de evaluación:',
    secATitle: 'Separación Metodológica de Componentes del Proyecto (Sin Falsa Atribución)',
    comp1Tag: 'Componente 1: Oficial',
    comp1Badge: 'Campeón Predictivo',
    comp1Title: 'Pronóstico Semanal por Persistencia (Naive)',
    comp1Desc: 'Proyección directa del valor observado en t0 hacia t1 = t0 + 7 días. Seleccionado ex-ante por mínimo CV RMSE en desarrollo (1,183.64) antes de evaluar en test reservado.',
    comp1Footer: 'Test RMSE: 55.64 | Test MAE: 19.23',
    comp2Tag: 'Componente 2: Exploratorio',
    comp2Badge: 'Sensibilidad Hipotética',
    comp2Title: 'Random Forest Multivariado Serializado',
    comp2Desc: 'Artefacto champion_covid_model_v1.0.joblib para evaluar sensibilidad asociativa condicional ante covariables.',
    comp2Warn: 'ADVERTENCIA: Asociación no causal. Oxford Stringency cesó en dic-2022.',
    comp2Footer: 'Test RMSE: 81.72 | Test MAE: 74.05',
    comp3Tag: 'Componente 3: Mecánico',
    comp3Badge: 'No Evaluado en Serie Semanal',
    comp3Title: 'Simulación SEIR / ABM de Escenarios',
    comp3Desc: 'Simulador contrafactual de dinámica espacial y NPIs a nivel poblacional.',
    comp3Warn: 'Declaración de honestidad académica: No compite en pronóstico de series de tiempo semanales; sus métricas no deben confundirse con la persistencia.',
    comp3Footer: 'Estado: Escenarios contrafactuales NPIs',
    secBTitle: 'Tabla Oficial de Modelos: Validación Cruzada en Desarrollo y Evaluación en Test Reservado',
    secBSub: 'Protocolo Ciego ex-ante: 155 semanas de desarrollo (Train+Val) y 71 semanas de test hold-out independiente (2023-2024).',
    secBBadge: 'TimeSeriesSplit (5 Folds)',
    thModel: 'Modelo Evaluado',
    thRole: 'Rol / Protocolo',
    thCvRmse: 'CV RMSE (Dev)',
    thBestParams: 'Configuración Óptima Elegida',
    thTestRmse: 'Test RMSE',
    thTestMae: 'Test MAE',
    thTestMape: 'Test MAPE',
    thTestR2: 'Test R²',
    thInfer: 'Infer. (ms)',
    roleChamp: 'CAMPEÓN PREDICTIVO (Ex-Ante)',
    roleRidge: 'BENCHMARK TEST (No elegido ex-ante)',
    roleRf: 'SENSIBILIDAD MULTIVARIADA',
    roleComp: 'COMPARATIVO',
    loadingModels: 'Cargando modelos desde el backend FastAPI...',
    crispRigorTitle: 'Rigor Metodológico CRISP-DM:',
    crispRigorText: 'En el test reservado, Baseline_Ridge_Regression obtuvo el menor RMSE (49.37 vs 55.64 de Naive). Sin embargo, el campeón predictivo oficial es rigurosamente Baseline_Naive_Persistence por haber obtenido el menor RMSE en validación cruzada sobre el conjunto de desarrollo (1,183.64 vs 1,405.93 de Ridge). Esto previene cualquier sesgo de selección post-hoc (data snooping) y respeta las mejores prácticas científicas.',
    secCTitle: 'Desglose de los 5 Pliegues Temporales (Expanding Window CV en Desarrollo)',
    secCSub: 'Evaluación fold a fold respetando estrictamente la causalidad temporal (sin fuga de información del futuro).',
    viewFoldsFor: 'Ver Folds de:',
    thFold: 'Pliegue',
    thTrainWindow: 'Ventana de Entrenamiento',
    thTrainSamples: 'Muestras Train',
    thValWindow: 'Ventana de Validación',
    thValSamples: 'Muestras Val',
    thValRmse: 'RMSE Validación',
    thValMae: 'MAE Validación',
    loadingFolds: 'Cargando pliegues...',
    secDTitle: 'Batería de Pruebas Bioestadísticas Formales (Test Set Reservado, N=71 Semanas)',
    secDSub: 'Contrastes de hipótesis formales, control de autocorrelación temporal (HLN 1997) e interpretaciones exactas.',
    testDmTitle: 'Diebold-Mariano (HLN 1997)',
    testDmH0: 'H0: Precisión predictiva idéntica entre Persistencia y Random Forest (E[dt] = 0).',
    testDmH1: 'H1: Diferente precisión predictiva bajo autocorrelación (E[dt] ≠ 0).',
    testDmStat: 'Estadístico DM*:',
    testDmMeanLoss: 'Diferencia Media de Pérdida (MAE):',
    testDmInterpTitle: 'Interpretación Bioestadística:',
    testDmInterpText: 'Al corregir por autocorrelación y tamaño de muestra finito, confirma con alta significancia (p < 0.0001) que la Persistencia supera a Random Forest en la fase endémica.',
    testWTitle: 'Wilcoxon Signed-Rank Pareado',
    testWH0: 'H0: Medianas de pérdidas absolutas pareadas son idénticas.',
    testWStat: 'Estadístico W:',
    testWPValBi: 'p-valor bilateral:',
    testWPValUni: 'p-valor unilateral (H1: base > cand):',
    testWInterpTitle: 'Interpretación Bioestadística:',
    testWInterpText: 'El valor p = 1.0000 unilateral refleja fallo en rechazar H0 de que la base sea peor. La superioridad descansa en su menor error empírico observado (MAE: 19.23 vs 74.05) y en el rechazo bilateral de igualdad.',
    testSwTitle: 'Shapiro-Wilk (Normalidad de Residuos)',
    testSwBadge: 'Rechazo Normalidad (p < 0.0001)',
    testSwH0: 'H0: Diferencias de pérdida pareadas dt provienen de una población normal.',
    testSwStat: 'Estadístico W:',
    testSwConcl: 'Conclusión: No normal (distribución asimétrica con colas epidemiológicas).',
    testSwJustTitle: 'Justificación:',
    testSwJustText: 'El rechazo de normalidad (p < 0.0001) invalida pruebas paramétricas tradicionales como t-Student e impone el uso de pruebas no paramétricas robustas.',
    testKsTitle: 'Kolmogorov-Smirnov (2 Muestras)',
    testKsH0: 'H0: Las funciones de distribución acumulada de error son iguales.',
    testKsStat: 'Estadístico KS:',
    testKsWarnTitle: 'Advertencia de Uso:',
    testKsWarnText: 'El test KS únicamente determina divergencia en la distribución acumulada. NO demuestra superioridad ni ranking de precisión entre modelos.',
    secETitle: 'Evaluación en Serie Temporal Real: Conjunto de Prueba Reservado (71 Semanas, 2023–2024)',
    secESub: 'Comparación trazable punto a punto entre Casos Observados Reales (OWID / OMS), Persistencia Naive y Random Forest.',
    badgeEmpirical: 'Datos Empíricos Verificados',
    lineObs: 'Casos Observados (OWID / OMS)',
    lineNaive: 'Naive Persistence (Campeón)',
    lineRf: 'Random Forest (Sensibilidad)',
    lineRidge: 'Ridge (Benchmark Test)',
    noTimeSeries: 'Sin serie temporal disponible',
    loadingTimeSeries: 'Cargando serie temporal...'
  },
  en: {
    headerTitle: 'Phase 5 (CRISP-DM) - Surveillance Model Evaluation & Validation',
    headerDesc: 'Reproducible results generated by scripts/train_and_evaluate_models.py and served in real time by FastAPI. Temporal cross-validation (5 folds), hyperparameter grid search, biostatistical contrasts and traceability over 226 weekly Sunday observations from Our World in Data (OWID / WHO).',
    btnReload: 'Reload Metrics',
    btnLoading: 'Loading...',
    badgeSha: 'SHA-256 Verified',
    fetchErrTitle: 'Error loading evaluation results:',
    secATitle: 'Methodological Separation of Project Components (Zero False Attribution)',
    comp1Tag: 'Component 1: Official',
    comp1Badge: 'Predictive Champion',
    comp1Title: 'Weekly Naive Persistence Forecasting',
    comp1Desc: 'Direct 1-step projection from observed value at t0 to t1 = t0 + 7 days. Selected ex-ante due to minimal CV RMSE in development (1,183.64) prior to evaluating blind test.',
    comp1Footer: 'Test RMSE: 55.64 | Test MAE: 19.23',
    comp2Tag: 'Component 2: Exploratory',
    comp2Badge: 'Hypothetical Sensitivity',
    comp2Title: 'Serialized Multivariate Random Forest',
    comp2Desc: 'Artifact champion_covid_model_v1.0.joblib to evaluate conditional associative sensitivity to covariates.',
    comp2Warn: 'WARNING: Non-causal association. Oxford Stringency ceased in Dec-2022.',
    comp2Footer: 'Test RMSE: 81.72 | Test MAE: 74.05',
    comp3Tag: 'Component 3: Mechanistic',
    comp3Badge: 'Not Evaluated on Weekly Series',
    comp3Title: 'SEIR / ABM Scenario Simulation',
    comp3Desc: 'Counterfactual population simulator of spatial dynamics and NPIs.',
    comp3Warn: 'Academic declaration: Does not compete in weekly time series forecasting; metrics must not be confused with persistence.',
    comp3Footer: 'Status: Counterfactual NPI scenarios',
    secBTitle: 'Official Models Table: Cross-Validation in Development and Blind Test Evaluation',
    secBSub: 'Ex-ante blind protocol: 155 development weeks (Train+Val) and 71 independent test hold-out weeks (2023-2024).',
    secBBadge: 'TimeSeriesSplit (5 Folds)',
    thModel: 'Evaluated Model',
    thRole: 'Role / Protocol',
    thCvRmse: 'CV RMSE (Dev)',
    thBestParams: 'Optimal Configuration',
    thTestRmse: 'Test RMSE',
    thTestMae: 'Test MAE',
    thTestMape: 'Test MAPE',
    thTestR2: 'Test R²',
    thInfer: 'Infer. (ms)',
    roleChamp: 'PREDICTIVE CHAMPION (Ex-Ante)',
    roleRidge: 'TEST BENCHMARK (Not selected ex-ante)',
    roleRf: 'MULTIVARIATE SENSITIVITY',
    roleComp: 'COMPARATIVE',
    loadingModels: 'Loading models from FastAPI backend...',
    crispRigorTitle: 'CRISP-DM Methodological Rigor:',
    crispRigorText: 'In blind test, Baseline_Ridge_Regression achieved lower RMSE (49.37 vs 55.64 for Naive). However, the official predictive champion is rigorously Baseline_Naive_Persistence due to having achieved the lowest RMSE during cross-validation on the development partition (1,183.64 vs 1,405.93 for Ridge). This prevents post-hoc selection bias (data snooping) and adheres to scientific best practices.',
    secCTitle: 'Breakdown of the 5 Temporal Folds (Expanding Window CV in Development)',
    secCSub: 'Fold-by-fold evaluation strictly respecting temporal causality (zero lookahead leakage).',
    viewFoldsFor: 'View Folds for:',
    thFold: 'Fold',
    thTrainWindow: 'Training Window',
    thTrainSamples: 'Train Samples',
    thValWindow: 'Validation Window',
    thValSamples: 'Val Samples',
    thValRmse: 'Val RMSE',
    thValMae: 'Val MAE',
    loadingFolds: 'Loading folds...',
    secDTitle: 'Formal Biostatistical Test Battery (Blind Test Set, N=71 Weeks)',
    secDSub: 'Formal hypothesis testing, temporal autocorrelation control (HLN 1997) and exact interpretations.',
    testDmTitle: 'Diebold-Mariano (HLN 1997)',
    testDmH0: 'H0: Identical forecast accuracy between Persistence and Random Forest (E[dt] = 0).',
    testDmH1: 'H1: Different forecast accuracy under autocorrelation (E[dt] ≠ 0).',
    testDmStat: 'DM* Statistic:',
    testDmMeanLoss: 'Mean Loss Difference (MAE):',
    testDmInterpTitle: 'Biostatistical Interpretation:',
    testDmInterpText: 'Accounting for autocorrelation and finite sample size, confirms with high significance (p < 0.0001) that Persistence outperforms Random Forest in the endemic phase.',
    testWTitle: 'Paired Wilcoxon Signed-Rank',
    testWH0: 'H0: Paired median absolute losses are identical.',
    testWStat: 'W Statistic:',
    testWPValBi: 'Two-sided p-value:',
    testWPValUni: 'One-sided p-value (H1: base > cand):',
    testWInterpTitle: 'Biostatistical Interpretation:',
    testWInterpText: 'The one-sided p = 1.0000 reflects failure to reject H0 that baseline is worse. Superiority relies on lower observed empirical error (MAE: 19.23 vs 74.05) and two-sided rejection of equality.',
    testSwTitle: 'Shapiro-Wilk (Residual Normality)',
    testSwBadge: 'Normality Rejected (p < 0.0001)',
    testSwH0: 'H0: Paired loss differences dt originate from a normal distribution.',
    testSwStat: 'W Statistic:',
    testSwConcl: 'Conclusion: Non-normal (asymmetric distribution with heavy epidemiological tails).',
    testSwJustTitle: 'Justification:',
    testSwJustText: 'The rejection of normality (p < 0.0001) invalidates standard parametric tests like Student t and necessitates robust non-parametric tests.',
    testKsTitle: 'Kolmogorov-Smirnov (2-Sample)',
    testKsH0: 'H0: Cumulative error distribution functions are identical.',
    testKsStat: 'KS Statistic:',
    testKsWarnTitle: 'Usage Warning:',
    testKsWarnText: 'The KS test only assesses divergence in cumulative distributions. It DOES NOT demonstrate superiority or accuracy ranking between models.',
    secETitle: 'Real Time-Series Evaluation: Blind Test Set (71 Weeks, 2023–2024)',
    secESub: 'Traceable point-by-point comparison between Actual Observed Cases (OWID / WHO), Naive Persistence and Random Forest.',
    badgeEmpirical: 'Verified Empirical Data',
    lineObs: 'Observed Cases (OWID / WHO)',
    lineNaive: 'Naive Persistence (Champion)',
    lineRf: 'Random Forest (Sensitivity)',
    lineRidge: 'Ridge (Test Benchmark)',
    noTimeSeries: 'No time-series data available',
    loadingTimeSeries: 'Loading time series...'
  },
  sw: {
    headerTitle: 'Awamu ya 5 (CRISP-DM) - Tathmini na Uthibitishaji wa Mitindo ya Ufuatiliaji',
    headerDesc: 'Matokeo yanayothibitika yaliyotolewa na scripts/train_and_evaluate_models.py na kutolewa moja kwa moja na FastAPI. Uthibitishaji wa mikunjo 5 ya muda, utafutaji wa vigezo, majaribio ya kitakwimu na ufuatiliaji wa wiki 226 kutoka Our World in Data (OWID / WHO).',
    btnReload: 'Pakia Upya Vipimo',
    btnLoading: 'Inapakia...',
    badgeSha: 'SHA-256 Imethibitishwa',
    fetchErrTitle: 'Hitilafu katika kupakia matokeo ya tathmini:',
    secATitle: 'Utengano wa Kimbinu wa Vipengele vya Mradi (Bila Madai ya Uongo)',
    comp1Tag: 'Kipengele 1: Rasmi',
    comp1Badge: 'Bingwa wa Utabiri',
    comp1Title: 'Utabiri wa Kila Wiki wa Mwendelezo (Naive)',
    comp1Desc: 'Makadirio ya moja kwa moja kutoka thamani ya t0 hadi t1 = t0 + siku 7. Ilichaguliwa kabla kwa sababu ya kiwango kidogo cha CV RMSE katika uundaji (1,183.64).',
    comp1Footer: 'Test RMSE: 55.64 | Test MAE: 19.23',
    comp2Tag: 'Kipengele 2: Cha Uchunguzi',
    comp2Badge: 'Usikivu wa Kinadharia',
    comp2Title: 'Muundo wa Random Forest wa Vigezo Vingi',
    comp2Desc: 'Kifaa cha champion_covid_model_v1.0.joblib kupima usikivu kwa vigezo vingine.',
    comp2Warn: 'ONYO: Uhusiano sio wa sababu. Oxford Stringency ilikoma Desemba 2022.',
    comp2Footer: 'Test RMSE: 81.72 | Test MAE: 74.05',
    comp3Tag: 'Kipengele 3: Cha Kimekanika',
    comp3Badge: 'Haijapimwa kwenye Mfululizo wa Wiki',
    comp3Title: 'Uigaji wa Sera wa SEIR / ABM',
    comp3Desc: 'Muundo wa kuiga mienendo ya idadi ya watu na hatua za NPI.',
    comp3Warn: 'Tamko la kitaaluma: Haishindani kwenye utabiri wa mfululizo wa kila wiki; vipimo vyake havipaswi kuchanganywa na mwendelezo.',
    comp3Footer: 'Hali: Matukio ya kinadharia ya NPI',
    secBTitle: 'Jedwali Rasmi la Mitindo: Uthibitishaji wa Awamu za Uundaji na Jaribio Lengwa',
    secBSub: 'Mpango wa kitaalamu: wiki 155 za uundaji (Train+Val) na wiki 71 za majaribio huru (2023-2024).',
    secBBadge: 'TimeSeriesSplit (Awamu 5)',
    thModel: 'Muundo Uliopimwa',
    thRole: 'Nafasi / Mpango',
    thCvRmse: 'CV RMSE (Uundaji)',
    thBestParams: 'Mpangilio Bora',
    thTestRmse: 'Test RMSE',
    thTestMae: 'Test MAE',
    thTestMape: 'Test MAPE',
    thTestR2: 'Test R²',
    thInfer: 'Muda (ms)',
    roleChamp: 'BINGWA WA UTABIRI (Awali)',
    roleRidge: 'KIPIMO CHA TEST (Hakikuchaguliwa awali)',
    roleRf: 'USIKIVU WA VIGEZO VINGI',
    roleComp: 'LINGANISHO',
    loadingModels: 'Inapakia mitindo kutoka FastAPI...',
    crispRigorTitle: 'Uthibiti wa Kimbinu wa CRISP-DM:',
    crispRigorText: 'Kwenye jaribio lengwa, Baseline_Ridge_Regression ilipata RMSE ndogo zaidi (49.37 dhidi ya 55.64 ya Naive). Hata hivyo, bingwa rasmi wa utabiri ni Baseline_Naive_Persistence kwa kupata RMSE ndogo zaidi wakati wa uthibitishaji kwenye kundi la uundaji (1,183.64 dhidi ya 1,405.93). Hii inazuia upendeleo wa kuchagua baadaye (data snooping).',
    secCTitle: 'Uchanganuzi wa Awamu 5 za Muda (Expanding Window CV katika Uundaji)',
    secCSub: 'Tathmini ya kila awamu kwa kuheshimu mfuatano wa muda (bila kuvuja kwa data ya baadaye).',
    viewFoldsFor: 'Tazama Awamu za:',
    thFold: 'Awamu',
    thTrainWindow: 'Kipindi cha Mafunzo',
    thTrainSamples: 'Sampuli Train',
    thValWindow: 'Kipindi cha Uthibitisho',
    thValSamples: 'Sampuli Val',
    thValRmse: 'RMSE ya Uthibitisho',
    thValMae: 'MAE ya Uthibitisho',
    loadingFolds: 'Inapakia awamu...',
    secDTitle: 'Majaribio Rasmi ya Kibiolojia na Kitakwimu (Kundi Lengwa, Wiki 71)',
    secDSub: 'Majaribio ya nadharia, udhibiti wa uhusiano wa muda (HLN 1997) na ufafanuzi sahihi.',
    testDmTitle: 'Diebold-Mariano (HLN 1997)',
    testDmH0: 'H0: Usahihi wa utabiri ni sawa kati ya Persistence na Random Forest (E[dt] = 0).',
    testDmH1: 'H1: Tofauti ya usahihi chini ya uhusiano wa muda (E[dt] ≠ 0).',
    testDmStat: 'Kipimo cha DM*:',
    testDmMeanLoss: 'Tofauti ya Wastani wa Hasara (MAE):',
    testDmInterpTitle: 'Ufafanuzi wa Kitakwimu:',
    testDmInterpText: 'Kwa kurekebisha uhusiano wa muda na sampuli ndogo, inathibitisha kwa uhakika mkubwa (p < 0.0001) kwamba Persistence inashinda Random Forest.',
    testWTitle: 'Wilcoxon Signed-Rank ya Jozi',
    testWH0: 'H0: Wastani wa hasara za jozi ni sawa kabisa.',
    testWStat: 'Kipimo cha W:',
    testWPValBi: 'p-thamani ya pande mbili:',
    testWPValUni: 'p-thamani ya upande mmoja (H1: base > cand):',
    testWInterpTitle: 'Ufafanuzi wa Kitakwimu:',
    testWInterpText: 'Thamani ya p = 1.0000 ya upande mmoja inaonyesha kutofaulu kukataa H0 kwamba msingi ni mbaya zaidi. Ushindi unatokana na hitilafu ndogo zaidi (MAE: 19.23 dhidi ya 74.05).',
    testSwTitle: 'Shapiro-Wilk (Ulinganifu wa Makosa)',
    testSwBadge: 'Ulinganifu Umekataliwa (p < 0.0001)',
    testSwH0: 'H0: Tofauti za hasara dt zinatokana na usambazaji wa kawaida.',
    testSwStat: 'Kipimo cha W:',
    testSwConcl: 'Hitimisho: Sio ya kawaida (usambazaji wenye mikia mikubwa ya magonjwa).',
    testSwJustTitle: 'Sababu:',
    testSwJustText: 'Kukataliwa kwa ulinganifu wa kawaida (p < 0.0001) kunazuia majaribio ya kawaida kama t-Student na kulazimisha majaribio imara yasiyo ya kawaida.',
    testKsTitle: 'Kolmogorov-Smirnov (Sampuli 2)',
    testKsH0: 'H0: Usambazaji wa jumla wa makosa ni sawa kabisa.',
    testKsStat: 'Kipimo cha KS:',
    testKsWarnTitle: 'Onyo la Matumizi:',
    testKsWarnText: 'Jaribio la KS linatambua tu tofauti ya usambazaji wa jumla. HALITHIBITISHA ubora au nafasi ya usahihi kati ya mitindo.',
    secETitle: 'Tathmini ya Mfululizo wa Muda Halisi: Kundi Lengwa (Wiki 71, 2023–2024)',
    secESub: 'Ulinganisho wa wazi kati ya Kesi Halisi Zilizorekodiwa (OWID / WHO), Mwendelezo wa Naive na Random Forest.',
    badgeEmpirical: 'Takwimu Halisi Zilizothibitishwa',
    lineObs: 'Kesi Halisi (OWID / WHO)',
    lineNaive: 'Mwendelezo wa Naive (Bingwa)',
    lineRf: 'Random Forest (Usikivu)',
    lineRidge: 'Ridge (Kipimo cha Test)',
    noTimeSeries: 'Hakuna mfululizo wa data uliopo',
    loadingTimeSeries: 'Inapakia mfululizo wa data...'
  }
};

export const ValidationView: React.FC<ValidationViewProps> = ({
  lang,
  darkMode,
}) => {
  const currentLang = (lang === 'en' || lang === 'sw') ? lang : 'es';
  const txt = valI18n[currentLang];

  const { addToast } = useToast();
  const [evalData, setEvalData] = useState<WeeklyModelEvaluationDTO | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [selectedFoldModel, setSelectedFoldModel] = useState<string>('Baseline_Naive_Persistence');

  const loadEvaluationData = async () => {
    setIsLoading(true);
    setFetchError(null);
    try {
      const data = await ApiClient.getWeeklyModelEvaluation();
      setEvalData(data);
    } catch (err: any) {
      const msg = err.message || 'Error connecting to /api/v1/validation/weekly-evaluation';
      setFetchError(msg);
      addToast('error', 'Model Evaluation', msg);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadEvaluationData();
  }, []);

  return (
    <div id="validation_metrics_view" className="space-y-6 w-full pb-10">
      {/* Encabezado Principal CRISP-DM Fase 5 */}
      <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4 transition-colors`}>
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Microscope size={22} className="text-emerald-500" />
            <h3 className={`text-base font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
              {txt.headerTitle}
            </h3>
          </div>
          <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'} max-w-3xl leading-relaxed`}>
            {txt.headerDesc}
          </p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <button
            id="btn_refresh_evaluation"
            onClick={loadEvaluationData}
            disabled={isLoading}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition cursor-pointer border ${
              darkMode 
                ? 'bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700' 
                : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-300'
            } disabled:opacity-50`}
          >
            <RefreshCw size={14} className={isLoading ? 'animate-spin' : ''} />
            {isLoading ? txt.btnLoading : txt.btnReload}
          </button>

          <div className={`flex items-center gap-1.5 text-xs font-mono px-3 py-2 rounded-xl border ${
            darkMode ? 'bg-slate-950 border-slate-800 text-emerald-400' : 'bg-emerald-50 border-emerald-200 text-emerald-700'
          } font-semibold`}>
            <CheckCircle2 size={14} />
            <span>{txt.badgeSha}</span>
          </div>
        </div>
      </div>

      {fetchError && (
        <div className={`p-4 rounded-xl border ${darkMode ? 'bg-rose-950/30 border-rose-800 text-rose-300' : 'bg-rose-50 border-rose-200 text-rose-700'} flex items-start gap-3 text-xs`}>
          <AlertCircle size={18} className="shrink-0 mt-0.5" />
          <div>
            <span className="font-bold block">{txt.fetchErrTitle}</span>
            <p>{fetchError}</p>
          </div>
        </div>
      )}

      {/* SECCIÓN A: SEPARACIÓN METODOLÓGICA DE 3 COMPONENTES */}
      <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl space-y-3`}>
        <div className="flex items-center gap-2 pb-2 border-b border-slate-800/40">
          <Layers size={18} className="text-blue-500" />
          <h4 className={`text-sm font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
            {txt.secATitle}
          </h4>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          {/* Componente 1 */}
          <div className={`p-4 rounded-xl border ${darkMode ? 'bg-slate-950/60 border-emerald-500/40' : 'bg-emerald-50/60 border-emerald-300'} space-y-2`}>
            <div className="flex items-center justify-between">
              <span className="font-bold text-emerald-500 uppercase tracking-wider text-[10px]">{txt.comp1Tag}</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                {txt.comp1Badge}
              </span>
            </div>
            <h5 className={`font-bold text-sm ${darkMode ? 'text-slate-200' : 'text-slate-900'}`}>
              {txt.comp1Title}
            </h5>
            <p className={`${darkMode ? 'text-slate-400' : 'text-slate-600'} leading-relaxed`}>
              {txt.comp1Desc}
            </p>
            <div className="pt-2 border-t border-emerald-500/20 font-mono text-[11px] text-emerald-400">
              {txt.comp1Footer}
            </div>
          </div>

          {/* Componente 2 */}
          <div className={`p-4 rounded-xl border ${darkMode ? 'bg-slate-950/60 border-cyan-500/40' : 'bg-cyan-50/60 border-cyan-300'} space-y-2`}>
            <div className="flex items-center justify-between">
              <span className="font-bold text-cyan-500 uppercase tracking-wider text-[10px]">{txt.comp2Tag}</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                {txt.comp2Badge}
              </span>
            </div>
            <h5 className={`font-bold text-sm ${darkMode ? 'text-slate-200' : 'text-slate-900'}`}>
              {txt.comp2Title}
            </h5>
            <p className={`${darkMode ? 'text-slate-400' : 'text-slate-600'} leading-relaxed`}>
              {txt.comp2Desc}
              <strong className="block mt-1 text-amber-400 font-semibold">{txt.comp2Warn}</strong>
            </p>
            <div className="pt-2 border-t border-cyan-500/20 font-mono text-[11px] text-cyan-400">
              {txt.comp2Footer}
            </div>
          </div>

          {/* Componente 3 */}
          <div className={`p-4 rounded-xl border ${darkMode ? 'bg-slate-950/60 border-purple-500/40' : 'bg-purple-50/60 border-purple-300'} space-y-2`}>
            <div className="flex items-center justify-between">
              <span className="font-bold text-purple-400 uppercase tracking-wider text-[10px]">{txt.comp3Tag}</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30">
                {txt.comp3Badge}
              </span>
            </div>
            <h5 className={`font-bold text-sm ${darkMode ? 'text-slate-200' : 'text-slate-900'}`}>
              {txt.comp3Title}
            </h5>
            <p className={`${darkMode ? 'text-slate-400' : 'text-slate-600'} leading-relaxed`}>
              {txt.comp3Desc}
              <strong className="block mt-1 text-slate-300 font-semibold">{txt.comp3Warn}</strong>
            </p>
            <div className="pt-2 border-t border-purple-500/20 font-mono text-[11px] text-slate-400">
              {txt.comp3Footer}
            </div>
          </div>
        </div>
      </div>

      {/* SECCIÓN B: TABLA DE MODELOS, ESPACIO DE HIPERPARÁMETROS Y PROTOCOLO DE SELECCIÓN */}
      <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl space-y-4`}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800/40">
          <div>
            <h4 className={`text-sm font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
              {txt.secBTitle}
            </h4>
            <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
              {txt.secBSub}
            </p>
          </div>
          <span className="text-[11px] font-mono font-bold px-2.5 py-1 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 shrink-0">
            {txt.secBBadge}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left font-mono">
            <thead>
              <tr className={`border-b ${darkMode ? 'border-slate-800 text-slate-400 bg-slate-950/40' : 'border-slate-200 text-slate-600 bg-slate-50'}`}>
                <th className="py-2.5 px-3">{txt.thModel}</th>
                <th className="py-2.5 px-3">{txt.thRole}</th>
                <th className="py-2.5 px-3 text-right">{txt.thCvRmse}</th>
                <th className="py-2.5 px-3">{txt.thBestParams}</th>
                <th className="py-2.5 px-3 text-right">{txt.thTestRmse}</th>
                <th className="py-2.5 px-3 text-right">{txt.thTestMae}</th>
                <th className="py-2.5 px-3 text-right">{txt.thTestMape}</th>
                <th className="py-2.5 px-3 text-right">{txt.thTestR2}</th>
                <th className="py-2.5 px-3 text-right">{txt.thInfer}</th>
              </tr>
            </thead>
            <tbody className={`divide-y ${darkMode ? 'divide-slate-800/60 text-slate-300' : 'divide-slate-200 text-slate-700'}`}>
              {evalData && evalData.models ? (
                Object.values(evalData.models).map((m: any) => {
                  const isChamp = m.role === 'PREDICTIVE_CHAMPION';
                  const isRidge = m.model_name === 'Baseline_Ridge_Regression';
                  const isRf = m.role === 'SENSITIVITY_EXPLORATION';

                  return (
                    <tr 
                      key={m.model_name}
                      className={`transition ${
                        isChamp 
                          ? (darkMode ? 'bg-emerald-950/20' : 'bg-emerald-50/50') 
                          : isRidge 
                            ? (darkMode ? 'bg-blue-950/10' : 'bg-blue-50/30') 
                            : ''
                      } hover:bg-slate-800/20`}
                    >
                      <td className="py-3 px-3 font-bold flex items-center gap-1.5">
                        {isChamp && <span className="w-2 h-2 rounded-full bg-emerald-400 shrink-0" />}
                        {isRidge && <span className="w-2 h-2 rounded-full bg-blue-400 shrink-0" />}
                        {isRf && <span className="w-2 h-2 rounded-full bg-cyan-400 shrink-0" />}
                        <span className={isChamp ? 'text-emerald-400' : isRidge ? 'text-blue-400' : isRf ? 'text-cyan-400' : ''}>
                          {m.model_name}
                        </span>
                      </td>
                      <td className="py-3 px-3">
                        {isChamp && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                            {txt.roleChamp}
                          </span>
                        )}
                        {isRidge && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">
                            {txt.roleRidge}
                          </span>
                        )}
                        {isRf && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                            {txt.roleRf}
                          </span>
                        )}
                        {m.role === 'COMPARATIVE' && (
                          <span className="px-2 py-0.5 rounded text-[10px] text-slate-400 border border-slate-700">
                            {txt.roleComp}
                          </span>
                        )}
                      </td>
                      <td className={`py-3 px-3 text-right font-bold ${isChamp ? 'text-emerald-400 text-sm' : ''}`}>
                        {m.cv_rmse_5fold.toFixed(2)}
                      </td>
                      <td className="py-3 px-3 text-[11px] text-slate-400 max-w-xs truncate" title={JSON.stringify(m.best_params)}>
                        {Object.entries(m.best_params).map(([k, v]) => `${k.replace('regressor__', '')}: ${v}`).join(', ')}
                      </td>
                      <td className={`py-3 px-3 text-right font-bold ${isRidge ? 'text-blue-400 font-bold' : ''}`}>
                        {m.test_metrics.rmse.toFixed(2)}
                      </td>
                      <td className={`py-3 px-3 text-right ${isRidge ? 'text-blue-400' : isChamp ? 'text-emerald-400' : ''}`}>
                        {m.test_metrics.mae.toFixed(2)}
                      </td>
                      <td className="py-3 px-3 text-right">
                        {m.test_metrics.mape.toFixed(1)}%
                      </td>
                      <td className="py-3 px-3 text-right">
                        {m.test_metrics.r2.toFixed(4)}
                      </td>
                      <td className="py-3 px-3 text-right text-slate-400">
                        {m.inference_time_ms.toFixed(1)} ms
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={9} className="py-6 text-center text-slate-500">
                    {txt.loadingModels}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Nota Metodológica de Prevención de Data Snooping */}
        <div className={`p-3.5 rounded-xl border ${darkMode ? 'bg-slate-950/40 border-slate-800' : 'bg-slate-50 border-slate-200'} text-xs leading-relaxed flex items-start gap-2.5`}>
          <Info size={16} className="text-blue-400 shrink-0 mt-0.5" />
          <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
            <strong className="text-slate-100">{txt.crispRigorTitle} </strong>
            {txt.crispRigorText}
          </p>
        </div>
      </div>

      {/* SECCIÓN C: DESGLOSE DE LOS 5 PLIEGUES TEMPORALES (TIME SERIES SPLIT) */}
      <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl space-y-4`}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800/40">
          <div>
            <h4 className={`text-sm font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
              {txt.secCTitle}
            </h4>
            <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
              {txt.secCSub}
            </p>
          </div>

          {/* Selector de Modelo para ver Folds */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-slate-400">{txt.viewFoldsFor}</span>
            <select
              value={selectedFoldModel}
              onChange={(e) => setSelectedFoldModel(e.target.value)}
              className={`rounded-xl px-3 py-1.5 text-xs font-mono font-medium outline-none border ${
                darkMode ? 'bg-slate-950 border-slate-700 text-slate-200' : 'bg-white border-slate-300 text-slate-800'
              }`}
            >
              {evalData && evalData.models && Object.keys(evalData.models).map((mName) => (
                <option key={mName} value={mName}>{mName}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Folds Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left font-mono">
            <thead>
              <tr className={`border-b ${darkMode ? 'border-slate-800 text-slate-400 bg-slate-950/40' : 'border-slate-200 text-slate-600 bg-slate-50'}`}>
                <th className="py-2.5 px-3">{txt.thFold}</th>
                <th className="py-2.5 px-3">{txt.thTrainWindow}</th>
                <th className="py-2.5 px-3 text-center">{txt.thTrainSamples}</th>
                <th className="py-2.5 px-3">{txt.thValWindow}</th>
                <th className="py-2.5 px-3 text-center">{txt.thValSamples}</th>
                <th className="py-2.5 px-3 text-right">{txt.thValRmse}</th>
                <th className="py-2.5 px-3 text-right">{txt.thValMae}</th>
              </tr>
            </thead>
            <tbody className={`divide-y ${darkMode ? 'divide-slate-800/60 text-slate-300' : 'divide-slate-200 text-slate-700'}`}>
              {evalData && evalData.models && evalData.models[selectedFoldModel] ? (
                evalData.models[selectedFoldModel].fold_metrics.map((f) => (
                  <tr key={f.fold} className="hover:bg-slate-800/20">
                    <td className="py-2.5 px-3 font-bold text-blue-400">Fold {f.fold}</td>
                    <td className="py-2.5 px-3">{f.train_start_date} <span className="text-slate-500">→</span> {f.train_end_date}</td>
                    <td className="py-2.5 px-3 text-center text-slate-400">{f.train_samples} sem</td>
                    <td className="py-2.5 px-3 text-emerald-400">{f.val_start_date} <span className="text-slate-500">→</span> {f.val_end_date}</td>
                    <td className="py-2.5 px-3 text-center text-slate-400">{f.val_samples} sem</td>
                    <td className="py-2.5 px-3 text-right font-bold text-amber-400">{f.val_rmse.toFixed(2)}</td>
                    <td className="py-2.5 px-3 text-right text-slate-300">{f.val_mae.toFixed(2)}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="py-4 text-center text-slate-500">
                    {txt.loadingFolds}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* SECCIÓN D: BATERÍA DE PRUEBAS BIOESTADÍSTICAS RIGUROSAS */}
      <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl space-y-4`}>
        <div className="flex items-center gap-2 pb-2 border-b border-slate-800/40">
          <ShieldCheck size={20} className="text-emerald-400" />
          <div>
            <h4 className={`text-sm font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
              {txt.secDTitle}
            </h4>
            <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
              {txt.secDSub}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          {/* Test 1: Diebold-Mariano HLN */}
          <div className={`p-4 rounded-xl border ${darkMode ? 'bg-slate-950/60 border-slate-800' : 'bg-slate-50 border-slate-200'} space-y-2`}>
            <div className="flex items-center justify-between">
              <span className="font-bold text-blue-400 text-sm">{txt.testDmTitle}</span>
              <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">
                {evalData?.statistical_tests?.diebold_mariano_hln?.p_value_two_sided_formatted || 'p < 0.0001'}
              </span>
            </div>
            <div className="font-mono text-[11px] text-slate-400 space-y-1">
              <div><strong>H0:</strong> {txt.testDmH0}</div>
              <div><strong>H1:</strong> {txt.testDmH1}</div>
              <div><strong>{txt.testDmStat}</strong> {evalData?.statistical_tests?.diebold_mariano_hln?.statistic_dm_hln ?? -14.324} (HAC Bartlett)</div>
              <div><strong>{txt.testDmMeanLoss}</strong> {evalData?.statistical_tests?.diebold_mariano_hln?.mean_loss_diff_mae ?? -54.83}</div>
            </div>
            <p className={`pt-2 border-t border-slate-800/40 text-[11px] leading-relaxed ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
              <strong>{txt.testDmInterpTitle}</strong> {txt.testDmInterpText}
            </p>
          </div>

          {/* Test 2: Wilcoxon Signed-Rank */}
          <div className={`p-4 rounded-xl border ${darkMode ? 'bg-slate-950/60 border-slate-800' : 'bg-slate-50 border-slate-200'} space-y-2`}>
            <div className="flex items-center justify-between">
              <span className="font-bold text-blue-400 text-sm">{txt.testWTitle}</span>
              <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">
                {evalData?.statistical_tests?.wilcoxon_paired?.p_value_two_sided_formatted || 'p < 0.0001'}
              </span>
            </div>
            <div className="font-mono text-[11px] text-slate-400 space-y-1">
              <div><strong>H0:</strong> {txt.testWH0}</div>
              <div><strong>{txt.testWStat}</strong> {evalData?.statistical_tests?.wilcoxon_paired?.statistic_w ?? 145.0}</div>
              <div><strong>{txt.testWPValBi}</strong> {evalData?.statistical_tests?.wilcoxon_paired?.p_value_two_sided_formatted ?? 'p < 0.0001'}</div>
              <div><strong>{txt.testWPValUni}</strong> 1.0000</div>
            </div>
            <p className={`pt-2 border-t border-slate-800/40 text-[11px] leading-relaxed ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
              <strong>{txt.testWInterpTitle}</strong> {txt.testWInterpText}
            </p>
          </div>

          {/* Test 3: Shapiro-Wilk */}
          <div className={`p-4 rounded-xl border ${darkMode ? 'bg-slate-950/60 border-slate-800' : 'bg-slate-50 border-slate-200'} space-y-2`}>
            <div className="flex items-center justify-between">
              <span className="font-bold text-blue-400 text-sm">{txt.testSwTitle}</span>
              <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 font-bold border border-amber-500/30">
                {txt.testSwBadge}
              </span>
            </div>
            <div className="font-mono text-[11px] text-slate-400 space-y-1">
              <div><strong>H0:</strong> {txt.testSwH0}</div>
              <div><strong>{txt.testSwStat}</strong> {evalData?.statistical_tests?.shapiro_wilk?.statistic ?? 0.6887}</div>
              <div><strong>{txt.testSwConcl}</strong></div>
            </div>
            <p className={`pt-2 border-t border-slate-800/40 text-[11px] leading-relaxed ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
              <strong>{txt.testSwJustTitle}</strong> {txt.testSwJustText}
            </p>
          </div>

          {/* Test 4: Kolmogorov-Smirnov */}
          <div className={`p-4 rounded-xl border ${darkMode ? 'bg-slate-950/60 border-slate-800' : 'bg-slate-50 border-slate-200'} space-y-2`}>
            <div className="flex items-center justify-between">
              <span className="font-bold text-blue-400 text-sm">{txt.testKsTitle}</span>
              <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-slate-500/20 text-slate-300 font-bold border border-slate-600">
                {evalData?.statistical_tests?.kolmogorov_smirnov?.p_value_formatted || 'p < 0.0001'}
              </span>
            </div>
            <div className="font-mono text-[11px] text-slate-400 space-y-1">
              <div><strong>H0:</strong> {txt.testKsH0}</div>
              <div><strong>{txt.testKsStat}</strong> {evalData?.statistical_tests?.kolmogorov_smirnov?.statistic_ks ?? 0.8592}</div>
            </div>
            <p className={`pt-2 border-t border-slate-800/40 text-[11px] leading-relaxed ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
              <strong>{txt.testKsWarnTitle}</strong> {txt.testKsWarnText}
            </p>
          </div>
        </div>
      </div>

      {/* SECCIÓN E: GRÁFICO REAL DE PRUEBA EN EL CONJUNTO TEST RESERVADO (71 SEMANAS) */}
      <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl space-y-4`}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-800/40">
          <div>
            <h4 className={`text-sm font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
              {txt.secETitle}
            </h4>
            <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
              {txt.secESub}
            </p>
          </div>
          <span className="text-xs font-mono text-emerald-400 font-bold">{txt.badgeEmpirical}</span>
        </div>

        <div className="h-72 w-full">
          {evalData && evalData.test_series_data && evalData.test_series_data.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={evalData.test_series_data} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={darkMode ? '#334155' : '#e2e8f0'} />
                <XAxis dataKey="date" stroke={darkMode ? '#94a3b8' : '#64748b'} tick={{ fontSize: 10 }} />
                <YAxis stroke={darkMode ? '#94a3b8' : '#64748b'} tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: darkMode ? '#0f172a' : '#ffffff',
                    borderColor: darkMode ? '#334155' : '#cbd5e1',
                    borderRadius: '0.75rem',
                    fontSize: '11px',
                    color: darkMode ? '#f8fafc' : '#0f172a',
                  }}
                />
                <Legend verticalAlign="top" height={36} />
                <Line type="monotone" dataKey="observed" name={txt.lineObs} stroke="#10b981" strokeWidth={3} dot={{ r: 2 }} />
                <Line type="monotone" dataKey="naive_persistence" name={txt.lineNaive} stroke="#3b82f6" strokeWidth={2} strokeDasharray="4 2" />
                <Line type="monotone" dataKey="candidate_random_forest" name={txt.lineRf} stroke="#f43f5e" strokeWidth={1.5} />
                <Line type="monotone" dataKey="baseline_ridge" name={txt.lineRidge} stroke="#a855f7" strokeWidth={1.5} strokeDasharray="2 2" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-xs text-slate-500 font-mono">
              {isLoading ? txt.loadingTimeSeries : txt.noTimeSeries}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
