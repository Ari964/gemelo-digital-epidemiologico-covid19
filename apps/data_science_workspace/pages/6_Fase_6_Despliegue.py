import sys
import streamlit as st
import json
import os
import hashlib
import requests
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from auth_helper import render_auth_sidebar, api_call, get_api_base_url

st.set_page_config(page_title="Fase 6: Despliegue y Gobernanza | CRISP-DM", page_icon="🚀", layout="wide")
render_auth_sidebar()

st.title("🚀 Fase 6 (CRISP-DM) - Despliegue Operativo, Gobernanza de Artefactos y Consumo FastAPI")
st.caption("Inspección de Artefactos Serializados, Descriptor de Persistencia, Conectividad REST y Trazabilidad hacia React")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
MODELS_DIR = os.path.join(BASE_DIR, "models")

PERSISTENCE_JSON_PATH = os.path.join(MODELS_DIR, "official_naive_persistence_v1.0.json")
CHAMPION_JOBLIB_PATH = os.path.join(MODELS_DIR, "champion_covid_model_v1.0.joblib")
CHAMPION_JSON_PATH = os.path.join(MODELS_DIR, "champion_covid_model_v1.0.json")
EVAL_RESULTS_PATH = os.path.join(MODELS_DIR, "model_evaluation_weekly_results.json")

tab1, tab2, tab3 = st.tabs([
    "📦 Inventario de Artefactos y Criptografía",
    "🔌 Estado de FastAPI y Respuesta en Vivo",
    "🔗 Trazabilidad hacia el Frontend React"
])

