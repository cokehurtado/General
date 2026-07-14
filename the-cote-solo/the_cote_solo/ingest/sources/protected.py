"""Sitios protegidos (Chrono24, WatchCharts): adapters DESHABILITADOS por diseño.

Gate legal. El ToS de estos sitios prohíbe el scraping automatizado; hacerlo
expone a incumplimiento de contrato, derecho sui generis de bases de datos (UE),
competencia desleal, GDPR y circunvención de anti-bot. Ver README §"Riesgos
legales". Estos stubs existen para que la arquitectura esté lista, pero NO
corren hasta que haya una vía legítima (API/partner) o una decisión legal
consciente. La forma correcta de habilitarlos es reemplazar el cuerpo de
`fetch` por una llamada a la API oficial/feed licenciado — no por un scraper.
"""

from __future__ import annotations

from typing import Optional

from ..source import IngestBatch, Source, SourceDisabled


class _DisabledSource(Source):
    enabled = False
    reason = "gate legal: requiere API/partner o decisión legal explícita"

    def fetch(self, cursor: Optional[str]) -> IngestBatch:
        raise SourceDisabled(f"{self.name}: {self.reason}")


class Chrono24Source(_DisabledSource):
    name = "chrono24"
    reason = (
        "ToS prohíbe scraping + anti-bot agresivo. Habilitar SOLO vía API de "
        "partner/dealer de Chrono24, no con un scraper."
    )


class WatchChartsSource(_DisabledSource):
    name = "watchcharts"
    reason = "datos bajo licencia. Habilitar SOLO licenciando su API/feed."
