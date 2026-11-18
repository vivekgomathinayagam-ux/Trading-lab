"""Foundry batch 6 (pre-registered in research/foundry/PREREG_batch6.md).

H19 H13 on the long archive, H20 0.5% morning continuation, H21 13:00 cutoff, H22 day-type marker
(first-hour range vs its 20-day mean), all on 5-min bars. H23 (market tide) and H24 (Flux Field) are in
lab/foundry/skylit6.py. Research only: nothing here trades.

  python -m lab.foundry.batch6 --long <alpaca5m dir> [--a <etf1m dir>] [--b <etf5m dir>] --out <dir>
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from lab.foundry.batch3 import clean_wicks
from lab.foundry.rules import COST, load_bars, to_5min

SYMS = ["SPY", "QQQ"]
EOD = 15 * 60 + 50          # last 5-min bar start used for the eod exit
STOP = 0.005
SEEDS = list(range(21, 29))
PER_DAY = 3


# ------------------------------------------------------------------ data
def load5(path: Path) -> pd.DataFrame:
    raw = load_bars(path)
    one_min = len(raw) > 1 and (raw.index[1] - raw.index[0]) < pd.Timedelta(minutes=5)
    raw, _ = clean_wicks(raw, 0.004 if one_min else 0.006)
    d = to_5min(raw)
    d["mins"] = d.index.hour * 60 + d.index.minute
    d["day"] = d.index.date.astype(str)
    return d


def days_of(d: pd.DataFrame) -> dict:
    """day -> dict of numpy arrays (o,h,l,c,mins,t). Days missing the 09:30 bar or with < 60 bars are dropped."""
    out = {}
    for day, g in d.groupby("day", sort=True):
        if len(g) < 60 or g["mins"].iloc[0] != 570:
            continue
        out[day] = dict(o=g["o"].values, h=g["h"].values, l=g["l"].values, c=g["c"].values,
                        mins=g["mins"].values, t=[str(x) for x in g.index])
    return out


# ------------------------------------------------------------------ one trade
def trade(b: dict, k: int, side: int, stop: float | None, cost: float = COST) -> dict | None:
    """Signal at bar k's close, fill at bar k+1's open; `stop` is an absolute price or None; flat at the
    15:50 bar's close (or the last bar)."""
    n = len(b["o"])
    if k + 1 >= n or b["mins"][k + 1] > EOD:
        return None
    entry = b["o"][k + 1]
    for j in range(k + 1, n):
        ex = why = None
        if stop is not None and side > 0 and b["l"][j] <= stop:
            ex, why = min(b["o"][j], stop), "stop"
        elif stop is not None and side < 0 and b["h"][j] >= stop:
            ex, why = max(b["o"][j], stop), "stop"
        elif b["mins"][j] >= EOD or j == n - 1:
            ex, why = b["c"][j], "eod"
        if ex is not None:
            g = side * (ex / entry - 1)
            return dict(t_in=b["t"][k + 1], t_out=b["t"][j], side=side, entry=float(entry), exit=float(ex),
                        why=why, bars=j - k, gross=float(g), net=float(g - cost))
    return None


# ------------------------------------------------------------------ rules
def h19(b: dict):
    """H13: first close 09:45-14:00 >= 1% from the open; stop at the open/signal-close midpoint."""
    o = b["o"][0]
    for k in range(len(b["c"])):
        if not (585 <= b["mins"][k] <= 840):
            continue
        r = b["c"][k] / o - 1
        if abs(r) >= 0.01:
            side = 1 if r > 0 else -1
            return k, side, (o + b["c"][k]) / 2
    return None


def h20(b: dict):
    """First close 09:45-10:25 >= 0.5% from the open; trade with it (stop handled by caller)."""
    o = b["o"][0]
    for k in range(len(b["c"])):
        if not (585 <= b["mins"][k] <= 625):
            continue
        r = b["c"][k] / o - 1
        if abs(r) >= 0.005:
            return k, (1 if r > 0 else -1)
    return None


def first_hour(b: dict):
    """(k of the 10:25 bar, first-hour range / open, direction) or None."""
    idx = np.where(b["mins"] == 625)[0]
    if not len(idx):
        return None
    k = int(idx[0])
    fr = (b["h"][: k + 1].max() - b["l"][: k + 1].min()) / b["o"][0]
    d = np.sign(b["c"][k] - b["o"][0])
    return k, fr, int(d)


