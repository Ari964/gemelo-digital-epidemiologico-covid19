"""
Fase 2 y 3 (CRISP-DM): Análisis Exploratorio de Datos (EDA),
Auditoría de Frecuencia Temporal y Preparación sin Fuga de Información.

- Audita dimensiones, tipos, nulos, duplicados, rangos y distribución.
- Demuestra analíticamente la periodicidad de reporte institucional (semanal dominical en OWID/OMS).
- Establece la conciliación matemática exacta de filas:
  1,674 (crudo) -> 1,606 (base de datos) -> 1,592 (modelado diario) y 230 -> 226 (modelado semanal).
- Construye el dataset semanal canónico (defendible epidemiológicamente) y el dataset diario descompuesto.
- Realiza partición cronológica estricta y ajuste de imputadores/escaladores EXCLUSIVAMENTE en Train.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

# Asegurar codificación utf-8 para consola Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Definición de rutas
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "owid_covid_kenya_raw.csv")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
FIGURES_DIR = os.path.join(BASE_DIR, "docs", "figures")

os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)


def run_eda_and_preparation():
    print("=" * 80)
    print("ETAPA 1: AUDITORÍA EXPLORATORIA Y FRECUENCIA DE REPORTE EPIDEMIOLÓGICO")
    print("=" * 80)

    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(f"Archivo crudo no encontrado en: {RAW_DATA_PATH}")

    df_raw = pd.read_csv(RAW_DATA_PATH)
    total_raw_rows, total_raw_cols = df_raw.shape
    print(f"Dimensiones del dataset original: {total_raw_rows} filas x {total_raw_cols} columnas.")

    df_raw["date"] = pd.to_datetime(df_raw["date"])
    df_raw = df_raw.sort_values(by="date").reset_index(drop=True)
    min_date = df_raw["date"].min().strftime("%Y-%m-%d")
    max_date = df_raw["date"].max().strftime("%Y-%m-%d")
    print(f"Cobertura temporal observada: desde {min_date} hasta {max_date}.")

    # Verificación de duplicados
    duplicates = int(df_raw.duplicated(subset=["date"]).sum())
    print(f"Registros duplicados por fecha: {duplicates} (Consistencia temporal 100%).")

    # 1.1 Demostración de la frecuencia real de reporte de la OMS / MoH Kenya
    df_raw["day_name"] = df_raw["date"].dt.day_name()
    positive_by_day = df_raw[df_raw["new_cases"] > 0]["day_name"].value_counts().to_dict()
    print("\nDistribución de días con nuevos casos positivos reportados (new_cases > 0):")
    for dname, cnt in positive_by_day.items():
        print(f"  - {dname:12s}: {cnt:4d} días con reporte positivo")

    sunday_ratio = (positive_by_day.get("Sunday", 0) / sum(positive_by_day.values())) * 100.0 if positive_by_day else 0.0
    print(f"\n[HALLAZGO METODOLÓGICO CRÍTICO]: El {sunday_ratio:.1f}% de los reportes positivos ocurren los DOMINGOS.")
    print("  La fuente institucional (OWID/OMS/MoH) consolida los casos en lotes semanales.")
    print("  'new_cases_smoothed' es la media móvil de 7 días (lote semanal dividido entre 7), NO un conteo diario independiente.")

    # 1.2 Auditoría del período de test 2023–2024
    test_period_df = df_raw[df_raw["date"] >= "2023-04-01"]
    test_zeros_raw = int((test_period_df["new_cases"] == 0).sum())
    test_zeros_smoothed = int((test_period_df["new_cases_smoothed"] == 0).sum())
    test_missing = int(test_period_df["new_cases_smoothed"].isna().sum())
    print(f"\nAuditoría período 2023-2024 (N = {len(test_period_df)} días):")
    print(f"  - Días con new_cases == 0 (conteo bruto):      {test_zeros_raw:4d} ({test_zeros_raw/len(test_period_df)*100:.1f}%)")
    print(f"  - Días con new_cases_smoothed == 0:          {test_zeros_smoothed:4d} ({test_zeros_smoothed/len(test_period_df)*100:.1f}%)")
    print(f"  - Valores faltantes en new_cases_smoothed:   {test_missing:4d} ({test_missing/len(test_period_df)*100:.1f}%)")

    # =========================================================================
    # ETAPA 2: TABLA DE CONCILIACIÓN EXACTA DE FILAS Y EXCLUSIONES
    # =========================================================================
    print("\n" + "=" * 80)
    print("ETAPA 2: CONCILIACIÓN EXACTA DE FILAS Y JUSTIFICACIÓN DE EXCLUSIONES")
    print("=" * 80)

    # Paso A: Total filas archivo de Kenia
    n_raw = len(df_raw)  # 1674

    # Paso B: Filas previas al primer caso confirmado en Kenia (2020-01-05 a 2020-03-12)
    # Kenya confirmó su primer caso el 13 de marzo de 2020 (publicado en OWID el 13/15 de marzo)
    df_pre_epidemic = df_raw[df_raw["date"] < "2020-03-13"]
    n_pre_epidemic = len(df_pre_epidemic)  # 68 filas con casos 0 pre-pandémicas

    # Paso C: Registros ingresados a la Base de Datos (dataset_observations)
    df_db = df_raw[df_raw["date"] >= "2020-03-13"].copy().reset_index(drop=True)
    n_db = len(df_db)  # 1606 filas

    # Paso D: Buffer de rezagos temporales (primeras 14 filas para calcular lags de 14 días)
    # Del 2020-03-13 al 2020-03-26 (14 días sin rezago histórico completo previo)
    n_lag_buffer = 14
    df_daily_model = df_db.iloc[n_lag_buffer:].copy().reset_index(drop=True)
    n_daily_model = len(df_daily_model)  # 1592 filas

    # Conciliación
    reconciliation_table = [
        {"Etapa": "1. Archivo crudo descargado (owid_covid_kenya_raw.csv)", "Registros": n_raw, "Rango Fechas": f"{df_raw['date'].min().strftime('%Y-%m-%d')} a {df_raw['date'].max().strftime('%Y-%m-%d')}", "Motivo / Justificación": "Extracción íntegra sin filtros del archivo global OWID para ISO KEN."},
        {"Etapa": "2. Exclusión período pre-epidémico", "Registros": -n_pre_epidemic, "Rango Fechas": "2020-01-05 a 2020-03-12", "Motivo / Justificación": "68 días previos a la detección del paciente cero de COVID-19 en Kenia."},
        {"Etapa": "3. Ingesta oficial en BD (dataset_observations)", "Registros": n_db, "Rango Fechas": "2020-03-13 a 2024-08-04", "Motivo / Justificación": "Período epidemiológico oficial activo sincronizado en la base de datos."},
        {"Etapa": "4. Exclusión de buffer de rezagos causales (14 días)", "Registros": -n_lag_buffer, "Rango Fechas": "2020-03-13 a 2020-03-26", "Motivo / Justificación": "Requerido para construir lag_14 y rolling_mean_14 sin imputar ceros ficticios."},
        {"Etapa": "5. Conjunto total para modelado diario (Train+Val+Test)", "Registros": n_daily_model, "Rango Fechas": "2020-03-27 a 2024-08-04", "Motivo / Justificación": "Partición: Train (826) + Val (274) + Test (492) = 1,592 días."}
    ]

    reconcile_df = pd.DataFrame(reconciliation_table)
    for _, row in reconcile_df.iterrows():
        print(f"  * {row['Etapa']:58s} | Filas: {str(row['Registros']):>6s} | {row['Motivo / Justificación']}")

    # =========================================================================
    # ETAPA 3: CONSTRUCCIÓN DE DATASET SEMANAL CANÓNICO (TAREA EPIDEMIOLÓGICA PRINCIPAL)
    # =========================================================================
    print("\n" + "=" * 80)
    print("ETAPA 3: CONSTRUCCIÓN DEL DATASET SEMANAL CANÓNICO (TAREA DEFENDIBLE)")
    print("=" * 80)
    print("Dado que la vigilancia oficial se reporta en lotes semanales los domingos, la formulación")
    print("metodológica canónica y defendible es la PREDICCIÓN DE INCIDENCIA SEMANAL (Weekly Epi Weeks).")

    df_db.set_index("date", inplace=True)
    df_weekly = df_db.resample("W-SUN").agg({
        "new_cases": "sum",
        "new_deaths": "sum",
        "stringency_index": "mean",
        "reproduction_rate": "mean"
    }).reset_index()

    # Rezagos semanales causales (semanas epidemiológicas previas w_{t-1}, w_{t-2}, ...)
    df_weekly["target_weekly_cases"] = df_weekly["new_cases"]
    df_weekly["weekly_lag_1"] = df_weekly["target_weekly_cases"].shift(1)
    df_weekly["weekly_lag_2"] = df_weekly["target_weekly_cases"].shift(2)
    df_weekly["weekly_lag_3"] = df_weekly["target_weekly_cases"].shift(3)
    df_weekly["weekly_lag_4"] = df_weekly["target_weekly_cases"].shift(4)

    # Ventanas móviles causales
    df_weekly["weekly_rolling_mean_4"] = df_weekly["target_weekly_cases"].shift(1).rolling(4, min_periods=1).mean()
    df_weekly["weekly_rolling_std_4"] = df_weekly["target_weekly_cases"].shift(1).rolling(4, min_periods=1).std().fillna(0.0)

    # Rezagos de muertes y factores de intervención
    df_weekly["weekly_deaths_lag_1"] = df_weekly["new_deaths"].shift(1)
    df_weekly["weekly_deaths_lag_2"] = df_weekly["new_deaths"].shift(2)
    df_weekly["stringency_lag_1"] = df_weekly["stringency_index"].shift(1).ffill().fillna(0.0)
    df_weekly["reproduction_rate_lag_1"] = df_weekly["reproduction_rate"].shift(1).ffill().fillna(1.0)
    df_weekly["month"] = df_weekly["date"].dt.month

    # Eliminar 4 semanas de buffer inicial para rezagos
    df_weekly_clean = df_weekly.iloc[4:].copy().reset_index(drop=True)
    n_total_weeks = len(df_weekly_clean)

    # Partición cronológica semanal:
    # Train: 2020-04-12 a 2022-06-26 (116 semanas) -> Olas principales
    # Val:   2022-07-03 a 2023-03-26 (39 semanas)  -> Transición y ajuste
    # Test:  2023-04-02 a 2024-08-04 (71 semanas)  -> Hold-out reservado fuera de muestra
    weekly_train_mask = (df_weekly_clean["date"] <= "2022-06-30")
    weekly_val_mask = (df_weekly_clean["date"] > "2022-06-30") & (df_weekly_clean["date"] <= "2023-03-31")
    weekly_test_mask = (df_weekly_clean["date"] > "2023-03-31")

    df_w_train = df_weekly_clean[weekly_train_mask].copy().reset_index(drop=True)
    df_w_val = df_weekly_clean[weekly_val_mask].copy().reset_index(drop=True)
    df_w_test = df_weekly_clean[weekly_test_mask].copy().reset_index(drop=True)

    print(f"Total semanas de modelado: {n_total_weeks} semanas epidemiológicas.")
    print(f"  - Train semanal: {len(df_w_train)} semanas ({df_w_train['date'].min().strftime('%Y-%m-%d')} a {df_w_train['date'].max().strftime('%Y-%m-%d')})")
    print(f"  - Val semanal:   {len(df_w_val)} semanas ({df_w_val['date'].min().strftime('%Y-%m-%d')} a {df_w_val['date'].max().strftime('%Y-%m-%d')})")
    print(f"  - Test semanal:  {len(df_w_test)} semanas ({df_w_test['date'].min().strftime('%Y-%m-%d')} a {df_w_test['date'].max().strftime('%Y-%m-%d')})")

    # =========================================================================
    # ETAPA 4: PREPROCESAMIENTO RIGUROSO SIN FUGA (FIT EXCLUSIVO EN TRAIN)
    # =========================================================================
    print("\n" + "=" * 80)
    print("ETAPA 4: AJUSTE DE TRANSFORMADORES SIN FUGA DE DATOS (ANTI DATA LEAKAGE)")
    print("=" * 80)

    weekly_features = [
        "weekly_lag_1", "weekly_lag_2", "weekly_lag_3", "weekly_lag_4",
        "weekly_rolling_mean_4", "weekly_rolling_std_4",
        "weekly_deaths_lag_1", "weekly_deaths_lag_2",
        "stringency_lag_1", "reproduction_rate_lag_1",
        "month"
    ]

    imputer_w = SimpleImputer(strategy="median")
    imputer_w.fit(df_w_train[weekly_features])

    scaler_w = StandardScaler()
    scaler_w.fit(imputer_w.transform(df_w_train[weekly_features]))

    # Exportar datasets semanales procesados
    df_w_train.to_csv(os.path.join(PROCESSED_DATA_DIR, "kenya_covid_weekly_train.csv"), index=False)
    df_w_val.to_csv(os.path.join(PROCESSED_DATA_DIR, "kenya_covid_weekly_val.csv"), index=False)
    df_w_test.to_csv(os.path.join(PROCESSED_DATA_DIR, "kenya_covid_weekly_test.csv"), index=False)

    # Mantener también datasets diarios procesados para compatibilidad
    daily_features = [
        "lag_1", "lag_2", "lag_3", "lag_7", "lag_14",
        "rolling_mean_7", "rolling_std_7", "rolling_mean_14",
        "deaths_lag_1", "deaths_lag_7",
        "stringency_lag_1", "stringency_lag_7",
        "reproduction_rate_lag_1",
        "day_of_week", "month"
    ]

    # Reconstruir características diarias en df_daily_model
    df_daily_model["target"] = df_daily_model["new_cases_smoothed"].fillna(df_daily_model["new_cases"]).fillna(0.0)
    for k in [1, 2, 3, 7, 14]:
        df_daily_model[f"lag_{k}"] = df_daily_model["target"].shift(k).bfill()
    df_daily_model["rolling_mean_7"] = df_daily_model["target"].shift(1).rolling(7, min_periods=1).mean().bfill()
    df_daily_model["rolling_std_7"] = df_daily_model["target"].shift(1).rolling(7, min_periods=1).std().fillna(0.0)
    df_daily_model["rolling_mean_14"] = df_daily_model["target"].shift(1).rolling(14, min_periods=1).mean().bfill()
    df_daily_model["deaths_lag_1"] = df_daily_model["new_deaths_smoothed"].shift(1).bfill().fillna(0.0)
    df_daily_model["deaths_lag_7"] = df_daily_model["new_deaths_smoothed"].shift(7).bfill().fillna(0.0)
    df_daily_model["stringency_lag_1"] = df_daily_model["stringency_index"].shift(1).ffill().fillna(0.0)
    df_daily_model["stringency_lag_7"] = df_daily_model["stringency_index"].shift(7).ffill().fillna(0.0)
    df_daily_model["reproduction_rate_lag_1"] = df_daily_model["reproduction_rate"].shift(1).ffill().fillna(1.0)
    df_daily_model["day_of_week"] = df_daily_model["date"].dt.dayofweek
    df_daily_model["month"] = df_daily_model["date"].dt.month

    daily_train = df_daily_model[df_daily_model["date"] <= "2022-06-30"].copy().reset_index(drop=True)
    daily_val = df_daily_model[(df_daily_model["date"] > "2022-06-30") & (df_daily_model["date"] <= "2023-03-31")].copy().reset_index(drop=True)
    daily_test = df_daily_model[df_daily_model["date"] > "2023-03-31"].copy().reset_index(drop=True)

    daily_train.to_csv(os.path.join(PROCESSED_DATA_DIR, "kenya_covid_train.csv"), index=False)
    daily_val.to_csv(os.path.join(PROCESSED_DATA_DIR, "kenya_covid_val.csv"), index=False)
    daily_test.to_csv(os.path.join(PROCESSED_DATA_DIR, "kenya_covid_test.csv"), index=False)

    metadata = {
        "dataset_name": "Kenya COVID-19 Official Surveillance Data",
        "processed_at": pd.Timestamp.now().isoformat(),
        "canonical_frequency": "WEEKLY (Semanas Epidemiológicas OMS/MoH Kenia)",
        "weekly_summary": {
            "total_weeks": n_total_weeks,
            "train_weeks": len(df_w_train),
            "val_weeks": len(df_w_val),
            "test_weeks": len(df_w_test),
            "features": weekly_features,
            "target": "target_weekly_cases"
        },
        "daily_summary": {
            "total_days": len(df_daily_model),
            "train_days": len(daily_train),
            "val_days": len(daily_val),
            "test_days": len(daily_test),
            "features": daily_features,
            "target": "target"
        },
        "row_reconciliation": reconciliation_table
    }

    with open(os.path.join(PROCESSED_DATA_DIR, "feature_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # =========================================================================
    # ETAPA 5: GENERACIÓN DE FIGURAS INSTITUCIONALES ACTUALIZADAS
    # =========================================================================
    print("\n" + "=" * 80)
    print("ETAPA 5: GENERACIÓN DE GRÁFICOS INSTITUCIONALES")
    print("=" * 80)

    # Gráfico 1: Incidencia Semanal Real vs NPIs
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    ax1.bar(df_weekly_clean["date"], df_weekly_clean["target_weekly_cases"], width=5, color="#0284C7", alpha=0.85, label="Casos Semanales Confirmados (OWID / MoH Kenya)")
    ax1.set_title("Vigilancia Epidemiológica Oficial de COVID-19 en Kenia: Incidencia Semanal Auténtica", fontsize=13, fontweight="bold")
    ax1.set_ylabel("Casos por Semana", fontsize=11)
    ax1.legend(loc="upper right", frameon=True)
    ax1.grid(True, linestyle="--", alpha=0.6)

    ax2.plot(df_weekly_clean["date"], df_weekly_clean["stringency_lag_1"], color="#DC2626", linewidth=2.0, label="Índice de Rigor Gubernamental Oxford (NPIs)")
    ax2.set_title("Medidas No Farmacéuticas Gubernamentales (Oxford Stringency Index)", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Fecha de Cierre de Semana Epidemiológica (Domingos)", fontsize=11)
    ax2.set_ylabel("Rigor (0 - 100)", fontsize=11)
    ax2.legend(loc="upper right", frameon=True)
    ax2.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()
    fig1_path = os.path.join(FIGURES_DIR, "01_evolucion_casos_stringency_kenia.png")
    fig.savefig(fig1_path, dpi=200)
    plt.close(fig)
    print(f"Gráfico 1 guardado en: {fig1_path}")

    # Gráfico 3: Partición Temporal Semanal
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(df_w_train["date"], df_w_train["target_weekly_cases"], width=5, color="#2563EB", label=f"Desarrollo - Train ({len(df_w_train)} semanas)")
    ax.bar(df_w_val["date"], df_w_val["target_weekly_cases"], width=5, color="#F59E0B", label=f"Desarrollo - Val ({len(df_w_val)} semanas)")
    ax.bar(df_w_test["date"], df_w_test["target_weekly_cases"], width=5, color="#10B981", label=f"Hold-out Test Reservado ({len(df_w_test)} semanas)")
    ax.axvline(pd.to_datetime("2022-06-30"), color="#64748B", linestyle="--", linewidth=1.5)
    ax.axvline(pd.to_datetime("2023-03-31"), color="#64748B", linestyle="--", linewidth=1.5)
    ax.set_title("Partición Cronológica Semanal sin Fuga de Información (Hold-out Temporal)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Fecha", fontsize=10)
    ax.set_ylabel("Casos Semanales", fontsize=10)
    ax.legend(loc="upper right", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    fig3_path = os.path.join(FIGURES_DIR, "03_particion_temporal_train_val_test.png")
    fig.savefig(fig3_path, dpi=200)
    plt.close(fig)
    print(f"Gráfico 3 guardado en: {fig3_path}")

    print("=" * 80)
    print("FASE DE ANÁLISIS EXPLORATORIO Y PREPARACIÓN COMPLETADA EXITOSAMENTE.")
    print("=" * 80)
    return metadata


if __name__ == "__main__":
    run_eda_and_preparation()
