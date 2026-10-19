import json
import os
import sys
import hashlib

# Ensure backend root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from backend.app.core.security import hash_password
import backend.app.db.session as session_module
from backend.app.models.user import UserDB
from backend.app.models.spatial import CountyDB
from backend.app.models.dataset import DatasetDB

def seed_data():
    print("Iniciando creación de tablas en la base de datos...")
    session_module.Base.metadata.create_all(bind=session_module.engine)
    db = session_module.SessionLocal()
    
    try:
        # 1. Seed Usuarios Oficiales con contraseñas hash bcrypt
        if db.query(UserDB).count() == 0:
            print("Sembrando usuarios con roles RBAC...")
            users = [
                UserDB(
                    id="usr-001",
                    name="Ing. Administrador Sistema",
                    email="admin@epidemic-twin.ke",
                    hashed_password=hash_password("AdminSecure2026!"),
                    role="admin",
                    status="active"
                ),
                UserDB(
                    id="usr-002",
                    name="Dra. Wanjiku (Epidemióloga Jefe)",
                    email="dr.wanjiku@health.go.ke",
                    hashed_password=hash_password("EpiChief2026!"),
                    role="epidemiologist",
                    status="active"
                ),
                UserDB(
                    id="usr-003",
                    name="Analista Omondi (MOH Kenya)",
                    email="omondi@moh.go.ke",
                    hashed_password=hash_password("AnalystMOH2026!"),
                    role="analyst",
                    status="active"
                )
            ]
            db.add_all(users)
            db.commit()
            print("3 usuarios iniciales creados exitosamente.")
        else:
            print("Usuarios ya existentes.")

        # 2. Seed 47 Condados Verificados
        if db.query(CountyDB).count() == 0:
            json_path = os.path.join(os.path.dirname(__file__), "../data/kenya_47_counties_verified.json")
            with open(json_path, "r", encoding="utf-8") as f:
                counties_data = json.load(f)

            print(f"Sembrando {len(counties_data)} condados oficiales de Kenia (KNBS 2019 + Barasa et al. 2020)...")
            counties = []
            for item in counties_data:
                q = item.get("poverty_quintiles")
                county = CountyDB(
                    code=item["code"],
                    iso_code=item["iso_code"],
                    name=item["name"],
                    capital=item["capital"],
                    population_2019=item["population_2019"],
                    area_sq_km=item["area_sq_km"],
                    latitude=item["latitude"],
                    longitude=item["longitude"],
                    q1_pct=q.get("q1") if q else None,
                    q2_pct=q.get("q2") if q else None,
                    q3_pct=q.get("q3") if q else None,
                    q4_pct=q.get("q4") if q else None,
                    q5_pct=q.get("q5") if q else None,
                    icu_beds_verified=item.get("icu_beds_verified"),
                    icu_source=item.get("icu_source"),
                    data_quality_flags=json.dumps(item.get("data_quality_flags", []))
                )
                counties.append(county)
            
            db.add_all(counties)
            db.commit()
            print(f"Éxito: {len(counties)} condados sembrados en la base de datos.")
        else:
            print(f"Condados ya registrados ({db.query(CountyDB).count()}).")

        # 3. Seed Datasets Oficiales con Linaje y Procedencia Formal
        json_path = os.path.join(os.path.dirname(__file__), "../data/kenya_47_counties_verified.json")
        counties_hash = ""
        if os.path.exists(json_path):
            with open(json_path, "rb") as f:
                counties_hash = hashlib.sha256(f.read()).hexdigest()

        default_datasets = [
            {
                "id": "ds-knbs-2019",
                "name": "Censo Poblacional Kenia KNBS 2019",
                "source": "Kenya National Bureau of Statistics (KNBS)",
                "source_type": "EMPIRICAL",
                "source_name": "KNBS 2019 Kenya Population and Housing Census",
                "source_reference": "KNBS Official Census Volume I-IV (2019)",
                "is_synthetic": False,
                "records_count": 47,
                "coverage_pct": 100.0,
                "quality_status": "VERIFIED",
                "content_sha256": counties_hash,
                "metadata_json": json.dumps({"description": "Población y áreas oficiales por condado (47 condados)", "unit": "individuals"})
            },
            {
                "id": "ds-kdhs-2022",
                "name": "Encuesta Demográfica y de Salud KDHS 2022 (Indicadores Estimados)",
                "source": "KDHS / KNBS",
                "source_type": "ESTIMATED",
                "source_name": "Kenya Demographic and Health Survey 2022",
                "source_reference": "KNBS & ICF (2022)",
                "is_synthetic": False,
                "records_count": 47,
                "coverage_pct": 100.0,
                "quality_status": "WARNING",
                "content_sha256": None,
                "metadata_json": json.dumps({
                    "description": "Distribución socioeconómica referencial estimada. No registrada como VERIFIED por carecer de microdatos abiertos condales auditados en el repositorio.",
                    "warning": "NO REGISTRADO COMO VERIFIED: Las encuestas KDHS nacionales no proveen microdatos abiertos de quintiles por condado en este repositorio; las cifras no verificables se eliminan de los datos operativos."
                })
            },
            {
                "id": "ds-meta-mobility",
                "name": "Matriz de Movilidad Estimada (Distancia y Corredores)",
                "source": "Modelo Estimado de Conectividad y Distancia Geodésica",
                "source_type": "ESTIMATED",
                "source_name": "Estimador Gravitacional y Corredores Viales A104",
                "source_reference": "Fórmula potencial poblacional calibrada intercondado",
                "is_synthetic": False,
                "records_count": 47,
                "coverage_pct": 94.2,
                "quality_status": "WARNING",
                "content_sha256": None,
                "metadata_json": json.dumps({
                    "description": "Matriz de movilidad estimada a partir de población, distancia y conectividad. No representa flujos observados directamente.",
                    "disclaimer": "MATRIZ ESTIMADA – NO REPRESENTA TRAZAS DE GPS OBSERVADAS DIRECTAMENTE"
                })
            },
            {
                "id": "ds-synthetic-gravity",
                "name": "Modelo Gravitacional Sintético Demostrativo",
                "source": "Generador Sintético Gravity",
                "source_type": "SYNTHETIC",
                "source_name": "Synthetic Gravity Model Generator",
                "source_reference": "Simulación teórica de gravedad no calibrada",
                "is_synthetic": True,
                "records_count": 47,
                "coverage_pct": 100.0,
                "quality_status": "WARNING",
                "content_sha256": None,
                "metadata_json": json.dumps({"warning": "DATOS SINTÉTICOS – NO VÁLIDOS PARA CONCLUSIONES CIENTÍFICAS"})
            }
        ]

        for d_info in default_datasets:
            existing = db.query(DatasetDB).filter(DatasetDB.id == d_info["id"]).first()
            if not existing:
                db.add(DatasetDB(**d_info))
            else:
                existing.source_type = d_info["source_type"]
                existing.source_name = d_info["source_name"]
                existing.source_reference = d_info["source_reference"]
                existing.quality_status = d_info["quality_status"]
                existing.content_sha256 = d_info["content_sha256"]
                existing.metadata_json = d_info["metadata_json"]
        db.commit()
        print("Datasets sincronizados con linaje, procedencia y advertencias metodológicas.")

    except Exception as e:
        db.rollback()
        print(f"Error al sembrar datos: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
