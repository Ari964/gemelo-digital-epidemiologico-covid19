import math
import os
import json
import hashlib
import numpy as np
from typing import List, Dict, Any, Tuple, Optional

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return max(1.0, R * c)

class MobilityEngine:
    """
    Motor de Movilidad Inter-Condados para los 47 condados de Kenia.
    Clasificación rigurosa de fuentes:
    - ESTIMATED: Derivado de distancias geodésicas, gravedad y factores de conectividad.
                 No representa observaciones directas ni trazas GPS de Meta.
    - SYNTHETIC: Generador gravitacional de prueba no calibrado.
    - EMPIRICAL: Requiere dataset validado en contenido, dimensiones (47x47),
                 metadatos de origen e integridad; si es inválido o no existe,
                 se revierte a ESTIMATED con justificación explícita.
    """
    def __init__(
        self,
        counties: List[Dict[str, Any]],
        use_empirical: bool = False,
        empirical_file_path: Optional[str] = None,
        od_matrix_file: Optional[str] = None
    ):
        self.counties = counties
        self.n_counties = len(counties)
        
        target_path = empirical_file_path or od_matrix_file
        default_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/empirical_mobility_od_matrix.json"))
        self.empirical_file_path = target_path or default_path
        
        self.use_empirical = False
        self.source_type = "ESTIMATED"
        self.empirical_rejection_reason: Optional[str] = None
        loaded_matrix = None

        if use_empirical:
            if not os.path.exists(self.empirical_file_path):
                self.empirical_rejection_reason = (
                    f"Dataset de movilidad empírica no encontrado en '{self.empirical_file_path}'. "
                    "Se revierte a matriz gravitacional estimada."
                )
            elif os.path.getsize(self.empirical_file_path) == 0:
                self.empirical_rejection_reason = (
                    "Archivo de movilidad empírica vacío (0 bytes). "
                    "Se revierte a matriz gravitacional estimada."
                )
            else:
                try:
                    with open(self.empirical_file_path, "r", encoding="utf-8") as f:
                        raw_data = json.load(f)

                    matrix_data = raw_data.get("matrix") or raw_data.get("od_matrix")
                    source_doc = raw_data.get("source") or raw_data.get("source_name")
                    unit = raw_data.get("unit")
                    period = raw_data.get("period") or raw_data.get("period_start")

                    if matrix_data is None:
                        self.empirical_rejection_reason = "El archivo no contiene la clave 'matrix' u 'od_matrix'."
                    elif not source_doc or not str(source_doc).strip():
                        self.empirical_rejection_reason = "El archivo carece de documentación de origen ('source' o 'source_name')."
                    else:
                        mat_arr = np.array(matrix_data, dtype=float)
                        if mat_arr.shape != (self.n_counties, self.n_counties):
                            self.empirical_rejection_reason = (
                                f"Dimensiones incompatibles: esperadas ({self.n_counties}, {self.n_counties}), "
                                f"obtenidas {mat_arr.shape}."
                            )
                        elif not np.all(np.isfinite(mat_arr)):
                            self.empirical_rejection_reason = "La matriz contiene valores nulos, infinitos o no numéricos."
                        elif np.any(mat_arr < 0.0):
                            self.empirical_rejection_reason = "La matriz contiene flujos negativos."
                        else:
                            # Comprobación de integridad hash si se declara
                            declared_hash = raw_data.get("sha256") or raw_data.get("content_sha256")
                            if declared_hash:
                                with open(self.empirical_file_path, "rb") as f_bytes:
                                    calc_hash = hashlib.sha256(f_bytes.read()).hexdigest()
                                if calc_hash.lower() != declared_hash.lower():
                                    self.empirical_rejection_reason = (
                                        f"Fallo de integridad criptográfica: hash calculado ({calc_hash[:12]}...) "
                                        f"difiere del declarado ({declared_hash[:12]}...)."
                                    )

                            if not self.empirical_rejection_reason:
                                # Normalización por filas: cada fila suma 1.0
                                row_sums = mat_arr.sum(axis=1, keepdims=True)
                                row_sums[row_sums == 0] = 1.0
                                loaded_matrix = mat_arr / row_sums
                                self.use_empirical = True
                                self.source_type = "EMPIRICAL"
                except Exception as e:
                    self.empirical_rejection_reason = f"Error al procesar archivo de movilidad empírica: {str(e)}"

        if self.use_empirical and loaded_matrix is not None:
            self.mobility_matrix = loaded_matrix
            self._distance_matrix = self._compute_distance_matrix()
        else:
            self.use_empirical = False
            self.source_type = "ESTIMATED"
            self._distance_matrix = self._compute_distance_matrix()
            self.mobility_matrix = self._build_mobility_matrix()

        self.is_synthetic = False

    def _compute_distance_matrix(self) -> np.ndarray:
        dist = np.zeros((self.n_counties, self.n_counties))
        for i in range(self.n_counties):
            for j in range(self.n_counties):
                if i == j:
                    dist[i, j] = 0.0
                else:
                    dist[i, j] = haversine(
                        self.counties[i]["latitude"], self.counties[i]["longitude"],
                        self.counties[j]["latitude"], self.counties[j]["longitude"]
                    )
        return dist

    def _build_mobility_matrix(self) -> np.ndarray:
        """
        Construye la matriz de transición de movilidad M[i, j]
        donde M[i, j] es la fracción de contacto de un residente del condado i en el condado j.
        """
        M = np.zeros((self.n_counties, self.n_counties))
        
        for i in range(self.n_counties):
            pop_i = self.counties[i]["population_2019"]
            for j in range(self.n_counties):
                if i == j:
                    continue
                pop_j = self.counties[j]["population_2019"]
                d = self._distance_matrix[i, j]
                
                # Corredores viales principales: A104 Nairobi-Mombasa, etc.
                corridor_factor = 1.0
                if (self.counties[i]["code"] == 47 and self.counties[j]["code"] == 1) or \
                   (self.counties[i]["code"] == 1 and self.counties[j]["code"] == 47):
                    corridor_factor = 2.8
                elif self.counties[j]["code"] == 47:
                    corridor_factor = 2.0
                elif self.counties[j]["code"] in [1, 32, 42, 27]:
                    corridor_factor = 1.5
                
                flow = (pop_j ** 0.6) / (d ** 1.35) * corridor_factor
                M[i, j] = flow

        for i in range(self.n_counties):
            total_outflow = np.sum(M[i, :])
            if total_outflow > 0:
                inter_county_rate = 0.08
                M[i, :] = (M[i, :] / total_outflow) * inter_county_rate
                M[i, i] = 1.0 - inter_county_rate
            else:
                M[i, i] = 1.0

        return M

    def get_mobility_info(self) -> Dict[str, Any]:
        warning_msg = None
        if self.empirical_rejection_reason:
            warning_msg = (
                f"Opción empírica deshabilitada: {self.empirical_rejection_reason} "
                "Se aplicó la matriz gravitacional estimada (ESTIMATED)."
            )
        elif self.source_type == "ESTIMATED":
            warning_msg = "Matriz de movilidad estimada a partir de población, distancia y conectividad. No representa flujos observados directamente."

        return {
            "source": "Matriz de movilidad OD empírica validada" if self.use_empirical else "Matriz estimada gravitacional (A104)",
            "source_type": self.source_type,
            "is_synthetic": self.is_synthetic,
            "empirical_available": self.use_empirical,
            "disclaimer": "Matriz de movilidad empírica validada" if self.use_empirical else "Matriz estimada a partir de población y distancia. No representa flujos observados directamente.",
            "warning": warning_msg,
            "counties_count": self.n_counties,
            "mean_outflow_rate": float(1.0 - np.mean(np.diag(self.mobility_matrix)))
        }
