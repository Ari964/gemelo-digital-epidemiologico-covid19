import numpy as np
from typing import Dict, Any, Optional
from backend.app.analytics.statistics import (
    compute_mape, compute_rmse, compute_r2,
    compare_paired_wilcoxon, clean_paired_series
)

class HypothesisEvaluator:
    """
    Evaluador Científico Formal de la Hipótesis Principal H1:
    'El Gemelo Digital Epidemiológico reduce el error predictivo (MAPE) en al menos 15 puntos
    porcentuales respecto al modelo SEIR estándar (Delta MAPE >= 15.0 pp, Wilcoxon p < 0.05).'

    COMPROMISO METODOLÓGICO Y SEPARACIÓN DE CONCEPTOS:
    1. Si los datos son SYNTHETIC, ESTIMATED o UNKNOWN (source_type != 'EMPIRICAL'),
       el contraste de H1 queda bloqueado con 'BLOCKED_NON_EMPIRICAL'.
    2. Si faltan observaciones reales en el período, retorna 'PENDING_OBSERVATIONS'.
    3. Si falta el modelo base, se calculan métricas descriptivas del candidato pero el
       contraste comparativo queda 'PENDING_BASELINE' (nunca se inventa el modelo base).
    4. Si hay solapamiento con el período de calibración, retorna 'PENDING_INDEPENDENT_EVALUATION'.
    5. Las métricas no calculables son estrictamente None (nunca ceros fabricados).
    """

    @classmethod
    def evaluate_h1(
        cls,
        ground_truth: Any,
        seir_predictions: Optional[Any] = None,
        twin_predictions: Optional[Any] = None,
        is_synthetic: bool = False,
        is_demo: bool = False,
        source_type: str = "EMPIRICAL",
        overlap_detected: bool = False,
        zero_policy: str = "epsilon_smoothed",
        calibration_period_known: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        # Handle case where twin_predictions is passed as second positional argument without baseline
        if twin_predictions is None and seir_predictions is not None and not isinstance(seir_predictions, (list, np.ndarray, tuple)):
            twin_predictions = seir_predictions
            seir_predictions = None

        # 1. Limpieza y alineación de serie candidata vs ground_truth
        yt, yp_twin, audit_twin = clean_paired_series(ground_truth, twin_predictions)

        # 2. Control de observaciones ausentes o muestra insuficiente (< 5)
        if len(yt) < 5 or len(yp_twin) < 5:
            return {
                "h1_status": "PENDING_OBSERVATIONS",
                "h1_supported": False,
                "eligible_for_h1": False,
                "warning": "Observaciones ausentes o muestra insuficiente para evaluación formal.",
                "reason": f"Se registraron {len(yt)} observaciones válidas (mínimo 5 requerido para evaluación cuantitativa).",
                "delta_mape_pp": None,
                "mape_seir_baseline_pct": None,
                "mape_digital_twin_pct": None,
                "rmse_candidate": None,
                "rmse_baseline": None,
                "r2_candidate": None,
                "r2_baseline": None,
                "wilcoxon_test": {"statistic": None, "p_value": None, "is_significant": False},
                "scientific_conclusion": "Evaluación en estado PENDIENTE_OBSERVACIONES por falta de evidencia empírica en el horizonte solicitado.",
                "audit": audit_twin,
                "is_synthetic": is_synthetic,
                "is_demo": is_demo
            }

        # 3. Cálculo de métricas del modelo candidato
        mape_twin, audit_twin_mape = compute_mape(yt, yp_twin, zero_policy=zero_policy)
        rmse_twin = compute_rmse(yt, yp_twin)
        r2_twin = compute_r2(yt, yp_twin)

        # 4. Bloqueo estricto por procedencia sintética o no empírica
        status_blocked = None
        if is_synthetic or source_type == "SYNTHETIC":
            status_blocked = "BLOCKED_SYNTHETIC"
        elif is_demo or source_type != "EMPIRICAL":
            status_blocked = "BLOCKED_NON_EMPIRICAL"

        if status_blocked:
            warn_msg = "DATOS SINTÉTICOS DETECTADOS: NO ELEGIBLE PARA ACEPTACIÓN DE HIPÓTESIS H1" if status_blocked == "BLOCKED_SYNTHETIC" else f"PROCEDENCIA [{source_type}] NO ELEGIBLE PARA ACEPTACIÓN DE HIPÓTESIS H1"
            return {
                "h1_status": status_blocked,
                "h1_supported": False,
                "eligible_for_h1": False,
                "warning": warn_msg,
                "reason": (
                    "La hipótesis científica H1 exige datos de vigilancia epidemiológica verificados (EMPIRICAL). "
                    f"La ejecución actual contiene fuentes clasificadas como {source_type} o modo demo/sintético."
                ),
                "delta_mape_pp": None,
                "mape_seir_baseline_pct": None,
                "mape_digital_twin_pct": mape_twin,
                "rmse_candidate": rmse_twin,
                "rmse_baseline": None,
                "r2_candidate": r2_twin,
                "r2_baseline": None,
                "wilcoxon_test": {"statistic": None, "p_value": None, "is_significant": False},
                "scientific_conclusion": f"Hipótesis H1 no evaluable: Procedencia {source_type}. Métricas descriptivas calculadas solo con fines exploratorios.",
                "audit": audit_twin_mape,
                "is_synthetic": is_synthetic,
                "is_demo": is_demo
            }

        # 5. Control de solapamiento con calibración
        calibration_period_known = kwargs.get("calibration_period_known", True)
        if overlap_detected:
            return {
                "h1_status": "PENDING_INDEPENDENT_EVALUATION",
                "h1_supported": False,
                "eligible_for_h1": False,
                "calibration_status": "OVERLAP_DETECTED",
                "warning": "SOLAPAMIENTO CON PERÍODO DE CALIBRACIÓN DETECTADO",
                "reason": "El intervalo temporal evaluado se solapa con el período de calibración. Se prohíbe presentar este resultado como validación externa o independiente.",
                "delta_mape_pp": None,
                "mape_seir_baseline_pct": None,
                "mape_digital_twin_pct": mape_twin,
                "rmse_candidate": rmse_twin,
                "rmse_baseline": None,
                "r2_candidate": r2_twin,
                "r2_baseline": None,
                "wilcoxon_test": {"statistic": None, "p_value": None, "is_significant": False},
                "scientific_conclusion": "Evaluación descriptiva completada; el solapamiento con la calibración impide aceptar H1 de forma independiente.",
                "audit": audit_twin_mape,
                "is_synthetic": False,
                "is_demo": False
            }

        # 6. Control de ausencia de modelo base (Baseline)
        if seir_predictions is None:
            return {
                "h1_status": "PENDING_BASELINE",
                "h1_supported": False,
                "eligible_for_h1": False,
                "calibration_status": "KNOWN" if calibration_period_known else "CALIBRATION_PERIOD_UNKNOWN",
                "warning": "Simulación base (SEIR clásico) no proporcionada.",
                "reason": "No se registró una simulación base persistida para contrastar la hipótesis H1. No se fabrican predicciones base artificiales.",
                "delta_mape_pp": None,
                "mape_seir_baseline_pct": None,
                "mape_digital_twin_pct": mape_twin,
                "rmse_candidate": rmse_twin,
                "rmse_baseline": None,
                "r2_candidate": r2_twin,
                "r2_baseline": None,
                "wilcoxon_test": {"statistic": None, "p_value": None, "is_significant": False},
                "scientific_conclusion": "Desempeño predictivo del Gemelo Digital evaluado. Contraste de H1 en estado PENDING_BASELINE.",
                "audit": audit_twin_mape,
                "is_synthetic": False,
                "is_demo": False
            }

        # 7. Evaluación comparativa formal con simulación base (Limpieza conjunta de 3 series)
        yt_raw = np.asarray(ground_truth, dtype=float)
        yc_raw = np.asarray(twin_predictions, dtype=float)
        yb_raw = np.asarray(seir_predictions, dtype=float)

        min_len = min(len(yt_raw), len(yc_raw), len(yb_raw))
        if min_len < 10:
            return {
                "h1_status": "PENDING_BASELINE",
                "h1_supported": False,
                "eligible_for_h1": False,
                "calibration_status": "KNOWN" if calibration_period_known else "CALIBRATION_PERIOD_UNKNOWN",
                "warning": f"Muestra insuficiente de puntos compartidos ({min_len} < 10 requerido para comparación).",
                "reason": f"Se requieren al menos 10 puntos temporales comunes entre observaciones, candidata y línea base.",
                "delta_mape_pp": None,
                "mape_seir_baseline_pct": None,
                "mape_digital_twin_pct": mape_twin,
                "rmse_candidate": rmse_twin,
                "rmse_baseline": None,
                "r2_candidate": r2_twin,
                "r2_baseline": None,
                "wilcoxon_test": {"statistic": None, "p_value": None, "is_significant": False},
                "scientific_conclusion": f"Contraste comparativo en estado PENDING_BASELINE: solo {min_len} puntos coincidentes.",
                "audit": audit_twin_mape,
                "is_synthetic": False,
                "is_demo": False
            }

        yt_cut = yt_raw[:min_len]
        yc_cut = yc_raw[:min_len]
        yb_cut = yb_raw[:min_len]

        finite_mask = np.isfinite(yt_cut) & np.isfinite(yc_cut) & np.isfinite(yb_cut)
        yt_shared = yt_cut[finite_mask]
        yc_shared = yc_cut[finite_mask]
        yb_shared = yb_cut[finite_mask]

        if len(yt_shared) < 10:
            return {
                "h1_status": "PENDING_BASELINE",
                "h1_supported": False,
                "eligible_for_h1": False,
                "calibration_status": "KNOWN" if calibration_period_known else "CALIBRATION_PERIOD_UNKNOWN",
                "warning": f"Muestra finita insuficiente tras limpieza conjunta ({len(yt_shared)} puntos < 10 requerido).",
                "reason": f"Solo {len(yt_shared)} puntos compartidos finitos entre las tres series.",
                "delta_mape_pp": None,
                "mape_seir_baseline_pct": None,
                "mape_digital_twin_pct": mape_twin,
                "rmse_candidate": rmse_twin,
                "rmse_baseline": None,
                "r2_candidate": r2_twin,
                "r2_baseline": None,
                "wilcoxon_test": {"statistic": None, "p_value": None, "is_significant": False},
                "scientific_conclusion": "Contraste comparativo en estado PENDING_BASELINE por datos no finitos o desalineación.",
                "audit": audit_twin_mape,
                "is_synthetic": False,
                "is_demo": False
            }

        mape_twin_shared, _ = compute_mape(yt_shared, yc_shared, zero_policy=zero_policy)
        mape_seir, _ = compute_mape(yt_shared, yb_shared, zero_policy=zero_policy)
        rmse_seir = compute_rmse(yt_shared, yb_shared)
        r2_seir = compute_r2(yt_shared, yb_shared)

        if mape_seir is None or mape_twin_shared is None:
            delta_mape_pp = None
        else:
            delta_mape_pp = round(float(mape_seir - mape_twin_shared), 2)

        # Test no paramétrico pareado de Wilcoxon sobre errores absolutos
        errors_seir = np.abs(yt_shared - yb_shared)
        errors_twin = np.abs(yt_shared - yc_shared)
        wilcoxon_res = compare_paired_wilcoxon(errors_seir, errors_twin)

        # Criterio formal de H1 (15 puntos porcentuales de diferencia en MAPE y p < 0.05)
        criteria_delta_passed = (delta_mape_pp is not None) and (delta_mape_pp >= 15.0)
        criteria_wilcoxon_passed = (wilcoxon_res["p_value"] is not None) and (wilcoxon_res["p_value"] < 0.05)
        h1_supported = criteria_delta_passed and criteria_wilcoxon_passed

        status = "SUPPORTED" if h1_supported else "REJECTED"
        if h1_supported:
            conclusion = f"Hipótesis H1 COMPROBADA: El Gemelo Digital reduce el error en {delta_mape_pp:.2f} pp con significancia estadística (Wilcoxon p = {wilcoxon_res['p_value']:.4e} < 0.05)."
        else:
            reasons = []
            if delta_mape_pp is None or delta_mape_pp < 15.0:
                reasons.append(f"Delta MAPE ({delta_mape_pp} pp) no alcanzó el umbral requerido de 15.0 pp")
            if wilcoxon_res["p_value"] is None or wilcoxon_res["p_value"] >= 0.05:
                reasons.append(f"p-valor de Wilcoxon ({wilcoxon_res['p_value']}) >= 0.05")
            conclusion = f"Hipótesis H1 NO COMPROBADA: {'; '.join(reasons)}."

        if not calibration_period_known:
            conclusion += " [AVISO: Período de calibración no registrado; no se puede descartar solapamiento ni certificar evaluación independiente.]"

        return {
            "h1_status": status,
            "h1_supported": h1_supported,
            "eligible_for_h1": True,
            "calibration_status": "KNOWN" if calibration_period_known else "CALIBRATION_PERIOD_UNKNOWN",
            "mape_seir_baseline_pct": mape_seir,
            "mape_digital_twin_pct": mape_twin_shared,
            "delta_mape_pp": delta_mape_pp,
            "required_delta_pp": 15.0,
            "rmse_candidate": rmse_twin,
            "rmse_baseline": rmse_seir,
            "r2_candidate": r2_twin,
            "r2_baseline": r2_seir,
            "wilcoxon_test": wilcoxon_res,
            "scientific_conclusion": conclusion,
            "audit": audit_twin_mape,
            "is_synthetic": False,
            "is_demo": False
        }
