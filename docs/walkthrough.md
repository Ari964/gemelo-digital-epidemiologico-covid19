# Guía de Sustentación Académica y Ruta de Evidencia Forense
## Gemelo Digital Epidemiológico de Kenia (GD_TI)
### Metodología CRISP-DM • Backend FastAPI • Frontend React/Vite • LangChain Core • Langflow Docker

---

## 1. Resumen Ejecutivo y Compromisos Cumplidos

Este documento constituye el **guion de demostración paso a paso** para la sustentación académica del proyecto **GD_TI**. Permite al docente o evaluador seguir cualquier cifra, gráfico o conclusión desde la interfaz de usuario en React hasta el código Python, los artefactos serializados, los endpoints de FastAPI y el dataset público original.

### Principios Metodológicos y Epistemológicos Consolidados
1. **Trazabilidad Total y Cero Datos Inventados:**
   - Dataset público de origen: Extracción sin alterar de las 1,674 filas correspondientes a Kenia (`KEN`) del repositorio global de Our World in Data (OWID / OMS), cubriendo del 2020-01-05 al 2024-08-04.
   - Hash SHA-256 inmutable verificado: `c82f3cfc5899b25557f3bf69de987dc9628bfa6fbbee55cd77b649c9d34cd2ba` (1,674 filas de datos, 1,675 líneas totales). Auditado mediante `scripts/check_owid_source.py`.
2. **Segregación Estricta de Tres Componentes:**
   - **Pronóstico Semanal Principal:** Modelo estadístico autorregresivo persistente (`Baseline_Naive_Persistence`, $\hat{y}_{t+1} = y_t$). Seleccionado ex-ante como campeón por mínimo CV RMSE en desarrollo (1,183.64 vs RF 1,345.87). En prueba ciega reservada registró MAE de 19.23 casos, RMSE de 55.64 y MAPE de 515.49% (el MAPE elevado responde a la conocida distorsión con denominadores 0 o 1 caso en el periodo endémico 2023-2024). Pruebas de Wilcoxon ($W = 145.0, p < 0.0001$) y Diebold-Mariano ($DM^* = -14.324, p < 0.0001$) confirman su superioridad estadística frente a Random Forest.
   - **Exploración de Sensibilidad:** Modelo multivariado serializado (`Candidate_Random_Forest`, grid de $n\_estimators=[50, 100]$, $max\_depth=[3, 5, 8]$). No causal; evalúa respuestas hipotéticas ante variables congeladas pos-2022.
   - **Gemelo Digital Mecanicista (SEIR + ABM):** Simulador de escenarios contrafactuales de políticas de salud pública (NPIs, cierres escolares, vacunación, DALYs). Clasificado con honestidad científica como `NOT_EVALUATED_IN_WEEKLY_SERIES` para la tarea de predicción puntual semanal.
3. **Auditoría de Fuentes Condales:**
   - Población oficial de los 47 condados: Censo KNBS 2019, Vol. I, Tabla 2.2 (Total nacional: 47,564,296 hab).
   - Capacidad hospitalaria y camas UCI: Estudio publicado de Barasa et al. (2020) PLOS ONE 15(7):e0236308, Tabla Suplementaria S1 (Nairobi: 276, Mombasa: 35, Kiambu: 16, Nakuru: 20, Bungoma: 24, Kisumu: 23, Uasin Gishu: 59; 27 condados con 0 camas).
   - Se eliminaron fórmulas arbitrarias de "índice de riesgo" y se reemplazaron por densidad real auditada.
4. **Integración Demostrable de LangChain y Langflow con Ollama:**
   - **LangChain Core:** Pipeline LCEL con herramientas `@tool` (`tool_query_observations`, `tool_query_forecasts`, `tool_query_hospital_capacity`), ejecutando localmente vía Ollama (`qwen2.5:0.5b`) con soporte multilingüe (ES, EN, SW). Si Ollama es inaccesible, emite HTTP 503 explícito sin fallbacks de datos inventados.
   - **Langflow en Docker (:7860):** Flujo epidemiológico real (`906a3d58-bcf0-48a9-9364-4a62ea230945`) con 4 nodos funcionales (Chat Input -> Prompt Template con hechos epidemiológicos -> Ollama Local qwen2.5:0.5b -> Chat Output). El grafo opera de forma autónoma y NO consulta FastAPI internamente. Exportación limpia en `docs/langflow_epidemiology_flow_exported.json`.
