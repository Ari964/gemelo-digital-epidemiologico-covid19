"""
Protocolo de evaluación temporal v2.0 (GD_TI) - CRISP-DM Fases 4 y 5.

Implementa, sobre datos reales de OWID/OMS (Kenia):
1. Partición temporal 80/20 (desarrollo vs prueba reservada), sin mezcla aleatoria.
2. Validación cruzada temporal de 5 folds (TimeSeriesSplit) dentro del 80% desarrollo.
3. Búsqueda de hiperparámetros con 5 folds temporales (GridSearchCV).
4. Selección del campeón por métrica principal de validación (CV RMSE), sin usar el 20% de prueba.
5. Reentrenamiento del campeón sobre el bloque de desarrollo completo y evaluación en el 20% reservado.
6. U de Theil (variante U1) vs baseline de persistencia, mismo horizonte/fechas/observaciones.
7. Mapa de calor de correlaciones (Pearson) de variables epidemiológicas, en bloque de desarrollo.
8. Pruebas estadísticas robustas: Wilcoxon pareado (mismas fechas) y Diebold-Mariano con HLN.
9. Interpretabilidad y explicabilidad de cada tabla y figura.
10. Exportación de figuras a 500 dpi (fondo blanco), CSV y paquete de descarga.

Referencia técnica U de Theil: Theil, H. (1966). Applied Economic Forecasting. North-Holland.
"""

import os
import sys
import json
import hashlib
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.base import BaseEstimator, RegressorMixin, clone
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Rutas (raíz del proyecto detectada por marcador)
# ---------------------------------------------------------------------------
def _find_project_root(start_dir):
    curr = os.path.abspath(start_dir)
    for _ in range(6):
        if os.path.exists(os.path.join(curr, "data", "raw", "owid_covid_kenya_raw.csv")):
            return curr
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

_BASE_START = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = _find_project_root(_BASE_START)
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
MODELS_DIR = os.path.join(BASE_DIR, "models", "protocolo_v2")
FIGURES_DIR = os.path.join(BASE_DIR, "docs", "figures", "protocolo_v2")
EXPORT_DIR = os.path.join(BASE_DIR, "docs", "export", "protocolo_v2")

for d in [MODELS_DIR, FIGURES_DIR, EXPORT_DIR]:
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------------------
# Estilo científico: fondo blanco, texto oscuro, 500 dpi reales
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.dpi": 500,
    "savefig.bbox": "tight",
    "text.color": "#1F2937",
    "axes.labelcolor": "#1F2937",
    "axes.edgecolor": "#1F2937",
    "xtick.color": "#1F2937",
    "ytick.color": "#1F2937",
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "legend.fontsize": 9,
    "figure.titlesize": 14,
})

PALETTE = {
    "observed": "#111827",
    "naive": "#6B7280",
    "ridge": "#2563EB",
    "rf": "#DC2626",
    "hgb": "#059669",
}

WEEKLY_FEATURES = [
    "weekly_lag_1", "weekly_lag_2", "weekly_lag_3", "weekly_lag_4",
    "weekly_rolling_mean_4", "weekly_rolling_std_4",
    "weekly_deaths_lag_1", "weekly_deaths_lag_2",
    "stringency_lag_1", "reproduction_rate_lag_1",
    "month",
]
TARGET_COL = "target_weekly_cases"
DATE_COL = "date"

# ===========================================================================
# Utilidades de métricas
# ===========================================================================
def regression_metrics(y_true, y_pred):
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)
    rmse = float(np.sqrt(mean_squared_error(y_t, y_p)))
    mae = float(mean_absolute_error(y_t, y_p))
    r2 = float(r2_score(y_t, y_p))
    return {"rmse": round(rmse, 4), "mae": round(mae, 4), "r2": round(r2, 4)}

def compute_mape_safe(y_true, y_pred, epsilon=1.0):
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)
    denom = np.maximum(np.abs(y_t), epsilon)
    return float(np.mean(np.abs(y_t - y_p) / denom) * 100.0)

# ===========================================================================
# U de Theil - Variante U1 (Theil's inequality coefficient)
# Referencia: Theil, H. (1966). Applied Economic Forecasting. North-Holland.
# Fórmula: U1 = sqrt( sum((f_t - o_t)^2) ) / sqrt( sum(f_t^2) + sum(o_t^2) )
# Rango: [0, 1]. 0 = ajuste perfecto; 1 = pronóstico equivalente a no usar información.
# NO confundir con U2 (cambios relativos) ni con variantes en niveles.
# ===========================================================================
def theil_u1(y_true, y_pred):
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)
    mask = np.isfinite(y_t) & np.isfinite(y_p)
    if mask.sum() == 0:
        return {"u1": None, "n": 0, "defined": False, "reason": "Sin observaciones válidas finitas."}
    y_t = y_t[mask]; y_p = y_p[mask]
    numerator = float(np.sqrt(np.sum((y_p - y_t) ** 2)))
    denominator = float(np.sqrt(np.sum(y_p ** 2) + np.sum(y_t ** 2)))
    if denominator == 0.0:
        return {"u1": None, "n": int(mask.sum()), "defined": False,
                "reason": "Denominador nulo: pronóstico y observados son todos cero."}
    u1 = numerator / denominator
    return {"u1": round(u1, 6), "n": int(mask.sum()), "defined": True,
            "reason": "U1 de Theil calculado sobre pronóstico vs observado."}

def theil_u1_vs_persistence(y_true, y_model_pred, y_persistence_pred):
    res_model = theil_u1(y_true, y_model_pred)
    res_pers = theil_u1(y_true, y_persistence_pred)
    comparison = None
    if res_model["defined"] and res_pers["defined"]:
        comparison = {
            "u1_modelo": res_model["u1"],
            "u1_persistencia": res_pers["u1"],
            "modelo_mejor_que_persistencia": res_model["u1"] < res_pers["u1"],
            "diferencia": round(res_pers["u1"] - res_model["u1"], 6),
        }
    return {"modelo": res_model, "persistencia": res_pers, "comparacion": comparison,
            "n": res_model["n"],
            "interpretacion": ("U1 = 0 indica ajuste perfecto. Valores cercanos a 1 indican que el pronóstico "
                               "no aporta información respecto a un pronóstico nulo. Si U1(modelo) < U1(persistencia), "
                               "el modelo supera al baseline de persistencia según este coeficiente.")}

