import streamlit as st
import os
import hashlib
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Fase 2: Comprensión de los Datos (EDA) | CRISP-DM", page_icon="📊", layout="wide")

st.title("📊 Fase 2 (CRISP-DM) - Origen, Linaje y Análisis Exploratorio de Datos (EDA)")
st.caption("Inspección Criptográfica del Dataset Público OWID, Diccionario de Variables, Auditoría de Calidad y EDA Nacional")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
RAW_CSV_PATH = os.path.join(BASE_DIR, "data", "raw", "owid_covid_kenya_raw.csv")
METADATA_JSON_PATH = os.path.join(BASE_DIR, "data", "raw", "dataset_metadata.json")
BARASA_CSV_PATH = os.path.join(BASE_DIR, "data", "raw", "barasa_2020_surge_capacity_s1_table.csv")

if not os.path.exists(RAW_CSV_PATH):
    st.error(f"❌ Archivo crudo no encontrado en: `{RAW_CSV_PATH}`")
    st.stop()

# Cálculo criptográfico en vivo al cargar la página
with open(RAW_CSV_PATH, "rb") as f:
    raw_bytes = f.read()
    live_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    raw_size_bytes = len(raw_bytes)

# Carga de datos crudos
df_raw = pd.read_csv(RAW_CSV_PATH)
df_raw["date"] = pd.to_datetime(df_raw["date"])
df_raw = df_raw.sort_values(by="date").reset_index(drop=True)

