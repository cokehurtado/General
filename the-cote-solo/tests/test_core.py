"""Tests del núcleo (stdlib unittest, sin dependencias externas).

Corre con:  python -m unittest discover tests
"""

import unittest

from the_cote_solo import grading, pricing, provenance, velocity
from the_cote_solo.arbitrage import evaluate, MIN_NET_EDGE
from the_cote_solo.costs import ImportCostConfig
from the_cote_solo.models import Condition, Instrument, LiquidityTier, Listing


def _inst(**kw):
    base = dict(
        ref="TEST", brand="Rolex", family="Submariner", name="Test",
        retail_usd=10000, base_fair_value_usd=14000, comparables_per_qtr=40,
    )
    base.update(kw)
    return Instrument(**base)


def _listing(**kw):
    base = dict(
        id="l1", ref="TEST", source="chrono24", price_usd=11000,
        condition_raw="Excellent, box and papers", has_box=True, has_papers=True,
        polished=False, seller_type="dealer_verified",
        signals={"platform_verified": True, "account_age_months": 60,
                 "completed_sales": 300, "rating": 4.8, "has_serial": True,
                 "real_photos": True},
    )
    base.update(kw)
    return Listing(**base)


class TestGrading(unittest.TestCase):
    def test_normalization_keywords(self):
        self.assertEqual(grading.grade_from_description("Brand new, unworn"), Condition.NEW_UNWORN)
        self.assertEqual(grading.grade_from_description("Mint like new"), Condition.MINT)
        self.assertEqual(grading.grade_from_description("for parts, broken"), Condition.POOR)

    def test_ambiguous_defaults_to_good(self):
        self.assertEqual(grading.grade_from_description("bonito reloj"), Condition.GOOD)

    def test_papers_penalize_more_than_box(self):
        no_papers = grading.condition_multiplier(Condition.EXCELLENT, has_box=True, has_papers=False)
        no_box = grading.condition_multiplier(Condition.EXCELLENT, has_box=False, has_papers=True)
        self.assertLess(no_papers, no_box)  # sin papeles vale menos que sin caja

    def test_full_set_is_baseline(self):
        m = grading.condition_multiplier(Condition.EXCELLENT, has_box=True, has_papers=True)
        self.assertAlmostEqual(m, 1.00, places=4)

    def test_condition_ordering(self):
        vals = [grading.CONDITION_MULTIPLIER[c] for c in
                [Condition.POOR, Condition.FAIR, Condition.GOOD, Condition.VERY_GOOD,
                 Condition.EXCELLENT, Condition.MINT, Condition.NEW_UNWORN]]
        self.assertEqual(vals, sorted(vals))  # monótono creciente


class TestPricing(unittest.TestCase):
    def test_liquidity_tiers(self):
        self.assertEqual(pricing.liquidity_tier(40), LiquidityTier.A)
        self.assertEqual(pricing.liquidity_tier(10), LiquidityTier.B)
        self.assertEqual(pricing.liquidity_tier(2), LiquidityTier.C)
        self.assertEqual(pricing.liquidity_tier(0), LiquidityTier.D)

    def test_realizable_below_fair_value(self):
        p = pricing.price_piece(_inst(), _listing())
        self.assertLess(p.realizable_value, p.fair_value)  # vendes al bid, no al mid

    def test_below_retail_signal(self):
        p = pricing.price_piece(_inst(retail_usd=10000), _listing(price_usd=9000))
        self.assertTrue(p.below_retail)

    def test_ci_widens_for_illiquid(self):
        a = pricing.price_piece(_inst(comparables_per_qtr=40), _listing())
        c = pricing.price_piece(_inst(comparables_per_qtr=2), _listing())
        width_a = (a.ci_high - a.fair_value) / a.fair_value
        width_c = (c.ci_high - c.fair_value) / c.fair_value
        self.assertGreater(width_c, width_a)


class TestCosts(unittest.TestCase):
    def test_landed_cost_positive(self):
        from the_cote_solo.costs import landed_cost
        b = landed_cost(11000, 11000, 45, ImportCostConfig())
        self.assertGreater(b["total"], 0)
        self.assertGreater(b["itbms"], 0)

    def test_zlc_zeroes_duty_and_tax(self):
        from the_cote_solo.costs import landed_cost
        b = landed_cost(11000, 11000, 45, ImportCostConfig.zlc_reexport())
        self.assertEqual(b["duty"], 0)
        self.assertEqual(b["itbms"], 0)


