"""Skylit pilot 2 (pre-registered in research/skylit/STUDY.md, 2026-10-31). Run from the repo root:

  python -m research.skylit.pilot2 --raw research/skylit/raw --archive <dir with etf1m/*.csv.gz> --out research/skylit/pilot2_results.json

Raw cache lives on branch `data` under research/skylit/raw/ (heat0dte_*.jsonl, tempest_hist_*.jsonl).
Outcomes use only 1-minute bars that START at or after the decision minute (board asOf is 1 s before it).
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import random
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

from lab.floor.data import load_archive

N_STRIKES = 30
DECISION = {"1000": (10, 0), "1230": (12, 30)}


def trim(strikes, spot, n=N_STRIKES):
    return sorted(sorted(strikes, key=lambda s: abs(s[0] - spot))[:n])


def board_features(r):
    spot = r["spot"]
    st = trim(r["strikes"], spot)
    near = [s for s in st if abs(s[0] / spot - 1) <= 0.01]
    pos = [s for s in near if s[1] > 0]
    neg = [s for s in near if s[1] < 0]
    return {"spot": spot,
            "magnet": max(pos, key=lambda s: s[1])[0] if pos else None,
            "accel": min(neg, key=lambda s: s[1])[0] if neg else None,
            "net0": sum(s[1] for s in st)}


def outcome(bars, day, hm, minutes):
    t0 = datetime.combine(day, datetime.min.time()).replace(hour=hm[0], minute=hm[1])
    w = [b for b in bars.get(day, []) if t0 <= b.t.replace(tzinfo=None) < t0 + timedelta(minutes=minutes)]
    if len(w) < minutes * 0.8:
        return None
    return {"close": w[-1].c, "hi": max(b.h for b in w), "lo": min(b.l for b in w)}


def binom(k, n):
    if n == 0:
        return None
    p = k / n
    h = 1.96 * math.sqrt(p * (1 - p) / n)
    return {"pct": round(100 * p, 1), "lo": round(100 * (p - h), 1), "hi": round(100 * (p + h), 1), "n": n}


def block_boot_diff(rows, key, cond, n=5000, seed=11):
    """mean(key | cond) - mean(key | not cond), resampling whole days."""
    by_day = defaultdict(list)
    for r in rows:
        by_day[r["date"]].append(r)
    days = sorted(by_day)

    def stat(sample):
        a = [r[key] for d in sample for r in by_day[d] if cond(r)]
        b = [r[key] for d in sample for r in by_day[d] if not cond(r)]
        if not a or not b:
            return None
        return sum(a) / len(a) - sum(b) / len(b), len(a), len(b)

    base = stat(days)
    if base is None:
        return None
    rng = random.Random(seed)
    ds = sorted(x[0] for x in (stat([rng.choice(days) for _ in days]) for _ in range(n)) if x)
    return {"diff": round(base[0], 4), "lo": round(ds[int(0.025 * len(ds))], 4),
            "hi": round(ds[int(0.975 * len(ds))], 4), "n_true": base[1], "n_false": base[2]}


def heat_study(raw, archive):
    boards = [json.loads(l) for f in sorted(glob.glob(str(Path(raw) / "heat0dte_*.jsonl"))) for l in open(f)]
    boards = [b for b in boards if "error" not in b]
    bars = {}
    for s in ("SPY", "QQQ"):
        by = defaultdict(list)
        for b in sorted(load_archive(Path(archive) / f"{s}.csv.gz").values(), key=lambda x: x.t):
            by[b.t.date()].append(b)
        bars[s] = by
    out = {}
    for minutes in (60, 90):
        rows = []
        for b in boards:
            day = datetime.strptime(b["date"], "%Y-%m-%d").date()
            o = outcome(bars[b["symbol"]], day, DECISION[b["t"]], minutes)
            if not o:
                continue
            f = board_features(b)
            spot = f["spot"]
            rows.append({"date": b["date"], "t": b["t"], "sym": b["symbol"], **f,
                         "ret": (o["close"] / spot - 1) * 100, "range": (o["hi"] - o["lo"]) / spot * 100,
                         "dist_accel": None if f["accel"] is None else abs(f["accel"] / spot - 1) * 100,
                         "dist_mag": None if f["magnet"] is None else (f["magnet"] / spot - 1) * 100,
                         "close_out": o["close"]})
        res = {"n_rows": len(rows), "n_days": len({r["date"] for r in rows})}
        m = [r for r in rows if r["dist_mag"] is not None and abs(r["dist_mag"]) > 0.05]
        hits = sum(1 for r in m if (r["close_out"] - r["spot"]) * (r["magnet"] - r["spot"]) > 0)
        res["Q2.1_toward_magnet"] = binom(hits, len(m))
        res["Q2.1_by_time"] = {t: binom(sum(1 for r in m if r["t"] == t and (r["close_out"] - r["spot"]) * (r["magnet"] - r["spot"]) > 0),
                                        sum(1 for r in m if r["t"] == t)) for t in DECISION}
        res["Q2.2_range_pos_minus_neg"] = block_boot_diff(rows, "range", lambda r: r["net0"] > 0)
        ra = [r for r in rows if r["dist_accel"] is not None]
        res["Q2.3_range_near_accel_minus_not"] = block_boot_diff(ra, "range", lambda r: r["dist_accel"] <= 0.25)
        res["mean_range_pct"] = round(sum(r["range"] for r in rows) / len(rows), 4)
        res["share_net0_pos"] = round(sum(r["net0"] > 0 for r in rows) / len(rows), 3)
        out[f"{minutes}min"] = res
    return out


def tempest_study(raw):
    out = {}
    pooled = []
    for s in ("SPY", "QQQ"):
        t = [json.loads(l) for l in open(Path(raw) / f"tempest_hist_{s}.jsonl")]
        rows = []
        for a, b in zip(t, t[1:]):
            mv = abs(b["close"] / a["close"] - 1) * 100
            rows.append({"date": a["date"], "sym": s, "em": a["em_1d_pct"], "slope": a["term_slope"],
                         "ratio": mv / a["em_1d_pct"], "breach": float(mv > a["em_1d_pct"])})
        pooled += rows
        half = len(rows) // 2
        res = {}
        for name, R in (("all", rows), ("first_half", rows[:half]), ("second_half", rows[half:])):
            k = int(sum(r["breach"] for r in R))
            sl = sorted(r["slope"] for r in R)
            lo_c, hi_c = sl[len(sl) // 3], sl[2 * len(sl) // 3]
            ext = [r for r in R if r["slope"] <= lo_c or r["slope"] >= hi_c]
            res[name] = {"from": R[0]["date"], "to": R[-1]["date"], "breach": binom(k, len(R)),
                         "mean_move_over_em": round(sum(r["ratio"] for r in R) / len(R), 3),
                         "median_move_over_em": round(sorted(r["ratio"] for r in R)[len(R) // 2], 3),
                         "Q2.6_breach_top_minus_bottom_slope_third": block_boot_diff(ext, "breach", lambda r, h=hi_c: r["slope"] >= h),
                         "slope_terciles": [round(lo_c, 3), round(hi_c, 3)]}
        out[s] = res
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--archive", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    res = {"heat": heat_study(a.raw, a.archive), "tempest": tempest_study(a.raw),
           "note": "term_slope = svx9 - svx30 (checked on Oct 26-30: matches to 4 decimals); positive = backwardation"}
    txt = json.dumps(res, indent=1)
    if a.out:
        Path(a.out).write_text(txt)
    print(txt)


if __name__ == "__main__":
    main()
