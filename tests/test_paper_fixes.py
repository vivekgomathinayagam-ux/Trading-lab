"""2026-11-17 paper-only fixes: CVD symbol guard and read-only bar / entry-context logging."""
import csv
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from engine.barlog import BarLog
from strategies.daytrade.core import Bar, CVDTurn, Desk, Features

NY = ZoneInfo("America/New_York")
T0 = datetime(2026, 11, 17, 9, 30, tzinfo=NY)


class CVDSymbolGuard(unittest.TestCase):
    def test_cvd_desk_ignores_other_symbols_bar_at_the_same_minute(self):
        rule = CVDTurn("SPY")
        t = T0 + timedelta(minutes=30)
        d = Desk(rule=rule)                                # Desk() resets the rule, so set last after
        rule.last = (t, "buy", False)                      # SPY's CVD just turned up on this bar
        b = Bar(t, 100, 100.1, 99.9, 100.1, 1000)
        f = Features()
        self.assertTrue(d.wants_entry("SPY", b, f))
        self.assertFalse(d.wants_entry("TQQQ", b, f))      # same timestamp, other symbol: no entry
        self.assertFalse(d.wants_entry("QQQ", b, f))


class BarLogTests(unittest.TestCase):
    def test_rows_and_entry_context(self):
        d = Path(tempfile.mkdtemp())
        bl = BarLog(d)
        px = 100.0
        for i in range(20):
            b = Bar(T0 + timedelta(minutes=i), px, px + 0.2, px - 0.1, px + 0.1, 1000)
            bl.bar("SPY", b, T0 + timedelta(minutes=i, seconds=5), True, True)
            px += 0.1
        bl.entry("cvd_spy", "SPY", b.t, 102.0, T0 + timedelta(minutes=20))
        bars = list(csv.DictReader((d / "daytrade_bars_2026-11-17.csv").open()))
        self.assertEqual(len(bars), 20)
        ctx = list(csv.DictReader((d / "daytrade_entry_context.csv").open()))
        self.assertEqual(len(ctx), 1)
        self.assertGreater(float(ctx[0]["ret_open_pct"]), 0)
        self.assertGreater(float(ctx[0]["atr14_pct"]), 0)

    def test_write_failure_never_raises(self):
        bl = BarLog(Path("/nonexistent/dir"))
        b = Bar(T0, 100, 101, 99, 100, 10)
        bl.bar("SPY", b, T0, True, True)
        bl.entry("x", "SPY", T0, 100.0, T0)


class RetiredDesks(unittest.TestCase):
    def test_cvd_not_in_paper_and_books_kept(self):
        import json
        from unittest import mock
        from engine.daytrade_runner import DayTradeRunner
        from strategies.daytrade.core import PAPER_RULES, RETIRED_RULES
        keys = [r.key for r in PAPER_RULES]
        for k in RETIRED_RULES:
            self.assertNotIn(k, keys)
        d = Path(tempfile.mkdtemp())
        (d / "daytrade_books.json").write_text(json.dumps({"desks": {
            "orb_vol": {"cash": 950.0}, "cvd_tqqq": {"cash": 917.32, "equity": 917.32}}}))
        r = DayTradeRunner(mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock(), d)
        r.load(); r.save({})
        out = json.loads((d / "daytrade_books.json").read_text())
        self.assertNotIn("cvd_tqqq", out["desks"])
        self.assertEqual(out["retired"]["cvd_tqqq"]["equity"], 917.32)
        r.load(); r.save({})                                   # survives a second restart
        self.assertIn("cvd_tqqq", json.loads((d / "daytrade_books.json").read_text())["retired"])


if __name__ == "__main__":
    unittest.main()
