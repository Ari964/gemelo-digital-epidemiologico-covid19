"""
Exporta el flujo del usuario 'Tutor de Idiomas con PostgreSQL' a docs/ y registra sus componentes.
"""
import requests
import json
import os

BASE_URL = "http://localhost:7860/api/v1"

def export_flow():
    env_path = r"C:\Users\KRISTEL\Documents\langflow\docker_example\.env"
    pw = ""
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("LANGFLOW_SUPERUSER_PASSWORD="):
                pw = line.strip().split("=", 1)[1]
    
    resp = requests.post(
        f"{BASE_URL}/login",
        data={"username": "langflow", "password": pw},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10
    )
    token = resp.json()["access_token"]
    
    flow_id = "906a3d58-bcf0-48a9-9364-4a62ea230945"
    flow_resp = requests.get(f"{BASE_URL}/flows/{flow_id}", headers={"Authorization": f"Bearer {token}"})
    flow_data = flow_resp.json()
    
    export_path = os.path.join("docs", "flujo_traductor_langflow_exportado.json")
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(flow_data, f, ensure_ascii=False, indent=2)
    
    print(f"Flujo '{flow_data['name']}' exportado exitosamente a: {export_path}")
    print(f"ID: {flow_data['id']}")
    print(f"Descripción: {flow_data.get('description')}")
    
    nodes = flow_data.get("data", {}).get("nodes", [])
    print(f"\nComponentes registrados ({len(nodes)}):")
    for n in nodes:
        node_id = n.get("id")
        display_name = n.get("data", {}).get("node", {}).get("display_name", node_id)
        comp_type = n.get("data", {}).get("type", "")
        print(f"  - [{node_id}] {display_name} (Tipo: {comp_type})")

if __name__ == "__main__":
    export_flow()
