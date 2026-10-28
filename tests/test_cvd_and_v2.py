"""CVD turn (cvd_spy / cvd_tqqq) and ema_vol_v2: rules added 2026-10-28.

Covers: close-location delta, 3-minute clock candles (incl. a missing last bar), buy/sell turns,
the fast-spike skip, no look-ahead, next-bar fills for signal exits, clock buckets in v2, and that
the original desks trade identically with the new desks present.
"""
import random
import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from lab.floor.engine import simulate
from strategies.daytrade.core import (ORB, PAPER_RULES, Bar, CVDTurn, Desk, EMACross, EMACrossV2,
                                      Features, VolSpike, _CVD3)

NY = ZoneInfo("America/New_York")
T0 = datetime(2026, 10, 5, 9, 30, tzinfo=NY)


def bar(m, o, h, l, c, v=1000.0, day=T0):
    return Bar(day + timedelta(minutes=m), o, h, l, c, v)


def up(m, v=1000.0, px=100.0, day=T0):      # closes at its high: delta = +v
    return bar(m, px, px + 0.1, px - 0.1, px + 0.1, v, day)


def dn(m, v=1000.0, px=100.0):      # closes at its low: delta = -v
    return bar(m, px, px + 0.1, px - 0.1, px - 0.1, v)


def random_days(seed=5, days=8, syms=("SPY", "QQQ", "TQQQ", "UPRO", "SQQQ", "SPXU"), drop=0.0):
    rng = random.Random(seed)
    out = {}
    for k, s in enumerate(syms):
        px, bars, d = 100.0 + k, [], datetime(2026, 9, 1, 9, 30, tzinfo=NY)
        for _ in range(days):
            while d.weekday() >= 5:
                d += timedelta(days=1)
            for m in range(390):
                r = rng.gauss(0, 0.0012)
                o, c = px, px * (1 + r)
                v = 2000 * (6 if rng.random() < 0.02 else 1) * (1 + rng.random())
                if rng.random() >= drop:
                    bars.append(Bar(d + timedelta(minutes=m), o, max(o, c) * 1.0004, min(o, c) * 0.9996, c, v))
                px = c
            d += timedelta(days=1)
        out[s] = bars
    return out


class CVDCandleTests(unittest.TestCase):
    def test_close_location_delta_and_candle_close(self):
        c = _CVD3()
        self.assertIsNone(c.update(up(0, 500)))
        self.assertIsNone(c.update(dn(1, 200)))
        c.update(bar(2, 100, 100.1, 99.9, 100.0, 999))     # closes mid-range: delta 0
        self.assertEqual(c.cvd, [300.0])                   # candle 09:30-09:32 closed on its 3rd bar

    def test_missing_last_bar_closes_on_next_candle(self):
        c = _CVD3()
        c.update(up(0, 100))
        c.update(up(1, 100))                               # 09:32 bar missing
        self.assertEqual(c.cvd, [])
        c.update(dn(3, 50))                                # first bar of 09:33 candle
        self.assertEqual(c.cvd, [200.0])                   # old candle closed, new bar not in it
        c.update(dn(4, 50)); c.update(dn(5, 50))
        self.assertEqual(c.cvd, [200.0, 50.0])

    def _feed(self, c, pattern):
        """pattern = list of candle deltas; each candle = 3 bars, delta on the first bar."""
        evs = []
        for i, dlt in enumerate(pattern):
            m = i * 3
            b0 = up(m, dlt) if dlt >= 0 else dn(m, -dlt)
            evs.append([c.update(b0), c.update(bar(m + 1, 100, 100.1, 99.9, 100.0)),
                        c.update(bar(m + 2, 100, 100.1, 99.9, 100.0))][-1])
        return evs

    def test_buy_turn_from_five_candle_low(self):
        c = _CVD3()
        evs = self._feed(c, [100, -50, -50, -50, -50, -50, 30])
        # CVD: 100,50,0,-50,-100,-150, -120 -> candle 5 is the 5-candle low, candle 6 rises
        self.assertEqual(evs[-1], "buy")
        self.assertEqual(evs[:-1].count("buy"), 0)

    def test_sell_turn_from_five_candle_high(self):
        c = _CVD3()
        evs = self._feed(c, [-100, 50, 50, 50, 50, 50, -30])
        self.assertEqual(evs[-1], "sell")

    def test_needs_five_candles(self):
        c = _CVD3()
        evs = self._feed(c, [-50, -50, -50, -50, 30])
        self.assertNotIn("buy", evs)

    def test_fast_spike_skips_entry(self):
        r = CVDTurn("SPY")
        f = Features()
        for i, dlt in enumerate([100, -50, -50, -50, -50, -50]):
            m = i * 3
            for b in (up(m, dlt) if dlt >= 0 else dn(m, -dlt), bar(m + 1, 100, 100.1, 99.9, 100), bar(m + 2, 100, 100.1, 99.9, 100)):
                r.observe("SPY", b)
        m = 18                                            # turn candle with a 10x range
        b0 = bar(m, 100, 101.0, 99.0, 101.0, 30)
        r.observe("SPY", b0); r.observe("SPY", bar(m + 1, 100, 100.1, 99.9, 100))
        last = bar(m + 2, 100, 100.1, 99.9, 100)
        r.observe("SPY", last)
        self.assertEqual(r.last[1], "buy")
        self.assertTrue(r.last[2])
        self.assertFalse(r.signal(f, last))

    def test_other_symbols_ignored_and_reset_daily(self):
        r = CVDTurn("TQQQ")
        self.assertIsNone(r.observe("SPY", up(0)))
        r.observe("TQQQ", up(0)); r.observe("TQQQ", up(1)); r.observe("TQQQ", up(2))
        self.assertEqual(len(r.cvd.cvd), 1)
        r.observe("TQQQ", up(0, day=T0 + timedelta(days=1)))
        self.assertEqual(r.cvd.cvd, [])


