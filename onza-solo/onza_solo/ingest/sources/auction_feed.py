"""Fuente limpia de ejemplo: resultados públicos de subastas (precios de CIERRE).

Los resultados de subastas son datos fácticos públicos → la vía legalmente más
defendible. Producen record_type='sale' (calibran el fair value; NO son deals
comprables).

En v0 lee un archivo-feed local que simula la respuesta ya parseada de los
resultados publicados. En producción, aquí va un GET a la página/endpoint público
de resultados (Phillips/Christie's/Sotheby's), respetando robots.txt y rate limits.
Incremental por `sold_date` vía cursor.
"""

from __future__ import annotations

import json
import os
from typing import Optional

from ..source import IngestBatch, RawRecord, Source

_DEFAULT_FEED = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "fixtures", "auction_feed.json"
)


class AuctionResultsSource(Source):
    name = "auction_results"
    enabled = True

    def __init__(self, feed_path: str = _DEFAULT_FEED):
        self.feed_path = feed_path

    def _load_feed(self) -> list[dict]:
        with open(self.feed_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def fetch(self, cursor: Optional[str]) -> IngestBatch:
        rows = self._load_feed()
        # Incremental: solo lotes vendidos DESPUÉS del cursor (última sold_date vista)
        new = [r for r in rows if cursor is None or str(r.get("sold_date", "")) > cursor]
        new.sort(key=lambda r: str(r.get("sold_date", "")))

        records = [
            RawRecord(
                source=self.name,
                external_id=str(r["external_id"]),
                record_type="sale",
                payload=r,
            )
            for r in new
        ]
        next_cursor = new[-1]["sold_date"] if new else cursor
        return IngestBatch(records=records, next_cursor=next_cursor)
