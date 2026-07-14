"""Tests del adapter de eBay (offline) y del ClaudeExtractor (cliente inyectado).

Sin red ni API key: eBay usa la fixture offline; ClaudeExtractor usa un cliente falso.
"""

import json
import os
import unittest

from the_cote_solo.ingest.extract import (
    ClaudeExtractor, FallbackExtractor, RuleBasedExtractor, default_extractor,
)
from the_cote_solo.ingest.normalize import payload_to_listing
from the_cote_solo.ingest.raw_store import RawStore
from the_cote_solo.ingest.scheduler import Scheduler
from the_cote_solo.ingest.source import SourceDisabled
from the_cote_solo.ingest.sources.ebay import EbaySource, _pct_to_5

_FIXTURE = os.path.join(os.path.dirname(__file__), "..", "fixtures", "ebay_sample.json")


class TestEbayOffline(unittest.TestCase):
    def test_parses_fixture_to_offers(self):
        src = EbaySource(offline_fixture=_FIXTURE)
        self.assertTrue(src.enabled)
        batch = src.fetch(None)
        refs = {r.payload["ref"] for r in batch.records}
        self.assertTrue({"124270", "126610LN", "310.30.42"} <= refs)
        self.assertTrue(all(r.record_type == "offer" for r in batch.records))

    def test_maps_price_seller_and_signals(self):
        rec = next(r for r in EbaySource(offline_fixture=_FIXTURE).fetch(None).records
                   if r.payload["ref"] == "124270")
        self.assertEqual(rec.payload["price_usd"], 6450.0)
        self.assertEqual(rec.payload["seller_name"], "luxwatch_dealer")
        self.assertTrue(rec.payload["signals"]["platform_verified"])
        self.assertEqual(rec.payload["signals"]["completed_sales"], 1820)
        self.assertAlmostEqual(rec.payload["signals"]["rating"], 4.98, places=2)

    def test_offer_normalizes_to_listing(self):
        rec = EbaySource(offline_fixture=_FIXTURE).fetch(None).records[0]
        listing = payload_to_listing(rec.source, rec.external_id, rec.payload)
        self.assertIsNotNone(listing)
        self.assertEqual(listing.source, "ebay")

    def test_disabled_without_credentials(self):
        src = EbaySource(client_id=None, client_secret=None)  # sin fixture ni llaves
        self.assertFalse(src.enabled)
        # el scheduler la omite limpiamente (no revienta)
        rep = Scheduler(RawStore(":memory:")).run_source(src)
        self.assertFalse(rep.ok)

    def test_fetch_without_creds_raises_disabled(self):
        with self.assertRaises(SourceDisabled):
            EbaySource(client_id=None, client_secret=None)._items()

    def test_pct_to_5(self):
        self.assertEqual(_pct_to_5("100.0"), 5.0)
        self.assertIsNone(_pct_to_5(None))


# --- Cliente falso de la Claude API para probar ClaudeExtractor sin red ---
class _FakeBlock:
    type = "text"
    def __init__(self, text): self.text = text

class _FakeMessage:
    def __init__(self, text): self.content = [_FakeBlock(text)]

class _FakeMessages:
    def __init__(self, payload, sink): self._payload = payload; self._sink = sink
    def create(self, **kwargs):
        self._sink.update(kwargs)
        return _FakeMessage(json.dumps(self._payload))

class _FakeClient:
    def __init__(self, payload, sink): self.messages = _FakeMessages(payload, sink)


class TestClaudeExtractor(unittest.TestCase):
    def test_parses_structured_output(self):
        payload = {"ref": "126710blro", "brand": "Rolex", "price_usd": 16800,
                   "year": 2022, "box": True, "papers": True, "polished": False,
                   "condition_text": "excelente"}
        sink = {}
        ex = ClaudeExtractor(client=_FakeClient(payload, sink))
        out = ex.extract("Rolex GMT Pepsi, impecable, USD 16,800")
        self.assertEqual(out["ref"], "126710BLRO")     # normaliza a mayúsculas
        self.assertEqual(out["price_usd"], 16800.0)
        self.assertTrue(out["papers"])
        self.assertEqual(out["condition_raw"], "excelente")

    def test_request_uses_structured_output_and_default_model(self):
        sink = {}
        ClaudeExtractor(client=_FakeClient({"ref": "124270"}, sink)).extract("texto")
        self.assertEqual(sink["model"], "claude-opus-4-8")
        self.assertIn("format", sink["output_config"])
        self.assertNotIn("temperature", sink)  # removido en opus 4.8

    def test_missing_sdk_gives_clear_error(self):
        # sin cliente inyectado y sin SDK instalado → error informativo, no crash silencioso
        with self.assertRaises(RuntimeError):
            ClaudeExtractor().extract("texto")


class TestFallbackExtractor(unittest.TestCase):
    class _Boom:
        def extract(self, text): raise RuntimeError("sin API")

    def test_falls_back_on_error(self):
        ex = FallbackExtractor(self._Boom(), RuleBasedExtractor())
        out = ex.extract("Rolex Explorer 124270 USD 6300 full set")
        self.assertEqual(out["ref"], "124270")  # lo resolvió el respaldo de reglas

    def test_uses_primary_when_it_finds_ref(self):
        class _Good:
            def extract(self, text): return {"ref": "126610LN", "price_usd": 9000}
        ex = FallbackExtractor(_Good(), RuleBasedExtractor())
        self.assertEqual(ex.extract("lo que sea")["ref"], "126610LN")

    def test_default_extractor_is_rulebased_without_env(self):
        # sin THE_COTE_LLM_EXTRACTOR/clave, el default es el parser de reglas
        old = os.environ.pop("THE_COTE_LLM_EXTRACTOR", None)
        try:
            self.assertIsInstance(default_extractor(), RuleBasedExtractor)
        finally:
            if old is not None:
                os.environ["THE_COTE_LLM_EXTRACTOR"] = old


if __name__ == "__main__":
    unittest.main()
