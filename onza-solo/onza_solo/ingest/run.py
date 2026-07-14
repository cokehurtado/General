"""CLI de ingesta: demuestra la vía híbrida end-to-end, sin red ni API key.

    python -m onza_solo.ingest.run
        Corre el scheduler sobre las fuentes limpias habilitadas (subastas),
        guarda los cierres en el raw store y reporta. Muestra el gate de los
        sitios protegidos (apagados).

    python -m onza_solo.ingest.run --paste "Rolex 124270 Explorer, USD 6300, full set, 2023"
        Ingesta 'pega-el-texto': extrae los campos del anuncio, lo pasa por el
        motor de arbitraje y muestra el veredicto con todas las variables.

    Flags: --zlc (escenario de costos ZLC para el arbitraje del deal pegado).
"""

from __future__ import annotations

import sys

from ..arbitrage import evaluate
from ..costs import ImportCostConfig
from ..universe import UNIVERSE
from .normalize import payload_to_listing
from .raw_store import RawStore
from .scheduler import Scheduler
from .sources.auction_feed import AuctionResultsSource
from .sources.paste_source import PasteSource
from .sources.protected import Chrono24Source, WatchChartsSource


def _run_scheduled() -> None:
    store = RawStore(":memory:")
    sched = Scheduler(store)
    sources = [AuctionResultsSource(), Chrono24Source(), WatchChartsSource()]

    print("\nONZA Solo · ingesta automatizada (tick del scheduler)\n" + "=" * 74)
    for rep in sched.run_all(sources):
        if rep.ok:
            print(f"✓ {rep.source:<18} nuevos {rep.new}  cambiados {rep.changed}  "
                  f"sin cambio {rep.unchanged}")
        else:
            print(f"· {rep.source:<18} omitida — {rep.skipped_reason}")

    sales = store.count("sale")
    refs = sorted({r['payload'].get('ref') for r in store.records('sale')})
    print("-" * 74)
    print(f"{sales} precios de cierre en el raw store (record_type='sale').")
    print(f"Calibrarían el fair value de: {', '.join(str(x) for x in refs)}")
    print("(Cablear estos cierres al motor de pricing es el paso siguiente documentado.)\n")
    store.close()


def _run_paste(text: str, cfg: ImportCostConfig) -> None:
    paste = PasteSource()
    # En un deal real de fuente informal, completa a mano lo que no viene en el texto:
    rec = paste.ingest_text(
        text,
        seller_type="dealer",
        region="LATAM",
        signals={"platform_verified": False, "account_age_months": 18,
                 "completed_sales": 25, "has_serial": True, "real_photos": True},
    )
    print("\nONZA Solo · ingesta 'pega-el-texto'\n" + "=" * 74)
    print("Campos extraídos:")
    for k, v in rec.payload.items():
        if k == "condition_raw":
            continue
        print(f"   {k}: {v}")

    listing = payload_to_listing(rec.source, rec.external_id, rec.payload)
    if listing is None:
        print("\n⚠ No se pudo extraer ref y/o precio. Corrige el texto o pasa overrides.\n")
        return

    inst = UNIVERSE.get(listing.ref)
    if inst is None:
        print(f"\n⚠ Ref {listing.ref} no está en el universo curado — agrégala a universe.py.\n")
        return

    o = evaluate(inst, listing, cfg)
    print(f"\n→ {inst.brand} {inst.name} [{inst.ref}]  precio {listing.price_usd:,.0f}")
    print(f"   VEREDICTO: {o.verdict}")
    print(f"   spread bruto {o.gross_edge:+.1%}  →  spread neto {o.net_edge:+.1%}")
    print(f"   ~{o.days_to_sell}d a venta  →  anualizado {o.annualized_edge:+.0%}  "
          f"|  {o.capital_turns_per_year:.1f} vueltas/año  |  procedencia {o.provenance_score:.0f}/100")
    for note in o.notes:
        print(f"     • {note}")
    print()


def main(argv: list[str]) -> int:
    cfg = ImportCostConfig.zlc_reexport() if "--zlc" in argv else ImportCostConfig()
    if "--paste" in argv:
        i = argv.index("--paste")
        text = argv[i + 1] if i + 1 < len(argv) else ""
        if not text:
            print("Uso: --paste \"texto del anuncio\"")
            return 1
        _run_paste(text, cfg)
    else:
        _run_scheduled()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
