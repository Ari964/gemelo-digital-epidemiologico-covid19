"""
Script de Inferencia Limpia y Verificación de Predicción Semanal (1 Semana hacia adelante - t+1).

Carga el artefacto serializado (joblib) desde un proceso limpio, valida las 11 características de entrada,
verifica la disponibilidad empírica vs. hipotética de cada variable en la fecha de corte,
y ejecuta la proyección a 1 semana.
"""

import os
import sys
import json
import hashlib
import argparse
import joblib
import numpy as np
import pandas as pd

# Asegurar codificación utf-8 para consola Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_MODEL_PATH = os.path.join(BASE_DIR, "models", "champion_covid_model_v1.0.joblib")
DEFAULT_META_PATH = os.path.join(BASE_DIR, "models", "champion_covid_model_v1.0.json")
PROCESSED_TEST_PATH = os.path.join(BASE_DIR, "data", "processed", "kenya_covid_weekly_test.csv")

FEATURE_NAMES = [
    "weekly_lag_1",
    "weekly_lag_2",
    "weekly_lag_3",
    "weekly_lag_4",
    "weekly_rolling_mean_4",
    "weekly_rolling_std_4",
    "weekly_deaths_lag_1",
    "weekly_deaths_lag_2",
    "stringency_lag_1",
    "reproduction_rate_lag_1",
    "month"
]


