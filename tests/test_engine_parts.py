import os
import tempfile
import unittest
from pathlib import Path

from engine import config
from engine.ledger import Ledger
from engine.shadow import ShadowSimulator
from engine.brokers.tradier import TradierBroker
from engine.risk import Order, OptionLeg
from strategies.registry import discover, load_runnable


class LedgerTests(unittest.TestCase):
    def test_trade_and_money_rows_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            led = Ledger(d)
            led.trade("order", "paper", "orb", "SPY", "buy", 1, price=580.0, source="tradier_sandbox")
            led.trade("shadow_fill", "paper", "orb", "SPY", "buy", 1, price=580.12, source="yahoo_rt")
            led.money_row("deposit", 50.0, "seed", note="own money cap")
            rows = led.read_rows("trades")
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[1]["event"], "shadow_fill")
            self.assertTrue(rows[0]["ts"])
            money = led.read_rows("money")
            self.assertEqual(money[0]["amount"], "50.0")
            hb = led.heartbeat("ok", {"x": 1})
            self.assertIn("as_of", hb.read_text())


class ShadowTests(unittest.TestCase):
    def test_slippage_direction(self):
        self.assertGreater(ShadowSimulator.apply_slippage(100.0, "buy", 2), 100.0)
        self.assertLess(ShadowSimulator.apply_slippage(100.0, "sell", 2), 100.0)
        self.assertAlmostEqual(ShadowSimulator.apply_slippage(100.0, "buy", 2), 100.02)


class ConfigTests(unittest.TestCase):
    def test_live_mode_needs_both_token_and_flag(self):
        env = {"TRADIER_SANDBOX_TOKEN": "x"}
        with unittest.mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(config.load().mode, "paper")
        with unittest.mock.patch.dict(os.environ, {**env, "TRADIER_LIVE_TOKEN": "y"}, clear=True):
            self.assertEqual(config.load().mode, "paper")
        with unittest.mock.patch.dict(os.environ, {**env, "LIVE_TRADING_ENABLED": "true"}, clear=True):
            self.assertEqual(config.load().mode, "paper")
        with unittest.mock.patch.dict(os.environ, {**env, "TRADIER_LIVE_TOKEN": "y",
                                                   "LIVE_TRADING_ENABLED": "true"}, clear=True):
            self.assertEqual(config.load().mode, "live")

    def test_redacted_never_contains_token(self):
        with unittest.mock.patch.dict(os.environ, {"TRADIER_SANDBOX_TOKEN": "SECRET123"}, clear=True):
            self.assertNotIn("SECRET123", str(config.load().redacted()))


class TradierAdapterTests(unittest.TestCase):
    def test_order_translation(self):
        o = Order("t", "SPY", "equity", "buy", 2, 10.0, 1160.0)
        d = TradierBroker._to_tradier(o)
        self.assertEqual(d["class"], "equity")
        self.assertEqual(d["quantity"], "2")
        legs = [OptionLeg("SPY251017C00580000", "buy_to_open", 1, 580, "call", "2025-10-17"),
                OptionLeg("SPY251017C00581000", "sell_to_open", 1, 581, "call", "2025-10-17")]
        s = Order("t", "SPY", "spread", "buy", 1, 40.0, 40.0, legs=legs)
        d = TradierBroker._to_tradier(s)
        self.assertEqual(d["class"], "multileg")
        self.assertEqual(d["side[1]"], "sell_to_open")

    def test_paper_adapter_refuses_live_order_without_network(self):
        b = TradierBroker.__new__(TradierBroker)
        b.live = False
        r = b.place(Order("t", "SPY", "equity", "buy", 1, 1.0, 1.0, mode="live"))
        self.assertFalse(r.ok)
        self.assertIn("refused", r.status)


class RegistryTests(unittest.TestCase):
    def test_discover_finds_specs_and_runs_none_yet(self):
        names = {c.name for c in discover()}
        self.assertTrue({"orb", "cvd_turn", "gex_spreads", "controls"} <= names)
        self.assertEqual(load_runnable(), [])


import unittest.mock  # noqa: E402

if __name__ == "__main__":
    unittest.main()
