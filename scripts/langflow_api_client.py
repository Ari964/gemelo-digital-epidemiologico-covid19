"""
Cliente de API autenticado para interactuar con la instalación local de Langflow en Docker.
"""
import requests
import json
import os

BASE_URL = "http://localhost:7860/api/v1"

def get_token():
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
    resp.raise_for_status()
    return resp.json()["access_token"]

def list_user_flows():
    token = get_token()
    resp = requests.get(
        f"{BASE_URL}/flows/",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    resp.raise_for_status()
    flows = resp.json()
    print(f"Total de flujos devueltos por API: {len(flows)}")
    for fl in flows:
        desc = (fl.get("description") or "")[:60]
        print(f"  - ID: {fl['id']} | Nombre: '{fl['name']}' | Descripción: '{desc}'")
    return flows

def get_flow_detail(flow_id):
    token = get_token()
    resp = requests.get(
        f"{BASE_URL}/flows/{flow_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    list_user_flows()
