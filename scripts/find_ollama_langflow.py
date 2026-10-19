import subprocess

cmd = ['docker', 'exec', 'docker_example-langflow-1', 'python', '-c', '''
import pkgutil
import importlib

for modname in ['lfx.components.models', 'lfx.components.models_and_agents', 'langflow.components.models']:
    try:
        m = importlib.import_module(modname)
        print("Found:", modname, dir(m))
    except Exception as e:
        print("Error in", modname, e)
''']
res = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
