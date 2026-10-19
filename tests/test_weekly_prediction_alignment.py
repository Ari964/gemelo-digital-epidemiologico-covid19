"""
Pruebas de Alineación Temporal Independientes (Fase 3 / Auditoría Externa).
---------------------------------------------------------------------------
Verifica de manera estrictamente independiente a la lógica del endpoint:
1. Lectura directa de las observaciones empíricas en los archivos CSV procesados.
2. Comprobación de que weekly_lag_1 en la fila t1 coincide exactamente con los casos observados en t0.
3. Comparación de los casos reales y calculados directamente con las respuestas de la API:
   - 2022-12-18 (t0 obs=183 -> t1 2022-12-25 obs=363, Naive=183.0, MAE=180.0, RF=276.28)
   - 2024-07-21 (t0 obs=1 -> t1 2024-07-28 obs=0, Naive=1.0, MAE=1.0, RF=70.76)
   - 2024-07-28 (t0 obs=0 -> t1 2024-08-04 obs=0, Naive=0.0, MAE=0.0, RF=70.76)
   - 2024-08-04 (Última fecha histórica: t0 obs=0 -> t1 2024-08-11 futura, obs=None, MAE=None)
   - Fechas no disponibles (e.g. 2025-01-01) -> Retorna HTTP 404 (NUNCA fallback 1.0)
"""

import os
import pandas as pd
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

