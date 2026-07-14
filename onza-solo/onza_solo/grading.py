"""Clasificación de calidad (grading) y su efecto en el precio.

Dos responsabilidades:
  1. Normalizar descripciones libres de las fuentes -> grado canónico Condition.
  2. Traducir grado + caja/papeles/pulido -> multiplicador sobre el base_fair_value.

Todos los factores son HEURÍSTICOS y CALIBRABLES. El objetivo del libro personal
es reemplazarlos por valores aprendidos de cierres reales. Punto de extensión:
un grader por visión (foto -> grado) enchufa en `grade_from_description`.
"""

from __future__ import annotations

from typing import Optional

from .models import Condition

# --- Multiplicadores de condición (baseline = EXCELLENT = 1.00) -----------------
# Relativos a una pieza EXCELLENT con full set (caja + papeles).
CONDITION_MULTIPLIER: dict[Condition, float] = {
    Condition.NEW_UNWORN: 1.08,
    Condition.MINT: 1.03,
    Condition.EXCELLENT: 1.00,
    Condition.VERY_GOOD: 0.93,
    Condition.GOOD: 0.86,
    Condition.FAIR: 0.75,
    Condition.POOR: 0.60,
}

# --- Ajustes por completitud (el baseline YA incluye full set) ------------------
NO_PAPERS_ADJ = -0.06   # los papeles pesan más que la caja en el mercado real
NO_BOX_ADJ = -0.02
POLISHED_ADJ = -0.04    # pulido afecta originalidad

# --- Normalización de texto libre -> grado --------------------------------------
# Palabras clave por grado, evaluadas de mejor a peor; primer match gana.
_KEYWORDS: list[tuple[Condition, tuple[str, ...]]] = [
    (Condition.NEW_UNWORN, ("new old stock", "nos", "unworn", "brand new", "sin uso",
                            "nuevo", "stickers", "full stickers", "unused")),
    (Condition.MINT, ("mint", "like new", "as new", "como nuevo", "impecable", "flawless")),
    (Condition.EXCELLENT, ("excellent", "excelente", "very good condition", "great condition",
                           "muy buen estado")),
    (Condition.VERY_GOOD, ("very good", "good plus", "light wear", "desgaste leve",
                           "minor wear", "buen estado")),
    (Condition.GOOD, ("good", "used", "usado", "wear", "scratches", "rayas", "worn")),
    (Condition.FAIR, ("fair", "regular", "heavy wear", "needs service", "requiere servicio",
                      "desgaste fuerte", "aged")),
    (Condition.POOR, ("poor", "damaged", "dañado", "for parts", "repuestos", "broken", "roto")),
]


def grade_from_description(text: str) -> Condition:
    """Normaliza una descripción libre a un grado canónico.

    Conservador: ante ambigüedad total, asume GOOD (no premia lo que no se puede
    verificar). Reemplazable por un grader de visión que reciba fotos.
    """
    t = (text or "").lower()
    for grade, kws in _KEYWORDS:
        if any(kw in t for kw in kws):
            return grade
    return Condition.GOOD


def condition_multiplier(
    grade: Condition,
    has_box: bool,
    has_papers: bool,
    polished: Optional[bool] = None,
) -> float:
    """Factor total sobre base_fair_value para una pieza concreta.

    Nunca baja de un piso razonable para evitar valores absurdos por acumulación.
    """
    m = CONDITION_MULTIPLIER[grade]
    if not has_papers:
        m += NO_PAPERS_ADJ
    if not has_box:
        m += NO_BOX_ADJ
    if polished is True:
        m += POLISHED_ADJ
    return max(m, 0.40)


def is_full_set(has_box: bool, has_papers: bool) -> bool:
    return has_box and has_papers
