"""Motor de arbitraje: edge neto, gates (vetos) y ranking.

Filosofía (doc 07): publicar el spread BRUTO engaña; el motor razona en NETO,
restando internación a Panamá, costo de capital y provisión de riesgo, y
descontando que se vende al bid (realizable), no al mid.
"""

from __future__ import annotations

from typing import Iterable

from .models import Instrument, LiquidityTier, Listing, Opportunity
from . import pricing, provenance
from .costs import ImportCostConfig, landed_cost

# Umbral mínimo de edge neto para recomendar compra
MIN_NET_EDGE = 0.10
# En tier ilíquido (C/D) exigimos un edge mucho mayor para compensar el riesgo de salida
ILLIQUID_MIN_NET_EDGE = 0.25

# Días esperados en inventario por tier (para el costo de capital)
_HOLD_DAYS = {
    LiquidityTier.A: 45,
    LiquidityTier.B: 75,
    LiquidityTier.C: 120,
    LiquidityTier.D: 180,
}

# Señal de "precio demasiado bueno": si el listing está muy por debajo del fair value,
# es red flag de falsificación/fraude (se inyecta al scoring de procedencia).
_TOO_GOOD_RATIO = 0.55   # precio < 55% del fair value


def evaluate(
    instrument: Instrument,
    listing: Listing,
    cfg: ImportCostConfig | None = None,
) -> Opportunity:
    cfg = cfg or ImportCostConfig()
    priced = pricing.price_piece(instrument, listing)

    # Inyecta la señal de precio anómalo al scoring de procedencia
    if listing.price_usd < priced.fair_value * _TOO_GOOD_RATIO:
        listing.signals = {**(listing.signals or {}), "price_too_good_flag": True}
    prov_score, prov_flags = provenance.score_seller(listing)

    hold_days = _HOLD_DAYS[priced.liquidity_tier]
    breakdown = landed_cost(
        buy_price=listing.price_usd,
        value_for_customs=listing.price_usd,
        hold_days=hold_days,
        cfg=cfg,
    )

    # Provisión de riesgo en función de la procedencia (peor procedencia -> más provisión)
    risk_provision = (1 - prov_score / 100.0) * 0.10 * listing.price_usd
    breakdown = {**breakdown, "risk_provision": round(risk_provision, 2)}
    total_extra = breakdown["total"] + risk_provision
    total_cost = listing.price_usd + total_extra

    gross_edge = (priced.fair_value - listing.price_usd) / listing.price_usd
    net_edge = (priced.realizable_value - total_cost) / total_cost

    notes: list[str] = []
    # --- Gates / vetos ---
    if not provenance.is_safe_source(prov_score):
        verdict = "UNSAFE_SOURCE"
        notes.append(
            f"Procedencia {prov_score:.0f} < {provenance.MIN_PROVENANCE:.0f}: "
            f"no comprar sin importar el edge."
        )
    elif priced.liquidity_tier in (LiquidityTier.C, LiquidityTier.D) and net_edge < ILLIQUID_MIN_NET_EDGE:
        verdict = "ILLIQUID"
        notes.append(
            f"Tier {priced.liquidity_tier.value}: edge neto {net_edge:.1%} < "
            f"{ILLIQUID_MIN_NET_EDGE:.0%} requerido para ilíquidos (difícil de salir)."
        )
    elif net_edge < MIN_NET_EDGE:
        verdict = "PASS"
        notes.append(f"Edge neto {net_edge:.1%} < umbral {MIN_NET_EDGE:.0%}.")
    else:
        verdict = "BUY"

    # Señales informativas
    if priced.below_retail:
        notes.append("Bajo retail (MSRP): señal fuerte si el modelo aprecia.")
    if priced.condition_grade.value in ("FAIR", "POOR"):
        notes.append("Condición baja: verificar costo de servicio antes de comprar.")

    # Score compuesto para ranking (solo positivo si es BUY)
    liquidity_factor = {
        LiquidityTier.A: 1.0, LiquidityTier.B: 0.8,
        LiquidityTier.C: 0.5, LiquidityTier.D: 0.3,
    }[priced.liquidity_tier]
    provenance_factor = prov_score / 100.0
    score = 0.0
    if verdict == "BUY":
        score = net_edge * priced.confidence_index * liquidity_factor * provenance_factor

    return Opportunity(
        listing=listing,
        priced=priced,
        gross_edge=round(gross_edge, 4),
        net_edge=round(net_edge, 4),
        landed_cost=round(total_cost, 2),
        cost_breakdown=breakdown,
        provenance_score=round(prov_score, 1),
        provenance_flags=prov_flags,
        verdict=verdict,
        score=round(score, 5),
        notes=notes,
    )


def scan(
    instruments_by_ref: dict[str, Instrument],
    listings: Iterable[Listing],
    cfg: ImportCostConfig | None = None,
) -> list[Opportunity]:
    """Evalúa todos los listings con instrumento conocido y los rankea.

    BUY primero (por score desc); luego el resto por edge neto desc.
    """
    opps: list[Opportunity] = []
    for lst in listings:
        inst = instruments_by_ref.get(lst.ref)
        if inst is None:
            continue  # ref no está en el universo curado
        opps.append(evaluate(inst, lst, cfg))

    opps.sort(key=lambda o: (o.verdict != "BUY", -o.score, -o.net_edge))
    return opps
