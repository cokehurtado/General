"""Scheduler de ingesta: corre las fuentes habilitadas, incremental e idempotente,
con circuit breaker por fuente. Una 'corrida' (tick) procesa todas las fuentes
programadas una vez; en producción se invoca por cron cada X horas por fuente.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .circuit_breaker import CircuitBreaker
from .raw_store import RawStore
from .source import Source, SourceDisabled


@dataclass
class SourceRunReport:
    source: str
    ok: bool
    new: int = 0
    changed: int = 0
    unchanged: int = 0
    skipped_reason: Optional[str] = None


@dataclass
class Scheduler:
    store: RawStore
    breakers: dict = field(default_factory=dict)

    def _breaker(self, name: str) -> CircuitBreaker:
        return self.breakers.setdefault(name, CircuitBreaker())

    def run_source(self, source: Source, now: Optional[float] = None) -> SourceRunReport:
        if not source.enabled:
            return SourceRunReport(source.name, ok=False, skipped_reason="deshabilitada (gate)")

        breaker = self._breaker(source.name)
        if breaker.is_open(now):
            return SourceRunReport(source.name, ok=False, skipped_reason="circuit breaker abierto")

        try:
            cursor = self.store.get_cursor(source.name)
            batch = source.fetch(cursor)
        except SourceDisabled as e:
            return SourceRunReport(source.name, ok=False, skipped_reason=str(e))
        except Exception as e:  # bloqueo, timeout, parse error, etc.
            breaker.record_failure(now)
            return SourceRunReport(source.name, ok=False, skipped_reason=f"error: {e}")

        rep = SourceRunReport(source.name, ok=True)
        for rec in batch.records:
            res = self.store.upsert(rec)
            if res.status == "new":
                rep.new += 1
            elif res.status == "changed":
                rep.changed += 1
            else:
                rep.unchanged += 1

        self.store.set_cursor(source.name, batch.next_cursor)
        breaker.record_success()
        return rep

    def run_all(self, sources: list[Source], now: Optional[float] = None) -> list[SourceRunReport]:
        return [self.run_source(s, now) for s in sources]
