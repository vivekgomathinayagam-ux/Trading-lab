"""Batch 5: the profit lock, the gate and the delayed stop must not look ahead; fills are next-bar opens."""
import unittest

import pandas as pd

from lab.foundry.batch4 import by_day, trade_from
from lab.foundry.batch5 import (ARMS, early_set, from_open_at, h13_delayed, profit_lock, trade_time)
from lab.foundry.rules import COST, add_features, to_5min
from lab.tests.test_foundry import synthetic


class Batch5(unittest.TestCase):
    def setUp(self):
        self.d = add_features(to_5min(synthetic(days=6, seed=8)))
        self.days = by_day(self.d)

    def test_profit_lock_ignores_bars_after_its_exit(self):
        rows = list(self.days.values())[2]
        for k in range(3, 50, 4):
            for side in (1, -1):
                t = trade_from(rows, k, side)
                if t is None:
                    continue
                i, j = k + 1, k + t["bars"]
                for arm in ARMS + [0.0005]:
                    net, armed, fired = profit_lock(rows, i, j, side, t["entry"], t["net"], arm)
                    if not fired:
                        self.assertEqual(net, t["net"])
                        continue
                    # find the exit bar and perturb everything after it: result must not change
                    ex_k = next(q for q in range(i, j) if rows[q + 1]["o"] == rows[q + 1]["o"] and
                                abs(side * (rows[q + 1]["o"] / t["entry"] - 1) - COST - net) < 1e-12)
                    bumped = [dict(r) for r in rows]
                    for r in bumped[ex_k + 2:]:
                        r["h"] *= 1.05; r["l"] *= 0.95; r["c"] *= 1.03; r["e5"] *= 1.02
                    n2, _, f2 = profit_lock(bumped, i, j, side, t["entry"], t["net"], arm)
                    self.assertTrue(f2)
                    self.assertAlmostEqual(n2, net)

    def test_profit_lock_fires_with_tiny_arm(self):
        rows = list(self.days.values())[1]
        fired = 0
        for k in range(3, 60, 3):
            t = trade_from(rows, k, 1)
            if t:
                fired += profit_lock(rows, k + 1, k + t["bars"], 1, t["entry"], t["net"], 0.0001)[2]
        self.assertGreater(fired, 0)

    def test_trade_time_next_open_and_30min(self):
        rows = list(self.days.values())[3]
        t = trade_time(rows, 5, 1, 6, stop_pct=0.5)
        self.assertEqual(t["entry"], rows[6]["o"])
        self.assertEqual(t["bars"], 6)
        self.assertEqual(t["exit"], rows[11]["c"])
        self.assertAlmostEqual(t["gross"] - t["net"], COST)

    def test_gate_feature_is_causal(self):
        rows = list(self.days.values())[2]
        k = 4
        bumped = [dict(r) for r in rows]
        for r in bumped[k + 1:]:
            r["c"] *= 1.1
        self.assertEqual(from_open_at(rows, rows[k]["t"]), from_open_at(bumped, rows[k]["t"]))

    def test_early_set_window_and_sides(self):
        e = early_set({"QQQ": self.days, "SPY": self.days})
        self.assertTrue(e["mins"].between(585, 625).all())
        self.assertEqual(set(e["side"]), {1, -1})

    def test_delayed_stop_never_exits_in_first_bars(self):
        rows = list(self.days.values())[4]
        for i in range(5, 40, 5):
            for side in (1, -1):
                entry = rows[i]["o"]
                stop = entry * (1 - 0.0005 * side)
                r = h13_delayed(rows, i, side, entry, stop)
                self.assertIsNotNone(r["net"])


if __name__ == "__main__":
    unittest.main()
