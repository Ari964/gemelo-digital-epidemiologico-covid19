import subprocess

cmd = ['docker', 'exec', 'docker_example-langflow-1', 'python', '-c', '''
import inspect
from lfx.custom import Component
methods = [m for m in dir(Component) if "tool" in m.lower()]
print("Component tool methods:", methods)
''']
res = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
