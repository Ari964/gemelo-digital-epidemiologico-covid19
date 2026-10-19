# Documento de Trazabilidad, Auditoría y Reproducibilidad Científica (Fase 1)
## Gemelo Digital Epidemiológico de Nivel Poblacional (Kenia - COVID-19)

**Fecha de Ejecución y Auditoría:** 23 de septiembre de 2026  
**Ámbito Territorial:** Kenia (Nivel Nacional y Articulación con 47 Condados)  
**Marco Metodológico:** CRISP-DM (Cross-Industry Standard Process for Data Mining) - Fases 1 a 5  
**Entorno de Ejecución:** Python 3.11 en entorno virtual `.venv`  

---

## 1. Auditoría del Estado del Repositorio y Diagnóstico Inicial

Se realizó una inspección forense del repositorio, el esquema relacional (`epidemic_twin.db`), los artefactos de modelos y los módulos de análisis:

1. **Datos Territoriales y Hospitalarios Preexistentes**:
   - El archivo `backend/app/data/kenya_47_counties_verified.json` contiene la demografía oficial de los 47 condados de Kenia (Censo KNBS 2019 y quintiles socioeconómicos KDHS 2022).
   - En camas de Unidades de Cuidados Intensivos (KMFL), los condados sin reporte verificado se mantienen rigurosamente en `null`.
2. **Ausencia de Series Temporales Empíricas en Base de Datos**:
   - La tabla `dataset_observations` de la base de datos `epidemic_twin.db` contenía **0 filas**.
   - Los registros de la tabla `evaluation_runs` apuntaban a `ds-knbs-2019` (un censo demográfico estático, no una serie temporal de incidencia).
3. **Simulaciones de Laboratorio Sintéticas**:
   - En `apps/data_science_workspace/pages/5_Fase_5_Evaluacion.py`, el laboratorio interactivo generaba curvas con funciones trigonométricas `np.sin()` y ruido Gaussiano (`ground_truth = np.abs(2000 * np.sin(t) + 350 * rng.normal(0, 1, n_days) + 2500)`), marcadas con la advertencia obligatoria `BLOCKED_DEMO`.
   - La movilidad intercondal utilizaba un modelo gravitacional sintético (`ESTIMATED` / `SYNTHETIC`), bloqueado para contraste científico formal de H1.
4. **Artefactos de Modelos en Disco**:
   - Los archivos `models/champion_v1.0.0-prod-e2e.json` y `models/champion_v1.0.0-test.json` eran archivos JSON estáticos con parámetros predefinidos (`r2: 0.94`, `mape: 4.8%`), pero **sin ningún pipeline de inferencia real serializado** (`.joblib` / `.pkl`) ni entrenamiento subyacente.
5. **Validación Externa (2023–2024)**:
   - El archivo `backend/app/data/kenya_external_validation_2023_2024.csv` no existía físicamente en disco, por lo que el gestor `ExternalValidationManager` reportaba honestamente `status: PENDING`.
6. **Objetivo Predictivo del Gemelo Digital**:
   - Predecir la dinámica temporal de casos de COVID-19 en Kenia en función del historial reciente, intervenciones gubernamentales no farmacéuticas (Oxford Stringency Index) e indicadores epidemiológicos (tasa de reproducción $R_t$).

---

## 2. Ficha Técnica y Procedencia del Dataset Público Auténtico

