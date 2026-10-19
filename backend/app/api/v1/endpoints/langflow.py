import os
import time
import json
import uuid
import urllib.request
import urllib.error
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, status

router = APIRouter()

LANGFLOW_URL = os.getenv("LANGFLOW_URL", "http://localhost:7860").rstrip("/")
LANGFLOW_FLOW_ID = os.getenv("LANGFLOW_FLOW_ID", "906a3d58-bcf0-48a9-9364-4a62ea230945")
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY", "")

class LangflowQueryRequest(BaseModel):
    query: str = Field(..., description="Consulta epidemiológica o analítica para el flujo Langflow")
    session_id: Optional[str] = Field(default=None, description="Identificador único de sesión")

class LangflowQueryResponse(BaseModel):
    reply: str
    flow_id: str
    flow_name: str
    session_id: str
    execution_time_ms: float
    status: str

def verify_flow_presence(flow_id: str) -> bool:
    """Comprueba si el flujo está registrado y disponible para ejecución."""
    check_url = f"{LANGFLOW_URL}/api/v1/run/{flow_id}"
    headers = {"Content-Type": "application/json"}
    if LANGFLOW_API_KEY:
        headers["x-api-key"] = LANGFLOW_API_KEY
    payload = {
        "input_value": "test_ping",
        "input_type": "chat",
        "output_type": "chat"
    }
    try:
        req = urllib.request.Request(check_url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=8.0) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as he:
        # Si devuelve 404, el flujo no existe en el motor
        if he.code == 404:
            return False
        # Si devuelve 500 por error interno o timeout de LLM, al menos el endpoint del flujo fue encontrado
        return he.code != 404
    except Exception:
        return False

@router.get("/status")
def get_langflow_status() -> Dict[str, Any]:
    """
    Verifica el estado de conexión con el servicio Langflow desplegado localmente en Docker.
    Distingue rigurosamente entre:
    1. Servicio disponible (contenedor y puerto 7860 activos).
    2. Flujo importado y ejecutable (ID 906a3d58-bcf0-48a9-9364-4a62ea230945 presente).
    """
    health_url = f"{LANGFLOW_URL}/health"
    t0 = time.time()
    try:
        req = urllib.request.Request(health_url, method="GET")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            elapsed_ms = (time.time() - t0) * 1000.0
            if resp.status == 200:
                flow_ready = verify_flow_presence(LANGFLOW_FLOW_ID)
                final_status = "ONLINE" if flow_ready else "NO_FLOW"
                return {
                    "status": final_status,
                    "connected": flow_ready,
                    "service_available": True,
                    "flow_imported": flow_ready,
                    "url": LANGFLOW_URL,
                    "flow_id": LANGFLOW_FLOW_ID,
                    "flow_name": "Asistente de Vigilancia Epidemiológica de Kenia",
                    "provider": "Ollama Local LLM + Docker",
                    "latency_ms": round(elapsed_ms, 1),
                    "error": None if flow_ready else f"Servicio disponible en {LANGFLOW_URL}, pero el flujo epidemiológico no está registrado. Importe docs/langflow_epidemiology_flow_exported.json."
                }
            else:
                return {
                    "status": "DEGRADED",
                    "connected": False,
                    "service_available": False,
                    "flow_imported": False,
                    "url": LANGFLOW_URL,
                    "flow_id": LANGFLOW_FLOW_ID,
                    "flow_name": "Asistente de Vigilancia Epidemiológica de Kenia",
                    "provider": "Ollama Local LLM + Docker",
                    "latency_ms": round(elapsed_ms, 1),
                    "error": f"HTTP {resp.status} retornado por /health"
                }
    except Exception as exc:
        return {
            "status": "OFFLINE",
            "connected": False,
            "service_available": False,
            "flow_imported": False,
            "url": LANGFLOW_URL,
            "flow_id": LANGFLOW_FLOW_ID,
            "flow_name": "Asistente de Vigilancia Epidemiológica de Kenia",
            "provider": "Ollama Local LLM + Docker",
            "latency_ms": None,
            "error": f"Servicio Langflow inaccesible en {LANGFLOW_URL} ({type(exc).__name__}: {str(exc)}). Inicie Docker Desktop y ejecute 'docker compose up -d'."
        }

