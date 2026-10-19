import os
import json
import urllib.request
import urllib.error
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.core.config import settings
from backend.app.models.user import UserDB
from backend.app.api.deps import get_current_user

router = APIRouter()

class ChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = None
    simulation_context: Optional[Dict[str, Any]] = None
    lang: Optional[str] = Field("es", description="Código de idioma objetivo: es, en, sw")

class ChatResponse(BaseModel):
    reply: str
    model: str
    sources_cited: List[str]
    latency_ms: float

@router.post("", response_model=ChatResponse)
def copilot_chat(
    req: ChatRequest,
    current_user: UserDB = Depends(get_current_user)
):
    base_url = (os.getenv("OLLAMA_BASE_URL") or settings.OLLAMA_BASE_URL).rstrip("/")
    model_name = os.getenv("OLLAMA_MODEL") or settings.OLLAMA_MODEL
    timeout_sec = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", str(settings.OLLAMA_TIMEOUT_SECONDS)))

    # Mapeo y solicitud estricta del idioma al modelo local Ollama
    lang_code = (req.lang or "es").lower()
    lang_names = {
        "es": "español formal y técnico",
        "en": "formal technical English",
        "sw": "Kiswahili sanifu na cha kitaalamu"
    }
    target_lang_str = lang_names.get(lang_code, "español formal y técnico")

    # Instrucción sistemática con rigor epistemológico y científico
    system_instruction = (
        f"Eres el Copiloto Epidemiológico de Inteligencia Artificial para el Gemelo Digital "
        f"Poblacional de Kenia (47 condados). Responde OBLIGATORIAMENTE en {target_lang_str}.\n\n"
        f"REGLAS METODOLÓGICAS ESTRICTAS:\n"
        f"1. DISTINCIÓN CATEGORIAL OBLIGATORIA:\n"
        f"   - DATOS OBSERVADOS EMPÍRICOS: Serie histórica oficial semanal OWID/OMS de Kenia "
        f"     (1,674 registros válidos, SHA-256 c82f3cfc..., rango temporal 2020-01-05 a 2024-08-04) y Censo KNBS 2019.\n"
        f"   - PRONÓSTICOS DE MODELOS ESTADÍSTICOS: Persistencia Naive seleccionada ex-ante como campeón "
        f"     de vigilancia mediante validación cruzada temporal en desarrollo (Test MAE: 19.23, RMSE: 55.64; "
        f"     el Test MAPE de 515.49% se debe a la inestabilidad matemática por semanas de incidencia 0 o 1 caso en el denominador). "
        f"     Random Forest es únicamente una exploración de sensibilidad no causal (grid n_estimators=[50,100], max_depth=[3,5,8], min_samples_split=[2,5]).\n"
        f"   - SIMULACIONES MECANICISTAS SEIR/ABM: Escenarios prospectivos contrafácticos a nivel de agentes "
        f"     para evaluar NPIs y equidad vacunal (DPR). Sus cifras NO son observaciones condales ni métricas del pronóstico semanal.\n"
        f"2. HONESTIDAD CIENTÍFICA ANTE DATOS FALTANTES: Si el usuario consulta un dato que no consta en los registros "
        f"   del sistema (por ejemplo, saturación UCI condal o incidencia no registrada), indica claramente que no se dispone del dato. "
        f"   NUNCA inventes números o supuestos clínicos no verificados.\n"
        f"3. Cita fuentes oficiales verificables: KNBS 2019, KDHS 2022, KMFL 2021, Barasa et al. 2020, OWID/OMS."
    )

    prompt_context = ""
    if req.simulation_context:
        prompt_context = f"\nContexto de la simulación o parámetros activos en el sistema:\n{json.dumps(req.simulation_context, ensure_ascii=False, indent=2)}\n"

    history_text = ""
    if req.conversation_history:
        for msg in req.conversation_history[-6:]:
            history_text += f"{msg.role.upper()}: {msg.content}\n"

    full_prompt = (
        f"{system_instruction}\n"
        f"{prompt_context}\n"
        f"{history_text}"
        f"USUARIO ({current_user.name}): {req.message}\n"
        f"RESPUESTA (en {target_lang_str}):"
    )

    ollama_endpoint = f"{base_url}/api/generate"
    payload = {
        "model": model_name,
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
            "num_predict": 128
        }
    }

    t0 = time.time()
    try:
        req_data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            ollama_endpoint,
            data=req_data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(request, timeout=timeout_sec) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            reply_text = res_json.get("response", "").strip()
            elapsed_ms = (time.time() - t0) * 1000.0

            if not reply_text:
                raise ValueError("Ollama retornó una respuesta vacía.")

            return ChatResponse(
                reply=reply_text,
                model=f"Ollama ({model_name})",
                sources_cited=[
                    "KNBS Census 2019",
                    "KDHS 2022",
                    "KMFL 2021",
                    "Barasa et al. (2020) PLOS ONE",
                    "OWID Weekly COVID-19 Surveillance (KEN)"
                ],
                latency_ms=round(elapsed_ms, 2)
            )
    except urllib.error.URLError as url_err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"Servicio de IA Ollama inaccesible en {base_url} ({str(url_err)}). "
                f"Verifique que Ollama esté iniciado ('ollama serve') y que el modelo "
                f"'{model_name}' haya sido descargado ('ollama pull {model_name}'). "
                f"Por rigor científico, no se presentan respuestas ficticias o heurísticas simuladas."
            )
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"Error al consultar el modelo Ollama '{model_name}' en {base_url}: {str(exc)}. "
                f"Verifique los recursos del sistema y la configuración del servicio local de inferencia."
            )
        )
