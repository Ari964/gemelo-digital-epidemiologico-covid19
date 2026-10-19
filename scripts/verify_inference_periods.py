"""
Script de Verificación Multi-Periodo de Inferencia (Requerimiento 2).
Prueba cortes dominicales en distintos regímenes de transmisión:
- Régimen de alta transmisión (Ola Delta 2021)
- Régimen de moderada transmisión / transición (2022-2023)
- Conjunto de test inicial (2023-04-02)
- Conjunto de test medio (2024-01-07)
- Conjunto de test tardío (2024-07-21)
- Caso de referencia de cierre (2024-07-28)
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath("."))
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

test_dates = [
    ("2021-07-11", "Alta transmisión (Ola Delta en Train)"),
    ("2022-12-18", "Transición / moderada transmisión (Omicron tardío en Val)"),
    ("2023-04-02", "Inicio del Test Reservado (Transición a endemia plana)"),
    ("2024-01-07", "Fase endémica intermedia (Test)"),
    ("2024-07-21", "Corte previo al cierre (Test)"),
    ("2024-07-28", "Corte de referencia final (Test)"),
    ("2024-08-04", "Última semana histórica consolidada (Test)")
]

print("=== INFERENCIA MULTI-PERIODO: EVALUACIÓN DE CORTES HISTÓRICOS ===")
results = []
for cutoff_date, regime in test_dates:
    res = client.post("/api/v1/predictions/weekly", json={"cutoff_date": cutoff_date, "county_code": 0})
    if res.status_code != 200:
        print(f"Error {res.status_code} para {cutoff_date}: {res.text}")
        continue
    data = res.json()
    cutoff_t0 = data["cutoff_date_t0"]
    horizon_t1 = data["forecast_horizon_t1"]
    lag_1 = data["validation_details"]["weekly_lag_1_used"]
    naive_pred = data["primary_forecast_cases"]
    rf_pred = data["hypothetical_rf_prediction"]
    observed_t1 = data["target_observed_actual"]
    naive_mae = data["forecast_error_mae"]
    rf_mae = data["historical_benchmark_audit"]["random_forest_error_abs"]
    
    row = {
        "cutoff_t0": cutoff_t0,
        "regime": regime,
        "horizon_t1": horizon_t1,
        "observed_t0 (lag_1)": lag_1,
        "observed_t1": observed_t1,
        "naive_pred": naive_pred,
        "naive_mae": naive_mae,
        "rf_pred": rf_pred,
        "rf_mae": rf_mae
    }
    results.append(row)
    print(f"\nFecha t0: {cutoff_t0} ({regime})")
    print(f"  -> Semana objetivo t+1: {horizon_t1}")
    print(f"  -> Observado t0 (weekly_lag_1): {lag_1} casos")
    print(f"  -> Observado t+1: {observed_t1} casos")
    print(f"  -> Predicción Persistencia: {naive_pred} casos | MAE: {naive_mae}")
    print(f"  -> Predicción Random Forest: {rf_pred} casos | MAE: {rf_mae}")

with open("docs/auditoria_inferencia_multiperiodo.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nResultados exportados a docs/auditoria_inferencia_multiperiodo.json")
