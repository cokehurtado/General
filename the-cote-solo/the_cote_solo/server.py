"""Servidor local del terminal — stdlib http.server, cero dependencias.

Sirve la UI (web/terminal.html) y expone el motor REAL como JSON:
  GET  /                      -> el terminal
  GET  /api/scan?scenario=zlc -> oportunidades (motor real, fair value calibrado)
  POST /api/analyze           -> {text, scenario} -> veredicto de un deal pegado
  GET  /api/portfolio         -> libro personal (posiciones + P&L + señales)

Producción: esto migra a FastAPI/uvicorn sin tocar el motor. Para v0 usamos la
stdlib para no instalar nada.  Uso:  python -m the_cote_solo.server  (puerto 8000)
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .arbitrage import evaluate, scan
from .comparables import SalesBook
from .costs import ImportCostConfig
from .ingest.normalize import payload_to_listing
from .ingest.raw_store import RawStore
from .ingest.scheduler import Scheduler
from .ingest.sources.auction_feed import AuctionResultsSource
from .ingest.sources.paste_source import PasteSource
from .portfolio import Portfolio, seed_demo
from .universe import UNIVERSE

_HERE = os.path.dirname(__file__)
_WEB = os.path.join(_HERE, "..", "web", "terminal.html")
_FIXTURES = os.path.join(_HERE, "..", "fixtures", "listings.json")

_VMAP = {"BUY": "buy", "PASS": "pass", "SLOW_TURN": "slow",
         "ILLIQUID": "illiq", "UNSAFE_SOURCE": "unsafe"}


def _load_listings():
    from .models import Listing
    with open(_FIXTURES, encoding="utf-8") as f:
        return [Listing(**r) for r in json.load(f)]


def _sales_book() -> SalesBook:
    """Calibra el fair value con los cierres de subasta ingestados."""
    store = RawStore(":memory:")
    Scheduler(store).run_source(AuctionResultsSource())
    book = SalesBook()
    book.add_records(store.records("sale"), source="auction")
    store.close()
    return book


def _cfg(scenario: str) -> ImportCostConfig:
    return ImportCostConfig.zlc_reexport() if scenario == "zlc" else ImportCostConfig()


def _opp_json(o) -> dict:
    p = o.priced
    return {
        "v": _VMAP.get(o.verdict, "pass"),
        "name": f"{UNIVERSE[o.listing.ref].brand} {UNIVERSE[o.listing.ref].name}",
        "ref": o.listing.ref, "price": o.listing.price_usd, "fv": p.fair_value,
        "gr": round(o.gross_edge * 100, 1), "net": round(o.net_edge * 100, 1),
        "d": o.days_to_sell, "an": (None if o.annualized_edge >= 20 else round(o.annualized_edge * 100, 0)),
        "x": o.capital_turns_per_year, "tier": p.liquidity_tier.value,
        "prov": round(o.provenance_score), "ncomp": p.n_sales or UNIVERSE[o.listing.ref].comparables_per_qtr,
        "upd": ("calibrado" if p.calibrated else "seed"),
        "flags": o.provenance_flags, "retail": bool(p.below_retail),
    }


def api_scan(scenario: str) -> list:
    sales = _sales_book()
    opps = scan(UNIVERSE, _load_listings(), _cfg(scenario), sales=sales)
    return [_opp_json(o) for o in opps]


def api_analyze(text: str, scenario: str) -> dict:
    rec = PasteSource().ingest_text(
        text, seller_type="dealer", region="LATAM",
        signals={"platform_verified": False, "account_age_months": 18,
                 "completed_sales": 25, "has_serial": True, "real_photos": True})
    listing = payload_to_listing(rec.source, rec.external_id, rec.payload)
    if listing is None or listing.ref not in UNIVERSE:
        return {"error": "No se detectó una referencia conocida y/o precio."}
    o = evaluate(UNIVERSE[listing.ref], listing, _cfg(scenario), sales=_sales_book())
    d = _opp_json(o)
    d["pflags"] = o.provenance_flags
    return d


def api_portfolio() -> dict:
    pf = Portfolio(":memory:"); seed_demo(pf)
    fv = lambda ref: UNIVERSE[ref].base_fair_value_usd if ref in UNIVERSE else None
    rows = []
    for v in pf.view(fv):
        inst = UNIVERSE.get(v.pos.ref)
        rows.append({"name": f"{inst.brand} {inst.name}" if inst else v.pos.ref,
                     "ref": v.pos.ref, "buy": v.pos.buy_price, "fv": v.fair_value,
                     "pnl": v.unrealized_pnl, "pct": v.pnl_pct, "d": v.days_held,
                     "tgt": v.pos.target_price, "sig": v.signal.lower(), "st": v.reason})
    out = {"positions": rows, "summary": pf.summary(fv)}
    pf.close()
    return out


class Handler(BaseHTTPRequestHandler):
    def _send(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):  # silencioso
        pass

    def do_GET(self):
        u = urlparse(self.path)
        if u.path in ("/", "/index.html"):
            try:
                with open(_WEB, "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except FileNotFoundError:
                self._send({"error": "terminal.html no encontrado"}, 404)
        elif u.path == "/api/scan":
            q = parse_qs(u.query)
            self._send(api_scan((q.get("scenario", ["import"])[0])))
        elif u.path == "/api/portfolio":
            self._send(api_portfolio())
        else:
            self._send({"error": "not found"}, 404)

    def do_POST(self):
        u = urlparse(self.path)
        if u.path == "/api/analyze":
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n) or b"{}")
            self._send(api_analyze(data.get("text", ""), data.get("scenario", "import")))
        else:
            self._send({"error": "not found"}, 404)


def serve(port: int = 8000) -> None:
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"The Cote · terminal en http://127.0.0.1:{port}  (Ctrl+C para salir)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    import sys
    serve(int(sys.argv[1]) if len(sys.argv) > 1 else 8000)