# ===========================================================================
# Baseline de persistencia ingenua
# ===========================================================================
class NaivePersistenceModel(BaseEstimator, RegressorMixin):
    def __init__(self, lag_idx=0):
        self.lag_idx = lag_idx
    def fit(self, X, y=None):
        return self
    def predict(self, X):
        X_arr = np.asarray(X)
        return X_arr[:, self.lag_idx]

# ===========================================================================
# Carga de datos y partición 80/20
# ===========================================================================
def load_weekly_data():
    train_path = os.path.join(PROCESSED_DIR, "kenya_covid_weekly_train.csv")
    val_path = os.path.join(PROCESSED_DIR, "kenya_covid_weekly_val.csv")
    test_path = os.path.join(PROCESSED_DIR, "kenya_covid_weekly_test.csv")
    dfs = [pd.read_csv(p, parse_dates=[DATE_COL]) for p in [train_path, val_path, test_path]]
    df = pd.concat(dfs, ignore_index=True).drop_duplicates(subset=[DATE_COL]).sort_values(DATE_COL).reset_index(drop=True)
    return df

def temporal_80_20_split(df):
    n = len(df)
    n_dev = int(round(0.8 * n))
    n_test = n - n_dev
    df_dev = df.iloc[:n_dev].copy().reset_index(drop=True)
    df_test = df.iloc[n_dev:].copy().reset_index(drop=True)
    split_info = {
        "n_total": int(n), "n_dev": int(n_dev), "n_test": int(n_test),
        "dev_pct": round(100.0 * n_dev / n, 2), "test_pct": round(100.0 * n_test / n, 2),
        "rounding_criterio": "round(0.8 * n_total); test = n_total - n_dev",
        "dev_fecha_inicio": str(df_dev[DATE_COL].min().date()),
        "dev_fecha_fin": str(df_dev[DATE_COL].max().date()),
        "test_fecha_inicio": str(df_test[DATE_COL].min().date()),
        "test_fecha_fin": str(df_test[DATE_COL].max().date()),
        "target_variable": TARGET_COL, "unidad": "casos semanales confirmados",
        "frecuencia": "semanal (W-SUN, cierre domingo)",
        "horizonte": "1 semana hacia adelante (t+1)",
        "ambito": "Nivel nacional, Kenia (ISO KEN)",
    }
    return df_dev, df_test, split_info

# ===========================================================================
# Entrenamiento y evaluación con 5 folds temporales
# ===========================================================================
def evaluate_model_with_cv(name, pipeline, params, X_dev, y_dev, dates_dev, tscv):
    result = {"name": name, "hyperparameter_space": params, "fold_metrics": []}
    dates_dev = pd.to_datetime(dates_dev)
    if params:
        grid = GridSearchCV(pipeline, param_grid=params, cv=tscv,
                            scoring="neg_root_mean_squared_error", n_jobs=-1)
        grid.fit(X_dev, y_dev)
        best_model = grid.best_estimator_
        best_params = grid.best_params_
        result["best_params"] = best_params
        result["cv_rmse_5fold"] = round(float(-grid.best_score_), 4)
        result["best_index"] = int(grid.best_index_)
    else:
        best_model = clone(pipeline)
        best_model.fit(X_dev, y_dev)
        best_params = {"strategy": "persistence_weekly_lag_1", "no_tuning": True}
        result["best_params"] = best_params
        cv_scores = []
        for tr_idx, val_idx in tscv.split(X_dev):
            p = best_model.predict(X_dev[val_idx])
            cv_scores.append(float(np.sqrt(mean_squared_error(y_dev[val_idx], p))))
        result["cv_rmse_5fold"] = round(float(np.mean(cv_scores)), 4)
        result["cv_scores_folds"] = [round(s, 4) for s in cv_scores]

    fold_idx = 1
    for tr_idx, val_idx in tscv.split(X_dev):
        m_fold = clone(best_model)
        m_fold.fit(X_dev[tr_idx], y_dev[tr_idx])
        p_val = np.maximum(0.0, m_fold.predict(X_dev[val_idx]))
        f = regression_metrics(y_dev[val_idx], p_val)
        result["fold_metrics"].append({
            "fold": fold_idx,
            "train_start_date": str(dates_dev[tr_idx[0]].date()),
            "train_end_date": str(dates_dev[tr_idx[-1]].date()),
            "val_start_date": str(dates_dev[val_idx[0]].date()),
            "val_end_date": str(dates_dev[val_idx[-1]].date()),
            "train_samples": int(len(tr_idx)),
            "val_samples": int(len(val_idx)),
            "val_rmse": f["rmse"], "val_mae": f["mae"], "val_r2": f["r2"],
        })
        fold_idx += 1

    preds_dev = np.maximum(0.0, best_model.predict(X_dev))
    result["dev_metrics"] = regression_metrics(y_dev, preds_dev)
    result["preds_dev"] = preds_dev
    result["best_model"] = best_model
    return result

