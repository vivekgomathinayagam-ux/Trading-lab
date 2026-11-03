"""Foundry batch 1 (pre-registered in research/foundry/PREREG.md).

Pure pandas/numpy. Input: 1-minute or 5-minute regular-hours bars per symbol.
Everything is decided at a 5-minute bar's close and filled at the next bar's open.

  python -m lab.foundry.rules --archive <dir with SYM.csv.gz> --syms SPY,QQQ --out out/foundry
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

SLIP = 0.0002
FEE = 0.00003
COST = 2 * (SLIP + FEE)          # round trip, fraction
HARD_STOP = 0.005
RULES = ["F1_cloud_ride", "F2_cloud_ride_tight", "F3_vwap_trend", "F4_trend_break", "F5_fib_618", "F6_fib_382"]


# ------------------------------------------------------------------ data
def load_bars(path: Path) -> pd.DataFrame:
    d = pd.read_csv(path)
    d["t"] = pd.to_datetime(d["t"], utc=True).dt.tz_convert("America/New_York")
    d = d.set_index("t").sort_index()
    m = d.index.hour * 60 + d.index.minute
    d = d[(m >= 570) & (m < 960) & (d.index.dayofweek < 5)]
    return d[["o", "h", "l", "c", "v"]].astype(float)


def to_5min(d: pd.DataFrame) -> pd.DataFrame:
    if len(d) > 1 and (d.index[1] - d.index[0]) >= pd.Timedelta(minutes=5):
        return d
    out = []
    for day, g in d.groupby(d.index.date):
        r = g.resample("5min", label="left", closed="left").agg(
            {"o": "first", "h": "max", "l": "min", "c": "last", "v": "sum"}).dropna()
        out.append(r)
    return pd.concat(out)


def add_features(d5: pd.DataFrame) -> pd.DataFrame:
    """Causal features. EMAs run continuously across days (like a chart);
    VWAP and session high/low reset each day."""
    d = d5.copy()
    for n in (5, 9, 12, 21, 34, 50):
        d[f"e{n}"] = d["c"].ewm(span=n, adjust=False).mean()
    day = pd.Series(d.index.date, index=d.index)
    tp = (d["h"] + d["l"] + d["c"]) / 3
    d["vwap"] = (tp * d["v"]).groupby(day).cumsum() / d["v"].groupby(day).cumsum().replace(0, np.nan)
    d["s_hi"] = d["h"].groupby(day).cummax()
    d["s_lo"] = d["l"].groupby(day).cummin()
    # bar index of the session high / low so far (to tell which came first)
    idx = pd.Series(np.arange(len(d)), index=d.index)
    d["hi_at"] = idx.where(d["h"] >= d["s_hi"]).groupby(day).ffill()
    d["lo_at"] = idx.where(d["l"] <= d["s_lo"]).groupby(day).ffill()
    above = (d["c"] > d["vwap"]).astype(int)
    below = (d["c"] < d["vwap"]).astype(int)
    # consecutive closes above/below VWAP, reset each day
    def run(s):
        out, k = [], 0
        for v in s:
            k = k + 1 if v else 0
            out.append(k)
        return pd.Series(out, index=s.index)
    d["run_above"] = above.groupby(day, group_keys=False).apply(run)
    d["run_below"] = below.groupby(day, group_keys=False).apply(run)
    d["day"] = day
    d["mins"] = d.index.hour * 60 + d.index.minute
    return d


# ------------------------------------------------------------------ simulation
def close_exit(rule: str, b: dict, side: int, pos: dict):
    c = b["c"]
    if rule == "F1_cloud_ride":
        lo, hi = min(b["e34"], b["e50"]), max(b["e34"], b["e50"])
        if (side > 0 and c < lo) or (side < 0 and c > hi):
            return "cloud"
    elif rule == "F2_cloud_ride_tight":
        lo, hi = min(b["e5"], b["e12"]), max(b["e5"], b["e12"])
        if (side > 0 and c < lo) or (side < 0 and c > hi):
            return "cloud"
    elif rule == "F3_vwap_trend":
        if (side > 0 and c < b["vwap"]) or (side < 0 and c > b["vwap"]):
            return "vwap"
    elif rule in ("F5_fib_618", "F6_fib_382"):
        lv = pos.get("fib_stop_close")
        if lv is not None and ((side > 0 and c < lv) or (side < 0 and c > lv)):
            return "fib_stop"
    return None


def entry_signal(rule: str, rows: list, i: int, fib_used: dict):
    b = rows[i]
    c, m = b["c"], b["mins"]
    if rule in ("F1_cloud_ride", "F2_cloud_ride_tight"):
        flo, fhi = min(b["e5"], b["e12"]), max(b["e5"], b["e12"])
        slo, shi = min(b["e34"], b["e50"]), max(b["e34"], b["e50"])
        if m < 9 * 60 + 45:
            return None
        if flo > shi and b["l"] <= fhi and c > b["e12"]:
            return (1, None, None)
        if fhi < slo and b["h"] >= flo and c < b["e12"]:
            return (-1, None, None)
    elif rule == "F3_vwap_trend":
        if m < 10 * 60 or i == 0 or rows[i - 1]["day"] != b["day"]:
            return None
        p = rows[i - 1]
        if c > b["vwap"] and p["c"] <= p["vwap"] and b["e9"] > b["e21"]:
            return (1, None, None)
        if c < b["vwap"] and p["c"] >= p["vwap"] and b["e9"] < b["e21"]:
            return (-1, None, None)
    elif rule == "F4_trend_break":
        if i < 6 or rows[i - 1]["day"] != b["day"]:
            return None
        p = rows[i - 1]
        recent = [r for r in rows[i - 6:i] if r["day"] == b["day"]]
        if not recent:
            return None
        if c < b["vwap"] and p["run_above"] >= 12:
            return (-1, max(r["h"] for r in recent), None)
        if c > b["vwap"] and p["run_below"] >= 12:
            return (1, min(r["l"] for r in recent), None)
    elif rule in ("F5_fib_618", "F6_fib_382"):
        if m < 10 * 60 + 30:
            return None
        hi, lo = b["s_hi"], b["s_lo"]
        rng = hi - lo
        if lo <= 0 or rng / lo < 0.004:
            return None
        z1, z2, stop_lv = (0.5, 0.618, 0.786) if rule == "F5_fib_618" else (0.382, 0.5, 0.618)
        key = (rule, b["day"])
        up = b["hi_at"] > b["lo_at"] and c > b["vwap"]
        dn = b["lo_at"] > b["hi_at"] and c < b["vwap"]
        if up and not fib_used.get(key + (1,)):
            top, bot = hi - z1 * rng, hi - z2 * rng
            if b["l"] <= top and c > top:
                fib_used[key + (1,)] = True
                sig = (1, None, hi)
                return _fib(sig, hi - stop_lv * rng)
        if dn and not fib_used.get(key + (-1,)):
            top = lo + z1 * rng
            if b["h"] >= top and c < top:
                fib_used[key + (-1,)] = True
                return _fib((-1, None, lo), lo + stop_lv * rng)
    return None


def _fib(sig, close_stop):
    side, _, target = sig
    # hard stop as a backstop beyond the close-based fib stop
    return (side, None, target) if close_stop is None else _FibSig(side, target, close_stop)


class _FibSig(tuple):
    def __new__(cls, side, target, close_stop):
        t = super().__new__(cls, (side, None, target))
        t.close_stop = close_stop
        return t


def simulate(d, rule, sym):
    """One position at a time per rule+symbol; at most 3 trades a day."""
    trades = []
    rows = d.reset_index().to_dict("records")
    n = len(rows)
    pos = pending = None
    count, fib_used = {}, {}
    for i in range(n):
        b = rows[i]
        day = b["day"]
        if i == 0 or rows[i - 1]["day"] != day:
            pending = None
        if pending is not None and pos is None:
            side, stop, target = pending
            pos = dict(side=side, entry=b["o"], stop=stop, target=target, i=i, t=b["t"], day=day,
                       fib_stop_close=getattr(pending, "close_stop", None))
            if pos["stop"] is None:
                pos["stop"] = b["o"] * (1 - HARD_STOP) if side > 0 else b["o"] * (1 + HARD_STOP)
            count[day] = count.get(day, 0) + 1
        pending = None
        if pos is not None:
            side, ex, why = pos["side"], None, None
            if side > 0:
                if b["l"] <= pos["stop"]:
                    ex, why = min(b["o"], pos["stop"]), "stop"
                elif pos["target"] and b["h"] >= pos["target"]:
                    ex, why = max(b["o"], pos["target"]), "target"
            else:
                if b["h"] >= pos["stop"]:
                    ex, why = max(b["o"], pos["stop"]), "stop"
                elif pos["target"] and b["l"] <= pos["target"]:
                    ex, why = min(b["o"], pos["target"]), "target"
            if ex is None:
                cx = close_exit(rule, b, side, pos)
                if cx:
                    ex, why = b["c"], cx
            last_bar = (i + 1 == n) or rows[i + 1]["day"] != day or b["mins"] >= 15 * 60 + 50
            if ex is None and last_bar:
                ex, why = b["c"], "eod"
            if ex is not None:
                gross = side * (ex / pos["entry"] - 1)
                trades.append(dict(sym=sym, rule=rule, day=str(day), side=side, t_in=str(pos["t"]),
                                   t_out=str(b["t"]), entry=pos["entry"], exit=ex, why=why,
                                   bars=i - pos["i"] + 1, net=gross - COST, gross=gross))
                pos = None
                continue
        if pos is None and 9 * 60 + 40 <= b["mins"] <= 15 * 60 + 25 and count.get(day, 0) < 3:
            sig = entry_signal(rule, rows, i, fib_used)
            if sig:
                pending = sig
    return trades


# ------------------------------------------------------------------ stats
def boot_ci(trades: pd.DataFrame, col="net", n=2000, seed=7):
    if trades.empty:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    days = trades["day"].unique()
    by = {dd: trades.loc[trades["day"] == dd, col].values for dd in days}
    means = []
    for _ in range(n):
        pick = rng.choice(days, size=len(days), replace=True)
        v = np.concatenate([by[p] for p in pick])
        means.append(v.mean())
    return tuple(np.percentile(means, [2.5, 97.5]))


def random_control(d: pd.DataFrame, tr: pd.DataFrame, draws=500, seed=11):
    """Same number of trades, same side mix and holding bars, random entry bars."""
    if tr.empty:
        return np.nan
    rng = np.random.default_rng(seed)
    o, c = d["o"].values, d["c"].values
    days = d["day"].values
    mins = d["mins"].values
    ok = np.where((mins >= 9 * 60 + 45) & (mins <= 15 * 60 + 30))[0]
    means = []
    for _ in range(draws):
        vals = []
        for _, t in tr.iterrows():
            for _try in range(20):
                k = rng.choice(ok)
                j = k + int(t["bars"]) - 1
                if j < len(c) and days[j] == days[k]:
                    vals.append(t["side"] * (c[j] / o[k] - 1) - COST)
                    break
        means.append(np.mean(vals) if vals else np.nan)
    return np.nanpercentile(means, 95)


def summarize(tr: pd.DataFrame, d_by_sym: dict, sessions: list) -> dict:
    out = {}
    half = set(sessions[: len(sessions) // 2])
    for rule in RULES + ["C1_long_0945"]:
        t = tr[tr["rule"] == rule]
        if t.empty:
            out[rule] = dict(trades=0)
            continue
        lo, hi = boot_ci(t)
        h1 = t[t["day"].isin([str(s) for s in half])]
        h2 = t[~t["day"].isin([str(s) for s in half])]
        rc = np.nanmean([random_control(d_by_sym[s], t[t["sym"] == s]) for s in t["sym"].unique()]) \
            if rule != "C1_long_0945" else np.nan
        wins = t[t["net"] > 0]["net"].sum()
        loss = -t[t["net"] < 0]["net"].sum()
        out[rule] = dict(
            trades=int(len(t)), win=round(float((t["net"] > 0).mean()), 3),
            exp_pct=round(100 * t["net"].mean(), 4), ci=[round(100 * lo, 4), round(100 * hi, 4)],
            pf=round(float(wins / loss), 2) if loss > 0 else None,
            exp_2x=round(100 * (t["net"] - COST).mean(), 4),
            half1=round(100 * h1["net"].mean(), 4) if len(h1) else None,
            half2=round(100 * h2["net"].mean(), 4) if len(h2) else None,
            n1=int(len(h1)), n2=int(len(h2)),
            longs=int((t["side"] > 0).sum()), shorts=int((t["side"] < 0).sum()),
            long_exp=round(100 * t[t["side"] > 0]["net"].mean(), 4) if (t["side"] > 0).any() else None,
            short_exp=round(100 * t[t["side"] < 0]["net"].mean(), 4) if (t["side"] < 0).any() else None,
            rand95=round(100 * rc, 4) if rc == rc else None,
            total_pct=round(100 * t["net"].sum(), 3),
            exits=t["why"].value_counts().to_dict(),
            avg_bars=round(float(t["bars"].mean()), 1),
            by_sym={s: round(100 * g["net"].mean(), 4) for s, g in t.groupby("sym")},
        )
    return out


def control_c1(d: pd.DataFrame, sym: str) -> list[dict]:
    out = []
    for day, g in d.groupby("day"):
        e = g[g["mins"] >= 9 * 60 + 45]
        x = g[g["mins"] <= 15 * 60 + 50]
        if e.empty or x.empty:
            continue
        en, ex = e["o"].iloc[0], x["c"].iloc[-1]
        out.append(dict(sym=sym, rule="C1_long_0945", day=str(day), side=1, t_in=str(e.index[0]),
                        t_out=str(x.index[-1]), entry=en, exit=ex, why="eod", bars=len(g), net=ex / en - 1 - COST,
                        gross=ex / en - 1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", required=True)
    ap.add_argument("--syms", default="SPY,QQQ")
    ap.add_argument("--out", required=True)
    ap.add_argument("--exclude-after", default=None, help="drop sessions after this date (holdout)")
    a = ap.parse_args()
    outd = Path(a.out)
    outd.mkdir(parents=True, exist_ok=True)
    all_tr, d_by = [], {}
    sessions = set()
    for s in a.syms.split(","):
        d = add_features(to_5min(load_bars(Path(a.archive) / f"{s}.csv.gz")))
        if a.exclude_after:
            d = d[d["day"].astype(str) <= a.exclude_after]
        d_by[s] = d
        sessions |= set(d["day"].unique())
        for r in RULES:
            all_tr += simulate(d, r, s)
        all_tr += control_c1(d, s)
    tr = pd.DataFrame(all_tr)
    sessions = sorted(sessions)
    tr.to_csv(outd / "trades.csv", index=False)
    summ = summarize(tr, d_by, sessions)
    meta = dict(sessions=len(sessions), first=str(sessions[0]), last=str(sessions[-1]), syms=a.syms)
    (outd / "summary.json").write_text(json.dumps(dict(meta=meta, rules=summ), indent=1, default=str))
    print(json.dumps(meta))
    for k, v in summ.items():
        print(k, json.dumps(v, default=str))


if __name__ == "__main__":
    main()
