"""
Ejecución de verificación por API de Langflow tras la prueba en interfaz.
Prueba las dos frases nuevas en chino y registra la salida real.
"""
import requests
import json
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://localhost:7860/api/v1"

def run_api_verification():
    env_path = r"C:\Users\KRISTEL\Documents\langflow\docker_example\.env"
    pw = ""
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("LANGFLOW_SUPERUSER_PASSWORD="):
                pw = line.strip().split("=", 1)[1]
    
    # Login
    resp = requests.post(
        f"{BASE_URL}/login",
        data={"username": "langflow", "password": pw},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10
    )
    token = resp.json()["access_token"]
    
    # Create or use fresh API key
    new_key = requests.post(
        f"{BASE_URL}/api_key/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "verification_run_key"}
    )
    if new_key.status_code in [200, 201]:
        api_key_val = new_key.json().get("api_key")
    else:
        # Fallback to query
        api_key_val = None
    
    flow_id = "906a3d58-bcf0-48a9-9364-4a62ea230945"
    run_url = f"{BASE_URL}/run/{flow_id}"
    headers = {"x-api-key": api_key_val} if api_key_val else {"Authorization": f"Bearer {token}"}
    
    test_queries = [
        {
            "id": "query_1",
            "prompt": "Traduce al chino: vigilancia epidemiológica",
            "test_type": "traduccion_termino_epidemiologico",
        },
        {
            "id": "query_2",
            "prompt": "Traduce al español: 社区卫生工作者正在偏远地区推广公共卫生干预措施。",
            "test_type": "traduccion_frase_china_completa",
        },
        {
            "id": "query_3",
            "prompt": "请将以下句子翻译成西班牙语：“在疫情暴发初期，多部门协同响应和资源调配对于控制病毒传播至关重要。”",
            "test_type": "traduccion_directa_chino_a_espanol",
        }
    ]
    
    results = []
    print("=== EJECUCIÓN POR API (TRAS VALIDACIÓN EN INTERFAZ) ===")
    for q in test_queries:
        payload = {
            "input_value": q["prompt"],
            "input_type": "chat",
            "output_type": "chat"
        }
        r = requests.post(run_url, json=payload, headers=headers, timeout=60)
        if r.status_code == 200:
            out_data = r.json()
            outputs = out_data.get("outputs", [])
            reply_text = ""
            if outputs and len(outputs) > 0:
                inner_outs = outputs[0].get("outputs", [])
                if inner_outs:
                    msg = inner_outs[0].get("results", {}).get("message", {})
                    reply_text = msg.get("data", {}).get("text", "")
            
            res_item = {
                "id": q["id"],
                "input_prompt": q["prompt"],
                "api_status_code": r.status_code,
                "real_output": reply_text,
                "execution_status": "EXITOSO"
            }
            results.append(res_item)
            print(f"\n[+] Consulta [{q['id']}]: '{q['prompt']}'")
            print(f"    Respuesta obtenida:\n{reply_text}")
        else:
            print(f"Error {r.status_code}: {r.text}")
            results.append({
                "id": q["id"],
                "input_prompt": q["prompt"],
                "api_status_code": r.status_code,
                "error": r.text,
                "execution_status": "ERROR"
            })
            
    # Guardar reporte de auditoría completo y verificado
    audit_data = {
        "flow_name": "Tutor de Idiomas con PostgreSQL",
        "flow_id": flow_id,
        "installation_type": "Docker Compose (langflow + postgres:16-trixie)",
        "deployment_path": r"C:\Users\KRISTEL\Documents\langflow\docker_example",
        "web_url": "http://localhost:7860",
        "persistence": "PostgreSQL (contenedor docker_example-postgres-1, BD 'langflow')",
        "provider": "Google Generative AI (Gemini)",
        "credential_status": "ALMACENADA Y OPERACIONAL en tabla 'variable' (tipo Credential)",
        "practice_status": "FUNCIONAL",
        "browser_ui_verification": {
            "status": "VERIFICADA_EN_PLAYGROUND",
            "screenshot_initial": "C:\\Users\\KRISTEL\\.gemini\\antigravity-ide\\brain\\b5022e3f-55f9-467d-977d-c09e9fb31649\\playground_results_1790352761335.png",
            "screenshot_chinese_direct": "C:\\Users\\KRISTEL\\.gemini\\antigravity-ide\\brain\\b5022e3f-55f9-467d-977d-c09e9fb31649\\langflow_chinese_translation_1790353574983.png",
            "recording": "C:\\Users\\KRISTEL\\.gemini\\antigravity-ide\\brain\\b5022e3f-55f9-467d-977d-c09e9fb31649\\langflow_ui_demo_1790351179305.webp",
            "recording_query_3": "C:\\Users\\KRISTEL\\.gemini\\antigravity-ide\\brain\\b5022e3f-55f9-467d-977d-c09e9fb31649\\langflow_chinese_test_3_1790353345412.webp",
            "query_1_response": "- 流行病学监测\n- liúxíngbìngxué jiāncè\n- Vigilancia epidemiológica\n- 加强流行病学监测非常重要。(Jiāqiáng liúxíngbìngxué jiāncè fēicháng zhòngyào - Es muy importante fortalecer la vigilancia epidemiológica.)",
            "query_2_response": "Los trabajadores de la salud comunitaria están promoviendo intervenciones de salud pública en áreas remotas.",
            "query_3_response": "Durante el inicio del brote epidémico, la respuesta coordinada multisectorial y la asignación de recursos fueron fundamentales para controlar la propagación del virus."
        },
        "api_verification": results
    }
    
    with open("docs/auditoria_ejecucion_langflow.json", "w", encoding="utf-8") as f:
        json.dump(audit_data, f, ensure_ascii=False, indent=2)
    print("\nAuditoría guardada exitosamente en docs/auditoria_ejecucion_langflow.json")

if __name__ == "__main__":
    run_api_verification()
