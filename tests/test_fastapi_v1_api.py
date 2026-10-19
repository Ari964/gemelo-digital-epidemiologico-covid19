import os
import unittest
from unittest.mock import patch
import json
from fastapi import HTTPException
from backend.app.db.session import SessionLocal
from backend.app.scripts.seed_verified_data import seed_data
from backend.app.models.user import UserDB
from backend.app.api.v1.endpoints import auth, counties, simulations, reports, chat, validation
from backend.app.schemas.auth import LoginRequest
from backend.app.schemas.simulation import SimulationParameters
from backend.app.schemas.report import ExportReportRequest

class TestFastAPIV1DirectEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed_data()

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_auth_login_and_verify_token(self):
        # Successful login
        req = LoginRequest(email="admin@epidemic-twin.ke", password="AdminSecure2026!")
        resp = auth.login(req, self.db)
        self.assertIn("access_token", resp)
        self.assertEqual(resp["role"], "admin")
        self.assertEqual(resp["email"], "admin@epidemic-twin.ke")

        # Wrong password
        req_bad = LoginRequest(email="admin@epidemic-twin.ke", password="WrongPassword!")
        with self.assertRaises(HTTPException) as ctx:
            auth.login(req_bad, self.db)
        self.assertEqual(ctx.exception.status_code, 401)

    def test_get_47_counties(self):
        county_list = counties.get_all_counties(self.db)
        self.assertEqual(len(county_list), 47)
        mombasa = next(c for c in county_list if c["code"] == 1)
        self.assertEqual(mombasa["name"], "Mombasa")
        self.assertEqual(mombasa["icu_beds_verified"], 35)

        # Camas no verificadas / 0 en Tana River son estrictamente None
        tana = next(c for c in county_list if c["name"] == "Tana River")
        self.assertIsNone(tana["icu_beds_verified"])

    def test_run_simulation_and_audit_trail(self):
        admin = self.db.query(UserDB).filter(UserDB.email == "dr.wanjiku@health.go.ke").first()
        self.assertIsNotNone(admin)

        sim_params = SimulationParameters(
            days=30,
            npi_stringency=0.2,
            vaccine_coverage=0.3,
            initial_infected_county=47,
            initial_cases=50,
            use_empirical_mobility=True,
            seed=42
        )
        sim_res = simulations.run_simulation(sim_params, self.db, admin)
        self.assertIn("simulation_id", sim_res)
        self.assertEqual(len(sim_res["county_results"]), 47)
        self.assertFalse(sim_res["is_synthetic"])
        self.assertIn("demographic_parity_ratio", sim_res["household_equity"])
        self.assertIn("dalys_total", sim_res["health_economics"])

        # Check history
        history = simulations.get_simulation_history(limit=5, db=self.db, current_user=admin)
        self.assertGreater(len(history), 0)
        self.assertEqual(history[0]["user_id"], admin.id)

    def test_export_pdf_and_excel(self):
        admin = self.db.query(UserDB).filter(UserDB.email == "admin@epidemic-twin.ke").first()
        export_req = ExportReportRequest(
            title="Informe de Preparación Pandémica 2026",
            national_summary={
                "total_cases": 120000,
                "total_deaths": 1800,
                "peak_infections": 25000,
                "peak_day": 40,
                "attack_rate": 0.0025
            },
            health_economics={
                "dalys_total": 22500.0,
                "yll": 21000.0,
                "yld": 1500.0,
                "intervention_cost_usd": 1000000.0,
                "intervention_cost_kes": 135000000.0
            }
        )

        pdf_resp = reports.export_pdf(export_req, self.db, admin)
        self.assertEqual(pdf_resp.media_type, "application/pdf")
        self.assertGreater(len(pdf_resp.body), 1000)

        excel_resp = reports.export_excel(export_req, self.db, admin)
        self.assertEqual(excel_resp.media_type, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        self.assertGreater(len(excel_resp.body), 1000)

    def test_chat_ai_strict_503(self):
        admin = self.db.query(UserDB).filter(UserDB.email == "admin@epidemic-twin.ke").first()
        chat_req = chat.ChatRequest(message="¿Qué condado tiene mayor riesgo?")
        # Without reachable Ollama service, must raise HTTP 503, never fake heuristic mocks
        with patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://127.0.0.1:99999"}):
            with self.assertRaises(HTTPException) as ctx:
                chat.copilot_chat(chat_req, admin)
            self.assertEqual(ctx.exception.status_code, 503)

    def test_validation_status(self):
        admin = self.db.query(UserDB).filter(UserDB.email == "admin@epidemic-twin.ke").first()
        val_status = validation.get_validation_status(self.db, admin)
        self.assertEqual(val_status["external_validation_2023_2024"]["status"], "PENDING")
        self.assertEqual(val_status["technical_approval_gate"]["min_coverage_pct"], 80.0)

if __name__ == "__main__":
    unittest.main()
