"""
Script de verificación reproducible de ingesta de observaciones.
Demuestra que:
1. Una base recién creada muestra 0 observaciones en dataset_observations y en el endpoint de asistente.
2. Al ejecutar la ingesta formal (scripts/seed_observations_to_db.py), se cargan exactamente 1.606 observaciones empíricas.
3. El conteo real en dataset_observations pasa a 1.606 sin retornos fijos arbitrarios.
"""

import os
import sys
import sqlite3

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

DB_PATH = os.path.join(BASE_DIR, "epidemic_twin.db")

print("=" * 70)
print("TEST DE REPRODUCIBILIDAD: CICLO DE INGESTA LIMPIA DE 1.606 OBSERVACIONES")
print("=" * 70)

# Paso 1: Eliminar base de datos existente para garantizar estado limpio
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("1. Base de datos anterior eliminada. Estado: LIMPIO.")
else:
    print("1. No existía base previa. Estado: LIMPIO.")

# Paso 2: Ejecutar seed_verified_data (crea tablas, usuarios, condados y datasets, SIN observaciones)
print("\n2. Ejecutando seed_verified_data...")
from backend.app.scripts.seed_verified_data import seed_data
seed_data()

# Paso 3: Verificar que en la base recién creada dataset_observations tiene 0 registros
from backend.app.db.session import SessionLocal
from backend.app.models.observation import ObservationDB
from backend.app.models.spatial import CountyDB

db = SessionLocal()
obs_count_initial = db.query(ObservationDB).count()
county_count = db.query(CountyDB).count()
print(f"\n3. Conteo inicial en 'dataset_observations': {obs_count_initial}")
print(f"   Conteo de condados registrados: {county_count}")
assert obs_count_initial == 0, f"ERROR: La base recién creada debió tener 0 observaciones, pero tiene {obs_count_initial}"

# Verificar endpoint data_assistant con base recién creada
from fastapi.testclient import TestClient
from backend.app.main import app
client = TestClient(app)

res_init = client.post("/api/v1/data-assistant/query", json={"query": "resumen general", "cutoff_date": "2024-07-28"})
assert res_init.status_code == 200
data_init = res_init.json()
total_rec_init = data_init["database_observations"]["total_historical_records"]
print(f"   Respuesta del asistente antes de la ingesta (total_historical_records): {total_rec_init}")
assert total_rec_init == 0, f"ERROR: El asistente no debe retornar 1606 cuando la base está vacía. Retornó: {total_rec_init}"

# Paso 4: Ejecutar la ingesta formal de observaciones
print("\n4. Ejecutando scripts/seed_observations_to_db.py...")
from scripts.seed_observations_to_db import seed_observations
seed_observations()

# Paso 5: Verificar que ahora hay exactamente 1606 observaciones en BD
obs_count_after = db.query(ObservationDB).count()
print(f"\n5. Conteo en 'dataset_observations' tras ingesta: {obs_count_after}")
assert obs_count_after == 1606, f"ERROR: Se esperaban 1606 observaciones, pero se obtuvieron {obs_count_after}"

# Verificar endpoint data_assistant tras la ingesta
res_after = client.post("/api/v1/data-assistant/query", json={"query": "resumen general", "cutoff_date": "2024-07-28"})
assert res_after.status_code == 200
data_after = res_after.json()
total_rec_after = data_after["database_observations"]["total_historical_records"]
print(f"   Respuesta del asistente tras la ingesta (total_historical_records): {total_rec_after}")
assert total_rec_after == 1606, f"ERROR: El asistente debe reportar 1606 registros tras la ingesta. Reportó: {total_rec_after}"

# Paso 6: Verificar datos condales y camas UCI Barasa S1
nairobi = db.query(CountyDB).filter(CountyDB.code == 47).first()
mombasa = db.query(CountyDB).filter(CountyDB.code == 1).first()
kiambu = db.query(CountyDB).filter(CountyDB.code == 22).first()
nakuru = db.query(CountyDB).filter(CountyDB.code == 32).first()

print(f"\n6. Verificación de camas UCI oficiales (Barasa et al. 2020 S1 Table):")
print(f"   - Nairobi: {nairobi.icu_beds_verified} camas (Fila 32 S1, Col 9)")
print(f"   - Mombasa: {mombasa.icu_beds_verified} camas (Fila 30 S1, Col 9)")
print(f"   - Kiambu:  {kiambu.icu_beds_verified} camas (Fila 15 S1, Col 9)")
print(f"   - Nakuru:  {nakuru.icu_beds_verified} camas (Fila 33 S1, Col 9)")
print(f"   - Quintiles de pobreza de Nairobi (deben ser None): {nairobi.q1_pct}")

assert nairobi.icu_beds_verified == 276
assert mombasa.icu_beds_verified == 35
assert kiambu.icu_beds_verified == 16
assert nakuru.icu_beds_verified == 20
assert nairobi.q1_pct is None

db.close()
print("\n" + "=" * 70)
print("VERIFICACIÓN EXITOSA: 100% REPRODUCIBLE (0 -> 1.606, Barasa S1 verificado)")
print("=" * 70)
