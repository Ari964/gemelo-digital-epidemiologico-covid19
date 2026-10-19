import React, { useState } from 'react';
import { 
  Compass, 
  ExternalLink, 
  FileCheck2, 
  Database, 
  Layers, 
  GitBranch, 
  Sliders, 
  Award, 
  FileCode2, 
  Server, 
  Monitor, 
  Bot, 
  Workflow, 
  MapPin, 
  ArrowRight, 
  Copy, 
  Check, 
  ShieldCheck, 
  Info,
  ChevronRight,
  Terminal
} from 'lucide-react';
import { LanguageCode } from '../i18n/translations';

interface EvidenceRouteViewProps {
  darkMode: boolean;
  lang: LanguageCode;
  onNavigateToTab?: (tab: string) => void;
}

type BadgeCategory = 'OBSERVED' | 'FORECAST' | 'SIMULATION' | 'REFERENTIAL' | 'PROTOCOL';

interface EvidenceStep {
  id: string;
  stepNumber: number;
  title: Record<LanguageCode, string>;
  category: BadgeCategory;
  categoryLabel: Record<LanguageCode, string>;
  targetModuleTab?: string;
  moduleLabel?: string;
  summary: Record<LanguageCode, string>;
  artifactPath?: string;
  hashOrSignature?: string;
  terminalCommand?: string;
  apiEndpoint?: string;
  publicUrl?: string;
  scientificNotes: Record<LanguageCode, string>;
}

