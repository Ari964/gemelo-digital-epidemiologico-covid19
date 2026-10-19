import subprocess

cmd = ['docker', 'exec', 'docker_example-langflow-1', 'python', '-c', '''
import sys
for modname in [
    'lfx.components.models.ollama',
    'langflow.components.models.ollama',
    'langflow.components.models.OllamaModel',
    'langflow.components.models.language_model'
]:
    try:
        __import__(modname)
        print("Found:", modname)
    except Exception as e:
        pass
''']
res = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
