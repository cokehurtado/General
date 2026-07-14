"""Adapter de la API oficial de eBay (Browse) — listings activos comprables.

Vía legal y estable (a diferencia del scraping): eBay expone una API oficial.
Produce record_type='offer' (anuncios activos que se escanean como arbitraje).

Autenticación: OAuth client-credentials. Requiere EBAY_CLIENT_ID / EBAY_CLIENT_SECRET
(App keys de eBay Developer). Sin credenciales, la fuente está deshabilitada (gate),
igual que los sitios protegidos — pero aquí el gate es solo por credenciales, no legal.

Modo offline: `EbaySource(offline_fixture=path)` lee una respuesta de ejemplo con la
forma de `buy/browse/v1/item_summary/search`, para probar el parseo sin red ni llaves.

HTTP con urllib (stdlib) para mantener el paquete sin dependencias; respeta el proxy
del entorno. La idempotencia la da el raw store por (source, itemId).
"""

from __future__ import annotations

import base64
import json
import os
import urllib.parse
import urllib.request
from typing import Optional

from ..extract import RuleBasedExtractor
from ..source import IngestBatch, RawRecord, Source, SourceDisabled

_OAUTH_URL = "https://api.ebay.com/identity/v1/oauth2/token"
_BROWSE_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"
_SCOPE = "https://api.ebay.com/oauth/api_scope"

# Referencias a consultar por defecto (deportivas líquidas del universo)
_DEFAULT_QUERIES = ["Rolex 124270", "Rolex 126610LN", "Rolex 126710BLRO", "Omega 310.30.42"]


def _pct_to_5(pct) -> Optional[float]:
    try:
        return round(float(pct) / 20.0, 2)  # 0..100% → 0..5
    except (TypeError, ValueError):
        return None


class EbaySource(Source):
    name = "ebay"

    def __init__(self, queries=None, marketplace: str = "EBAY_US",
                 client_id: Optional[str] = None, client_secret: Optional[str] = None,
                 category_ids: str = "31387",  # Wristwatches
                 limit: int = 50, offline_fixture: Optional[str] = None, timeout: int = 20):
        self.queries = queries or _DEFAULT_QUERIES
        self.marketplace = marketplace
        self.category_ids = category_ids
        self.limit = limit
        self.offline_fixture = offline_fixture
        self.timeout = timeout
        self.client_id = client_id or os.getenv("EBAY_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("EBAY_CLIENT_SECRET")
        self.enabled = bool(offline_fixture) or bool(self.client_id and self.client_secret)

    # --- HTTP (solo se usa en modo online; los tests usan offline_fixture) ---
    def _token(self) -> str:
        cred = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        body = urllib.parse.urlencode({"grant_type": "client_credentials", "scope": _SCOPE}).encode()
        req = urllib.request.Request(_OAUTH_URL, data=body, method="POST", headers={
            "Authorization": f"Basic {cred}",
            "Content-Type": "application/x-www-form-urlencoded",
        })
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return json.loads(r.read())["access_token"]

    def _search(self, token: str, query: str) -> list[dict]:
        qs = urllib.parse.urlencode({"q": query, "category_ids": self.category_ids, "limit": self.limit})
        req = urllib.request.Request(f"{_BROWSE_URL}?{qs}", headers={
            "Authorization": f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": self.marketplace,
        })
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return json.loads(r.read()).get("itemSummaries", []) or []

    # --- parseo (compartido por online y offline) ---
    def item_to_record(self, item: dict) -> Optional[RawRecord]:
        item_id = item.get("itemId")
        title = item.get("title", "")
        price = item.get("price", {}) or {}
        value = price.get("value")
        if not item_id or value is None:
            return None
        # eBay no da la referencia canónica: se extrae del título con el parser de reglas.
        fields = RuleBasedExtractor().extract(title)
        if not fields.get("ref"):
            return None  # sin ref conocida no sirve para el motor

        seller = item.get("seller", {}) or {}
        payload = {
            **fields,
            "price_usd": float(value),
            "condition": f"{item.get('condition', '')} {title}".strip(),
            "seller_name": seller.get("username", "unknown"),
            "seller_type": "dealer",
            "region": "US",
            "url": item.get("itemWebUrl", ""),
            "signals": {
                "platform_verified": True,
                "real_photos": bool(item.get("image") or item.get("thumbnailImages")),
                "completed_sales": seller.get("feedbackScore"),
                "rating": _pct_to_5(seller.get("feedbackPercentage")),
            },
        }
        return RawRecord(source=self.name, external_id=str(item_id),
                         record_type="offer", payload=payload)

    def _items(self) -> list[dict]:
        if self.offline_fixture:
            with open(self.offline_fixture, encoding="utf-8") as f:
                return json.load(f).get("itemSummaries", []) or []
        if not (self.client_id and self.client_secret):
            raise SourceDisabled("ebay: faltan EBAY_CLIENT_ID / EBAY_CLIENT_SECRET")
        token = self._token()
        items: list[dict] = []
        for q in self.queries:
            items.extend(self._search(token, q))
        return items

    def fetch(self, cursor: Optional[str]) -> IngestBatch:
        records = [r for r in (self.item_to_record(it) for it in self._items()) if r]
        # Idempotencia por (source, itemId) en el raw store; sin cursor incremental nativo.
        return IngestBatch(records=records, next_cursor=cursor)