# =========================================================================
# TAB 1: INVENTARIO DE ARTEFACTOS Y CRIPTOGRAFÍA
# =========================================================================
with tab1:
    st.subheader("1. Artefactos Serializados Oficiales en Disco")
    st.markdown("""
    En cumplimiento estricto del protocolo CRISP-DM:
    - Si un artefacto no existe, se presenta en estado **PENDIENTE** o **ERROR**. Jamás se inyectan cifras inventadas.
    - Se delimita categóricamente el rol de cada archivo.
    """)

    artifacts_info = []

    # 1. Descriptor de Persistencia Naive
    if os.path.exists(PERSISTENCE_JSON_PATH):
        with open(PERSISTENCE_JSON_PATH, "rb") as f:
            h_pers = hashlib.sha256(f.read()).hexdigest()
        with open(PERSISTENCE_JSON_PATH, "r", encoding="utf-8") as f:
            p_data = json.load(f)
        artifacts_info.append({
            "Artefacto": "official_naive_persistence_v1.0.json",
            "Rol Metodológico": "🏆 CAMPEÓN PREDICTIVO OFICIAL (t+1)",
            "Naturaleza": "Descriptor de persistencia autorregresiva (sin pesos .joblib)",
            "Tamaño": f"{os.path.getsize(PERSISTENCE_JSON_PATH)} bytes",
            "SHA-256": h_pers[:16] + "..." + h_pers[-8:],
            "Estado": "DISPONIBLE"
        })
    else:
        artifacts_info.append({
            "Artefacto": "official_naive_persistence_v1.0.json",
            "Rol Metodológico": "🏆 CAMPEÓN PREDICTIVO OFICIAL",
            "Naturaleza": "Descriptor de persistencia",
            "Tamaño": "0 bytes",
            "SHA-256": "N/D",
            "Estado": "❌ PENDIENTE"
        })

    # 2. Random Forest Joblib (Sensibilidad)
    if os.path.exists(CHAMPION_JOBLIB_PATH):
        with open(CHAMPION_JOBLIB_PATH, "rb") as f:
            h_joblib = hashlib.sha256(f.read()).hexdigest()
        artifacts_info.append({
            "Artefacto": "champion_covid_model_v1.0.joblib",
            "Rol Metodológico": "🔬 EXPLORACIÓN DE SENSIBILIDAD (NO CAUSAL)",
            "Naturaleza": "Pipeline scikit-learn serializado para análisis hipotético",
            "Tamaño": f"{os.path.getsize(CHAMPION_JOBLIB_PATH):,} bytes",
            "SHA-256": h_joblib[:16] + "..." + h_joblib[-8:],
            "Estado": "DISPONIBLE"
        })
    else:
        artifacts_info.append({
            "Artefacto": "champion_covid_model_v1.0.joblib",
            "Rol Metodológico": "🔬 EXPLORACIÓN DE SENSIBILIDAD",
            "Naturaleza": "Pipeline serializado",
            "Tamaño": "0 bytes",
            "SHA-256": "N/D",
            "Estado": "❌ PENDIENTE"
        })

    # 3. Metadatos de Gobernanza JSON
    if os.path.exists(CHAMPION_JSON_PATH):
        with open(CHAMPION_JSON_PATH, "rb") as f:
            h_json = hashlib.sha256(f.read()).hexdigest()
        artifacts_info.append({
            "Artefacto": "champion_covid_model_v1.0.json",
            "Rol Metodológico": "📋 METADATOS DE GOBERNANZA",
            "Naturaleza": "Contrato de linaje, auditoría y espacio de hiperparámetros",
            "Tamaño": f"{os.path.getsize(CHAMPION_JSON_PATH):,} bytes",
            "SHA-256": h_json[:16] + "..." + h_json[-8:],
            "Estado": "DISPONIBLE"
        })
    else:
        artifacts_info.append({
            "Artefacto": "champion_covid_model_v1.0.json",
            "Rol Metodológico": "📋 METADATOS DE GOBERNANZA",
            "Naturaleza": "Contrato de linaje",
            "Tamaño": "0 bytes",
            "SHA-256": "N/D",
            "Estado": "❌ PENDIENTE"
        })

    # 4. JSON de Evaluación Exhaustiva
    if os.path.exists(EVAL_RESULTS_PATH):
        with open(EVAL_RESULTS_PATH, "rb") as f:
            h_eval = hashlib.sha256(f.read()).hexdigest()
        artifacts_info.append({
            "Artefacto": "model_evaluation_weekly_results.json",
            "Rol Metodológico": "⚖️ REPORTE DE EVALUACIÓN SEMANAL",
            "Naturaleza": "Resultados de 5 folds, test reservado y pruebas bioestadísticas",
            "Tamaño": f"{os.path.getsize(EVAL_RESULTS_PATH):,} bytes",
            "SHA-256": h_eval[:16] + "..." + h_eval[-8:],
            "Estado": "DISPONIBLE"
        })
    else:
        artifacts_info.append({
            "Artefacto": "model_evaluation_weekly_results.json",
            "Rol Metodológico": "⚖️ REPORTE DE EVALUACIÓN",
            "Naturaleza": "Resultados de evaluación",
            "Tamaño": "0 bytes",
            "SHA-256": "N/D",
            "Estado": "❌ PENDIENTE"
        })

    st.dataframe(pd.DataFrame(artifacts_info), use_container_width=True)

    with st.expander("🔍 Ver Contenido del Descriptor del Campeón Oficial (`official_naive_persistence_v1.0.json`)"):
        if os.path.exists(PERSISTENCE_JSON_PATH):
            with open(PERSISTENCE_JSON_PATH, "r", encoding="utf-8") as f:
                st.json(json.load(f))