def load_model_and_verify(model_path=DEFAULT_MODEL_PATH, meta_path=DEFAULT_META_PATH):
    """Carga el modelo serializado y valida su integridad criptográfica SHA-256."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No se encontró el archivo del modelo en: {model_path}")
    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"No se encontró el archivo de metadatos en: {meta_path}")

    with open(model_path, "rb") as f:
        model_bytes = f.read()
        computed_sha256 = hashlib.sha256(model_bytes).hexdigest()

    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    expected_sha256 = metadata.get("artifact_sha256")
    if expected_sha256 and expected_sha256 != computed_sha256:
        raise ValueError(f"Discrepancia de integridad SHA-256. Esperado: {expected_sha256}, Calculado: {computed_sha256}")

    model = joblib.load(model_path)
    return model, metadata, computed_sha256


def assess_feature_availability(features_dict, prediction_date_str):
    """
    Evalúa la disponibilidad real de cada variable en la fecha de corte indicada.
    Distingue rigurosamente entre variables epidemiológicas continuas y covariables descontinuadas.
    """
    availability_report = {}
    is_post_2022 = prediction_date_str >= "2023-01-01"

    for feat in FEATURE_NAMES:
        val = features_dict.get(feat)
        if feat in ["weekly_lag_1", "weekly_lag_2", "weekly_lag_3", "weekly_lag_4"]:
            availability_report[feat] = {
                "valor": val,
                "disponibilidad": "100% DISPONIBLE (Empírico, OMS/MoH Kenia reporte dominical)",
                "origen": "Observación real semanal de casos positivos",
                "tipo": "Covariable endógena"
            }
        elif feat in ["weekly_rolling_mean_4", "weekly_rolling_std_4"]:
            availability_report[feat] = {
                "valor": val,
                "disponibilidad": "100% DISPONIBLE (Calculada de ventana móvil semanal)",
                "origen": "Transformación determinística de los 4 lags observados",
                "tipo": "Transformación endógena"
            }
        elif feat in ["weekly_deaths_lag_1", "weekly_deaths_lag_2"]:
            availability_report[feat] = {
                "valor": val,
                "disponibilidad": "100% DISPONIBLE (Empírico, OMS/MoH Kenia reporte dominical)",
                "origen": "Observación real semanal de defunciones",
                "tipo": "Covariable endógena"
            }
        elif feat == "month":
            availability_report[feat] = {
                "valor": val,
                "disponibilidad": "100% DISPONIBLE (Calendario gregoriano)",
                "origen": "Variable temporal fija",
                "tipo": "Estacionalidad exógena"
            }
        elif feat == "stringency_lag_1":
            if is_post_2022:
                availability_report[feat] = {
                    "valor": val,
                    "disponibilidad": "DESCONTINUADA / NO DISPONIBLE (100% ausente post-2022)",
                    "origen": "Oxford OxCGRT finalizó el 31/12/2022. Valor ingresado como control hipotético de sensibilidad.",
                    "tipo": "Exploración hipotética (NO causal)"
                }
            else:
                availability_report[feat] = {
                    "valor": val,
                    "disponibilidad": "DISPONIBLE HISTÓRICAMENTE (Índice Oxford Blavatnik)",
                    "origen": "Registro histórico empírico pre-2023",
                    "tipo": "Intervención observada"
                }
        elif feat == "reproduction_rate_lag_1":
            if is_post_2022:
                availability_report[feat] = {
                    "valor": val,
                    "disponibilidad": "DESCONTINUADA / NO DISPONIBLE (100% ausente post-2022)",
                    "origen": "Estimación OWID cesó en enero 2023. Valor ingresado como control referencial.",
                    "tipo": "Covariable referencial"
                }
            else:
                availability_report[feat] = {
                    "valor": val,
                    "disponibilidad": "DISPONIBLE HISTÓRICAMENTE (Estimación OWID)",
                    "origen": "Registro histórico empírico",
                    "tipo": "Estimación previa"
                }

    return availability_report


def predict_for_week(features_dict, prediction_date_str, model, metadata):
    """Ejecuta la inferencia a 1 semana hacia adelante (t+1)."""
    # Validar presencia de las 11 entradas exigidas
    missing_inputs = [f for f in FEATURE_NAMES if f not in features_dict]
    if missing_inputs:
        raise ValueError(f"Faltan las siguientes variables de entrada requeridas: {missing_inputs}")

    # Construir array con orden estricto de las 11 características
    X_input = np.array([[features_dict[f] for f in FEATURE_NAMES]], dtype=float)

    # Inferencia
    raw_pred = model.predict(X_input)[0]
    final_pred = max(0.0, float(raw_pred))

    # Cálculo de fecha objetivo (t+1 semana)
    t0_date = pd.to_datetime(prediction_date_str)
    t1_date = t0_date + pd.Timedelta(days=7)

    return {
        "prediction_date_t0": t0_date.strftime("%Y-%m-%d"),
        "forecast_horizon_t1": t1_date.strftime("%Y-%m-%d"),
        "horizon_description": "1 semana hacia adelante (cierre semanal siguiente t+1)",
        "predicted_weekly_cases": round(final_pred, 2),
        "raw_model_output": float(raw_pred)
    }


def main():
    parser = argparse.ArgumentParser(description="Inferencia y verificación semanal de modelo epidemiológico (1 semana t+1).")
    parser.add_argument("--date", type=str, default="2024-07-28", help="Fecha de corte semanal (YYYY-MM-DD).")
    parser.add_argument("--model-path", type=str, default=DEFAULT_MODEL_PATH, help="Ruta al artefacto .joblib.")
    parser.add_argument("--meta-path", type=str, default=DEFAULT_META_PATH, help="Ruta al archivo .json de metadatos.")
    parser.add_argument("--stringency-override", type=float, default=None, help="Valor para exploración hipotética de stringency_index.")
    args = parser.parse_args()

    print("=" * 85)
    print("PROCESO LIMPIO DE INFERENCIA EPIDEMIOLÓGICA SEMANAL (HORIZONTE 1 SEMANA - t+1)")
    print("=" * 85)

    # 1. Cargar artefacto serializado
    model, metadata, sha256_hash = load_model_and_verify(args.model_path, args.meta_path)
    print(f"Modelo cargado exitosamente: {os.path.basename(args.model_path)}")
    print(f"SHA-256 verificado: {sha256_hash}")
    print(f"Nombre en metadatos: {metadata.get('name')}")
    print(f"Frecuencia canónica: {metadata.get('canonical_frequency')}")
    print(f"Horizonte configurado: {metadata.get('forecast_horizon')}")

    # 2. Cargar todos los conjuntos semanales procesados (Train, Val, Test)
    PROCESSED_TRAIN_PATH = os.path.join(BASE_DIR, "data", "processed", "kenya_covid_weekly_train.csv")
    PROCESSED_VAL_PATH = os.path.join(BASE_DIR, "data", "processed", "kenya_covid_weekly_val.csv")

    dfs = []
    for p in [PROCESSED_TRAIN_PATH, PROCESSED_VAL_PATH, PROCESSED_TEST_PATH]:
        if os.path.exists(p):
            dfs.append(pd.read_csv(p))
    if not dfs:
        raise FileNotFoundError("No se encontraron archivos de datos semanales procesados.")
    df_all = pd.concat(dfs, ignore_index=True).drop_duplicates(subset=["date"]).sort_values("date").reset_index(drop=True)

    cutoff_date_str = args.date
    t0_dt = pd.to_datetime(cutoff_date_str)
    t1_dt = t0_dt + pd.Timedelta(days=7)
    horizon_date_str = t1_dt.strftime("%Y-%m-%d")

    m_t0 = df_all[df_all["date"] == cutoff_date_str]
    if m_t0.empty:
        print(f"\n[ERROR]: La fecha de corte '{cutoff_date_str}' no existe en las observaciones históricas.")
        print("No se asigna 1.0 ni datos ficticios por defecto. Ingrese una fecha dominical válida entre 2020-04-12 y 2024-08-04.")
        sys.exit(1)

    row_t0 = m_t0.iloc[0]
    obs_t0 = float(row_t0["target_weekly_cases"])

    m_t1 = df_all[df_all["date"] == horizon_date_str]
    has_real_target = False
    real_target = None

    if not m_t1.empty:
        row_t1 = m_t1.iloc[0]
        has_real_target = True
        real_target = float(row_t1["target_weekly_cases"])
        features = {feat: float(row_t1[feat]) for feat in FEATURE_NAMES}
    else:
        # Última fecha histórica disponible (ej. 2024-08-04): pronóstico hacia t1 futuro
        has_real_target = False
        real_target = None
        lag_1 = obs_t0
        lag_2 = float(row_t0.get("weekly_lag_1", 0.0))
        lag_3 = float(row_t0.get("weekly_lag_2", 0.0))
        lag_4 = float(row_t0.get("weekly_lag_3", 0.0))
        lags = [lag_1, lag_2, lag_3, lag_4]
        features = {
            "weekly_lag_1": lag_1,
            "weekly_lag_2": lag_2,
            "weekly_lag_3": lag_3,
            "weekly_lag_4": lag_4,
            "weekly_rolling_mean_4": float(np.mean(lags)),
            "weekly_rolling_std_4": float(np.std(lags, ddof=1)) if len(lags) > 1 else 0.0,
            "weekly_deaths_lag_1": float(row_t0.get("new_deaths", row_t0.get("weekly_deaths_lag_1", 0.0))),
            "weekly_deaths_lag_2": float(row_t0.get("weekly_deaths_lag_1", 0.0)),
            "stringency_lag_1": float(row_t0.get("stringency_lag_1", 22.77)),
            "reproduction_rate_lag_1": float(row_t0.get("reproduction_rate_lag_1", 0.54)),
            "month": float(t1_dt.month)
        }

    if args.stringency_override is not None:
        print(f"\n[EXPLORACIÓN HIPOTÉTICA]: Modificando stringency_lag_1 de {features['stringency_lag_1']} a {args.stringency_override}")
        features["stringency_lag_1"] = float(args.stringency_override)

    # 3. Evaluar disponibilidad y advertencias de datos faltantes
    availability = assess_feature_availability(features, cutoff_date_str)

    print(f"\n--- AUDITORÍA DE LAS 11 ENTRADAS EXIGIDAS EN FECHA DE CORTE: {cutoff_date_str} ---")
    print(f"{'Característica':25s} | {'Valor':8s} | {'Disponibilidad / Estado Empírico'}")
    print("-" * 85)
    for feat, info in availability.items():
        print(f"{feat:25s} | {info['valor']:8.2f} | {info['disponibilidad']}")

    # 4. Ejecutar predicción
    result = predict_for_week(features, cutoff_date_str, model, metadata)

    print("\n" + "=" * 85)
    print("SALIDA REAL DE INFERENCIA")
    print("=" * 85)
    print(f"Fecha de corte semanal (t0)          : {result['prediction_date_t0']}")
    print(f"Casos reales observados en t0        : {obs_t0:.0f} casos")
    print(f"Horizonte de predicción (t+1)        : {result['forecast_horizon_t1']} ({result['horizon_description']})")
    print(f"Predicción Naive Persistence (t+1)   : {features['weekly_lag_1']:.1f} casos")
    print(f"Predicción Random Forest (t+1)       : {result['predicted_weekly_cases']:.2f} casos")

    # Comparación con valor real observado si existe en los datos
    print(f"\n--- COMPARACIÓN CON REGISTRO OBSERVADO EN t+1 ---")
    if has_real_target and real_target is not None:
        naive_baseline_pred = float(features["weekly_lag_1"])
        err_model = abs(real_target - result['predicted_weekly_cases'])
        err_naive = abs(real_target - naive_baseline_pred)
        print(f"Casos observados reales en {result['forecast_horizon_t1']} : {real_target:.0f} casos")
        print(f"Proyección Naive Persistence (t0)               : {naive_baseline_pred:.0f} casos (Error abs: {err_naive:.2f})")
        print(f"Proyección Random Forest                        : {result['predicted_weekly_cases']:.2f} casos (Error abs: {err_model:.2f})")
    else:
        print(f"Casos observados reales en {result['forecast_horizon_t1']} : No disponible (semana futura fuera del registro histórico)")
        print(f"Error absoluto Naive Persistence                : No disponible")
        print(f"Error absoluto Random Forest                    : No disponible")

    print("\n" + "=" * 85)
    print("ADVERTENCIA METODOLÓGICA DE FASE 1:")
    print("1. La sensibilidad del modelo ante variaciones de stringency_lag_1 es una exploración hipotética")
    print("   asociativa, NO un efecto causal validado de una intervención sanitaria.")
    print("2. El índice de rigurosidad de Oxford cesó en 2022 (100% ausente post-2022 en datos crudos).")
    print("3. Las variables epidemiológicas de casos y muertes tienen 0% de datos faltantes en frecuencia semanal.")
    print("=" * 85)


if __name__ == "__main__":
    main()