export const EvidenceRouteView: React.FC<EvidenceRouteViewProps> = ({ darkMode, lang, onNavigateToTab }) => {
  const [selectedStepIndex, setSelectedStepIndex] = useState<number>(0);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const steps: EvidenceStep[] = [
    {
      id: 'public_source',
      stepNumber: 1,
      title: {
        es: '1. Repositorio Público Global Our World in Data (OWID)',
        en: '1. Public Global Repository Our World in Data (OWID)',
        sw: '1. Hifadhidata ya Umma ya Ulimwengu Our World in Data (OWID)'
      },
      category: 'OBSERVED',
      categoryLabel: {
        es: 'DATO OBSERVADO PÚBLICO',
        en: 'PUBLIC OBSERVED DATA',
        sw: 'TAKWIMU ZA UMMA ZILIZOANGALIWA'
      },
      publicUrl: 'https://catalog.ourworldindata.org/garden/covid/latest/compact/compact.csv',
      summary: {
        es: 'Extracción sin alterar de las 1,674 filas de Kenia (código ISO "KEN") a partir del consolidado global de vigilancia COVID-19 de Our World in Data (OWID / OMS), cubriendo de 2020-01-05 a 2024-08-04.',
        en: 'Unmodified extraction of Kenya\'s 1,674 rows (ISO code "KEN") from Our World in Data\'s global consolidated COVID-19 surveillance repository (2020-01-05 to 2024-08-04).',
        sw: 'Uchimbaji bila mabadiliko wa safu 1,674 za Kenya (msimbo wa ISO "KEN") kutoka kwenye hifadhidata ya ulimwengu ya Our World in Data (2020-01-05 hadi 2024-08-04).'
      },
      scientificNotes: {
        es: 'Los datos de casos de OWID son de alcance estrictamente NACIONAL (código de país KEN). No contienen desglose por condados ni variables de admisión hospitalaria por condado.',
        en: 'OWID case data is strictly at the NATIONAL level (country code KEN). It does not contain county-level disaggregation or county hospital admissions.',
        sw: 'Takwimu za visa za OWID ni za kitaifa tu (msimbo wa nchi KEN). Hazina mgawanyo wa kaunti au viwango vya kulazwa hospitalini kwa kaunti.'
      }
    },
    {
      id: 'raw_csv_hash',
      stepNumber: 2,
      title: {
        es: '2. Dataset Crudo Local y Comprobación Criptográfica SHA-256',
        en: '2. Local Raw Dataset and Cryptographic SHA-256 Verification',
        sw: '2. Hifadhidata Ghafi ya Ndani na Uthibitishaji wa SHA-256'
      },
      category: 'OBSERVED',
      categoryLabel: {
        es: 'DATO OBSERVADO AUDITABLE',
        en: 'AUDITABLE OBSERVED DATA',
        sw: 'TAKWIMU ZA UKAGUZI ZILIZOANGALIWA'
      },
      artifactPath: 'data/raw/owid_covid_kenya_raw.csv',
      hashOrSignature: 'c82f3cfc5899b25557f3bf69de987dc9628bfa6fbbee55cd77b649c9d34cd2ba',
      terminalCommand: 'python scripts/check_owid_source.py',
      summary: {
        es: 'Archivo local preservado con 1,674 registros (1,675 líneas con encabezado) entre 2020-01-05 y 2024-08-04. Procedimiento de auditoría criptográfica ejecutado por scripts/check_owid_source.py sin alterar valores.',
        en: 'Preserved local file with 1,674 records (1,675 lines total) spanning 2020-01-05 to 2024-08-04. Cryptographic audit executed by scripts/check_owid_source.py without modifying values.',
        sw: 'Faili la ndani lililohifadhiwa lenye rekodi 1,674 (mistari 1,675 kwa jumla) kati ya 2020-01-05 na 2024-08-04. Ukaguzi unathibitishwa na scripts/check_owid_source.py bila kubadilisha thamani.'
      },
      scientificNotes: {
        es: 'Se audita que no se inventaron ni completaron registros faltantes. El hash garantiza que el archivo es inmutable durante toda la sustentación.',
        en: 'Audited to ensure zero fabricated or synthetically completed missing records. The cryptographic hash guarantees file immutability.',
        sw: 'Imekaguliwa kuhakikisha hakuna rekodi bandia zilizoundwa. Hashi inahakikisha faili halibadiliki wakati wa ukaguzi.'
      }
    },
    {
      id: 'eda_loading',
      stepNumber: 3,
      title: {
        es: '3. Carga y Análisis Exploratorio de Datos (EDA)',
        en: '3. Data Ingestion and Exploratory Data Analysis (EDA)',
        sw: '3. Upakiaji na Uchambuzi wa Awali wa Takwimu (EDA)'
      },
      category: 'OBSERVED',
      categoryLabel: {
        es: 'DATO OBSERVADO / EDA',
        en: 'OBSERVED DATA / EDA',
        sw: 'TAKWIMU ZILIZOANGALIWA / EDA'
      },
      artifactPath: 'notebooks/eda_auditoria_covid_kenya.ipynb',
      terminalCommand: 'python scripts/check_owid_source.py',
      summary: {
        es: 'Inspección de distribuciones empíricas, tasas de no reporte, estacionalidad dominical y detección de cambios de régimen en la serie temporal nacional.',
        en: 'Empirical distribution inspection, non-reporting rates, Sunday seasonality, and regime shift detection across the national time series.',
        sw: 'Ukaguzi wa usambazaji, viwango vya kutoripoti, na mabadiliko ya vipindi katika mfululizo wa muda wa kitaifa.'
      },
      scientificNotes: {
        es: 'Demuestra que tras 2022 el reporte se volvió semanal acumulado cada domingo, requiriendo agregación canónica de periodicidad dominical.',
        en: 'Demonstrates that after 2022 reporting switched to weekly Sunday reporting, requiring canonical Sunday aggregation (W-SUN).',
        sw: 'Inaonyesha kuwa baada ya 2022 ripoti zilihamia kwa kila Jumapili, ikihitaji muungano wa kila wiki (W-SUN).'
      }
    },
    {
      id: 'data_cleaning',
      stepNumber: 4,
      title: {
        es: '4. Limpieza, Agregación Semanal y Base SQLite',
        en: '4. Cleaning, Weekly Aggregation, and SQLite Database',
        sw: '4. Usafishaji, Ujumuishaji wa Kila Wiki na Hifadhidata ya SQLite'
      },
      category: 'OBSERVED',
      categoryLabel: {
        es: 'DATO OBSERVADO LIMPIO',
        en: 'CLEAN OBSERVED DATA',
        sw: 'TAKWIMU SAFI ZILIZOANGALIWA'
      },
      artifactPath: 'data/clean/kenya_covid_clean.db',
      terminalCommand: 'python scripts/build_clean_kenya_database.py',
      summary: {
        es: 'Generación de la base de datos limpia con 231 semanas epidemiológicas dominicales (W-SUN) sin fugas de información futura (no data leakage).',
        en: 'Generation of clean database with 231 epidemiological Sunday weeks (W-SUN) strictly preventing lookahead bias or data leakage.',
        sw: 'Uzalishaji wa hifadhidata safi yenye wiki 231 za magonjwa bila uvujaji wa takwimu za baadaye.'
      },
      scientificNotes: {
        es: 'Tabla kenya_weekly_cases con variables canónicas: observed_weekly_cases, lag1, lag2, media móvil 4 semanas, y stringency_index.',
        en: 'Table kenya_weekly_cases with canonical features: observed_weekly_cases, lag1, lag2, 4-week rolling mean, and stringency_index.',
        sw: 'Jedwali kenya_weekly_cases lenye vipengele rasmi: observed_weekly_cases, lag1, lag2, na stringency_index.'
      }
    },
    {
      id: 'temporal_partition',
      stepNumber: 5,
      title: {
        es: '5. Partición Temporal Estricta (Train/Dev vs Test Ciego)',
        en: '5. Strict Temporal Split (Train/Dev vs Blind Test)',
        sw: '5. Mgawanyiko wa Muda (Train/Dev dhidi ya Test)'
      },
      category: 'PROTOCOL',
      categoryLabel: {
        es: 'PROTOCOLO METODOLÓGICO',
        en: 'METHODOLOGICAL PROTOCOL',
        sw: 'UTARATIBU WA KISAYANSI'
      },
      summary: {
        es: 'Partición cronológica sin traslape: Entrenamiento y Desarrollo (2020-03-08 a 2023-03-26, 160 semanas) vs Evaluación Ciega (2023-04-02 a 2024-07-28, 71 semanas).',
        en: 'Chronological non-overlapping partition: Train/Dev (2020-03-08 to 2023-03-26, 160 weeks) vs Blind Test (2023-04-02 to 2024-07-28, 71 weeks).',
        sw: 'Mgawanyiko wa kufuata wakati: Mafunzo (2020-03-08 hadi 2023-03-26, wiki 160) dhidi ya Jaribio (2023-04-02 hadi 2024-07-28, wiki 71).'
      },
      scientificNotes: {
        es: 'Garantiza que el periodo endémico de baja incidencia se evalúe fuera de muestra, simulando las condiciones reales de vigilancia operacional.',
        en: 'Guarantees that the low-incidence endemic period is evaluated strictly out-of-sample, mirroring operational surveillance.',
        sw: 'Inahakikisha kipindi cha maambukizi ya chini kinapimwa nje ya sampuli ya mafunzo.'
      }
    },
    {
      id: 'temporal_cv',
      stepNumber: 6,
      title: {
        es: '6. Validación Cruzada Temporal (5 Pliegues TimeSeriesSplit)',
        en: '6. Temporal Cross-Validation (5 TimeSeriesSplit Folds)',
        sw: '6. Uthibitishaji wa Muda (Mikunjo 5 ya TimeSeriesSplit)'
      },
      category: 'PROTOCOL',
      categoryLabel: {
        es: 'VALIDACIÓN TEMPORAL CRUZADA',
        en: 'TEMPORAL CROSS-VALIDATION',
        sw: 'UTHIBITISHAJI WA MUDA'
      },
      targetModuleTab: 'evaluation_validation',
      moduleLabel: 'Fase 5: Validación',
      summary: {
        es: 'Ejecución de TimeSeriesSplit(n_splits=5) con ventanas de entrenamiento crecientes: Pliegue 1 (27 sem), Pliegue 2 (53 sem), Pliegue 3 (80 sem), Pliegue 4 (106 sem), Pliegue 5 (133 sem).',
        en: 'Execution of TimeSeriesSplit(n_splits=5) with expanding training windows: Fold 1 (27 wks), Fold 2 (53 wks), Fold 3 (80 wks), Fold 4 (106 wks), Fold 5 (133 wks).',
        sw: 'Utekelezaji wa TimeSeriesSplit(n_splits=5) na madirisha yanayopanuka: Mkunjo 1 (wiki 27), 2 (53), 3 (80), 4 (106), 5 (133).'
      },
      scientificNotes: {
        es: 'Cada pliegue registra de manera transparente sus métricas individuales en models/model_evaluation_weekly_results.json consultables en la pestaña de Validación.',
        en: 'Each fold transparently logs its individual metrics to models/model_evaluation_weekly_results.json viewable in the Validation tab.',
        sw: 'Kila mkunjo hurekodi vipimo vyake katika models/model_evaluation_weekly_results.json vinavyoweza kutazamwa kwenye kichupo cha Uthibitishaji.'
      }
    },
    {
      id: 'hyperparameter_tuning',
      stepNumber: 7,
      title: {
        es: '7. Espacio y Ajuste de Hiperparámetros de Modelos',
        en: '7. Hyperparameter Space and Model Optimization',
        sw: '7. Urekebishaji wa Vigezo vya Mitindo'
      },
      category: 'PROTOCOL',
      categoryLabel: {
        es: 'OPTIMIZACIÓN REPRODUCIBLE',
        en: 'REPRODUCIBLE OPTIMIZATION',
        sw: 'UREKEBISHAJI RASMI'
      },
      targetModuleTab: 'evaluation_validation',
      moduleLabel: 'Fase 5: Validación',
      summary: {
        es: 'Exploración formal sobre grillas definidas: Random Forest (n_estimators=[50, 100], max_depth=[3, 5, 8], min_samples_split=[2, 5]), Ridge (alpha=[0.1, 1.0, 10.0, 100.0, 500.0, 1000.0]).',
        en: 'Formal exploration across defined grids: Random Forest (n_estimators=[50, 100], max_depth=[3, 5, 8], min_samples_split=[2, 5]), Ridge (alpha=[0.1, 1.0, 10.0, 100.0, 500.0, 1000.0]).',
        sw: 'Uchunguzi wa vigezo: Random Forest (n_estimators=[50, 100], max_depth=[3, 5, 8]) na Ridge kulingana na CV RMSE ya maendeleo.'
      },
      scientificNotes: {
        es: 'Mejor configuración seleccionada por menor MAE en validación cruzada. Persistencia actúa como baseline sin hiperparámetros.',
        en: 'Best configuration chosen by lowest CV MAE. Naive persistence acts as non-parametric reference baseline.',
        sw: 'Usanidi bora ulichaguliwa kwa MAE ya chini zaidi katika uthibitishaji.'
      }
    },
    {
      id: 'champion_tests',
      stepNumber: 8,
      title: {
        es: '8. Selección del Modelo Campeón y Pruebas Bioestadísticas',
        en: '8. Champion Model Selection and Biostatistical Tests',
        sw: '8. Uchaguzi wa Mtindo Bingwa na Majaribio ya Kitakwimu'
      },
      category: 'FORECAST',
      categoryLabel: {
        es: 'PRONÓSTICO SEMANAL AUDITADO',
        en: 'AUDITED WEEKLY FORECAST',
        sw: 'UTABIRI WA KILA WIKI ULIOPIMWA'
      },
      targetModuleTab: 'evaluation_validation',
      moduleLabel: 'Fase 5: Validación',
      summary: {
        es: 'El modelo Baseline_Naive_Persistence fue seleccionado campeón ex-ante por menor RMSE en validación cruzada temporal de desarrollo (CV RMSE 1,183.64 vs RF 1,345.87). En prueba ciega registró MAE 19.23, RMSE 55.64 y MAPE 515.49% (inflado matemáticamente por semanas de incidencia cero o unitaria en el denominador). Pruebas de Diebold-Mariano (DM* = -14.324, p < 0.0001) y Wilcoxon (W = 145.0, p < 0.0001) confirman superioridad estadística frente a Random Forest.',
        en: 'Baseline_Naive_Persistence was selected champion ex-ante by lowest CV RMSE on development set (1,183.64 vs RF 1,345.87). In blind test it achieved MAE 19.23, RMSE 55.64, and MAPE 515.49% (mathematically inflated by zero or 1-case denominator weeks). Diebold-Mariano (DM* = -14.324, p < 0.0001) and Wilcoxon (W = 145.0, p < 0.0001) confirm statistical superiority over Random Forest.',
        sw: 'Baseline_Naive_Persistence ilichaguliwa kama bingwa ex-ante kwa CV RMSE ndogo zaidi ya maendeleo (1,183.64). Kwenye jaribio ilipata MAE 19.23, RMSE 55.64 na MAPE 515.49% (iliyoathiriwa na kesi sifuri kwenye kigawanyo). Majaribio ya Diebold-Mariano (DM* = -14.324, p < 0.0001) na Wilcoxon (W = 145.0, p < 0.0001) yanathibitisha ubora wake dhidi ya Random Forest.'
      },
      scientificNotes: {
        es: 'Ridge obtuvo menor RMSE en test (49.37 vs 55.64), pero no se seleccionó para evitar sesgo retrospectivo (data snooping). El simulador mecanicista SEIR/ABM queda estrictamente segregado de la predicción semanal de casos.',
        en: 'Ridge achieved lower test RMSE (49.37 vs 55.64), but was rejected to prevent retrospective selection bias (data snooping). Mechanistic SEIR/ABM simulation remains strictly separated from weekly statistical forecasting.',
        sw: 'Ridge ilipata RMSE ndogo zaidi kwenye jaribio (49.37), lakini haikuchaguliwa kuzuia upendeleo wa baadae. Mfumo wa SEIR/ABM umetenganishwa rasmi na utabiri wa kila wiki.'
      }
    },
    {
      id: 'artifact_serialization',
      stepNumber: 9,
      title: {
        es: '9. Serialización de Artefactos de Modelos (Joblib & JSON)',
        en: '9. Model Artifact Serialization (Joblib & JSON)',
        sw: '9. Uhifadhi wa Mitindo ya Kompyuta (Joblib na JSON)'
      },
      category: 'PROTOCOL',
      categoryLabel: {
        es: 'ARTEFACTO SERIALIZADO',
        en: 'SERIALIZED ARTEFACT',
        sw: 'KIELELEZO KILICHOHIFADHIWA'
      },
      artifactPath: 'models/champion_covid_model_v1.0.joblib (Sensibilidad) & models/official_naive_persistence_v1.0.json (Campeón t+1)',
      terminalCommand: 'python scripts/train_and_evaluate_models.py',
      summary: {
        es: 'Generación de artefactos formales: official_naive_persistence_v1.0.json (modelo oficial de vigilancia t+1), champion_covid_model_v1.0.joblib (Random Forest para sensibilidad hipotética) y model_evaluation_weekly_results.json. Ridge (MAE 16.04) es benchmark de series temporales, no calibración del SEIR.',
        en: 'Generation of formal artifacts: official_naive_persistence_v1.0.json (official t+1 surveillance champion), champion_covid_model_v1.0.joblib (Random Forest for hypothetical sensitivity), and model_evaluation_weekly_results.json. Ridge (MAE 16.04) is a time series benchmark, not SEIR calibration.',
        sw: 'Uzalishaji wa faili za mitindo: official_naive_persistence_v1.0.json (bingwa t+1), champion_covid_model_v1.0.joblib (usikivu wa Random Forest) na model_evaluation_weekly_results.json.'
      },
      scientificNotes: {
        es: 'El modelo operacional oficial es la Persistencia Naive. El artefacto serializado joblib corresponde al Random Forest multivariado usado estrictamente para análisis de sensibilidad condicional.',
        en: 'The official operational model is Naive Persistence. The serialized joblib artifact belongs to the multivariate Random Forest used strictly for conditional sensitivity analysis.',
        sw: 'Muundo rasmi wa kiutendaji ni Naive Persistence. Kifaa cha joblib ni cha Random Forest kwa ajili ya uchambuzi wa usikivu pekee.'
      }
    },
    {
      id: 'fastapi_backend',
      stepNumber: 10,
      title: {
        es: '10. Endpoints en FastAPI (Backend en Puerto :8000)',
        en: '10. FastAPI Service Endpoints (Backend on Port :8000)',
        sw: '10. Njia za FastAPI (Huduma kwenye Mlango :8000)'
      },
      category: 'PROTOCOL',
      categoryLabel: {
        es: 'SERVICIO BACKEND REST',
        en: 'REST BACKEND SERVICE',
        sw: 'HUDUMA YA NYUMA YA REST'
      },
      apiEndpoint: '/api/v1/validation/weekly-evaluation',
      terminalCommand: 'python -m pytest tests/test_fastapi_v1_api.py -v',
      summary: {
        es: 'Exposición de contratos Pydantic rigurosos: GET /api/v1/validation/weekly-evaluation, GET /api/v1/weekly-forecasting/predict, POST /api/v1/langchain-agent/query y POST /api/v1/langflow/query.',
        en: 'Rigorous Pydantic schema contracts: GET /api/v1/validation/weekly-evaluation, GET /api/v1/weekly-forecasting/predict, POST /api/v1/langchain-agent/query, and POST /api/v1/langflow/query.',
        sw: 'Mikataba ya Pydantic: njia za validation, weekly-forecasting, langchain-agent na langflow.'
      },
      scientificNotes: {
        es: 'Los endpoints resuelven rutas dinámicas relativas con validación de existencia de archivos e informe de errores tipados.',
        en: 'Endpoints resolve dynamic relative paths with existence verification and typed error responses.',
        sw: 'Njia huthibitisha uwepo wa faili na kutoa makosa yaliyopangwa.'
      }
    },
    {
      id: 'react_ui',
      stepNumber: 11,
      title: {
        es: '11. Consumo y Renderizado en Interfaz React (Vite)',
        en: '11. Consumption and Rendering in React Interface (Vite)',
        sw: '11. Matumizi na Mwonekano katika Kiolesura cha React'
      },
      category: 'FORECAST',
      categoryLabel: {
        es: 'INTERFAZ DE USUARIO',
        en: 'USER INTERFACE',
        sw: 'KIOLESURA CHA MTUMIAJI'
      },
      targetModuleTab: 'weekly_forecasting',
      moduleLabel: 'Predicción Semanal & Sensibilidad',
      summary: {
        es: 'La aplicación React consume los endpoints mediante ApiClient, mostrando las series históricas, las métricas de pliegues en Recharts y las predicciones en tiempo real.',
        en: 'React consumes endpoints via ApiClient, rendering historical series, fold metrics on Recharts, and real-time forecasts.',
        sw: 'Programu ya React hutumia ApiClient kuonyesha mfululizo wa kihistoria na utabiri kwa wakati halisi.'
      },
      scientificNotes: {
        es: 'Cada cifra mostrada en pantalla tiene correspondencia unívoca con el JSON de evaluación y con la base de datos limpia.',
        en: 'Every displayed figure maps 1-to-1 to the evaluation JSON and clean database.',
        sw: 'Kila nambari inayooenekana inalingana na JSON na hifadhidata safi.'
      }
    },
    {
      id: 'seir_simulation',
      stepNumber: 12,
      title: {
        es: '12. Gemelo Digital SEIR/ABM (Simulación Mecanicista de Escenarios)',
        en: '12. Digital Twin SEIR/ABM (Mechanistic Scenario Simulation)',
        sw: '12. Pacha wa Kidijitali SEIR/ABM (Uigaji wa Matukio)'
      },
      category: 'SIMULATION',
      categoryLabel: {
        es: 'SIMULACIÓN DE POLÍTICAS',
        en: 'POLICY SIMULATION',
        sw: 'UIGAJI WA SERA'
      },
      targetModuleTab: 'scenario_deployment',
      moduleLabel: 'Fase 6: Despliegue NPIs',
      summary: {
        es: 'Simulador metapoblacional SEIR acoplado con agentes estocásticos intra-hogar para explorar intervenciones no farmacológicas (NPIs), cierres escolares y vacunación.',
        en: 'Metapopulation SEIR simulator coupled with stochastic intra-household agents to explore non-pharmaceutical interventions (NPIs), school closures, and vaccines.',
        sw: 'Kifanisi cha SEIR kilichounganishwa na mawakala wa nyumbani kuchunguza hatua zisizo za dawa na chanjo.'
      },
      scientificNotes: {
        es: 'Diferenciado explícitamente: es una herramienta de simulación contrafactual "qué pasaría si", no un pronosticador puntual semanal de series temporales.',
        en: 'Explicitly differentiated: it is a counterfactual "what-if" policy simulation tool, not a weekly time-series point forecaster.',
        sw: 'Imetofautishwa wazi: ni zana ya uigaji wa sera, sio mtindo wa kutabiri kesi za kila wiki.'
      }
    },
    {
      id: 'langchain_orchestration',
      stepNumber: 13,
      title: {
        es: '13. Orquestación LangChain Core (Pipeline LCEL con @tool)',
        en: '13. LangChain Core Orchestration (LCEL Pipeline with @tool)',
        sw: '13. Mpangilio wa LangChain Core (Mfereji wa LCEL na @tool)'
      },
      category: 'PROTOCOL',
      categoryLabel: {
        es: 'ORQUESTACIÓN LANGCHAIN',
        en: 'LANGCHAIN ORCHESTRATION',
        sw: 'MPANGILIO WA LANGCHAIN'
      },
      targetModuleTab: 'langchain_agent',
      moduleLabel: 'Agente Integrador LangChain',
      summary: {
        es: 'Pipeline determinista LCEL que ejecuta herramientas estructuradas de consulta SQLite, pronósticos de modelos y capacidad condal, con síntesis semántica o fallback tipado.',
        en: 'Deterministic LCEL pipeline executing structured SQLite query tools, model forecasts, and county capacities, with semantic synthesis or typed fallback.',
        sw: 'Mfereji wa LCEL unaoendesha zana za SQLite, utabiri wa mitindo na uwezo wa kaunti.'
      },
      scientificNotes: {
        es: 'Muestra con transparencia absoluta el proveedor, modo de ejecución y lista de herramientas invocadas sin llamarlo falsamente "agente autónomo".',
        en: 'Transparently displays the provider, execution mode, and invoked tool list without falsely calling it an "autonomous agent".',
        sw: 'Inaonyesha wazi mtoaji, hali ya utekelezaji, na orodha ya zana zilizotumiwa bila kusema uongo kuwa ni "wakala anayejitegemea".'
      }
    },
    {
      id: 'langflow_flow',
      stepNumber: 14,
      title: {
        es: '14. Grafo Visual Langflow en Contenedor Docker (:7860)',
        en: '14. Visual Langflow Graph in Docker Container (:7860)',
        sw: '14. Grafu ya Langflow kwenye Kontena ya Docker (:7860)'
      },
      category: 'PROTOCOL',
      categoryLabel: {
        es: 'SERVICIO LANGFLOW',
        en: 'LANGFLOW SERVICE',
        sw: 'HUDUMA YA LANGFLOW'
      },
      targetModuleTab: 'langflow_assistant',
      moduleLabel: 'Flujo Langflow (Servicio API)',
      artifactPath: 'docs/langflow_epidemiology_flow_exported.json',
      apiEndpoint: '/api/v1/langflow/status',
      summary: {
        es: 'Flujo visual en Docker con 4 nodos: Chat Input, Prompt delimitado a fuentes verificadas, componente Ollama Local (qwen2.5:0.5b) y Chat Output, consumido por FastAPI.',
        en: 'Visual flow in Docker with 4 nodes: Chat Input, Prompt bounded by verified sources, Ollama Local (qwen2.5:0.5b) component, and Chat Output, consumed via FastAPI.',
        sw: 'Mtiririko wa kuona katika Docker wenye nodi 4: Chat Input, Prompt iliyothibitishwa, Ollama Local (qwen2.5:0.5b) na Chat Output.'
      },
      scientificNotes: {
        es: 'Verificable en vivo: indicador de conexión real, latencia y respuesta en la interfaz sin emular respuestas si Docker u Ollama están apagados. El grafo no consulta FastAPI.',
        en: 'Live verifiable: real connection indicator, latency, and response in UI without simulating responses if Docker or Ollama are offline. Graph does not query FastAPI.',
        sw: 'Inaweza kuthibitishwa moja kwa moja bila kuiga majibu ikiwa Docker au Ollama imezimwa. Grafu haitumii FastAPI moja kwa moja.'
      }
    },
    {
      id: 'county_audit',
      stepNumber: 15,
      title: {
        es: '15. Datos Condales Auditados (Censo KNBS 2019 & Barasa 2020)',
        en: '15. Audited County Baseline (KNBS 2019 Census & Barasa 2020)',
        sw: '15. Takwimu za Kaunti Zilizothibitishwa (KNBS 2019 & Barasa 2020)'
      },
      category: 'REFERENTIAL',
      categoryLabel: {
        es: 'DATO REFERENCIAL AUDITADO',
        en: 'AUDITED REFERENTIAL DATA',
        sw: 'TAKWIMU ZA REJEA ZILIZOTHIBITISHWA'
      },
      artifactPath: 'src/data/kenyaCounties.ts',
      summary: {
        es: 'Auditoría completa de los 47 condados de Kenia: poblaciones del Censo KNBS 2019 (total nacional: 47,564,296) y camas UCI según Barasa et al. (2020) PLOS ONE Tabla S1.',
        en: 'Full audit of Kenya\'s 47 counties: KNBS 2019 census populations (national total: 47,564,296) and ICU beds per Barasa et al. (2020) PLOS ONE Table S1.',
        sw: 'Ukaguzi kamili wa kaunti 47 za Kenya: idadi ya watu ya KNBS 2019 na vitanda vya ICU kulingana na Barasa et al. (2020) PLOS ONE Jedwali S1.'
      },
      scientificNotes: {
        es: 'Nairobi: 276 camas; Kiambu: 16 camas; Nakuru: 20 camas; 27 condados con 0 camas UCI. Se removieron fórmulas arbitrarias de índice de riesgo.',
        en: 'Nairobi: 276 beds; Kiambu: 16 beds; Nakuru: 20 beds; 27 counties with 0 ICU beds. Arbitrary risk formulas were eliminated.',
        sw: 'Nairobi: vitanda 276; Kiambu: 16; Nakuru: 20; kaunti 27 zina vitanda 0 vya ICU. Njia za nasibu za hatari ziliondolewa.'
      }
    }
  ];

  const currentStep = steps[selectedStepIndex];

  const getBadgeStyle = (category: BadgeCategory) => {
    switch (category) {
      case 'OBSERVED':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'FORECAST':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      case 'SIMULATION':
        return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
      case 'REFERENTIAL':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
      case 'PROTOCOL':
        return 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30';
      default:
        return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Header de la Ruta de Evidencia */}
      <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/60 border-slate-800' : 'bg-white border-slate-200'} shadow-sm`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                <Compass size={20} />
              </span>
              <h2 className="text-xl font-bold tracking-tight">
                {lang === 'en' ? 'Evidence Route (Academic Audit)' : lang === 'sw' ? 'Njia ya Ushahidi (Ukaguzi wa Masomo)' : 'Ruta de Evidencia (Auditoría Académica)'}
              </h2>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                15 Estaciones Verificables • Cero Fabricaciones
              </span>
            </div>
            <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
              {lang === 'en'
                ? 'Follow any figure from the UI back to the Python code, model artifact, SQLite database, and public source. Explicitly distinguishes observed data, forecasts, scenario simulations, and referential data.'
                : lang === 'sw'
                ? 'Fuatilia nambari yoyote kutoka kwenye kiolesura hadi kwenye msimbo wa Python, faili ya mtindo, hifadhidata ya SQLite na chanzo cha umma. Inatofautisha takwimu zilizopimwa, utabiri, uigaji na takwimu za rejea.'
                : 'Permite al docente seguir cualquier cifra desde la interfaz hasta el código Python, el artefacto del modelo, la base SQLite y la fuente pública. Distingue con rigor datos observados, pronósticos, simulaciones y datos referenciales.'}
            </p>
          </div>

          {/* Guía Rápida de Categorías Epistemológicas */}
          <div className="flex flex-wrap gap-1.5 text-[10px] font-mono font-bold">
            <span className="px-2 py-1 rounded-md bg-blue-500/20 text-blue-400 border border-blue-500/30">
              OBSERVADO
            </span>
            <span className="px-2 py-1 rounded-md bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              PRONÓSTICO
            </span>
            <span className="px-2 py-1 rounded-md bg-purple-500/20 text-purple-400 border border-purple-500/30">
              SIMULACIÓN
            </span>
            <span className="px-2 py-1 rounded-md bg-amber-500/20 text-amber-400 border border-amber-500/30">
              REFERENCIAL
            </span>
          </div>
        </div>
      </div>

      {/* 2. Pipeline Horizontal Interactivo de Estaciones */}
      <div className={`p-4 rounded-2xl border overflow-x-auto ${darkMode ? 'bg-slate-900/40 border-slate-800' : 'bg-slate-100/70 border-slate-200'}`}>
        <div className="flex items-center gap-2 min-w-max pb-1">
          {steps.map((st, idx) => (
            <button
              key={st.id}
              onClick={() => setSelectedStepIndex(idx)}
              className={`flex items-center gap-2 px-3 py-2 rounded-xl border text-xs font-mono transition cursor-pointer ${
                selectedStepIndex === idx
                  ? darkMode
                    ? 'bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-600/30 font-bold'
                    : 'bg-indigo-600 text-white border-indigo-600 shadow-md font-bold'
                  : darkMode
                  ? 'bg-slate-800/80 border-slate-700/60 text-slate-300 hover:bg-slate-800'
                  : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-200'
              }`}
            >
              <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                selectedStepIndex === idx ? 'bg-white text-indigo-700' : 'bg-slate-700/60 text-slate-300'
              }`}>
                {st.stepNumber}
              </span>
              <span className="truncate max-w-[120px]">{st.id}</span>
              {idx < steps.length - 1 && <ChevronRight size={12} className="opacity-40 ml-1" />}
            </button>
          ))}
        </div>
      </div>

      {/* 3. Panel de Detalle de la Estación Seleccionada */}
      <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/60 border-slate-800' : 'bg-white border-slate-200'} shadow-sm space-y-5`}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-700/40">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border ${getBadgeStyle(currentStep.category)}`}>
                {currentStep.categoryLabel[lang] || currentStep.categoryLabel.es}
              </span>
              <span className="text-xs font-mono text-slate-400">Estación {currentStep.stepNumber} de {steps.length}</span>
            </div>
            <h3 className="text-base sm:text-lg font-bold tracking-tight">
              {currentStep.title[lang] || currentStep.title.es}
            </h3>
          </div>

          {/* Botón de Navegación Rápida a la Pantalla Correspondiente */}
          {currentStep.targetModuleTab && onNavigateToTab && (
            <button
              onClick={() => onNavigateToTab(currentStep.targetModuleTab!)}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold flex items-center gap-2 shadow-lg shadow-indigo-600/20 transition cursor-pointer"
            >
              <span>Abrir {currentStep.moduleLabel || 'Módulo'}</span>
              <ArrowRight size={14} />
            </button>
          )}
        </div>

        {/* Resumen de la Estación */}
        <p className={`text-xs leading-relaxed ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
          {currentStep.summary[lang] || currentStep.summary.es}
        </p>

        {/* Cajas de Evidencia Técnica */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
          {/* Ruta de Archivo o URL */}
          {currentStep.artifactPath && (
            <div className={`p-3.5 rounded-xl border ${darkMode ? 'bg-slate-950/70 border-slate-800' : 'bg-slate-50 border-slate-200'}`}>
              <div className="text-[10px] text-slate-400 mb-1 flex items-center justify-between">
                <span>ARCHIVO DEL PROYECTO:</span>
                <button
                  onClick={() => copyToClipboard(currentStep.artifactPath!, 'path')}
                  className="hover:text-indigo-400 transition"
                  title="Copiar ruta"
                >
                  {copiedKey === 'path' ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                </button>
              </div>
              <div className="font-bold text-indigo-400 break-all select-all">
                {currentStep.artifactPath}
              </div>
            </div>
          )}

          {currentStep.publicUrl && (
            <div className={`p-3.5 rounded-xl border ${darkMode ? 'bg-slate-950/70 border-slate-800' : 'bg-slate-50 border-slate-200'}`}>
              <div className="text-[10px] text-slate-400 mb-1 flex items-center justify-between">
                <span>URL PÚBLICA OFICIAL:</span>
                <a
                  href={currentStep.publicUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-indigo-400 transition flex items-center gap-1"
                >
                  <ExternalLink size={12} />
                </a>
              </div>
              <div className="font-bold text-blue-400 break-all select-all">
                {currentStep.publicUrl}
              </div>
            </div>
          )}

          {/* Hash Criptográfico o Firma */}
          {currentStep.hashOrSignature && (
            <div className={`p-3.5 rounded-xl border ${darkMode ? 'bg-slate-950/70 border-slate-800' : 'bg-slate-50 border-slate-200'}`}>
              <div className="text-[10px] text-slate-400 mb-1 flex items-center justify-between">
                <span>HASH SHA-256 INMUTABLE:</span>
                <button
                  onClick={() => copyToClipboard(currentStep.hashOrSignature!, 'hash')}
                  className="hover:text-indigo-400 transition"
                  title="Copiar Hash"
                >
                  {copiedKey === 'hash' ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                </button>
              </div>
              <div className="font-bold text-emerald-400 break-all select-all text-[11px]">
                {currentStep.hashOrSignature}
              </div>
            </div>
          )}

          {/* Comando Terminal Reproducible */}
          {currentStep.terminalCommand && (
            <div className={`p-3.5 rounded-xl border ${darkMode ? 'bg-slate-950/70 border-slate-800' : 'bg-slate-50 border-slate-200'}`}>
              <div className="text-[10px] text-slate-400 mb-1 flex items-center justify-between">
                <span className="flex items-center gap-1">
                  <Terminal size={11} /> COMANDO POWERSHELL:
                </span>
                <button
                  onClick={() => copyToClipboard(currentStep.terminalCommand!, 'cmd')}
                  className="hover:text-indigo-400 transition"
                  title="Copiar comando"
                >
                  {copiedKey === 'cmd' ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                </button>
              </div>
              <div className="font-bold text-amber-300 break-all select-all text-[11px]">
                {currentStep.terminalCommand}
              </div>
            </div>
          )}

          {/* Endpoint FastAPI */}
          {currentStep.apiEndpoint && (
            <div className={`p-3.5 rounded-xl border ${darkMode ? 'bg-slate-950/70 border-slate-800' : 'bg-slate-50 border-slate-200'}`}>
              <div className="text-[10px] text-slate-400 mb-1 flex items-center justify-between">
                <span>ENDPOINT REST:</span>
                <button
                  onClick={() => copyToClipboard(currentStep.apiEndpoint!, 'api')}
                  className="hover:text-indigo-400 transition"
                  title="Copiar endpoint"
                >
                  {copiedKey === 'api' ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                </button>
              </div>
              <div className="font-bold text-purple-400 break-all select-all text-[11px]">
                {currentStep.apiEndpoint}
              </div>
            </div>
          )}
        </div>

        {/* Nota Científica / Delimitación */}
        <div className={`p-4 rounded-xl border text-xs flex items-start gap-3 ${
          darkMode ? 'bg-indigo-950/20 border-indigo-900/40 text-indigo-200' : 'bg-indigo-50 border-indigo-200 text-indigo-900'
        }`}>
          <Info size={16} className="text-indigo-400 shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <strong>Delimitación Metodológica para la Sustentación:</strong>{' '}
            {currentStep.scientificNotes[lang] || currentStep.scientificNotes.es}
          </div>
        </div>

        {/* Navegación Anterior / Siguiente */}
        <div className="flex items-center justify-between pt-2">
          <button
            onClick={() => setSelectedStepIndex(Math.max(0, selectedStepIndex - 1))}
            disabled={selectedStepIndex === 0}
            className={`px-3.5 py-1.5 rounded-xl border text-xs font-semibold transition cursor-pointer disabled:opacity-30 ${
              darkMode ? 'bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700' : 'bg-slate-100 border-slate-300 text-slate-700 hover:bg-slate-200'
            }`}
          >
            ← Anterior
          </button>
          <span className="text-[11px] font-mono text-slate-400">
            {selectedStepIndex + 1} de {steps.length}
          </span>
          <button
            onClick={() => setSelectedStepIndex(Math.min(steps.length - 1, selectedStepIndex + 1))}
            disabled={selectedStepIndex === steps.length - 1}
            className={`px-3.5 py-1.5 rounded-xl border text-xs font-semibold transition cursor-pointer disabled:opacity-30 ${
              darkMode ? 'bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700' : 'bg-slate-100 border-slate-300 text-slate-700 hover:bg-slate-200'
            }`}
          >
            Siguiente →
          </button>
        </div>
      </div>
    </div>
  );
};
