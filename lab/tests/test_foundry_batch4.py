"""Batch 4: features and fills must not look ahead; fail-fast is a paired variant of the same trade."""
import unittest

import pandas as pd

from lab.foundry.batch4 import by_day, fail_fast, features, random_set, trade_from, day_shape
from lab.foundry.rules import COST, add_features, to_5min
from lab.tests.test_foundry import synthetic


class Batch4(unittest.TestCase):
    def setUp(self):
        self.d = add_features(to_5min(synthetic(days=6, seed=8)))
        self.days = by_day(self.d)

    def test_features_ignore_future_bars(self):
        rows = list(self.days.values())[2]
        k = 20
        bumped = [dict(r) for r in rows]
        for r in bumped[k + 1:]:
            r["h"] *= 1.05; r["l"] *= 0.95; r["c"] *= 1.03
        for side in (1, -1):
            self.assertEqual(features(rows, k, side), features(bumped, k, side))

    def test_fill_is_next_bar_open_and_costed(self):
        rows = list(self.days.values())[1]
        t = trade_from(rows, 10, 1)
        self.assertEqual(t["entry"], rows[11]["o"])
        self.assertAlmostEqual(t["gross"] - t["net"], COST)
        self.assertGreater(t["t_in"], str(rows[10]["t"]))

    def test_fail_fast_only_changes_slow_starters(self):
        rows = list(self.days.values())[3]
        for k in range(5, 60, 7):
            for side in (1, -1):
                t = trade_from(rows, k, side)
                if t is None:
                    continue
                ff, hit = fail_fast(rows, k + 1, side, t["entry"], t["bars"], t["net"])
                if not hit:
                    self.assertEqual(ff, t["net"])
                else:
                    self.assertGreater(t["bars"], 3)
                    exp = side * (rows[k + 3]["c"] / t["entry"] - 1) - COST
                    self.assertAlmostEqual(ff, exp)

    def test_random_set_deterministic(self):
        a = random_set({"SPY": self.days})
        b = random_set({"SPY": self.days})
        pd.testing.assert_frame_equal(a, b)
        self.assertTrue({"dist", "stretched", "ff_net"} <= set(a.columns))

    def test_day_shape(self):
        rows = [dict(o=100, h=101, l=99.9, c=100.5)]
        self.assertEqual(day_shape(rows), "up")
        self.assertEqual(day_shape([dict(o=100, h=100.9, l=99.9, c=100.1)]), "V")


if __name__ == "__main__":
    unittest.main()


class H13(unittest.TestCase):
    def test_no_look_ahead(self):
        from lab.foundry.batch4 import open1_signal
        from lab.foundry.batch3 import simulate
        raw = synthetic(days=8, seed=12)
        raw.loc[raw.index.date == raw.index[390 * 3].date(), ["o", "h", "l", "c"]] *= 1.0  # untouched
        full = add_features(to_5min(raw))
        days = sorted(full["day"].unique())
        cut = add_features(to_5min(raw[pd.Series(raw.index.date, index=raw.index) <= days[5]]))
        a = [t for t in simulate(full, "SPY", "H13", open1_signal(0.002)) if t["day"] <= str(days[4])]
        b = [t for t in simulate(cut, "SPY", "H13", open1_signal(0.002)) if t["day"] <= str(days[4])]
        self.assertEqual(a, b)
        self.assertTrue(len(a) > 0)
        for t in a:
            self.assertAlmostEqual(t["gross"] - t["net"], COST)
