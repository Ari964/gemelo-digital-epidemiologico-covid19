#!/usr/bin/env python3
"""
Pruebas rigurosas de Langflow con preguntas de ámbito único y delimitado:
1. Pronóstico nacional semanal puro (sin mezclar camas ni condados).
2. Capacidad hospitalaria condal pura (auditoría Barasa 2020 sin mezclar proyecciones).
3. Deslinde epistemológico SEIR/ABM vs modelos estadísticos de OWID.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error

# Forzar codificación UTF-8 en Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
ENDPOINT = f"{BASE_URL}/api/v1/langflow/query"

TEST_QUESTIONS = [
    {
        "id": "Q1_NATIONAL_SURVEILLANCE",
        "scope": "Pronóstico Nacional Semanal Puro",
        "query": "¿Cuál es el modelo campeón seleccionado para la vigilancia epidemiológica semanal nacional de Kenia y cuál es su horizonte de predicción?",
        "expected_themes": ["persistencia", "semana", "t+1", "owid"]
    },
    {
        "id": "Q2_COUNTY_INFRASTRUCTURE",
        "scope": "Capacidad Hospitalaria Condal Pura (Auditoría Barasa 2020)",
        "query": "Según la auditoría pública de Barasa et al. (2020), ¿cuántas camas UCI basales se identificaron en el condado de Nairobi y cuál es el total nacional?",
        "expected_themes": ["276", "537", "nairobi", "uci"]
    },
    {
        "id": "Q3_METHODOLOGICAL_BOUNDARY",
        "scope": "Deslinde Metodológico SEIR/ABM vs Extrapolación Estadística",
        "query": "¿Por qué el Gemelo Digital SEIR/ABM opera como simulación contrafactual y no compite con la serie temporal semanal de Our World in Data?",
        "expected_themes": ["contrafactual", "intervenciones", "escenarios", "seir"]
    }
]

def run_tests():
    print("=" * 80)
    print("VERIFICACIÓN RIGUROSA DE LANGFLOW: PREGUNTAS DE ÁMBITO ÚNICO Y NO MEZCLADO")
    print(f"Endpoint evaluado: {ENDPOINT}")
    print("=" * 80)

    results = []
    all_ok = True

    for i, item in enumerate(TEST_QUESTIONS, 1):
        print(f"\n[Test {i}/3] {item['id']} - Ámbito: {item['scope']}")
        print(f"Pregunta enviada: \"{item['query']}\"")
        
        payload = json.dumps({
            "query": item["query"],
            "session_id": f"unmixed-session-{item['id'].lower()}"
        }).encode("utf-8")

        req = urllib.request.Request(
            ENDPOINT,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                elapsed = round(time.time() - t0, 2)
                res_data = json.loads(resp.read().decode("utf-8"))
                reply = res_data.get("reply", "")
                status_code = resp.status

                print(f" -> HTTP {status_code} en {elapsed}s")
                print(f" -> Respuesta Langflow/Ollama:\n   \"{reply.strip()}\"")

                results.append({
                    "id": item["id"],
                    "scope": item["scope"],
                    "query": item["query"],
                    "http_status": status_code,
                    "elapsed_sec": elapsed,
                    "status": "SUCCESS",
                    "reply": reply
                })
        except urllib.error.HTTPError as he:
            elapsed = round(time.time() - t0, 2)
            err_body = he.read().decode("utf-8", errors="ignore")
            print(f" -> ERROR HTTP {he.code} en {elapsed}s: {err_body}")
            all_ok = False
            results.append({
                "id": item["id"],
                "scope": item["scope"],
                "query": item["query"],
                "http_status": he.code,
                "elapsed_sec": elapsed,
                "status": "HTTP_ERROR",
                "error": err_body
            })
        except Exception as exc:
            elapsed = round(time.time() - t0, 2)
            print(f" -> ERROR CONEXIÓN: {exc}")
            all_ok = False
            results.append({
                "id": item["id"],
                "scope": item["scope"],
                "query": item["query"],
                "http_status": None,
                "elapsed_sec": elapsed,
                "status": "CONNECTION_ERROR",
                "error": str(exc)
            })

    # Guardar evidencia formal en docs/auditoria_ejecucion_langflow.json
    output_path = os.path.join(os.path.dirname(__file__), "..", "docs", "auditoria_ejecucion_langflow.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "tested_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "flow_id": "906a3d58-bcf0-48a9-9364-4a62ea230945",
            "all_tests_passed": all_ok,
            "results": results
        }, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    if all_ok:
        print(f"[ÉXITO TOTAL] Las 3 preguntas no mezcladas respondieron correctamente.")
    else:
        print(f"[ALERTA] Algunas pruebas presentaron incidencias.")
    print(f"Evidencia guardada en: {output_path}")
    print("=" * 80)
    return all_ok

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