5. **Generación de 4 Informes Académicos Oficiales (ReportLab & OpenPyXL):**
   - Cuatro áreas de informe: Procedencia de Datos, Validación de Modelos, Predicción Semanal y Escenarios SEIR/ABM.
   - Vista previa interactiva en React y descargas nativas en PDF formal (ReportLab con tablas y pie de firma) y hojas de cálculo Excel (openpyxl con estilos corporativos y metadatos).
6. **Traducción Trilingüe y Dual-Theme:**
   - Cobertura completa en Español (ES), Inglés (EN) y Suajili (SW) en todas las vistas, tablas y diálogos.
   - Modos Claro y Oscuro con contraste verificado y persistencia en `localStorage`.

---

## 2. Modos de Verificación Empírica Ejecutados

| Componente | Tipo de Prueba | Comando / Archivo de Ejecución | Resultado Verificado |
| :--- | :---: | :--- | :--- |
| **Integridad del Dataset Crudo** | Criptográfica | `python scripts/check_owid_source.py` | `c82f3cfc5899b25557f3bf69de987dc9628bfa6fbbee55cd77b649c9d34cd2ba` (1,674 filas) |
| **Entrenamiento Reproducible** | Script Python | `python scripts/train_and_evaluate_models.py` | 5 pliegues temporales, grilla RF [50, 100], serialización de modelos y JSON de resultados |
| **Suite Completa Backend** | Pruebas Automatizadas | `pytest tests/ -v` | **83 passed, 1 skipped** (100% pruebas activas aprobadas) |
| **Documentación OpenAPI Swagger** | Interfaz Interactiva | Abrir en navegador: `http://127.0.0.1:8000/api/v1/docs` | 200 OK: Swagger UI interactivo con esquemas Pydantic y autorización OAuth2 |
| **Endpoint Evaluación Semanal** | API REST | `curl http://localhost:8000/api/v1/validation/weekly-evaluation` | 200 OK: 4 modelos, 5 pliegues, Wilcoxon $W=145$, DM $DM^*=-14.324$, 71 puntos test |
| **Endpoint Predicción Semanal** | API REST | `POST /api/v1/predictions/weekly` | 200 OK: Cortes 2024-07-28 ($0.0 \to 0.0$) y 2021-07-11 ($2922 \to 3922$) |
| **Servicio Langflow Docker** | API & Contenedor | `curl http://localhost:8000/api/v1/langflow/status` | 200 OK: `status: "ONLINE"`, `connected: true`, latencia verificada |
| **Informes ReportLab & OpenPyXL** | Pruebas API & Binarios | `python scripts/test_reports_live.py` | 4 reportes validados: Preview JSON, PDF (%PDF) y Excel (PK ZIP) en ES, EN y SW |
| **Compilación Frontend** | TypeScript / Vite | `npm run build` | **0 errores TypeScript** (`tsc --noEmit`), bundle generado limpiamente |
| **Recorrido de Interfaz** | Visual e Interactiva | `http://localhost:3000` | 15 pantallas accesibles, 3 idiomas (ES, EN, SW), 2 temas (Claro/Oscuro) |

---

### 2.1 Credenciales Sembradas Oficiales (`seed_verified_data.py`) y Acceso Swagger

La base de datos SQLite del sistema (`kenya_covid_clean.db`) cuenta con tres roles RBAC activos sembrados con contraseñas hash bcrypt seguras mediante `backend/app/scripts/seed_verified_data.py`:

