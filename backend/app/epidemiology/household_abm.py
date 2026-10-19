import numpy as np
from typing import Dict, Any, List

class HouseholdABM:
    """
    Micro-Agent Model for Intra-Household Transmission & Socioeconomic Quintiles.
    Captures secondary attack rates (SAR) inside dwellings according to KDHS poverty quintiles.
    Uses PCG64 random generator for exact reproducibility.
    """
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.default_rng(np.random.PCG64(seed))

    def simulate_county_cohort(
        self,
        population_sample: int = 5000,
        poverty_quintiles: Dict[str, float] = None,
        base_intra_sar: float = 0.35,  # Secondary Attack Rate inside household
        external_prevalence: float = 0.05,
        mask_adherence: float = 0.0,
        vaccine_coverage: float = 0.0
    ) -> Dict[str, Any]:
        """
        Simulates household transmission across a representative cohort.
        """
        quintiles = poverty_quintiles or {"q1": 0.2, "q2": 0.2, "q3": 0.2, "q4": 0.2, "q5": 0.2}
        
        # 1. Generate households with sizes based on Kenya census distributions (mean ~4.2, higher in Q1/Q2)
        households = []
        current_pop = 0
        hh_id = 0
        
        q_keys = ["q1", "q2", "q3", "q4", "q5"]
        q_probs = [quintiles[k] for k in q_keys]
        
        while current_pop < population_sample:
            # Quintile assignment
            q = self.rng.choice(q_keys, p=q_probs)
            # Household size: larger in vulnerable quintiles
            if q in ["q1", "q2"]:
                size = int(self.rng.choice([3, 4, 5, 6, 7, 8], p=[0.1, 0.2, 0.3, 0.2, 0.1, 0.1]))
            else:
                size = int(self.rng.choice([1, 2, 3, 4, 5, 6], p=[0.15, 0.25, 0.25, 0.2, 0.1, 0.05]))
            
            households.append({"id": hh_id, "quintile": q, "size": size, "members": []})
            current_pop += size
            hh_id += 1

        # 2. Assign members and simulate infection
        total_infected = 0
        infected_by_quintile = {k: 0 for k in q_keys}
        pop_by_quintile = {k: 0 for k in q_keys}
        vax_by_quintile = {k: 0 for k in q_keys}

        for hh in households:
            q = hh["quintile"]
            size = hh["size"]
            pop_by_quintile[q] += size

            # Socioeconomic disparity in initial vaccine access: Q5 has higher access unless targeted
            # Q1 baseline vax factor: 0.6x, Q5 baseline: 1.4x
            q_vax_weight = {"q1": 0.6, "q2": 0.8, "q3": 1.0, "q4": 1.2, "q5": 1.4}[q]
            hh_vax_prob = min(0.95, vaccine_coverage * q_vax_weight)

            # Crowding factor in transmission
            crowding_factor = 1.3 if q in ["q1", "q2"] else 0.9

            hh_infected = 0
            # Primary infection from community
            for _ in range(size):
                is_vax = self.rng.random() < hh_vax_prob
                if is_vax:
                    vax_by_quintile[q] += 1
                
                # Susceptibility
                susceptibility = 0.15 if is_vax else 1.0
                if self.rng.random() < (external_prevalence * susceptibility):
                    hh_infected += 1

            # Secondary intra-household transmission
            if hh_infected > 0 and hh_infected < size:
                secondary_prob = min(0.9, base_intra_sar * crowding_factor * (1.0 - mask_adherence * 0.4))
                uninfected = size - hh_infected
                for _ in range(uninfected):
                    if self.rng.random() < secondary_prob:
                        hh_infected += 1

            total_infected += hh_infected
            infected_by_quintile[q] += hh_infected

        # Attack rates by quintile
        attack_rate_by_quintile = {}
        for k in q_keys:
            attack_rate_by_quintile[k] = float(infected_by_quintile[k] / max(1, pop_by_quintile[k]))

        return {
            "total_cohort_size": current_pop,
            "households_count": len(households),
            "total_infected": total_infected,
            "overall_attack_rate": float(total_infected / max(1, current_pop)),
            "attack_rate_by_quintile": attack_rate_by_quintile,
            "vaccinated_by_quintile": vax_by_quintile,
            "population_by_quintile": pop_by_quintile,
            "random_seed": self.seed
        }
