"""Every risk cap must block an order that breaks it, and a clean order must pass.
Run:  python -m unittest discover -s tests -v   (or: pytest)
"""
import unittest

from engine.risk import AccountState, Order, OptionLeg, RiskEngine


def live_acct(**kw) -> AccountState:
    base = dict(equity=1000.0, peak_equity=1000.0, start_of_day_equity=1000.0,
                settled_cash=1000.0, mode="live", live_token_present=True)
    base.update(kw)
    return AccountState(**base)


def paper_acct(**kw) -> AccountState:
    base = dict(equity=1000.0, peak_equity=1000.0, start_of_day_equity=1000.0,
                settled_cash=1000.0, mode="paper", live_token_present=False)
    base.update(kw)
    return AccountState(**base)


def equity_order(mode="paper", **kw) -> Order:
    base = dict(strategy="test", symbol="SPY", asset_type="equity", side="buy",
                qty=1, max_loss=20.0, cost=580.0, mode=mode)
    base.update(kw)
    return Order(**base)


class CleanOrderPasses(unittest.TestCase):
    def test_paper_equity_passes(self):
        v = RiskEngine().check(equity_order(), paper_acct())
        self.assertTrue(v.allowed, v.reasons)

    def test_live_equity_passes_with_token(self):
        v = RiskEngine().check(equity_order(mode="live"), live_acct())
        self.assertTrue(v.allowed, v.reasons)

    def test_defined_risk_vertical_passes(self):
        legs = [OptionLeg("SPY251017C00580000", "buy_to_open", 1, 580, "call", "2025-10-17"),
                OptionLeg("SPY251017C00581000", "sell_to_open", 1, 581, "call", "2025-10-17")]
        o = Order(strategy="t", symbol="SPY", asset_type="spread", side="buy", qty=1,
                  max_loss=40.0, cost=40.0, legs=legs)
        v = RiskEngine().check(o, paper_acct())
        self.assertTrue(v.allowed, v.reasons)