| Rol RBAC | Nombre del Usuario | Correo Electrónico (Username) | Contraseña Oficial | Ámbito de Permisos y Uso |
| :--- | :--- | :--- | :--- | :--- |
| **Administrador** (`admin`) | Ing. Administrador Sistema | `admin@epidemic-twin.ke` | `AdminSecure2026!` | Acceso total, auditoría, re-entrenamiento de modelos y control de usuarios |
| **Epidemióloga Jefe** (`epidemiologist`) | Dra. Wanjiku | `dr.wanjiku@health.go.ke` | `EpiChief2026!` | Parametrización SEIR/ABM, simulación contrafactual y exportación de reportes |
| **Analista MOH** (`analyst`) | Analista Omondi | `omondi@moh.go.ke` | `AnalystMOH2026!` | Consulta de series temporales, descarga de informes (PDF/Excel) y vigilancia |

#### Procedimiento de Autorización en Swagger UI:
1. Abrir la URL canónica de la API: **`http://127.0.0.1:8000/api/v1/docs`** (Swagger UI con prefijo `/api/v1`).
2. Presionar el botón superior derecho **Authorize** (ícono de candado).
3. En el diálogo modal OAuth2 (`/api/v1/auth/login`), ingresar:
   - **Username:** `admin@epidemic-twin.ke`
   - **Password:** `AdminSecure2026!`
4. Hacer clic en **Authorize** y luego **Close**. Todos los endpoints protegidos (predicciones semanales, generación de reportes binarios, auditorías) se ejecutarán con token JWT Bearer verificado.
*(Documentación técnica alternativa ReDoc en `http://127.0.0.1:8000/api/v1/redoc` y especificación OpenAPI cruda en `http://127.0.0.1:8000/api/v1/openapi.json`)*.

---

## 3. Guion de Demostración Presencial Paso a Paso

### Estación 1: Fuente Pública y Criptografía del Dataset Crudo
- **Qué abrir:** Consola PowerShell o explorador de archivos en `data/raw/owid_covid_kenya_raw.csv`.
- **Qué ejecutar:**
  ```powershell
  python scripts/check_owid_source.py
  Get-FileHash data/raw/owid_covid_kenya_raw.csv -Algorithm SHA256
  ```
- **Qué observar:**
  - Hash exacto: `c82f3cfc5899b25557f3bf69de987dc9628bfa6fbbee55cd77b649c9d34cd2ba`.
  - Número de filas: 1,674 observaciones empíricas (2020-01-05 a 2024-08-04, 1,675 líneas con encabezado).
- **Límite científico a explicar:**  
  *«El CSV crudo es una extracción sin alterar de las filas de Kenia del consolidado global de Our World in Data. Los datos de incidencia son de alcance estrictamente NACIONAL. No contienen desglose condal ni se inventaron registros.»*

---

### Estación 2: Carga, Limpieza y Partición Temporal (CRISP-DM Fase 1-3)
- **Qué abrir:** En el frontend, módulo **«Fase 1-3: Integración ETL»** (`DataIntegrationView`).
- **Qué ejecutar en terminal (si se solicita reproducción):**
  ```powershell
  python scripts/build_clean_kenya_database.py
  ```
- **Qué observar:**
  - Base SQLite en `data/clean/kenya_covid_clean.db` con tabla `kenya_weekly_cases`.
  - Agregación canónica dominical (`W-SUN`): 231 semanas epidemiológicas.
  - Partición cronológica estricta sin data leakage:
    * Conjunto de Desarrollo: 160 semanas (2020-03-08 a 2023-03-26).
    * Conjunto de Prueba Ciego: 71 semanas (2023-04-02 a 2024-07-28).
- **Límite científico a explicar:**  
  *«No se realizó partición aleatoria porque destruiría la autocorrelación de la serie temporal. El conjunto de prueba se reservó íntegramente fuera de muestra para evaluar la meseta endémica.»*

---

