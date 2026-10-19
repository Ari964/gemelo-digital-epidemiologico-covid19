# Artículo Científico del Proyecto: Gemelo Digital Epidemiológico para Vigilancia Semanal y Evaluación de Escenarios de Respuesta ante COVID-19 en Kenia

> **Aviso de Formato Institucional:** En el repositorio actual del proyecto (`GD_TI`) **solo existe este borrador formal en formato Markdown (`docs/ARTICULO_CIENTIFICO_PROYECTO.md`)**. No se incluye ningún archivo propietario `.docx` ni `.pdf` en este directorio. Este documento constituye el manuscrito científico definitivo y fuente de verdad técnica, alineado con el pipeline semanal aprobado al cierre de la Fase 1 y desplegado en la Fase 2.

---

**Autores:** Equipo de Investigación de Gemelos Digitales Epidemiológicos  
**Afiliación:** Facultad de Ingeniería de Sistemas e Informática / Departamento Académico de Computación  
**Línea de Investigación:** Modelado Computacional, Gemelos Digitales en Salud Pública e Inteligencia Artificial Aplicada  
**Fecha de Actualización:** 23 de septiembre de 2026  

---

## Resumen

Los gemelos digitales epidemiológicos constituyen herramientas avanzadas para la anticipación y toma de decisiones sanitarias. Sin embargo, su traslación a entornos con recursos limitados suele enfrentar desafíos críticos de fidelidad de datos, periodicidad de reporte y sobreajuste algorítmico. En este trabajo, desarrollamos y auditamos un gemelo digital epidemiológico de nivel poblacional para Kenia enfocado en la vigilancia de COVID-19 a escala nacional (código ISO `KEN`, ámbito nacional agregado, `county_code = 0`) articulado con la infraestructura hospitalaria de los 47 condados de Kenia (Censo KNBS 2019). Analizamos la serie temporal oficial completa de Our World in Data / Organización Mundial de la Salud (OMS), comprendida entre el 15 de marzo de 2020 y el 04 de agosto de 2024 (1,606 observaciones diarias observadas, consolidadas en 230 semanas epidemiológicas agregadas de corte dominical; 226 semanas modeladas tras descontar el búfer inicial de 4 rezagos autorregresivos).

Demostramos empíricamente que el 100% de los reportes positivos en la serie oficial ocurren en lotes semanales dominicales, lo que invalida el modelado autorregresivo a paso diario continuo y establece la predicción de incidencia semanal ($\hat{y}_{t+1}$) como la tarea formal de vigilancia. Mediante un protocolo de partición temporal estricto (conjunto de desarrollo 2020–2023 con 155 semanas —116 de entrenamiento y 39 de validación— y conjunto de prueba reservado post-marzo 2023 con 71 semanas), evaluamos los modelos mediante validación cruzada con origen rodante (TimeSeriesSplit, 5 folds sobre las 155 semanas de desarrollo). El criterio de selección *ex-ante* sobre el conjunto de desarrollo determinó la superioridad del modelo de persistencia ingenua (*Baseline Naive Persistence*, $\hat{y}_{t+1} = y_t$), el cual obtuvo un RMSE de validación cruzada de **1,183.64 casos/semana**, superando al Random Forest (**1,345.87 casos/semana**), a la Regresión Ridge (**1,405.93 casos/semana**) y a HistGradientBoosting (**2,041.78 casos/semana**).

En el conjunto de prueba reservado (71 semanas: 02 de abril de 2023 a 04 de agosto de 2024) —caracterizado por una marcada fase endémica con baja transmisión y alta dispersión de ceros—, la persistencia ratificó su liderazgo frente a los ensambles multivariados con un RMSE de **55.64 casos/semana** y un MAE de **19.23 casos/semana**, frente a un RMSE de **81.72 casos/semana** y MAE de **74.05 casos/semana** de Random Forest. Aunque la Regresión Ridge obtuvo un RMSE menor en test (49.37 casos/semana, MAE 16.04), se reporta transparentemente como benchmark no seleccionado ex-ante para preservar la regla metodológica contra el sesgo de selección posterior (*data snooping*). El contraste de Diebold–Mariano corroboró la significancia estadística del menor error de la persistencia frente a Random Forest ($DM^* = -14.324$, $p < 0.0001$). Asimismo, advertimos que las variables exógenas (`stringency_index` de Oxford y tasa de reproducción $R_t$) cesaron su publicación tras diciembre de 2022, requiriendo imputación constante (22.77 y 0.54) para inferencia; en consecuencia, Random Forest queda categorizado estrictamente como una herramienta de «exploración hipotética de sensibilidad» y no como un evaluador contrafactual causal. El sistema integra un Asistente de Datos del Gemelo Digital con separación factual estricta entre observaciones de base de datos, pronósticos estadísticos y texto generado por IA.

