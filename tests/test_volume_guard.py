"""Running-volume guard (LESSONS 56, 2026-11-25): Yahoo bars whose volume is the session's running
total are treated as having no volume. Run: python -m unittest discover -s tests -t . -v
"""
import math
import random
import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from strategies.daytrade.core import (ORB, Bar, EMACross, EMACrossV2, Features, VolSpike,
                                      running_volume_mask)

NY = ZoneInfo("America/New_York")


def session(day, n=120, vols=None, seed=1, drift=0.0):
    rnd = random.Random(seed)
    t0 = datetime(day.year, day.month, day.day, 9, 30, tzinfo=NY)
    out, c = [], 100.0
    for i in range(n):
        o = c
        c = o * (1 + drift + rnd.gauss(0, 0.0008))
        v = vols[i] if vols else rnd.uniform(800, 1200)
        out.append(Bar(t0 + timedelta(minutes=i), o, max(o, c) * 1.0002, min(o, c) * 0.9998, c, v))
    return out


def with_running_total(bars, idx):
    """Replace bar idx's volume with the session's running total (the Yahoo fault)."""
    tot = sum(b.v for b in bars[: idx + 1])
    b = bars[idx]
    return bars[:idx] + [Bar(b.t, b.o, b.h, b.l, b.c, tot)] + bars[idx + 1:]


class GuardTests(unittest.TestCase):
    def test_running_total_bar_is_not_a_spike(self):
        bars = with_running_total(session(datetime(2026, 11, 2)), 60)
        f, g = Features(), Features(vol_guard=False)
        for b in bars:
            f.update(b); g.update(b)
            if b is bars[60]:
                self.assertTrue(f.vol_missing)
                self.assertTrue(math.isnan(f.vol_ratio))
                self.assertFalse(f.volume_ok())
                self.assertTrue(g.volume_ok())          # unguarded: fires the 3x gate
        self.assertEqual(f.vol_missing_n, 1)

    def test_running_total_bar_kept_out_of_vwap_and_baselines(self):
        clean = session(datetime(2026, 11, 2))
        bad = with_running_total(clean, 60)
        f_clean, f_bad = Features(), Features()
        for b in clean[:60] + clean[61:]:
            f_clean.update(b)
        for b in bad:
            f_bad.update(b)
        # VWAP and the volume baseline match the session without that bar's volume
        self.assertAlmostEqual(f_bad.vv, f_clean.vv, places=6)
        self.assertEqual(list(f_bad.vols), list(f_clean.vols))

    def test_real_spike_still_passes(self):
        vols = [1000.0] * 120
        vols[60] = 6000.0                              # 6x a normal minute, far below the running total
        f = Features()
        for b in session(datetime(2026, 11, 2), vols=vols):
            f.update(b)
            if b.t.minute == 30 and b.t.hour == 10:
                self.assertFalse(f.vol_missing)
                self.assertTrue(f.volume_ok())

    def test_first_bar_of_day_never_flagged(self):
        f = Features()
        for b in session(datetime(2026, 11, 2)):
            f.update(b)
        big = session(datetime(2026, 11, 3), vols=[1e7] + [1000.0] * 119)
        f.update(big[0])
        self.assertFalse(f.vol_missing)

    def test_batch_mask_equals_features(self):
        bars = []
        for k, d in enumerate([datetime(2026, 11, 2), datetime(2026, 11, 3), datetime(2026, 11, 4)]):
            s = session(d, seed=k)
            for i in (45, 46, 90):
                s = with_running_total(s, i)
            bars += s
        f, flags = Features(), []
        for b in bars:
            f.update(b)
            flags.append(f.vol_missing)
        mask = running_volume_mask([b.t.date() for b in bars], [b.v for b in bars])
        self.assertEqual(flags, mask)
        self.assertEqual(sum(mask), 9)

    def test_clean_data_desks_identical(self):
        """No running-total bars -> every desk rule signals on exactly the same bars."""
        rules = [ORB(), EMACross(), VolSpike(), EMACrossV2(), ORB(None), VolSpike(2.0)]
        for seed in range(6):
            vols = [random.Random(seed).uniform(500, 1500) for _ in range(390)]
            for j in range(40, 390, 37):
                vols[j] *= 5                            # real 3-5x spikes
            bars = []
            for k in range(3):
                bars += session(datetime(2026, 11, 2 + k), n=390, vols=vols, seed=seed * 10 + k, drift=0.00005)
            fa, fb, sa, sb = Features(), Features(vol_guard=False), [], []
            for b in bars:
                fa.update(b); fb.update(b)
                sa.append(tuple(r.signal(fa, b) for r in rules))
                sb.append(tuple(r.signal(fb, b) for r in rules))
            self.assertEqual(fa.vol_missing_n, 0)
            self.assertEqual(sa, sb)


if __name__ == "__main__":
    unittest.main()