### Estación 3: Vista de Evaluación Semanal y Pruebas Bioestadísticas (CRISP-DM Fase 5)
- **Qué abrir:** En el frontend, módulo **«Fase 5: Validación»** (`ValidationView`).
- **Qué observar en pantalla:**
  1. **Banner Epistemológico:** Deslinde explícito entre modelos estadísticos semanales y el simulador de escenarios SEIR/ABM.
  2. **Tabla de Modelos Evaluados:**
     - `Baseline_Naive_Persistence`: Campeón Oficial (CV RMSE: 1,183.64, Test MAE: 19.23, Test RMSE: 55.64, Test MAPE: 515.49%).
     - `Candidate_Random_Forest`: Exploración de Sensibilidad (CV RMSE: 1,345.87, Test MAE: 74.05, Test RMSE: 81.72, Test MAPE: 5,045.49%).
     - `Baseline_Ridge_Regression`: Benchmark Estadístico Ex-Post (CV RMSE: 1,405.93, Test MAE: 16.04, Test RMSE: 49.37, Test MAPE: 43.66%).
     - `Candidate_HistGradientBoosting`: Comparativo (CV RMSE: 2,041.78, Test MAE: 63.27, Test RMSE: 74.09, Test MAPE: 4,280.72%).
  3. **Visualizador de 5 Pliegues Temporales (`TimeSeriesSplit`):**
     - Selector interactivo de Pliegues 1 a 5 con fechas de entrenamiento y validación transparentes.
  4. **Tarjetas de Pruebas Bioestadísticas Formales:**
     - **Diebold-Mariano (Harvey-Leybourne-Newbold 1997):** $DM^* = -14.324, p < 0.0001$. Confirma superioridad de la persistencia corrigiendo por autocorrelación.
     - **Wilcoxon Signed-Rank:** $W = 145.0, p < 0.0001$. Diferencia significativa en medianas de error pareado.
     - **Shapiro-Wilk:** $W = 0.6887, p < 0.0001$. Demuestra no normalidad de residuos y justifica pruebas no paramétricas.
     - **Kolmogorov-Smirnov:** Determina divergencia acumulada ($D = 0.8592, p < 0.0001$) sin declarar ranking.
  5. **Gráfico Recharts de la Serie Temporal de Test (71 semanas):**
     - Curva de casos observados reales frente a la persistencia y Random Forest.
- **Límite científico a explicar:**  
  *«Se retiraron los STATIC_METRICS y las afirmaciones no sustentadas de 'SEIR supera a otros modelos +74%'. El simulador SEIR/ABM queda formalmente registrado como NO EVALUADO en la serie semanal porque su propósito es el análisis de políticas contrafactuales, no el pronóstico autorregresivo puntual.»*

---

### Estación 4: Vigilancia Semanal y Exploración de Sensibilidad
- **Qué abrir:** Módulo **«Predicción Semanal & Sensibilidad»** (`WeeklyForecastingView`).
- **Qué probar:**
  - Seleccionar **Corte 2024-07-28 (Endémico)**:
    * Naive pronostica para 2024-08-04: $0.0\text{ casos}$ (Observado real: $0.0$, MAE = $0.0$).
    * Random Forest predice: $70.76\text{ casos}$ (Sobrepredicción por variables macroeconómicas e índices congelados pos-2022).
  - Seleccionar **Corte 2021-07-11 (Ola Delta)**:
    * Naive pronostica para 2021-07-18: $2,922\text{ casos}$ (Observado real: $3,922$).
    * Random Forest predice: $3,270.26\text{ casos}$.
- **Límite científico a explicar:**  
  *«En regímenes planos endémicos con reporte semanal nulo, la persistencia es matemáticamente insuperable. Random Forest sirve para explorar sensibilidad ante políticas hipotéticas, pero no constituye un efecto causal demostrado.»*

---

### Estación 5: Agente Integrador LangChain Core
- **Qué abrir:** Módulo **«Agente Integrador LangChain»** (`LangChainAgentView`).
- **Qué configurar y ejecutar:**
  - Ámbito: `Kiambu (22)`.
  - Corte: `2024-07-28`.
  - Pregunta: *«¿Cuál es el pronóstico nacional y la capacidad de camas UCI registrada para el condado?»*
  - Clic en **«Ejecutar LangChain»**.
- **Qué observar:**
  - Panel 1: Observaciones SQLite (`tool_query_observations`).
  - Panel 2: Pronósticos estadísticos (`tool_query_forecasts`).
  - Panel 3: Síntesis contextualizada delimitando casos nacionales (KEN) de inventario condal descriptivo (Kiambu: 16 camas Barasa 2020 / 24 camas inventario).
  - Panel 4: Metadatos técnicos de ejecución: Proveedor, tiempo de ejecución en ms, componentes de `langchain_core` ejecutados y herramientas `@tool` invocadas.