def f2_exit(b: dict, k: int, side: int, cost: float = COST) -> float | None:
    """Tight exit for H22's paired comparison: first close through the 5/12 EMA (computed from the day's
    bars up to that bar), 0.5% stop, flat at the close."""
    c = pd.Series(b["c"])
    e5, e12 = c.ewm(span=5, adjust=False).mean().values, c.ewm(span=12, adjust=False).mean().values
    n = len(c)
    if k + 1 >= n:
        return None
    entry = b["o"][k + 1]
    stop = entry * (1 - STOP * side)
    for j in range(k + 1, n):
        if side > 0 and b["l"][j] <= stop:
            ex = min(b["o"][j], stop)
        elif side < 0 and b["h"][j] >= stop:
            ex = max(b["o"][j], stop)
        elif (side > 0 and b["c"][j] < min(e5[j], e12[j])) or (side < 0 and b["c"][j] > max(e5[j], e12[j])) \
                or b["mins"][j] >= EOD or j == n - 1:
            ex = b["c"][j]
        else:
            continue
        return float(side * (ex / entry - 1) - cost)
    return None


# ------------------------------------------------------------------ sets
def rule_trades(days_by: dict) -> pd.DataFrame:
    out = []
    for s, days in days_by.items():
        prev_fr = []
        for day, b in days.items():
            r = h19(b)
            if r:
                t = trade(b, r[0], r[1], r[2])
                if t:
                    out.append(dict(rule="H19", sym=s, day=day, **t))
            r = h20(b)
            if r:
                k, side = r
                for name, stp in (("H20_nostop", None), ("H20_stop", "pct")):
                    stop = b["o"][k + 1] * (1 - STOP * side) if (stp and k + 1 < len(b["o"])) else None
                    t = trade(b, k, side, stop)
                    if t:
                        out.append(dict(rule=name, sym=s, day=day, **t))
            fh = first_hour(b)
            if fh:
                k, fr, d = fh
                if len(prev_fr) >= 20 and d != 0:
                    R = fr / np.mean(prev_fr[-20:])
                    for g in (1.25, 1.5, 2.0):
                        if R >= g and k + 1 < len(b["o"]):
                            t = trade(b, k, d, b["o"][k + 1] * (1 - STOP * d))
                            if t:
                                tight = f2_exit(b, k, d)
                                out.append(dict(rule=f"H22_R{g}", sym=s, day=day, R=R, tight=tight, **t))
                prev_fr.append(fr)
    return pd.DataFrame(out)


def random_trades(days_by: dict) -> pd.DataFrame:
    out = []
    for s, days in days_by.items():
        for seed in SEEDS:
            rng = np.random.default_rng(seed * 1000 + (1 if s == "SPY" else 2))
            for day, b in days.items():
                ok = np.where((b["mins"] >= 585) & (b["mins"] <= 905))[0]
                if len(ok) < PER_DAY:
                    continue
                for k in sorted(rng.choice(ok, size=PER_DAY, replace=False)):
                    side = int(rng.choice([1, -1]))
                    if int(k) + 1 >= len(b["o"]):
                        continue
                    t = trade(b, int(k), side, b["o"][int(k) + 1] * (1 - STOP * side))
                    if t:
                        out.append(dict(sym=s, seed=seed, day=day, sig_min=int(b["mins"][int(k)]), **t))
    return pd.DataFrame(out)


# ------------------------------------------------------------------ stats
def boot_days(t: pd.DataFrame, col: str = "net", n: int = 2000, seed: int = 7):
    by = [g[col].values for _, g in t.groupby("day")]
    if not by:
        return [None, None]
    rng = np.random.default_rng(seed)
    sums = np.array([x.sum() for x in by])
    cnts = np.array([len(x) for x in by])
    idx = rng.integers(0, len(by), size=(n, len(by)))
    means = sums[idx].sum(1) / cnts[idx].sum(1)
    return [float(np.percentile(means, 2.5) * 100), float(np.percentile(means, 97.5) * 100)]


def rnd_p95(rnd: pd.DataFrame, n: int, draws: int = 500, seed: int = 11) -> float | None:
    if rnd.empty or n == 0:
        return None
    rng = np.random.default_rng(seed)
    v = rnd["net"].values
    return float(np.percentile([rng.choice(v, size=n).mean() for _ in range(draws)], 95) * 100)


