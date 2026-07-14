"""Fuente 'pega-el-texto': ingesta semi-automática de un anuncio comprable.

Tú traes el deal (de Instagram, WhatsApp, un dealer, donde sea), lo pegas, y
esto produce un record_type='offer' listo para escanear como arbitraje. No
scrapea nada: automatiza el ANÁLISIS, no la obtención.
"""

from __future__ import annotations

import hashlib
from typing import Optional

from ..extract import Extractor, default_extractor
from ..source import IngestBatch, RawRecord, Source


def _stable_id(text: str) -> str:
    return "paste-" + hashlib.sha256(text.strip().encode("utf-8")).hexdigest()[:16]


class PasteSource(Source):
    """No es programada: se alimenta on-demand con `ingest_text`."""

    name = "paste"
    enabled = True

    def __init__(self, extractor: Optional[Extractor] = None):
        self.extractor = extractor or default_extractor()

    def ingest_text(self, text: str, **overrides) -> RawRecord:
        """Extrae campos del texto y arma un RawRecord 'offer'.

        `overrides` permite corregir a mano lo que el extractor no captó
        (p.ej. seller_type, region, signals de procedencia).
        """
        fields = self.extractor.extract(text)
        fields.update(overrides)
        return RawRecord(
            source=self.name,
            external_id=_stable_id(text),
            record_type="offer",
            payload=fields,
        )

    def fetch(self, cursor: Optional[str]) -> IngestBatch:
        # No participa del scheduler programado.
        return IngestBatch(records=[], next_cursor=cursor)
