"""Interfaz común de fuentes y tipos de la ingesta.

Una fuente nueva = un adapter que implementa `Source`. El motor no cambia.
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def content_hash(payload: dict) -> str:
    """Hash estable del payload para detectar cambios / deduplicar."""
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


@dataclass
class RawRecord:
    """Registro crudo tal como llega de la fuente (inmutable en el raw store)."""

    source: str
    external_id: str              # id estable dentro de la fuente (para idempotencia)
    record_type: str              # "sale" (cierre, calibra) | "offer" (comprable, se escanea)
    payload: dict                 # campos crudos específicos de la fuente
    fetched_at: str = field(default_factory=utcnow_iso)
    hash: str = ""

    def __post_init__(self):
        if not self.hash:
            self.hash = content_hash(self.payload)


@dataclass
class IngestBatch:
    """Lo que devuelve una fuente en un fetch: registros + nuevo cursor incremental."""

    records: list[RawRecord]
    next_cursor: Optional[str] = None


class SourceDisabled(RuntimeError):
    """La fuente está apagada a propósito (p.ej. gate legal)."""


class Source(ABC):
    """Contrato de una fuente de datos."""

    name: str = "source"
    enabled: bool = True

    @abstractmethod
    def fetch(self, cursor: Optional[str]) -> IngestBatch:
        """Trae registros nuevos desde `cursor` (incremental). Idempotente aguas abajo."""
        raise NotImplementedError
