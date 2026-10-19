import streamlit as st

st.set_page_config(page_title="Fase 1: Comprensión del Negocio | CRISP-DM", page_icon="📋", layout="wide")

st.title("📋 Fase 1 (CRISP-DM) - Comprensión del Negocio y Definición del Problema")
st.caption("Objetivo Predictivo Nacional, Delimitación de Variables, Ventana de Rezagos Históricos y Separación Epistemológica")

tab1, tab2, tab3 = st.tabs([
    "🎯 Definición del Problema Predictivo",
    "🔬 Ventana Histórica vs Horizonte (Aclaración Metodológica)",
    "⚖️ Pronóstico Estadístico vs Gemelo Digital SEIR/ABM"
])

with tab1:
    st.subheader("1. Formulación del Objetivo Predictivo Canónico")
    st.markdown("""
    En el marco de la vigilancia epidemiológica en Kenia y bajo la metodología **CRISP-DM**, el objetivo analítico principal es:
    
    > **Objetivo:** Predecir con una semana de anticipación ($t+1$) el volumen agregado nacional de nuevos casos confirmados de COVID-19 en Kenia, a partir de la serie temporal histórica oficial reportada por el Ministerio de Salud (MoH) y la Organización Mundial de la Salud (OMS) a través de Our World in Data (OWID).

    #### Especificación Técnica de la Tarea:
    """)

    col1, col2, col3 = st.columns(3)
    col1.info("**Variable Objetivo ($y_{t+1}$)**\n\n`target_weekly_cases`: Casos positivos confirmados acumulados en la semana epidemiológica.")
    col2.info("**Unidad de Medida**\n\nCasos nuevos confirmados por semana (`casos/semana`).")
    col3.info("**Frecuencia y Corte**\n\nSemanal canónica con corte dominical (`W-SUN`).")

    col4, col5, col6 = st.columns(3)
    col4.success("**Horizonte de Predicción**\n\n**Estrictamente 1 semana hacia adelante ($t+1$)**. Extrapolaciones a múltiples semanas requerirían predicción recursiva autoregresiva acumulando incertidumbre no validada.")
    col5.success("**Alcance Geográfico**\n\nNivel Nacional (`ISO: KEN`), coincidente con el registro oficial primario continuo.")
    col6.success("**Criterio de Evaluación**\n\nMinimización del error cuadrático medio (RMSE) y absoluto (MAE) en validación temporal sin fuga.")

with tab2:
    st.subheader("2. Aclaración Metodológica Crítica: Ventana Histórica vs Horizonte de Predicción")
    st.warning("""
    ⚠️ **DESLINDE CONCEPTUAL IMPORTANTE:**  
    Las cuatro semanas observadas en los descriptores del modelo (`weekly_lag_1`, `weekly_lag_2`, `weekly_lag_3`, `weekly_lag_4`) **NO constituyen un pronóstico de 4 semanas hacia el futuro**.  
    Representan la **ventana de entrada histórica retrospectiva de 4 semanas** utilizada para capturar la inercia epidémica reciente antes del corte $t_0$.
    """)

    st.markdown(r"""
    ### Esquema Temporal de Inferencia:
    
    $$\underbrace{[t_0 - 21\text{ d}]}_{\text{Lag 4}} \longrightarrow \underbrace{[t_0 - 14\text{ d}]}_{\text{Lag 3}} \longrightarrow \underbrace{[t_0 - 7\text{ d}]}_{\text{Lag 2}} \longrightarrow \underbrace{[t_0]}_{\text{Lag 1 (Última obs.)}} \quad \Bigg| \quad \xrightarrow{\text{Predicción}} \quad \mathbf{\widehat{y}_{t+1}\ [t_0 + 7\text{ d}]}$$

    | Variable de Entrada | Tipo de Información | Naturaleza Temporal |
    | :--- | :--- | :--- |
    | `weekly_lag_1` | Casos observados en la semana de corte $t_0$ | Retrospectiva ($t_0$) |
    | `weekly_lag_2` | Casos observados 1 semana antes de $t_0$ | Retrospectiva ($t_0 - 7\text{ d}$) |
    | `weekly_lag_3` | Casos observados 2 semanas antes de $t_0$ | Retrospectiva ($t_0 - 14\text{ d}$) |
    | `weekly_lag_4` | Casos observados 3 semanas antes de $t_0$ | Retrospectiva ($t_0 - 21\text{ d}$) |
    | `weekly_rolling_mean_4` | Promedio móvil de las 4 semanas previas | Resumen de tendencia reciente |
    | `weekly_rolling_std_4` | Desviación estándar de las 4 semanas previas | Resumen de volatilidad reciente |
    | `weekly_deaths_lag_1, 2` | Muertes observadas en semanas previas | Severidad clínica observada |
    | `stringency_lag_1` | Índice de rigor gubernamental Oxford (hasta 2022) | Covariable contextual de intervención |
    | `reproduction_rate_lag_1` | Tasa de reproducción efectiva previa ($R_t$) | Dinámica de transmisión previa |
    | `month` | Mes del año (1 a 12) | Estacionalidad |
    """)

with tab3:
    st.subheader("3. Separación de Componentes: Pronóstico Estadístico vs Simulación Contrafactual SEIR/ABM")
    st.markdown("""
    Para mantener la máxima honestidad y rigor científico, el proyecto delimita de manera categórica dos herramientas distintas:
    """)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        ### A. Modelos Estadísticos y Machine Learning
        - **Propósito:** Pronosticar el valor puntual de incidencia semanal en $t+1$.
        - **Modelos:** Naive Persistence ($\hat{y}_{t+1} = y_t$), Ridge Regression, Random Forest, HistGradientBoosting.
        - **Datos de sustento:** Serie empírica verificada de Our World in Data (OWID).
        - **Evaluación empírica:** Validado con 5 pliegues temporales (`TimeSeriesSplit`) y prueba ciega reservada de 71 semanas (2023-2024).
        - **Rol del Campeón Oficial:** `Baseline_Naive_Persistence` (CV RMSE: 1,183.64 casos; Test MAE: 19.23 casos).
        - **Rol de Random Forest:** Exploración hipotética de sensibilidad condicional ante covariables (no causal).
        """)

    with col_b:
        st.markdown("""
        ### B. Gemelo Digital Mecanicista (SEIR Espacial + ABM)
        - **Propósito:** Simulación matemática contrafactual de escenarios de políticas de salud pública (NPIs, cierres escolares, cuarentenas, vacunación, DALYs).
        - **Naturaleza:** Sistema determinista/estocástico basado en compartimentos epidemiológicos y adyacencia espacial de 47 condados.
        - **Clasificación Formal:** **`NOT_EVALUATED_IN_WEEKLY_SERIES`**.
        - **Advertencia Científica:** Sus curvas de salida son simulaciones matemáticas contrafactuales; **no equivalen a casos clínicos observados ni demuestran un efecto causal comprobado**.
        - **No atribución cruzada:** No se le atribuyen las métricas estadísticas de Ridge o Random Forest al simulador SEIR/ABM.
        """)

    st.markdown("---")
    st.info("💡 **Conclusión de Fase 1:** El sistema aborda el pronóstico semanal a corto plazo con rigor estadístico ciego y restringe el Gemelo Digital mecanicista a su rol legítimo de simulador contrafactual de políticas de salud pública.")