class NoLookAheadTests(unittest.TestCase):
    def test_changing_future_bars_never_changes_past_events(self):
        days = random_days(seed=11, days=2, syms=("SPY",))["SPY"]
        cut = 300
        base = _CVD3()
        ev1 = [base.update(b) for b in days]
        rng = random.Random(1)
        changed = days[:cut] + [Bar(b.t, b.o, b.h * (1 + rng.random() / 50), b.l, b.c * (1 + rng.random() / 100), b.v * 7)
                                for b in days[cut:]]
        other = _CVD3()
        ev2 = [other.update(b) for b in changed]
        self.assertEqual(ev1[:cut], ev2[:cut])


class SignalExitFillTests(unittest.TestCase):
    def test_signal_exit_fills_at_next_bar_open(self):
        bars = random_days(seed=3, days=10)
        res = simulate(bars, [CVDTurn("SPY"), CVDTurn("TQQQ")])
        by = {s: {b.t: b for b in v} for s, v in bars.items()}
        sig = [(d, t) for d in res["desks"] for t in d.trades if t["reason"] == "cvd_sell"]
        self.assertTrue(sig, "synthetic data should produce some CVD sell exits")
        for d, t in sig:
            exit_t = datetime.fromisoformat(t["exit_t"])
            b = by[t["sym"]][exit_t]
            from strategies.daytrade.core import SLIP
            self.assertAlmostEqual(t["exit_px"], round(b.o * (1 - SLIP[t["sym"]]), 4), places=4)
        for d in res["desks"]:
            days = [t["entry_t"][:10] for t in d.trades]
            self.assertEqual(len(days), len(set(days)))       # one entry per day


class EmaV2Tests(unittest.TestCase):
    def test_v2_equals_v1_when_no_bars_missing(self):
        bars = random_days(seed=8, days=8)
        res = simulate(bars, [EMACross(), EMACrossV2()])
        a, b = res["desks"]
        strip = lambda ts: [(t["sym"], t["entry_t"], t["exit_t"], t["pnl_usd"]) for t in ts]  # noqa: E731
        self.assertEqual(strip(a.trades), strip(b.trades))

    def test_v2_closes_bucket_when_boundary_bar_missing(self):
        f = Features()
        for m in range(0, 4):                      # 09:30-09:33, 09:34 missing
            f.update(up(m))
        self.assertEqual(f.ema2_n, 0)
        f.update(up(5))                            # 09:35 arrives: old bucket closes, by clock
        self.assertEqual(f.ema2_n, 1)
        self.assertEqual(f.ema_n, 0)               # v1 still waiting (the original behaviour)


class OriginalDesksUnchanged(unittest.TestCase):
    def test_original_desks_identical_with_new_desks_present(self):
        bars = random_days(seed=21, days=10, drop=0.03)
        orig = lambda: [ORB(), EMACross(), VolSpike(), ORB(None), EMACross(None), VolSpike(2.0)]  # noqa: E731
        alone = simulate(bars, orig())
        mixed = simulate(bars, orig() + [EMACrossV2(), CVDTurn("SPY"), CVDTurn("TQQQ")])
        A = {d.key: d.trades for d in alone["desks"]}
        B = {d.key: d.trades for d in mixed["desks"]}
        for k, v in A.items():
            self.assertEqual(v, B[k], k)

    def test_paper_rules_keys_unique_and_originals_first(self):
        keys = [r.key for r in PAPER_RULES]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(keys[:3], ["orb_vol", "ema_vol", "volspike"])

    def test_base_rule_observe_is_noop(self):
        d = Desk(rule=EMACross())
        self.assertIsNone(d.rule.observe("SPY", up(0)))


if __name__ == "__main__":
    unittest.main()
