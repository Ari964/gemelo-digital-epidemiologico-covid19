import os

compose_path = r"C:\Users\KRISTEL\Documents\langflow\docker_example\docker-compose.yml"
with open(compose_path, "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace("pull_policy: always", "pull_policy: if_not_present")
with open(compose_path, "w", encoding="utf-8") as f:
    f.write(text)
print("Updated pull_policy to if_not_present")