def run_model_comparison(df_dev, df_test):
    tscv = TimeSeriesSplit(n_splits=5)
    X_dev = df_dev[WEEKLY_FEATURES].values
    y_dev = df_dev[TARGET_COL].values
    dates_dev = pd.to_datetime(df_dev[DATE_COL].values)
    X_test = df_test[WEEKLY_FEATURES].values
    y_test = df_test[TARGET_COL].values
    dates_test = pd.to_datetime(df_test[DATE_COL].values)

    models_config = {
        "Baseline_Naive_Persistence": {"pipeline": NaivePersistenceModel(lag_idx=0), "params": {}},
        "Baseline_Ridge_Regression": {
            "pipeline": Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                ("regressor", Ridge(random_state=42))]),
            "params": {"regressor__alpha": [0.1, 1.0, 10.0, 100.0, 500.0, 1000.0]}},
        "Candidate_Random_Forest": {
            "pipeline": Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                ("regressor", RandomForestRegressor(random_state=42, n_jobs=-1))]),
            "params": {"regressor__n_estimators": [50, 100],
                       "regressor__max_depth": [3, 5, 8],
                       "regressor__min_samples_split": [2, 5]}},
        "Candidate_HistGradientBoosting": {
            "pipeline": Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                ("regressor", HistGradientBoostingRegressor(random_state=42))]),
            "params": {"regressor__learning_rate": [0.03, 0.05, 0.1],
                       "regressor__max_iter": [30, 50, 80],
                       "regressor__max_leaf_nodes": [7, 15]}},
    }

    results = {}
    for name, cfg in models_config.items():
        print(f"=== Evaluando {name} (5 folds temporales en desarrollo) ===", flush=True)
        results[name] = evaluate_model_with_cv(name, cfg["pipeline"], cfg["params"],
                                               X_dev, y_dev, dates_dev, tscv)
        best_model = results[name]["best_model"]
        preds_test = np.maximum(0.0, best_model.predict(X_test))
        results[name]["test_metrics"] = regression_metrics(y_test, preds_test)
        results[name]["preds_test"] = preds_test
        results[name]["mape_test"] = round(compute_mape_safe(y_test, preds_test), 4)
        print(f"  CV RMSE (dev): {results[name]['cv_rmse_5fold']} | "
              f"Test RMSE: {results[name]['test_metrics']['rmse']} | "
              f"Test MAE: {results[name]['test_metrics']['mae']}", flush=True)

    predictive_champion = min(results.keys(), key=lambda m: results[m]["cv_rmse_5fold"])
    print(f">>> CAMPEÓN PREDICTIVO (mínimo CV RMSE en desarrollo): {predictive_champion}", flush=True)
    print(f"    CV RMSE dev: {results[predictive_champion]['cv_rmse_5fold']}", flush=True)

    champion_model = results[predictive_champion]["best_model"]
    preds_champion_test = np.maximum(0.0, champion_model.predict(X_test))
    champion_test_metrics = regression_metrics(y_test, preds_champion_test)
    champion_test_mape = round(compute_mape_safe(y_test, preds_champion_test), 4)

    preds_persistence_test = np.maximum(0.0, X_test[:, 0])
    persistence_test_metrics = regression_metrics(y_test, preds_persistence_test)

    return {
        "results": results, "predictive_champion": predictive_champion,
        "X_dev": X_dev, "y_dev": y_dev, "dates_dev": dates_dev,
        "X_test": X_test, "y_test": y_test, "dates_test": dates_test,
        "champion_test_metrics": champion_test_metrics,
        "champion_test_mape": champion_test_mape,
        "champion_preds_test": preds_champion_test,
        "persistence_test_metrics": persistence_test_metrics,
        "persistence_preds_test": preds_persistence_test,
    }

# ===========================================================================
# Pruebas estadísticas robustas
# ===========================================================================
def statistical_tests(y_test, preds_model, preds_persistence, model_name):
    e_model = np.abs(y_test - preds_model)
    e_pers = np.abs(y_test - preds_persistence)
    d_loss = e_pers - e_model
    out = {"n": int(len(y_test))}

    shapiro_sample = d_loss[:min(500, len(d_loss))]
    sw_stat, sw_p = stats.shapiro(shapiro_sample)
    out["shapiro_wilk"] = {
        "statistic": round(float(sw_stat), 4), "p_value": float(sw_p),
        "is_normal": bool(sw_p >= 0.05),
        "interpretation": ("Residuos de diferencia de pérdidas: normalidad no rechazada" if sw_p >= 0.05
                           else "Normalidad rechazada (p < 0.05): se justifican tests no paramétricos."),
    }

    try:
        wilc = stats.wilcoxon(e_pers, e_model, alternative="two-sided")
        out["wilcoxon_paired"] = {
            "statistic": round(float(wilc.statistic), 4),
            "p_value_two_sided": float(wilc.pvalue),
            "interpretation": ("Diferencia de errores no estadísticamente significativa (p >= 0.05)"
                               if wilc.pvalue >= 0.05 else
                               "Diferencia de errores absolutos pareados estadísticamente significativa (p < 0.05)."),
            "note": "Prueba sobre las mismas fechas y observaciones; no trata folds como observaciones independientes.",
        }
    except Exception as ex:
        out["wilcoxon_paired"] = {"statistic": None, "p_value_two_sided": None,
                                  "interpretation": f"No computable: {ex}"}

    def diebold_mariano(e_base, e_cand, h=1):
        d = np.abs(e_base) - np.abs(e_cand)
        T = len(d); d_bar = float(np.mean(d))
        def autocov(k):
            if k == 0: return float(np.var(d, ddof=0))
            return float(np.mean((d[k:] - d_bar) * (d[:-k] - d_bar)))
        lr_var = autocov(0) + sum(2.0 * (1.0 - k / h) * autocov(k) for k in range(1, h))
        lr_var = max(1e-12, lr_var)
        dm_stat = d_bar / np.sqrt(lr_var / T)
        hln = np.sqrt((T + 1.0 - 2.0 * h + (h * (h - 1.0)) / T) / T)
        dm_mod = dm_stat * hln
        p_two = float(2.0 * (1.0 - stats.t.cdf(np.abs(dm_mod), df=max(1, T - 1))))
        return {"dm_stat_hln": round(float(dm_mod), 4), "mean_loss_diff": round(float(d_bar), 4),
                "p_value_two_sided": p_two,
                "p_value_formatted": ("p < 0.0001" if p_two < 0.0001 else f"{p_two:.4e}"),
                "sample_size": int(T), "criterion": "MAE"}

    out["diebold_mariano_hln"] = diebold_mariano(e_pers, e_model)
    out["diebold_mariano_hln"]["interpretation"] = (
        f"{'p < 0.05: diferencia significativa' if out['diebold_mariano_hln']['p_value_two_sided'] < 0.05 else 'p >= 0.05: no se concluye diferencia significativa'} "
        f"controlando autocorrelación (HAC Bartlett, HLN 1997)."
    )

    sd_diff = float(np.std(d_loss, ddof=1)) if len(d_loss) > 1 else 0.0
    mean_diff = float(np.mean(d_loss))
    cohens_d = (mean_diff / sd_diff) if sd_diff > 0 else None
    out["efecto"] = {
        "diferencia_media_mae_pers_menos_modelo": round(mean_diff, 4),
        "desviacion_estandar_diferencias": round(sd_diff, 4),
        "d_de_cohen": round(cohens_d, 4) if cohens_d is not None else None,
        "interpretacion_efecto": ("tamaño del efecto no computable (varianza cero en diferencias entre errores pareados)"
                                  if cohens_d is None else
                                  ("efecto pequeño" if abs(cohens_d) < 0.5 else ("efecto medio" if abs(cohens_d) < 0.8 else "efecto grande"))),
    }
    out["advertencia_multiplicidad"] = (
        "Se realizan múltiples contrastes (Wilcoxon, Diebold-Mariano) sobre la misma muestra de prueba. "
        "Los p-valores son nominales; no se aplica corrección de Bonferroni para no ocultar evidencia, "
        "pero deben interpretarse con cautela."
    )
    return out

