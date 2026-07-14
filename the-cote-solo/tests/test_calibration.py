"""Tests de calibración del fair value y del libro personal."""

import unittest

from the_cote_solo import pricing
from the_cote_solo.arbitrage import evaluate
from the_cote_solo.comparables import Sale, SalesBook, calibrated_fair_value, sale_from_record
from the_cote_solo.models import Instrument, Listing
from the_cote_solo.portfolio import Portfolio, seed_demo


def _inst(**kw):
    base = dict(ref="TEST", brand="Rolex", family="Sub", name="Test",
                retail_usd=10000, base_fair_value_usd=14000, comparables_per_qtr=40)
    base.update(kw)
    return Instrument(**base)


def _listing(**kw):
    base = dict(id="l1", ref="TEST", source="chrono24", price_usd=11000,
                condition_raw="Excellent, box and papers", has_box=True, has_papers=True,
                seller_type="dealer_verified",
                signals={"platform_verified": True, "account_age_months": 60,
                         "completed_sales": 300, "rating": 4.8, "has_serial": True,
                         "real_photos": True})
    base.update(kw)
    return Listing(**base)


class TestComparables(unittest.TestCase):
    def test_needs_minimum_sales(self):
        self.assertIsNone(calibrated_fair_value([Sale("A", 100, 1.0, 0)]))

    def test_weighted_average(self):
        sales = [Sale("A", 10000, 1.0, 0), Sale("A", 12000, 1.0, 0)]
        fv, n = calibrated_fair_value(sales)
        self.assertEqual(n, 2)
        self.assertAlmostEqual(fv, 11000, delta=1)

    def test_recency_weights_recent_higher(self):
        recent = [Sale("A", 10000, 1.0, 0), Sale("A", 20000, 1.0, 3650)]
        fv, _ = calibrated_fair_value(recent)
        self.assertLess(fv, 15000)  # el viejo pesa menos → más cerca de 10000

    def test_sale_from_record_normalizes_condition(self):
        # una venta sin papeles debe subir su baseline (baseline = precio/mult, mult<1)
        s = sale_from_record({"ref": "A", "hammer_usd": 9400, "condition": "excellent",
                              "box": True, "papers": False, "sold_date": "2024-01-01"})
        self.assertGreater(s.baseline_price, 9400)


class TestPricingCalibration(unittest.TestCase):
    def test_falls_back_to_seed_without_sales(self):
        p = pricing.price_piece(_inst(base_fair_value_usd=14000), _listing())
        self.assertFalse(p.calibrated)
        self.assertAlmostEqual(p.fair_value, 14000, delta=1)  # EXCELLENT full set = baseline

    def test_uses_calibrated_baseline(self):
        book = SalesBook()
        book.add(Sale("TEST", 16000, 1.0, 0)); book.add(Sale("TEST", 16000, 1.0, 0))
        p = pricing.price_piece(_inst(base_fair_value_usd=14000), _listing(), sales=book)
        self.assertTrue(p.calibrated)
        self.assertEqual(p.n_sales, 2)
        self.assertAlmostEqual(p.fair_value, 16000, delta=1)  # cierres mandan sobre el seed

    def test_calibration_flows_into_arbitrage(self):
        book = SalesBook()
        for _ in range(3):
            book.add(Sale("TEST", 17000, 1.0, 0))
        o = evaluate(_inst(base_fair_value_usd=12000), _listing(price_usd=11000), sales=book)
        self.assertTrue(o.priced.calibrated)
        # baseline 17000 > seed 12000 → mejor edge que sin calibrar
        self.assertGreater(o.priced.fair_value, 15000)


class TestPortfolio(unittest.TestCase):
    def _fv(self, ref):
        return {"126610LN": 14000, "310.30.42": 6600, "126710BLNR": 18000}.get(ref)

    def test_buy_and_view_pnl(self):
        pf = Portfolio(":memory:")
        pf.record_buy("126610LN", 11200, "2024-01-01", target=14500)
        views = pf.view(self._fv)
        self.assertEqual(len(views), 1)
        self.assertAlmostEqual(views[0].unrealized_pnl, 2800, delta=1)

    def test_sell_signal_on_target(self):
        pf = Portfolio(":memory:")
        pf.record_buy("126610LN", 11200, "2024-01-01", target=13000)  # fv 14000 >= target
        self.assertEqual(pf.view(self._fv)[0].signal, "SELL")

    def test_recorded_sale_becomes_comparable(self):
        pf = Portfolio(":memory:")
        pid = pf.record_buy("126610LN", 11200, "2024-01-01")
        pf.record_sale(pid, 13800, "2024-03-01")
        comps = pf.realized_sales_as_comparables()
        self.assertEqual(len(comps), 1)
        self.assertEqual(comps[0].quality, 1.0)  # venta propia = calidad máxima
        self.assertEqual(pf.realized_days_to_sell(), [60])

    def test_summary(self):
        pf = Portfolio(":memory:"); seed_demo(pf)
        s = pf.summary(self._fv)
        self.assertEqual(s["open_positions"], 3)
        self.assertGreater(s["deployed"], 0)


if __name__ == "__main__":
    unittest.main()
