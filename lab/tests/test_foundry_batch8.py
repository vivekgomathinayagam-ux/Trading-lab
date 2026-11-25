"""Batch 8 (H30 V days, H31 impulse fade): no look-ahead, costs, and the hand-built cases."""
import unittest

import numpy as np

from lab.foundry import batch8 as b8
from lab.foundry.rules import COST


def sess(closes, pc=100.0, day="2026-01-05", wick=0.0005):
    c = np.array(closes, float)
    o = np.r_[c[0], c[:-1]]
    return {"day": day, "m": np.arange(len(c)) * 5, "o": o, "h": np.maximum(o, c) * (1 + wick),
            "l": np.minimum(o, c) * (1 - wick), "c": c, "pc": pc}


def random_sess(seed, pc=100.0):
    rng = np.random.default_rng(seed)
    px = pc * (1 + rng.normal(0, 0.012))
    c = px * np.cumprod(1 + rng.normal(0, 0.004, 78))
    return sess(c, pc=pc, day=f"2026-01-{5 + seed % 20:02d}")


def perturb_after(s, k, seed=1):
    rng = np.random.default_rng(seed)
    t = {kk: (v.copy() if isinstance(v, np.ndarray) else v) for kk, v in s.items()}
    f = 1 + rng.normal(0, 0.01, len(t["c"]) - k)
    for col in ("o", "h", "l", "c"):
        t[col][k:] = t[col][k:] * f
    t["h"][k:] = np.maximum.reduce([t["h"][k:], t["o"][k:], t["c"][k:]])
    t["l"][k:] = np.minimum.reduce([t["l"][k:], t["o"][k:], t["c"][k:]])
    return t


class NoLookAhead(unittest.TestCase):
    def test_signals_ignore_future_bars(self):
        for seed in range(60):
            s = random_sess(seed)
            for k in (20, 40, 60):
                t = perturb_after(s, k, seed)
                a = [x["sig_m"] for x in b8.h31_session(s, "X") if x["sig_m"] < (k - 1) * 5]
                b = [x["sig_m"] for x in b8.h31_session(t, "X") if x["sig_m"] < (k - 1) * 5]
                self.assertEqual(a, b)
                va, vb = b8.v_day(s), b8.v_day(t)
                if va and va[1] < k - 1:
                    self.assertEqual(va, vb)


class Cases(unittest.TestCase):
    def test_v_day_gap_up(self):
        # gap +2%, flush to -1.5% by 09:45, recover 1%+ off the low by 10:05
        closes = [102, 101, 100.6, 100.5, 101.0, 101.7, 102] + [102] * 71
        v = b8.v_day(sess(closes, pc=100.0))
        self.assertIsNotNone(v)
        self.assertEqual(v[0], 1)
        t, vd = b8.h30([sess(closes, pc=100.0)], "X")
        self.assertEqual({x["cell"] for x in t}, {"with_gapup", "fade_gapup"})
        for x in t:
            self.assertAlmostEqual(x["gross"] - x["net"], COST)

    def test_no_v_without_gap(self):
        self.assertIsNone(b8.v_day(sess([100.2, 99, 98.5, 99.8, 100.5] + [100] * 73, pc=100.0)))

    def test_impulse_fade_short(self):
        # rally 2% to 10:30, then a lower low -> short; price falls into the close
        up = list(np.linspace(100, 102, 13))
        down = list(np.linspace(101.9, 100.5, 65))
        tr = b8.h31_session(sess(up + down, pc=100.0, wick=0.0), "X")
        shorts = [x for x in tr if x["cell"] == "fade_up_short"]
        self.assertEqual(len(shorts), 1)
        self.assertGreater(shorts[0]["gross"], 0)
        self.assertEqual(shorts[0]["why"], "eod")


if __name__ == "__main__":
    unittest.main()
