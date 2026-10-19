import subprocess

cmd = ['docker', 'exec', 'docker_example-postgres-1', 'psql', '-U', 'langflow', '-d', 'langflow', '-c', 
       "SELECT id, name, description FROM flow;"]
res = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:", res.stdout)