**Palabras clave:** Gemelo Digital, Vigilancia Epidemiológica, Persistencia Ingenua, Random Forest, COVID-19 Kenia, CRISP-DM, Dispersión Temporal, Evaluación No Causal.

---

## 1. Introducción

La pandemia de COVID-19 demandó sistemas analíticos capaces de anticipar la saturación de los sistemas de salud pública y simular intervenciones no farmacéuticas (NPIs). Los gemelos digitales se han posicionado como una tecnología prometedora para este propósito al prometer una réplica computacional de la dinámica poblacional. No obstante, una debilidad recurrente en la literatura es la asunción de flujos de datos ideales continuos o el reporte de métricas engañosas derivadas de modelos sobreparametrizados que ignoran la dinámica real de los sistemas de reporte epidemiológico.

En países de ingresos bajos y medios como Kenia, la notificación de contagios no se efectúa mediante telemetría en tiempo real o sensores IoT, sino mediante la consolidación periódica de pruebas moleculares PCR y de antígenos que el Ministerio de Salud (MoH) centraliza semanalmente ante la Organización Mundial de la Salud (OMS). Cuando estos datos se analizan sin rigor metodológico, algoritmos complejos como ensambles de árboles de decisión (Random Forest) tienden a memorizar el régimen epidémico de alta incidencia (2020–2021) y fallan severamente en regímenes de transición endémica o baja notificación (2023–2024).

El presente artículo documenta el desarrollo, entrenamiento, auditoría y despliegue del componente de modelado y vigilancia del Gemelo Digital Epidemiológico de Kenia bajo el marco metodológico CRISP-DM (Cross-Industry Standard Process for Data Mining). Los objetivos específicos de esta investigación son:
1. Auditar la naturaleza y periodicidad del dataset oficial de Kenia para definir una tarea de predicción epidemiológicamente fundada y reproducible.
2. Formular un protocolo de evaluación temporal estricto (Rolling-Origin Cross-Validation) que seleccione el modelo campeón utilizando exclusivamente datos del conjunto de desarrollo.
3. Evaluar el desempeño comparativo entre modelos lineales, no lineales (Random Forest) y baselines estadísticos (Persistencia Ingenua), contrastando su robustez ante cambios estructurales de régimen.
4. Formalizar las limitaciones epistemológicas del modelo multivariado, delimitando las intervenciones no farmacéuticas a una exploración hipotética de sensibilidad sin atribuir causalidad empírica.
5. Integrar la inferencia en un asistente de datos explicable que separe taxativamente observaciones empíricas, pronósticos matemáticos y resúmenes de inteligencia artificial.

---

## 2. Metodología

### 2.1 Fuente de Datos y Alcance Geográfico

La serie temporal epidemiológica nacional fue obtenida del repositorio público y consolidado de **Our World in Data (OWID)** en colaboración con la Universidad de Oxford y la OMS (licencia CC BY 4.0).
- **Cobertura Temporal:** 15 de marzo de 2020 al 04 de agosto de 2024.
- **Volumen Total:** 1,606 registros diarios observados en la base relacional del proyecto (`epidemic_twin.db`).
- **Ámbito Geográfico:** Exclusivamente Nacional (código ISO `KEN`, `location = 'Kenya'`, `county_code = 0`). Las series temporales oficiales de la OMS/OWID no proveen desagregación subnacional por condados. La heterogeneidad territorial de los 47 condados se articula en el gemelo digital mediante la base estructural estática del Censo KNBS 2019 (población, pirámide demográfica, quintiles de pobreza KDHS 2022 y capacidad hospitalaria de camas y UCI del Kenya Master Health Facility List).

### 2.2 Auditoría de Frecuencia Temporal y Definición de la Variable Objetivo

El análisis exploratorio forense evidenció que el 100% de los valores positivos de la columna `new_cases` se registraron exclusivamente en días domingo (reporte acumulado en bloque semanal). Los días de lunes a sábado registran estrictamente cero casos debido a la política de consolidación semanal del Ministerio de Salud. La variable `new_cases_smoothed` reportada por OWID divide el total dominical entre 7 y lo replica uniformemente.

