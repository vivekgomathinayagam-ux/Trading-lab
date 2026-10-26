"""Shared day-trade core: features, rules, desk exits, and the lab engine loop.
Run: python -m unittest discover -s tests -t . -v
"""
import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from strategies.daytrade.core import (ORB, Bar, Desk, EMACross, Features, VolSpike,
                                      STOP_PCT, TARGET_PCT)
from lab.floor.engine import simulate

NY = ZoneInfo("America/New_York")


def day_bars(day, closes, vols=None, start=(9, 30)):
    t0 = datetime(day.year, day.month, day.day, *start, tzinfo=NY)
    out = []
    prev = closes[0]
    for i, c in enumerate(closes):
        o = prev
        v = (vols[i] if vols else 1000.0)
        out.append(Bar(t0 + timedelta(minutes=i), o, max(o, c) + 0.01, min(o, c) - 0.01, c, v))
        prev = c
    return out


D1 = datetime(2026, 10, 20)


class FeatureTests(unittest.TestCase):
    def test_opening_range_uses_first_15_minutes(self):
        closes = [100 + (i % 3) * 0.1 for i in range(15)] + [100.5] * 5
        f = Features()
        for b in day_bars(D1, closes):
            f.update(b)
        self.assertAlmostEqual(f.or_high, 100.2 + 0.01, places=6)
        self.assertTrue(f.or_done)

    def test_volume_ratio_uses_prior_bars_only(self):
        bars = day_bars(D1, [100] * 30, vols=[1000] * 29 + [5000])
        f = Features()
        for b in bars:
            f.update(b)
        self.assertAlmostEqual(f.vol_ratio, 5.0)
        self.assertTrue(f.volume_ok(3.0))
        self.assertFalse(f.volume_ok(6.0))

    def test_no_lookahead_changing_future_bars(self):
        base = [100 + 0.05 * i for i in range(60)]
        alt = base[:40] + [90] * 20
        r = VolSpike(2.0)
        sig_a, sig_b = [], []
        for closes, sig in ((base, sig_a), (alt, sig_b)):
            f = Features()
            vols = [1000] * 35 + [9000] + [1000] * 24
            for b in day_bars(D1, closes, vols):
                f.update(b)
                sig.append(r.signal(f, b))
        self.assertEqual(sig_a[:40], sig_b[:40])

    def test_same_minute_history_blocks_open_rush(self):
        f = Features()
        for k in range(4):   # 4 sessions where minute 6 always has 10x volume
            d = D1 + timedelta(days=k)
            vols = [1000] * 6 + [10000] + [1000] * 23
            for b in day_bars(d, [100] * 30, vols):
                f.update(b)
        d = D1 + timedelta(days=4)
        for b in day_bars(d, [100] * 7, [1000] * 6 + [10000]):
            f.update(b)
        self.assertGreaterEqual(f.vol_ratio, 3.0)
        self.assertFalse(f.volume_ok(3.0))   # normal for that minute, so not a spike


class DeskTests(unittest.TestCase):
    def setUp(self):
        self.d = Desk(rule=ORB())
        self.t = datetime(2026, 10, 20, 10, 0, tzinfo=NY)
        self.d.fill_entry("TQQQ", 100.0, self.t)

    def test_position_size_whole_shares_all_cash(self):
        self.assertEqual(self.d.pos.qty, 10)
        self.assertAlmostEqual(self.d.pos.stop, 100 * (1 - STOP_PCT))
        self.assertAlmostEqual(self.d.pos.target, 100 * (1 + TARGET_PCT))

    def test_stop_wins_when_bar_hits_both(self):
        b = Bar(self.t + timedelta(minutes=1), 100, 106, 97, 101, 1000)
        self.assertEqual(self.d.exit_check("TQQQ", b), ("stop", 97.5))

    def test_target(self):
        b = Bar(self.t + timedelta(minutes=1), 101, 105.5, 100.5, 105, 1000)
        self.assertEqual(self.d.exit_check("TQQQ", b), ("target", 105.0))

    def test_gap_through_stop_fills_at_open(self):
        b = Bar(self.t + timedelta(minutes=1), 96, 96.5, 95, 96, 1000)
        self.assertEqual(self.d.exit_check("TQQQ", b), ("stop", 96))

    def test_eod_flat_at_1555(self):
        b = Bar(datetime(2026, 10, 20, 15, 55, tzinfo=NY), 101, 101, 101, 101, 1000)
        self.assertEqual(self.d.exit_check("TQQQ", b), ("eod", 101))

    def test_one_entry_per_day(self):
        tr = self.d.fill_exit(105.0, self.t + timedelta(minutes=5), "target")
        self.assertAlmostEqual(tr["pnl_usd"], 50.0)
        f = Features()
        b = Bar(self.t + timedelta(minutes=30), 100, 101, 99, 100.5, 1000)
        f.update(b)
        self.assertFalse(self.d.wants_entry("SPY", b, f))

    def test_other_symbol_bar_does_not_exit(self):
        b = Bar(self.t + timedelta(minutes=1), 100, 200, 1, 100, 1000)
        self.assertIsNone(self.d.exit_check("SPY", b))


class EngineTests(unittest.TestCase):
    def _breakout_day(self, day, spike=True):
        closes = [100.0] * 15 + [100.0] * 5 + [101.0] + [101.2 + 0.25 * i for i in range(40)] + [111] * 10
        vols = [1000.0] * 20 + [(9000.0 if spike else 1000.0)] + [1000.0] * 50
        return day_bars(day, closes, vols)

    def test_orb_volume_trade_hits_target_and_compounds(self):
        bars = []
        for k in range(3):   # warm-up sessions with no breakout
            bars += day_bars(D1 + timedelta(days=k), [100.0] * 60)
        bars += self._breakout_day(D1 + timedelta(days=3))
        res = simulate({"SPY": bars}, [ORB()], slip_mult=0.0, warmup_days=3)
        d = res["desks"][0]
        self.assertEqual(len(d.trades), 1)
        self.assertEqual(d.trades[0]["reason"], "target")
        self.assertGreater(d.cash, 1000.0)

    def test_volume_filter_blocks_quiet_breakout(self):
        bars = []
        for k in range(3):
            bars += day_bars(D1 + timedelta(days=k), [100.0] * 60)
        bars += self._breakout_day(D1 + timedelta(days=3), spike=False)
        res = simulate({"SPY": bars}, [ORB(), ORB(None)], slip_mult=0.0, warmup_days=3)
        vol, plain = res["desks"]
        self.assertEqual(len(vol.trades), 0)
        self.assertEqual(len(plain.trades), 1)

    def test_entry_fills_next_bar_open(self):
        bars = []
        for k in range(3):
            bars += day_bars(D1 + timedelta(days=k), [100.0] * 60)
        day = self._breakout_day(D1 + timedelta(days=3))
        bars += day
        res = simulate({"SPY": bars}, [ORB()], slip_mult=0.0, warmup_days=3)
        t = res["desks"][0].trades[0]
        self.assertEqual(t["entry_px"], round(day[21].o, 4))   # signal on bar 20, fill at bar 21 open


class EmaTests(unittest.TestCase):
    def test_cross_up_detected_on_bucket_close(self):
        f = Features()
        closes = [100 - 0.02 * i for i in range(150)] + [97 + 0.08 * i for i in range(120)]
        crosses = []
        for b in day_bars(D1, closes[:270]):
            f.update(b)
            if f.cross_up:
                crosses.append(b.t)
        self.assertTrue(crosses)
        self.assertTrue(all((c.minute + 1) % 5 == 0 for c in crosses))


if __name__ == "__main__":
    unittest.main()
