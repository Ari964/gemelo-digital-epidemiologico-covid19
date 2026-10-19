"""
CLI Runner para exportación de informes PDF (ReportLab) y Excel (OpenPyXL)
Invocado por server.ts o directamente desde la consola.
"""
import sys
import json
from backend.main import export_report_pdf, export_report_excel, ExportPayload, SessionLocal

def main():
    if len(sys.argv) < 2:
        print("Uso: python -m backend.export_cli [pdf|excel]", file=sys.stderr)
        sys.exit(1)

    export_type = sys.argv[1].lower()
    input_data = sys.stdin.read()

    try:
        data = json.loads(input_data) if input_data.strip() else {}
    except Exception as e:
        data = {}

    db = SessionLocal()
    try:
        payload = ExportPayload(**data)
        if export_type == "pdf":
            resp = export_report_pdf(payload, db)
            sys.stdout.buffer.write(resp.body)
        elif export_type == "excel":
            resp = export_report_excel(payload, db)
            sys.stdout.buffer.write(resp.body)
        else:
            print(f"Tipo de exportación desconocido: {export_type}", file=sys.stderr)
            sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