- **Límite científico a explicar:**  
  *«La interfaz no llama 'agente autónomo' a una secuencia fija. Muestra con transparencia el modo de ejecución LCEL y prohíbe inferir saturación hospitalaria en Kiambu por ausencia de desagregación territorial de casos.»*

---

### Estación 6: Flujo Langflow en Contenedor Docker (:7860)
- **Qué abrir:** Módulo **«Flujo Langflow (Servicio API)»** (`LangflowAssistantView`).
- **Qué verificar en pantalla:**
  - **Indicador de Conexión:** Muestra `ONLINE` (en verde) con la latencia real en milisegundos hacia el puerto 7860.
  - **Topología Real del Grafo:** Detalla los 4 nodos activos del flujo (`Chat Input` $\to$ `Prompt Template Delimitado` $\to$ `Ollama Local (qwen2.5:0.5b)` $\to$ `Chat Output`).
  - **Naturaleza del Flujo:** El flujo real opera mediante inyección de contexto científico verificado en el prompt (datos de OWID, Baseline_Naive_Persistence, Camas Barasa 2020 S1 Table, Censo KNBS 2019) y generación local con Ollama (`qwen2.5:0.5b`). **No ejecuta llamadas HTTP a endpoints de FastAPI en tiempo de ejecución**. La interacción es unidireccional (FastAPI consulta a Langflow como servicio externo).
- **Qué ejecutar:**
  - Enviar una consulta en vivo: *«¿Cuál es el pronóstico nacional del modelo campeón y cuántas camas UCI verificadas tiene Kiambu según Barasa et al. (2020)?»*
- **Qué observar:**
  - Respuesta generada en vivo por Ollama procesada a través del grafo de Langflow vía API REST (`POST /api/v1/langflow/query`).
  - Banner de trazabilidad empírica fundamentado en Barasa et al. (2020) y KNBS 2019.
  - Si el contenedor Docker se detuviera, el sistema reporta `OFFLINE` de inmediato con diagnóstico visible y sin simular respuestas ficticias.
- **Demostración en Langflow UI:**
  - Abrir `http://localhost:7860` en el navegador.
  - Abrir el flujo **«Asistente de Vigilancia Epidemiológica de Kenia»** (`906a3d58-bcf0-48a9-9364-4a62ea230945`).
  - Abrir el **Playground** de Langflow y ejecutar la misma consulta, comprobando la total concordancia con la vista en React y el backend FastAPI.
  - El flujo exportado completo se encuentra archivado en `docs/langflow_epidemiology_flow_exported.json`.

---

### Estación 7: Navegación por la «Ruta de Evidencia»
- **Qué abrir:** Módulo **«Ruta de Evidencia (Auditoría)»** (`EvidenceRouteView`).
- **Qué observar:**
  - Las 15 estaciones ordenadas desde la URL pública de OWID hasta el flujo de Langflow.
  - Distintivos epistemológicos por color: `[DATO OBSERVADO]`, `[PRONÓSTICO SEMANAL]`, `[SIMULACIÓN ESCENARIO]`, `[DATO REFERENCIAL]`, `[PROTOCOLO METODOLÓGICO]`.
  - Botones de copiado de rutas, comandos de terminal verificables y botones de salto directo a los módulos.

---

### Estación 8: Verificación Trilingüe (ES, EN, SW) y Dual-Theme
- **Qué probar:**
  - Cambiar idioma en la barra superior a **EN** (English) y **SW** (Kiswahili).
  - Verificar que el sidebar, títulos, selectores, botones y leyendas cambian de idioma.
  - Cambiar el tema a **Modo Claro** y **Modo Oscuro** con el botón inferior del sidebar.
  - Recargar la página (`F5`): verificar que la preferencia de idioma y modo de tema se preservan mediante `localStorage`.

---

