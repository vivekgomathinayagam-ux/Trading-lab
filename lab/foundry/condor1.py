"""Skylit condor study 1 (research/skylit/PREREG_condor1.md + amendment A). Research only.

  python -m lab.foundry.condor1 --plan condor_plan.json --raw condor_raw.jsonl --spy1m SPY.csv.gz --out out.json
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd

COMM = 0.65


def row_of(resp):
    r = resp
    if isinstance(r, dict):
        for k in ("rows", "history", "data", "days"):
            if k in r:
                r = r[k]
                break
    if isinstance(r, list):
        r = r[0] if r else None
    return r


def evaluate(plan, legs, settle, slip):
    out = []
    for p in plan:
        L = legs.get(p["D"], {})
        if len(L) < 4 or any((L[k] or {}).get("lastPrice") in (None, 0) for k in ("sc", "lc", "sp", "lp")):
            out.append(dict(D=p["D"], dropped=True))
            continue
        px = {k: float(L[k]["lastPrice"]) for k in L}
        credit = (px["sc"] - slip) + (px["sp"] - slip) - (px["lc"] + slip) - (px["lp"] + slip)
        S1 = settle[p["exp"]]
        intr = dict(sc=max(0, S1 - p["sc"]), lc=max(0, S1 - p["lc"]), sp=max(0, p["sp"] - S1), lp=max(0, p["lp"] - S1))
        itm = sum(1 for v in intr.values() if v > 0)
        payout = intr["sc"] - intr["lc"] + intr["sp"] - intr["lp"]
        pnl = 100 * (credit - payout - slip * itm) - COMM * (4 + itm)
        maxloss = 100 * (5 - credit) + COMM * 4
        out.append(dict(D=p["D"], exp=p["exp"], S=p["S"], S1=round(S1, 3), em=p["em"], credit=round(credit, 3),
                        pnl=round(pnl, 2), maxloss=round(maxloss, 2), pct_maxloss=round(100 * pnl / maxloss, 2),
                        breach=bool(S1 > p["sc"] or S1 < p["sp"]), move_sigma=round(abs(S1 / p["S"] - 1) * 100 / p["em"], 3),
                        dropped=False))
    return out


def summarize(res):
    t = pd.DataFrame([r for r in res if not r["dropped"]])
    n = len(t)
    h = n // 2
    rng = np.random.default_rng(3)
    boots = [t["pnl"].values[rng.integers(0, n, n)].mean() for _ in range(4000)]
    return dict(trades=n, dropped=sum(r["dropped"] for r in res), mean_pnl=round(t["pnl"].mean(), 2),
                ci=[round(float(np.percentile(boots, 2.5)), 2), round(float(np.percentile(boots, 97.5)), 2)],
                total=round(t["pnl"].sum(), 2), win=round(float((t["pnl"] > 0).mean()), 3),
                half1=round(t["pnl"].iloc[:h].mean(), 2), half2=round(t["pnl"].iloc[h:].mean(), 2),
                breach_rate=round(float(t["breach"].mean()), 3), worst=round(t["pnl"].min(), 2),
                mean_credit=round(t["credit"].mean(), 3), mean_pct_maxloss=round(t["pct_maxloss"].mean(), 2),
                mean_move_sigma=round(t["move_sigma"].mean(), 3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--raw", required=True)
    ap.add_argument("--spy1m", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    legs = {}
    for line in open(a.raw):
        r = json.loads(line)
        legs.setdefault(r["D"], {})[r["leg"]] = row_of(r["response"])
    d = pd.read_csv(a.spy1m)
    d["t"] = pd.to_datetime(d["t"], utc=True).dt.tz_convert("America/New_York")
    d = d[(d["t"].dt.hour * 60 + d["t"].dt.minute) < 960]
    settle = {str(k): float(g["c"].iloc[-1]) for k, g in d.groupby(d["t"].dt.date)}
    out = {}
    for tag, slip in (("cost_1x", 0.02), ("cost_2x", 0.04), ("gross_no_slip", 0.0)):
        res = evaluate(plan, legs, settle, slip)
        out[tag] = dict(summary=summarize(res), trades=res)
    json.dump(out, open(a.out, "w"), indent=1)
    for k, v in out.items():
        print(k, json.dumps(v["summary"]))


if __name__ == "__main__":
    main()
