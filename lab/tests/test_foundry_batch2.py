"""Batch 2 must not look ahead: truncating after a day leaves earlier trades unchanged; GB fills next bar."""
import unittest

import pandas as pd

from lab.foundry import batch2 as B
from lab.foundry.rules import add_features, to_5min
from lab.tests.test_foundry import synthetic


def run_all(d):
    td = B.trend_days(d)
    out = []
    out += B.simulate2(d, "SPY", "G1", B.b1_signal("F1_cloud_ride", 630,
                       lambda b, s: td.get(b["day"], {}).get("trend") and td[b["day"]]["dir"] == s), B.b1_exit("F1_cloud_ride"))
    out += B.simulate2(d, "SPY", "G3", B.g3_signal(td, True))
    out += B.simulate2(d, "SPY", "G3x", B.g3_signal(td, False))
    out += B.simulate2(d, "SPY", "R1", B.r1_signal())
    out += B.simulate2(d, "SPY", "F3+GB", B.b1_signal("F3_vwap_trend"), B.b1_exit("F3_vwap_trend"), gb=True)
    return out


class Batch2NoLookAhead(unittest.TestCase):
    def setUp(self):
        self.d5 = to_5min(synthetic(days=16, seed=5))

    def test_truncation(self):
        full = add_features(self.d5)
        days = sorted(full["day"].unique())
        cut = add_features(self.d5[pd.Series(self.d5.index.date, index=self.d5.index) <= days[13]])
        a = [t for t in run_all(full) if t["day"] <= str(days[12])]
        b = [t for t in run_all(cut) if t["day"] <= str(days[12])]
        self.assertEqual(a, b)

    def test_trend_gate_uses_first_hour_only(self):
        full = add_features(self.d5)
        g1 = B.trend_days(full)
        d2 = self.d5.copy()
        late = d2.index.hour * 60 + d2.index.minute >= 630
        d2.loc[late, ["o", "h", "l", "c"]] *= 1.05          # change everything after 10:30
        g2 = B.trend_days(add_features(d2))
        for k in g1:
            self.assertEqual((g1[k]["trend"], g1[k]["dir"]), (g2[k]["trend"], g2[k]["dir"]))

    def test_gb_fills_next_open(self):
        d = add_features(self.d5)
        idx = {str(t): i for i, t in enumerate(d.index)}
        for t in B.simulate2(d, "SPY", "R", B.random_signal(d), gb=True, max_per_day=2):
            if t["why"] == "gb":
                self.assertEqual(t["exit"], d["o"].iloc[idx[t["t_out"]]])

    def test_gb_never_later_than_hold(self):
        d = add_features(self.d5)
        hold = B.simulate2(d, "SPY", "R", B.random_signal(d), max_per_day=2)
        gb = B.simulate2(d, "SPY", "R", B.random_signal(d), gb=True, max_per_day=2)
        hk = {(t["t_in"], t["side"]): t["t_out"] for t in hold}
        for t in gb:
            k = (t["t_in"], t["side"])
            if k in hk:
                self.assertLessEqual(pd.Timestamp(t["t_out"]), pd.Timestamp(hk[k]))


if __name__ == "__main__":
    unittest.main()