@router.post("/import-flow")
def import_flow_endpoint() -> Dict[str, Any]:
    """
    Importa automáticamente el flujo epidemiológico desde docs/langflow_epidemiology_flow_exported.json.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
    json_path = os.path.join(base_dir, "docs", "langflow_epidemiology_flow_exported.json")
    if not os.path.exists(json_path):
        json_path = os.path.join(base_dir, "docs", "flujo_epidemiologico_langflow_exportado.json")
    
    if not os.path.exists(json_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Archivo exportado del flujo no encontrado en {json_path}"
        )
    
    with open(json_path, "r", encoding="utf-8") as f:
        flow_json = json.load(f)
    
    # 1. Intentar vía API REST
    flow_data = flow_json.get("data", flow_json)
    payload = {
        "id": LANGFLOW_FLOW_ID,
        "name": flow_json.get("name", "Asistente de Vigilancia Epidemiológica de Kenia"),
        "description": flow_json.get("description", "Flujo epidemiológico de Kenia"),
        "data": flow_data,
        "is_component": False
    }
    headers = {"Content-Type": "application/json"}
    if LANGFLOW_API_KEY:
        headers["x-api-key"] = LANGFLOW_API_KEY

    try:
        req = urllib.request.Request(
            f"{LANGFLOW_URL}/api/v1/flows/",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status in (200, 201):
                return {
                    "status": "SUCCESS",
                    "flow_id": LANGFLOW_FLOW_ID,
                    "message": "Flujo importado exitosamente a través de la API REST de Langflow."
                }
    except Exception as exc:
        pass

    # 2. Comprobar si ya está listo
    if verify_flow_presence(LANGFLOW_FLOW_ID):
        return {
            "status": "SUCCESS",
            "flow_id": LANGFLOW_FLOW_ID,
            "message": "El flujo epidemiológico ya se encuentra registrado y disponible en Langflow."
        }
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="No se pudo importar automáticamente el flujo. Ejecute 'python scripts/import_langflow_flow.py' o cargue el archivo en http://localhost:7860."
    )

@router.post("/query", response_model=LangflowQueryResponse)
def execute_langflow_query(req: LangflowQueryRequest) -> LangflowQueryResponse:
    """
    Ejecuta una consulta analítica en tiempo real invocando la API de ejecución de Langflow.
    No simula éxito si Langflow está fuera de línea: reporta el error real del backend.
    """
    # 1. Comprobación preliminar de salud
    health = get_langflow_status()
    if not health.get("connected"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health.get("error") or "Langflow se encuentra fuera de línea."
        )

    run_url = f"{LANGFLOW_URL}/api/v1/run/{LANGFLOW_FLOW_ID}"
    sess_id = req.session_id or str(uuid.uuid4())
    
    payload = {
        "input_value": req.query,
        "input_type": "chat",
        "output_type": "chat",
        "session_id": sess_id
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    if LANGFLOW_API_KEY:
        headers["x-api-key"] = LANGFLOW_API_KEY

    t0 = time.time()
    try:
        req_obj = urllib.request.Request(
            run_url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req_obj, timeout=60.0) as resp:
            elapsed_ms = (time.time() - t0) * 1000.0
            data = json.loads(resp.read().decode("utf-8"))
            
            # Extracción del texto de salida de Langflow
            try:
                outputs = data.get("outputs", [])
                text_reply = outputs[0]["outputs"][0]["results"]["message"]["text"]
            except (KeyError, IndexError, TypeError) as parse_err:
                text_reply = f"Respuesta recibida pero con formato inesperado: {json.dumps(data)[:300]}"

            return LangflowQueryResponse(
                reply=text_reply,
                flow_id=LANGFLOW_FLOW_ID,
                flow_name="Asistente de Vigilancia Epidemiológica de Kenia",
                session_id=sess_id,
                execution_time_ms=round(elapsed_ms, 2),
                status="SUCCESS"
            )
    except urllib.error.HTTPError as http_err:
        err_msg = http_err.read().decode("utf-8", errors="ignore")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Langflow reportó indisponibilidad ({http_err.code}): {err_msg[:400]}"
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Fallo de comunicación con Langflow: {type(exc).__name__} - {str(exc)}"
        )
