import numpy as np
from scipy import stats
from sklearn import metrics
from typing import List, Dict, Any, Tuple, Optional

def clean_paired_series(
    y_true: Any,
    y_pred: Any
) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Valida y alinea dos series pareadas, filtrando valores nulos o no finitos.
    Retorna arrays limpios y metadatos de auditoría (conteos de ceros, faltantes y exclusiones).
    """
    if y_true is None or y_pred is None:
        return np.array([]), np.array([]), {"observations_count": 0, "zeros_count": 0, "missing_count": 0, "exclusions_count": 0}

    try:
        yt = np.asarray(y_true, dtype=float)
        yp = np.asarray(y_pred, dtype=float)
    except Exception:
        return np.array([]), np.array([]), {"observations_count": 0, "zeros_count": 0, "missing_count": 0, "exclusions_count": 0}

    if yt.shape != yp.shape:
        # Intentar truncar a la longitud mínima común si es unidimensional
        if yt.ndim == 1 and yp.ndim == 1:
            min_len = min(len(yt), len(yp))
            yt = yt[:min_len]
            yp = yp[:min_len]
        else:
            return np.array([]), np.array([]), {"observations_count": 0, "zeros_count": 0, "missing_count": 0, "exclusions_count": 0}

    # Máscara de valores finitos
    finite_mask = np.isfinite(yt) & np.isfinite(yp)
    missing_count = int(np.sum(~finite_mask))

    yt_clean = yt[finite_mask]
    yp_clean = yp[finite_mask]

    zeros_count = int(np.sum(yt_clean == 0))
    total_obs = len(yt_clean)

    audit_info = {
        "observations_count": total_obs,
        "zeros_count": zeros_count,
        "missing_count": missing_count,
        "exclusions_count": missing_count
    }
    return yt_clean, yp_clean, audit_info

def compute_mape(
    y_true: Any,
    y_pred: Any,
    zero_policy: str = "exclude"
) -> Tuple[Optional[float], Dict[str, Any]]:
    """
    Mean Absolute Percentage Error (MAPE).
    Manejo documentado de observaciones iguales a cero:
    - zero_policy='exclude': Excluye observaciones donde y_true == 0 para evitar distorsiones asintóticas.
    - Si todas las observaciones son cero o la serie está vacía, retorna (None, audit_info).
    """
    yt, yp, audit = clean_paired_series(y_true, y_pred)
    if len(yt) == 0:
        audit["zero_handling_method"] = "empty_series"
        return None, audit

    if zero_policy == "exclude":
        non_zero_mask = yt > 0
        excluded = int(np.sum(~non_zero_mask))
        audit["exclusions_count"] += excluded
        audit["zero_handling_method"] = f"excluded_{excluded}_zero_observations"
        
        yt_eval = yt[non_zero_mask]
        yp_eval = yp[non_zero_mask]
        
        if len(yt_eval) == 0:
            return None, audit
            
        mape_val = float(np.mean(np.abs((yt_eval - yp_eval) / yt_eval)) * 100.0)
        return round(mape_val, 2), audit
    else:
        # Fallback con epsilon documentado
        eps = 1.0
        audit["zero_handling_method"] = f"epsilon_smoothed_eps_{eps}"
        denominator = np.maximum(yt, eps)
        mape_val = float(np.mean(np.abs((yt - yp) / denominator)) * 100.0)
        return round(mape_val, 2), audit

def compute_rmse(y_true: Any, y_pred: Any) -> Optional[float]:
    """Root Mean Squared Error (RMSE). Retorna None si la serie está vacía."""
    yt, yp, _ = clean_paired_series(y_true, y_pred)
    if len(yt) == 0:
        return None
    val = float(np.sqrt(np.mean((yt - yp) ** 2)))
    return round(val, 2)

def compute_r2(y_true: Any, y_pred: Any) -> Optional[float]:
    """
    Coeficiente de Determinación (R²).
    Retorna None si la muestra es menor a 2 o si la varianza de y_true es nula.
    """
    yt, yp, _ = clean_paired_series(y_true, y_pred)
    if len(yt) < 2:
        return None
    ss_tot = float(np.sum((yt - np.mean(yt)) ** 2))
    if ss_tot == 0.0:
        # Varianza nula en observaciones: R² no está definido
        return None
    ss_res = float(np.sum((yt - yp) ** 2))
    r2_val = float(1.0 - (ss_res / ss_tot))
    return round(r2_val, 4)

def compare_paired_wilcoxon(
    errors_model_a: Any,
    errors_model_b: Any
) -> Dict[str, Any]:
    """
    Test de Rangos con Signo de Wilcoxon para muestras pareadas.
    Comprueba si el Modelo B tiene errores significativamente menores al Modelo A.
    Retorna estadístico y p-valor nulos si la muestra es insuficiente (< 5) o no hay diferencias.
    """
    ea, eb, audit = clean_paired_series(errors_model_a, errors_model_b)
    n = len(ea)
    if n < 5:
        return {
            "statistic": None,
            "p_value": None,
            "is_significant": False,
            "interpretation": f"Muestra insuficiente ({n} < 5) para aplicar test no paramétrico de Wilcoxon."
        }

    diff = ea - eb
    if np.all(diff == 0):
        return {
            "statistic": None,
            "p_value": None,
            "is_significant": False,
            "interpretation": "Diferencias pareadas todas iguales a cero: idéntica precisión empírica."
        }

    try:
        res = stats.wilcoxon(ea, eb, alternative='greater')
        stat = float(res.statistic)
        p_val = float(res.pvalue)
        return {
            "statistic": round(stat, 4),
            "p_value": float(p_val),
            "is_significant": bool(p_val < 0.05),
            "interpretation": "El modelo candidato reduce significativamente el error respecto a la línea base (p < 0.05)" if p_val < 0.05 else "La diferencia de errores no es estadísticamente significativa (p >= 0.05)"
        }
    except Exception as e:
        return {
            "statistic": None,
            "p_value": None,
            "is_significant": False,
            "interpretation": f"No fue posible computar el test de Wilcoxon: {str(e)}"
        }

def kolmogorov_smirnov_2sample(sample1: Any, sample2: Any) -> Dict[str, Any]:
    """
    Test Kolmogorov-Smirnov de 2 muestras para igualdad de distribuciones.
    Retorna métricas nullables si la muestra es insuficiente.
    """
    try:
        s1 = np.asarray(sample1, dtype=float)
        s2 = np.asarray(sample2, dtype=float)
        s1 = s1[np.isfinite(s1)]
        s2 = s2[np.isfinite(s2)]
    except Exception:
        return {"statistic": None, "p_value": None, "distributions_differ": False, "warning": "Datos no convertibles a numéricos finitos."}

    if len(s1) < 4 or len(s2) < 4:
        return {
            "statistic": None,
            "p_value": None,
            "distributions_differ": False,
            "warning": f"Tamaño de muestra insuficiente (n1={len(s1)}, n2={len(s2)}) para test KS confiable."
        }

    res = stats.ks_2samp(s1, s2)
    return {
        "statistic": round(float(res.statistic), 4),
        "p_value": float(res.pvalue),
        "distributions_differ": bool(res.pvalue < 0.05),
        "warning": None if len(s1) >= 20 and len(s2) >= 20 else "Muestra moderada: p-valor sujeto a dispersión."
    }

def compute_population_stability_index(
    reference: Any,
    current: Any,
    num_bins: int = 10,
    epsilon: float = 1e-4
) -> Tuple[Optional[float], Optional[str], Optional[str]]:
    """
    Calcula el Population Stability Index (PSI) para medir Data Drift.
    - Define los cuantiles/bins utilizando estrictamente la distribución de referencia.
    - Aplica los mismos bins al conjunto actual.
    - Maneja frecuencias cero con suavizado epsilon documentado.
    - Umbrales: PSI < 0.10: STABLE, 0.10 <= PSI < 0.25: WARNING, PSI >= 0.25: CRITICAL.
    Retorna: (psi_value, severity_status, warning_msg).
    """
    try:
        ref = np.asarray(reference, dtype=float)
        curr = np.asarray(current, dtype=float)
        ref = ref[np.isfinite(ref)]
        curr = curr[np.isfinite(curr)]
    except Exception:
        return None, None, "Error en tipos de datos de entrada para PSI."

    if len(ref) < 10 or len(curr) < 10:
        return None, None, f"Muestra insuficiente (ref={len(ref)}, curr={len(curr)}) para calcular PSI confiable (mínimo 10 requerido)."

    # Varianza nula en referencia
    if np.std(ref) == 0:
        if np.array_equal(ref, curr):
            return 0.0, "STABLE", "Distribución constante idéntica en ambas ventanas."
        else:
            return 1.0, "CRITICAL", "Referencia constante pero ventana actual presenta dispersión."

    try:
        # Bins basados en cuantiles de la referencia
        quantiles = np.linspace(0, 100, num_bins + 1)
        bins = np.percentile(ref, quantiles)
        bins = np.unique(bins)  # Evitar bordes duplicados si hay empates
        if len(bins) < 2:
            return None, None, "No se pudieron formar bins diferenciados en la referencia."

        # Extender bordes para cubrir rango completo
        bins[0] = -np.inf
        bins[-1] = np.inf

        # Frecuencias en referencia y actual
        ref_counts, _ = np.histogram(ref, bins=bins)
        curr_counts, _ = np.histogram(curr, bins=bins)

        # Proporciones con suavizado epsilon ante frecuencias cero
        ref_pct = (ref_counts + epsilon) / (len(ref) + epsilon * len(ref_counts))
        curr_pct = (curr_counts + epsilon) / (len(curr) + epsilon * len(curr_counts))

        psi_val = float(np.sum((curr_pct - ref_pct) * np.log(curr_pct / ref_pct)))
        psi_val = round(max(0.0, psi_val), 4)

        if psi_val < 0.10:
            severity = "STABLE"
        elif psi_val < 0.25:
            severity = "WARNING"
        else:
            severity = "CRITICAL"

        return psi_val, severity, None
    except Exception as e:
        return None, None, f"Error de cómputo en PSI: {str(e)}"

def compute_icu_saturation_auc_roc(
    y_true_binary: Any,
    y_score: Any
) -> Dict[str, Any]:
    """
    Calcula el Área bajo la Curva ROC (AUC-ROC) para eventos binarios de saturación hospitalaria / UCI (>90%).
    """
    try:
        yt = np.asarray(y_true_binary, dtype=int)
        ys = np.asarray(y_score, dtype=float)
        valid = np.isfinite(yt) & np.isfinite(ys)
        yt = yt[valid]
        ys = ys[valid]
        
        if len(np.unique(yt)) < 2:
            return {"auc_roc": None, "discrimination_quality": "No calculable (solo una clase presente)", "warning": "Requiere casos positivos y negativos."}
        
        auc = float(metrics.roc_auc_score(yt, ys))
        quality = "Excelente" if auc >= 0.90 else "Bueno" if auc >= 0.80 else "Aceptable" if auc >= 0.70 else "Pobre"
        return {"auc_roc": round(auc, 4), "discrimination_quality": quality, "warning": None}
    except Exception as e:
        return {"auc_roc": None, "discrimination_quality": "Error", "warning": str(e)}

def anderson_darling_k_sample(samples: List[Any]) -> Dict[str, Any]:
    """
    Test de Anderson-Darling para k muestras.
    """
    try:
        cleaned = [np.asarray(s, dtype=float)[np.isfinite(np.asarray(s, dtype=float))] for s in samples]
        if any(len(s) < 5 for s in cleaned):
            return {"statistic": None, "critical_values": None, "significance_level": None, "warning": "Muestras insuficientes."}
        res = stats.anderson_ksamp(cleaned)
        return {"statistic": round(float(res.statistic), 4), "critical_values": [round(float(v), 4) for v in res.critical_values], "significance_level": float(res.pvalue), "warning": None}
    except Exception as e:
        return {"statistic": None, "warning": str(e)}

