"""CLI de ingesta: demuestra la vía híbrida end-to-end, sin red ni API key.

    python -m the_cote_solo.ingest.run
        Corre el scheduler sobre las fuentes limpias habilitadas (subastas),
        guarda los cierres en el raw store y reporta. Muestra el gate de los
        sitios protegidos (apagados).

    python -m the_cote_solo.ingest.run --paste "Rolex 124270 Explorer, USD 6300, full set, 2023"
        Ingesta 'pega-el-texto': extrae los campos del anuncio, lo pasa por el
        motor de arbitraje y muestra el veredicto con todas las variables.

    Flags: --zlc (escenario de costos ZLC para el arbitraje del deal pegado).
"""

from __future__ import annotations

import os
import sys

from ..arbitrage import evaluate
from ..costs import ImportCostConfig
from ..universe import UNIVERSE
from .normalize import payload_to_listing
from .raw_store import RawStore
from .scheduler import Scheduler
from .sources.auction_feed import AuctionResultsSource
from .sources.ebay import EbaySource
from .sources.paste_source import PasteSource
from .sources.protected import Chrono24Source, WatchChartsSource

_EBAY_FIXTURE = os.path.join(os.path.dirname(__file__), "..", "..", "fixtures", "ebay_sample.json")


def _run_scheduled() -> None:
    store = RawStore(":memory:")
    sched = Scheduler(store)
    # eBay: online si hay EBAY_CLIENT_ID/SECRET; si no, modo offline con la fixture.
    ebay = EbaySource() if (os.getenv("EBAY_CLIENT_ID") and os.getenv("EBAY_CLIENT_SECRET")) \
        else EbaySource(offline_fixture=_EBAY_FIXTURE)
    sources = [AuctionResultsSource(), ebay, Chrono24Source(), WatchChartsSource()]

    print("\nThe Cote Solo · ingesta automatizada (tick del scheduler)\n" + "=" * 74)
    for rep in sched.run_all(sources):
        if rep.ok:
            print(f"✓ {rep.source:<18} nuevos {rep.new}  cambiados {rep.changed}  "
                  f"sin cambio {rep.unchanged}")
        else:
            print(f"· {rep.source:<18} omitida — {rep.skipped_reason}")

    # Cablea los cierres al motor: calibra el fair value con datos reales.
    from ..comparables import SalesBook, calibrated_fair_value
    from ..universe import UNIVERSE
    book = SalesBook()
    book.add_records(store.records("sale"), source="auction")

    print("-" * 74)
    print(f"{store.count('sale')} cierres en el raw store → calibrando fair value:\n")
    print(f"  {'REF':<12}{'SEED':>10}{'CALIBRADO':>12}{'Δ':>8}   cierres")
    for ref in sorted(book.refs()):
        inst = UNIVERSE.get(ref)
        if not inst:
            continue
        est = calibrated_fair_value(book.for_ref(ref))
        if est is None:
            print(f"  {ref:<12}{('$'+format(inst.base_fair_value_usd,',.0f')):>10}"
                  f"{'—':>12}{'(n<2)':>8}   {len(book.for_ref(ref))}")
        else:
            fv, n = est
            delta = (fv / inst.base_fair_value_usd - 1) * 100
            print(f"  {ref:<12}{('$'+format(inst.base_fair_value_usd,',.0f')):>10}"
                  f"{('$'+format(fv,',.0f')):>12}{(('%+.1f' % delta)+'%'):>8}   {n}")
    print("\nEl fair value ya no es semilla: usa tus cierres reales (doc 07).\n")

    # Ofertas activas ingestadas (eBay) → escaneadas como arbitraje, con fair value calibrado.
    offers = list(store.records("offer"))
    if offers:
        print(f"{len(offers)} ofertas activas ingestadas → escaneo de arbitraje:\n")
        for rec in offers:
            listing = payload_to_listing(rec["source"], rec["external_id"], rec["payload"])
            if listing is None or listing.ref not in UNIVERSE:
                continue
            o = evaluate(UNIVERSE[listing.ref], listing, ImportCostConfig.zlc_reexport(), sales=book)
            inst = UNIVERSE[listing.ref]
            print(f"  [{o.verdict:<12}] {inst.brand} {inst.name:<26} "
                  f"${listing.price_usd:>8,.0f}  neto {o.net_edge:+.1%}  "
                  f"({'calibrado' if o.priced.calibrated else 'seed'}) · {rec['source']}")
        print()
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
    print("\nThe Cote Solo · ingesta 'pega-el-texto'\n" + "=" * 74)
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