En consecuencia, se transformó la serie a una **frecuencia semanal canónica** con corte dominical ($t_0$), donde:
- $\text{weekly\_lag\_1} = \sum_{\tau \in \text{semana}} \text{casos}(\tau)$: representa el total de casos confirmados durante la semana que concluye en el domingo de corte $t_0$.
- La variable objetivo formal es el total de casos positivos de la semana posterior:
  $$y_{t+1} = \text{target\_weekly\_cases} = \text{casos}(t_0 + 7\text{ días})$$
La serie consolidada cuenta con 230 semanas epidemiológicas agregadas. Al requerir 4 semanas previas de retardo autorregresivo (`weekly_lag_1` a `weekly_lag_4`, media y desviación estándar móvil de 4 semanas), el conjunto modelado efectivo comprende $N = 226$ semanas.

### 2.3 Partición Temporal sin Filtración (Data Leakage)

Siguiendo el estándar epidemiológico, la serie se particionó cronológicamente en tres subconjuntos sin traslape:
1. **Conjunto de Entrenamiento (Train Set):** 116 semanas (12 de abril de 2020 a 26 de junio de 2022).
2. **Conjunto de Validación Temporal (Val Set):** 39 semanas (03 de julio de 2022 a 26 de marzo de 2023).
   - *Conjunto de Desarrollo Consolidado (Train + Val):* 155 semanas (2020-04-12 a 2023-03-26).
3. **Conjunto de Prueba Reservado (Test Set):** 71 semanas (02 de abril de 2023 a 04 de agosto de 2024).

### 2.4 Modelos Evaluados

Se formularon cuatro enfoques competitivos:
1. **Baseline de Persistencia Ingenua (*Naive Persistence*):**  
   $$\hat{y}_{t+1} = y_t = \text{weekly\_lag\_1}$$
   Asume que el volumen de contagios de la próxima semana replicará el del último corte dominical observado.
2. **Baseline de Regresión Ridge ($L_2$ Regularized Linear Model):**  
   Modelo lineal regularizado con estandarización previa de características autorregresivas y de movilidad.
3. **Candidate Random Forest Regressor (Ensamble No Lineal):**  
   Conjunto de 100 árboles de decisión (`n_estimators=100`, `max_depth=5`, `random_state=42`) entrenado sobre retardos (`weekly_lag_1` a `weekly_lag_4`), estadísticas rodantes de 4 semanas, defunciones previas, `stringency_index`, `reproduction_rate` y variable estacional `month`.
4. **Candidate HistGradientBoosting Regressor:**  
   Ensamble basado en histogramas para gradiente descendente sobre árboles de decisión.

### 2.5 Criterio de Selección y Pruebas Estadísticas

Para evitar sesgos de optimismo y *data leakage*, el modelo campeón predictivo fue seleccionado **antes** de consultar el conjunto de prueba reservado, utilizando el Error Cuadrático Medio (RMSE) obtenido en una **Validación Cruzada con Origen Rodante (TimeSeriesSplit, 5 folds)** sobre las 155 semanas de desarrollo.

Para contrastar el comportamiento de las pérdidas en el conjunto de prueba reservado, se aplicaron:
- **Test de Shapiro–Wilk:** Evaluación de normalidad sobre las diferencias pareadas de pérdida ($e_1^2 - e_2^2$).
- **Test de Diebold–Mariano con corrección de Harvey, Leybourne y Newbold (HLN 1997):** Compara las trayectorias de pérdida de pronósticos competitivos en series temporales con autocovarianza residual.
- **Test de Rangos Signados de Wilcoxon:** Evaluación no paramétrica sobre errores absolutos pareados.
- **Test de Kolmogorov–Smirnov:** Prueba no paramétrica de dos muestras sobre la distribución acumulada de residuos.

---

## 3. Resultados Experimentales

### 3.1 Desempeño en Validación Cruzada (Conjunto de Desarrollo: 155 semanas)

La Tabla 1 resume los resultados de la validación cruzada con origen rodante de 5 pliegues aplicada exclusivamente sobre el conjunto de desarrollo (155 semanas: 2020-04-12 a 2023-03-26).

