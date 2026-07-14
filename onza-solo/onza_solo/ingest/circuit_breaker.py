"""Circuit breaker por fuente.

Si una fuente empieza a fallar (bloqueos, errores), el breaker se ABRE y se
deja de golpear por un período de enfriamiento — así una fuente problemática no
tumba el pipeline ni escala el riesgo de bloqueo. `now` se inyecta para tests.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class CircuitBreaker:
    failure_threshold: int = 3
    cooldown_seconds: float = 900.0
    failures: int = 0
    opened_at: Optional[float] = None

    def _now(self, now: Optional[float]) -> float:
        return now if now is not None else time.monotonic()

    def is_open(self, now: Optional[float] = None) -> bool:
        """True si está abierto (no golpear). Se auto-cierra tras el cooldown."""
        if self.opened_at is None:
            return False
        if self._now(now) - self.opened_at >= self.cooldown_seconds:
            # half-open: dejamos pasar un intento y reseteamos
            self.opened_at = None
            self.failures = 0
            return False
        return True

    def record_success(self) -> None:
        self.failures = 0
        self.opened_at = None

    def record_failure(self, now: Optional[float] = None) -> None:
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.opened_at = self._now(now)
