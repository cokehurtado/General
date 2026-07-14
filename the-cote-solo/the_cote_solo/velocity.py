"""Factibilidad de venta: tiempo estimado de venta y su impacto en flujo de caja.

Insight quant: el arbitraje no se decide por el spread absoluto sino por el
retorno POR UNIDAD DE TIEMPO. Un edge de 20% en 180 días es peor para el flujo
de caja que uno de 12% en 30 días, porque el capital inmovilizado no se recicla.

Este módulo estima los días esperados de venta y de ahí se derivan:
  - retorno anualizado (la métrica de decisión real)
  - velocidad de capital (vueltas/año)

El tiempo estimado también alimenta el costo de capital (mismo número en todo
el motor). Todos los factores son heurísticos y calibrables con tus cierres
reales — cada venta que registres en el libro personal afina esta curva.
"""

from __future__ import annotations

from typing import Optional

from .models import Condition, LiquidityTier

# Días medianos para vender AL PRECIO REALIZABLE (bid), por tier de liquidez.
BASE_DAYS_TO_SELL = {
    LiquidityTier.A: 45,
    LiquidityTier.B: 90,
    LiquidityTier.C: 150,
    LiquidityTier.D: 240,
}

# Piso de días: evita anualizaciones explosivas/engañosas en ventas muy rápidas.
MIN_DAYS_FLOOR = 21

# La condición afecta la velocidad: full set / nuevo se vende más rápido.
_CONDITION_SPEED = {
    Condition.NEW_UNWORN: 0.85,
    Condition.MINT: 0.90,
    Condition.EXCELLENT: 1.00,
    Condition.VERY_GOOD: 1.05,
    Condition.GOOD: 1.15,
    Condition.FAIR: 1.35,
    Condition.POOR: 1.60,
}

# Confianza en la estimación de tiempo (más ilíquido = más incierto el tiempo).
_TIME_CONFIDENCE = {
    LiquidityTier.A: 0.85,
    LiquidityTier.B: 0.65,
    LiquidityTier.C: 0.45,
    LiquidityTier.D: 0.30,
}


def expected_days_to_sell(
    tier: LiquidityTier,
    grade: Condition,
    premium_over_retail: Optional[float] = None,
    full_set: bool = True,
) -> tuple[int, float]:
    """Devuelve (días_esperados, confianza_en_el_tiempo 0..1)."""
    days = float(BASE_DAYS_TO_SELL[tier])
    days *= _CONDITION_SPEED.get(grade, 1.0)

    # Demanda: modelos que cotizan muy sobre retail están 'calientes' (venden más
    # rápido); los que cotizan bajo retail suelen ser modelos suaves (más lentos).
    if premium_over_retail is not None:
        if premium_over_retail > 0.30:
            days *= 0.85
        elif premium_over_retail < 0.0:
            days *= 1.15

    if not full_set:
        days *= 1.10  # sin caja/papeles cuesta un poco más colocar

    days = max(MIN_DAYS_FLOOR, round(days))
    return int(days), _TIME_CONFIDENCE[tier]


def annualized_return(net_edge: float, days_to_sell: int) -> float:
    """Convierte un edge neto absoluto en retorno anualizado compuesto.

    (1 + edge)^(365/días) − 1. Guarda contra edge <= -100%.
    """
    if net_edge <= -1.0:
        return -1.0
    days = max(1, days_to_sell)
    r = (1.0 + net_edge) ** (365.0 / days) - 1.0
    # Techo de cordura: anualizar edges enormes (típico de precios fraudulentos)
    # produce números sin sentido. Se cap a 2000%/año para display y ranking.
    return min(r, 20.0)


def capital_turns_per_year(days_to_sell: int) -> float:
    """Cuántas veces se recicla el capital en un año (velocidad de capital)."""
    return 365.0 / max(1, days_to_sell)