**Tabla 1. Evaluación de Modelos en el Conjunto de Desarrollo (CV TimeSeriesSplit 5-Fold)**
| Modelo | CV RMSE (casos/semana) | Rol Metodológico | Criterio de Selección |
| :--- | :---: | :---: | :---: |
| **Baseline_Naive_Persistence** | **1,183.64** | Baseline Canónico | **Seleccionado Campeón Ex-Ante** |
| Candidate_Random_Forest | 1,345.87 | Ensamble Multivariado | Descartado como predictor principal; retenido para sensibilidad |
| Baseline_Ridge_Regression | 1,405.93 | Modelo Lineal $L_2$ | Descartado |
| Candidate_HistGradientBoosting | 2,041.78 | Ensamble Boosting | Descartado |

Bajo el criterio predefinido de mínimo RMSE en validación cruzada, el modelo **Baseline_Naive_Persistence** resultó seleccionado inequívocamente como el modelo campeón oficial para la predicción de vigilancia epidemiológica semanal.

### 3.2 Evaluación en el Conjunto de Prueba Reservado (Test: 71 semanas)

Una vez congelada la arquitectura y seleccionado el modelo campeón, se evaluaron los modelos sobre las 71 semanas del conjunto de prueba reservado (02 de abril de 2023 a 04 de agosto de 2024). Los resultados cuantitativos se exponen en la Tabla 2.

**Tabla 2. Métricas de Rendimiento en el Conjunto de Prueba Reservado (71 semanas holdout)**
| Modelo | RMSE (casos/sem) | MAE (casos/sem) | MAPE (%) | R² Score | Observación Metodológica |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Baseline_Naive_Persistence** | **55.64** | **19.23** | **515.49%** | **-0.4203** | **Modelo Campeón Oficial en Producción** |
| Baseline_Ridge_Regression | 49.37 | 16.04 | 43.66% | -0.1181 | Benchmark ex-post; no seleccionado para evitar data snooping |
| Candidate_HistGradientBoosting | 74.09 | 63.27 | 4280.72% | -1.5179 | Degradación severa por pisos residuales en baja transmisión |
| Candidate_Random_Forest | 81.72 | 74.05 | 5045.49% | -2.0638 | Retenido para Exploración Hipotética de Sensibilidad |

La Persistencia Ingenua superó holgadamente al ensamble multivariado Random Forest tanto en RMSE (55.64 vs 81.72 casos/semana) como en MAE (19.23 vs 74.05 casos/semana). Random Forest acumuló un MAE casi 4 veces superior al del baseline simple. Asimismo, se reconoce de manera transparente que la Regresión Ridge obtuvo el menor RMSE en el conjunto de prueba reservado (49.37 casos/semana, con MAE de 16.04), comportándose como un benchmark competitivo ex-post. No obstante, la persistencia se mantuvo como el modelo oficial de vigilancia epidemiológica en producción porque fue seleccionada ex-ante bajo el criterio metodológico predefinido de mínimo RMSE en validación temporal cruzada sobre las 155 semanas de desarrollo (1,183.64 vs 1,405.93 de Ridge y 1,345.87 de Random Forest). Reemplazar el modelo campeón tras observar los datos de prueba constituiría una práctica viciada de *data snooping*.

### 3.3 Significancia Estadística y Pruebas Biostatísticas

Para contrastar formalmente si las diferencias de precisión predictiva entre el modelo oficial (**Baseline Naive Persistence**) y el ensamble multivariado (**Candidate Random Forest**) son estadísticamente significativas sobre las 71 semanas del conjunto de prueba reservado, se evaluaron las siguientes pruebas de hipótesis:

1. **Test de Shapiro–Wilk sobre Diferencias de Pérdida Pareada:**  
   - *Modelos y variable evaluada:* Serie de diferencias de pérdida absoluta $d_t = |e_{t, \text{Naive}}| - |e_{t, \text{RF}}|$ ($N=71$).
   - *Hipótesis:* $H_0$: Las diferencias de pérdida siguen una distribución normal.
   - *Resultado:* Estadístico $W = 0.6887$, $p = 5.53 \times 10^{-11}$. Se rechaza rotundamente la normalidad, invalidando los supuestos de una prueba paramétrica $t$ de Student pareada y exigiendo contrastes robustos ante asimetría y autocorrelación.