def stat(t: pd.DataFrame, sessions: list, rnd: pd.DataFrame | None = None, col: str = "net") -> dict:
    if t.empty:
        return dict(n=0)
    half = set(sessions[: len(sessions) // 2])
    h1, h2 = t[t["day"].isin(half)], t[~t["day"].isin(half)]
    y26 = t[t["day"] >= "2026-01-01"]
    L, S = t[t["side"] > 0], t[t["side"] < 0]
    m = lambda x: float(x[col].mean() * 100) if len(x) else None
    pos, neg = t[t["gross"] > 0]["gross"].sum(), -t[t["gross"] <= 0]["gross"].sum()
    out = dict(n=int(len(t)), days=int(t["day"].nunique()), mean=m(t), ci=boot_days(t, col),
               win=float((t[col] > 0).mean()), pf=float(pos / neg) if neg > 0 else None,
               mean_2x=float((t["gross"] - 2 * COST).mean() * 100),
               h1=m(h1), n1=int(len(h1)), h2=m(h2), n2=int(len(h2)), y2026=m(y26), n2026=int(len(y26)),
               long=m(L), long_n=int(len(L)), short=m(S), short_n=int(len(S)),
               stops=int((t["why"] == "stop").sum()) if "why" in t else None)
    if rnd is not None:
        out["rand_p95"] = rnd_p95(rnd, len(t))
    return out


def passes(s: dict) -> bool:
    if not s.get("n"):
        return False
    return bool(s["mean"] > 0 and s["ci"][0] > 0 and s["h1"] is not None and s["h1"] > 0 and s["h2"] is not None
                and s["h2"] > 0 and (s["long"] or 0) > 0 and (s["short"] or 0) > 0 and s["mean_2x"] > 0
                and s.get("rand_p95") is not None and s["mean"] > s["rand_p95"])


def diff_ci(a: pd.DataFrame, b: pd.DataFrame, n: int = 2000, seed: int = 7) -> dict:
    """mean(a) - mean(b) with a day-block bootstrap over the union of days."""
    if a.empty or b.empty:
        return dict(diff=None)
    days = sorted(set(a["day"]) | set(b["day"]))
    di = {d: i for i, d in enumerate(days)}
    def arr(t):
        s, c = np.zeros(len(days)), np.zeros(len(days))
        for d, g in t.groupby("day"):
            s[di[d]], c[di[d]] = g["net"].sum(), len(g)
        return s, c
    sa, ca = arr(a)
    sb, cb = arr(b)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(days), size=(n, len(days)))
    ma = sa[idx].sum(1) / np.maximum(ca[idx].sum(1), 1)
    mb = sb[idx].sum(1) / np.maximum(cb[idx].sum(1), 1)
    dd = (ma - mb) * 100
    return dict(diff=float((a["net"].mean() - b["net"].mean()) * 100),
                ci=[float(np.percentile(dd, 2.5)), float(np.percentile(dd, 97.5))], na=int(len(a)), nb=int(len(b)))


def h21(rnd: pd.DataFrame, sessions: list) -> dict:
    half = set(sessions[: len(sessions) // 2])
    out = {}
    for side, name in ((1, "long"), (-1, "short")):
        r = rnd[rnd["side"] == side]
        late, early = r[r["sig_min"] >= 780], r[r["sig_min"] < 780]
        res = dict(all=diff_ci(late, early))
        for hn, mask in (("h1", r["day"].isin(half)), ("h2", ~r["day"].isin(half))):
            rr = r[mask]
            res[hn] = diff_ci(rr[rr["sig_min"] >= 780], rr[rr["sig_min"] < 780])
        res["late_mean"] = float(late["net"].mean() * 100)
        res["early_mean"] = float(early["net"].mean() * 100)
        out[name] = res
    return out


def run(arch: Path, label: str) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    days_by = {s: days_of(load5(Path(arch) / f"{s}.csv.gz")) for s in SYMS}
    sessions = sorted(set().union(*[set(v) for v in days_by.values()]))
    rt, rnd = rule_trades(days_by), random_trades(days_by)
    res = dict(label=label, sessions=len(sessions), first=sessions[0], last=sessions[-1], rules={})
    for rule in sorted(rt["rule"].unique()) if not rt.empty else []:
        t = rt[rt["rule"] == rule]
        s = stat(t, sessions, rnd)
        s["pass"] = passes(s)
        s["by_sym"] = {k: float(g["net"].mean() * 100) for k, g in t.groupby("sym")}
        if rule == "H20_nostop":
            fade = t.assign(net=-t["gross"] - COST, gross=-t["gross"], side=-t["side"])
            s["fade"] = stat(fade, sessions)
        if rule.startswith("H22"):
            tt = t.dropna(subset=["tight"])
            s["hold_vs_tight"] = dict(hold=float(tt["net"].mean() * 100), tight=float(tt["tight"].mean() * 100),
                                      n=int(len(tt)))
        res["rules"][rule] = s
    res["random"] = stat(rnd, sessions)
    res["H21"] = h21(rnd, sessions)
    return res, rt, rnd


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--long", required=True)
    ap.add_argument("--a")
    ap.add_argument("--b")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    summary = {}
    for label, arch in (("L", a.long), ("A", a.a), ("B", a.b)):
        if not arch:
            continue
        res, rt, rnd = run(Path(arch), label)
        summary[label] = res
        rt.to_csv(out / f"rules_{label}.csv.gz", index=False)
    (out / "summary.json").write_text(json.dumps(summary, indent=1, default=str))
    print(json.dumps({k: {r: (v["n"], round(v["mean"], 4) if v.get("n") else None, v.get("pass"))
                          for r, v in s["rules"].items()} for k, s in summary.items()}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
