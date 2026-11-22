"""Batch 7: the fast desk replay must equal lab.floor.engine.simulate, and the MA grid features
must not look ahead (cutting the data after a signal leaves its features unchanged)."""
import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from lab.floor.engine import simulate
from lab.foundry import batch7 as B
from strategies.daytrade.core import ORB, SYMBOLS, VolSpike

NY = ZoneInfo("America/New_York")


def synth(seed: int, days: int = 8) -> dict:
    rng = np.random.default_rng(seed)
    out = {}
    start = datetime(2024, 3, 4, 9, 30, tzinfo=NY)
    for k, sym in enumerate(SYMBOLS):
        rows, px = [], 100.0 + 10 * k
        lev = 3 if sym in ("TQQQ", "UPRO", "SQQQ", "SPXU") else 1
        for dd in range(days):
            day0 = start + timedelta(days=dd)
            drift = rng.normal(0, 0.0004) * lev
            for m in range(390):
                o = px
                px = px * (1 + drift + rng.normal(0, 0.001 * lev))
                v = rng.integers(1000, 3000) * (8 if rng.random() < 0.03 else 1)
                rows.append({"t": (day0 + timedelta(minutes=m)).isoformat(), "o": o, "h": max(o, px) * 1.0005,
                             "l": min(o, px) * 0.9995, "c": px, "v": v})
        d = pd.DataFrame(rows)
        d["ts"] = pd.to_datetime(d["t"], utc=True).dt.tz_convert("America/New_York")
        d["day"] = d.ts.dt.date.astype(str)
        d["m"] = d.ts.dt.hour * 60 + d.ts.dt.minute - 570
        d["v"] = d["v"].astype(float)
        out[sym] = d
    return out


class Batch7(unittest.TestCase):
    def test_replay_matches_engine(self):
        for seed in (1, 2):
            data = synth(seed)
            days = sorted(set(data["SPY"].day))
            rules = {"volspike": VolSpike(), "orb_none": ORB(None)}
            sig = B.signal_table(data, rules, days[3])
            res = simulate({s: B.to_bars(d) for s, d in data.items()}, [VolSpike(), ORB(None)])
            for desk, key in zip(res["desks"], rules):
                mine = B.pick(sig[sig.rule == key])
                eng = [(t["entry_t"][:16], t["sym"], t["reason"], round(t["move_pct"], 1)) for t in desk.trades]
                me = [(r.entry_t.tz_convert("America/New_York").isoformat()[:16], r.sym, r.reason, round(r.move, 1))
                      for r in mine.itertuples()]
                self.assertEqual(eng, me, key)

    def test_ma_features_no_lookahead(self):
        data = synth(3)
        days = sorted(set(data["SPY"].day))
        sig = B.signal_table(data, {"volspike": VolSpike()}, days[3])
        sig = sig[sig.valid].reset_index(drop=True)
        self.assertGreater(len(sig), 0)
        full = B.ma_features(data, sig)
        for r in sig.head(5).itertuples():
            cutoff = r.t
            cut = {s: d[d.ts <= cutoff].reset_index(drop=True) for s, d in data.items()}
            one = sig.loc[[r.Index]]
            f1 = B.ma_features(cut, one)
            a = full.loc[r.Index, f1.columns].values.astype(float)
            b = f1.iloc[0].values.astype(float)
            self.assertTrue(np.allclose(a, b, equal_nan=True))

    def test_mirrored_filter(self):
        data = synth(4)
        days = sorted(set(data["SPY"].day))
        sig = B.signal_table(data, {"volspike": VolSpike()}, days[3])
        sig = sig[sig.valid].reset_index(drop=True)
        F = B.ma_features(data, sig)
        masks = B.grid_filters(F)
        self.assertEqual(len(masks), 924)   # 2 views x 3 TF x 2 types x (11 x 2 tests + 55 pairs)
        self.assertTrue(all(m.shape == (len(sig),) for m in masks.values()))
        inv = sig.sym.isin(["SQQQ", "SPXU"]).values
        if inv.any():
            und = F["und|close"].values > F["und|1|EMA|20|now"].values
            m = masks["und|1m|EMA20|above"]
            self.assertTrue(np.array_equal(m[inv], ~und[inv] & ~np.isnan(F["und|1|EMA|20|now"].values[inv])
                                           & (F["und|close"].values[inv] != F["und|1|EMA|20|now"].values[inv])))


if __name__ == "__main__":
    unittest.main()