2. **Test de Diebold–Mariano con Corrección de Harvey, Leybourne y Newbold (HLN 1997):**  
   - *Modelos y variable evaluada:* Pérdidas absolutas pareadas $|e_{t, \text{Naive}}|$ frente a $|e_{t, \text{RF}}|$ con corrección de autocorrelación serial de orden $h-1 = 0$ (horizonte de 1 semana).
   - *Hipótesis:* $H_0: E[d_t] = 0$ (igual precisión predictiva media) frente a la alternativa bilateral $H_1: E[d_t] \neq 0$.
   - *Resultado:* Diferencia media de pérdida $\bar{d} = -54.826$ casos/semana (favorable a la persistencia), con estadístico corregido $DM^* = -14.324$ y valor $p < 0.0001$. Se rechaza con alta significancia la hipótesis nula de igual exactitud, confirmando la superioridad de la persistencia frente a Random Forest.
3. **Test de Rangos Signados de Wilcoxon Pareado:**  
   - *Modelos y variable evaluada:* Errores absolutos $|e_{t, \text{Naive}}|$ frente a $|e_{t, \text{RF}}|$ ($N=71$).
   - *Hipótesis evaluada:* $H_0$: La mediana de las diferencias de error absoluto es cero ($\text{mediana}(|e_{\text{Naive}}| - |e_{\text{RF}}|) = 0$).
   - *Resultado:* Estadístico $W = 132.5$, valor $p$ bilateral $p = 4.04 \times 10^{-11} < 0.0001$. Se rechaza la equivalencia de medianas, demostrando distribuciones de error disímiles. En una formulación unilateral con hipótesis alternativa $H_1: \text{error}_{\text{Naive}} > \text{error}_{\text{RF}}$, el valor obtenido es $p = 1.0000$, lo cual matemáticamente solo indica que no existe evidencia alguna de que la persistencia cometa mayor error que Random Forest; dicho valor $p=1.0000$ no se utiliza para inferir superioridad inversa por sí solo. La dirección favorable a la persistencia se fundamenta en su MAE marcadamente inferior (19.23 vs 74.05 casos/semana) y el signo negativo del estadístico Diebold-Mariano.
4. **Test de Kolmogorov–Smirnov para Dos Muestras:**  
   - *Modelos y variable evaluada:* Funciones de distribución empírica acumulada de los residuos absolutos $F_{|e_{\text{Naive}}|}(x)$ y $F_{|e_{\text{RF}}|}(x)$.
   - *Resultado:* Estadístico $KS = 0.8592$, $p < 0.0001$, confirmando que los perfiles de error poblacional provienen de distribuciones distintas.

### 3.4 Inferencia Multi-Periodo y Análisis Forense de Cortes Históricos

Para verificar la generalidad del comportamiento dinámico del endpoint de inferencia y evitar conclusiones apresuradas basadas en cortes consecutivos aislados, se evaluaron cortes dominicales correspondientes a distintos regímenes de transmisión:

**Tabla 3. Auditoría de Inferencia Multi-Periodo a Través de Regímenes Epidémicos**
| Corte Dominical ($t_0$) | Régimen Epidémico | Observado $t_0$ | Fecha Objetivo ($t_1$) | Observado $t_1$ | Persistencia ($\hat{y}$) | Error Persistencia (MAE) | Random Forest ($\hat{y}$) | Error Random Forest (MAE) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2021-07-11** | Alta transmisión (Ola Delta, Train / Sanity Check) | 2,922 casos | 2021-07-18 | 3,922 casos | 2,922.0 casos | 1,000.0 casos | 3,270.26 casos | **651.74 casos** |
| **2022-12-18** | Transición moderada (Omicron tardío, Val) | 183 casos | 2022-12-25 | 363 casos | 183.0 casos | 180.0 casos | 276.28 casos | **86.72 casos** |
| **2023-04-02** | Inicio test reservado (Transición endémica) | 16 casos | 2023-04-09 | 9 casos | 16.0 casos | **7.0 casos** | 69.91 casos | 60.91 casos |
| **2024-01-07** | Fase endémica plana (Test) | 0 casos | 2024-01-14 | 0 casos | 0.0 casos | **0.0 casos** | 70.76 casos | 70.76 casos |
| **2024-07-21** | Corte penúltimo (Test) | 1 caso | 2024-07-28 | 0 casos | 1.0 caso | **1.0 caso** | 70.76 casos | 70.76 casos |
| **2024-07-28** | Corte de referencia final (Test) | 0 casos | 2024-08-04 | 0 casos | 0.0 casos | **0.0 casos** | 70.76 casos | 70.76 casos |
| **2024-08-04** | Última fecha histórica (Test / Futuro) | 0 casos | 2024-08-11 | *No disp.* | 0.0 casos | *No disp.* | 70.76 casos | *No disp.* |

