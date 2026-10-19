"""
Inspección de las claves del template en Agent-EXpSZ.
"""
import subprocess
import json

def inspect_keys():
    cmd = [
        "docker", "exec", "docker_example-postgres-1",
        "psql", "-U", "langflow", "-d", "langflow", "-t", "-A", "-c",
        "SELECT data FROM flow WHERE id = '906a3d58-bcf0-48a9-9364-4a62ea230945';"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    data = json.loads(res.stdout.strip())
    for n in data.get("nodes", []):
        if n.get("id") == "Agent-EXpSZ":
            t = n.get("data", {}).get("node", {}).get("template", {})
            for k, v in t.items():
                if isinstance(v, dict):
                    print(f"Key: {k} -> type={v.get('type')}, value={v.get('value')}, load_from_db={v.get('load_from_db')}")
                else:
                    print(f"Key: {k} -> {v}")

if __name__ == "__main__":
    inspect_keys()
