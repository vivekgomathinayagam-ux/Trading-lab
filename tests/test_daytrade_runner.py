import csv
import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from engine.brokers.base import OrderResult
from engine.daytrade_runner import DayTradeRunner
from engine.ledger import Ledger
from engine.risk import RiskEngine
from strategies.daytrade.core import ORB, Bar

NY = ZoneInfo("America/New_York")
DAY = datetime(2026, 10, 27, 9, 30, tzinfo=NY)


def make_day(d0, closes, vols):
    out, prev = [], closes[0]
    for i, c in enumerate(closes):
        out.append(Bar(d0 + timedelta(minutes=i), prev, max(prev, c) + 0.01, min(prev, c) - 0.01, c, vols[i]))
        prev = c
    return out


class FakeMD:
    """Serves bars up to 'now' like Yahoo would (completed minutes only)."""
    def __init__(self, history, today):
        self.history, self.today = history, today

    def bars(self, sym, rng="1d", now=None):
        if sym != "SPY":
            return [], None
        if rng == "5d":
            return list(self.history), None
        done = [b for b in self.today if b.t + timedelta(minutes=1) <= now]
        return done, (done[-1].c if done else None)


class FakeBroker:
    def __init__(self):
        self.orders = []

    def place(self, order, preview=False):
        self.orders.append(order)
        return OrderResult(True, str(len(self.orders)), "ok", {})


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        hist = []
        for k in range(4):
            hist += make_day(DAY - timedelta(days=k + 1), [100.0] * 390, [1000.0] * 390)
        hist.sort(key=lambda b: b.t)
        closes = [100.0] * 20 + [101.0] + [101.2 + 0.25 * i for i in range(40)] + [111.0] * 329
        vols = [1000.0] * 20 + [9000.0] + [1000.0] * 369
        self.today = make_day(DAY, closes, vols)
        self.md = FakeMD(hist, self.today)
        self.broker = FakeBroker()
        self.ledger = Ledger(str(self.dir))

    def runner(self):
        return DayTradeRunner(self.ledger, self.broker, RiskEngine(), self.md, self.dir,
                              symbols=["SPY"], rules=[ORB()])

    def test_trades_breakout_hits_target_and_persists(self):
        r = self.runner()
        for i in range(1, 70):
            r.step(DAY + timedelta(minutes=i, seconds=5))
        desk = r.desks["orb_vol"]
        self.assertIsNone(desk.pos)
        rows = list(csv.DictReader((self.dir / "daytrade_trades.csv").open()))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["reason"], "target")
        self.assertGreater(float(rows[0]["pnl_usd"]), 0)
        self.assertEqual([o.side for o in self.broker.orders], ["buy", "sell"])
        self.assertTrue(all(o.mode == "paper" for o in self.broker.orders))
        books = json.loads((self.dir / "daytrade_books.json").read_text())
        self.assertGreater(books["desks"]["orb_vol"]["cash"], 1000)
        # restart: state reloads, no second entry the same day
        r2 = self.runner()
        self.assertEqual(r2.desks["orb_vol"].cash, desk.cash)
        for i in range(70, 120):
            r2.step(DAY + timedelta(minutes=i, seconds=5))
        self.assertEqual(len(self.broker.orders), 2)

    def test_stale_signal_after_outage_is_not_traded(self):
        r = self.runner()
        r.step(DAY + timedelta(minutes=1, seconds=5))
        r.step(DAY + timedelta(minutes=40, seconds=5))   # bot was down while the breakout happened
        self.assertEqual(self.broker.orders, [])

    def test_safety_flat_before_close(self):
        r = self.runner()
        for i in range(1, 25):
            r.step(DAY + timedelta(minutes=i, seconds=5))
        d = r.desks["orb_vol"]
        self.assertIsNotNone(d.pos)
        d.pos.target = 1e9   # make sure the target can't close it first
        r.step(DAY.replace(hour=15, minute=58, second=30))
        self.assertIsNone(d.pos)
        rows = list(csv.DictReader((self.dir / "daytrade_trades.csv").open()))
        self.assertIn(rows[-1]["reason"], ("eod", "eod_safety"))


if __name__ == "__main__":
    unittest.main()
