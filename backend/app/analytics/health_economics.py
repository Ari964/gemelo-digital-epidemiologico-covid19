from typing import Dict, Any

class HealthEconomicsCalculator:
    """
    Calculador de Métricas de Economía de la Salud (DALYs, YLL, YLD, ICER).
    Documentado en USD y KES (tasa de cambio KES 135 por USD).
    """
    KES_PER_USD: float = 135.0

    @staticmethod
    def calculate_dalys(
        total_deaths: float,
        mild_cases: float,
        severe_cases: float,
        critical_cases: float,
        average_years_lost_per_death: float = 12.5
    ) -> Dict[str, Any]:
        """
        Calcula Años de Vida Ajustados por Discapacidad: DALY = YLL + YLD.
        - YLL = Muertes * Años de vida perdidos estándar
        - YLD = Sum(Casos_s * Duración_s * Peso_Discapacidad_s)
          Pesos Global Burden of Disease:
          Leve: 0.051 (7 días)
          Severo: 0.133 (14 días)
          Crítico: 0.655 (21 días)
        """
        yll = total_deaths * average_years_lost_per_death
        
        yld_mild = mild_cases * (7.0 / 365.0) * 0.051
        yld_severe = severe_cases * (14.0 / 365.0) * 0.133
        yld_critical = critical_cases * (21.0 / 365.0) * 0.655
        yld_total = yld_mild + yld_severe + yld_critical

        daly_total = yll + yld_total

        return {
            "daly_total": round(daly_total, 1),
            "yll": round(yll, 1),
            "yld": round(yld_total, 1),
            "breakdown": {
                "yld_mild": round(yld_mild, 1),
                "yld_severe": round(yld_severe, 1),
                "yld_critical": round(yld_critical, 1)
            }
        }

    @classmethod
    def calculate_icer(
        cls,
        cost_intervention_usd: float,
        cost_baseline_usd: float,
        dalys_intervention: float,
        dalys_baseline: float
    ) -> Dict[str, Any]:
        """
        Calcula la Razón de Costo-Efectividad Incremental (ICER):
        ICER = (Costo_Intervencion - Costo_Base) / (DALYs_Salvados)
        Donde DALYs_Salvados = DALYs_Base - DALYs_Intervencion.
        """
        delta_cost_usd = cost_intervention_usd - cost_baseline_usd
        dalys_averted = dalys_baseline - dalys_intervention

        if dalys_averted <= 0:
            icer_usd = 0.0
            interpretation = "Dominada (No ahorra DALYs respecto al comparador)"
        else:
            icer_usd = delta_cost_usd / dalys_averted
            # Umbral OMS: Costo-efectivo si ICER < 3x PIB per cápita (Kenia PIB per cápita ~ $2,100 USD)
            if icer_usd < 2100:
                interpretation = "Muy Costo-Efectivo (< 1x PIB per cápita de Kenia)"
            elif icer_usd < 6300:
                interpretation = "Costo-Efectivo (< 3x PIB per cápita de Kenia)"
            else:
                interpretation = "No Costo-Efectivo (> 3x PIB per cápita de Kenia)"

        icer_kes = icer_usd * cls.KES_PER_USD

        return {
            "dalys_averted": round(dalys_averted, 1),
            "delta_cost_usd": round(delta_cost_usd, 2),
            "delta_cost_kes": round(delta_cost_usd * cls.KES_PER_USD, 2),
            "icer_usd_per_daly": round(icer_usd, 2),
            "icer_kes_per_daly": round(icer_kes, 2),
            "interpretation": interpretation,
            "currency": {"exchange_rate": cls.KES_PER_USD, "reference": "USD/KES"}
        }
