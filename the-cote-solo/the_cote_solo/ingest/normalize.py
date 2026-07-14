"""Normalización: RawRecord.payload (crudo por fuente) -> Listing del motor.

Mantiene el crudo intacto en el raw store; esto solo produce el objeto que el
motor entiende. El grading de condición lo hace el motor aguas abajo a partir
de `condition_raw`.
"""

from __future__ import annotations

from typing import Optional

from ..models import Listing


def _to_bool(v, default=False) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.strip().lower() in ("1", "true", "yes", "si", "sí", "y")
    return default


def payload_to_listing(source: str, external_id: str, payload: dict) -> Optional[Listing]:
    """Convierte un payload normalizado a Listing. Devuelve None si falta lo esencial.

    Espera (con tolerancia) las llaves: ref, price_usd|hammer_usd, condition,
    box|has_box, papers|has_papers, polished, year, seller_name, seller_type,
    region, url, signals.
    """
    ref = payload.get("ref")
    price = payload.get("price_usd", payload.get("hammer_usd"))
    if not ref or price is None:
        return None

    return Listing(
        id=f"{source}:{external_id}",
        ref=str(ref),
        source=source,
        price_usd=float(price),
        condition_raw=str(payload.get("condition", payload.get("condition_raw", ""))),
        has_box=_to_bool(payload.get("box", payload.get("has_box")), default=False),
        has_papers=_to_bool(payload.get("papers", payload.get("has_papers")), default=False),
        polished=payload.get("polished"),
        year=payload.get("year"),
        seller_name=str(payload.get("seller_name", "unknown")),
        seller_type=str(payload.get("seller_type", "unknown")),
        region=str(payload.get("region", "unknown")),
        url=str(payload.get("url", "")),
        signals=payload.get("signals", {}) or {},
    )
