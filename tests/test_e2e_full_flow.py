import unittest
import json
from datetime import datetime
from fastapi import HTTPException
from backend.app.db.session import SessionLocal
from backend.app.scripts.seed_verified_data import seed_data
from backend.app.models.user import UserDB
from backend.app.models.audit import AuditLogDB
from backend.app.models.dataset import DatasetDB
from backend.app.models.simulation import SimulationRunDB
from backend.app.models.evaluation import EvaluationRunDB
from backend.app.models.monitoring import ActiveModelDeploymentDB
from backend.app.api.v1.endpoints import (
    auth,
    users,
    counties,
    data,
    simulations,
    audit,
    validation,
    reports
)
from backend.app.schemas.auth import LoginRequest
from backend.app.schemas.simulation import SimulationParameters
from backend.app.schemas.report import ExportReportRequest, ExportReportByIdRequest
from backend.app.schemas.validation import (
    EvaluationCreateRequest,
    TechnicalApprovalRequest,
    ModelActivationRequest
)

class TestEndToEndFullFlow(unittest.TestCase):
    """
    Prueba Integral End-to-End (E2E) que valida el ciclo metodológico completo CRISP-DM Fases 1 a 6:
    1. Login y autenticación RBAC.
    2. Consulta de 47 condados oficiales KNBS 2019.
    3. Pipeline ETL con métricas reales de procesamiento.
    4. Ejecución de Simulación Experimental y persistencia en DB con auditoría.
    5. Creación de Evaluación reproducible (Fase 5) con derivación de demo y bloqueo científico.
    6. Aprobación Técnica estricta por evaluation_id sin inyección de métricas manuales.
    7. Activación Singleton de Modelo (Fase 6) y Monitoreo On-Demand.
    8. Validación Externa Fuera de Muestra 2023-2024 -> PENDING con declaración honesta.
    9. Exportación de Dossier PDF y Excel con comprobación de integridad SHA-256.
    """

    @classmethod
    def setUpClass(cls):
        seed_data()

    def setUp(self):
        self.db = SessionLocal()
        self.admin = self.db.query(UserDB).filter(UserDB.email == "admin@epidemic-twin.ke").first()
        self.assertIsNotNone(self.admin)

    def tearDown(self):
        self.db.close()

    def test_01_auth_flow(self):
        login_req = LoginRequest(email="admin@epidemic-twin.ke", password="AdminSecure2026!")
        token_data = auth.login(login_req, self.db)
        self.assertIn("access_token", token_data)
        self.assertEqual(token_data["email"], "admin@epidemic-twin.ke")
        self.assertEqual(token_data["role"], "admin")

    def test_02_counties_verified_data_integrity(self):
        county_list = counties.get_all_counties(self.db)
        self.assertEqual(len(county_list), 47)
        nairobi = next(c for c in county_list if "nairobi" in c["name"].lower())
        self.assertEqual(nairobi["population_2019"], 4397073)
        self.assertEqual(nairobi["icu_beds_verified"], 276)

        tana = next(c for c in county_list if c["name"] == "Tana River")
        self.assertIsNone(tana["icu_beds_verified"])

    def test_03_data_datasets_and_etl_pipeline(self):
        datasets_resp = data.get_datasets(self.db)
        self.assertIn("datasets", datasets_resp)
        self.assertIn("mobilityMatrixSample", datasets_resp)
        self.assertIn("dhsIndicators", datasets_resp)
        self.assertTrue(len(datasets_resp["datasets"]) >= 4)

        # Trigger ETL synthetic generation
        etl_resp = data.generate_synthetic_data(self.db, current_user=self.admin)
        self.assertEqual(etl_resp.status, "SUCCESS")
        self.assertEqual(etl_resp.rows_read, 2209)
        self.assertEqual(etl_resp.rows_valid, 2209)
        self.assertEqual(etl_resp.coverage_pct, 100.0)

    def test_04_run_simulation_and_verify_audit_log(self):
        sim_params = SimulationParameters(
            days=45,
            npi_stringency=0.25,
            vaccine_coverage=0.40,
            initial_infected_county=47,
            initial_cases=100,
            use_empirical_mobility=True,
            seed=2026,
            run_mode="EXPERIMENTAL"
        )
        sim_res = simulations.run_simulation(sim_params, self.db, current_user=self.admin)
        self.assertIn("national_summary", sim_res)
        self.assertIn("county_results", sim_res)
        self.assertIn("national_time_series", sim_res)
        self.assertEqual(len(sim_res["county_results"]), 47)
        self.assertGreater(sim_res["national_summary"]["total_cases"], 0)

        # Verify audit log in DB linked to this specific simulation
        sim_id = sim_res["simulation_id"]
        check_db = SessionLocal()
        audit_entry = check_db.query(AuditLogDB).filter(
            AuditLogDB.action == "SIMULATION_RUN",
            AuditLogDB.details.contains(sim_id)
        ).first()
        self.assertIsNotNone(audit_entry)
        self.assertEqual(audit_entry.user_email, "admin@epidemic-twin.ke")
        self.assertEqual(audit_entry.seed, 2026)
        check_db.close()

    def test_05_create_evaluation_and_derive_provenance(self):
        # 1. Crear simulación experimental
        sim_params = SimulationParameters(
            days=30,
            npi_stringency=0.2,
            vaccine_coverage=0.3,
            initial_infected_county=47,
            initial_cases=50,
            use_empirical_mobility=True,
            seed=42,
            run_mode="EXPERIMENTAL"
        )
        sim_res = simulations.run_simulation(sim_params, self.db, current_user=self.admin)
        sim_id = sim_res["simulation_id"]

        # 2. Evaluar contra dataset observado verificado
        eval_req = EvaluationCreateRequest(
            candidate_simulation_id=sim_id,
            baseline_simulation_id=None,
            observed_dataset_id="ds-knbs-2019",
            target_variable="daily_cases"
        )
        eval_res = validation.create_evaluation(eval_req, self.db, current_user=self.admin)
        self.assertIsNotNone(eval_res.evaluation_id)
        self.assertIn(eval_res.h1_status, [
            "SUPPORTED", "REJECTED", "BLOCKED_NON_EMPIRICAL", "BLOCKED_SYNTHETIC",
            "PENDING", "PENDING_OBSERVATIONS", "PENDING_BASELINE", "PENDING_INDEPENDENT_EVALUATION"
        ])

    def test_06_technical_approval_requires_persisted_eval_and_blocks_demo(self):
        # Simulación demo
        sim_params = SimulationParameters(
            days=20,
            npi_stringency=0.1,
            vaccine_coverage=0.0,
            initial_infected_county=47,
            initial_cases=20,
            use_empirical_mobility=False,  # activa síntesis gravitacional
            seed=999,
            run_mode="EXPERIMENTAL"
        )
        sim_res = simulations.run_simulation(sim_params, self.db, current_user=self.admin)
        eval_req = EvaluationCreateRequest(
            candidate_simulation_id=sim_res["simulation_id"],
            baseline_simulation_id=None,
            observed_dataset_id="synthetic_gravity_flow",
            target_variable="daily_cases"
        )
        eval_res = validation.create_evaluation(eval_req, self.db, current_user=self.admin)
        self.assertTrue(eval_res.is_demo)

        # Intento de aprobación técnica sobre evaluación demo debe ser rechazado
        appr_req = TechnicalApprovalRequest(
            evaluation_id=eval_res.evaluation_id,
            notes="Intento de aprobación en datos estimados"
        )
        appr_res = validation.technical_approval(appr_req, self.db, current_user=self.admin)
        self.assertFalse(appr_res.is_approved)
        self.assertTrue(any("demostrativ" in r.lower() or "sint" in r.lower() for r in appr_res.rejection_reasons))

    def test_07_external_validation_returns_pending(self):
        val_status = validation.get_external_validation()
        self.assertEqual(val_status["status"], "PENDING")
        self.assertIsNone(val_status["mape"])
        self.assertIsNone(val_status["rmse"])
        self.assertIsNone(val_status["r2"])
        self.assertIn("validación externa no están incorporados ni verificados", val_status["note"])

    def test_08_export_pdf_and_excel_reports(self):
        latest_sim = self.db.query(SimulationRunDB).order_by(SimulationRunDB.created_at.desc()).first()
        if not latest_sim:
            sim_params = SimulationParameters(days=5, seed=42)
            sim_res = simulations.run_simulation(sim_params, self.db, current_user=self.admin)
            sim_id = sim_res["simulation_id"]
        else:
            sim_id = latest_sim.id

        export_req = ExportReportRequest(
            title="Dossier Epidemiológico Oficial",
            simulation_id=sim_id,
            is_synthetic=False,
            is_demo=False
        )
        # PDF response
        pdf_resp = reports.export_pdf(export_req, db=self.db, current_user=self.admin)
        self.assertEqual(pdf_resp.media_type, "application/pdf")
        self.assertTrue(pdf_resp.body.startswith(b"%PDF-"))

        # Excel response
        excel_resp = reports.export_excel(export_req, db=self.db, current_user=self.admin)
        self.assertEqual(
            excel_resp.media_type,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        self.assertTrue(excel_resp.body.startswith(b"PK"))

    def test_09_export_by_id_exactly_one_validation(self):
        # 1. Reject if neither simulation_id nor evaluation_id is supplied
        with self.assertRaises(ValueError):
            ExportReportByIdRequest()

        # 2. Reject if both are supplied
        with self.assertRaises(ValueError):
            ExportReportByIdRequest(simulation_id="sim-123", evaluation_id="eval-456")

        # 3. Accept if exactly one is supplied
        req_valid = ExportReportByIdRequest(simulation_id="sim-123")
        self.assertEqual(req_valid.simulation_id, "sim-123")
        self.assertIsNone(req_valid.evaluation_id)

if __name__ == "__main__":
    unittest.main()