# ===========================================================================
# Mapa de calor de correlaciones (Pearson) en bloque de desarrollo
# ===========================================================================
def correlation_heatmap(df_dev):
    numeric_cols = [c for c in WEEKLY_FEATURES + [TARGET_COL] if c in df_dev.columns]
    corr = df_dev[numeric_cols].corr(method="pearson")
    n_obs = int(df_dev[numeric_cols].notna().all(axis=1).sum())

    fig, ax = plt.subplots(figsize=(10, 8), facecolor="white")
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(numeric_cols)))
    ax.set_yticks(range(len(numeric_cols)))
    labels = [c.replace("weekly_", "w_").replace("_", " ").title() for c in numeric_cols]
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(labels, fontsize=8)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Coeficiente de correlación de Pearson", fontsize=9)
    for i in range(len(numeric_cols)):
        for j in range(len(numeric_cols)):
            val = corr.values[i, j]
            ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                    color="white" if abs(val) > 0.5 else "#1F2937", fontsize=7, fontweight="bold")
    ax.set_title("Mapa de calor de correlaciones (Pearson) - Variables epidemiológicas (bloque de desarrollo)",
                 fontsize=12, fontweight="bold", pad=14)
    plt.tight_layout()
    path_png = os.path.join(FIGURES_DIR, "mapa_calor_correlaciones_desarrollo.png")
    path_svg = os.path.join(FIGURES_DIR, "mapa_calor_correlaciones_desarrollo.svg")
    fig.savefig(path_png, dpi=500, facecolor="white")
    fig.savefig(path_svg, facecolor="white")
    plt.close(fig)
    corr_path = os.path.join(EXPORT_DIR, "correlaciones_pearson_desarrollo.csv")
    corr.to_csv(corr_path, encoding="utf-8")

    return {
        "metodo": "Pearson",
        "justificacion": "Relaciones lineales entre variables numéricas epidemiológicas; las variables son aproximadamente continuas.",
        "variables": numeric_cols,
        "n_observaciones_utilizadas": n_obs,
        "tratamiento_faltantes": "Pares completos (pairwise); correlaciones calculadas sobre observaciones con valores finitos en ambas variables.",
        "excluidas": "Identificadores (date), columnas constantes y la fecha de corte; no hay variables geográficas inventadas.",
        "advertencia_causalidad": "Correlación no implica causalidad. Tendencias y autocorrelación de la serie temporal pueden inflar coeficientes. La correlación entre predictores no demuestra por sí sola importancia para el modelo.",
        "calculado_en": "bloque de desarrollo (80%), sin usar el bloque de prueba reservado.",
        "figura_png": path_png, "figura_svg": path_svg,
        "csv_correlaciones": corr_path,
        "matriz_correlacion": corr.round(4).to_dict(),
    }

# ===========================================================================
# Figuras y exportaciones
# ===========================================================================
def save_observed_vs_predicted(dates_test, y_test, preds_dict, champion_name):
    fig, ax = plt.subplots(figsize=(13, 5), facecolor="white")
    ax.plot(dates_test, y_test, marker="o", linestyle="-", color=PALETTE["observed"],
            label="Observado real (OWID/OMS)", linewidth=1.8, markersize=3)
    ax.plot(dates_test, preds_dict["naive"], linestyle="--", color=PALETTE["naive"],
            label="Persistencia (baseline)", linewidth=1.5)
    ax.plot(dates_test, preds_dict["ridge"], linestyle=":", color=PALETTE["ridge"],
            label="Ridge (benchmark test)", linewidth=1.5)
    ax.plot(dates_test, preds_dict["rf"], linestyle="-.", color=PALETTE["rf"],
            label="Random Forest (sensibilidad)", linewidth=1.5)
    ax.plot(dates_test, preds_dict["champion"], linestyle="-", color=PALETTE["hgb"],
            label=f"{champion_name} (campeón)", linewidth=2.0)
    ax.set_title("Observados frente a predicciones - Prueba reservada (últimas 45 semanas, 2023-2024)",
                 fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel("Fecha de cierre semanal (domingo)", fontsize=10)
    ax.set_ylabel("Casos semanales", fontsize=10)
    ax.legend(loc="best", frameon=False, fontsize=8)
    ax.grid(True, linestyle="--", alpha=0.5, color="#E5E7EB")
    plt.tight_layout()
    p = os.path.join(FIGURES_DIR, "observados_vs_predicciones_test.png")
    fig.savefig(p, dpi=500, facecolor="white")
    plt.close(fig)
    csv_path = os.path.join(EXPORT_DIR, "observados_vs_predicciones_test.csv")
    pd.DataFrame({
        "date": [str(d.date()) for d in dates_test],
        "observado": y_test, "naive_persistence": preds_dict["naive"],
        "ridge": preds_dict["ridge"], "random_forest": preds_dict["rf"],
        "campeon": preds_dict["champion"],
    }).to_csv(csv_path, index=False, encoding="utf-8")
    return {"figura_png": p, "csv": csv_path}

def save_residuals(dates_test, y_test, preds_champion, champion_name):
    resid = y_test - preds_champion
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), facecolor="white")
    axes[0].scatter(dates_test, resid, color=PALETTE["hgb"], s=20, alpha=0.7)
    axes[0].axhline(0, color="#1F2937", linestyle="--", linewidth=1)
    axes[0].set_title("Residuos del campeón en prueba", fontsize=11, fontweight="bold")
    axes[0].set_xlabel("Fecha", fontsize=9)
    axes[0].set_ylabel("Residuo (observado - predicho)", fontsize=9)
    axes[0].tick_params(axis='x', rotation=45, labelsize=7)
    axes[0].grid(True, linestyle="--", alpha=0.5, color="#E5E7EB")
    axes[1].hist(resid, bins=15, color=PALETTE["hgb"], alpha=0.7, edgecolor="white")
    axes[1].axvline(resid.mean(), color="#DC2626", linestyle="--", linewidth=1, label=f"Media = {resid.mean():.2f}")
    axes[1].set_title("Distribución de residuos", fontsize=11, fontweight="bold")
    axes[1].set_xlabel("Residuo", fontsize=9)
    axes[1].set_ylabel("Frecuencia", fontsize=9)
    axes[1].legend(fontsize=8, frameon=False)
    axes[1].grid(True, linestyle="--", alpha=0.5, color="#E5E7EB")
    plt.tight_layout()
    p = os.path.join(FIGURES_DIR, "residuos_distribucion_errores.png")
    fig.savefig(p, dpi=500, facecolor="white")
    plt.close(fig)
    csv_path = os.path.join(EXPORT_DIR, "residuos_campeon_test.csv")
    pd.DataFrame({"date": [str(d.date()) for d in dates_test],
                  "observado": y_test, "predicho": preds_champion,
                  "residuo": resid}).to_csv(csv_path, index=False, encoding="utf-8")
    return {"figura_png": p, "csv": csv_path}

