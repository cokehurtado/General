"""Motor de fair value de una pieza concreta.

Combina el base_fair_value del instrumento con el grading de la pieza y produce:
  - fair_value ajustado (condición/caja/papeles)
  - tier de liquidez + intervalo de confianza
  - valor realizable (bid, neto de realizar) — porque no vendes al mid
  - señales contra retail y contra fair value
"""

from __future__ import annotations

from typing import Optional

from .models import Condition, Instrument, LiquidityTier, Listing, PricedPiece
from . import comparables, grading

# Tier de liquidez a partir de comparables/trimestre (mismo criterio que doc 07)
def liquidity_tier(comparables_per_qtr: int) -> LiquidityTier:
    if comparables_per_qtr >= 20:
        return LiquidityTier.A
    if comparables_per_qtr >= 5:
        return LiquidityTier.B
    if comparables_per_qtr >= 1:
        return LiquidityTier.C
    return LiquidityTier.D


# Ancho del intervalo de confianza por tier (± fracción del fair value)
_CI_WIDTH = {
    LiquidityTier.A: 0.06,
    LiquidityTier.B: 0.12,
    LiquidityTier.C: 0.22,
    LiquidityTier.D: 0.35,
}

# Haircut de realización: vendes al bid y pagas por realizar (mientras más ilíquido, más caro salir)
_REALIZATION_HAIRCUT = {
    LiquidityTier.A: 0.04,
    LiquidityTier.B: 0.08,
    LiquidityTier.C: 0.15,
    LiquidityTier.D: 0.25,
}

# Índice de confianza base por tier (se puede penalizar por recencia cuando haya datos reales)
_CONFIDENCE_BASE = {
    LiquidityTier.A: 0.90,
    LiquidityTier.B: 0.75,
    LiquidityTier.C: 0.55,
    LiquidityTier.D: 0.35,
}


def price_piece(instrument: Instrument, listing: Listing,
                sales: Optional["comparables.SalesBook"] = None) -> PricedPiece:
    grade = grading.grade_from_description(listing.condition_raw)
    mult = grading.condition_multiplier(
        grade, listing.has_box, listing.has_papers, listing.polished
    )

    # Baseline calibrado con cierres reales si los hay; si no, valor semilla.
    baseline = instrument.base_fair_value_usd
    calibrated = False
    n_sales = 0
    if sales is not None:
        est = comparables.calibrated_fair_value(sales.for_ref(instrument.ref))
        if est is not None:
            baseline, n_sales = est[0], est[1]
            calibrated = True

    fair_value = baseline * mult

    tier = liquidity_tier(instrument.comparables_per_qtr)
    ci = _CI_WIDTH[tier]
    ci_low = fair_value * (1 - ci)
    ci_high = fair_value * (1 + ci)
    confidence = _CONFIDENCE_BASE[tier]

    realizable = fair_value * (1 - _REALIZATION_HAIRCUT[tier])

    # Señales contra retail (a nivel referencia, full-set/excellent) y contra fair value de la pieza
    premium = None
    below_retail = None
    if instrument.retail_usd:
        premium = baseline / instrument.retail_usd - 1
        below_retail = listing.price_usd < instrument.retail_usd

    below_fv = listing.price_usd < fair_value

    return PricedPiece(
        ref=instrument.ref,
        fair_value=round(fair_value, 2),
        ci_low=round(ci_low, 2),
        ci_high=round(ci_high, 2),
        liquidity_tier=tier,
        confidence_index=confidence,
        realizable_value=round(realizable, 2),
        condition_grade=grade,
        condition_multiplier=round(mult, 4),
        retail_usd=instrument.retail_usd,
        premium_over_retail=round(premium, 4) if premium is not None else None,
        below_retail=below_retail,
        below_fair_value=below_fv,
        calibrated=calibrated,
        n_sales=n_sales,
    )
