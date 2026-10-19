"""
Script para la descarga e incorporación reproducible del dataset público epidemiológico.
Fuente: Our World in Data (OWID) - COVID-19 Public Database.
Institución: University of Oxford / Global Change Data Lab.
Licencia: Creative Commons Attribution 4.0 International (CC BY 4.0).
Estado del Repositorio: Archivo histórico oficial congelado en 2024.
"""

import os
import sys
import json
import hashlib
import urllib.request
import pandas as pd
from datetime import datetime

# Definición de rutas absolutas
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# Metadatos institucionales y de procedencia
DATASET_METADATA = {
    "institution": "Our World in Data (OWID) / University of Oxford / Global Change Data Lab",
    "dataset_title": "Coronavirus Pandemic (COVID-19) - Kenya Official Time-Series Data",
    "source_page_url": "https://ourworldindata.org/coronavirus",
    "direct_download_url": "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv",
    "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
    "query_date": "2026-09-23",
    "target_country_iso": "KEN",
    "country_name": "Kenya",
    "historical_status": "Repositorio histórico consolidado; congeló actualizaciones periódicas en 2024 debido a la transición global de reporte de la OMS.",
    "description": (
        "Dataset epidemiológico oficial con registros de casos confirmados, muertes, pruebas, "
        "tasa de positividad, tasa de reproducción (Rt), índice de rigor de políticas gubernamentales (Oxford Blavatnik "
        "School Stringency Index) y avance de vacunación para Kenia, consolidado a partir de reportes del Ministerio de "
        "Salud de Kenia (MoH) y la Organización Mundial de la Salud (OMS)."
    ),
    "coverage_temporal": "2020-01-05 a 2024-08-04",
    "coverage_geographic": "Kenya (National Level - ISO: KEN)",
    "target_variable": "new_cases (conteo semanal acumulado reportado los domingos)",
    "target_variable_smoothed": "new_cases_smoothed (media móvil de 7 días generada por OWID dividiendo el reporte semanal)"
}

RAW_FILE_PATH = os.path.join(RAW_DATA_DIR, "owid_covid_kenya_raw.csv")
RAW_META_PATH = os.path.join(RAW_DATA_DIR, "dataset_metadata.json")


def download_and_extract_kenya_data():
    print("=" * 80)
    print("DESCARGA E INCORPORACIÓN REPRODUCIBLE DE DATASET PÚBLICO OFICIAL")
    print("=" * 80)
    print(f"Institución: {DATASET_METADATA['institution']}")
    print(f"URL de Origen: {DATASET_METADATA['direct_download_url']}")
    print(f"Licencia: {DATASET_METADATA['license']}")
    print(f"Extrayendo registros auténticos para ISO: {DATASET_METADATA['target_country_iso']} ({DATASET_METADATA['country_name']})...")

    req = urllib.request.Request(
        DATASET_METADATA["direct_download_url"],
        headers={"User-Agent": "Epidemic-Twin-Kenya-Academic/1.0"}
    )

    lines_kenya = []
    header = ""

    with urllib.request.urlopen(req, timeout=60) as response:
        header = response.readline().decode("utf-8")
        lines_kenya.append(header)
        for raw_line in response:
            line_str = raw_line.decode("utf-8", errors="replace")
            # Filtrado exacto para Kenya sin alterar ningún dato original
            if line_str.startswith(f"{DATASET_METADATA['target_country_iso']},"):
                lines_kenya.append(line_str)

    total_records = len(lines_kenya) - 1
    print(f"Descargadas {total_records} filas históricas auténticas para Kenia.")

    # Guardar archivo original sin alteraciones
    with open(RAW_FILE_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines_kenya)

    # Calcular hash criptográfico SHA-256 del archivo extraído
    with open(RAW_FILE_PATH, "rb") as f:
        content_bytes = f.read()
        sha256_hash = hashlib.sha256(content_bytes).hexdigest()

    DATASET_METADATA["file_name"] = os.path.basename(RAW_FILE_PATH)
    DATASET_METADATA["file_size_bytes"] = len(content_bytes)
    DATASET_METADATA["sha256_checksum"] = sha256_hash
    DATASET_METADATA["total_records"] = total_records
    DATASET_METADATA["downloaded_at"] = datetime.utcnow().isoformat() + "Z"

    with open(RAW_META_PATH, "w", encoding="utf-8") as f:
        json.dump(DATASET_METADATA, f, indent=2, ensure_ascii=False)

    print(f"Archivo de Kenia preservado en: {RAW_FILE_PATH}")
    print(f"Checksum SHA-256: {sha256_hash}")
    print(f"Metadatos de procedencia guardados en: {RAW_META_PATH}")

    # Verificación de carga con pandas
    df = pd.read_csv(RAW_FILE_PATH)
    print(f"Dimensiones del archivo crudo: {df.shape[0]} filas x {df.shape[1]} columnas.")
    print(f"Rango de fechas observado: {df['date'].min()} a {df['date'].max()}.")
    return df, DATASET_METADATA


if __name__ == "__main__":
    download_and_extract_kenya_data()
