"""Batch 3 rules must not look ahead, and wick cleaning must only clip outliers."""
import unittest

import numpy as np
import pandas as pd

from lab.foundry.batch3 import CANDIDATES, clean_wicks, random_set, simulate
from lab.foundry.rules import COST, add_features, to_5min
from lab.tests.test_foundry import synthetic


class Batch3(unittest.TestCase):
    def test_no_look_ahead(self):
        raw = synthetic(days=10, seed=5) * 1.0
        full = add_features(to_5min(raw))
        days = sorted(full["day"].unique())
        cut_raw = raw[pd.Series(raw.index.date, index=raw.index) <= days[6]]
        cut = add_features(to_5min(cut_raw))
        for name, mk in CANDIDATES.items():
            a = [t for t in simulate(full, "SPY", name, mk()) if t["day"] <= str(days[5])]
            b = [t for t in simulate(cut, "SPY", name, mk()) if t["day"] <= str(days[5])]
            self.assertEqual(a, b, name)

    def test_future_bar_change_keeps_past(self):
        raw = synthetic(days=6, seed=9)
        d = add_features(to_5min(raw))
        day = sorted(d["day"].unique())[3]
        g = d[d["day"] == day]
        k = len(g) // 2
        bumped = raw.copy()
        mask = (pd.Series(raw.index.date, index=raw.index) == day) & (raw.index > g.index[k] + pd.Timedelta(minutes=5))
        bumped.loc[mask, ["o", "h", "l", "c"]] *= 1.03
        d2 = add_features(to_5min(bumped))
        cutoff = str(g.index[k])
        for name, mk in CANDIDATES.items():
            a = [t["t_in"] for t in simulate(d, "SPY", name, mk()) if t["t_in"] <= cutoff]
            b = [t["t_in"] for t in simulate(d2, "SPY", name, mk()) if t["t_in"] <= cutoff]
            self.assertEqual(a, b, name)

    def test_costs_and_fills(self):
        d = add_features(to_5min(synthetic(days=5, seed=2)))
        for name, mk in CANDIDATES.items():
            for t in simulate(d, "QQQ", name, mk()):
                self.assertAlmostEqual(t["gross"] - t["net"], COST)
                self.assertGreater(t["t_in"], t["day"])  # filled on a bar after the signal

    def test_clean_wicks(self):
        idx = pd.date_range("2026-11-04 09:30", periods=3, freq="1min", tz="America/New_York")
        d = pd.DataFrame(dict(o=[100, 100, 100], h=[100.1, 101.0, 100.2], l=[99.9, 99.9, 98.0], c=[100, 100.1, 100], v=1), index=idx)
        c, n = clean_wicks(d, 0.004)
        self.assertEqual(n, 2)
        self.assertAlmostEqual(c["h"].iloc[1], 100.1 * 1.004)
        self.assertAlmostEqual(c["l"].iloc[2], 100 * 0.996)
        self.assertEqual(c["h"].iloc[0], 100.1)

    def test_random_set_runs(self):
        d = add_features(to_5min(synthetic(days=4, seed=4)))
        r = random_set({"SPY": d})
        self.assertIn("stale", r.columns)


if __name__ == "__main__":
    unittest.main()
