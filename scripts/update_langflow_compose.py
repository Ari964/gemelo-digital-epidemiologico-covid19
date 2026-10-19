import os

compose_path = r"C:\Users\KRISTEL\Documents\langflow\docker_example\docker-compose.yml"
with open(compose_path, "r", encoding="utf-8") as f:
    text = f.read()

target = "- LANGFLOW_CONFIG_DIR=/app/langflow"
replacement = """- LANGFLOW_CONFIG_DIR=/app/langflow
      - LANGFLOW_SSRF_ALLOWED_HOSTS=host.docker.internal,localhost,127.0.0.1,192.168.65.254
      - LANGFLOW_SSRF_ENABLED=false"""

if target in text and "LANGFLOW_SSRF_ALLOWED_HOSTS" not in text:
    text = text.replace(target, replacement)
    with open(compose_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("docker-compose.yml updated successfully!")
else:
    print("Already updated or target not found.")