class EveryCapBlocks(unittest.TestCase):
    def test_live_gate_blocks_without_live_token(self):
        v = RiskEngine().check(equity_order(mode="live"), live_acct(live_token_present=False))
        self.assertFalse(v.allowed)
        self.assertFalse(v.checks["live_gate"])

    def test_live_gate_blocks_when_account_in_paper_mode(self):
        v = RiskEngine().check(equity_order(mode="live"), paper_acct(live_token_present=True))
        self.assertFalse(v.checks["live_gate"])

    def test_per_trade_cap_blocks_over_5pct(self):
        # 5% of $1000 = $50; a $51 max loss must be refused
        v = RiskEngine().check(equity_order(max_loss=51.0), paper_acct())
        self.assertFalse(v.allowed)
        self.assertFalse(v.checks["max_loss_per_trade"])

    def test_per_trade_cap_allows_exactly_5pct(self):
        v = RiskEngine().check(equity_order(max_loss=50.0), paper_acct())
        self.assertTrue(v.checks["max_loss_per_trade"])

    def test_per_trade_cap_blocks_option_too_big_for_small_account(self):
        # $50 account: a $100-wide spread risking $60 is too big. Rule 6.
        o = Order(strategy="t", symbol="SPY", asset_type="option", side="buy_to_open",
                  qty=1, max_loss=60.0, cost=60.0, mode="paper")
        v = RiskEngine().check(o, paper_acct(equity=50.0, peak_equity=50.0,
                                             start_of_day_equity=50.0, settled_cash=50.0))
        self.assertFalse(v.checks["max_loss_per_trade"])
        self.assertIn("too small", " ".join(v.reasons))

    def test_daily_loss_stop_blocks_new_live_entries(self):
        # start of day $1000, now $900 = 10% loss -> no new live entries
        v = RiskEngine().check(equity_order(mode="live"), live_acct(equity=900.0, peak_equity=1000.0))
        self.assertFalse(v.allowed)
        self.assertFalse(v.checks["daily_loss_stop"])

    def test_daily_loss_stop_still_allows_live_exits(self):
        v = RiskEngine().check(equity_order(mode="live", side="sell", is_entry=False, max_loss=0, cost=0),
                               live_acct(equity=900.0, peak_equity=1000.0))
        self.assertTrue(v.checks["daily_loss_stop"])
        self.assertTrue(v.allowed, v.reasons)

    def test_daily_loss_stop_does_not_block_paper(self):
        v = RiskEngine().check(equity_order(), paper_acct(equity=900.0, peak_equity=1000.0))
        self.assertTrue(v.checks["daily_loss_stop"])

    def test_drawdown_kill_blocks_all_live(self):
        # peak $1000, now $700 = 30% drawdown -> even exits refused live
        acct = live_acct(equity=700.0, peak_equity=1000.0, start_of_day_equity=700.0)
        v_entry = RiskEngine().check(equity_order(mode="live"), acct)
        v_exit = RiskEngine().check(equity_order(mode="live", side="sell", is_entry=False,
                                                 max_loss=0, cost=0), acct)
        self.assertFalse(v_entry.checks["drawdown_kill"])
        self.assertFalse(v_exit.checks["drawdown_kill"])
        self.assertFalse(v_entry.allowed)
        self.assertFalse(v_exit.allowed)

    def test_kill_switch_is_sticky(self):
        # equity recovered but switch still on -> still blocked until human reset
        v = RiskEngine().check(equity_order(mode="live"), live_acct(kill_switch_on=True))
        self.assertFalse(v.checks["drawdown_kill"])

    def test_margin_blocked(self):
        v = RiskEngine().check(equity_order(uses_margin=True), paper_acct())
        self.assertFalse(v.checks["no_margin"])
        self.assertFalse(v.allowed)

    def test_naked_short_option_blocked(self):
        o = Order(strategy="t", symbol="SPY", asset_type="option", side="sell_to_open",
                  qty=1, max_loss=10.0, cost=0.0)
        v = RiskEngine().check(o, paper_acct())
        self.assertFalse(v.checks["defined_risk"])
        self.assertFalse(v.allowed)

    def test_ratio_spread_with_extra_short_blocked(self):
        legs = [OptionLeg("A", "buy_to_open", 1, 580, "call", "2025-10-17"),
                OptionLeg("B", "sell_to_open", 2, 585, "call", "2025-10-17")]
        o = Order(strategy="t", symbol="SPY", asset_type="spread", side="sell", qty=1,
                  max_loss=10.0, cost=0.0, legs=legs)
        v = RiskEngine().check(o, paper_acct())
        self.assertFalse(v.checks["defined_risk"])

    def test_short_equity_blocked(self):
        v = RiskEngine().check(equity_order(side="sell", is_entry=True), paper_acct())
        self.assertFalse(v.checks["defined_risk"])

    def test_fractional_blocked_until_confirmed(self):
        v = RiskEngine().check(equity_order(qty=0.5, cost=290, max_loss=10), paper_acct())
        self.assertFalse(v.checks["whole_units"])
        v2 = RiskEngine().check(equity_order(qty=0.5, cost=290, max_loss=10, fractional_ok=True),
                                paper_acct())
        self.assertTrue(v2.checks["whole_units"])

    def test_unsettled_cash_blocked(self):
        v = RiskEngine().check(equity_order(cost=580.0), paper_acct(settled_cash=500.0))
        self.assertFalse(v.checks["settled_cash"])
        self.assertFalse(v.allowed)

    def test_zero_qty_blocked(self):
        v = RiskEngine().check(equity_order(qty=0), paper_acct())
        self.assertFalse(v.checks["sane"])


class Sizing(unittest.TestCase):
    def test_max_qty_respects_loss_cap_and_cash(self):
        eng = RiskEngine()
        acct = paper_acct(equity=1000.0, settled_cash=1000.0)
        # $10 risk per share, $580 per share: loss cap allows 5, cash allows 1
        self.assertEqual(eng.max_qty(acct, loss_per_unit=10.0, cost_per_unit=580.0), 1)
        # cheap stock: loss cap binds
        self.assertEqual(eng.max_qty(acct, loss_per_unit=10.0, cost_per_unit=50.0), 5)

    def test_max_qty_zero_when_nothing_fits(self):
        acct = paper_acct(equity=50.0, settled_cash=50.0)
        self.assertEqual(RiskEngine().max_qty(acct, loss_per_unit=60.0, cost_per_unit=60.0), 0)


if __name__ == "__main__":
    unittest.main()
