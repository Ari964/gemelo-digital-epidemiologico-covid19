import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import numpy as np
from sqlalchemy.orm import Session

from backend.app.models.monitoring import ModelMonitoringLogDB, ActiveModelDeploymentDB
from backend.app.models.dataset import DatasetDB
from backend.app.models.simulation import SimulationRunDB
from backend.app.models.observation import ObservationDB
from backend.app.analytics.statistics import (
    compute_population_stability_index,
    kolmogorov_smirnov_2sample,
    compute_mape, compute_rmse, compute_r2
)
from backend.app.schemas.monitoring import (
    MonitoringStatusResponse,
    MonitoringLogResponse,
    DriftMetric
)

class ModelMonitoringService:
    """
    Servicio de Monitoreo de Modelos Epidemiológicos (CRISP-DM Fase 6).
    Opera en modalidad 'Monitoreo Manual / Bajo Demanda'.
    Sin fabricación aleatoria de datos (se eliminó rng.normal, rng.beta, etc.).
    Distingue rigurosamente tres modalidades de monitoreo:
    1. DATA_DRIFT: Estabilidad temporal de insumos en ObservationDB (PSI / KS).
    2. OUTPUT_STABILITY: Estabilidad entre corridas de simulación del modelo.
    3. PREDICTIVE_DEGRADATION: Comparación de predicciones del modelo activo vs observaciones reales posteriores.
    Si no hay datos empíricos suficientes, reporta estado PENDING honesto sin métricas ficticias.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_monitoring_status(self) -> MonitoringStatusResponse:
        """Recupera el último estado de monitoreo evaluado para el modelo activo o el último registrado."""
        active_deploy = self.db.query(ActiveModelDeploymentDB).first()
        
        query = self.db.query(ModelMonitoringLogDB)
        if active_deploy:
            query = query.filter(ModelMonitoringLogDB.model_version == active_deploy.active_version)
        latest_log = query.order_by(ModelMonitoringLogDB.created_at.desc()).first()

        if not latest_log and not active_deploy:
            return MonitoringStatusResponse(
                active_model_name=None,
                active_model_version=None,
                is_active=False,
                monitoring_mode="DATA_DRIFT",
                overall_status="PENDING",
                last_evaluated_at=None,
                unavailability_reason="No hay un modelo activo desplegado en producción ni registros de monitoreo.",
                psi_value=None,
                psi_status=None,
                ks_p_value=None,
                ks_status=None,
                metrics=[],
                alerts=["Despliegue operativo inactivo. Las simulaciones deben correr en modo experimental."],
                recommendation="Para habilitar monitoreo, calibre y apruebe técnicamente una versión de modelo.",
                is_manual_run=True
            )

        if not latest_log and active_deploy:
            return MonitoringStatusResponse(
                active_model_name=active_deploy.model_name,
                active_model_version=active_deploy.active_version,
                is_active=True,
                monitoring_mode="DATA_DRIFT",
                overall_status="PENDING",
                last_evaluated_at=None,
                unavailability_reason="Modelo activo sin ciclo de monitoreo ejecutado aún.",
                psi_value=None,
                psi_status=None,
                ks_p_value=None,
                ks_status=None,
                metrics=[],
                alerts=["Monitoreo pendiente de ejecución manual sobre observaciones reales o simulaciones."],
                recommendation="Ejecute una evaluación de monitoreo en una de las tres modalidades soportadas.",
                is_manual_run=True
            )

        psi_list = json.loads(latest_log.psi_metrics_json) if latest_log.psi_metrics_json else []
        ks_list = json.loads(latest_log.ks_metrics_json) if latest_log.ks_metrics_json else []
        alerts = json.loads(latest_log.alerts_json) if latest_log.alerts_json else []
        perf_data = json.loads(latest_log.performance_metrics_json) if latest_log.performance_metrics_json else None

        combined_metrics: List[DriftMetric] = []
        for i, psi in enumerate(psi_list):
            var_name = psi.get("variable", f"var_{i}")
            ks_data = next((k for k in ks_list if k.get("variable") == var_name), {})
            combined_metrics.append(DriftMetric(
                variable=var_name,
                psi_value=psi.get("psi_value"),
                psi_status=psi.get("psi_status"),
                ks_statistic=ks_data.get("statistic"),
                ks_p_value=ks_data.get("p_value"),
                sample_size_ref=latest_log.sample_size_reference,
                sample_size_curr=latest_log.sample_size_current,
                warning_message=psi.get("warning") or ks_data.get("warning")
            ))

        first_psi = psi_list[0] if psi_list else {}
        first_ks = ks_list[0] if ks_list else {}

        mode = (perf_data.get("mode") if perf_data else None) or "DATA_DRIFT"

        return MonitoringStatusResponse(
            active_model_name=active_deploy.model_name if active_deploy else "Modelo en Evaluación",
            active_model_version=active_deploy.active_version if active_deploy else latest_log.model_version,
            is_active=bool(active_deploy),
            monitoring_mode=mode,
            overall_status=latest_log.severity_status or "PENDING",
            last_evaluated_at=latest_log.created_at,
            unavailability_reason=latest_log.unavailability_reason,
            psi_value=first_psi.get("psi_value"),
            psi_status=first_psi.get("psi_status"),
            ks_p_value=first_ks.get("p_value"),
            ks_status="SIGNIFICANT" if (first_ks.get("p_value") is not None and first_ks.get("p_value") < 0.05) else ("NO_DRIFT" if first_ks.get("p_value") is not None else None),
            metrics=combined_metrics,
            performance_metrics=perf_data,
            alerts=alerts,
            recommendation=latest_log.recommendation,
            is_manual_run=True
        )

    def run_monitoring_evaluation(
        self,
        notes: Optional[str] = None,
        monitoring_mode: str = "DATA_DRIFT",
        reference_dataset_id: Optional[str] = None,
        current_dataset_id: Optional[str] = None,
        recent_sim_id: Optional[str] = None,
        variables: Optional[List[str]] = None,
        evaluated_by: Optional[str] = None
    ) -> MonitoringStatusResponse:
        """
        Ejecuta un ciclo de monitoreo evaluando datos reales en una de las 3 modalidades:
        1. DATA_DRIFT: Compara distribución de observaciones reales entre dos fuentes o períodos verificados.
        2. OUTPUT_STABILITY: Compara series simuladas comparables (mismo modelo, escenario y horizonte).
        3. PREDICTIVE_DEGRADATION: Alinea predicciones del modelo activo con observaciones posteriores por fecha y territorio.
        """
        active_deploy = self.db.query(ActiveModelDeploymentDB).first()
        active_version = active_deploy.active_version if active_deploy else "v_unassigned"
        active_name = active_deploy.model_name if active_deploy else "Modelo no asignado"
        eval_user = evaluated_by or "operator"

        variables = variables or ["daily_cases"]
        target_var = variables[0] if variables else "daily_cases"

        psi_results = []
        ks_results = []
        alerts = []
        highest_severity = "PENDING"
        unavail_reason = None
        recommendation = None
        sample_ref = 0
        sample_curr = 0
        perf_summary: Dict[str, Any] = {"mode": monitoring_mode, "notes": notes}

        real_ref_id = reference_dataset_id or "UNSPECIFIED"
        real_curr_id = current_dataset_id or recent_sim_id or "UNSPECIFIED"

        if monitoring_mode == "DATA_DRIFT":
            # Modalidad 1: Deriva de datos en ObservationDB
            # 1. Validar existencia de las fuentes solicitadas
            ref_ds = None
            curr_ds = None

            if reference_dataset_id:
                ref_ds = self.db.query(DatasetDB).filter(DatasetDB.id == reference_dataset_id).first()
                if not ref_ds:
                    highest_severity = "PENDING"
                    unavail_reason = f"Dataset de referencia solicitado '{reference_dataset_id}' no existe en el sistema."
                    alerts.append(unavail_reason)
                    recommendation = "Verifique el identificador del dataset de referencia en el catálogo de datos."

            if current_dataset_id and highest_severity == "PENDING" and unavail_reason is None:
                curr_ds = self.db.query(DatasetDB).filter(DatasetDB.id == current_dataset_id).first()
                if not curr_ds:
                    highest_severity = "PENDING"
                    unavail_reason = f"Dataset actual solicitado '{current_dataset_id}' no existe en el sistema."
                    alerts.append(unavail_reason)
                    recommendation = "Verifique el identificador del dataset actual en el catálogo de datos."

            if unavail_reason is None:
                # Si no se proporcionan datasets explícitos o falta uno de ellos sin ventanas temporales
                if not reference_dataset_id or not current_dataset_id:
                    highest_severity = "PENDING"
                    unavail_reason = "Se requiere especificar tanto el dataset de referencia como el dataset actual para evaluar deriva de datos."
                    alerts.append(unavail_reason)
                    recommendation = "Proporcione 'reference_dataset_id' y 'current_dataset_id' válidos."
                else:
                    # Procedencia: advertir si son sintéticos
                    is_synthetic_eval = bool(
                        (ref_ds and (ref_ds.is_synthetic or ref_ds.source_type in ["SYNTHETIC", "ESTIMATED"])) or
                        (curr_ds and (curr_ds.is_synthetic or curr_ds.source_type in ["SYNTHETIC", "ESTIMATED"]))
                    )
                    perf_summary["is_synthetic"] = is_synthetic_eval
                    if ref_ds:
                        perf_summary["reference_source_type"] = ref_ds.source_type
                    if curr_ds:
                        perf_summary["current_source_type"] = curr_ds.source_type

                    if is_synthetic_eval:
                        alerts.append("Aviso de Procedencia: Uno o ambos datasets evaluados contienen datos sintéticos o estimados.")

                    # Recuperar observaciones de cada dataset
                    ref_obs = (
                        self.db.query(ObservationDB)
                        .filter(ObservationDB.dataset_id == reference_dataset_id, ObservationDB.variable == target_var)
                        .order_by(ObservationDB.observation_date.asc())
                        .all()
                    )
                    curr_obs = (
                        self.db.query(ObservationDB)
                        .filter(ObservationDB.dataset_id == current_dataset_id, ObservationDB.variable == target_var)
                        .order_by(ObservationDB.observation_date.asc())
                        .all()
                    )

                    # Validar tamaño mínimo por ventana (mínimo 15 observaciones por ventana)
                    if len(ref_obs) < 15 or len(curr_obs) < 15:
                        highest_severity = "PENDING"
                        unavail_reason = (
                            f"Muestra insuficiente para evaluar deriva (referencia: {len(ref_obs)}, actual: {len(curr_obs)}; "
                            f"mínimo 15 observaciones requeridas por ventana)."
                        )
                        alerts.append(unavail_reason)
                        recommendation = "Amplíe la ventana temporal o seleccione datasets con mayor cobertura temporal."
                    else:
                        # Exigir compatibilidad de unidad, territorio y agregación
                        ref_units = set(o.unit for o in ref_obs)
                        curr_units = set(o.unit for o in curr_obs)
                        ref_aggs = set(o.aggregation_level for o in ref_obs)
                        curr_aggs = set(o.aggregation_level for o in curr_obs)

                        if ref_units != curr_units or ref_aggs != curr_aggs:
                            highest_severity = "PENDING"
                            unavail_reason = (
                                f"Incompatibilidad entre datasets: unidades ({ref_units} vs {curr_units}) o "
                                f"niveles de agregación ({ref_aggs} vs {curr_aggs}) no coinciden."
                            )
                            alerts.append(unavail_reason)
                            recommendation = "Homogeneice las variables y unidades de las series antes de evaluar deriva."
                        else:
                            ref_vals = np.array([o.value for o in ref_obs], dtype=float)
                            curr_vals = np.array([o.value for o in curr_obs], dtype=float)
                            sample_ref = len(ref_vals)
                            sample_curr = len(curr_vals)

                            psi_val, psi_sev, psi_warn = compute_population_stability_index(ref_vals, curr_vals, num_bins=6)
                            ks_res = kolmogorov_smirnov_2sample(ref_vals, curr_vals)

                            if psi_val is None or not np.isfinite(psi_val):
                                highest_severity = "PENDING"
                                unavail_reason = f"No fue posible calcular PSI: {psi_warn or 'datos con varianza nula o intervalos degenerados'}."
                                alerts.append(unavail_reason)
                            else:
                                highest_severity = psi_sev
                                psi_results.append({
                                    "variable": target_var,
                                    "psi_value": psi_val,
                                    "psi_status": psi_sev,
                                    "warning": psi_warn
                                })
                                ks_results.append({
                                    "variable": target_var,
                                    "statistic": ks_res.get("statistic"),
                                    "p_value": ks_res.get("p_value"),
                                    "distributions_differ": ks_res.get("distributions_differ"),
                                    "warning": ks_res.get("warning")
                                })

                                psi_str = f"{psi_val:.4f}"
                                if psi_sev == "CRITICAL":
                                    alerts.append(f"Alerta Crítica: Deriva significativa en '{target_var}' (PSI = {psi_str} >= 0.25).")
                                    recommendation = "Se detectó cambio severo en la distribución de insumos. Se recomienda recalibrar."
                                elif psi_sev == "WARNING":
                                    alerts.append(f"Advertencia: Deriva moderada en '{target_var}' (PSI = {psi_str}).")
                                    recommendation = "Monitorear de cerca la evolución de las observaciones recientes."
                                else:
                                    highest_severity = "HEALTHY"
                                    alerts.append(f"Insumos estables respecto al período de referencia (PSI = {psi_str} < 0.10).")
                                    recommendation = "Distribución de insumos observados estable."

        elif monitoring_mode == "OUTPUT_STABILITY":
            # Modalidad 2: Estabilidad de salidas del modelo entre corridas comparables
            curr_sim = None
            if recent_sim_id:
                curr_sim = self.db.query(SimulationRunDB).filter(SimulationRunDB.id == recent_sim_id).first()
                if not curr_sim:
                    highest_severity = "PENDING"
                    unavail_reason = f"Simulación reciente solicitada '{recent_sim_id}' no existe."
                    alerts.append(unavail_reason)
            else:
                curr_sim = self.db.query(SimulationRunDB).order_by(SimulationRunDB.created_at.desc()).first()

            if unavail_reason is None:
                if not curr_sim:
                    highest_severity = "PENDING"
                    unavail_reason = "No existen simulaciones registradas para evaluar estabilidad de salidas."
                    alerts.append(unavail_reason)
                    recommendation = "Ejecute al menos dos simulaciones comparables para habilitar esta modalidad."
                else:
                    curr_series = json.loads(curr_sim.daily_series_json) if curr_sim.daily_series_json else []
                    curr_params = json.loads(curr_sim.effective_parameters_json or curr_sim.parameters_json or "{}")
                    curr_scenario = curr_params.get("scenario_name") or curr_params.get("scenario") or "default"
                    curr_horizon = len(curr_series)

                    # Buscar simulación candidata comparable (mismo model_version, escenario y horizonte)
                    candidates = (
                        self.db.query(SimulationRunDB)
                        .filter(SimulationRunDB.id != curr_sim.id)
                        .filter(SimulationRunDB.model_version == curr_sim.model_version)
                        .order_by(SimulationRunDB.created_at.desc())
                        .limit(10)
                        .all()
                    )

                    ref_sim = None
                    for cand in candidates:
                        cand_series = json.loads(cand.daily_series_json) if cand.daily_series_json else []
                        cand_params = json.loads(cand.effective_parameters_json or cand.parameters_json or "{}")
                        cand_scenario = cand_params.get("scenario_name") or cand_params.get("scenario") or "default"
                        cand_horizon = len(cand_series)
                        if cand_scenario == curr_scenario and abs(cand_horizon - curr_horizon) == 0:
                            ref_sim = cand
                            break

                    if not ref_sim:
                        highest_severity = "PENDING"
                        unavail_reason = (
                            f"No se encontró una simulación comparable para la versión '{curr_sim.model_version}' "
                            f"con idéntico escenario ('{curr_scenario}') y horizonte ({curr_horizon} días)."
                        )
                        alerts.append(unavail_reason)
                        recommendation = "Ejecute simulaciones bajo condiciones idénticas de escenario y horizonte para auditar estabilidad."
                    else:
                        real_ref_id = ref_sim.id
                        real_curr_id = curr_sim.id
                        ref_series = json.loads(ref_sim.daily_series_json) if ref_sim.daily_series_json else []

                        if len(curr_series) < 15 or len(ref_series) < 15:
                            highest_severity = "PENDING"
                            unavail_reason = f"Horizonte de simulación insuficiente ({min(len(curr_series), len(ref_series))} días, mínimo 15 requeridos)."
                            alerts.append(unavail_reason)
                        else:
                            ref_vals = np.array(ref_series, dtype=float)
                            curr_vals = np.array(curr_series, dtype=float)
                            sample_ref = len(ref_vals)
                            sample_curr = len(curr_vals)

                            psi_val, psi_sev, psi_warn = compute_population_stability_index(ref_vals, curr_vals, num_bins=6)
                            ks_res = kolmogorov_smirnov_2sample(ref_vals, curr_vals)

                            if psi_val is None or not np.isfinite(psi_val):
                                highest_severity = "PENDING"
                                unavail_reason = f"No fue posible calcular estabilidad de salidas: {psi_warn}"
                                alerts.append(unavail_reason)
                            else:
                                highest_severity = psi_sev
                                psi_results.append({
                                    "variable": "model_output_daily_cases",
                                    "psi_value": psi_val,
                                    "psi_status": psi_sev,
                                    "warning": psi_warn
                                })
                                ks_results.append({
                                    "variable": "model_output_daily_cases",
                                    "statistic": ks_res.get("statistic"),
                                    "p_value": ks_res.get("p_value"),
                                    "distributions_differ": ks_res.get("distributions_differ"),
                                    "warning": ks_res.get("warning")
                                })

                                psi_str = f"{psi_val:.4f}"
                                if psi_sev in ["CRITICAL", "WARNING"]:
                                    alerts.append(f"Variación notable en las salidas del modelo entre corridas (PSI = {psi_str}).")
                                    recommendation = "Revisar si los parámetros de simulación cambiaron drásticamente."
                                else:
                                    highest_severity = "HEALTHY"
                                    alerts.append(f"Salidas del modelo reproducibles y estables (PSI = {psi_str}).")
                                    recommendation = "Comportamiento del motor de simulación consistente."

        elif monitoring_mode == "PREDICTIVE_DEGRADATION":
            # Modalidad 3: Degradación predictiva vs observaciones reales posteriores alineadas
            if not active_deploy:
                highest_severity = "PENDING"
                unavail_reason = "No existe un modelo activo desplegado en producción para evaluar degradación predictiva."
                alerts.append(unavail_reason)
                recommendation = "Active un modelo aprobado técnicamente para habilitar esta modalidad."
            else:
                # Recuperar simulación asociada al modelo activo con serie temporal y fecha de inicio
                sim = (
                    self.db.query(SimulationRunDB)
                    .filter(SimulationRunDB.model_version == active_deploy.active_version)
                    .order_by(SimulationRunDB.created_at.desc())
                    .first()
                )

                if not sim or not sim.simulation_start_date or not sim.daily_series_json:
                    highest_severity = "PENDING"
                    unavail_reason = f"No se encontró una simulación con serie temporal y fecha de inicio para el modelo activo '{active_deploy.active_version}'."
                    alerts.append(unavail_reason)
                else:
                    real_ref_id = active_deploy.active_version
                    real_curr_id = sim.id
                    sim_start = sim.simulation_start_date
                    sim_series = json.loads(sim.daily_series_json)

                    # Calendario propio de la simulación
                    sim_calendar = {}
                    for i, val in enumerate(sim_series):
                        if val is not None and np.isfinite(val):
                            sim_calendar[(sim_start + timedelta(days=i)).date()] = float(val)

                    # Observaciones empíricas con compatibilidad territorial (nacional agregada)
                    obs_query = (
                        self.db.query(ObservationDB)
                        .filter(
                            ObservationDB.observation_date >= sim_start,
                            ObservationDB.variable == target_var,
                            ObservationDB.county_code == 0,
                            ObservationDB.aggregation_level == "NATIONAL_DAILY"
                        )
                        .order_by(ObservationDB.observation_date.asc())
                        .all()
                    )

                    # Alinear observaciones con predicciones por fecha de calendario exacta
                    aligned_pairs = []
                    for o in obs_query:
                        o_date = o.observation_date.date()
                        if o_date in sim_calendar and o.value is not None and np.isfinite(o.value):
                            aligned_pairs.append((float(o.value), sim_calendar[o_date]))

                    if len(aligned_pairs) < 10:
                        highest_severity = "PENDING"
                        unavail_reason = (
                            f"Insuficientes fechas coincidentes entre predicciones y observaciones territoriales posteriores "
                            f"({len(aligned_pairs)} puntos alineados, mínimo 10 requeridos)."
                        )
                        alerts.append(unavail_reason)
                        recommendation = "Aguarde la disponibilidad de observaciones epidemiológicas que coincidan con el horizonte de simulación."
                    else:
                        y_true = np.array([p[0] for p in aligned_pairs], dtype=float)
                        y_pred = np.array([p[1] for p in aligned_pairs], dtype=float)
                        sample_ref = len(y_true)
                        sample_curr = len(y_pred)

                        mape_val, _ = compute_mape(y_true, y_pred)
                        rmse_val = compute_rmse(y_true, y_pred)
                        r2_val = compute_r2(y_true, y_pred)

                        # Buscar evaluación de referencia para comparar contra la línea base de calibración
                        from backend.app.models.evaluation import EvaluationRunDB
                        baseline_eval = (
                            self.db.query(EvaluationRunDB)
                            .filter(EvaluationRunDB.model_version == active_deploy.active_version)
                            .order_by(EvaluationRunDB.created_at.desc())
                            .first()
                        )
                        baseline_mape = baseline_eval.candidate_mape if baseline_eval else None

                        mape_str = f"{mape_val:.2f}%" if mape_val is not None else "N/A"
                        base_mape_str = f"{baseline_mape:.2f}%" if baseline_mape is not None else "N/A"

                        perf_summary.update({
                            "mape_posterior": mape_val,
                            "rmse_posterior": rmse_val,
                            "r2_posterior": r2_val,
                            "sample_size": len(y_true),
                            "baseline_mape": baseline_mape
                        })

                        if baseline_mape is not None and mape_val is not None:
                            delta_mape = mape_val - baseline_mape
                            perf_summary["delta_mape_vs_baseline"] = delta_mape
                            if delta_mape > 15.0 or mape_val > 35.0:
                                highest_severity = "CRITICAL"
                                alerts.append(f"Degradación crítica: MAPE posterior ({mape_str}) supera la línea base ({base_mape_str}) en +{delta_mape:.2f} puntos porcentuales.")
                                recommendation = "El modelo activo presenta degradación severa respecto a su calibración. Recalibrar de inmediato."
                            elif delta_mape > 5.0 or mape_val > 25.0:
                                highest_severity = "WARNING"
                                alerts.append(f"Degradación moderada: MAPE posterior ({mape_str}) aumentó +{delta_mape:.2f} puntos respecto a la línea base ({base_mape_str}).")
                                recommendation = "Monitorear de cerca. Programar calibración en la siguiente ventana."
                            else:
                                highest_severity = "HEALTHY"
                                alerts.append(f"Desempeño estable: MAPE posterior ({mape_str}) consistente con línea base ({base_mape_str}).")
                                recommendation = "El modelo mantiene precisión acorde a su registro de validación."
                        elif mape_val is not None:
                            if mape_val > 35.0:
                                highest_severity = "CRITICAL"
                                alerts.append(f"Error posterior elevado (MAPE = {mape_str}), sin registro de línea base previa.")
                                recommendation = "Error absoluto alto detectado. Evaluar recalibración."
                            elif mape_val > 25.0:
                                highest_severity = "WARNING"
                                alerts.append(f"Error posterior moderado (MAPE = {mape_str}), sin registro de línea base previa.")
                                recommendation = "Monitorear próximas observaciones."
                            else:
                                highest_severity = "HEALTHY"
                                alerts.append(f"Error posterior aceptable (MAPE = {mape_str}).")
                                recommendation = "Modelo dentro de umbrales operativos generales."
                        else:
                            highest_severity = "PENDING"
                            unavail_reason = "No fue posible calcular métricas de error posteriores de forma finita."
                            alerts.append(unavail_reason)

        log_id = f"mon-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        monitoring_entry = ModelMonitoringLogDB(
            id=log_id,
            model_version=active_version,
            reference_dataset_id=real_ref_id,
            current_dataset_id=real_curr_id,
            time_window_start=now - timedelta(days=30),
            time_window_end=now,
            availability_status="AVAILABLE" if highest_severity != "PENDING" else "PENDING",
            severity_status=highest_severity if highest_severity != "PENDING" else None,
            unavailability_reason=unavail_reason,
            variables_analyzed_json=json.dumps([target_var]),
            sample_size_reference=sample_ref,
            sample_size_current=sample_curr,
            psi_metrics_json=json.dumps(psi_results),
            ks_metrics_json=json.dumps(ks_results),
            performance_metrics_json=json.dumps(perf_summary),
            alerts_json=json.dumps(alerts),
            recommendation=recommendation or "Sin recomendación activa.",
            evaluated_by=eval_user
        )
        self.db.add(monitoring_entry)
        self.db.commit()

        return self.get_monitoring_status()

    def get_monitoring_history(self, limit: int = 50) -> List[MonitoringLogResponse]:
        """Retorna el historial de evaluaciones de monitoreo registradas."""
        logs = (
            self.db.query(ModelMonitoringLogDB)
            .order_by(ModelMonitoringLogDB.created_at.desc())
            .limit(limit)
            .all()
        )
        results = []
        for log in logs:
            psi_list = json.loads(log.psi_metrics_json) if log.psi_metrics_json else []
            ks_list = json.loads(log.ks_metrics_json) if log.ks_metrics_json else []
            first_psi = psi_list[0] if psi_list else {}
            first_ks = ks_list[0] if ks_list else {}
            perf = json.loads(log.performance_metrics_json) if log.performance_metrics_json else {}

            results.append(MonitoringLogResponse(
                id=log.id,
                model_version=log.model_version,
                evaluated_at=log.created_at,
                psi_value=first_psi.get("psi_value"),
                psi_status=first_psi.get("psi_status"),
                ks_p_value=first_ks.get("p_value"),
                ks_status="SIGNIFICANT" if (first_ks.get("p_value") is not None and first_ks.get("p_value") < 0.05) else ("NO_DRIFT" if first_ks.get("p_value") is not None else None),
                overall_status=log.severity_status or "PENDING",
                notes=perf.get("notes"),
                unavailability_reason=log.unavailability_reason
            ))
        return results
