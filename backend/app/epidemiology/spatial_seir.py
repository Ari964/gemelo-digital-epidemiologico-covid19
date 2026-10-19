import numpy as np
from typing import List, Dict, Any, Optional

class SpatialSEIRModel:
    """
    Metapopulation SEIR model across the 47 counties of Kenya.
    Couples local epidemiological compartments via the inter-county mobility matrix.
    """
    def __init__(
        self,
        counties: List[Dict[str, Any]],
        mobility_matrix: np.ndarray,
        is_synthetic: bool = False,
        beta_base: float = 0.35,
        sigma: float = 1.0 / 5.2,
        gamma: float = 1.0 / 10.0,
        mu: float = 0.015
    ):
        self.counties = counties
        self.K = len(counties)
        self.M = mobility_matrix  # shape (K, K)
        self.is_synthetic = is_synthetic
        self.beta_base = beta_base
        self.sigma = sigma
        self.gamma = gamma
        self.mu = mu

        self.populations = np.array([c["population_2019"] for c in counties], dtype=np.float64)

    def simulate(
        self,
        days: int = 120,
        interventions: Optional[Dict[str, Any]] = None,
        initial_infected_county_code: int = 47,  # Default seed in Nairobi (KE-47)
        initial_infected_count: int = 50
    ) -> Dict[str, Any]:
        """
        Executes discrete-time Euler integration (step = 1 day) for all 47 counties.
        """
        interventions = interventions or {}
        npi_reduction = float(interventions.get("npi_stringency", 0.0))  # 0.0 to 1.0
        vax_coverage = float(interventions.get("vaccine_coverage", 0.0))  # 0.0 to 1.0
        
        # Compartment arrays: shape (K, days + 1)
        S = np.zeros((self.K, days + 1), dtype=np.float64)
        E = np.zeros((self.K, days + 1), dtype=np.float64)
        I = np.zeros((self.K, days + 1), dtype=np.float64)
        R = np.zeros((self.K, days + 1), dtype=np.float64)
        D = np.zeros((self.K, days + 1), dtype=np.float64)
        daily_cases = np.zeros((self.K, days), dtype=np.float64)

        # Initial conditions
        for i, c in enumerate(self.counties):
            N_i = self.populations[i]
            if c["code"] == initial_infected_county_code:
                I[i, 0] = initial_infected_count
                E[i, 0] = initial_infected_count * 2.5
            else:
                I[i, 0] = 0.0
                E[i, 0] = 0.0
            
            # If vaccination applied initially, move fraction of S to R
            vax_fraction = vax_coverage * 0.85  # 85% vaccine efficacy
            R[i, 0] = N_i * vax_fraction
            S[i, 0] = N_i - E[i, 0] - I[i, 0] - R[i, 0]

        # Effective beta accounting for NPIs
        effective_beta = self.beta_base * (1.0 - npi_reduction * 0.7)

        # Time-stepping
        for t in range(days):
            # Compute effective prevalence in each county
            # prev[j] = I[j, t] / N[j]
            prev = I[:, t] / np.maximum(1.0, self.populations)
            
            # Spatial force of infection experienced by county i:
            # lambda_i = beta * sum_j (M_ij * prev_j)
            spatial_pressure = np.dot(self.M, prev)
            lambda_i = effective_beta * spatial_pressure

            # State transitions
            new_exposed = np.clip(lambda_i * S[:, t], 0, S[:, t])
            new_infected = self.sigma * E[:, t]
            new_recovered = self.gamma * I[:, t]
            new_deaths = self.mu * I[:, t]

            daily_cases[:, t] = new_infected

            S[:, t + 1] = S[:, t] - new_exposed
            E[:, t + 1] = E[:, t] + new_exposed - new_infected
            I[:, t + 1] = I[:, t] + new_infected - new_recovered - new_deaths
            R[:, t + 1] = R[:, t] + new_recovered
            D[:, t + 1] = D[:, t] + new_deaths

        # County-level summaries
        county_results = []
        for i, c in enumerate(self.counties):
            total_cases = float(np.sum(daily_cases[i, :]))
            total_deaths = float(D[i, -1])
            peak_i = float(np.max(I[i, :]))
            peak_day = int(np.argmax(I[i, :]))
            icu_beds = c.get("icu_beds_verified")
            
            # ICU saturation threshold: 10% of active severe infections require ICU
            icu_required_peak = peak_i * 0.08
            icu_saturated = False
            if icu_beds is not None and icu_beds > 0:
                icu_saturated = bool(icu_required_peak > (icu_beds * 0.9))

            county_results.append({
                "code": c["code"],
                "name": c["name"],
                "population": int(self.populations[i]),
                "total_cases": round(total_cases),
                "total_deaths": round(total_deaths),
                "peak_infected": round(peak_i),
                "peak_day": peak_day,
                "icu_beds_verified": icu_beds,
                "icu_saturated": icu_saturated,
                "daily_cases": [round(float(x)) for x in daily_cases[i, :]]
            })

        # National aggregation
        national_daily_cases = np.sum(daily_cases, axis=0)
        national_active_infected = np.sum(I, axis=0)
        national_deaths = np.sum(D, axis=0)

        return {
            "days": list(range(days + 1)),
            "is_synthetic": self.is_synthetic,
            "warning": "DATOS SINTÉTICOS – NO VÁLIDOS PARA CONCLUSIONES CIENTÍFICAS" if self.is_synthetic else None,
            "national_summary": {
                "total_cases": int(np.round(np.sum(national_daily_cases))),
                "total_deaths": int(np.round(national_deaths[-1])),
                "peak_infections": int(np.round(np.max(national_active_infected))),
                "peak_day": int(np.argmax(national_active_infected)),
                "attack_rate": float(np.sum(national_daily_cases) / np.sum(self.populations))
            },
            "national_time_series": {
                "daily_cases": [round(float(x)) for x in national_daily_cases],
                "active_infected": [round(float(x)) for x in national_active_infected],
                "cumulative_deaths": [round(float(x)) for x in national_deaths]
            },
            "county_results": county_results
        }
