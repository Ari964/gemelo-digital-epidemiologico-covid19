"""
Endpoint de Integración con LangChain para el Gemelo Digital Epidemiológico.

Implementa un caso integrador pequeño, verificable y trazable utilizando
componentes oficiales de LangChain (langchain-core, tools, LCEL, StrOutputParser).

Cumple estrictamente con:
1. Consulta de observaciones reales de la base de datos (SQLite) mediante herramientas (@tool).
2. Consulta de pronósticos de modelos existentes (Persistencia Naive y Random Forest) mediante herramientas (@tool).
3. Ejecución de un pipeline LCEL de LangChain (ChatPromptTemplate | Model/Runnable | StrOutputParser).
4. Separación explícita entre:
   - database_observations (datos observados)
   - model_forecasts (predicciones)
   - generated_text (texto generado por la cadena)
5. Reporte transparente de los componentes de LangChain ejecutados y herramientas invocadas.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import os
import time

from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from backend.app.db.session import get_db
from backend.app.models.observation import ObservationDB
from backend.app.models.spatial import CountyDB
from backend.app.api.v1.endpoints.predictions import (
    predict_weekly_cases,
    PredictionRequest,
)

router = APIRouter()


# ---------------------------------------------------------
# 1. Definición de Herramientas Estructuradas con LangChain
# ---------------------------------------------------------

@tool
def tool_query_observations(cutoff_date: str) -> Dict[str, Any]:
    """Consulta observaciones epidemiológicas históricas oficiales para una fecha de corte semanal t0 (YYYY-MM-DD)."""
    import pandas as pd
    test_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "data", "processed", "kenya_covid_weekly_test.csv"))
    val_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "data", "processed", "kenya_covid_weekly_val.csv"))
    train_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "data", "processed", "kenya_covid_weekly_train.csv"))
    
    match_row = None
    source_file = None
    for p in [test_path, val_path, train_path]:
        if os.path.exists(p):
            df = pd.read_csv(p)
            m = df[df["date"] == cutoff_date]
            if not m.empty:
                match_row = m.iloc[0].to_dict()
                source_file = os.path.basename(p)
                break
                
    if match_row:
        import numpy as np
        target_cases = match_row.get("target_weekly_cases")
        new_cases = match_row.get("new_cases")
        obs_cases = None
        if pd.notna(target_cases):
            obs_cases = float(target_cases)
        elif pd.notna(new_cases):
            obs_cases = float(new_cases)

        new_deaths = match_row.get("new_deaths")
        lag_deaths = match_row.get("weekly_deaths_lag_1")
        obs_deaths = None
        if pd.notna(new_deaths):
            obs_deaths = float(new_deaths)
        elif pd.notna(lag_deaths):
            obs_deaths = float(lag_deaths)

        # Distinguir variables con imputación documentada de datos observados directos
        stringency_raw = match_row.get("stringency_lag_1")
        is_stringency_imputed = False
        stringency_val = None
        if pd.notna(stringency_raw):
            stringency_val = float(stringency_raw)
            if str(match_row.get("date", "")) >= "2023-01-01":
                is_stringency_imputed = True

        reproduction_raw = match_row.get("reproduction_rate_lag_1")
        is_reproduction_imputed = False
        reproduction_val = None
        if pd.notna(reproduction_raw):
            reproduction_val = float(reproduction_raw)
            if str(match_row.get("date", "")) >= "2023-01-01":
                is_reproduction_imputed = True

        return {
            "date": str(match_row.get("date")),
            "observed_weekly_cases": obs_cases,
            "observed_weekly_deaths": obs_deaths,
            "stringency_index_lag1": stringency_val,
            "stringency_is_imputed": is_stringency_imputed,
            "reproduction_rate_lag1": reproduction_val,
            "reproduction_is_imputed": is_reproduction_imputed,
            "data_source": f"Serie Semanal Oficial OWID/OMS Kenia ({source_file})",
            "status": "Registro histórico empírico localizado",
            "epistemological_note": (
                "Casos y decesos son observaciones empíricas directas de OWID/OMS (Kenia nacional). "
                "Índices de rigurosidad pos-2022 constituyen imputaciones conservadoras documentadas."
                if is_stringency_imputed else
                "Casos, decesos e índices son observaciones empíricas históricas de OWID/OMS."
            )
        }
    return {
        "date": cutoff_date,
        "observed_weekly_cases": None,
        "data_source": "Serie Semanal Oficial OWID/OMS Kenia",
        "status": f"Fecha {cutoff_date} no registrada en el dataset histórico de vigilancia."
    }


@tool
def tool_query_forecasts(cutoff_date: str, county_code: int = 0) -> Dict[str, Any]:
    """Consulta la inferencia del modelo campeón (Baseline_Naive_Persistence) y la sensibilidad de Random Forest."""
    from backend.app.db.session import SessionLocal
    db = SessionLocal()
    try:
        req = PredictionRequest(cutoff_date=cutoff_date, county_code=county_code)
        res = predict_weekly_cases(req, db=db)
        return {
            "cutoff_date": res.cutoff_date,
            "target_week": res.target_week,
            "primary_model": res.primary_model_name,
            "persistence_prediction_cases": res.primary_forecast_cases,
            "observed_target_actual": res.target_observed_actual,
            "random_forest_sensitivity_cases": res.hypothetical_rf_prediction,
            "sensitivity_disclaimer": res.sensitivity_disclaimer
        }
    finally:
        db.close()


@tool
def tool_query_hospital_capacity(county_code: int = 0) -> Dict[str, Any]:
    """Consulta la capacidad hospitalaria y camas UCI del Censo KNBS para Kenia o un condado específico."""
    from backend.app.db.session import SessionLocal
    db = SessionLocal()
    try:
        if county_code > 0:
            c = db.query(CountyDB).filter(CountyDB.code == county_code).first()
            if c:
                return {
                    "county_name": c.name,
                    "county_code": c.code,
                    "population": c.population_2019,
                    "icu_beds": c.icu_beds_verified,
                    "source": c.icu_source or "Barasa et al. (2020) PLOS ONE 15(7):e0236308 S1 Table (DOI: 10.1371/journal.pone.0236308.s001)",
                    "verification_status": "VERIFICADA_BARASA_2020_S1" if c.icu_beds_verified is not None else "SIN_CAMAS_VERIFICADAS"
                }
            return {
                "county_code": county_code,
                "status": f"Condado con código {county_code} no encontrado en la base de datos.",
                "verification_status": "NO_ENCONTRADO",
                "population": None,
                "icu_beds": None
            }
        from sqlalchemy import func
        total_pop = db.query(func.sum(CountyDB.population_2019)).scalar()
        if total_pop is None or total_pop == 0:
            return {
                "scope": "Nacional Agregado (Kenia, KEN)",
                "total_population_2019": None,
                "total_verified_icu_beds": None,
                "status": "Datos de población nacional no disponibles en la base de datos CountyDB.",
                "verification_status": "DATO_AUSENTE_BD"
            }
        total_icu = db.query(func.sum(CountyDB.icu_beds_verified)).filter(CountyDB.icu_beds_verified != None).scalar()
        top3 = db.query(CountyDB).order_by(CountyDB.population_2019.desc()).limit(3).all()
        return {
            "scope": "Nacional Agregado (Kenia, KEN)",
            "total_population_2019": int(total_pop),
            "total_verified_icu_beds": int(total_icu) if total_icu is not None else None,
            "sample_major_counties": [{"name": c.name, "population": c.population_2019, "icu_beds": c.icu_beds_verified} for c in top3],
            "source": "Barasa et al. (2020) PLOS ONE 15(7):e0236308 S1 Table (DOI: 10.1371/journal.pone.0236308.s001)",
            "verification_status": "INVENTARIO_ESTATICO_BARASA_2020",
            "epistemological_note": "Inventario estático descriptivo nacional. No existe modelo de conversión a demanda UCI clínica a partir de las proyecciones semanales de incidencia."
        }
    finally:
        db.close()


# ---------------------------------------------------------
# 2. Schemas de Solicitud y Respuesta
# ---------------------------------------------------------

class LangChainQueryRequest(BaseModel):
    query: str = Field(..., description="Consulta del usuario a procesar con la cadena LangChain.")
    cutoff_date: Optional[str] = Field("2024-07-28", description="Fecha de corte dominical (YYYY-MM-DD)")
    county_code: Optional[int] = Field(0, description="0 para Nacional, 1-47 para condados específicos")
    lang: Optional[str] = Field("es", description="Código de idioma objetivo: es, en, sw")


class LangChainMetadata(BaseModel):
    framework: str = Field("LangChain Core 1.6+ (LCEL Runnable)", description="Framework de orquestación")
    execution_mode: str = Field(..., description="Modo de ejecución del pipeline (RunnableLambda determinista vs LLM)")
    orchestration_type: str = Field(..., description="Tipo de orquestación de herramientas")
    components_executed: List[str] = Field(..., description="Nombres de clases y componentes LangChain ejecutados")
    tools_invoked: List[Dict[str, Any]] = Field(..., description="Herramientas LangChain ejecutadas con sus argumentos")
    provider: str = Field(..., description="Proveedor o ejecutor del razonamiento")
    execution_time_ms: float = Field(..., description="Latencia de ejecución en milisegundos")


class LangChainIntegrationResponse(BaseModel):
    query: str
    cutoff_date: str
    database_observations: Dict[str, Any] = Field(..., description="Datos empíricos recuperados por tool_query_observations")
    model_forecasts: Dict[str, Any] = Field(..., description="Predicciones generadas por tool_query_forecasts")
    hospital_capacity: Dict[str, Any] = Field(..., description="Capacidad médica obtenida por tool_query_hospital_capacity")
    generated_text: str = Field(..., description="Texto sintetizado por el pipeline LangChain LCEL")
    langchain_metadata: LangChainMetadata


# ---------------------------------------------------------
# 3. Endpoint FastAPI de Integración LangChain
# ---------------------------------------------------------

@router.post("/query", response_model=LangChainIntegrationResponse)
def execute_langchain_agent(
    request: LangChainQueryRequest,
    db: Session = Depends(get_db)
):
    start_time = time.time()
    cutoff = request.cutoff_date or "2024-07-28"
    county = request.county_code or 0

    components_executed: List[str] = []
    tools_invoked: List[Dict[str, Any]] = []

    # 1. Ejecutar herramientas LangChain
    components_executed.append("langchain_core.tools.StructuredTool(tool_query_observations)")
    obs_res = tool_query_observations.invoke({"cutoff_date": cutoff})
    tools_invoked.append({
        "tool_name": "tool_query_observations",
        "args": {"cutoff_date": cutoff},
        "output_summary": f"Casos observados en t0: {obs_res.get('observed_weekly_cases')}"
    })

    components_executed.append("langchain_core.tools.StructuredTool(tool_query_forecasts)")
    forecast_res = tool_query_forecasts.invoke({"cutoff_date": cutoff, "county_code": county})
    tools_invoked.append({
        "tool_name": "tool_query_forecasts",
        "args": {"cutoff_date": cutoff, "county_code": county},
        "output_summary": f"Persistencia: {forecast_res.get('persistence_prediction_cases')} casos, RF: {forecast_res.get('random_forest_sensitivity_cases')} casos"
    })

    components_executed.append("langchain_core.tools.StructuredTool(tool_query_hospital_capacity)")
    hosp_res = tool_query_hospital_capacity.invoke({"county_code": county})
    tools_invoked.append({
        "tool_name": "tool_query_hospital_capacity",
        "args": {"county_code": county},
        "output_summary": f"Recursos obtenidos para ámbito {hosp_res.get('scope', hosp_res.get('county_name'))}"
    })

    # 2. Configurar PromptTemplate de LangChain
    components_executed.append("langchain_core.prompts.ChatPromptTemplate")
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "Eres el Agente de Integración Epidemiológica de LangChain para el Gemelo Digital de Kenia.\n"
            "Tu tarea es sintetizar objetivamente los datos empíricos de la base y los pronósticos de los modelos.\n"
            "REGLAS METODOLÓGICAS ESTRICTAS:\n"
            "1. Cita con precisión las cifras de observaciones ({observations}) y pronósticos ({forecasts}), identificándolas siempre como cifras NACIONALES agregadas de Kenia (KEN, county_code=0).\n"
            "2. Destaca que la Persistencia Naive es el modelo campeón de vigilancia seleccionado ex-ante por validación cruzada temporal en desarrollo.\n"
            "3. Explica que la predicción de Random Forest es una exploración hipotética de sensibilidad y no un efecto causal.\n"
            "4. Identifica las camas UCI ({capacity}) estrictamente como inventario descriptivo estático del ámbito solicitado. Si el usuario seleccionó un condado específico, menciona únicamente dicho condado; si seleccionó ámbito nacional, menciona los condados principales o generales. NUNCA inventes saturación UCI ni concluyas que las camas se saturan o no: el pronóstico epidemiológico es nacional y no existe un modelo de conversión a demanda UCI condal.\n"
            "5. NO inventes cifras adicionales."
        )),
        ("human", "Consulta del usuario: {query}")
    ])

    # 3. Proveedor de Lenguaje: Google GenAI si existe en env de forma segura, o Runnable determinista LangChain
    components_executed.append("langchain_core.runnables.RunnableSequence")
    components_executed.append("langchain_core.output_parsers.StrOutputParser")

    ollama_base_url = (os.getenv("OLLAMA_BASE_URL") or "http://127.0.0.1:11434").rstrip("/")
    ollama_model = os.getenv("OLLAMA_MODEL") or "qwen2.5:0.5b"
    ollama_timeout = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "60"))

    # Mapeo estricto del idioma solicitado
    lang_code = (request.lang or "es").lower()
    lang_names = {
        "es": "español formal y técnico",
        "en": "formal technical English",
        "sw": "Kiswahili sanifu na cha kitaalamu"
    }
    target_lang_str = lang_names.get(lang_code, "español formal y técnico")

    provider_name = ""
    execution_mode = ""
    orchestration_type = "Invocación Orquestada por Pipeline LCEL (Herramientas predefinidas)"
    generated_text = ""

    chain_input = {
        "observations": str(obs_res),
        "forecasts": str(forecast_res),
        "capacity": str(hosp_res),
        "query": f"{request.query} (Responde OBLIGATORIAMENTE en {target_lang_str})"
    }

    try:
        from langchain_ollama import ChatOllama
        llm = ChatOllama(
            base_url=ollama_base_url,
            model=ollama_model,
            temperature=0.1,
            timeout=ollama_timeout
        )
        components_executed.append(f"langchain_ollama.ChatOllama({ollama_model})")
        chain = prompt | llm | StrOutputParser()
        generated_text = chain.invoke(chain_input)
        if not generated_text or not generated_text.strip():
            raise ValueError(f"El modelo Ollama '{ollama_model}' retornó una respuesta vacía.")
        provider_name = f"Ollama Local LLM ({ollama_model}) vía LangChain LCEL"
        execution_mode = "LLM_LOCAL_OLLAMA (Generativo Trazable)"
    except Exception as ollama_exc:
        # Requisito 1: Cero fallbacks silenciosos a RunnableLambda con cifras inventadas o cableadas.
        # Si Ollama no está disponible o falla, elevar inmediatamente HTTP 503 explícito.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Servicio Ollama no disponible en {ollama_base_url} (modelo '{ollama_model}'): {str(ollama_exc)}. Inicie el servicio Ollama para ejecutar el agente LangChain."
        )

    elapsed_ms = (time.time() - start_time) * 1000.0

    return LangChainIntegrationResponse(
        query=request.query,
        cutoff_date=cutoff,
        database_observations=obs_res,
        model_forecasts=forecast_res,
        hospital_capacity=hosp_res,
        generated_text=generated_text,
        langchain_metadata=LangChainMetadata(
            framework="LangChain 1.4+ (langchain_core)",
            execution_mode=execution_mode,
            orchestration_type=orchestration_type,
            components_executed=components_executed,
            tools_invoked=tools_invoked,
            provider=provider_name,
            execution_time_ms=round(elapsed_ms, 2)
        )
    )

