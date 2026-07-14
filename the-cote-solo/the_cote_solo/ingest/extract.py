"""Extractor 'pega-el-texto': convierte el texto libre de un anuncio en campos
estructurados, sin scrapear nada. Tú traes el deal; esto automatiza el análisis.

Dos implementaciones:
  - RuleBasedExtractor: regex + keywords. Corre ya, sin dependencias ni API.
  - ClaudeExtractor:     STUB. Enchufa la Claude API cuando quieras (no requiere
                         credenciales hoy; cae en error informativo si se usa
                         sin configurar). Ver README.

Ambos devuelven un dict con las llaves que entiende normalize.payload_to_listing.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Optional

from ..universe import UNIVERSE

# Referencias y marcas conocidas para anclar la extracción
_KNOWN_REFS = {ref.upper(): inst for ref, inst in UNIVERSE.items()}
_KNOWN_BRANDS = sorted({inst.brand for inst in UNIVERSE.values()}, key=len, reverse=True)


class Extractor(ABC):
    name = "extractor"

    @abstractmethod
    def extract(self, text: str) -> dict:
        raise NotImplementedError


class RuleBasedExtractor(Extractor):
    name = "rules"

    _PRICE_RE = re.compile(r"(?:us\$|usd|\$)\s?([0-9][0-9\.,]{2,})", re.IGNORECASE)
    _YEAR_RE = re.compile(r"\b(19[5-9]\d|20[0-4]\d)\b")

    def extract(self, text: str) -> dict:
        t = text or ""
        low = t.lower()
        out: dict = {"condition_raw": t.strip()[:300]}

        # Referencia: primero por match exacto contra el universo, luego patrón genérico
        ref = None
        upper = t.upper()
        for known in _KNOWN_REFS:
            if known in upper:
                ref = known
                break
        if ref is None:
            m = re.search(r"\b([0-9]{5,6}[A-Z]{0,4}(?:/[0-9A-Z]+)?)\b", upper)
            if m:
                ref = m.group(1)
        if ref:
            out["ref"] = ref
            inst = _KNOWN_REFS.get(ref)
            if inst:
                out["brand"] = inst.brand

        # Marca (si no vino de la ref)
        if "brand" not in out:
            for b in _KNOWN_BRANDS:
                if b.lower() in low:
                    out["brand"] = b
                    break

        # Precio (toma el mayor número con símbolo de moneda; los precios de lujo son grandes)
        prices = []
        for m in self._PRICE_RE.finditer(t):
            num = m.group(1).replace(".", "").replace(",", "")
            if num.isdigit():
                prices.append(float(num))
        if prices:
            out["price_usd"] = max(prices)

        # Año
        y = self._YEAR_RE.search(t)
        if y:
            out["year"] = int(y.group(1))

        # Caja / papeles / full set / pulido
        full_set = any(k in low for k in ("full set", "complete set", "set completo"))
        out["box"] = full_set or any(k in low for k in ("box", "caja"))
        out["papers"] = full_set or any(
            k in low for k in ("papers", "papeles", "warranty card", "certificado", "tarjeta")
        )
        if any(k in low for k in ("polished", "pulido")):
            out["polished"] = True
        elif any(k in low for k in ("unpolished", "sin pulir")):
            out["polished"] = False

        return out


class ClaudeExtractor(Extractor):
    """STUB. Estructura de integración con la Claude API, apagada por defecto.

    Cuando quieras precisión superior en textos ambiguos (español informal de
    WhatsApp, abreviaturas, faltas), enchufa aquí una llamada a la Claude API que
    pida extracción a JSON con el mismo esquema que RuleBasedExtractor. Hasta
    entonces, no requiere API key y falla con un mensaje claro si se invoca.
    """

    name = "claude"

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-5"):
        self.api_key = api_key
        self.model = model

    def extract(self, text: str) -> dict:
        raise NotImplementedError(
            "ClaudeExtractor es un stub: configura ANTHROPIC_API_KEY y cablea la "
            "llamada a la Claude API (extracción a JSON). Por ahora usa RuleBasedExtractor."
        )


def default_extractor() -> Extractor:
    return RuleBasedExtractor()
