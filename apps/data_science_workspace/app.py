import streamlit as st
import json
import os
from auth_helper import render_auth_sidebar, get_api_base_url

st.set_page_config(
    page_title="Data Science Workspace | Gemelo Digital Kenia",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_auth_sidebar()

st.title("🔬 Workspace Científico de Ciencia de Datos (CRISP-DM)")
st.caption("Entorno Técnico de Auditoría, Experimentación y Entrenamiento para el Evaluador Académico y Equipo de Ciencia de Datos")

st.markdown("""
---
### Metodología CRISP-DM Aplicada al Gemelo Digital Epidemiológico de Kenia

Este workspace es el **entorno técnico especializado** concebido para la revisión científica rigurosa. A diferencia de la aplicación web en React (destinada a tomadores de decisiones de salud pública), este espacio expone el linaje de datos íntegro, el código ejecutable de preprocesamiento, el entrenamiento canónico reproducible de modelos con validación cruzada temporal (5 pliegues) y las pruebas bioestadísticas formales.

| Fase CRISP-DM | Nombre de la Fase | Contenido Técnico y Científico Demostrable en Vivo |
| :--- | :--- | :--- |
| **Fase 1** | **Comprensión del Negocio** | Formulación del problema predictivo nacional semanal ($t+1$), rezagos como ventana de entrada observada (no pronóstico multi-paso), delimitación epistemológica entre pronóstico estadístico y simulación mecanicista SEIR/ABM. |
| **Fase 2** | **Comprensión de los Datos** | Procedencia verificable de Our World in Data (OWID / OMS), licencia CC BY 4.0, cálculo en vivo de SHA-256 del CSV crudo, inspección/descarga del archivo original (1,674 filas), EDA riguroso con interpretación e implicancia metodológica por gráfica. |
| **Fase 3** | **Preparación de los Datos** | Pipeline de limpieza reproducible, conciliación matemática exacta de exclusiones, agregación semanal canónica dominical (`W-SUN`), ingeniería de rezagos sin fuga temporal (anti-leakage) y verificación de ajuste exclusivo en Train. |
| **Fase 4** | **Modelado y Entrenamiento Real** | Invocación interactiva y autenticada de `scripts/train_and_evaluate_models.py`, progreso en tiempo real, grillas de hiperparámetros exploradas, `TimeSeriesSplit(n_splits=5)` en desarrollo, métricas por pliegue y selección ciega ex-ante del campeón. Calibración honesta vinculada a observaciones o exploración teórica. |
| **Fase 5** | **Evaluación Científica Real** | Tabla trazable CV / Hiperparámetros / Test, persistencia naive seleccionada ex-ante vs Ridge benchmark ex-post, advertencia sobre MAPE con ceros endémicos, pruebas pareadas de Shapiro-Wilk, Wilcoxon (bilateral y unilateral), Diebold-Mariano HLN (1997) y Kolmogorov-Smirnov con dirección, supuestos y conclusiones. |
| **Fase 6** | **Despliegue y Gobernanza** | Visualización de artefactos serializados (`.joblib`, `.json`), hashes criptográficos, verificación del servicio FastAPI en `:8000`, enlace a la respuesta JSON real del endpoint de predicción y trazabilidad hacia React. |

---
""")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Dataset Primario", "OWID / OMS (KEN)", "1,674 observaciones")
col2.metric("Tarea Predictiva", "Casos Semanales t+1", "Corte dominical W-SUN")
col3.metric("Validación Temporal", "TimeSeriesSplit (5 folds)", "Sin data snooping")
col4.metric("Backend Canónico", "FastAPI :8000", "Consumo de artefactos")

st.info("👈 Utiliza el menú lateral para recorrer secuencialmente las 6 fases metodológicas de CRISP-DM.")
