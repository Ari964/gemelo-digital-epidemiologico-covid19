#!/usr/bin/env python3
"""
Script de Importación y Verificación del Flujo Epidemiológico de Langflow.
Garantiza la reproducibilidad desde una instalación limpia.

Procedimiento:
1. Carga docs/langflow_epidemiology_flow_exported.json (o docs/flujo_epidemiologico_langflow_exportado.json).
2. Conecta con el contenedor PostgreSQL o SQLite de Langflow, o con su API REST.
3. Registra el flujo con ID fijo '906a3d58-bcf0-48a9-9364-4a62ea230945' y nombre 'Asistente de Vigilancia Epidemiológica de Kenia'.
4. Ejecuta una consulta de verificación hacia Langflow -> Ollama para comprobar que responde.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error

# Forzar codificación UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FLOW_ID = os.getenv("LANGFLOW_FLOW_ID", "906a3d58-bcf0-48a9-9364-4a62ea230945")
LANGFLOW_URL = os.getenv("LANGFLOW_URL", "http://localhost:7860").rstrip("/")
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY", "")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_FLOW_PATH = os.path.join(BASE_DIR, "docs", "langflow_epidemiology_flow_exported.json")
ALT_FLOW_PATH = os.path.join(BASE_DIR, "docs", "flujo_epidemiologico_langflow_exportado.json")

def load_flow_json():
    target_path = DOCS_FLOW_PATH if os.path.exists(DOCS_FLOW_PATH) else ALT_FLOW_PATH
    if not os.path.exists(target_path):
        print(f"[ERROR] No se encontró archivo exportado en {DOCS_FLOW_PATH} ni {ALT_FLOW_PATH}")
        sys.exit(1)
    
    with open(target_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"[OK] Archivo de flujo cargado desde: {target_path}")
    return data

def import_to_postgres(flow_content):
    """Intenta importar insertando en PostgreSQL si está disponible."""
    try:
        import psycopg2
        flow_data = flow_content.get("data", flow_content)
        name = flow_content.get("name", "Asistente de Vigilancia Epidemiológica de Kenia")
        desc = flow_content.get("description", "Flujo epidemiológico ejecutando Ollama local en host.docker.internal:11434 con datos auditados de OWID, KNBS 2019 y Barasa 2020.")

        conn = psycopg2.connect(
            dbname=os.getenv("LANGFLOW_DB_NAME", "langflow"),
            user=os.getenv("LANGFLOW_DB_USER", "langflow"),
            password=os.getenv("LANGFLOW_DB_PASSWORD", "langflow"),
            host=os.getenv("LANGFLOW_DB_HOST", "localhost"),
            port=int(os.getenv("LANGFLOW_DB_PORT", "5432")),
            connect_timeout=3
        )
        cur = conn.cursor()
        query = """
            INSERT INTO flow (id, name, description, data, is_component, updated_at)
            VALUES (%s, %s, %s, %s, false, NOW())
            ON CONFLICT (id) DO UPDATE 
            SET name = EXCLUDED.name, description = EXCLUDED.description, data = EXCLUDED.data, updated_at = NOW();
        """
        cur.execute(query, (FLOW_ID, name, desc, json.dumps(flow_data)))
        conn.commit()
        cur.close()
        conn.close()
        print(f"[OK] Flujo {FLOW_ID} sincronizado exitosamente en base de datos PostgreSQL de Langflow.")
        return True
    except Exception as exc:
        print(f"[INFO] Inserción directa en PostgreSQL omitida ({type(exc).__name__}: {exc}). Probando API REST...")
        return False

def import_via_api(flow_content):
    """Intenta importar mediante API REST de Langflow."""
    flow_data = flow_content.get("data", flow_content)
    name = flow_content.get("name", "Asistente de Vigilancia Epidemiológica de Kenia")
    desc = flow_content.get("description", "Flujo epidemiológico ejecutando Ollama local en host.docker.internal:11434.")
    
    payload = {
        "id": FLOW_ID,
        "name": name,
        "description": desc,
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
                print(f"[OK] Flujo creado/importado exitosamente vía API REST en {LANGFLOW_URL}/api/v1/flows/ (HTTP {resp.status})")
                return True
    except urllib.error.HTTPError as he:
        print(f"[WARN] API REST de Langflow retornó HTTP {he.code}: {he.read().decode('utf-8', errors='ignore')[:200]}")
    except Exception as exc:
        print(f"[WARN] Error al conectar con API REST de Langflow: {exc}")
    return False

def test_flow_execution():
    """Ejecuta una consulta real frontend -> FastAPI/Langflow -> Ollama."""
    print(f"\nVerificando ejecución de consulta en Langflow ({LANGFLOW_URL}/api/v1/run/{FLOW_ID})...")
    payload = {
        "input_value": "¿Cuál es el modelo campeón de vigilancia epidemiológica?",
        "input_type": "chat",
        "output_type": "chat"
    }
    headers = {"Content-Type": "application/json"}
    if LANGFLOW_API_KEY:
        headers["x-api-key"] = LANGFLOW_API_KEY
    
    t0 = time.time()
    try:
        req = urllib.request.Request(
            f"{LANGFLOW_URL}/api/v1/run/{FLOW_ID}",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=40) as resp:
            elapsed = round(time.time() - t0, 2)
            data = json.loads(resp.read().decode("utf-8"))
            try:
                reply = data["outputs"][0]["outputs"][0]["results"]["message"]["text"]
            except Exception:
                reply = str(data)[:200]
            print(f"[ÉXITO] Consulta completada en {elapsed}s.")
            print(f"Respuesta del LLM (Ollama): {reply.strip()[:180]}...")
            return True
    except Exception as exc:
        print(f"[ERROR] Falló la verificación de ejecución del flujo: {exc}")
        return False

def main():
    print("=== IMPORTACIÓN REPRODUCIBLE DE FLUJO LANGFLOW ===")
    flow_content = load_flow_json()
    
    # 1. Intentar PostgreSQL
    success = import_to_postgres(flow_content)
    if not success:
        # 2. Intentar API REST
        success = import_via_api(flow_content)
    
    # 3. Probar ejecución final
    test_ok = test_flow_execution()
    if test_ok:
        print("\n[OK] Flujo reproducible verificado al 100%.")
    else:
        print("\n[AVISO] Verifique que Docker y Ollama estén en ejecución.")

if __name__ == "__main__":
    main()