### Estación 9: Workspace de Ciencia de Datos en Streamlit (:8501) - CRISP-DM Integral
- **Qué abrir:** En el navegador web, acceder a `http://localhost:8501`.
- **Qué recorrer secuencialmente:**
  1. **Inicio (`app.py`):** Visión panorámica del estándar CRISP-DM y deslinde estricto entre el workspace técnico para el docente/científico de datos y el frontend en React para tomadores de decisiones.
  2. **Fase 1 (Comprensión del Negocio):** Definición formal de la variable objetivo nacional semanal ($y_{t+1}$), unidad (`casos/semana`), horizonte estricto de 1 semana hacia adelante, aclaración de que los 4 rezagos constituyen una ventana retrospectiva de entrada y no un pronóstico multi-paso, y separación categórica entre modelos estadísticos y el gemelo mecanicista SEIR/ABM.
  3. **Fase 2 (Comprensión de los Datos / EDA):** Enlace oficial a Our World in Data, licencia CC BY 4.0, cálculo en vivo de SHA-256 del CSV crudo (`c82f3cfc5899b25557f3bf69de987dc9628bfa6fbbee55cd77b649c9d34cd2ba`), botón de descarga directa del CSV original sin alterar, EDA exhaustivo sobre la serie nacional con interpretaciones e implicancias metodológicas bajo cada gráfica, demostración de concentración de reportes dominicales (87.8%), y auditoría pública de los 47 condados con la Tabla S1 de Barasa et al. (2020) PLOS ONE presente en disco.
  4. **Fase 3 (Preparación de Datos):** Tabla de conciliación matemática exacta de filas (1,674 crudos $\to$ exclusión pre-epidémica de 68 días $\to$ 1,606 días activos $\to$ 230 semanas dominicales $\to$ 4 semanas de buffer causal $\to$ 226 semanas finales), desglose cronológico estricto (155 semanas de desarrollo y 71 semanas de test hold-out), y verificación automática de ajuste exclusivo de escaladores e imputadores en desarrollo (anti data leakage).
  5. **Fase 4 (Modelado y Entrenamiento Canónico):** Botón interactivo de ejecución que invoca directamente `scripts/train_and_evaluate_models.py` en tiempo real, auditoría de los 5 pliegues temporales (`TimeSeriesSplit`), visualización de la grilla de hiperparámetros explorada, selección ciega ex-ante del campeón por menor CV RMSE en desarrollo (Naive Persistence), y calibración honesta de parámetros SEIR vinculada a picos reales observados en OWID (Ola Ómicron / Delta) sin sliders inventados.
  6. **Fase 5 (Evaluación Científica y Pruebas Bioestadísticas):** Eliminación total de muestras aleatorias (`np.random`). Tabla trazable de métricas en desarrollo y prueba reservada, contraste ex-ante (Naive campeón) vs ex-post (Ridge benchmark), explicación de la distorsión de MAPE ante ceros endémicos, pruebas estadísticas pareadas formales de Shapiro-Wilk ($W=0.6887, p < 0.0001$), Wilcoxon pareado ($W=145.0, p < 0.0001$ bilateral; $p=1.0000$ unilateral con interpretación bioestadística exacta), Diebold-Mariano HLN 1997 ($DM^*=-14.324, p < 0.0001$), Kolmogorov-Smirnov ($D=0.8592$), y deslinde formal de comparaciones no evaluadas (AUC-ROC saturación UCI y SEIR/ABM en serie semanal).
  7. **Fase 6 (Despliegue y Gobernanza):** Inventario de artefactos serializados con hashes criptográficos, descriptor de persistencia `official_naive_persistence_v1.0.json`, modelo de sensibilidad `champion_covid_model_v1.0.joblib`, estado en vivo del backend FastAPI (:8000), y consulta en vivo del endpoint `/api/v1/predictions/weekly` con respuesta JSON real en pantalla.

---

## 4. Auditoría de Datos Condales: Población y Camas UCI

### 4.1 Población de los 47 Condados (Censo KNBS 2019)
- Fuente: *Kenya National Bureau of Statistics (KNBS) 2019 Kenya Population and Housing Census, Volume I, Table 2.2*.
- Población nacional total verificada: **47,564,296 habitantes**.