#### Explicación Científica del Comportamiento Real:
- **En alta y moderada incidencia (2021–2022):** Cuando la serie presenta alta señal dinámica y variabilidad en los retardos autorregresivos, Random Forest explota eficazmente las combinaciones de covariables alcanzando predicciones competitivas frente a variaciones aceleradas (MAE de 651.74 vs 1,000.0 de persistencia en julio de 2021, y MAE de 86.72 vs 180.0 en diciembre de 2022).
- **En baja incidencia y transición endémica (2023–2024):** Cuando la incidencia colapsa a números de dos o un dígito, las hojas terminales de los árboles de decisión de Random Forest retienen un umbral inferior inducido por la imputación estática de `stringency_index = 22.77` y `reproduction_rate = 0.54`. Como consecuencia, cuando todos los retardos son 0 o 1, Random Forest se estanca en una predicción de ~70.76 casos/semana. En este régimen, la persistencia ingenua responde con precisión inmediata (errores de 0 a 1 caso), confirmando su superioridad para vigilancia sanitaria en mesetas endémicas.

---

## 4. Discusión y Límites Epistemológicos

### 4.1 Por qué la Persistencia Ingenua es Superior en Vigilancia Epidemiológica

En epidemiología cuantitativa, la persistencia ingenua ($\hat{y}_{t+1} = y_t$) no es una trivialidad matemática, sino el estándar de referencia canónico (*gold standard baseline*) avalado por los Centros para el Control y la Prevención de Enfermedades (CDC) y el COVID-19 Forecast Hub. Cuando una enfermedad entra en una fase de baja transmisión comunitaria o transición endémica donde la mayoría de semanas registran 0 contagios, la correlación serial a corto plazo domina ampliamente sobre cualquier función no lineal aprendida durante regímenes epidémicos pasados.

### 4.2 Ausencia de Validez Causal en el Modelo Random Forest

Un hallazgo crucial de esta auditoría es que la sensibilidad de una predicción de Random Forest ante variaciones de `stringency_index` **no constituye una prueba de efecto causal de una intervención sanitaria**. Las intervenciones gubernamentales se desplegaron simultáneamente con cambios en el comportamiento poblacional, restricciones de movilidad espontáneas y subnotificación de pruebas diagnósticas. Presentar las predicciones de Random Forest como estimaciones de políticas públicas equivaldría a incurrir en falacia de causa común (*confounding bias*).

Asimismo, el hecho de que la Universidad de Oxford haya finalizado la recolección del Oxford COVID-19 Government Response Tracker (OxCGRT) en diciembre de 2022 significa que cualquier inferencia para 2023 o 2024 requiere valores imputados de rigor (22.77) y tasa $R_t$ (0.54), los cuales reflejan suposiciones estáticas y no observaciones dinámicas de la semana en curso. En la arquitectura del gemelo digital, Random Forest se ha reubicado honestamente bajo el módulo de **«Exploración hipotética de sensibilidad»**, advirtiendo explícitamente a los analistas sanitarios de sus supuestos.

### 4.3 Arquitectura del Asistente de Datos del Gemelo Digital

Para garantizar la transferibilidad y transparencia de las predicciones, se implementó el **«Asistente de datos del gemelo digital»**. El diseño de su interfaz cumple tres principios deontológicos:
1. **Tripartición Estricta:** Las pantallas de respuesta segregan visiblemente (a) Observaciones empíricas de la base SQLite, (b) Pronósticos matemáticos del modelo, y (c) Síntesis explicativa redactada por el modelo de lenguaje.
2. **Trazabilidad de Herramientas y Fuentes:** Se explicitan las funciones del motor (`sql_db_query`, `weekly_forecasting_engine`) y las fuentes formales (Censo KNBS 2019, Barasa et al. 2020 S1 Table, OWID/OMS 2020–2024).
3. **Supresión de Trazas de Pensamiento:** Se omiten *scratchpads* o cadenas de pensamiento internas (*thought traces*) para prevenir confusión en la interpretación técnica por parte de los funcionarios de salud.

### 4.4 Límites Epistemológicos en la Capacidad Hospitalaria y Recursos Condales

