"""Tests for the Crypto Pier backtest lab: fills, fees, stops, sizing, no look-ahead."""
import unittest

import numpy as np
import pandas as pd

from lab.crypto import data as D
from lab.crypto import strategies as S
from lab.crypto.engine import Costs, Signals, metrics, run

FREE = Costs(0.0, 0.0)


def bars(closes, opens=None, highs=None, lows=None, freq="1D"):
    c = np.asarray(closes, float)
    o = np.asarray(opens if opens is not None else np.r_[c[0], c[:-1]], float)
    h = np.asarray(highs if highs is not None else np.maximum(o, c), float)
    lo = np.asarray(lows if lows is not None else np.minimum(o, c), float)
    idx = pd.date_range("2020-01-01", periods=len(c), freq=freq, tz="UTC")
    return pd.DataFrame({"open": o, "high": h, "low": lo, "close": c, "volume": 1.0}, index=idx)


def sig(n, enter_at=(), exit_at=(), stop=np.nan, target=1.0, trail=False, max_hold=None):
    e = np.zeros(n, bool); x = np.zeros(n, bool)
    e[list(enter_at)] = True; x[list(exit_at)] = True
    return Signals(e, x, np.full(n, stop, float), np.full(n, target, float), trail, max_hold)


class TestFills(unittest.TestCase):
    def test_entry_fills_next_open_not_signal_close(self):
        df = bars([100, 100, 100, 100], opens=[100, 100, 120, 120])
        res = run(df, sig(4, enter_at=[1], exit_at=[2]), FREE)
        t = res.trades[0]
        self.assertEqual(t.entry_px, 120.0)  # bar 2's open, not bar 1's close (100)
        self.assertEqual(t.entry_time, df.index[2])

    def test_fees_and_slippage_charged_both_sides(self):
        df = bars([100] * 5)
        res = run(df, sig(5, enter_at=[0], exit_at=[2]), Costs(0.01, 0.0))
        # 1% in, 1% out on a flat price: roughly -2% of equity
        self.assertAlmostEqual(res.equity.iloc[-1], 1000 * (1 - 0.01) / (1 + 0.01) + 0, delta=1.0)
        self.assertLess(res.trades[0].pnl_pct, -1.9)

    def test_signal_exit_fills_next_open(self):
        df = bars([100, 100, 110, 110, 90], opens=[100, 100, 100, 130, 90])
        res = run(df, sig(5, enter_at=[0], exit_at=[2]), FREE)
        self.assertEqual(res.trades[0].exit_px, 130.0)


class TestStops(unittest.TestCase):
    def test_stop_fills_at_stop_when_touched(self):
        df = bars([100, 100, 100, 100], lows=[100, 100, 89, 100])
        res = run(df, sig(4, enter_at=[0], stop=10.0), FREE)
        self.assertEqual(res.trades[0].reason, "stop")
        self.assertAlmostEqual(res.trades[0].exit_px, 90.0)

    def test_gap_through_stop_fills_at_open(self):
        df = bars([100, 100, 80, 80], opens=[100, 100, 75, 80], lows=[100, 100, 70, 80])
        res = run(df, sig(4, enter_at=[0], stop=10.0), FREE)
        self.assertAlmostEqual(res.trades[0].exit_px, 75.0)  # worse than the 90 stop

    def test_stop_active_on_entry_bar(self):
        df = bars([100, 100, 100], opens=[100, 100, 100], lows=[100, 85, 100])
        res = run(df, sig(3, enter_at=[0], stop=10.0), FREE)
        self.assertEqual(res.trades[0].exit_time, df.index[1])
        self.assertAlmostEqual(res.trades[0].exit_px, 90.0)

    def test_trailing_stop_only_moves_up(self):
        df = bars([100, 120, 110, 100], lows=[100, 100, 109, 95])
        res = run(df, sig(4, enter_at=[0], stop=10.0, trail=True), FREE)
        # after the 120 close the stop trails to 110; the next low of 109 hits it
        self.assertEqual(res.trades[0].reason, "stop")
        self.assertAlmostEqual(res.trades[0].exit_px, 110.0)

    def test_time_exit(self):
        df = bars([100] * 10)
        res = run(df, sig(10, enter_at=[0], max_hold=3), FREE)
        self.assertEqual(res.trades[0].reason, "time")


class TestRiskSizing(unittest.TestCase):
    def test_risk_sizing_caps_stop_loss_near_5pct(self):
        df = bars([100, 100, 100, 100], lows=[100, 100, 79, 100])
        res = run(df, sig(4, enter_at=[0], stop=20.0), FREE, sizing="risk", risk_cap=0.05)
        t = res.trades[0]
        self.assertAlmostEqual(t.frac, 0.25, places=3)       # 5% / 20% stop distance
        self.assertAlmostEqual(t.pnl_pct, -5.0, places=1)
        self.assertAlmostEqual(t.r_mult, -1.0, places=2)

    def test_risk_sizing_without_stop_does_not_trade(self):
        df = bars([100] * 4)
        res = run(df, sig(4, enter_at=[0]), FREE, sizing="risk")
        self.assertEqual(len(res.trades), 0)

    def test_full_sizing_never_exceeds_equity(self):
        df = bars([100] * 4)
        res = run(df, sig(4, enter_at=[0], target=1.0), Costs(0.01, 0.001))
        self.assertGreaterEqual(res.equity.min(), 0.0)


