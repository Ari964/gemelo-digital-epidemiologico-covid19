"""
Módulo de resolución y trazabilidad de procedencia formal de datos (CRISP-DM Fase 2 y 5).
Define la jerarquía canónica de 4 niveles:
SYNTHETIC > UNKNOWN > ESTIMATED > EMPIRICAL

Reglas de combinación estricta:
1. Cualquier combinación que incluya al menos un componente SYNTHETIC -> SYNTHETIC
2. Cualquier combinación que incluya UNKNOWN (y ningún SYNTHETIC) -> UNKNOWN
3. Cualquier combinación con ESTIMATED (y sin SYNTHETIC ni UNKNOWN) -> ESTIMATED
4. Todos los componentes requeridos verificados como EMPIRICAL -> EMPIRICAL

Estados de ingestión:
- 'PENDING', 'COMPLETED', 'FAILED': Estados del ciclo de vida del proceso de ingestión ETL,
  conceptualmente independientes de la categoría de procedencia epistémica.
"""
from typing import Dict, Tuple, List, Union


def resolve_composite_provenance(components: Union[Dict[str, str], List[str]]) -> Tuple[str, bool, bool]:
    """
    Evalúa la procedencia por componentes y devuelve la tupla canónica:
    (global_source_type: str, is_synthetic: bool, is_demo: bool)
    
    Garantiza:
    - Una etiqueta global nunca oculta un componente UNKNOWN bajo ESTIMATED o EMPIRICAL.
    - Los datos sintéticos siempre contaminan el conjunto hacia SYNTHETIC (is_synthetic=True).
    - Un archivo real de procedencia desconocida NUNCA se reclasifica automáticamente como SYNTHETIC.
    """
    if isinstance(components, dict):
        sources = list(components.values())
    else:
        sources = list(components)

    if not sources:
        return "UNKNOWN", False, True

    norm_sources = [str(s).upper().strip() for s in sources]

    if "SYNTHETIC" in norm_sources:
        return "SYNTHETIC", True, True
    if "UNKNOWN" in norm_sources:
        return "UNKNOWN", False, True
    if "ESTIMATED" in norm_sources:
        return "ESTIMATED", False, True
    if all(s == "EMPIRICAL" for s in norm_sources):
        return "EMPIRICAL", False, False

    # Por defecto ante valores no reconocidos
    return "UNKNOWN", False, True
