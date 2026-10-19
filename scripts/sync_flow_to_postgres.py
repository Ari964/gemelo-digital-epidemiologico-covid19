import json
import psycopg2

def sync_flow():
    with open("docs/flujo_epidemiologico_langflow_exportado.json", "r", encoding="utf-8") as f:
        flow_json = json.load(f)

    flow_data = flow_json.get("data", {})
    flow_id = "906a3d58-bcf0-48a9-9364-4a62ea230945"

    conn = psycopg2.connect(
        dbname="langflow",
        user="langflow",
        password="langflow",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    # Update flow data
    cur.execute(
        "UPDATE flow SET data = %s, description = %s, updated_at = NOW() WHERE id = %s",
        (json.dumps(flow_data), flow_json.get("description", ""), flow_id)
    )
    rows = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()

    print(f"Synced flow {flow_id} to postgres. Rows updated: {rows}")

if __name__ == "__main__":
    sync_flow()