# =========================================================================
# TAB 2: ESTADO DE FASTAPI Y RESPUESTA EN VIVO
# =========================================================================
with tab2:
    st.subheader("2. Conectividad con FastAPI y Consulta en Vivo de Endpoints")
    
    api_url = get_api_base_url()
    st.markdown(f"Servidor backend configurado en: `{api_url}`")

    backend_online = False
    try:
        r_health = requests.get(f"{api_url}/health", timeout=2.0)
        if r_health.status_code == 200:
            backend_online = True
    except Exception:
        backend_online = False

    c_stat1, c_stat2 = st.columns([1, 2])
    with c_stat1:
        if backend_online:
            st.success("🟢 FASTAPI ONLINE (:8000)")
        else:
            st.error("🔴 FASTAPI OFFLINE")
            st.caption("Inicie el backend con: `uvicorn backend.app.main:app --port 8000`")

    with c_stat2:
        st.markdown("""
        **Endpoints Operativos Verificados:**
        - `GET /api/v1/validation/weekly-evaluation`: Expone el JSON de evaluación exhaustiva para React.
        - `POST /api/v1/predictions/weekly`: Ejecuta la inferencia semanal canónica $t+1$.
        """)

    st.markdown("---")
    st.markdown("#### Prueba en Vivo del Endpoint de Predicción Semanal (`POST /api/v1/predictions/weekly`):")
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        cutoff_sel = st.selectbox(
            "Seleccionar Domingo de Corte ($t_0$):",
            [
                "2024-07-28 (Meseta Endémica - Casos = 0.0)",
                "2021-07-11 (Ola Delta - Casos = 2,922.0)",
                "2021-12-19 (Ola Ómicron - Casos = 13,607.0)"
            ]
        )
        cutoff_date = cutoff_sel.split(" ")[0]

    with col_in2:
        st.write("")
        st.write("")
        query_btn = st.button("📡 Enviar Petición HTTP al Endpoint de FastAPI", type="primary", disabled=not backend_online)

    if query_btn:
        try:
            with st.spinner("Consultando FastAPI..."):
                resp = requests.post(
                    f"{api_url}/predictions/weekly",
                    json={"cutoff_date": cutoff_date},
                    timeout=5.0
                )
                if resp.status_code == 200:
                    data = resp.json()
                    st.success(f"✅ Respuesta 200 OK recibida en tiempo real desde FastAPI:")
                    
                    c_res1, c_res2, c_res3 = st.columns(3)
                    c_res1.metric("Casos Observados en Corte t0", f"{data.get('observed_cases_at_cutoff', 0.0):,}")
                    c_res2.metric("Pronóstico Oficial Naive (t+1)", f"{data.get('predicted_weekly_cases', 0.0):,}")
                    rf_pred = data.get("candidate_models_predictions", {}).get("Candidate_Random_Forest", {}).get("predicted_weekly_cases")
                    c_res3.metric("Sensibilidad Random Forest (t+1)", f"{rf_pred:,.2f}" if rf_pred is not None else "N/D")

                    with st.expander("📄 Ver JSON Completo de Respuesta de FastAPI", expanded=True):
                        st.json(data)
                else:
                    st.error(f"Error {resp.status_code} de FastAPI: {resp.text}")
        except Exception as e:
            st.error(f"Fallo al conectar con el endpoint: {e}")

# =========================================================================
# TAB 3: TRAZABILIDAD HACIA EL FRONTEND REACT
# =========================================================================
with tab3:
    st.subheader("3. Trazabilidad de Consumo: Streamlit → FastAPI → React")
    st.markdown("""
    La arquitectura del sistema garantiza una estricta **separación de públicos**:
    
    ```
    [ Dataset OWID Kenya (1,674 filas) ]
                    │
                    ▼
    [ scripts/eda_and_data_prep.py ] ──> [ kenya_covid_weekly_*.csv ]
                    │
                    ▼
    [ scripts/train_and_evaluate_models.py ] (5 pliegues TimeSeriesSplit)
                    │
                    ▼
    [ Artefactos: models/*.json & .joblib ]
                    │
                    ▼
    [ FastAPI Backend (:8000) ]
        ├── GET  /api/v1/validation/weekly-evaluation
        └── POST /api/v1/predictions/weekly
                    │
                    ▼
    [ Frontend React (:3000) ]
        ├── Vista de Validación (ValidationView)
        ├── Vigilancia Semanal (WeeklyForecastingView)
        └── Informes PDF/Excel Sustantivos (ReportsView)
    ```

    - **Workspace Streamlit (:8501):** Espacio técnico para el evaluador docente y el equipo de ciencia de datos. Permite ejecutar y auditar cada etapa científica.
    - **Frontend React (:3000):** Espacio para tomadores de decisiones de salud pública. Presenta pronósticos claros, escenarios interactivos e interpretaciones, sin abrumar con código ni grillas de hiperparámetros.
    """)