| Parámetro | Detalle Institucional Verificado |
| :--- | :--- |
| **Institución Emisora** | **Our World in Data (OWID) / University of Oxford / Global Change Data Lab** |
| **Título Oficial** | Coronavirus Pandemic (COVID-19) - Kenya Official Time-Series Data |
| **Página Web Oficial** | [https://ourworldindata.org/coronavirus](https://ourworldindata.org/coronavirus) |
| **Enlace Directo de Descarga** | [https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv](https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv) |
| **Licencia de Uso** | **Creative Commons Attribution 4.0 International (CC BY 4.0)** |
| **Estado del Repositorio** | **Archivo histórico oficial consolidado**. Congeló actualizaciones periódicas en 2024 ante la transición de los sistemas de reporte de la OMS post-emergencia. |
| **Fecha de Consulta y Extracción**| 23 de septiembre de 2026 |
| **Entidad Geográfica** | Kenia (`iso_code: KEN`, `location: Kenya`) |
| **Cobertura Temporal Observada** | **2020-01-05 a 2024-08-04** (1,674 días / 230 semanas epidemiológicas) |
| **Variables Principales** | `date`, `total_cases`, `new_cases`, `new_cases_smoothed`, `total_deaths`, `new_deaths`, `stringency_index` (Oxford Blavatnik School), `reproduction_rate` ($R_t$), `positive_rate`, `tests_per_case`, `people_vaccinated`, `population`, `hospital_beds_per_thousand`. |
| **Archivo Extraído y Preservado**| [`data/raw/owid_covid_kenya_raw.csv`](file:///d:/X%20CICLO/TRABAJO%20DE%20INVESTIGACI%C3%93N/SEMANA%202/GD_TI/data/raw/owid_covid_kenya_raw.csv) (1,674 filas $\times$ 67 columnas) |
| **Checksum SHA-256** | `c82f3cfc5899b25557f3bf69de987dc9628bfa6fbbee55cd77b649c9d34cd2ba` |
| **Declaración de Alcance** | Registros epidemiológicos históricos oficiales consolidados por OMS/MoH. **No se atribuyen sensores IoT en tiempo real ni trazas de GPS simuladas.** |

---

## 3. Análisis de Frecuencia Real y Conciliación Exacta de Registros

### 3.1 Frecuencia Real de los Datos de Casos y Definición de `new_cases_smoothed`

La auditoría cuantitativa reveló un hallazgo fundamental sobre la naturaleza del dato:
- En el archivo crudo de Kenia, **el 100.0% de los valores positivos de `new_cases` ocurren exclusivamente los DOMINGOS** (189 domingos con reporte positivo; de lunes a sábado el valor registrado es estrictamente 0).
- La columna `new_cases_smoothed` corresponde a una media móvil de 7 días calculada por OWID: en la práctica, **divide el lote semanal reportado el domingo entre 7** y lo replica como un valor constante a lo largo de los días de esa semana epidemiológica.
- **Consecuencia Metodológica**: Describir `new_cases_smoothed` como un "conteo diario observado" es incorrecto; es un valor promedio imputado a partir de un reporte semanal en bloque. En consecuencia, la **tarea predictiva canónica y defendible es la PREDICCIÓN DE INCIDENCIA SEMANAL (Weekly Epidemiological Surveillance)**, que coincide con el estándar de vigilancia de la OMS, los CDC de África y el Ministerio de Salud de Kenia.

### 3.2 Tabla Reproducible de Conciliación de Filas y Exclusiones

| Etapa del Flujo | Registros | Rango de Fechas | Justificación Metodológica y Regla de Exclusión |
| :--- | :---: | :---: | :--- |
| **1. Archivo crudo descargado** (`owid_covid_kenya_raw.csv`) | **1,674 filas** | 2020-01-05 a 2024-08-04 | Extracción íntegra sin filtros del archivo global OWID para el código ISO `KEN`. |
| **2. Exclusión de período pre-epidémico** | **-68 filas** | 2020-01-05 a 2020-03-12 | Días previos a la detección oficial del primer caso confirmado de COVID-19 en Kenia (13 de marzo de 2020). Todos los registros tenían 0 casos. |
| **3. Ingesta oficial en Base de Datos** (`dataset_observations`) | **1,606 filas** | 2020-03-13 a 2024-08-04 | Período epidémico y post-emergencia activo sincronizado en la base de datos relacional SQLite (`county_code = 0`). |
| **4. Exclusión de buffer de rezagos causales diarios** | **-14 filas** | 2020-03-13 a 2020-03-26 | Primeros 14 días requeridos para construir los rezagos `lag_14` y `rolling_mean_14` sin introducir imputaciones ficticias. |
| **5. Conjunto para modelado diario** (Train + Val + Test) | **1,592 filas** | 2020-03-27 a 2024-08-04 | Partición: Train (826) + Val (274) + Test (492) = **1,592 días**. |
| **6. Agregación canónica semanal** (Semanas Epidemiológicas) | **230 semanas** | 2020-03-15 a 2024-08-04 | Reagrupación por semanas epidemiológicas cerradas en domingo (`W-SUN`). |
| **7. Exclusión buffer semanal (4 semanas)** | **-4 semanas** | 2020-03-15 a 2020-04-05 | Buffer para rezagos semanales (`weekly_lag_4`, `weekly_rolling_mean_4`). |
| **8. Conjunto total para modelado semanal canónico** | **226 semanas** | 2020-04-12 a 2024-08-04 | Partición: Desarrollo (155 semanas) + Test Reservado (71 semanas) = **226 semanas**. |

---

## 4. Partición Cronológica sin Fuga de Información (Hold-out Temporal)

Para garantizar la causalidad y evitar cualquier filtración de información (*data leakage*):
- **Conjunto de Desarrollo (Train + Val)**: **155 semanas** (2020-04-12 a 2023-03-26).
  - Train: 116 semanas (2020-04-12 a 2022-06-26) $\rightarrow$ Olas epidémicas agudas (Alpha, Beta, Delta, Ómicron).
  - Validation: 39 semanas (2022-07-03 a 2023-03-26) $\rightarrow$ Transición post-emergencia utilizada para calibración de hiperparámetros.
- **Conjunto de Prueba Reservado (Hold-out Test)**: **71 semanas** (2023-04-02 a 2024-08-04). Período completamente independiente, **nunca utilizado para entrenar ni para seleccionar modelos**.
- **Aislamiento de Transformadores**:
  - `SimpleImputer(strategy='median')` y `StandardScaler()` se ajustaron (`fit`) **única y exclusivamente sobre el subconjunto de entrenamiento de desarrollo** y se aplicaron (`transform`) e### 5.1 Definición de Criterios de Selección

Para cumplir con la máxima rigurosidad científica y metodológica (CRISP-DM), se definieron dos criterios formales con objetivos explícitos:

1. **Criterio Predictivo Puro (Mínimo RMSE en TimeSeriesSplit CV sobre Desarrollo)**:
   - Se evalúa el RMSE promedio en `TimeSeriesSplit(n_splits=5)` **exclusivamente sobre el conjunto de desarrollo (155 semanas)**.
   - **Baseline Naive Persistence** obtuvo el menor error en desarrollo (CV RMSE = **1,183.64** casos/semana) y se seleccionó como la **Campeona Predictiva Oficial antes de evaluar en el conjunto de prueba**.
   - **Aclaración Metodológica sobre Ridge**: En el conjunto de test reservado, **Baseline Ridge Regression** obtuvo el menor RMSE (**49.37** casos/semana frente a 55.64 de Naive). Sin embargo, para respetar el protocolo ciego y evitar el sesgo de selección post-hoc (*data snooping* / fuga de información del test set), **Ridge no fue elegida como campeona**: la selección quedó formalmente sellada con los datos de desarrollo.

2. **Criterio de Exploración Hipotética de Sensibilidad**:
   - La persistencia ingenua carece de variables explicativas: su sensibilidad ante covariables externas es nula.
   - Se seleccionó el mejor modelo multivariado en desarrollo, **Candidate Random Forest** (CV RMSE Desarrollo = **1,345.87** casos/semana), para posibilitar una **exploración hipotética de sensibilidad condicional**.
   - **ADVERTENCIA CIENTÍFICA CRÍTICA**:
     * La sensibilidad de una predicción a `stringency_index` es una asociación estadística observacional y **NO prueba un efecto causal de una intervención sanitaria**.
     * **No debe presentarse como modelo contrafactual validado ni como estimador del efecto de políticas públicas**.
     * Límites: No modela endogeneidad de las intervenciones, no controla factores de confusión no observados ni reproduce las dinámicas biológicas mecanicistas de transmisión.
     * Disponibilidad: El índice de Oxford cesó su recolección el 31/12/2022 (100% de datos ausentes post-2022 en datos crudos). Si se mantiene en la interfaz, se rotula como «exploración hipotética de sensibilidad».

### 5.2 Tabla de Resultados de Ejecución Real (Tarea Canónica Semanal)

> [!IMPORTANT]
> Todas las cifras provienen de la ejecución real y reproducible de `scripts/train_and_evaluate_models.py`. Ningún dato fue modificado.

| Modelo Evaluado | CV RMSE Desarrollo (5-fold) | Test RMSE (casos/sem) | Test MAE (casos/sem) | Test MAPE (%) | Test $R^2$ | Tiempo Ajuste (s) | Selección y Rol Metodológico |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Baseline Naive Persistence** | **1,183.64** | **55.64** | **19.23** | 515.49% | -0.4203 | 0.004 s | **Champion Predictivo Oficial (Mínimo CV RMSE Desarrollo)** |
| **Baseline Ridge Regression** | 1,405.93 | **49.37** | **16.04** | **43.66%** | **-0.1181** | 3.225 s | Benchmark Test (Mínimo RMSE en Test, no seleccionado a priori) |
| **Candidate Random Forest** | **1,345.87** | 81.72 | 74.05 | 5,045.49% | -2.0638 | 7.403 s | **Exploración Hipotética de Sensibilidad** |
| **Candidate HistGradientBoosting** | 2,041.78 | 74.09 | 63.27 | 4,280.72% | -1.5179 | 2.111 s | Comparativo No Lineal |

### 5.3 Veredicto de Selección y Desempeño:
- **Selección A Priori**: **Baseline Naive Persistence es la campeona predictiva** (CV RMSE = 1,183.64 casos/semana), superando a todos los modelos de Machine Learning en desarrollo y registrando un MAE de 19.23 casos/semana en Test.
- **Desempeño en Test Reservado**: **Baseline Ridge Regression** obtuvo el menor error cuadrático en test (RMSE = 49.37), superando a Naive (55.64) y a Random Forest (81.72). Se reporta con transparencia como benchmark sin alterar la decisión tomada en desarrollo.
- **Exploración de Sensibilidad**: **Candidate Random Forest** se utiliza exclusivamente para explorar la sensibilidad condicional ante covariables, reconociendo que en la fase endémica plana de 2023–2024 sobrestima la varianza residual debido a la ausencia de datos observados del índice Oxford.

---

## 6. Pruebas Bioestadísticas Formales y Control de Dependencia Temporal

### 6.1 Comparación Directa de Errores Observados en el Test Set (N = 71 semanas)
- **Baseline Naive Persistence**: MAE = **19.23** casos/semana | RMSE = **55.64** casos/semana
- **Baseline Ridge Regression**: MAE = **16.04** casos/semana | RMSE = **49.37** casos/semana
- **Candidate Random Forest**: MAE = **74.05** casos/semana | RMSE = **81.72** casos/semana
- **Candidate HistGradientBoosting**: MAE = **63.27** casos/semana | RMSE = **74.09** casos/semana

### 6.2 Test de Normalidad de Shapiro-Wilk
- **Variable Evaluada**: Diferencia de pérdidas pareadas en Test: $d_t = |y_t - \hat{y}_t^{\text{Naive}}| - |y_t - \hat{y}_t^{\text{RandomForest}}|$.
- **Estadístico $W$**: $0.6887$
- **p-value**: $5.5341 \times 10^{-11}$ ($p < 0.0001$)
- **Conclusión**: Se rechaza la hipótesis de normalidad ($p < 0.05$). Justifica formalmente el empleo de pruebas no paramétricas y métodos robustos para series de tiempo.

### 6.3 Test de Rangos con Signo de Wilcoxon Pareado (Test Set, N = 71 semanas)
- **Hipótesis**:
  - $H_0: \tilde{d} = 0$ (la mediana de las diferencias de pérdida pareada es cero).
  - $H_1$ Bilateral: $\tilde{d} \neq 0$ (las distribuciones de error difieren significativamente).
  - $H_1$ Unilateral: $\tilde{d} > 0$ (el error de la persistencia es mayor que el error del Random Forest).
- **Estadístico $W$**: $132.5$
- **p-value Bilateral**: $3.9975 \times 10^{-11}$ ($p < 0.0001$)
- **p-value Unilateral**: $1.0000$ ($p \ge 0.05$)
- **Interpretación Bioestadística Exacta**:
  - El resultado $p = 1.0000$ en la prueba unilateral **NO demuestra por sí solo la superioridad de la persistencia**. Estadísticamente indica un fallo completo en rechazar $H_0$ en la dirección evaluada (no existe ninguna evidencia muestral de que la persistencia tenga mayor error que el Random Forest).
  - La superioridad observada de la persistencia frente al Random Forest en la fase endémica se fundamenta en la **comparación de los errores absolutos observados (MAE: 19.23 vs 74.05)** y en el **rechazo bilateral de igualdad distributiva ($p < 0.0001$)**, no en el valor $p = 1.0000$ en sí mismo.

### 6.4 Test de Diebold-Mariano (1995) con Corrección Harvey-Leybourne-Newbold (HLN 1997)
Para controlar formalmente la **autocorrelación serial de los errores de pronóstico**:
- **Diferencia media de pérdidas (MAE)**: $\bar{d} = -54.83$ casos/semana (favorable a la persistencia).
- **Estadístico $DM^*$ modificado**: $-14.3240$
- **p-value Bilateral**: **$p < 0.0001$** ($1.22 \times 10^{-21}$)
- **Conclusión**: Al estimar la varianza asintótica de largo plazo mediante el estimador consistente con heterocedasticidad y autocorrelación (HAC Bartlett) con corrección para muestra finita, Diebold-Mariano confirma que **la diferencia de pérdidas entre la persistencia y el Random Forest es estadísticamente significativa ($p < 0.0001$)**, ratificando la ventaja de precisión de la persistencia en la cola endémica post-emergencia.

### 6.5 Clarificación Metodológica del Test de Kolmogorov-Smirnov
- **Estadístico KS**: $0.8592$ | **p-value**: **$p < 0.0001$** ($3.57 \times 10^{-27}$).
- **Aclaración**: El test KS de 2 muestras únicamente evalúa si las funciones de distribución acumulada de los errores $F(e_{\text{Naive}})$ y $F(e_{\text{RF}})$ son diferentes. **En ningún caso demuestra que un modelo sea superior o mejor predictor que otro**, únicamente valida que operan bajo dinámicas estocásticas distintas.

---

## 7. Alcance Nacional vs Articulación con los 47 Condados

> [!WARNING]
> **Aclaración de Alcance Territorial**: El modelo de Machine Learning entrenado (`champion_covid_model_v1.0.joblib`) opera a **Nivel Nacional Agregado** (`county_code = 0`, `NATIONAL_DAILY` / `NATIONAL_WEEKLY`), reflejando la cobertura del dataset oficial de Kenia de OWID/OMS.

### Comportamiento Definido para la Interfaz en la Fase 2:
Cuando el usuario interactúe con el mapa o panel de control:
1. **Selección Nacional (`county_code = 0` / Kenya)**:
   - Despliega las proyecciones del modelo (`champion_covid_model_v1.0.joblib`) y la persistencia de referencia.
   - Habilita el control deslizante como **«Exploración Hipotética de Sensibilidad»** (`stringency_index` de 0 a 100), advirtiendo expresamente que no evalúa causalidad y que el índice observado cesó en 2022.
2. **Selección de un Condado Específico (`county_code = 1..47`)**:
   - Muestra los datos estructurales y hospitalarios verificados del condado (Población Censo KNBS 2019, camas UCI KMFL, quintiles socioeconómicos KDHS 2022).
   - Ejecuta el **Gemelo Digital Mecanicista Territorial (`SpatialSEIR` + `HouseholdABM`)**, el cual sí modela la interacción espacial y movilidad metapoblacional entre los 47 condados.
   - Si se solicita proyectar casos a nivel condal a partir del modelo estadístico nacional, se aplicará una desagregación ponderada demográficamente ($w_c = \text{Población}_c / \text{Población}_{\text{Nacional}}$) con la advertencia explícita en pantalla:
     > *"Proyección condal estimada por prorrateo demográfico nacional. No constituye microdatos de vigilancia condal. Para dinámicas epidemiológicas territoriales autónomas, consulte el motor SEIR Espacial."*

---

## 8. Disponibilidad de Entradas, Valores Faltantes e Inferencia en Tiempo Real

### 8.1 Horizonte de Pronóstico
- **Horizonte Oficial**: **1 semana hacia adelante ($t+1$ semana)**.

### 8.2 Auditoría de Disponibilidad y Valores Faltantes (11 Características Semanales)
Se auditó la presencia de valores faltantes tanto en la serie cruda como en el conjunto de prueba (2023-04-01 a 2024-08-04, 71 semanas / 492 días) y al momento de inferir:

| Variable Predictora | Faltantes en Test Crudo | Faltantes en Inferencia | Estado de Disponibilidad al Momento de Inferir ($t$) | ¿Depende de Información Futura? |
| :--- | :---: | :---: | :--- | :---: |
| `weekly_lag_1` a `weekly_lag_4` | **0.0%** (0/492) | **0.0%** | Conocidos al cierre del domingo previo ($t-1, t-2, \dots$) desde reporte OMS/MoH. | **NO** |
| `weekly_rolling_mean_4`, `weekly_rolling_std_4` | **0.0%** (0/492) | **0.0%** | Calculados endógenamente sobre las 4 semanas previas. | **NO** |
| `weekly_deaths_lag_1`, `weekly_deaths_lag_2` | **0.0%** (0/492) | **0.0%** | Registrados en el reporte dominical de la semana previa. | **NO** |
| `month` | **0.0%** (0/492) | **0.0%** | Mes calendario (determinista, conocido a priori). | **NO** |
| `stringency_lag_1` | **100.0%** (492/492) | **100.0%** ausente | **DESCONTINUADA POST-2022**. Oxford OxCGRT cesó el 31/12/2022. En inferencia se fija por el usuario como valor hipotético de sensibilidad o se imputa el último observado. | **NO** |
| `reproduction_rate_lag_1` | **100.0%** (492/492) | **100.0%** ausente | **DESCONTINUADA POST-2022**. Estimación cesó en enero 2023. Se ingresa como valor de referencia o imputación. | **NO** |

---

## 9. Información para la Fase 2

### 9.1 Rutas de Artefactos y Datos
- **Dataset Crudo**: `data/raw/owid_covid_kenya_raw.csv` (SHA-256: `c82f3cfc5899b25557f3bf69de987dc9628bfa6fbbee55cd77b649c9d34cd2ba`).
- **Metadatos de Procedencia**: `data/raw/dataset_metadata.json`.
- **Datasets Semanales Procesados**:
  - `data/processed/kenya_covid_weekly_train.csv` (116 semanas)
  - `data/processed/kenya_covid_weekly_val.csv` (39 semanas)
  - `data/processed/kenya_covid_weekly_test.csv` (71 semanas)
  - `data/processed/feature_metadata.json` (Especificación completa de características y conciliación).
- **Modelo Serializado para Exploración de Sensibilidad**: `models/champion_covid_model_v1.0.joblib` (SHA-256: `2de57bc99863c085902f12df0e86886aa8ccde738669334d7d58df3de4deb8d2`).
- **Ficha de Gobernanza**: `models/champion_covid_model_v1.0.json` (SHA-256: `c00a60bce6b7723e0e58a6df9281b7af5d7beacd8ff0816fb96a59597d040eb2`).
- **Base de Datos**: `epidemic_twin.db` con 1,606 registros en `dataset_observations` (`dataset_id = 'ds-owid-covid-kenya'`).

### 9.2 Verificación de Inferencia Limpia desde Proceso Independiente
Se construyó y ejecutó el script `scripts/predict_weekly.py`, el cual carga el modelo serializado en un proceso de Python completamente aislado y valida la inferencia semanal ($t+1$):

```powershell
.\.venv\Scripts\python.exe scripts/predict_weekly.py --date 2024-07-28
```

**Entradas Utilizadas (Corte 2024-07-28)**:
- `weekly_lag_1`: `1.0` (casos semana previa)
- `weekly_lag_2`: `0.0`
- `weekly_lag_3`: `0.0`
- `weekly_lag_4`: `0.0`
- `weekly_rolling_mean_4`: `0.25`
- `weekly_rolling_std_4`: `0.50`
- `weekly_deaths_lag_1`: `0.0`
- `weekly_deaths_lag_2`: `0.0`
- `stringency_lag_1`: `22.77` (control hipotético; 100% ausente en datos crudos)
- `reproduction_rate_lag_1`: `0.54` (control referencial; 100% ausente en datos crudos)
- `month`: `7.0` (julio)

**Salida Real Obtenida**:
- **Fecha de corte ($t_0$)**: `2024-07-28`
- **Horizonte de pronóstico ($t+1$)**: `2024-08-04` (1 semana hacia adelante)
- **Predicción generada**: **70.76 casos/semana**
- **Casos reales observados en $t+1$**: `0 casos`
- **Proyección de Naive Persistence**: `1 casos` (Error absoluto Naive: 1.00 vs Error absoluto RF: 70.76)

### 9.3 Decisiones Metodológicas Mandatarias para la Interfaz (Fase 2):
1. **No Atribución de Causalidad**: El control deslizante de `stringency_index` debe estar titulado exclusivamente como **«Exploración Hipotética de Sensibilidad»**. Bajo ninguna circunstancia debe denominarse "Simulación Contrafactual de Políticas" o "Estimador de Efecto de Políticas".
2. **Advertencia de Descontinuación de Datos**: La interfaz debe exhibir un indicador visible que advierta al usuario que el índice de rigor Oxford cesó en diciembre de 2022 y que su valor actual es un parámetro hipotético fijado por el usuario.
3. **Separación Estricta Territorial**: La predicción de Machine Learning es estrictamente nacional (`KEN`). No debe presentarse en el mapa como si fueran observaciones locales de los 47 condados. Cualquier desagregación debe indicar expresamente su condición de prorrateo demográfico o remitir al modelo mecanicista `SpatialSEIR`.

---

## 10. Puntos que No Pudieron ser Comprobados

En estricto apego a la transparencia académica exigida:
1. **Microdatos Subnacionales Desagregados por los 47 Condados**: El dataset público internacional de OWID/OMS contiene únicamente la serie temporal consolidada a nivel nacional (`KEN`). No incluye series temporales diarias ni semanales independientes para cada uno de los 47 condados de Kenia (los cuales solo se encuentran en reportes situacionales no estructurados en PDF del Ministerio de Salud de Kenia). Por tanto, **el modelo predictivo entrenado es de escala nacional**, y cualquier desagregación condal en la fase 2 se realizará mediante ponderación demográfica o a través del motor SEIR espacial.
2. **Validación Externa Independiente Fuera de Muestra 2023–2024 con Microdatos MOH**: Permanece oficialmente en estado `PENDING` en el sistema (`ExternalValidationManager`), ya que no se dispone de microdatos clínicos individuales del Ministerio de Salud de Kenia.
3. **Disponibilidad Empírica del Índice de Rigor de Oxford y Rt Post-2022**: Oxford Blavatnik School cesó la recolección periódica del *Stringency Index* el 31 de diciembre de 2022 (100% de datos faltantes en el periodo post-2022 en datos crudos). Por tanto, no puede comprobarse empíricamente su impacto en el periodo 2023–2024, quedando restringido a una herramienta de exploración hipotética de sensibilidad.
