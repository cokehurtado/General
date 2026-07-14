"""Tests de la capa de ingesta (stdlib unittest, sin red ni API key)."""

import unittest

from onza_solo.ingest.circuit_breaker import CircuitBreaker
from onza_solo.ingest.extract import RuleBasedExtractor, ClaudeExtractor
from onza_solo.ingest.normalize import payload_to_listing
from onza_solo.ingest.raw_store import RawStore
from onza_solo.ingest.scheduler import Scheduler
from onza_solo.ingest.source import RawRecord, content_hash
from onza_solo.ingest.sources.auction_feed import AuctionResultsSource
from onza_solo.ingest.sources.paste_source import PasteSource
from onza_solo.ingest.sources.protected import Chrono24Source


class TestRawStoreIdempotency(unittest.TestCase):
    def _rec(self, ext_id, price):
        return RawRecord(source="s", external_id=ext_id, record_type="offer",
                         payload={"ref": "124270", "price_usd": price})

    def test_new_then_unchanged(self):
        store = RawStore(":memory:")
        self.assertEqual(store.upsert(self._rec("a", 6000)).status, "new")
        self.assertEqual(store.upsert(self._rec("a", 6000)).status, "unchanged")  # idempotente
        self.assertEqual(store.count(), 1)

    def test_change_detected(self):
        store = RawStore(":memory:")
        store.upsert(self._rec("a", 6000))
        self.assertEqual(store.upsert(self._rec("a", 5800)).status, "changed")  # bajó precio
        self.assertEqual(store.count(), 1)  # sigue siendo un registro (misma pieza)

    def test_cursor_roundtrip(self):
        store = RawStore(":memory:")
        self.assertIsNone(store.get_cursor("s"))
        store.set_cursor("s", "2024-06-01")
        self.assertEqual(store.get_cursor("s"), "2024-06-01")


class TestCircuitBreaker(unittest.TestCase):
    def test_opens_after_threshold(self):
        cb = CircuitBreaker(failure_threshold=3, cooldown_seconds=100)
        for _ in range(3):
            cb.record_failure(now=0)
        self.assertTrue(cb.is_open(now=0))

    def test_closes_after_cooldown(self):
        cb = CircuitBreaker(failure_threshold=1, cooldown_seconds=100)
        cb.record_failure(now=0)
        self.assertTrue(cb.is_open(now=50))
        self.assertFalse(cb.is_open(now=150))  # half-open tras cooldown

    def test_success_resets(self):
        cb = CircuitBreaker(failure_threshold=2)
        cb.record_failure(now=0)
        cb.record_success()
        cb.record_failure(now=0)
        self.assertFalse(cb.is_open(now=0))  # el éxito reseteó el conteo


class TestAuctionSourceIncremental(unittest.TestCase):
    def test_incremental_by_cursor(self):
        src = AuctionResultsSource()
        first = src.fetch(cursor=None)
        self.assertGreater(len(first.records), 0)
        self.assertTrue(all(r.record_type == "sale" for r in first.records))
        # Con el cursor al final, no debería traer nada nuevo
        second = src.fetch(cursor=first.next_cursor)
        self.assertEqual(len(second.records), 0)

    def test_scheduler_idempotent_across_ticks(self):
        store = RawStore(":memory:")
        sched = Scheduler(store)
        src = AuctionResultsSource()
        r1 = sched.run_source(src)
        r2 = sched.run_source(src)  # segundo tick: cursor avanzado → 0 nuevos
        self.assertGreater(r1.new, 0)
        self.assertEqual(r2.new, 0)


class TestProtectedGate(unittest.TestCase):
    def test_disabled_source_skipped(self):
        store = RawStore(":memory:")
        sched = Scheduler(store)
        rep = sched.run_source(Chrono24Source())
        self.assertFalse(rep.ok)
        self.assertIn("gate", rep.skipped_reason.lower())


class TestExtractor(unittest.TestCase):
    def test_extracts_ref_price_box_papers(self):
        ex = RuleBasedExtractor()
        f = ex.extract("Rolex Explorer 124270, USD 6,300, full set, año 2023")
        self.assertEqual(f["ref"], "124270")
        self.assertEqual(f["price_usd"], 6300)
        self.assertTrue(f["box"])
        self.assertTrue(f["papers"])
        self.assertEqual(f["year"], 2023)
        self.assertEqual(f.get("brand"), "Rolex")

    def test_paste_source_produces_offer(self):
        rec = PasteSource().ingest_text("GMT Pepsi 126710BLRO $16800 box only 2022")
        self.assertEqual(rec.record_type, "offer")
        self.assertEqual(rec.payload["ref"], "126710BLRO")
        self.assertTrue(rec.payload["box"])
        self.assertFalse(rec.payload["papers"])  # 'box only' → sin papeles

    def test_normalize_offer_to_listing(self):
        rec = PasteSource().ingest_text("Explorer 124270 USD 6300 full set")
        listing = payload_to_listing(rec.source, rec.external_id, rec.payload)
        self.assertIsNotNone(listing)
        self.assertEqual(listing.ref, "124270")
        self.assertEqual(listing.price_usd, 6300)

    def test_claude_extractor_is_stub(self):
        with self.assertRaises(NotImplementedError):
            ClaudeExtractor().extract("cualquier texto")

    def test_content_hash_stable(self):
        self.assertEqual(content_hash({"a": 1, "b": 2}), content_hash({"b": 2, "a": 1}))


if __name__ == "__main__":
    unittest.main()
