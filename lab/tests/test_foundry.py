"""Foundry rules must not look ahead: cutting the data after a day leaves earlier trades unchanged."""
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from lab.foundry.rules import RULES, add_features, simulate, to_5min


def synthetic(days=8, seed=3):
    rng = np.random.default_rng(seed)
    rows, px = [], 500.0
    for d in pd.bdate_range("2026-01-05", periods=days):
        for m in range(390):
            t = pd.Timestamp(d.date()).tz_localize("America/New_York") + pd.Timedelta(minutes=570 + m)
            o = px
            px *= 1 + rng.normal(0, 0.0007)
            rows.append(dict(t=t, o=o, h=max(o, px) * 1.0003, l=min(o, px) * 0.9997, c=px, v=1000 + rng.integers(0, 500)))
    return pd.DataFrame(rows).set_index("t")


class NoLookAhead(unittest.TestCase):
    def test_truncation(self):
        d = to_5min(synthetic())
        full = add_features(d)
        days = sorted(full["day"].unique())
        cut = add_features(d[pd.Series(d.index.date, index=d.index) <= days[5]])
        for r in RULES:
            a = [t for t in simulate(full, r, "X") if t["day"] <= str(days[4])]
            b = [t for t in simulate(cut, r, "X") if t["day"] <= str(days[4])]
            self.assertEqual(a, b, r)

    def test_costs_charged(self):
        d = add_features(to_5min(synthetic(4)))
        for r in RULES:
            for t in simulate(d, r, "X"):
                self.assertAlmostEqual(t["gross"] - t["net"], 2 * (0.0002 + 0.00003))


if __name__ == "__main__":
    unittest.main()
