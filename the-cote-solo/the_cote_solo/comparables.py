"""Calibración del fair value con cierres reales (cierra el loop de ingesta → pricing).

El motor semilla usa `instrument.base_fair_value_usd` (valores ilustrativos). Este
módulo reemplaza esa magnitud por una estimación **derivada de cierres reales**
(subastas, eBay sold, ventas propias) siguiendo la metodología de doc 07:

  1. Normaliza cada cierre a la condición baseline (EXCELLENT + full set) dividiendo
     por su multiplicador de condición.
  2. Pondera por recencia (decaimiento exponencial) y calidad de la fuente.
  3. Promedia ponderado → fair value baseline calibrado.

Si no hay suficientes cierres para una referencia, devuelve None y el motor cae al
valor semilla. Todo es transparente y calibrable.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from . import grading
from .models import Condition

# Calidad del dato por fuente (mismo criterio que doc 05/07)
SOURCE_QUALITY = {
    "own_close": 1.0,     # cierre propio — el dato de oro
    "auction": 0.8,       # resultado de subasta público
    "ebay_sold": 0.7,     # cierre en eBay
    "listed_delist": 0.4, # precio de lista al desaparecer (inferido)
    "listed_active": 0.3, # lista activa (oferta, no cierre)
}

RECENCY_HALF_LIFE_DAYS = 120.0   # un cierre pierde la mitad de su peso cada ~4 meses
MIN_SALES_TO_CALIBRATE = 2


@dataclass
class Sale:
    """Un cierre real, ya normalizado a precio-baseline."""

    ref: str
    baseline_price: float   # precio llevado a EXCELLENT + full set
    quality: float          # peso de calidad de fuente (0..1)
    age_days: float


def sale_from_record(payload: dict, source: str = "auction",
                     now: Optional[datetime] = None) -> Optional[Sale]:
    """Convierte un payload de cierre ingestado en un Sale normalizado."""
    ref = payload.get("ref")
    price = payload.get("hammer_usd", payload.get("price_usd"))
    if not ref or price is None:
        return None

    grade = grading.grade_from_description(str(payload.get("condition", "")))
    has_box = bool(payload.get("box", payload.get("has_box", False)))
    has_papers = bool(payload.get("papers", payload.get("has_papers", False)))
    mult = grading.condition_multiplier(grade, has_box, has_papers)
    baseline_price = float(price) / mult if mult else float(price)

    age = 0.0
    sold = payload.get("sold_date")
    if sold:
        try:
            d = datetime.fromisoformat(str(sold)).replace(tzinfo=timezone.utc)
            ref_now = now or datetime.now(timezone.utc)
            age = max(0.0, (ref_now - d).days)
        except ValueError:
            age = 0.0

    return Sale(ref=str(ref), baseline_price=baseline_price,
                quality=SOURCE_QUALITY.get(source, 0.5), age_days=age)


class SalesBook:
    """Registro de cierres por referencia, listo para calibrar el pricing."""

    def __init__(self):
        self._by_ref: dict[str, list[Sale]] = {}

    def add(self, sale: Sale) -> None:
        self._by_ref.setdefault(sale.ref, []).append(sale)

    def add_records(self, records, source: str = "auction",
                    now: Optional[datetime] = None) -> int:
        n = 0
        for r in records:
            payload = r["payload"] if isinstance(r, dict) and "payload" in r else r
            s = sale_from_record(payload, source=source, now=now)
            if s:
                self.add(s); n += 1
        return n

    def for_ref(self, ref: str) -> list[Sale]:
        return self._by_ref.get(ref, [])

    def refs(self) -> list[str]:
        return list(self._by_ref.keys())


def calibrated_fair_value(sales: list[Sale],
                          half_life: float = RECENCY_HALF_LIFE_DAYS,
                          min_n: int = MIN_SALES_TO_CALIBRATE) -> Optional[tuple[float, int]]:
    """Fair value baseline (EXCELLENT + full set) ponderado por recencia y calidad.

    Devuelve (fair_value, n_cierres) o None si no hay datos suficientes.
    """
    if len(sales) < min_n:
        return None
    num = den = 0.0
    for s in sales:
        w = (0.5 ** (s.age_days / half_life)) * s.quality
        num += w * s.baseline_price
        den += w
    if den == 0:
        return None
    return num / den, len(sales)
