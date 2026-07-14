"""Modelos de dominio. Mismo grafo que el diseño grande (instruments/listings),
reducido a lo que necesita el terminal personal."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Condition(str, Enum):
    """Escala canónica de condición (de mejor a peor). El grading normaliza
    las descripciones libres de las fuentes a uno de estos grados."""

    NEW_UNWORN = "NEW_UNWORN"      # nuevo, sin uso, stickers/garantía vigente
    MINT = "MINT"                  # usado pero sin desgaste visible
    EXCELLENT = "EXCELLENT"        # desgaste leve — baseline de valuación
    VERY_GOOD = "VERY_GOOD"        # desgaste visible, marcas menores
    GOOD = "GOOD"                  # desgaste notorio, rayas
    FAIR = "FAIR"                  # desgaste fuerte, puede requerir servicio
    POOR = "POOR"                  # dañado / incompleto

    # orden para comparaciones
    @property
    def rank(self) -> int:
        order = [
            Condition.POOR, Condition.FAIR, Condition.GOOD, Condition.VERY_GOOD,
            Condition.EXCELLENT, Condition.MINT, Condition.NEW_UNWORN,
        ]
        return order.index(self)


class LiquidityTier(str, Enum):
    A = "A"  # líquido
    B = "B"  # semi-líquido
    C = "C"  # ilíquido
    D = "D"  # único/raro


@dataclass(frozen=True)
class Instrument:
    """El 'ticker': un modelo canónico de reloj."""

    ref: str                      # número de referencia canónico, ej. "126710BLRO"
    brand: str
    family: str
    name: str
    retail_usd: Optional[float]   # MSRP conocido (None si descatalogado sin retail)
    base_fair_value_usd: float    # fair value del secundario en condición EXCELLENT + full set
    comparables_per_qtr: int      # densidad de datos (gobierna el tier de liquidez)
    category: str = "watch"


@dataclass
class Listing:
    """Una publicación/oferta concreta de una pieza física."""

    id: str
    ref: str
    source: str                   # chrono24 | auction | watchcharts | local | ...
    price_usd: float
    condition_raw: str            # texto libre de la fuente
    has_box: bool
    has_papers: bool
    polished: Optional[bool] = None   # None = desconocido
    year: Optional[int] = None
    seller_name: str = "unknown"
    seller_type: str = "unknown"      # dealer_verified | dealer | private | unknown
    region: str = "unknown"           # US | EU | LATAM | PA | ...
    url: str = ""
    # señales para el scoring de procedencia
    signals: dict = field(default_factory=dict)


@dataclass
class PricedPiece:
    """Resultado de valuar una pieza concreta (listing) contra su instrumento."""

    ref: str
    fair_value: float             # ajustado por condición/caja/papeles de ESTA pieza
    ci_low: float
    ci_high: float
    liquidity_tier: LiquidityTier
    confidence_index: float       # 0..1
    realizable_value: float       # lo que realmente recuperas al vender (bid, neto de realizar)
    condition_grade: Condition
    condition_multiplier: float   # factor total aplicado sobre base_fair_value
    retail_usd: Optional[float]
    premium_over_retail: Optional[float]   # fair_value_fullset / retail - 1
    below_retail: Optional[bool]           # listing.price < retail
    below_fair_value: bool                 # listing.price < fair_value de la pieza
    calibrated: bool = False               # baseline vino de cierres reales, no del seed
    n_sales: int = 0                       # cuántos cierres calibraron el baseline


@dataclass
class Opportunity:
    """Evaluación de arbitraje de un listing."""

    listing: Listing
    priced: PricedPiece
    gross_edge: float             # (fair_value - price) / price
    net_edge: float               # (realizable - landed_cost) / landed_cost
    landed_cost: float
    cost_breakdown: dict
    provenance_score: float
    provenance_flags: list
    verdict: str                  # BUY | PASS | ILLIQUID | SLOW_TURN | UNSAFE_SOURCE
    score: float                  # ranking compuesto (anualizado)
    # Factibilidad de venta / flujo de caja
    days_to_sell: int             # tiempo estimado de venta
    time_confidence: float        # confianza en esa estimación (0..1)
    annualized_edge: float        # (1 + net_edge)^(365/días) - 1  ← métrica de decisión
    capital_turns_per_year: float # velocidad de capital (365/días)
    notes: list = field(default_factory=list)