def load_all_independent_weekly_data() -> pd.DataFrame:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "processed"))
    dfs = []
    for split in ["train", "val", "test"]:
        path = os.path.join(base_dir, f"kenya_covid_weekly_{split}.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            dfs.append(df)
    combined = pd.concat(dfs, ignore_index=True)
    combined = combined.drop_duplicates(subset=["date"]).sort_values("date").reset_index(drop=True)
    return combined


def test_independent_csv_temporal_lag_consistency():
    """
    Verifica a nivel de datos puros que en todo el dataset:
    Para cada fila con fecha t1, su 'weekly_lag_1' es exactamente igual al
    'target_weekly_cases' de la fila fechada en t0 = t1 - 7 días.
    """
    df = load_all_independent_weekly_data()
    df["dt"] = pd.to_datetime(df["date"])
    date_to_cases = dict(zip(df["date"], df["target_weekly_cases"]))
    
    mismatches = []
    for idx, row in df.iterrows():
        t1_str = row["date"]
        t0_dt = row["dt"] - timedelta(days=7)
        t0_str = t0_dt.strftime("%Y-%m-%d")
        
        if t0_str in date_to_cases:
            expected_lag_1 = date_to_cases[t0_str]
            actual_lag_1 = row["weekly_lag_1"]
            if expected_lag_1 != actual_lag_1:
                mismatches.append((t1_str, t0_str, expected_lag_1, actual_lag_1))
                
    assert len(mismatches) == 0, f"Discrepancias en rezagos CSV: {mismatches[:5]}"


def test_independent_alignment_case_2022_12_18():
    """
    Fecha de corte: 2022-12-18 (Validación)
    En CSV:
    - 2022-12-18: target_weekly_cases = 183
    - 2022-12-25: target_weekly_cases = 363, weekly_lag_1 = 183
    """
    df = load_all_independent_weekly_data()
    cases_t0 = float(df[df["date"] == "2022-12-18"]["target_weekly_cases"].values[0])
    cases_t1 = float(df[df["date"] == "2022-12-25"]["target_weekly_cases"].values[0])
    lag_1_t1 = float(df[df["date"] == "2022-12-25"]["weekly_lag_1"].values[0])
    
    assert cases_t0 == 183.0
    assert cases_t1 == 363.0
    assert lag_1_t1 == cases_t0
    
    # Llamar API
    response = client.post(
        "/api/v1/predictions/weekly",
        json={"cutoff_date": "2022-12-18", "county_code": 0}
    )
    assert response.status_code == 200
    res = response.json()
    
    assert res["cutoff_date"] == "2022-12-18"
    assert res["target_week"] == "2022-12-25"
    assert res["primary_forecast_cases"] == cases_t0
    assert res["target_observed_actual"] == cases_t1
    assert res["forecast_error_mae"] == abs(cases_t1 - cases_t0)
    assert round(res["hypothetical_rf_prediction"], 2) == 276.28


def test_independent_alignment_case_2024_07_21():
    """
    Fecha de corte: 2024-07-21 (Test)
    En CSV:
    - 2024-07-21: target_weekly_cases = 1
    - 2024-07-28: target_weekly_cases = 0, weekly_lag_1 = 1
    """
    df = load_all_independent_weekly_data()
    cases_t0 = float(df[df["date"] == "2024-07-21"]["target_weekly_cases"].values[0])
    cases_t1 = float(df[df["date"] == "2024-07-28"]["target_weekly_cases"].values[0])
    lag_1_t1 = float(df[df["date"] == "2024-07-28"]["weekly_lag_1"].values[0])
    
    assert cases_t0 == 1.0
    assert cases_t1 == 0.0
    assert lag_1_t1 == cases_t0
    
    response = client.post(
        "/api/v1/predictions/weekly",
        json={"cutoff_date": "2024-07-21", "county_code": 0}
    )
    assert response.status_code == 200
    res = response.json()
    
    assert res["cutoff_date"] == "2024-07-21"
    assert res["target_week"] == "2024-07-28"
    assert res["primary_forecast_cases"] == cases_t0
    assert res["target_observed_actual"] == cases_t1
    assert res["forecast_error_mae"] == abs(cases_t1 - cases_t0)
    assert round(res["hypothetical_rf_prediction"], 2) == 70.76


def test_independent_alignment_case_2024_07_28():
    """
    Fecha de corte: 2024-07-28 (Referencia Test)
    En CSV:
    - 2024-07-28: target_weekly_cases = 0
    - 2024-08-04: target_weekly_cases = 0, weekly_lag_1 = 0
    """
    df = load_all_independent_weekly_data()
    cases_t0 = float(df[df["date"] == "2024-07-28"]["target_weekly_cases"].values[0])
    cases_t1 = float(df[df["date"] == "2024-08-04"]["target_weekly_cases"].values[0])
    lag_1_t1 = float(df[df["date"] == "2024-08-04"]["weekly_lag_1"].values[0])
    
    assert cases_t0 == 0.0
    assert cases_t1 == 0.0
    assert lag_1_t1 == cases_t0
    
    response = client.post(
        "/api/v1/predictions/weekly",
        json={"cutoff_date": "2024-07-28", "county_code": 0}
    )
    assert response.status_code == 200
    res = response.json()
    
    assert res["cutoff_date"] == "2024-07-28"
    assert res["target_week"] == "2024-08-04"
    assert res["primary_forecast_cases"] == cases_t0
    assert res["target_observed_actual"] == cases_t1
    assert res["forecast_error_mae"] == abs(cases_t1 - cases_t0)
    assert round(res["hypothetical_rf_prediction"], 2) == 70.76


def test_independent_alignment_last_historical_date_2024_08_04():
    """
    Última fecha histórica disponible en el dataset: 2024-08-04.
    Pronostica la semana futura t1 = 2024-08-11.
    Casos observados en t1 no existen en el dataset -> target_observed_actual = None, MAE = None.
    Casos observados en t0 = 0.0 -> Persistencia = 0.0.
    """
    df = load_all_independent_weekly_data()
    last_date = df["date"].max()
    assert last_date == "2024-08-04"
    cases_t0 = float(df[df["date"] == last_date]["target_weekly_cases"].values[0])
    assert cases_t0 == 0.0
    
    response = client.post(
        "/api/v1/predictions/weekly",
        json={"cutoff_date": "2024-08-04", "county_code": 0}
    )
    assert response.status_code == 200
    res = response.json()
    
    assert res["cutoff_date"] == "2024-08-04"
    assert res["target_week"] == "2024-08-11"
    assert res["primary_forecast_cases"] == 0.0
    assert res["target_observed_actual"] is None
    assert res["forecast_error_mae"] is None
    assert round(res["hypothetical_rf_prediction"], 2) == 70.76
    assert res["validation_details"]["is_future_forecast"] is True


def test_independent_alignment_unavailable_date_returns_404_no_fallback():
    """
    Una fecha no disponible (e.g. 2025-01-01) DEBE retornar HTTP 404
    y NUNCA un valor de respaldo 1.0 artificial.
    """
    response = client.post(
        "/api/v1/predictions/weekly",
        json={"cutoff_date": "2025-01-01", "county_code": 0}
    )
    assert response.status_code == 404
    detail = response.json()["detail"]
    assert "no encontrada" in detail.lower() or "disponible" in detail.lower()


def test_independent_alignment_pre_buffer_date_returns_404():
    """
    Una fecha previa al búfer histórico (e.g. 2020-03-01) debe retornar 404
    sin fallback arbitrario.
    """
    response = client.post(
        "/api/v1/predictions/weekly",
        json={"cutoff_date": "2020-03-01", "county_code": 0}
    )
    assert response.status_code == 404
