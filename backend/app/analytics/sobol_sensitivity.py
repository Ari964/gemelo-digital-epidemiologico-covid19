import time
import uuid
import json
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional
import numpy as np

from backend.app.epidemiology.seir_baseline import SEIRBaselineModel
from backend.app.db import session as session_module
from backend.app.models.sobol import SobolTaskDB

try:
    from SALib.sample import sobol as sobol_sample
    from SALib.analyze import sobol as sobol_analyze
    HAS_SALIB = True
except ImportError:
    try:
        from SALib.sample import saltelli as sobol_sample
        from SALib.analyze import sobol as sobol_analyze
        HAS_SALIB = True
    except ImportError:
        HAS_SALIB = False

class SobolSensitivityAnalyzer:
    """
    Análisis de Sensibilidad Global de Sobol (Saltelli Variance Decomposition).
    ALCANCE CIENTÍFICO EXPLÍCITO:
    - Evalúa estrictamente el Modelo SEIR Clásico Agregado (Línea Base Compartimental).
    - NO representa la sensibilidad causal del motor híbrido completo (SEIR Espacial + ABM).
    - Emplea el estimador de descomposición de varianza de Saltelli/Sobol (SALib).
    - Persiste el estado y los resultados canónicos en la base de datos (tabla sobol_tasks).
    - Tras un reinicio, recupera tareas inconclusas marcándolas como INTERRUPTED.
    """

    _lock = threading.Lock()
    _semaphore = threading.Semaphore(2)  # Máximo 2 análisis concurrentes
    _analyses: Dict[str, Dict[str, Any]] = {}

    PROBLEM = {
        'num_vars': 5,
        'names': ['beta_transmission', 'sigma_latency', 'gamma_recovery', 'mu_fatality', 'initial_seed'],
        'bounds': [
            [0.20, 0.50],        # beta
            [1.0/7.0, 1.0/3.5],  # sigma (período de incubación 3.5 - 7 días)
            [1.0/14.0, 1.0/7.0], # gamma (período infeccioso 7 - 14 días)
            [0.005, 0.030],      # mu (letalidad 0.5% - 3%)
            [10, 150]            # seed (casos iniciales)
        ]
    }

    PARAMETER_DISPLAY_NAMES = {
        'beta_transmission': 'Tasa de Transmisión (β)',
        'sigma_latency': 'Tasa de Latencia / Incubación (σ)',
        'gamma_recovery': 'Tasa de Recuperación (γ)',
        'mu_fatality': 'Tasa de Letalidad por Infección (μ)',
        'initial_seed': 'Semilla Inicial de Infecciones (I₀)'
    }

    @classmethod
    def start_analysis_task(
        cls,
        samples_n: int = 128,
        target_metric: str = "peak_infections",
        seed: int = 42
    ) -> str:
        """Inicia el análisis de forma asíncrona no bloqueante y persiste el registro PENDING en BD."""
        analysis_id = f"sobol-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        total_evals = (cls.PROBLEM['num_vars'] + 2) * samples_n

        task_record = {
            "analysis_id": analysis_id,
            "status": "PENDING",
            "progress_pct": 0,
            "model_engine": "SEIR_CLASSICAL_BASELINE",
            "model_analyzed": "SEIR Classical Baseline Model (Compartmental Aggregated)",
            "target_metric": target_metric,
            "samples_per_variable": samples_n,
            "n_samples": samples_n,
            "total_evaluations": total_evals,
            "seed": seed,
            "calc_second_order": False,
            "method": "Sobol Global Sensitivity Analysis (Saltelli Variance Decomposition)",
            "indices": None,
            "sobol_indices": None,
            "most_sensitive_parameter": None,
            "error": None,
            "error_message": None,
            "created_at": now,
            "completed_at": None,
            "duration_ms": None
        }

        with cls._lock:
            cls._analyses[analysis_id] = task_record

        # Persistir registro en Base de Datos
        try:
            db = session_module.SessionLocal()
            try:
                db_task = SobolTaskDB(
                    id=analysis_id,
                    status="PENDING",
                    model_analyzed=task_record["model_analyzed"],
                    target_metric=target_metric,
                    samples_per_variable=samples_n,
                    total_evaluations=total_evals,
                    seed=seed,
                    indices_json=None,
                    most_sensitive_parameter=None,
                    error=None,
                    created_at=now
                )
                db.add(db_task)
                db.commit()
            finally:
                db.close()
        except Exception as e:
            print(f"[SobolSensitivityAnalyzer] Error al persistir tarea en BD: {e}")

        # Lanzar en hilo de fondo para no bloquear FastAPI
        t = threading.Thread(
            target=cls._run_worker,
            args=(analysis_id, samples_n, target_metric, seed),
            daemon=True
        )
        t.start()

        return analysis_id

    @classmethod
    def get_analysis_status(cls, analysis_id: str) -> Optional[Dict[str, Any]]:
        # Primero buscar en memoria
        with cls._lock:
            record = cls._analyses.get(analysis_id)
            if record:
                return record.copy()

        # Si no está en memoria (e.g. tras reinicio del servidor), consultar en BD
        try:
            db = SessionLocal()
            try:
                db_task = db.query(SobolTaskDB).filter(SobolTaskDB.id == analysis_id).first()
                if db_task:
                    indices_parsed = json.loads(db_task.indices_json) if db_task.indices_json else None
                    rec = {
                        "analysis_id": db_task.id,
                        "status": db_task.status,
                        "progress_pct": 100 if db_task.status == "COMPLETED" else 0,
                        "model_engine": "SEIR_CLASSICAL_BASELINE",
                        "model_analyzed": db_task.model_analyzed,
                        "target_metric": db_task.target_metric,
                        "samples_per_variable": db_task.samples_per_variable,
                        "n_samples": db_task.samples_per_variable,
                        "total_evaluations": db_task.total_evaluations,
                        "seed": db_task.seed,
                        "calc_second_order": False,
                        "method": "Sobol Global Sensitivity Analysis (Saltelli Variance Decomposition)",
                        "indices": indices_parsed,
                        "sobol_indices": indices_parsed,
                        "most_sensitive_parameter": db_task.most_sensitive_parameter,
                        "error": db_task.error,
                        "error_message": db_task.error,
                        "created_at": db_task.created_at,
                        "completed_at": db_task.completed_at,
                        "duration_ms": db_task.duration_ms
                    }
                    with cls._lock:
                        cls._analyses[analysis_id] = rec
                    return rec.copy()
            finally:
                db.close()
        except Exception as e:
            print(f"[SobolSensitivityAnalyzer] Error al consultar tarea en BD: {e}")

        return None

    @classmethod
    def list_analyses(cls, limit: int = 10) -> List[Dict[str, Any]]:
        # Consultar BD para tener la lista completa incluso tras reinicios
        try:
            db = SessionLocal()
            try:
                db_tasks = db.query(SobolTaskDB).order_by(SobolTaskDB.created_at.desc()).limit(limit).all()
                out = []
                for db_task in db_tasks:
                    indices_parsed = json.loads(db_task.indices_json) if db_task.indices_json else None
                    out.append({
                        "analysis_id": db_task.id,
                        "status": db_task.status,
                        "progress_pct": 100 if db_task.status == "COMPLETED" else 0,
                        "model_engine": "SEIR_CLASSICAL_BASELINE",
                        "model_analyzed": db_task.model_analyzed,
                        "target_metric": db_task.target_metric,
                        "samples_per_variable": db_task.samples_per_variable,
                        "n_samples": db_task.samples_per_variable,
                        "total_evaluations": db_task.total_evaluations,
                        "seed": db_task.seed,
                        "calc_second_order": False,
                        "method": "Sobol Global Sensitivity Analysis (Saltelli Variance Decomposition)",
                        "indices": indices_parsed,
                        "sobol_indices": indices_parsed,
                        "most_sensitive_parameter": db_task.most_sensitive_parameter,
                        "error": db_task.error,
                        "error_message": db_task.error,
                        "created_at": db_task.created_at,
                        "completed_at": db_task.completed_at,
                        "duration_ms": db_task.duration_ms
                    })
                if out:
                    return out
            finally:
                db.close()
        except Exception as e:
            print(f"[SobolSensitivityAnalyzer] Error al listar tareas de BD: {e}")

        with cls._lock:
            sorted_items = sorted(cls._analyses.values(), key=lambda x: x["created_at"], reverse=True)
            return [x.copy() for x in sorted_items[:limit]]

    @classmethod
    def recover_on_startup(cls):
        """
        Marca como INTERRUPTED cualquier análisis que hubiera quedado en RUNNING o PENDING
        al reiniciar el servicio, tanto en memoria como en la base de datos persistente.
        """
        with cls._lock:
            for item in cls._analyses.values():
                if item["status"] in ["RUNNING", "PENDING"]:
                    item["status"] = "INTERRUPTED"
                    item["error"] = "Análisis interrumpido por reinicio del servidor."
                    item["error_message"] = item["error"]

        try:
            db = session_module.SessionLocal()
            try:
                uncompleted = db.query(SobolTaskDB).filter(SobolTaskDB.status.in_(["RUNNING", "PENDING"])).all()
                for task in uncompleted:
                    task.status = "INTERRUPTED"
                    task.error = "Análisis interrumpido por reinicio del servidor."
                    task.completed_at = datetime.utcnow()
                db.commit()
            finally:
                db.close()
        except Exception as e:
            print(f"[SobolSensitivityAnalyzer] Error al recuperar tareas interrumpidas en BD: {e}")

    @classmethod
    def _run_worker(cls, analysis_id: str, samples_n: int, target_metric: str, seed: int):
        with cls._semaphore:
            with cls._lock:
                if analysis_id not in cls._analyses:
                    return
                cls._analyses[analysis_id]["status"] = "RUNNING"
                cls._analyses[analysis_id]["progress_pct"] = 25

            # Actualizar estado a RUNNING en BD
            try:
                db = session_module.SessionLocal()
                try:
                    db_task = db.query(SobolTaskDB).filter(SobolTaskDB.id == analysis_id).first()
                    if db_task:
                        db_task.status = "RUNNING"
                        db.commit()
                finally:
                    db.close()
            except Exception as e:
                print(f"[SobolSensitivityAnalyzer] Error al actualizar estado RUNNING en BD: {e}")

            start_t = time.time()
            try:
                result = cls._compute_sobol(samples_n, target_metric, seed)
                duration_ms = int((time.time() - start_t) * 1000)

                with cls._lock:
                    rec = cls._analyses[analysis_id]
                    rec["status"] = "COMPLETED"
                    rec["progress_pct"] = 100
                    rec["completed_at"] = datetime.utcnow()
                    rec["duration_ms"] = duration_ms
                    rec["indices"] = result["indices"]
                    rec["sobol_indices"] = result["indices"]
                    rec["most_sensitive_parameter"] = result["most_sensitive_parameter"]
                    rec["total_evaluations"] = result["total_evaluations"]

                # Actualizar COMPLETED en BD
                try:
                    db = session_module.SessionLocal()
                    try:
                        db_task = db.query(SobolTaskDB).filter(SobolTaskDB.id == analysis_id).first()
                        if db_task:
                            db_task.status = "COMPLETED"
                            db_task.completed_at = rec["completed_at"]
                            db_task.duration_ms = duration_ms
                            db_task.indices_json = json.dumps(result["indices"])
                            db_task.most_sensitive_parameter = result["most_sensitive_parameter"]
                            db_task.total_evaluations = result["total_evaluations"]
                            db.commit()
                    finally:
                        db.close()
                except Exception as e:
                    print(f"[SobolSensitivityAnalyzer] Error al persistir resultado COMPLETED en BD: {e}")

            except Exception as e:
                duration_ms = int((time.time() - start_t) * 1000)
                err_str = str(e)
                with cls._lock:
                    rec = cls._analyses[analysis_id]
                    rec["status"] = "FAILED"
                    rec["progress_pct"] = 0
                    rec["completed_at"] = datetime.utcnow()
                    rec["duration_ms"] = duration_ms
                    rec["error"] = err_str
                    rec["error_message"] = err_str

                # Actualizar FAILED en BD
                try:
                    db = session_module.SessionLocal()
                    try:
                        db_task = db.query(SobolTaskDB).filter(SobolTaskDB.id == analysis_id).first()
                        if db_task:
                            db_task.status = "FAILED"
                            db_task.completed_at = rec["completed_at"]
                            db_task.duration_ms = duration_ms
                            db_task.error = err_str
                            db.commit()
                    finally:
                        db.close()
                except Exception as e:
                    print(f"[SobolSensitivityAnalyzer] Error al persistir FAILED en BD: {e}")

    @classmethod
    def _compute_sobol(cls, N: int, target_metric: str, seed: int) -> Dict[str, Any]:
        """Cálculo matemático riguroso de índices de Sobol (Saltelli Variance Decomposition)."""
        param_names = cls.PROBLEM['names']
        bounds = cls.PROBLEM['bounds']
        D = cls.PROBLEM['num_vars']

        def eval_single_param_vector(p):
            m = SEIRBaselineModel(
                population=47564296,
                initial_infected=int(p[4]),
                initial_exposed=int(p[4] * 2),
                beta=float(p[0]),
                sigma=float(p[1]),
                gamma=float(p[2]),
                mu=float(p[3])
            )
            sim_out = m.run(days=100)
            if target_metric == "total_cases":
                return float(sim_out.get("total_cases", sim_out["peak_infections"]))
            return float(sim_out["peak_infections"])

        if HAS_SALIB:
            try:
                # SALib 1.5+ sobol.sample con seed reproducible
                param_values = sobol_sample.sample(cls.PROBLEM, N, calc_second_order=False, seed=seed)
            except TypeError:
                # Versiones anteriores de SALib
                param_values = sobol_sample.sample(cls.PROBLEM, N, calc_second_order=False)

            Y = np.zeros(len(param_values))
            for i, row in enumerate(param_values):
                Y[i] = eval_single_param_vector(row)

            try:
                sobol_res = sobol_analyze.analyze(cls.PROBLEM, Y, calc_second_order=False, print_to_console=False, seed=seed)
            except TypeError:
                sobol_res = sobol_analyze.analyze(cls.PROBLEM, Y, calc_second_order=False, print_to_console=False)

            indices = []
            for j, name in enumerate(param_names):
                s1 = float(sobol_res['S1'][j])
                st = float(sobol_res['ST'][j])
                s1_conf = float(sobol_res['S1_conf'][j]) if 'S1_conf' in sobol_res and not np.isnan(sobol_res['S1_conf'][j]) else None
                st_conf = float(sobol_res['ST_conf'][j]) if 'ST_conf' in sobol_res and not np.isnan(sobol_res['ST_conf'][j]) else None

                indices.append({
                    "parameter": name,
                    "parameter_name": cls.PARAMETER_DISPLAY_NAMES.get(name, name),
                    "S1": round(s1, 4),
                    "S1_conf": round(s1_conf, 4) if s1_conf is not None else None,
                    "ST": round(st, 4),
                    "ST_conf": round(st_conf, 4) if st_conf is not None else None,
                    "confidence_interval": [round(s1 - (s1_conf or 0), 4), round(s1 + (s1_conf or 0), 4)] if s1_conf else None
                })
            total_evals = len(param_values)
        else:
            # Estimador de descomposición de varianza de Saltelli con NumPy puro
            rng = np.random.default_rng(seed)
            A = np.zeros((N, D))
            B = np.zeros((N, D))
            for d in range(D):
                low, high = bounds[d]
                A[:, d] = rng.uniform(low, high, N)
                B[:, d] = rng.uniform(low, high, N)

            y_A = np.array([eval_single_param_vector(A[i, :]) for i in range(N)])
            y_B = np.array([eval_single_param_vector(B[i, :]) for i in range(N)])
            
            y_all = np.concatenate([y_A, y_B])
            var_y = float(np.var(y_all))
            if var_y == 0.0:
                var_y = 1.0

            indices = []
            total_evals = 2 * N
            for j in range(D):
                AB_j = B.copy()
                AB_j[:, j] = A[:, j]
                y_AB = np.array([eval_single_param_vector(AB_j[i, :]) for i in range(N)])
                total_evals += N

                # Estimador Saltelli primer orden S1
                s1 = float(np.mean(y_B * (y_AB - y_A)) / var_y)
                # Estimador Saltelli orden total ST
                st = float(np.mean((y_A - y_AB) ** 2) / (2.0 * var_y))

                indices.append({
                    "parameter": param_names[j],
                    "parameter_name": cls.PARAMETER_DISPLAY_NAMES.get(param_names[j], param_names[j]),
                    "S1": round(s1, 4),
                    "S1_conf": None,
                    "ST": round(st, 4),
                    "ST_conf": None,
                    "confidence_interval": None
                })

        st_values = [p["ST"] for p in indices]
        top_param = param_names[int(np.argmax(st_values))]

        return {
            "indices": indices,
            "most_sensitive_parameter": cls.PARAMETER_DISPLAY_NAMES.get(top_param, top_param),
            "total_evaluations": total_evals
        }

    @classmethod
    def evaluate_ishigami_benchmark(cls, N: int = 512, seed: int = 42) -> Dict[str, Any]:
        """
        Función de referencia matemática de Ishigami para verificación formal de SALib:
        f(x1, x2, x3) = sin(x1) + a * sin^2(x2) + b * x3^4 * sin(x1)
        Valores analíticos conocidos para a=7, b=0.1 en [-pi, pi]^3:
        S1 ~ 0.3138, S2 ~ 0.4424, S3 ~ 0.0000
        ST1 ~ 0.5574, ST2 ~ 0.4424, ST3 ~ 0.2436
        """
        problem = {
            'num_vars': 3,
            'names': ['x1', 'x2', 'x3'],
            'bounds': [[-np.pi, np.pi], [-np.pi, np.pi], [-np.pi, np.pi]]
        }
        a = 7.0
        b = 0.1

        def ishigami(x):
            return np.sin(x[:, 0]) + a * (np.sin(x[:, 1]) ** 2) + b * (x[:, 2] ** 4) * np.sin(x[:, 0])

        if HAS_SALIB:
            param_values = sobol_sample.sample(problem, N, calc_second_order=False, seed=seed)
            Y = ishigami(param_values)
            res = sobol_analyze.analyze(problem, Y, calc_second_order=False, seed=seed)
            return {
                "S1": [float(v) for v in res['S1']],
                "ST": [float(v) for v in res['ST']],
                "N": N,
                "seed": seed,
                "analytical_S1": [0.3138, 0.4424, 0.0],
                "passed_convergence": bool(abs(res['S1'][0] - 0.3138) < 0.15 and abs(res['S1'][1] - 0.4424) < 0.15)
            }
        else:
            return {"error": "SALib no instalado", "passed_convergence": False}


def evaluate_ishigami_benchmark(samples_n: int = 512, seed: int = 42) -> Dict[str, Any]:
    """Función de nivel de módulo para verificación de referencia Ishigami."""
    raw = SobolSensitivityAnalyzer.evaluate_ishigami_benchmark(N=samples_n, seed=seed)
    return {
        "converged": raw.get("passed_convergence", False),
        "benchmark_passed": raw.get("passed_convergence", False),
        "indices": {
            "first_order": raw.get("S1", []),
            "total_order": raw.get("ST", [])
        },
        "raw": raw
    }