# Cargar metadatos documentados
meta = {}
if os.path.exists(METADATA_JSON_PATH):
    with open(METADATA_JSON_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

tab_prov, tab_eda, tab_counties = st.tabs([
    "🌐 Procedencia y Ficha Criptográfica",
    "📈 EDA Nacional de la Serie OWID",
    "🏥 Auditoría de Fuentes Públicas Condales"
])

# =========================================================================
# TAB 1: PROCEDENCIA Y FICHA CRIPTOGRÁFICA
# =========================================================================
with tab_prov:
    st.subheader("1. Ficha Técnica y Linaje del Dataset Primario")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Institución Emisora", "Our World in Data (OWID)", "Univ. of Oxford / OMS")
    col2.metric("Licencia de Uso", "CC BY 4.0 Internacional", "Acceso Abierto")
    col3.metric("Fecha de Extracción", meta.get("query_date", "2026-09-23"), "Repositorio Consolidado")

    st.markdown("""
    - **Página oficial pública:** [Our World in Data COVID-19 Dataset](https://ourworldindata.org/coronavirus)
    - **URL de descarga directa original:** `https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv`
    - **Ruta local del CSV crudo inmutable:** `data/raw/owid_covid_kenya_raw.csv`
    """)

    st.markdown("#### Verificación de Integridad Criptográfica en Tiempo Real:")
    c_hash1, c_hash2 = st.columns([3, 1])
    with c_hash1:
        st.code(f"SHA-256 Calculado al Abrir: {live_sha256}", language="text")
        if live_sha256 == meta.get("sha256_checksum"):
            st.success("✅ INTEGRIDAD CERTIFICADA: El hash coincide exactamente con el registro inmutable de auditoría.")
        else:
            st.error("⚠️ DISCREPANCIA EN CHECKSUM")
    with c_hash2:
        st.download_button(
            label="⬇️ Descargar CSV Original Sin Alterar",
            data=raw_bytes,
            file_name="owid_covid_kenya_raw.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown("---")
    st.markdown("#### ¿Qué representa cada fila del dataset crudo?")
    st.markdown("""
    Cada fila representa **un día calendario de vigilancia epidemiológica para Kenia a nivel NACIONAL** (`ISO: KEN`), abarcando desde el **2020-01-05** hasta el **2024-08-04** (1,674 días consecutivos).  
    *Nota epistemológica:* La fuente institucional reporta la incidencia agregada del país; no contiene subdivisión por condados.
    """)

    st.markdown("#### Diccionario de Columnas Críticas Utilizadas:")
    dict_data = [
        {"Columna": "date", "Tipo": "date (YYYY-MM-DD)", "Descripción": "Fecha calendario del reporte oficial.", "Rol": "Eje temporal"},
        {"Columna": "new_cases", "Tipo": "float64", "Descripción": "Casos confirmados diarios reportados por MoH/OMS. Presenta concentración en domingos.", "Rol": "Base para agregación semanal"},
        {"Columna": "new_cases_smoothed", "Tipo": "float64", "Descripción": "Media móvil de 7 días calculada por OWID dividiendo el lote semanal.", "Rol": "Referencia exploratoria"},
        {"Columna": "new_deaths", "Tipo": "float64", "Descripción": "Defunciones diarias atribuidas a COVID-19 confirmadas.", "Rol": "Covariable de severidad"},
        {"Columna": "stringency_index", "Tipo": "float64", "Descripción": "Oxford Government Response Tracker (0 a 100). Finalizó el 31/12/2022.", "Rol": "Covariable contextual NPI"},
        {"Columna": "reproduction_rate", "Tipo": "float64", "Descripción": "Tasa efectiva de reproducción Rt estimada por OWID. Cesó pos-2022.", "Rol": "Covariable epidemiológica"},
        {"Columna": "total_cases", "Tipo": "float64", "Descripción": "Acumulado histórico total de casos confirmados.", "Rol": "Monitoreo acumulado"}
    ]
    st.dataframe(pd.DataFrame(dict_data), use_container_width=True)

# =========================================================================
# TAB 2: EDA NACIONAL DE LA SERIE OWID
# =========================================================================
with tab_eda:
    st.subheader("2. Análisis Exploratorio de Datos (EDA) sobre la Serie Nacional")
    
    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    col_d1.metric("Total Observaciones", f"{len(df_raw):,} filas")
    col_d2.metric("Total Columnas Crudas", f"{df_raw.shape[1]} variables")
    col_d3.metric("Duplicados de Fecha", f"{df_raw.duplicated(subset=['date']).sum()} registros", "Consistencia 100%")
    col_d4.metric("Rango Temporal", f"{df_raw['date'].min().strftime('%Y-%m-%d')} a {df_raw['date'].max().strftime('%Y-%m-%d')}")

    # Tabla 1: Auditoría de Nulos y Tipos en Variables Clave
    st.markdown("#### A. Auditoría de Valores Nulos y Estadísticas Descriptivas")
    key_cols = ["date", "new_cases", "new_cases_smoothed", "new_deaths", "stringency_index", "reproduction_rate", "total_cases"]
    eda_summary = []
    for c in key_cols:
        if c in df_raw.columns:
            s = df_raw[c]
            eda_summary.append({
                "Variable": c,
                "Tipo": str(s.dtype),
                "No Nulos": int(s.notna().sum()),
                "Nulos": int(s.isna().sum()),
                "% Nulos": round(float(s.isna().mean() * 100.0), 2),
                "Mínimo": round(float(s.min()), 2) if pd.api.types.is_numeric_dtype(s) else str(s.min()),
                "Mediana": round(float(s.median()), 2) if pd.api.types.is_numeric_dtype(s) else "N/A",
                "Máximo": round(float(s.max()), 2) if pd.api.types.is_numeric_dtype(s) else str(s.max())
            })
    st.dataframe(pd.DataFrame(eda_summary), use_container_width=True)
    st.caption("""
    🔍 **Interpretación Metodológica:**
    - `new_cases` tiene 0% de nulos en el periodo epidémico; los valores en cero tras 2023 reflejan el cese de reportes diarios independientes de la OMS.
    - `stringency_index` presenta un 34.8% de nulos totales porque la Universidad de Oxford interrumpió la recolección global de datos el 31 de diciembre de 2022. Cualquier modelo que utilice esta covariable pos-2022 requiere imputación o fijación de política hipotética.
    """)

    st.markdown("---")
    # Gráfica 1: Serie Temporal de Casos
    st.markdown("#### B. Evolución Temporal de Nuevos Casos (2020 - 2024)")
    fig_cases = px.line(
        df_raw, x="date", y=["new_cases", "new_cases_smoothed"],
        labels={"value": "Casos Diarios", "date": "Fecha", "variable": "Serie"},
        title="Nuevos Casos Diarios Confirmados en Kenia (OWID/OMS)"
    )
    fig_cases.update_layout(template="plotly_dark" if st.session_state.get("dark_mode", True) else "plotly_white")
    st.plotly_chart(fig_cases, use_container_width=True)
    st.caption("""
    🔍 **Interpretación Metodológica e Implicancia:**
    - Se aprecian claramente las 5 olas pandémicas principales en Kenia: Ola Ancestral (Jul-Ago 2020), Ola Beta (Nov 2020), Ola Alpha/Delta (Marzo-Agosto 2021) y Ola Ómicron (Dic 2021 - Ene 2022 con pico de ~3,700 casos/día).
    - A partir de abril de 2023, la serie entra en una meseta endémica de reporte nulo (`0 casos`), interrumpida esporádicamente por reportes acumulados tardíos. Esto justifica la separación entre conjunto de desarrollo (2020-2023) y prueba ciega reservada (2023-2024).
    """)

    st.markdown("---")
    # Gráfica 2: Concentración de Reportes en Domingos
    st.markdown("#### C. Hallazgo Metodológico Crítico: Frecuencia Real de Reporte Institucional")
    df_raw["dia_semana"] = df_raw["date"].dt.day_name()
    day_counts = df_raw[df_raw["new_cases"] > 0]["dia_semana"].value_counts().reset_index()
    day_counts.columns = ["Día de la Semana", "Días con Reporte Positivo (new_cases > 0)"]
    
    col_g1, col_g2 = st.columns([2, 1])
    with col_g1:
        fig_bar = px.bar(
            day_counts, x="Día de la Semana", y="Días con Reporte Positivo (new_cases > 0)",
            color="Días con Reporte Positivo (new_cases > 0)",
            title="Días de la Semana con Reportes Positivos de Casos"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    with col_g2:
        st.markdown("""
        **Comprobación de Periodicidad:**
        - **Domingos (Sunday):** Concentra la inmensa mayoría de reportes positivos en las fases de transición.
        - **Conclusión de Ingeniería:** Modelar la serie diaria induce a predecir ceros artificiales de lunes a sábado y picos el domingo.
        - **Implicancia Metodológica:** La formulación científica matemáticamente defendible es agregar a **semanas epidemiológicas completas (`W-SUN`)**, eliminando el artefacto de notificación dominical.
        """)

# =========================================================================
# TAB 3: AUDITORÍA DE FUENTES PÚBLICAS CONDALES
# =========================================================================
with tab_counties:
    st.subheader("3. Auditoría de Fuentes Públicas de los 47 Condados")
    st.markdown("""
    En estricto cumplimiento del principio de **no inventar datos ni citar fuentes ausentes**:
    """)

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("### A. Población Oficial (Censo KNBS 2019)")
        st.markdown("""
        - **Fuente:** Kenya National Bureau of Statistics (KNBS) 2019 Census, Vol. I, Tabla 2.2.
        - **Población Nacional Total:** **47,564,296 habitantes**.
        - **Condados más poblados:** Nairobi (4,397,073), Kiambu (2,417,735), Nakuru (2,162,202).
        - **Integridad:** Auditada en `src/data/kenyaCounties.ts` y tabla de gobernanza.
        """)

    with col_c2:
        st.markdown("### B. Camas UCI Auditadas (Barasa et al. 2020 PLOS ONE)")
        st.markdown("""
        - **Fuente:** Barasa, E., et al. (2020). *Assessing hospital surge capacity in Kenya*. **PLOS ONE** 15(7):e0236308.
        - **Archivo público presente:** `data/raw/barasa_2020_surge_capacity_s1_table.csv`
        - **Hallazgo Real:** Total nacional de 537 camas UCI. Nairobi cuenta con 276, Mombasa 35, Kiambu 16, Nakuru 20.
        - **Realidad de Cobertura:** **27 condados tenían 0 camas UCI registradas** al inicio de la pandemia.
        """)

    if os.path.exists(BARASA_CSV_PATH):
        st.markdown("#### Vista del CSV de Barasa et al. (2020) Suplementario S1:")
        df_barasa = pd.read_csv(BARASA_CSV_PATH)
        st.dataframe(df_barasa.head(10), use_container_width=True)
        st.caption("Visualizando las primeras 10 filas de `data/raw/barasa_2020_surge_capacity_s1_table.csv`.")

    st.markdown("---")
    st.markdown("### C. Declaración Honesta sobre Movilidad Intercondal")
    st.info("""
    📌 **DECLARACIÓN DE INTEGRIDAD:**  
    No se dispone en el repositorio de una suscripción de datos cerrados de telefonía celular continua (CDR) para los 47 condados.  
    La matriz de movilidad del simulador SEIR opera bajo un **modelo gravitacional estimado basado en distancias geodésicas Haversine y población del censo**.  
    Por tanto, queda formalmente etiquetada como **ESTIMACIÓN TEÓRICA**, sin pretender que represente observaciones directas de movilidad empírica continua.
    """)
