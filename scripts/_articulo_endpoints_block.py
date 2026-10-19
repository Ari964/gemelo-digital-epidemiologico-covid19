# ===========================================================================
# Endpoints del Artículo Científico (GD_TI Fase 13)
# Sirven los resultados del Protocolo V2.0, figuras a 500 dpi y descargas.
# ===========================================================================

PROTOCOLO_RESULTS_PATH = os.path.join(get_project_root(), "models", "protocolo_v2", "protocolo_v2_resultados.json")
PROTOCOLO_FIGURES_DIR = os.path.join(get_project_root(), "docs", "figures", "protocolo_v2")
PROTOCOLO_EXPORT_DIR = os.path.join(get_project_root(), "docs", "export", "protocolo_v2")

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:0.5b")
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT_SECONDS", "60"))


def _load_protocolo_results() -> Dict[str, Any]:
    if not os.path.exists(PROTOCOLO_RESULTS_PATH):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resultados del protocolo v2.0 no encontrados: {PROTOCOLO_RESULTS_PATH}. Ejecute scripts/protocolo_temporal_v2.py."
        )
    with open(PROTOCOLO_RESULTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/articulo/resultados")
def get_articulo_resultados(current_user: UserDB = Depends(get_current_user)):
    """Devuelve el JSON completo de resultados del protocolo v2.0 (métricas, folds, U de Theil, mapa de calor, pruebas, interpretabilidad/explicabilidad)."""
    return _load_protocolo_results()


@router.get("/articulo/figura/{fig_name}")
def get_articulo_figura(fig_name: str, current_user: UserDB = Depends(get_current_user)):
    """Sirve una figura del protocolo v2.0 (PNG/SVG) para visualización en el artículo."""
    safe_name = os.path.basename(fig_name)
    path = os.path.join(PROTOCOLO_FIGURES_DIR, safe_name)
    if os.path.exists(path):
        media = "image/png" if safe_name.endswith(".png") else "image/svg+xml"
        return FileResponse(path, media_type=media, filename=safe_name)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Figura no encontrada: {fig_name}"
    )


@router.get("/articulo/descarga/{file_name}")
def get_articulo_descarga(file_name: str, current_user: UserDB = Depends(get_current_user)):
    """Descarga un archivo de datos del protocolo v2.0 (CSV o JSON)."""
    safe_name = os.path.basename(file_name)
    path = os.path.join(PROTOCOLO_EXPORT_DIR, safe_name)
    if not os.path.exists(path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Archivo de exportación no encontrado: {file_name}"
        )
    media = "application/json" if safe_name.endswith(".json") else ("text/csv" if safe_name.endswith(".csv") else "application/octet-stream")
    return FileResponse(path, media_type=media, filename=safe_name)


class SeleccionIARequest(BaseModel):
    modo: str = Field("auto", description="auto (Ollama) o manual")
    criterios: Optional[str] = Field(None, description="Criterios de selección adicionales")


