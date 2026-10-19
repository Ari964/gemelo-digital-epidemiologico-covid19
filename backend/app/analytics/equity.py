import numpy as np
from typing import Dict, Any, List

class EquityEvaluator:
    """
    Evaluador de Equidad Sanitaria y Paridad Demográfica.
    Mide equidad socioeconómica (KDHS Q1-Q5) y geográfica entre condados.
    """

    @staticmethod
    def calculate_demographic_parity_ratio(
        vax_counts: Dict[str, float],
        pop_counts: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        DPR = (v_Q1 / p_Q1) / (v_Q5 / p_Q5)
        - DPR in [0.8, 1.2]: Regla del 80% (Paridad Demográfica Aceptable)
        - DPR < 0.8: Disparidad adversa para el quintil más pobre Q1
        - DPR > 1.2: Enfoque pro-equidad focalizado en los más vulnerables
        """
        v_q1 = vax_counts.get("q1", 0.0)
        p_q1 = max(1.0, pop_counts.get("q1", 1.0))
        rate_q1 = v_q1 / p_q1

        v_q5 = vax_counts.get("q5", 0.0)
        p_q5 = max(1.0, pop_counts.get("q5", 1.0))
        rate_q5 = v_q5 / p_q5

        if rate_q5 == 0:
            dpr = 1.0 if rate_q1 == 0 else 2.0
        else:
            dpr = rate_q1 / rate_q5

        if 0.8 <= dpr <= 1.2:
            verdict = "PARIDAD_DEMOGRAFICA_CUMPLIDA"
            desc = "Distribución vacunal equitativa entre quintiles extremos (Regla del 80%)."
        elif dpr < 0.8:
            verdict = "DISPARIDAD_DESFAVORABLE_Q1"
            desc = f"El quintil más acomodado (Q5) tiene {1.0/max(1e-3, dpr):.1f}x mayor tasa de cobertura que el más vulnerable (Q1)."
        else:
            verdict = "PRIORIZACION_PRO_EQUIDAD"
            desc = f"Focalización afirmativa: Q1 tiene {dpr:.1f}x mayor tasa que Q5."

        return {
            "demographic_parity_ratio": round(dpr, 3),
            "rate_q1_vulnerable": round(rate_q1, 4),
            "rate_q5_wealthy": round(rate_q5, 4),
            "verdict": verdict,
            "description": desc,
            "thresholds": {"min_parity": 0.8, "max_parity": 1.2}
        }

    @staticmethod
    def calculate_gini_index(values: List[float]) -> float:
        """
        Calcula el coeficiente de Gini de desigualdad (0 = perfecta igualdad, 1 = máxima desigualdad).
        """
        arr = np.sort(np.asarray(values, dtype=float))
        n = len(arr)
        if n == 0 or np.sum(arr) == 0:
            return 0.0
        index = np.arange(1, n + 1)
        return float((2.0 * np.sum(index * arr)) / (n * np.sum(arr)) - (n + 1) / n)
