import time
import hashlib
import json
from typing import List, Dict, Any, Optional

from backend.app.epidemiology.mobility_engine import MobilityEngine
from backend.app.epidemiology.spatial_seir import SpatialSEIRModel
from backend.app.epidemiology.household_abm import HouseholdABM

class EpidemiologicalDigitalTwin:
    """
    Motor Híbrido Gemelo Digital Epidemiológico a Nivel Poblacional.
    Integra SEIR espacial metapoblacional (47 condados) + ABM intra-domicilio.
    """
    def __init__(
        self,
        counties: List[Dict[str, Any]],
        use_empirical_mobility: bool = False,
        seed: int = 42,
        calibrated_params: Optional[Dict[str, Any]] = None,
        base_intra_sar: Optional[float] = None
    ):
        self.counties = counties
        self.use_empirical_mobility = use_empirical_mobility
        self.seed = seed
        self.calibrated_params = dict(calibrated_params or {})
        if base_intra_sar is not None:
            self.calibrated_params["base_intra_sar"] = base_intra_sar

        # 1. Parámetros calibrados efectivos distinguiendo None, ausencia y 0.0
        def _get_float_param(keys: List[str], default: float, min_val: float = 0.0, max_val: float = 10.0) -> float:
            for k in keys:
                if k in self.calibrated_params and self.calibrated_params[k] is not None:
                    try:
                        v = float(self.calibrated_params[k])
                        if min_val <= v <= max_val:
                            return v
                    except (ValueError, TypeError):
                        pass
            return default

        self.beta_base = _get_float_param(["beta_base", "beta"], 0.35, min_val=0.0, max_val=5.0)
        self.sigma = _get_float_param(["sigma"], 1.0 / 5.2, min_val=0.001, max_val=5.0)
        self.gamma = _get_float_param(["gamma"], 1.0 / 10.0, min_val=0.001, max_val=5.0)
        self.mu = _get_float_param(["mu"], 0.015, min_val=0.0, max_val=1.0)
        self.base_intra_sar = _get_float_param(["base_intra_sar"], 0.35, min_val=0.0, max_val=1.0)
        
        # 2. Iniciar motores componentes
        self.mobility_engine = MobilityEngine(counties, use_empirical=use_empirical_mobility)
        mobility_info = self.mobility_engine.get_mobility_info()
        mobility_src = mobility_info.get("source_type", "ESTIMATED")

        # 3. Derivación estricta de procedencia por componentes
        demographics_prov = "EMPIRICAL" if (self.counties and all(c.get("population_2019", 0) > 0 for c in self.counties)) else "UNKNOWN"
        has_verified_icu = any(c.get("icu_beds_verified") is not None and c.get("icu_source") for c in self.counties)
        icu_prov = "EMPIRICAL" if has_verified_icu else "UNKNOWN"

        self.components_provenance = {
            "demographics": demographics_prov,
            "mobility": mobility_src,
            "icu_beds": icu_prov
        }

        # Árbol de precedencia canónico (SYNTHETIC > UNKNOWN > ESTIMATED > EMPIRICAL)
        try:
            from backend.app.analytics.provenance import resolve_composite_provenance
        except ImportError:
            from app.analytics.provenance import resolve_composite_provenance
        self.source_type, self.is_synthetic, self.is_demo = resolve_composite_provenance(self.components_provenance)

        self.spatial_seir = SpatialSEIRModel(
            counties=counties,
            mobility_matrix=self.mobility_engine.mobility_matrix,
            is_synthetic=self.is_synthetic,
            beta_base=self.beta_base,
            sigma=self.sigma,
            gamma=self.gamma,
            mu=self.mu
        )
        self.household_abm = HouseholdABM(seed=seed)

    def run_simulation(
        self,
        days: int = 120,
        npi_stringency: float = 0.0,
        vaccine_coverage: float = 0.0,
        school_closure: bool = False,
        border_screening: bool = False,
        initial_infected_county: int = 47,
        initial_cases: int = 50
    ) -> Dict[str, Any]:
        start_time = time.time()

        # Ajuste de severidad según medidas
        effective_npi = npi_stringency
        if school_closure:
            effective_npi = min(1.0, effective_npi + 0.15)
        if border_screening:
            effective_npi = min(1.0, effective_npi + 0.08)

        # 1. Ejecutar SEIR Espacial (Macro)
        seir_results = self.spatial_seir.simulate(
            days=days,
            interventions={
                "npi_stringency": effective_npi,
                "vaccine_coverage": vaccine_coverage
            },
            initial_infected_county_code=initial_infected_county,
            initial_infected_count=initial_cases
        )

        # 2. Ejecutar ABM Hogares (Micro) calibrado con la prevalencia pico nacional
        peak_prev = seir_results["national_summary"]["attack_rate"]
        abm_results = self.household_abm.simulate_county_cohort(
            population_sample=10000,
            base_intra_sar=self.base_intra_sar,
            external_prevalence=peak_prev,
            mask_adherence=effective_npi * 0.8,
            vaccine_coverage=vaccine_coverage
        )

        # 3. Equidad: Demographic Parity Ratio (DPR)
        # DPR = (v_Q1 / p_Q1) / (v_Q5 / p_Q5)
        vax_q = abm_results["vaccinated_by_quintile"]
        pop_q = abm_results["population_by_quintile"]
        rate_q1 = vax_q["q1"] / max(1, pop_q["q1"])
        rate_q5 = vax_q["q5"] / max(1, pop_q["q5"])
        dpr = float(rate_q1 / max(1e-4, rate_q5))

        # 4. Métricas de Salud Económica: DALYs = YLL + YLD
        total_deaths = seir_results["national_summary"]["total_deaths"]
        total_cases = seir_results["national_summary"]["total_cases"]
        
        # YLL (Años de Vida Perdidos): Esperanza de vida promedio en Kenia ~66 años, edad promedio de defunción ~54 -> ~12 años perdidos
        yll = total_deaths * 12.5
        # YLD (Años Vividos con Discapacidad): 15% severos (peso 0.133, 14 días), 5% críticos (peso 0.655, 21 días)
        severe_cases = total_cases * 0.15
        critical_cases = total_cases * 0.05
        yld = (severe_cases * (14.0 / 365.0) * 0.133) + (critical_cases * (21.0 / 365.0) * 0.655)
        dalys_total = yll + yld

        # Costos de intervención (USD): vacunas (~$7 por dosis) + implementación NPI
        pop_total = sum(c["population_2019"] for c in self.counties)
        vax_cost_usd = vaccine_coverage * pop_total * 7.5
        npi_cost_usd = effective_npi * pop_total * 1.2
        total_cost_usd = vax_cost_usd + npi_cost_usd
        kes_exchange_rate = 135.0  # 1 USD = ~135 KES
        total_cost_kes = total_cost_usd * kes_exchange_rate

        execution_time_ms = int((time.time() - start_time) * 1000)

        # Hash criptográfico de parámetros para auditoría
        param_payload = {
            "days": days,
            "npi_stringency": effective_npi,
            "vaccine_coverage": vaccine_coverage,
            "school_closure": school_closure,
            "border_screening": border_screening,
            "seed": self.seed,
            "is_synthetic": self.is_synthetic
        }
        param_hash = hashlib.sha256(json.dumps(param_payload, sort_keys=True).encode("utf-8")).hexdigest()
        mobility_info = self.mobility_engine.get_mobility_info()

        return {
            "model_type": "Hybrid_SpatialSEIR_HouseholdABM",
            "source_type": self.source_type,
            "components_provenance": self.components_provenance,
            "effective_calibrated_parameters": {
                "beta_base": self.beta_base,
                "sigma": self.sigma,
                "gamma": self.gamma,
                "mu": self.mu,
                "base_intra_sar": self.base_intra_sar
            },
            "is_synthetic": self.is_synthetic,
            "is_demo": self.is_demo,
            "mobility_source_type": mobility_info.get("source_type", "ESTIMATED"),
            "warning": mobility_info.get("warning") or ("DATOS SINTÉTICOS / NO EMPÍRICOS – NO VÁLIDOS PARA CONCLUSIONES CIENTÍFICAS" if self.is_demo else None),
            "execution_time_ms": execution_time_ms,
            "parameters_hash": param_hash,
            "seed": self.seed,
            "national_summary": seir_results["national_summary"],
            "national_time_series": seir_results["national_time_series"],
            "county_results": seir_results["county_results"],
            "household_equity": {
                "demographic_parity_ratio": round(dpr, 3),
                "attack_rate_by_quintile": abm_results["attack_rate_by_quintile"],
                "equity_assessment": "EQUITATIVO" if 0.8 <= dpr <= 1.2 else ("DESFAVORECE_VULNERABLES" if dpr < 0.8 else "PRO_VULNERABLES")
            },
            "health_economics": {
                "dalys_total": round(dalys_total, 1),
                "yll": round(yll, 1),
                "yld": round(yld, 1),
                "intervention_cost_usd": round(total_cost_usd, 2),
                "intervention_cost_kes": round(total_cost_kes, 2),
                "currency_rates": {"USD_KES": kes_exchange_rate}
            }
        }
