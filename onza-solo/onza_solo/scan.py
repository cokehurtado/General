"""CLI del scanner: carga fixtures, evalúa arbitraje e imprime un reporte.

Uso:
    python -m onza_solo.scan                 # usa fixtures/listings.json + config default
    python -m onza_solo.scan --zlc           # usa config de reexportación ZLC (arancel/ITBMS ~0)
    python -m onza_solo.scan path/al.json    # otro archivo de listings
"""

from __future__ import annotations

import json
import os
import sys

from .arbitrage import scan
from .costs import ImportCostConfig
from .models import Listing
from .universe import UNIVERSE

_VERDICT_MARK = {
    "BUY": "✅ BUY",
    "PASS": "· PASS",
    "ILLIQUID": "⚠ ILLIQUID",
    "UNSAFE_SOURCE": "⛔ UNSAFE",
}


def _load_listings(path: str) -> list[Listing]:
    with open(path, "r", encoding="utf-8") as f:
        rows = json.load(f)
    return [Listing(**r) for r in rows]


def _fmt_usd(x: float) -> str:
    return f"${x:,.0f}"


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    flags = {a for a in argv if a.startswith("--")}

    default_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "listings.json")
    path = args[0] if args else default_path
    cfg = ImportCostConfig.zlc_reexport() if "--zlc" in flags else ImportCostConfig()

    listings = _load_listings(path)
    opps = scan(UNIVERSE, listings, cfg)

    scenario = "ZLC reexportación (arancel/ITBMS ~0)" if "--zlc" in flags else "importación uso propio"
    print(f"\nONZA Solo · scanner de arbitraje  —  escenario de costos: {scenario}")
    print(f"Universo: {len(UNIVERSE)} refs · Listings evaluados: {len(opps)}\n")
    print("=" * 92)

    for o in opps:
        inst = UNIVERSE[o.listing.ref]
        p = o.priced
        mark = _VERDICT_MARK.get(o.verdict, o.verdict)
        print(f"{mark:<14} {inst.brand} {inst.name}  [{inst.ref}]   src={o.listing.source}")
        print(
            f"   precio {_fmt_usd(o.listing.price_usd)}  |  fair value {_fmt_usd(p.fair_value)} "
            f"(±{(p.ci_high - p.fair_value)/p.fair_value:.0%}, tier {p.liquidity_tier.value})  |  "
            f"grado {p.condition_grade.value} (x{p.condition_multiplier})"
        )
        retail_txt = "—"
        if p.retail_usd:
            retail_txt = f"{_fmt_usd(p.retail_usd)} ({'BAJO retail' if p.below_retail else 'sobre retail'}, prem {p.premium_over_retail:+.0%})"
        print(
            f"   retail {retail_txt}  |  edge bruto {o.gross_edge:+.1%}  →  "
            f"edge NETO {o.net_edge:+.1%}  |  procedencia {o.provenance_score:.0f}/100"
        )
        cb = o.cost_breakdown
        print(
            f"   costo landed {_fmt_usd(o.landed_cost)}  "
            f"(flete {_fmt_usd(cb['shipping'])}, seguro {_fmt_usd(cb['insurance'])}, "
            f"arancel {_fmt_usd(cb['duty'])}, ITBMS {_fmt_usd(cb['itbms'])}, "
            f"capital {_fmt_usd(cb['capital_cost'])}, riesgo {_fmt_usd(cb['risk_provision'])})"
        )
        for flag in o.provenance_flags:
            print(f"     ⚑ {flag}")
        for note in o.notes:
            print(f"     • {note}")
        print("-" * 92)

    buys = [o for o in opps if o.verdict == "BUY"]
    print(f"\nResumen: {len(buys)} señal(es) de compra de {len(opps)} listings.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
