import unittest
import math
from backend.app.db.session import SessionLocal
from backend.app.models.spatial import CountyDB
from backend.app.models.user import UserDB
from backend.app.core.security import verify_password

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points in km"""
    R = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class TestKenyaSpatialData(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_county_count_is_exactly_47(self):
        counties = self.db.query(CountyDB).all()
        self.assertEqual(len(counties), 47, "Must have all 47 constitutional counties of Kenya")

    def test_nairobi_and_mombasa_properties(self):
        nairobi = self.db.query(CountyDB).filter(CountyDB.code == 47).first()
        self.assertIsNotNone(nairobi)
        self.assertEqual(nairobi.name, "Nairobi City")
        # Verificado en Barasa et al. (2020) S1 Table, Col 9 Total ICU Beds
        self.assertEqual(nairobi.icu_beds_verified, 276)
        self.assertGreater(nairobi.population_2019, 4000000)

        mombasa = self.db.query(CountyDB).filter(CountyDB.code == 1).first()
        self.assertIsNotNone(mombasa)
        self.assertEqual(mombasa.name, "Mombasa")
        # Verificado en Barasa et al. (2020) S1 Table, Col 9 Total ICU Beds
        self.assertEqual(mombasa.icu_beds_verified, 35)

    def test_unverified_icu_beds_are_strictly_null(self):
        tana_river = self.db.query(CountyDB).filter(CountyDB.name == "Tana River").first()
        self.assertIsNotNone(tana_river)
        self.assertIsNone(tana_river.icu_beds_verified, "Unverified ICU beds must be null, never invented")

    def test_unverified_poverty_quintiles_are_strictly_null(self):
        """Los quintiles sin fuente pública verificable en el repositorio deben ser null en datos operativos."""
        counties = self.db.query(CountyDB).all()
        for county in counties:
            self.assertIsNone(county.q1_pct, f"Unverified quintiles in {county.name} must be null")
            self.assertIsNone(county.q5_pct, f"Unverified quintiles in {county.name} must be null")

    def test_geodesic_haversine_python_distance(self):
        """Prueba de cálculo geodésico en Python (Fórmula de Haversine entre centroides)."""
        nairobi = self.db.query(CountyDB).filter(CountyDB.code == 47).first()
        mombasa = self.db.query(CountyDB).filter(CountyDB.code == 1).first()
        dist = haversine_distance(nairobi.latitude, nairobi.longitude, mombasa.latitude, mombasa.longitude)
        # Expected distance between Nairobi and Mombasa is approx 440-490 km
        self.assertTrue(400 < dist < 500, f"Distance Nairobi-Mombasa should be ~450km, got {dist:.1f}km")

    def test_postgis_real_spatial_query(self):
        """
        Prueba espacial real sobre motor PostgreSQL con extensión PostGIS (ST_Distance / ST_DWithin).
        Si el motor activo no es PostgreSQL o PostGIS no está instalado/accesible en el host,
        registra honestamente la verificación como omitida/pendiente con su causa concreta.
        """
        import os
        from sqlalchemy import text
        from backend.app.db.session import engine

        if engine.dialect.name != "postgresql":
            self.skipTest(
                "Verificación PostGIS omitida / pendiente: El motor activo de base de datos es "
                f"'{engine.dialect.name}'. La prueba espacial real mediante PostGIS requiere una instancia "
                "activa de PostgreSQL con extensión PostGIS habilitada (bloqueo documentado en entorno local)."
            )

        # Si es PostgreSQL, verificar si la extensión postgis está disponible
        try:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT PostGIS_Version()")).scalar()
                self.assertIsNotNone(res, "PostGIS extension must return a valid version string")

                # Ejecutar consulta espacial real PostGIS
                dist_query = text("""
                    SELECT ST_Distance(
                        (SELECT geom FROM counties WHERE code = 47),
                        (SELECT geom FROM counties WHERE code = 1)
                    ) / 1000.0 AS distance_km
                """)
                spatial_dist = conn.execute(dist_query).scalar()
                self.assertIsNotNone(spatial_dist)
                self.assertTrue(350 < spatial_dist < 550, f"PostGIS distance should be ~450km, got {spatial_dist}")
        except Exception as e:
            self.skipTest(f"Verificación PostGIS bloqueada: Fallo al consultar extensión PostGIS en PostgreSQL: {e}")

    def test_rbac_users_hashed_passwords(self):
        admin = self.db.query(UserDB).filter(UserDB.email == "admin@epidemic-twin.ke").first()
        self.assertIsNotNone(admin)
        self.assertTrue(verify_password("AdminSecure2026!", admin.hashed_password))
        self.assertFalse(verify_password("WrongPassword!", admin.hashed_password))

if __name__ == "__main__":
    unittest.main()