class TestNoLookAhead(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(3)
        n = 24 * 400
        c = 100 * np.exp(np.cumsum(rng.standard_normal(n) * 0.01))
        self.h = bars(c, freq="1h")
        self.h["high"] *= 1.003
        self.h["low"] *= 0.997
        self.d = D.resample(self.h, "1D", 20)

    def _check(self, builder, df, daily, **kw):
        a = builder(df, daily, **kw)
        k = 50  # change the last k bars violently; earlier signals must not move
        df2 = df.copy()
        df2.iloc[-k:, :4] *= 3.0
        daily2 = D.resample(df2, "1D", 20) if daily is not None and df.index.freq != daily.index.freq else daily
        b = builder(df2, daily2, **kw)
        cut = len(df) - k - 25  # a day of margin for the prior-day filter
        for f in ("enter", "exit"):
            self.assertTrue(np.array_equal(getattr(a, f)[:cut], getattr(b, f)[:cut]), f"{builder.__name__}.{f}")
        np.testing.assert_allclose(a.stop_dist[:cut], b.stop_dist[:cut], equal_nan=True)

    def test_daily_strategies_causal(self):
        d = self.d
        for b, kw in [(S.trend_sma, {}), (S.trend_voltarget, {}), (S.donchian, {}), (S.rsi2_meanrev, {"trend_n": 50}),
                      (S.extreme_drop_bounce, {}), (S.momentum_burst, {}), (S.squeeze_breakout, {"squeeze_n": 30})]:
            self._check(b, d, d, **kw)

    def test_intraday_strategies_causal(self):
        for b in (S.intraday_breakout, S.intraday_meanrev):
            self._check(b, self.h, self.d)

    def test_prior_day_filter_uses_yesterday(self):
        ok = S.prior_day_filter(self.h, self.d, 5)
        # every hour of a day carries one value, equal to the previous day's verdict
        verdict = (self.d["close"] > S.sma(self.d["close"], 5)).shift(1).fillna(False)
        day = self.d.index[100]
        hours = ok[(ok.index >= day) & (ok.index < day + pd.Timedelta("1D"))]
        self.assertTrue((hours == bool(verdict.loc[day])).all())

    def test_donchian_level_excludes_current_bar(self):
        df = bars([10, 11, 12, 13, 14, 15])
        s = S.donchian(df, df, entry_n=2, exit_n=2, atr_n=1)
        # close 12 at bar 2 breaks the prior two highs (10, 11)
        self.assertTrue(s.enter[2])

    def test_drop_bounce_enters_on_single_day_drop(self):
        df = bars([100, 100, 88, 88])  # -12% day at bar 2
        s = S.extreme_drop_bounce(df, df, drop_pct=10.0)
        self.assertTrue(s.enter[2])
        self.assertFalse(s.enter[1])

    def test_momentum_burst_enters_on_multiday_move(self):
        df = bars([100, 105, 110, 120])  # +20% over 3 days by bar 3
        s = S.momentum_burst(df, df, lookback=3, thresh_pct=15.0)
        self.assertTrue(s.enter[3])


class TestData(unittest.TestCase):
    def test_resample_drops_partial_buckets(self):
        idx = pd.date_range("2020-01-01", periods=7, freq="1h", tz="UTC")
        df = pd.DataFrame({"open": 1.0, "high": 2.0, "low": 0.5, "close": 1.5, "volume": 1.0}, index=idx)
        out = D.resample(df, "4h", 4)
        self.assertEqual(len(out), 1)  # 00-04 complete, 04-07 partial

    def test_clean_removes_bad_rows(self):
        idx = pd.date_range("2020-01-01", periods=3, freq="1D", tz="UTC")
        df = pd.DataFrame({"open": [1, -1, 2], "high": [2, 2, 1], "low": [0.5, 0.5, 3], "close": [1, 1, 2],
                           "volume": 1.0}, index=idx)
        self.assertEqual(len(D.clean(df)), 1)


class TestMetrics(unittest.TestCase):
    def test_buy_hold_metrics_sane(self):
        df = bars(np.linspace(100, 200, 400))
        res = run(df, S.buy_hold(df, df), FREE)
        m = metrics(res, len(df))
        self.assertGreater(m["cagr_pct"], 0)
        self.assertEqual(m["max_dd_pct"], 0.0)


if __name__ == "__main__":
    unittest.main()