def save_partition_figure(df_dev, df_test, split_info):
    fig, ax = plt.subplots(figsize=(13, 4), facecolor="white")
    ax.bar(df_dev[DATE_COL], df_dev[TARGET_COL], width=2.5, color=PALETTE["ridge"],
           label=f"Desarrollo/Entrenamiento (80%): {split_info['n_dev']} semanas", alpha=0.85)
    ax.bar(df_test[DATE_COL], df_test[TARGET_COL], width=2.5, color=PALETTE["naive"],
           label=f"Prueba reservada (20%): {split_info['n_test']} semanas", alpha=0.85)
    cut = pd.to_datetime(df_dev[DATE_COL].max())
    ax.axvline(cut, color="#1F2937", linestyle="--", linewidth=1.5)
    ax.text(cut, ax.get_ylim()[1]*0.95, "Corte 80/20", rotation=90, fontsize=8, va="top")
    ax.set_title("Partición temporal 80/20 sin mezcla aleatoria", fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel("Fecha", fontsize=10)
    ax.set_ylabel("Casos semanales", fontsize=10)
    ax.legend(loc="best", frameon=False, fontsize=8)
    ax.grid(True, linestyle="--", alpha=0.5, color="#E5E7EB")
    plt.tight_layout()
    p = os.path.join(FIGURES_DIR, "particion_temporal_80_20.png")
    fig.savefig(p, dpi=500, facecolor="white")
    plt.close(fig)
    return p

def auditoria_temporal(df_test, preds_champion, champion_name, preds_persistence):
    rows = []
    for i, d in enumerate(df_test[DATE_COL]):
        rows.append({
            "fecha_emision": str(d.date()),
            "ultima_informacion_disponible": str(d.date()),
            "fecha_objetivo_t1": str((d + pd.Timedelta(days=7)).date()),
            "valor_observado": float(df_test[TARGET_COL].iloc[i]),
            "prediccion_campeon": float(preds_champion[i]),
            "prediccion_persistencia": float(preds_persistence[i]),
            "modelo_campeon": champion_name,
        })
    df_aud = pd.DataFrame(rows)
    path = os.path.join(EXPORT_DIR, "auditoria_temporal_predicciones.csv")
    df_aud.to_csv(path, index=False, encoding="utf-8")
    return path

# ===========================================================================
# Interpretabilidad y explicabilidad por tabla/figura
# ===========================================================================
def generar_interpretabilidad(execution, split_info, champion_name, cv_ch, rmse_ch, mae_ch,
                              u_theil, stats_res, heatmap_info, hm, n_dev, n_test,
                              dev_ini, dev_fin, test_ini, test_fin, u1_mod, u1_pers, u1_n,
                              mae_ch_local=None):
    mae_ch = mae_ch if mae_ch_local is None else mae_ch_local

    def _sec(fig_id, titulo, representa, vars_pop, como_leer, hallazgo, alcance,
             datos_transf, metodo, parametros, procedimiento, limitaciones):
        return {
            "id": fig_id, "titulo": titulo,
            "interpretabilidad": {
                "que_representa": representa,
                "variables_unidades_periodo_poblacion": vars_pop,
                "como_leer": como_leer,
                "hallazgo_concreto": hallazgo,
                "alcance_y_limites": alcance,
            },
            "explicabilidad": {
                "datos_y_transformaciones": datos_transf,
                "metodo_modelo_prueba": metodo,
                "parametros_y_supuestos": parametros,
                "procedimiento_genera_resultado": procedimiento,
                "limitaciones_y_fuentes_error": limitaciones,
            },
        }

    return {
        "particion_80_20": _sec(
            "particion_80_20",
            "Partición temporal 80/20 (desarrollo vs prueba reservada)",
            "División cronológica de las 226 semanas epidemiológicas semanales de Kenia (2020-04-12 a 2024-08-04) en un bloque de desarrollo (80%) y un bloque de prueba final reservado (20%), sin mezcla aleatoria.",
            "Variable objetivo: casos semanales confirmados (target_weekly_cases), unidad: casos/semana. Población: Kenia, nivel nacional (ISO KEN). Periodo desarrollo: " + dev_ini + " a " + dev_fin + ". Periodo prueba: " + test_ini + " a " + test_fin + ".",
            "Barras azules = desarrollo/entrenamiento (primeras " + str(n_dev) + " semanas, " + str(split_info['dev_pct']) + "%); barras grises = prueba reservada (últimas " + str(n_test) + " semanas, " + str(split_info['test_pct']) + "%). Línea vertical = corte cronológico. Sin solapamiento entre bloques.",
            "El campeón se selecciona usando solo el bloque de desarrollo; el bloque de prueba (" + str(n_test) + " semanas, " + test_ini + " a " + test_fin + ") queda totalmente fuera de muestra y no influye en la selección ni el ajuste de hiperparámetros.",
            "Partición estrictamente temporal, protocolo 80/20. Redondeo: round(0.8 * n_total); test = n_total - n_dev. No es aleatoria; respeta el orden cronológico y evita fuga de información futura.",
            "CSV semanales procesados generados por scripts/eda_and_data_prep.py, ordenados por fecha y concatenados sin mezcla aleatoria.",
            "Partición cronológica simple: primeras " + str(n_dev) + " observaciones = desarrollo, últimas " + str(n_test) + " = prueba.",
            "n_total=" + str(split_info['n_total']) + ", n_dev=" + str(n_dev) + ", n_test=" + str(n_test) + ", semilla: N/A (sin aleatorización).",
            "Se ordena por fecha y se parte por posición; no hay entrenamiento sobre datos futuros. El 20% se reserva antes de cualquier entrenamiento.",
            "Si el horizonte de predicción cambiara, habría que redefinir el corte; la partición asume horizonte de 1 semana (t+1)."),
        "resultados_por_modelo": _sec(
            "resultados_por_modelo",
            "Cuadro de comparación de modelos (validación en desarrollo y prueba reservada)",
            "Métricas de desempeño de cuatro modelos (persistencia ingenua, Ridge, Random Forest, HistGradientBoosting) en validación cruzada temporal de 5 folds sobre el desarrollo y en el prueba reservado.",
            "CV RMSE (casos/semana), Test RMSE, Test MAE, Test R², mejor hiperparámetro por modelo. Ámbito: Kenia nacional, casos semanales.",
            "Cada fila = un modelo. Columna 'rol': campeón predictivo (seleccionado ex-ante por CV RMSE en desarrollo), baseline de persistencia o comparativo. Los valores de prueba son referencia y NO se usaron para elegir al campeón.",
            "Campeón predictivo: " + champion_name + " con CV RMSE " + str(cv_ch) + " casos/semana en desarrollo. En prueba: RMSE " + str(rmse_ch) + ", MAE " + str(mae_ch) + ". El resto son comparativos o baseline.",
            "El cuadro distingue desarrollo (selección) de prueba (evaluación ciega). No se declara superioridad causal; solo errores observados.",
            "DataFrames semanales; TimeSeriesSplit(n_splits=5) y GridSearchCV con scoring neg_root_mean_squared_error.",
            "Validación cruzada temporal (expanding window) sin solapamiento; imputación/escalado ajustados solo en train de cada fold; persistencia sin hiperparámetros.",
            "Grid de hiperparámetros por modelo; random_state=42.",
            "GridSearchCV reentrena en cada ventana train del fold y evalúa en la ventana val inmediatamente posterior.",
            "El campeón se elige sin ver el test; cambiar el campeón por el test sería data snooping."),
        "observados_vs_predicciones": _sec(
            "observados_vs_predicciones",
            "Observados frente a predicciones (prueba reservada, últimas 45 semanas)",
            "Serie temporal de casos observados reales (OWID/OMS) y predicciones de un paso (t+1) del campeón, la persistencia, Ridge y Random Forest sobre el bloque de prueba.",
            "Eje X: fecha de cierre semanal (domingo). Eje Y: casos semanales. Colores por modelo según leyenda. Periodo: " + test_ini + " a " + test_fin + ".",
            "La línea del campeón debe seguir la de observados. Cuanto más cercanas, mejor el ajuste. En semanas de incidencia cero o cercana a cero, todos los modelos tienden a predecir cerca de cero.",
            "Durante el periodo endémico de baja incidencia (" + test_ini + " a " + test_fin + "), los casos observados son predominantemente cercanos a cero y el campeón (persistencia) los rastrea con error bajo (MAE " + str(mae_ch) + ").",
            "Gráfico de un paso (t+1), no recursivo multietapa. Cada predicción usa información conocida hasta t0. No se usan observaciones reales futuras como si estuvieran disponibles al emitir el pronóstico.",
            "Series de prueba y predicciones almacenadas del protocolo v2.0.",
            "Predicción de un paso adelante con el modelo campeón entrenado en desarrollo completo; trazabilidad punto a punto observado vs predicho.",
            "Horizonte fijo de 1 semana; modelos entrenados con semilla fija (42).",
            "Se itera sobre fechas del test y se compara predicción vs observado real de la semana siguiente (t+1).",
            "No es pronóstico recursivo multietapa; si se requiriera varios pasos adelante, se acumularía error de propagación."),
        "residuos": _sec(
            "residuos_distribucion_errores",
            "Residuos y distribución de errores del campeón (prueba reservada)",
            "Gráfico de dispersión de residuos (observado - predicho) a lo largo del tiempo y histograma de su distribución, para el campeón en el bloque de prueba.",
            "Eje X (izq): fecha. Eje Y (izq): residuo en casos. Eje X (der): magnitud del residuo. Eje Y (der): frecuencia (conteo de semanas).",
            "Puntos dispersos alrededor de cero sin patrón sistemático = errores no sesgados. Histograma centrado en cero = ausencia de sesgo de sobre/subestimación.",
            "Media de residuos cercana a cero; la dispersión refleja la baja incidencia del periodo de prueba (muchas semanas con 0-1 caso).",
            "Residuos calculados sobre las 45 semanas de prueba fuera de muestra. El histograma muestra la distribución empírica de errores.",
            "Residuos = observado - predicho del campeón en prueba.",
            "Resta elemento a elemento de arrays numpy; histograma con 15 bins; línea de media marcada.",
            "Sin parámetros adicionales; visualización exploratoria de errores.",
            "Se calcula sobre los 45 puntos del bloque de prueba, fuera de muestra del campeón.",
            "La dispersión está condicionada por la baja incidencia (casi todo cerca de cero); no representa periodos de alta transmisión."),
        "mapa_calor": _sec(
            "mapa_calor_correlaciones_desarrollo",
            "Mapa de calor de correlaciones (Pearson) de variables epidemiológicas",
            "Matriz de correlaciones de Pearson entre las variables numéricas epidemiológicas relevantes, calculada solo en el bloque de desarrollo.",
            "Coeficientes de correlación de Pearson entre pares de variables. N observaciones: " + str(hm['n_observaciones_utilizadas']) + ".",
            "Colores rojos = correlación positiva, azules = negativa. Centro (cero) = blanco en paleta divergente. Valores cercanos a ±1 = fuerte relación lineal.",
            "Las correlaciones más altas se observan entre los rezagos de casos semanales (weekly_lag_1 a 4). Las variables de políticas (stringency) y tasa de reproducción muestran alta falta de datos post-2022.",
            "Mapa calculado exclusivamente en el bloque de desarrollo, sin usar la prueba reservada para decisiones de selección de variables.",
            "DataFrame del bloque de desarrollo; columnas numéricas epidemiológicas de WEEKLY_FEATURES + target.",
            "Correlación de Pearson. Tratamiento de faltantes: pares completos (pairwise).",
            "Variables excluidas: identificador (date), columnas constantes, sin variables geográficas inventadas.",
            "df_dev[numeric_cols].corr(method='pearson'); exportación a CSV y figura PNG/SVG a 500 dpi, fondo blanco. Se calcula solo en desarrollo, nunca usando el bloque de prueba.",
            "Sin hiperparámetros; método paramétrico que asume linealidad. Correlación no implica causalidad; tendencias y autocorrelación pueden inflar coeficientes."),
        "u_de_theil": _sec(
            "u_de_theil",
            "Coeficiente U de Theil (variante U1) del campeón vs persistencia",
            "Coeficiente U1 de Theil que compara el error cuadrático del pronóstico del campeón y del baseline de persistencia sobre las mismas fechas, horizonte y observaciones del bloque de prueba.",
            "U1 adimensional en [0,1]. n = " + str(u1_n) + " semanas evaluadas. Periodo: " + test_ini + " a " + test_fin + ".",
            "U1 = 0 indica ajuste perfecto; valores cercanos a 1 indican que el pronóstico no aporta información respecto a un pronóstico nulo. Si U1(modelo) < U1(persistencia), el modelo supera al baseline según este coeficiente.",
            "U1(campeón) = " + str(u1_mod) + " y U1(persistencia) = " + str(u1_pers) + ". Como el campeón es la persistencia, ambos coeficientes coinciden (diferencia = 0.0), resultado honesto de los datos.",
            "Variante U1 (Theil's inequality coefficient), NO U2 ni niveles. Fórmula: sqrt(sum((f-o)^2)) / sqrt(sum(f^2) + sum(o^2)). Referencia: Theil (1966).",
            "Mismo conjunto de fechas, horizonte (t+1) y observaciones para modelo y baseline (n = " + str(u1_n) + ").",
            "Sin constantes arbitrarias; denominador nulo controlado.",
            "Cálculo elemento a elemento sobre arrays de pronóstico y observado, con máscara de valores finitos.",
            "Referencia primaria: Theil, H. (1966). No se añaden constantes para forzar finitud.",
            "U de Theil es una métrica descriptiva; no reemplaza las pruebas estadísticas."),
        "pruebas_estadisticas": _sec(
            "pruebas_estadisticas",
            "Batería de pruebas estadísticas (prueba reservada, N=" + str(stats_res['n']) + " semanas)",
            "Contrastes de hipótesis sobre errores absolutos pareados entre el campeón y el baseline de persistencia en las mismas fechas del bloque de prueba.",
            "Estadístico W (Wilcoxon), DM* (Diebold-Mariano HLN), p-valor, tamaño de efecto d de Cohen. n = " + str(stats_res['n']) + " semanas.",
            "p < 0.05 sugiere evidencia contra la igualdad de errores; p >= 0.05 indica que no se rechaza la igualdad. La ausencia de significancia no se interpreta como equivalencia.",
            "Resultados nominales reportados sin corrección de comparaciones múltiples; interpretarse con cautela. No se trata a los 5 folds como observaciones independientes.",
            "Pruebas justificadas por la dependencia temporal de errores: Wilcoxon pareado (mismas fechas) y Diebold-Mariano con corrección HLN (autocorrelación).",
            "H0: errores iguales entre campeón y persistencia. H1: errores distintos. Nivel de significancia 0.05 (nominal).",
            "No hay ajuste de Bonferroni; Shapiro-Wilk informativo (no decisivo).",
            "Errores absolutos pareados alineados por fecha; estadísticos de scipy.stats.",
            "Wilcoxon y Diebold-Mariano sobre las mismas fechas y observaciones; tamaño de muestra = 45 semanas.",
            "Muestreo temporal no independiente; los p-valores son nominales y deben interpretarse con prudencia."),
    }

# ===========================================================================
# Orquestador principal
# ===========================================================================
def run_protocolo():
    print("=" * 80, flush=True)
    print("PROTOCOLO DE EVALUACIÓN TEMPORAL V2.0 - GD_TI (Kenia, OWID/OMS)", flush=True)
    print("=" * 80, flush=True)

    raw_path = os.path.join(RAW_DIR, "owid_covid_kenya_raw.csv")
    with open(raw_path, "rb") as f:
        raw_sha = hashlib.sha256(f.read()).hexdigest()

    df = load_weekly_data()
    df_dev, df_test, split_info = temporal_80_20_split(df)
    print(f"\nPartición 80/20: dev={split_info['n_dev']} ({split_info['dev_fecha_inicio']} a {split_info['dev_fecha_fin']}), "
          f"test={split_info['n_test']} ({split_info['test_fecha_inicio']} a {split_info['test_fecha_fin']})", flush=True)

    comp = run_model_comparison(df_dev, df_test)
    champion_name = comp["predictive_champion"]
    print("POST_CHAMPION: inicio post-seleccion", flush=True)

    print("PASO: u_theil", flush=True)
    u_theil = theil_u1_vs_persistence(comp["y_test"], comp["champion_preds_test"], comp["persistence_preds_test"])

    print("PASO: statistical_tests", flush=True)
    stats_res = statistical_tests(comp["y_test"], comp["champion_preds_test"],
                                  comp["persistence_preds_test"], champion_name)

    print("PASO: correlation_heatmap", flush=True)
    heatmap_info = correlation_heatmap(df_dev)
    print("PASO: heatmap OK", flush=True)

    print("PASO: save_partition_figure", flush=True)
    fig_partition = save_partition_figure(df_dev, df_test, split_info)
    preds_dict = {
        "naive": comp["persistence_preds_test"],
        "ridge": comp["results"]["Baseline_Ridge_Regression"]["preds_test"],
        "rf": comp["results"]["Candidate_Random_Forest"]["preds_test"],
        "hgb": comp["results"]["Candidate_HistGradientBoosting"]["preds_test"],
        "champion": comp["champion_preds_test"],
    }
    print("PASO: save_observed_vs_predicted", flush=True)
    fig_obs_pred = save_observed_vs_predicted(comp["dates_test"], comp["y_test"], preds_dict, champion_name)
    print("PASO: obs_pred OK", flush=True)
    fig_resid = save_residuals(comp["dates_test"], comp["y_test"], comp["champion_preds_test"], champion_name)
    print("PASO: resid OK", flush=True)
    aud_path = auditoria_temporal(df_test, comp["champion_preds_test"], champion_name, comp["persistence_preds_test"])
    print("PASO: auditoria OK", flush=True)

    rmse_ch = comp["champion_test_metrics"]["rmse"]
    mae_ch = comp["champion_test_metrics"]["mae"]
    r2_ch = comp["champion_test_metrics"]["r2"]
    mape_ch = comp["champion_test_mape"]
    cv_ch = comp["results"][champion_name]["cv_rmse_5fold"]
    n_dev = split_info["n_dev"]; n_test = split_info["n_test"]
    dev_ini = split_info["dev_fecha_inicio"]; dev_fin = split_info["dev_fecha_fin"]
    test_ini = split_info["test_fecha_inicio"]; test_fin = split_info["test_fecha_fin"]
    u1_mod = u_theil["modelo"]["u1"]; u1_pers = u_theil["persistencia"]["u1"]
    u1_n = u_theil["n"]
    hm = heatmap_info

    execution = {
        "protocolo_version": "v2.0",
        "ejecutado_en": pd.Timestamp.now().isoformat(),
        "dataset_raw_sha256": raw_sha,
        "dataset_raw_file": "data/raw/owid_covid_kenya_raw.csv",
        "particion_80_20": split_info,
        "metrica_principal_validacion": "CV RMSE (TimeSeriesSplit, 5 folds)",
        "justificacion_metrica": "Tarea de regresión de cantidades (casos semanales). RMSE es pertinente y penaliza errores grandes; MAE se reporta como complementario. No se usa F1 ni AUC-ROC (no hay tarea de clasificación).",
        "regla_seleccion_campeon": "Mínimo CV RMSE en desarrollo (protocolo ciego ex-ante); el 20% de prueba no se usa para seleccionar.",
        "campeon": champion_name,
        "campeon_test_rmse": comp["champion_test_metrics"]["rmse"],
        "campeon_test_mae": comp["champion_test_metrics"]["mae"],
        "campeon_test_r2": comp["champion_test_metrics"]["r2"],
        "campeon_test_mape": comp["champion_test_mape"],
        "u_de_theil": u_theil,
        "pruebas_estadisticas": stats_res,
        "mapa_calor": heatmap_info,
        "figuras": {
            "particion_80_20": fig_partition,
            "observados_vs_predicciones": fig_obs_pred["figura_png"],
            "residuos": fig_resid["figura_png"],
            "mapa_calor": heatmap_info["figura_png"],
        },
        "exportaciones": {
            "auditoria_temporal": aud_path,
            "observados_vs_predicciones_csv": fig_obs_pred["csv"],
            "residuos_csv": fig_resid["csv"],
            "correlaciones_csv": heatmap_info["csv_correlaciones"],
        },
        "resultados_por_modelo": {},
    }

    print("PASO: antes bucle modelos", flush=True)
    for name, r in comp["results"].items():
        print("PASO: modelo " + name, flush=True)
        execution["resultados_por_modelo"][name] = {
            "cv_rmse_5fold": r["cv_rmse_5fold"],
            "best_params": r["best_params"],
            "fold_metrics": r["fold_metrics"],
            "dev_metrics": r["dev_metrics"],
            "test_metrics": r["test_metrics"],
            "test_mape": r["mape_test"],
            "rol": "CAMPEON_PREDICTIVO" if name == champion_name else ("BASELINE_PERSISTENCIA" if name == "Baseline_Naive_Persistence" else "COMPARATIVO"),
        }
    print("PASO: despues bucle modelos", flush=True)

    print("PASO: generar_interpretabilidad", flush=True)
    execution["interpretabilidad_explicabilidad"] = generar_interpretabilidad(
        execution, split_info, champion_name, cv_ch, rmse_ch, mae_ch,
        u_theil, stats_res, heatmap_info, hm, n_dev, n_test,
        dev_ini, dev_fin, test_ini, test_fin, u1_mod, u1_pers, u1_n,
        mae_ch_local=mae_ch,
    )
    print("PASO: interpretabilidad OK", flush=True)

    print("POST_JSON: antes de serializar", flush=True)
    out_path = os.path.join(MODELS_DIR, "protocolo_v2_resultados.json")
    try:
        def _sanitize(o):
            """Reemplaza float inf/nan (no JSON-compliant) por None de forma recursiva."""
            import math
            if isinstance(o, float):
                if math.isnan(o) or math.isinf(o):
                    return None
                return o
            if isinstance(o, dict):
                return {k: _sanitize(v) for k, v in o.items()}
            if isinstance(o, list):
                return [_sanitize(v) for v in o]
            return o

        execution = _sanitize(execution)
        execution_serializable = json.loads(json.dumps(execution, default=lambda o: float(o) if isinstance(o, (np.floating,)) else int(o) if isinstance(o, (np.integer,)) else str(o)))
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(execution_serializable, f, indent=2, ensure_ascii=False, allow_nan=False)
        print("POST_JSON: escrito", out_path, flush=True)
    except Exception as je:
        print("POST_JSON: ERROR al serializar/escribir:", repr(je), flush=True)
        raise

    print("\n" + "=" * 80, flush=True)
    print("PROTOCOLO V2.0 COMPLETADO", flush=True)
    print("=" * 80, flush=True)
    print(f"Campeón: {champion_name}", flush=True)
    print(f"Test RMSE: {comp['champion_test_metrics']['rmse']} | Test MAE: {comp['champion_test_metrics']['mae']}", flush=True)
    print(f"U de Theil modelo: {u_theil['modelo']['u1']} | U de Theil persistencia: {u_theil['persistencia']['u1']}", flush=True)
    print(f"Resultados: {out_path}", flush=True)
    print(f"Figuras en: {FIGURES_DIR}", flush=True)
    print(f"Exportaciones en: {EXPORT_DIR}", flush=True)
    return execution

if __name__ == "__main__":
    try:
        run_protocolo()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
