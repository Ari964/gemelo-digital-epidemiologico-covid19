import subprocess
import json

cmd = ['docker', 'exec', 'docker_example-postgres-1', 'psql', '-U', 'langflow', '-d', 'langflow', '-t', '-A', '-c', 
       "SELECT data FROM flow WHERE id='e4eecf2d-14ff-4d42-9a57-77db12cfa527';"]
res = subprocess.check_output(cmd).decode()
d = json.loads(res)
for n in d['nodes']:
    if n.get('data', {}).get('type') == 'Prompt':
        print("Prompt value:", n['data']['node']['template']['template']['value'])
        print("Template keys:", list(n['data']['node']['template'].keys()))
        for k, v in n['data']['node']['template'].items():
            if k not in ['_type', 'code', 'template']:
                print(f"Key {k}:", v)
