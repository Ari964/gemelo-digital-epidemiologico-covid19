import os
import psycopg2
from langflow.services.auth.utils import decrypt_api_key

conn = psycopg2.connect(os.environ['LANGFLOW_DATABASE_URL'])
cur = conn.cursor()
cur.execute("SELECT name, value, type FROM variable WHERE name = 'GOOGLE_API_KEY';")
row = cur.fetchone()

if row:
    name, encrypted_val, var_type = row
    decrypted = decrypt_api_key(encrypted_val)
    
    import urllib.request
    import json
    
    # Try gemini-2.5-flash
    model_to_test = "gemini-2.5-flash"
    gen_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_to_test}:generateContent?key={decrypted}"
    payload = json.dumps({"contents": [{"parts": [{"text": "Traduce al chino con pinyin y ejemplo: 'Gemelo digital'"}]}]}).encode("utf-8")
    gen_req = urllib.request.Request(gen_url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(gen_req, timeout=15) as gen_resp:
            gen_data = json.loads(gen_resp.read().decode("utf-8"))
            reply = gen_data["candidates"][0]["content"]["parts"][0]["text"].strip()
            print(f"SUCCESS with {model_to_test}!")
            print("REPLY PREVIEW:")
            print(reply[:200])
    except Exception as e:
        print(f"Error with {model_to_test}:", e)
