import urllib.request
import json

def test_reports():
    # 1. Login
    login_data = json.dumps({"email": "admin@epidemic-twin.ke", "password": "AdminSecure2026!"}).encode()
    login_req = urllib.request.Request("http://127.0.0.1:8000/api/v1/auth/login", data=login_data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(login_req) as resp:
        tokens = json.loads(resp.read().decode())
        token = tokens["access_token"]
        print("Logged in successfully. Token acquired.")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # 2. Test Preview for all 4 types and 3 languages
    types = ['data_provenance', 'models_cv', 'weekly_forecast', 'seir_abm_scenarios']
    languages = ['es', 'en', 'sw']

    for rtype in types:
        for lang in languages:
            req = urllib.request.Request(
                "http://127.0.0.1:8000/api/v1/reports/preview",
                data=json.dumps({"report_type": rtype, "lang": lang, "cutoff_date": "2024-07-28", "county_code": 0}).encode(),
                headers=headers
            )
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
                print(f"[PREVIEW OK] Type={rtype:20} Lang={lang} Title={data['title'][:35]} | Metrics={len(data.get('summary_metrics', []))} | Tables={len(data.get('tables', []))}")

    # 3. Test PDF export for provenance
    pdf_req = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/reports/export/pdf",
        data=json.dumps({"report_type": "data_provenance", "lang": "es"}).encode(),
        headers=headers
    )
    with urllib.request.urlopen(pdf_req) as resp:
        pdf_bytes = resp.read()
        print(f"[PDF OK] Received {len(pdf_bytes)} bytes of PDF (starts with {pdf_bytes[:4].decode('latin1')})")

    # 4. Test Excel export for models
    xlsx_req = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/reports/export/excel",
        data=json.dumps({"report_type": "models_cv", "lang": "es"}).encode(),
        headers=headers
    )
    with urllib.request.urlopen(xlsx_req) as resp:
        xlsx_bytes = resp.read()
        print(f"[EXCEL OK] Received {len(xlsx_bytes)} bytes of XLSX (starts with {xlsx_bytes[:2].decode('latin1')})")

if __name__ == "__main__":
    test_reports()
