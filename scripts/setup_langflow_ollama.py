import json
import copy
import subprocess
import urllib.request

# 1. Load Basic Prompting as base template since it's known valid
cmd = ['docker', 'exec', 'docker_example-postgres-1', 'psql', '-U', 'langflow', '-d', 'langflow', '-t', '-A', '-c', 
       "SELECT data FROM flow WHERE id='e4eecf2d-14ff-4d42-9a57-77db12cfa527';"]
res = subprocess.check_output(cmd).decode()
flow_data = json.loads(res)

# 2. Modify LanguageModelComponent to use Ollama
for n in flow_data["nodes"]:
    if n.get("data", {}).get("type") == "LanguageModelComponent":
        tpl = n["data"]["node"]["template"]
        tpl["provider"]["value"] = "Ollama"
        tpl["model_name"]["value"] = "qwen2.5:0.5b"
        tpl["ollama_base_url"]["value"] = "http://host.docker.internal:11434"
        tpl["ollama_base_url"]["show"] = True
        tpl["model"]["value"] = [{
            "name": "qwen2.5:0.5b",
            "icon": "Ollama",
            "provider": "Ollama"
        }]
    elif n.get("data", {}).get("type") == "Prompt":
        tpl = n["data"]["node"]["template"]
        tpl["template"]["value"] = (
            "Eres el Asistente Epidemiológico del Gemelo Digital de Kenia en Langflow (conectado con Ollama local).\n"
            "DATOS VERIFICADOS OBLIGATORIOS:\n"
            "- Dataset: Our World in Data (OWID) / OMS, ISO KEN, 1,674 registros, SHA-256 c82f3cfc...\n"
            "- Modelo Campeón: Baseline_Naive_Persistence (CV RMSE: 1,183.64, Test MAE: 19.23 casos, MAPE: 515.49% por semanas de 0 casos).\n"
            "- Camas UCI en Kenia: 537 camas verificadas (Barasa et al. 2020 S1 Table). Nairobi: 276, Kiambu: 16, Mombasa: 35. 27 condados con 0 camas.\n"
            "- Censo Nacional: KNBS 2019 (47,564,296 habitantes).\n"
            "Responde de forma concisa, técnica y respetando estrictamente estos datos."
        )

# 3. Update flow in PostgreSQL
flow_id = "906a3d58-bcf0-48a9-9364-4a62ea230945"
sql_update = f"""UPDATE flow SET data = $json${json.dumps(flow_data)}$json$, updated_at = NOW() WHERE id = '{flow_id}';"""
p = subprocess.run(['docker', 'exec', '-i', 'docker_example-postgres-1', 'psql', '-U', 'langflow', '-d', 'langflow'],
                   input=sql_update, text=True, capture_output=True)
print("Postgres update:", p.stdout, p.stderr)

# 4. Save flow json to docs
with open("docs/flujo_epidemiologico_langflow_exportado.json", "w", encoding="utf-8") as f:
    json.dump({
        "id": flow_id,
        "name": "Asistente de Vigilancia Epidemiológica de Kenia",
        "description": "Flujo epidemiológico ejecutando Ollama local en host.docker.internal:11434 con datos auditados de OWID, KNBS 2019 y Barasa 2020.",
        "data": flow_data
    }, f, indent=2, ensure_ascii=False)
print("Saved clean flow export to docs/flujo_epidemiologico_langflow_exportado.json")
