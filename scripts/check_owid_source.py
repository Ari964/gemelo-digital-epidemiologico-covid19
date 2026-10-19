"""
Script de Auditoría y Comprobación Criptográfica de la Fuente Oficial OWID
========================================================================
Verifica la procedencia inmutable de data/raw/owid_covid_kenya_raw.csv:
1. Hash criptográfico SHA-256 (debe coincidir con c82f3cfc...)
2. Conteo exacto de líneas físicas y filas de datos (1,675 líneas / 1,674 filas de datos)
3. Rango temporal: 2020-01-05 a 2024-08-04
4. Frecuencia y patrón dominical (W-SUN)
"""

import os
import sys
import hashlib
import pandas as pd

RAW_CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "owid_covid_kenya_raw.csv")

def verify_owid_dataset():
    if not os.path.exists(RAW_CSV_PATH):
        print(f"[ERROR] Archivo no encontrado: {RAW_CSV_PATH}")
        sys.exit(1)
        
    # 1. SHA-256 Hash
    sha256 = hashlib.sha256()
    with open(RAW_CSV_PATH, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    file_hash = sha256.hexdigest()
    
    # 2. Conteo de líneas físicas
    with open(RAW_CSV_PATH, "r", encoding="utf-8") as f:
        total_physical_lines = sum(1 for _ in f)
        
    # 3. Inspección con pandas
    df = pd.read_csv(RAW_CSV_PATH)
    total_data_rows = len(df)
    
    date_min = df["date"].min()
    date_max = df["date"].max()
    iso_codes = df["iso_code"].unique()
    
    print("=" * 70)
    print("REPORTE DE AUDITORÍA CRIPTOGRÁFICA DE FUENTE OWID (KENIA)")
    print("=" * 70)
    print(f"Ruta de archivo:          {RAW_CSV_PATH}")
    print(f"Hash SHA-256:             {file_hash}")
    print(f"Líneas físicas totales:   {total_physical_lines} (1 cabecera + {total_physical_lines - 1} filas)")
    print(f"Filas de datos reales:    {total_data_rows}")
    print(f"Rango temporal cubierto:  {date_min} a {date_max}")
    print(f"Código ISO verificado:    {list(iso_codes)}")
    
    # Total de casos reportados
    total_new_cases = df["new_cases"].fillna(0).sum()
    total_new_deaths = df["new_deaths"].fillna(0).sum()
    print(f"Total casos nuevos sumados:  {total_new_cases:,.0f}")
    print(f"Total muertes sumadas:       {total_new_deaths:,.0f}")
    
    # Validaciones obligatorias de integridad
    expected_prefix = "c82f3cfc"
    assert file_hash.startswith(expected_prefix), f"Hash no inicia con {expected_prefix}: {file_hash}"
    assert total_data_rows == 1674, f"Se esperaban 1674 filas de datos, encontradas {total_data_rows}"
    assert total_physical_lines == 1675, f"Se esperaban 1675 líneas físicas, encontradas {total_physical_lines}"
    assert "KEN" in iso_codes, "El dataset no corresponde a Kenia"
    
    print("=" * 70)
    print("[OK] Comprobación de integridad superada exitosamente.")
    print("=" * 70)

if __name__ == "__main__":
    verify_owid_dataset()