class TestVelocity(unittest.TestCase):
    def test_illiquid_sells_slower(self):
        fast, _ = velocity.expected_days_to_sell(LiquidityTier.A, Condition.EXCELLENT)
        slow, _ = velocity.expected_days_to_sell(LiquidityTier.C, Condition.EXCELLENT)
        self.assertGreater(slow, fast)

    def test_worse_condition_sells_slower(self):
        good, _ = velocity.expected_days_to_sell(LiquidityTier.A, Condition.NEW_UNWORN)
        bad, _ = velocity.expected_days_to_sell(LiquidityTier.A, Condition.FAIR)
        self.assertGreater(bad, good)

    def test_annualized_rewards_speed(self):
        # mismo edge absoluto, distinta velocidad -> el más rápido anualiza más
        fast = velocity.annualized_return(0.12, 30)
        slow = velocity.annualized_return(0.20, 180)
        self.assertGreater(fast, slow)

    def test_annualized_guards_total_loss(self):
        self.assertEqual(velocity.annualized_return(-1.0, 30), -1.0)

    def test_capital_turns(self):
        self.assertAlmostEqual(velocity.capital_turns_per_year(365), 1.0, places=3)


class TestArbitrage(unittest.TestCase):
    def test_clear_buy(self):
        # compra muy por debajo del fair value, buena procedencia, tier A
        o = evaluate(_inst(base_fair_value_usd=16000), _listing(price_usd=11000))
        self.assertEqual(o.verdict, "BUY")
        self.assertGreater(o.net_edge, MIN_NET_EDGE)
        self.assertGreater(o.score, 0)

    def test_overpriced_pass(self):
        o = evaluate(_inst(base_fair_value_usd=12000), _listing(price_usd=11800))
        self.assertEqual(o.verdict, "PASS")

    def test_unsafe_source_vetoes_even_with_huge_edge(self):
        # precio irrisorio (red flag) + vendedor desconocido sin señales
        bad = _listing(
            price_usd=4000, seller_type="unknown",
            signals={"account_age_months": 1, "completed_sales": 0, "real_photos": False},
        )
        o = evaluate(_inst(base_fair_value_usd=16000), bad)
        self.assertEqual(o.verdict, "UNSAFE_SOURCE")
        self.assertEqual(o.score, 0)  # nunca se rankea como compra

    def test_illiquid_needs_bigger_edge(self):
        # tier C: un edge que bastaría en A no basta aquí
        inst = _inst(base_fair_value_usd=13000, comparables_per_qtr=2)
        o = evaluate(inst, _listing(price_usd=11000))
        self.assertIn(o.verdict, ("ILLIQUID", "PASS"))
        self.assertNotEqual(o.verdict, "BUY")

    def test_net_edge_below_gross_edge(self):
        # el neto SIEMPRE es menor que el bruto (costos + realización)
        o = evaluate(_inst(base_fair_value_usd=16000), _listing(price_usd=11000))
        self.assertLess(o.net_edge, o.gross_edge)

    def test_opportunity_carries_cashflow_fields(self):
        o = evaluate(_inst(base_fair_value_usd=16000), _listing(price_usd=11000))
        self.assertGreater(o.days_to_sell, 0)
        self.assertGreater(o.capital_turns_per_year, 0)
        # con edge neto positivo, el anualizado supera al neto absoluto
        self.assertGreater(o.annualized_edge, o.net_edge)

    def test_slow_turn_gate(self):
        # edge absoluto por encima del piso, pero en un tier lento (B) con
        # condición pobre -> se realiza tan lento que falla el hurdle anualizado.
        inst = _inst(base_fair_value_usd=12800, comparables_per_qtr=6)  # tier B
        slow = _listing(price_usd=11000, condition_raw="fair, heavy wear")
        o = evaluate(inst, slow, ImportCostConfig.zlc_reexport())
        # o pasa el piso absoluto pero lo frena la velocidad, o queda en PASS:
        self.assertIn(o.verdict, ("SLOW_TURN", "PASS"))
        self.assertNotEqual(o.verdict, "BUY")

    def test_faster_turn_ranks_higher(self):
        # dos compras idénticas en edge, distinta liquidez -> la líquida (rota rápido)
        # debe rankear con mayor score
        fast = evaluate(_inst(base_fair_value_usd=16000, comparables_per_qtr=40),
                        _listing(price_usd=11000), ImportCostConfig.zlc_reexport())
        slower = evaluate(_inst(base_fair_value_usd=16000, comparables_per_qtr=6),
                          _listing(price_usd=11000), ImportCostConfig.zlc_reexport())
        if fast.verdict == "BUY" and slower.verdict == "BUY":
            self.assertGreater(fast.score, slower.score)


if __name__ == "__main__":
    unittest.main()
