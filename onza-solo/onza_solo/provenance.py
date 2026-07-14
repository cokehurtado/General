"""Scoring de procedencia / confiabilidad del proveedor.

Objetivo: asegurar procedencia segura. Produce un score 0..100 y una lista de
flags. Tiene poder de VETO: bajo MIN_PROVENANCE no se recomienda comprar sin
importar el edge (una falsificación o un fraude borra cualquier spread).

Todos los pesos son calibrables. Señales esperadas en Listing.signals (todas
opcionales; ausencia = incertidumbre, no se premia):
  - platform_verified: bool     vendedor verificado por la plataforma
  - account_age_months: int
  - completed_sales: int
  - rating: float               0..5
  - has_serial: bool            comparte número de serie
  - real_photos: bool           fotos propias (no de catálogo/robadas)
  - has_service_history: bool
  - price_too_good_flag: bool    precio anómalamente bajo (lo setea el motor)
"""

from __future__ import annotations

from .models import Listing

MIN_PROVENANCE = 55.0   # umbral de veto

# Puntajes base por tipo de vendedor
_SELLER_TYPE_BASE = {
    "dealer_verified": 70.0,
    "dealer": 55.0,
    "private": 40.0,
    "unknown": 30.0,
}


def score_seller(listing: Listing) -> tuple[float, list[str]]:
    """Devuelve (score 0..100, flags)."""
    s = listing.signals or {}
    flags: list[str] = []

    score = _SELLER_TYPE_BASE.get(listing.seller_type, 30.0)

    # Reputación
    if s.get("platform_verified"):
        score += 8
    else:
        flags.append("sin verificación de plataforma")

    age = s.get("account_age_months")
    if isinstance(age, (int, float)):
        if age >= 24:
            score += 6
        elif age < 3:
            score -= 8
            flags.append("cuenta muy nueva (<3 meses)")

    sales = s.get("completed_sales")
    if isinstance(sales, (int, float)):
        if sales >= 50:
            score += 8
        elif sales == 0:
            score -= 6
            flags.append("sin historial de ventas")

    rating = s.get("rating")
    if isinstance(rating, (int, float)):
        if rating >= 4.7:
            score += 6
        elif rating < 4.0:
            score -= 8
            flags.append(f"rating bajo ({rating})")

    # Trazabilidad de la pieza
    if s.get("has_serial"):
        score += 6
    else:
        flags.append("no comparte número de serie")

    if s.get("real_photos"):
        score += 6
    else:
        score -= 6
        flags.append("sin fotos propias verificables")

    if s.get("has_service_history"):
        score += 3

    # Señal de fraude clásica: precio demasiado bueno para ser verdad
    if s.get("price_too_good_flag"):
        score -= 20
        flags.append("precio anómalamente bajo (posible falsificación/fraude)")

    score = max(0.0, min(100.0, score))
    return score, flags


def is_safe_source(score: float) -> bool:
    return score >= MIN_PROVENANCE
