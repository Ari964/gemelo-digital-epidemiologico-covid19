"""
Prueba de generación de API key en Langflow y ejecución del endpoint run.
"""
import requests
import json
import os

BASE_URL = "http://localhost:7860/api/v1"

def run_test():
    env_path = r"C:\Users\KRISTEL\Documents\langflow\docker_example\.env"
    pw = ""
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("LANGFLOW_SUPERUSER_PASSWORD="):
                pw = line.strip().split("=", 1)[1]
    
    # 1. Login
    resp = requests.post(
        f"{BASE_URL}/login",
        data={"username": "langflow", "password": pw},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10
    )
    token = resp.json()["access_token"]
    
    # 2. Get or create Langflow API Key
    keys_resp = requests.get(f"{BASE_URL}/api_key/", headers={"Authorization": f"Bearer {token}"})
    print("API keys list status:", keys_resp.status_code)
    
    api_key_val = None
    # Create an API key for testing
    new_key_resp = requests.post(
        f"{BASE_URL}/api_key/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "test_verification_key"}
    )
    if new_key_resp.status_code in [200, 201]:
        api_key_val = new_key_resp.json().get("api_key")
        print("Nueva API Key creada con éxito:", bool(api_key_val))
    else:
        print("Error creating key:", new_key_resp.status_code, new_key_resp.text)
    
    # 3. Test running flow with API Key
    flow_id = "906a3d58-bcf0-48a9-9364-4a62ea230945"
    run_url = f"{BASE_URL}/run/{flow_id}"
    
    payload = {
        "input_value": "Traduce la palabra 'vacuna' al chino",
        "input_type": "chat",
        "output_type": "chat"
    }
    
    headers = {"x-api-key": api_key_val} if api_key_val else {"Authorization": f"Bearer {token}"}
    run_resp = requests.post(run_url, json=payload, headers=headers, timeout=60)
    print("Run endpoint status:", run_resp.status_code)
    try:
        res = run_resp.json()
        print("Run result keys:", list(res.keys()) if isinstance(res, dict) else type(res))
        # Print outputs
        outputs = res.get("outputs", [])
        if outputs:
            first_out = outputs[0].get("outputs", [])
            print("First output preview:", json.dumps(first_out, indent=2)[:600])
        else:
            print("Result:", res)
    except Exception as e:
        print("Error parsing run output:", e, run_resp.text[:300])

if __name__ == "__main__":
    run_test()