Para contextualizar descriptivamente la infraestructura sanitaria de los 47 condados, se incorporaron las cifras oficiales del censo de capacidad hospitalaria de Barasa et al. (2020) (`S1 Table`, *PLOS ONE*, 15(7):e0236308, DOI: `10.1371/journal.pone.0236308.s001`), que audita un total nacional de **537 camas UCI** concentradas en 20 condados (Nairobi: 276, Mombasa: 35, Kiambu: 16, Nakuru: 20; 27 condados con 0 camas). Al no contarse con microdatos abiertos auditados de quintiles socioeconómicos a nivel de condado en este repositorio, se eliminaron de los datos operativos las estimaciones no verificables (`poverty_quintiles = null`) y se reclasificó `ds-kdhs-2022` a estado no verificado (`WARNING`/`ESTIMATED`). Asimismo, al no existir un modelo de derivación clínica de pacientes entre jurisdicciones, se mantiene una estricta prohibición metodológica de inferir saturación hospitalaria condal a partir de las proyecciones agregadas de vigilancia nacional.

---

## 5. Conclusiones

1. La auditoría empírica del dataset nacional de Kenia (1,606 observaciones diarias consolidadas en 230 semanas agregadas y 226 modeladas) demostró que el 100% de los reportes positivos ocurrieron en lotes dominicales, fundamentando la formulación del problema como vigilancia epidemiológica semanal.
2. Bajo un protocolo estricto de validación cruzada rodante en el conjunto de desarrollo (155 semanas: 2020-04-12 a 2023-03-26), el modelo **Baseline Naive Persistence** superó a los modelos multivariados complejos, obteniendo un RMSE de **1,183.64 casos/semana** frente a **1,345.87 casos/semana** de Random Forest.
3. En el conjunto de prueba reservado (71 semanas: 2023-04-02 a 2024-08-04), la persistencia ratificó su liderazgo frente a Random Forest con un RMSE de **55.64 casos/semana** frente a **81.72 casos/semana** y un MAE de **19.23** frente a **74.05 casos/semana**, con significancia estadística respaldada por el test de Diebold–Mariano ($DM^* = -14.324$, $p < 0.0001$).
4. La evaluación multi-periodo demostró que la persistencia domina en la fase endémica plana con bajas tasas de notificación, mientras que Random Forest queda condicionado por su hoja terminal de ~70.76 casos debido a la imputación de variables de control no observadas post-2022.
5. El Gemelo Digital Epidemiológico de Kenia articula un marco metodológico reproducible, honesto y transparente, separando con claridad la predicción oficial de vigilancia de la exploración hipotética de sensibilidad, con plena concordancia entre la documentación científica, la base de datos relacional y la interfaz de usuario.

---

## 6. Referencias

1. Our World in Data. (2024). *Coronavirus Pandemic (COVID-19) - Kenya Official Time-Series Data*. University of Oxford.
2. Kenya National Bureau of Statistics (KNBS). (2019). *2019 Kenya Population and Housing Census: Volume II - Distribution of Population by Administrative Units*. Government of Kenya.
3. Hale, T., Angrist, N., Goldszmidt, R., et al. (2021). *A global panel database of pandemic policies (Oxford COVID-19 Government Response Tracker)*. Nature Human Behaviour, 5(4), 529-538.
4. Diebold, F. X., & Mariano, R. S. (1995). *Comparing predictive accuracy*. Journal of Business & Economic Statistics, 13(3), 253-263.
5. Harvey, D., Leybourne, S., & Newbold, P. (1997). *Testing the equality of prediction mean squared errors*. International Journal of Forecasting, 13(2), 281-291.
6. Cramer, E. Y., Ray, E. L., Lopez, V. K., et al. (2022). *Evaluation of individual and ensemble probabilistic forecasts of COVID-19 mortality in the US*. Proceedings of the National Academy of Sciences, 119(15), e2113561119.
7. Chapman, P., Clinton, J., Kerber, R., et al. (2000). *CRISP-DM 1.0: Step-by-step data mining guide*. The CRISP-DM Consortium.
8. Barasa, E., Ouma, P. O., & Okiro, E. A. (2020). *Assessing the hospital surge capacity of the Kenyan health system in the face of the COVID-19 pandemic*. PLOS ONE, 15(7), e0236308. https://doi.org/10.1371/journal.pone.0236308
