"""Batch 6 rules must not look ahead: cutting a day after bar m leaves every signal at or before m unchanged,
and the Flux gate must use the point of minute t-1."""
import unittest

import numpy as np
import pandas as pd

from lab.foundry import batch6 as B
from lab.foundry.rules import COST


def day(seed=1, drift=0.0):
    rng = np.random.default_rng(seed)
    mins = np.arange(570, 960, 5)
    px, o, h, l, c = 100.0, [], [], [], []
    for _ in mins:
        op = px
        px *= 1 + drift + rng.normal(0, 0.003)
        o.append(op); c.append(px); h.append(max(op, px) * 1.001); l.append(min(op, px) * 0.999)
    return dict(o=np.array(o), h=np.array(h), l=np.array(l), c=np.array(c), mins=mins,
                t=[f"T{m}" for m in mins])


def cut(b, k):
    return {key: (v[: k + 1] if not isinstance(v, list) else v[: k + 1]) for key, v in b.items()}


class NoLookAhead(unittest.TestCase):
    def test_signals_use_past_only(self):
        for seed in range(30):
            b = day(seed, drift=0.0008 if seed % 2 else -0.0008)
            for fn in (B.h19, B.h20):
                full = fn(b)
                if full is None:
                    continue
                k = full[0]
                self.assertEqual(fn(cut(b, k))[:2], full[:2])
            fh = B.first_hour(b)
            if fh:
                self.assertEqual(B.first_hour(cut(b, fh[0])), fh)

    def test_costs_and_fill(self):
        b = day(3, 0.001)
        t = B.trade(b, 10, 1, None)
        self.assertAlmostEqual(t["gross"] - t["net"], COST)
        self.assertEqual(t["entry"], b["o"][11])

    def test_stop(self):
        b = day(4, -0.002)
        t = B.trade(b, 5, 1, b["o"][6] * 0.995)
        self.assertEqual(t["why"], "stop")
        self.assertLessEqual(t["gross"], -0.005 + 1e-9)


class FluxShift(unittest.TestCase):
    def test_flux_point_is_previous_minute(self):
        from lab.foundry import skylit6 as S
        idx = pd.date_range("2026-11-17 09:30", periods=400, freq="1min", tz="America/New_York")
        flux = pd.DataFrame(dict(lvl=np.arange(400.0), iu=np.arange(400.0) + 1, il=np.arange(400.0) - 1), index=idx)
        shifted = flux.shift(1)
        self.assertTrue(np.isnan(shifted["lvl"].iloc[0]))
        self.assertEqual(shifted["lvl"].iloc[10], 9.0)


if __name__ == "__main__":
    unittest.main()
