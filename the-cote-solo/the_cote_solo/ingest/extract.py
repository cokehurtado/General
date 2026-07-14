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

import json
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


# Esquema de extracción estructurada (structured outputs de la Claude API).
_SCHEMA = {
    "type": "object",
    "properties": {
        "ref": {"type": ["string", "null"]},
        "brand": {"type": ["string", "null"]},
        "price_usd": {"type": ["number", "null"]},
        "year": {"type": ["integer", "null"]},
        "box": {"type": ["boolean", "null"]},
        "papers": {"type": ["boolean", "null"]},
        "polished": {"type": ["boolean", "null"]},
        "condition_text": {"type": ["string", "null"]},
    },
    "required": ["ref", "brand", "price_usd", "year", "box", "papers", "polished", "condition_text"],
    "additionalProperties": False,
}

_SYSTEM = (
    "Eres un extractor de datos de anuncios de relojes de lujo de segunda mano. "
    "Devuelves SOLO los campos estructurados del esquema. Reglas: 'ref' es el número "
    "de referencia canónico del modelo (ej. 126710BLRO, 5711/1A); si no aparece, null. "
    "'box'/'papers' son true si el anuncio menciona caja/papeles originales o 'full set'. "
    "'price_usd' en dólares (convierte si viene en otra moneda y es evidente). "
    "'condition_text' es la descripción de estado tal cual. Usa null para lo que no aparezca."
)


class ClaudeExtractor(Extractor):
    """Extractor con la Claude API (SDK oficial), para texto ambiguo/informal.

    Import perezoso del SDK: el núcleo sigue siendo cero-dependencias; el paquete
    `anthropic` solo se necesita si de verdad usas este extractor. Modelo por defecto
    `claude-opus-4-8` (configurable; `claude-haiku-4-5` es la opción de menor costo
    para esta tarea de extracción). `client` es inyectable para tests sin red.
    """

    name = "claude"

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-opus-4-8", client=None):
        self.api_key = api_key
        self.model = model
        self._client = client

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            import anthropic  # import perezoso
        except ImportError as e:
            raise RuntimeError(
                "ClaudeExtractor requiere el SDK de Anthropic: `pip install anthropic` "
                "y define ANTHROPIC_API_KEY (o usa RuleBasedExtractor)."
            ) from e
        self._client = anthropic.Anthropic(api_key=self.api_key)  # api_key None → env/perfil
        return self._client

    @staticmethod
    def _first_text(message) -> str:
        for block in getattr(message, "content", []) or []:
            if getattr(block, "type", None) == "text":
                return block.text
        return "{}"

    def extract(self, text: str) -> dict:
        client = self._get_client()
        message = client.messages.create(
            model=self.model,
            max_tokens=512,
            system=_SYSTEM,
            messages=[{"role": "user", "content": text}],
            output_config={"format": {"type": "json_schema", "schema": _SCHEMA}},
        )
        data = json.loads(self._first_text(message))
        return _to_extractor_fields(data)


def _to_extractor_fields(data: dict) -> dict:
    """Normaliza la salida del LLM al mismo dict que produce RuleBasedExtractor."""
    out: dict = {}
    if data.get("ref"):
        out["ref"] = str(data["ref"]).upper()
    if data.get("brand"):
        out["brand"] = str(data["brand"])
    if data.get("price_usd") is not None:
        out["price_usd"] = float(data["price_usd"])
    if data.get("year") is not None:
        out["year"] = int(data["year"])
    for k in ("box", "papers", "polished"):
        if data.get(k) is not None:
            out[k] = bool(data[k])
    out["condition_raw"] = str(data.get("condition_text") or "").strip()[:300]
    return out


class FallbackExtractor(Extractor):
    """Intenta el extractor primario; ante error o ref no detectada, usa el de respaldo."""

    name = "fallback"

    def __init__(self, primary: Extractor, fallback: Extractor):
        self.primary = primary
        self.fallback = fallback

    def extract(self, text: str) -> dict:
        try:
            result = self.primary.extract(text)
            if result.get("ref"):
                return result
        except Exception:
            pass
        return self.fallback.extract(text)


def default_extractor() -> Extractor:
    """RuleBased por defecto; LLM (con fallback a reglas) si está habilitado por entorno.

    Activa el LLM con THE_COTE_LLM_EXTRACTOR=1 y una ANTHROPIC_API_KEY configurada.
    """
    import os
    if os.getenv("THE_COTE_LLM_EXTRACTOR", "").lower() in ("1", "true", "yes") and os.getenv("ANTHROPIC_API_KEY"):
        return FallbackExtractor(ClaudeExtractor(), RuleBasedExtractor())
    return RuleBasedExtractor()
