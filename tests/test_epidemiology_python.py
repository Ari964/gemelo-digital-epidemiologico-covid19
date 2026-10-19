import unittest
import numpy as np
import json
import os
from backend.app.epidemiology.seir_baseline import SEIRBaselineModel
from backend.app.epidemiology.mobility_engine import MobilityEngine
from backend.app.epidemiology.spatial_seir import SpatialSEIRModel
from backend.app.epidemiology.household_abm import HouseholdABM
from backend.app.epidemiology.hybrid_engine import EpidemiologicalDigitalTwin
from backend.app.analytics.statistics import compute_mape, compute_rmse, compare_paired_wilcoxon, compute_icu_saturation_auc_roc
from backend.app.analytics.hypothesis_evaluator import HypothesisEvaluator
from backend.app.analytics.model_registry import ModelRegistryManager
from backend.app.analytics.validation_data import ExternalValidationManager

class TestEpidemiologyEngines(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        json_path = os.path.join(os.path.dirname(__file__), "../backend/app/data/kenya_47_counties_verified.json")
        with open(json_path, "r", encoding="utf-8") as f:
            cls.counties = json.load(f)

    def test_seir_baseline_conservation(self):
        model = SEIRBaselineModel(population=100000, initial_infected=50, initial_exposed=100)
        res = model.run(days=60)
        self.assertEqual(len(res["days"]), 61)
        # Check conservation of total population: S + E + I + R + D = N
        total = res["susceptible"][-1] + res["exposed"][-1] + res["infected"][-1] + res["recovered"][-1] + res["deceased"][-1]
        self.assertAlmostEqual(total, 100000, delta=50)

    def test_mobility_empirical_vs_synthetic(self):
        emp_engine = MobilityEngine(self.counties, use_empirical=True)
        # Sin dataset empírico verificado en disco, el motor debe advertir honestamente y no declararse empírico
        emp_info = emp_engine.get_mobility_info()
        self.assertFalse(emp_engine.use_empirical)
        self.assertIsNotNone(emp_info["warning"])
        self.assertIn("Opción empírica deshabilitada", emp_info["warning"])

        syn_engine = MobilityEngine(self.counties, use_empirical=False)
        syn_info = syn_engine.get_mobility_info()
        self.assertIsNotNone(syn_info["warning"])

    def test_spatial_seir_all_47_counties(self):
        emp_engine = MobilityEngine(self.counties, use_empirical=True)
        spatial = SpatialSEIRModel(self.counties, emp_engine.mobility_matrix)
        res = spatial.simulate(days=30, initial_infected_county_code=47, initial_infected_count=100)
        self.assertEqual(len(res["county_results"]), 47)
        self.assertGreater(res["national_summary"]["total_cases"], 100)

    def test_household_abm_reproducibility_with_pcg64(self):
        abm1 = HouseholdABM(seed=12345)
        res1 = abm1.simulate_county_cohort(population_sample=2000)

        abm2 = HouseholdABM(seed=12345)
        res2 = abm2.simulate_county_cohort(population_sample=2000)

        self.assertEqual(res1["total_infected"], res2["total_infected"])
        self.assertEqual(res1["overall_attack_rate"], res2["overall_attack_rate"])

    def test_hybrid_engine_dalys_and_equity(self):
        twin = EpidemiologicalDigitalTwin(self.counties, use_empirical_mobility=True, seed=42)
        res = twin.run_simulation(days=45, npi_stringency=0.3, vaccine_coverage=0.4)
        
        self.assertIn("demographic_parity_ratio", res["household_equity"])
        self.assertIn("dalys_total", res["health_economics"])
        self.assertGreater(res["health_economics"]["dalys_total"], 0)
        self.assertIn("intervention_cost_kes", res["health_economics"])

    def test_hypothesis_evaluator_strict_synthetic_blocking(self):
        y_true = np.array([100, 150, 200, 250, 300])
        y_seir = np.array([130, 195, 260, 325, 390])  # 30% MAPE
        y_twin = np.array([105, 155, 205, 255, 305])  # ~3% MAPE
        
        # Test synthetic blocking hard gate
        blocked_res = HypothesisEvaluator.evaluate_h1(y_true, y_seir, y_twin, is_synthetic=True)
        self.assertEqual(blocked_res["h1_status"], "BLOCKED_SYNTHETIC")
        self.assertFalse(blocked_res["h1_supported"])
        self.assertIn("DATOS SINTÉTICOS", blocked_res["warning"])

        # Test empirical validation: Delta MAPE >= 15.0 and Wilcoxon p < 0.05
        # With larger sample to satisfy Wilcoxon test
        np.random.seed(42)
        y_true_large = np.random.uniform(500, 5000, 30)
        y_seir_large = y_true_large * 1.35  # ~35% MAPE
        y_twin_large = y_true_large * 1.05  # ~5% MAPE (Delta = 30 pp >= 15 pp)
        
        valid_res = HypothesisEvaluator.evaluate_h1(y_true_large, y_seir_large, y_twin_large, is_synthetic=False)
        self.assertEqual(valid_res["h1_status"], "SUPPORTED")
        self.assertTrue(valid_res["h1_supported"])
        self.assertGreaterEqual(valid_res["delta_mape_pp"], 15.0)
        self.assertLess(valid_res["wilcoxon_test"]["p_value"], 0.05)

    def test_model_registry_approval_gate_and_sha256(self):
        # Gate fails if coverage < 80%
        gate_fail = ModelRegistryManager.evaluate_technical_approval(
            r2_fit=0.92, mape=12.0, data_coverage_pct=75.0, is_synthetic=False, approver_name="Dr. Wanjiku"
        )
        self.assertFalse(gate_fail["is_approved"])

        # Gate fails if synthetic data
        gate_synth_fail = ModelRegistryManager.evaluate_technical_approval(
            r2_fit=0.92, mape=12.0, data_coverage_pct=95.0, is_synthetic=True, approver_name="Dr. Wanjiku"
        )
        self.assertFalse(gate_synth_fail["is_approved"])

        # Gate passes with valid data
        gate_pass = ModelRegistryManager.evaluate_technical_approval(
            r2_fit=0.92, mape=12.0, data_coverage_pct=95.0, is_synthetic=False, approver_name="Dr. Wanjiku"
        )
        self.assertTrue(gate_pass["is_approved"])

        # Save and verify SHA-256 artifact
        saved = ModelRegistryManager.save_model_artifact(
            version="v1.0.0-test",
            name="Champion SEIR-ABM",
            parameters={"beta": 0.35},
            metrics={"mape": 12.0, "r2": 0.92},
            technical_approval=True,
            approved_by="Dr. Wanjiku",
            data_coverage_pct=95.0,
            is_synthetic=False
        )
        self.assertIn("sha256_checksum", saved)

        loaded = ModelRegistryManager.load_model_artifact("v1.0.0-test")
        self.assertEqual(loaded["version"], "v1.0.0-test")
        self.assertEqual(loaded["approved_by"], "Dr. Wanjiku")

    def test_external_validation_reports_pending(self):
        status = ExternalValidationManager.get_external_validation_status()
        self.assertEqual(status["status"], "PENDING")
        self.assertIsNone(status["mape"])
        self.assertFalse(status["dataset_available"])

if __name__ == "__main__":
    unittest.main()