def _seleccion_ia_ollama(resultados: Dict[str, Any], criterios: Optional[str]) -> Dict[str, Any]:
    """Consulta Ollama local para recomendar tablas y figuras del artículo. Nunca inventa evidencia."""
    import urllib.request
    elementos = []
    for sec_id, sec in resultados.get("interpretabilidad_explicabilidad", {}).items():
        elementos.append({
            "id": sec_id,
            "titulo": sec.get("titulo"),
            "tipo": "figura" if sec_id in ["particion_80_20", "observados_vs_predicciones", "residuos", "mapa_calor"] else "tabla",
            "disponible": True,
        })
    for key in ["u_de_theil", "pruebas_estadisticas"]:
        if key in resultados.get("interpretabilidad_explicabilidad", {}):
            elementos.append({"id": key, "titulo": resultados["interpretabilidad_explicabilidad"][key]["titulo"], "tipo": "tabla", "disponible": True})

    prompt = {
        "model": OLLAMA_MODEL,
        "system": "Eres un asistente de investigación científica. Recomienda SOLO tablas y figuras que existan en la lista proporcionada. No inventes cifras, evidencia ni referencias. Responde en español, en JSON válido, con claves: seleccion (lista de ids), justificacion (texto), criterios_usados (texto). No alteres datos del protocolo.",
        "template": "A continuación tienes los resultados científicos reales de un protocolo de evaluación temporal 80/20 con 5 folds y los elementos disponibles para el artículo científico. Selecciona los más relevantes, justificando relevancia, calidad y ausencia de redundancia. Elementos disponibles: " + json.dumps(elementos, ensure_ascii=False) + ". Criterios adicionales del usuario: " + str(criterios or "ninguno") + ".",
        "stream": False,
        "format": "json",
    }
    try:
        req = urllib.request.Request(
            OLLAMA_BASE_URL + "/api/generate",
            data=json.dumps(prompt).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        texto = data.get("response", "{}")
        try:
            seleccion_ia = json.loads(texto)
        except Exception:
            seleccion_ia = {"seleccion": [], "justificacion": "No se pudo parsear la respuesta de la IA.", "criterios_usados": str(criterios), "raw": texto}
        ids_validos = {e["id"] for e in elementos}
        seleccion_ia["seleccion"] = [i for i in seleccion_ia.get("seleccion", []) if i in ids_validos]
        seleccion_ia["modelo_utilizado"] = OLLAMA_MODEL
        seleccion_ia["origen"] = "ollama_local"
        seleccion_ia["fecha"] = datetime.utcnow().isoformat()
        return seleccion_ia
    except Exception as ex:
        return {
            "seleccion": [],
            "justificacion": f"Ollama no disponible ({ex}). Se selecciona manualmente por criterios explícitos.",
            "criterios_usados": str(criterios),
            "modelo_utilizado": None,
            "origen": "fallback_manual",
            "fecha": datetime.utcnow().isoformat(),
            "error": str(ex),
        }


@router.post("/articulo/seleccion-ia")
def post_articulo_seleccion_ia(req: SeleccionIARequest, current_user: UserDB = Depends(get_current_user)):
    """Selección asistida por IA de tablas y figuras para el artículo. Si Ollama no está disponible, usa criterios manuales explícitos."""
    resultados = _load_protocolo_results()
    if req.modo == "auto":
        ia = _seleccion_ia_ollama(resultados, req.criterios)
    else:
        ia = {
            "seleccion": ["particion_80_20", "mapa_calor", "observados_vs_predicciones", "u_de_theil", "resultados_por_modelo", "pruebas_estadisticas"],
            "justificacion": "Selección manual por criterios explícitos: partición, mapa de calor, series observado/predicho, U de Theil, comparación de modelos y pruebas estadísticas son los elementos centrales del artículo.",
            "criterios_usados": req.criterios or "relevancia central al artículo",
            "modelo_utilizado": None,
            "origen": "manual_explícito",
            "fecha": datetime.utcnow().isoformat(),
        }
    ie = resultados.get("interpretabilidad_explicabilidad", {})
    recomendados = []
    for sid in ia.get("seleccion", []):
        if sid in ie:
            recomendados.append({"id": sid, "titulo": ie[sid]["titulo"], "interpretabilidad": ie[sid]["interpretabilidad"], "explicabilidad": ie[sid]["explicabilidad"]})
    ia["recomendados_detalle"] = recomendados
    return {"resultado_base": resultados, "seleccion_ia": ia}


@router.get("/articulo/paquete")
def get_articulo_paquete(current_user: UserDB = Depends(get_current_user)):
    """Descarga un paquete ZIP con el JSON de resultados, todas las figuras (PNG+SVG) y los CSV de exportación."""
    resultados = _load_protocolo_results()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("protocolo_v2_resultados.json", json.dumps(resultados, indent=2, ensure_ascii=False))
        fig_dir = PROTOCOLO_FIGURES_DIR
        for fname in os.listdir(fig_dir):
            if fname.endswith((".png", ".svg")):
                z.write(os.path.join(fig_dir, fname), arcname="figures/" + fname)
        exp_dir = PROTOCOLO_EXPORT_DIR
        for fname in os.listdir(exp_dir):
            if fname.endswith((".csv", ".json")):
                z.write(os.path.join(exp_dir, fname), arcname="export/" + fname)
    buffer.seek(0)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return Response(
        content=buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=GD_TI_Articulo_Paquete_{ts}.zip"},
    )
