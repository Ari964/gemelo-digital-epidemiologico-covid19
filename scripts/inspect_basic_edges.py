import subprocess
import json

cmd = ['docker', 'exec', 'docker_example-postgres-1', 'psql', '-U', 'langflow', '-d', 'langflow', '-t', '-A', '-c', 
       "SELECT data FROM flow WHERE id='e4eecf2d-14ff-4d42-9a57-77db12cfa527';"]
res = subprocess.check_output(cmd).decode()
d = json.loads(res)
print("Edges in Basic Prompting:")
for e in d['edges']:
    print(f"{e.get('source')} ({e.get('sourceHandle')}) --> {e.get('target')} ({e.get('targetHandle')})")