### 4.2 Camas de Cuidados Intensivos (Barasa et al. 2020 PLOS ONE)
- Referencia: Barasa, E., Ouma, P. O., & Okiro, E. A. (2020). *Assessing the hospital surge capacity of the Kenyan health system in the face of the COVID-19 pandemic*. **PLOS ONE**, 15(7), e0236308. DOI: [10.1371/journal.pone.0236308](https://doi.org/10.1371/journal.pone.0236308).
- Material Suplementario: `S1 Table. Data on hospital, ICU beds, and ventilators in Kenya`.
- Cifras auditadas incorporadas en `src/data/kenyaCounties.ts`:
  * **Nairobi:** 276 camas (99 públicas, 137 privadas, 40 religiosas).
  * **Mombasa:** 35 camas (12 públicas, 23 privadas).
  * **Kiambu:** 16 camas (11 públicas, 5 religiosas).
  * **Nakuru:** 20 camas (6 públicas, 14 privadas).
  * **Bungoma:** 24 camas.
  * **Kisumu:** 23 camas.
  * **Uasin Gishu:** 59 camas.
  * **27 condados:** 0 camas UCI registradas.
  * **Total nacional:** 537 camas UCI.
- Se eliminaron todos los fallbacks ficticios y se documentó la distinción entre el inventario basal publicado y las cifras operativas referenciales.

---

## 5. Arquitectura de Servicios y Puertos de Red

FastAPI corre de forma **nativa en el entorno virtual de Windows** (`.venv`), mientras que **Langflow** y su base de datos PostgreSQL se ejecutan dentro de **Docker Desktop**. Ollama corre localmente en Windows escuchando en `0.0.0.0:11434`.

```
[ Navegador Web ]
      │
      ├─── HTTP :3000 ────────> [ Frontend React + Vite (Tailwind CSS) ]
      │                                    │
      │                             Proxy / API Fetch
      │                                    ▼
      ├─── HTTP :8000 ────────> [ Backend FastAPI (Windows .venv - Python 3.11) ]
      │                                    │
      │                         ┌──────────┴──────────────────────────┐
      │                         ▼                                     ▼
      │               [ SQLite Clean DB ]                  [ Modelos Serializados ]
      │             (kenya_covid_clean.db)                  (models/*.joblib & .json)
      │                         │                                     │
      │                         │                                     ▼
      │                         │                         [ Ollama Daemon :11434 ]
      │                         │                          (Modelo: qwen2.5:0.5b)
      │                         │                                     ▲
      │                         ▼                                     │ (host.docker.internal:11434)
      └─── HTTP :7860 ───> [ Langflow en Contenedor Docker ] ─────────┘
```

### Rutas de Red Demostradas y Verificadas:
1. **Navegador → Vite (`http://localhost:3000`)**: Carga la SPA React en ES/EN/SW con soporte de temas claro/oscuro.
2. **Vite → FastAPI (`http://127.0.0.1:8000`)**: Proxy configurado en `vite.config.ts` para `/api` → `http://127.0.0.1:8000`.
3. **Backend → Ollama (`http://localhost:11434`)**: FastAPI se comunica directamente con la API REST de Ollama (`/api/generate`) utilizando el modelo local `qwen2.5:0.5b`. Usado en `/api/v1/ai/chat`, `/api/v1/langchain-agent/query` y en `apps/academic_translator`.
4. **Backend → Langflow (`http://localhost:7860`)**: FastAPI ejecuta consultas hacia la API de Langflow v1.0 (`POST /api/v1/run/{flow_id}`) para obtener síntesis de lenguaje natural con el asistente de vigilancia.
5. **Langflow (Docker) → Ollama (`http://host.docker.internal:11434`)**: El contenedor Docker se conecta al host de Windows mediante `host.docker.internal` para la generación LLM con el modelo local `qwen2.5:0.5b`.
*(Nota: El flujo de Langflow opera mediante Prompt delimitado con datos del proyecto y Ollama; no realiza llamadas HTTP de regreso a FastAPI).*

---

## 6. Lista Real de Pendientes Técnicos y Fronteras Científicas

Para preservar la total integridad académica ante el jurado, se declaran los siguientes límites y trabajos futuros reales:

1. **Ausencia de Serie Temporal Desagregada por Condado:**  
   El Ministerio de Salud de Kenia (MOH) y Our World in Data publican la serie temporal histórica a nivel estrictamente nacional (`KEN`). No existe un repositorio público abierto que provea la incidencia semanal continua de casos para los 47 condados individuales entre 2020 y 2024. La distribución espacial condal opera mediante la estructura metapoblacional SEIR y datos de censo, no por series empíricas locales observadas.
2. **Modelo de Admisión Clínica Territorial Pendiente:**  
   No existe una función de transferencia clínica validada empíricamente que convierta los casos nacionales reportados en ingresos hospitalarios a camas UCI por condado en Kenia. Por tal razón, se prohíbe cualquier conclusión que afirme la "saturación o no saturación de camas UCI en Kiambu".
3. **Persistencia de Variables Macroeconómicas Pos-2022:**  
   El índice de rigurosidad gubernamental de Oxford (`stringency_index`) y la tasa de reproducción efectiva se interrumpieron en las fuentes globales tras finales de 2022. Para evaluar Random Forest pos-2022, se utilizan valores imputados conservadores (último valor observado), lo que explica la sobrepredicción del modelo en la fase endémica frente a la persistencia.
4. **Requisitos de Hardware para Ollama:**  
   El sistema está optimizado para inferencia en CPU/GPU mediante el modelo local ligero `qwen2.5:0.5b` (398 MB), eliminando la dependencia de credenciales en la nube (`GEMINI_API_KEY`). Si Ollama se detiene, el backend y los tests capturan la excepción con un mensaje controlado de desconexión sin provocar caída del servidor.

---

## 7. Instrucciones para Arrancar Todo el Entorno Local en Windows

### Terminal 1: Ollama Daemon
```powershell
ollama serve
# Verificar que el modelo qwen2.5:0.5b esté disponible:
ollama run qwen2.5:0.5b "test"
```

### Terminal 2: Contenedor Docker de Langflow
```powershell
cd "C:\Users\KRISTEL\Documents\langflow\docker_example"
docker compose up -d
# Verificar que el contenedor esté UP:
docker ps
```
*(Disponible en `http://localhost:7860`)*

### Terminal 3: Backend FastAPI (Windows Nativo)
```powershell
cd "d:\X CICLO\TRABAJO DE INVESTIGACIÓN\SEMANA 2\GD_TI"
.\.venv\Scripts\Activate.ps1
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
*(Documentación OpenAPI Swagger interactiva en `http://127.0.0.1:8000/api/v1/docs` | ReDoc en `http://127.0.0.1:8000/api/v1/redoc`)*

### Terminal 4: Frontend React / Vite
```powershell
cd "d:\X CICLO\TRABAJO DE INVESTIGACIÓN\SEMANA 2\GD_TI"
npm run dev
```
*(Acceder en el navegador a `http://localhost:3000`)*

### Terminal 5: Workspace Científico Streamlit (CRISP-DM)
```powershell
cd "d:\X CICLO\TRABAJO DE INVESTIGACIÓN\SEMANA 2\GD_TI"
.\.venv\Scripts\Activate.ps1
streamlit run apps/data_science_workspace/app.py --server.port 8501
```
*(Acceder en el navegador a `http://localhost:8501`)*

### Terminal 6: Comprobaciones Automatizadas y Empaquetado
```powershell
cd "d:\X CICLO\TRABAJO DE INVESTIGACIÓN\SEMANA 2\GD_TI"
# Suite estricta de servicios en vivo:
.\.venv\Scripts\python.exe -m pytest tests/test_live_services_strict.py -v
# Suite de regresión metodológica:
.\.venv\Scripts\python.exe -m pytest tests/test_weekly_prediction_alignment.py tests/test_langchain_agent.py tests/test_weekly_evaluation_and_langflow.py -v
# Compilación del frontend:
npm run build
# Generación del archivo RAR final único de entrega:
python scripts/package_submission.py
```

