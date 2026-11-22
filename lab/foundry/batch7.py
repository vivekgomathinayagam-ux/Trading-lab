"""Foundry batch 7 (pre-registered: research/foundry/PREREG_batch7.md and PREREG_volspike_grid.md).

Desk replays on the Alpaca 1-min archive with the paper desks' own code:
  * signals: strategies.daytrade.core Features + rule.signal(), entry window 09:35-15:30
  * outcome of a signal: Desk order of operations (fill next bar open + slip; eod / stop / target)
  * a variant's trades: its first passing signal of each session (one entry per day, symbol
    priority on ties), skipping sessions where the previous trade is still open.

Usage: python -m lab.foundry.batch7 <alpaca1m dir> <out dir> [dev|holdout]
"""
from __future__ import annotations

import json
import math
import sys
from datetime import datetime, time as dtime
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

from strategies.daytrade.core import (ENTRY_END, ENTRY_START, FLAT_AT, SLIP, STOP_PCT, SYMBOLS,
                                      TARGET_PCT, Bar, EMACross, Features, ORB, VolSpike)

PRIO = {s: i for i, s in enumerate(SYMBOLS)}
LONG_SIDE = ["SPY", "QQQ", "TQQQ", "UPRO"]
SHORT_SIDE = ["SQQQ", "SPXU"]
UNDER = {"SPY": ("SPY", 1), "QQQ": ("QQQ", 1), "UPRO": ("SPY", 1), "TQQQ": ("QQQ", 1),
         "SPXU": ("SPY", -1), "SQQQ": ("QQQ", -1)}
LENGTHS = [5, 8, 9, 10, 13, 20, 21, 34, 50, 100, 200]
TFS = [1, 5, 15]
EQUITY = 1000.0
DEV_END = "2025-12-31"


# ------------------------------------------------------------------ data
def load(path: Path) -> pd.DataFrame:
    d = pd.read_csv(path)
    d["ts"] = pd.to_datetime(d["t"], utc=True).dt.tz_convert("America/New_York")
    d = d[(d.ts.dt.time >= dtime(9, 30)) & (d.ts.dt.time < dtime(16, 0))].copy()
    d = d.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    d["day"] = d.ts.dt.date.astype(str)
    d["m"] = d.ts.dt.hour * 60 + d.ts.dt.minute - 570
    return split_adjust(d)


SPLITS: dict = {}


def split_adjust(d: pd.DataFrame) -> pd.DataFrame:
    """Raw Alpaca bars: back-adjust prices (and volume inversely) at overnight jumps > 35%
    (splits / reverse splits), so multi-session MAs and volume baselines are continuous.
    Intraday % moves are unchanged."""
    d["v"] = d["v"].astype(float)
    first = d.groupby("day").head(1).index
    prev_close = d["c"].shift(1)
    ratio = (d.loc[first, "o"] / prev_close.loc[first]).dropna()
    jumps = ratio[(ratio > 1.35) | (ratio < 1 / 1.35)]
    for idx, r in jumps.items():
        f = round(r) if r > 1 else 1 / round(1 / r)
        for col in ("o", "h", "l", "c"):
            d.loc[: idx - 1, col] = d.loc[: idx - 1, col] * f
        d.loc[: idx - 1, "v"] = d.loc[: idx - 1, "v"] / f
    SPLITS[id(d)] = [(d.loc[i, "day"], float(r)) for i, r in jumps.items()]
    return d


def to_bars(d: pd.DataFrame) -> list[Bar]:
    return [Bar(t.to_pydatetime(), o, h, l, c, v)
            for t, o, h, l, c, v in zip(d.ts, d.o, d.h, d.l, d.c, d.v)]


# ------------------------------------------------------------------ signals and outcomes
def signals(d: pd.DataFrame, rules: dict, trade_from: str) -> dict:
    """{rule key: [bar index, ...]} signals at bar close, inside the entry window."""
    f = Features(bar_minutes=1)
    out = {k: [] for k in rules}
    bars = to_bars(d)
    days = d["day"].values
    for i, b in enumerate(bars):
        f.update(b)
        if days[i] < trade_from:
            continue
        tt = b.t.time()
        if not (ENTRY_START <= tt < ENTRY_END):
            continue
        for k, r in rules.items():
            if r.signal(f, b):
                out[k].append(i)
    return out


_ARR: dict = {}


def _arrays(d: pd.DataFrame) -> dict:
    """Numpy views of a session frame, cached by object id (not in DataFrame.attrs: pandas deep-copies
    attrs on every column access, which made the first full run crawl)."""
    a = _ARR.get(id(d))
    if a is None or len(a["o"]) != len(d):
        a = {"o": d.o.values, "h": d.h.values, "l": d.l.values, "c": d.c.values, "m": d.m.values,
             "day": d.day.values}
        _ARR[id(d)] = a
    return a


FLAT_M = FLAT_AT.hour * 60 + FLAT_AT.minute - 570
END_M = ENTRY_END.hour * 60 + ENTRY_END.minute - 570


def outcome(d: pd.DataFrame, i: int, slip_mult: float = 1.0, sym: str = "SPY", target_pct: float = TARGET_PCT):
    """Trade from a signal at bar i (Desk rules). Returns dict or None (pending invalid)."""
    a = _arrays(d)
    n = len(a["o"])
    j = i + 1
    if j >= n or a["day"][j] != a["day"][i] or a["m"][j] >= END_M:
        return None
    slip = SLIP[sym] * slip_mult
    o, h, l, m = a["o"], a["h"], a["l"], a["m"]
    entry = o[j] * (1 + slip)
    stop, target = entry * (1 - STOP_PCT), entry * (1 + target_pct)
    qty = int(EQUITY // entry)
    if qty < 1:
        return None
    k, start = None, j
    while start < n:                       # session by session (a short session carries over)
        end = start
        dd = a["day"][start]
        end = np.searchsorted(a["day"], dd, side="right") if a["day"][-1] != dd else n
        seg = slice(start, end)
        hit = (m[seg] >= FLAT_M) | (l[seg] <= stop) | (h[seg] >= target)
        if hit.any():
            k = start + int(np.argmax(hit))
            break
        start = end
    if k is None:
        k = n - 1
        px, why = a["c"][k], "end"
    elif m[k] >= FLAT_M:
        px, why = o[k], "eod"
    elif l[k] <= stop:
        px, why = min(o[k], stop), "stop"
    else:
        px, why = max(o[k], target), "target"
    exitp = px * (1 - slip)
    return {"entry_i": j, "exit_i": k, "entry": entry, "exit": exitp, "reason": why, "qty": qty,
            "move": (exitp / entry - 1) * 100, "pnl": qty * (exitp - entry) / EQUITY * 100}


def outcomes_fast(d: pd.DataFrame, idx: list, sym: str, slip_mult: float = 1.0) -> list:
    """Vectorised over a session: same results as outcome() (tested)."""
    return [outcome(d, i, slip_mult, sym) for i in idx]


def signal_table(data: dict, rules: dict, trade_from: str) -> pd.DataFrame:
    rows = []
    for sym, d in data.items():
        sig = signals(d, rules, trade_from)
        dayv = d.day.values
        for key, idx in sig.items():
            if not key.startswith("volspike"):          # only a session's first signal per symbol can be picked
                seen, keep = set(), []
                for i in idx:
                    if dayv[i] not in seen:
                        seen.add(dayv[i]); keep.append(i)
                idx = keep
            for i in idx:
                o1 = outcome(d, i, 1.0, sym)
                if o1 is None:
                    rows.append({"rule": key, "sym": sym, "i": i, "valid": False, "day": d.day.values[i], "t": d.ts.iloc[i], "exit_t": d.ts.iloc[i]})
                    continue
                o2 = outcome(d, i, 2.0, sym)
                rows.append({"rule": key, "sym": sym, "i": i, "valid": True, "day": d.day.values[i],
                             "t": d.ts.iloc[i], "exit_t": d.ts.iloc[o1["exit_i"]], "reason": o1["reason"],
                             "move": o1["move"], "pnl": o1["pnl"], "pnl2": o2["pnl"] if o2 else np.nan,
                             "entry_t": d.ts.iloc[o1["entry_i"]]})
    s = pd.DataFrame(rows)
    if s.empty:
        return s
    s["prio"] = s.sym.map(PRIO)
    s["t"] = pd.to_datetime(s["t"], utc=True)
    s["exit_t"] = pd.to_datetime(s["exit_t"], utc=True)
    return s.sort_values(["t", "prio"]).reset_index(drop=True)


def pick(s: pd.DataFrame, mask: np.ndarray | None = None) -> pd.DataFrame:
    """Desk selection: first passing signal of each session; an invalid first signal (pending
    cleared at 15:30) uses up nothing but is skipped; a session whose start is inside the
    previous trade (carried past a short session) is skipped."""
    c = s if mask is None else s[mask]
    c = c[c.valid]
    first = c.drop_duplicates("day", keep="first")
    if (first.exit_t.dt.date.astype(str) != first.day).any():
        keep, last_exit = [], None
        for r in first.itertuples():
            if last_exit is not None and r.t <= last_exit:
                continue
            keep.append(r.Index)
            last_exit = r.exit_t
        first = first.loc[keep]
    return first


# ------------------------------------------------------------------ MA features
def bucket_series(d: pd.DataFrame, tf: int) -> pd.DataFrame:
    g = d.assign(bid=d.m // tf).groupby(["day", "bid"], sort=True)
    b = g["c"].last().reset_index()
    b["end"] = b.bid * tf + tf - 1
    return b


def ma(x: pd.Series, kind: str, n: int) -> np.ndarray:
    if kind == "EMA":
        return x.ewm(span=n, adjust=False).mean().values
    return x.rolling(n).mean().values


def ma_features(data: dict, sig: pd.DataFrame) -> pd.DataFrame:
    """For every signal row: close and MA values (now and 3 buckets earlier) on its own symbol
    and its underlying, using only buckets closed at or before the signal bar's close."""
    feats = {}
    keys = {}
    for sym, d in data.items():
        dayidx = {dd: k for k, dd in enumerate(sorted(d.day.unique()))}
        keys[sym] = dayidx
        for tf in TFS:
            b = bucket_series(d, tf)
            bkey = b.day.map(dayidx).values * 1000 + b.end.values
            cols = {}
            for kind in ("EMA", "SMA"):
                for n in LENGTHS:
                    cols[(kind, n)] = ma(b.c, kind, n)
            feats[(sym, tf)] = (bkey, cols)
    out = {}
    for view in ("own", "und"):
        for sym in sig.sym.unique():
            rows = sig.index[sig.sym == sym]
            u, sgn = (sym, 1) if view == "own" else UNDER[sym]
            du = data[u]
            t = sig.loc[rows, "t"].dt.tz_convert("America/New_York")
            dk = t.dt.date.astype(str).map(keys[u]).values
            mk = (t.dt.hour * 60 + t.dt.minute - 570).values
            key = dk * 1000 + mk
            ukey = du.day.map(keys[u]).values * 1000 + du.m.values      # underlying bar close at t
            ui = np.searchsorted(ukey, key, side="right") - 1
            close = du.c.values[ui]
            out.setdefault((view, "close"), pd.Series(np.nan, index=sig.index)).loc[rows] = close
            out.setdefault((view, "sgn"), pd.Series(np.nan, index=sig.index)).loc[rows] = sgn
            for tf in TFS:
                bkey, cols = feats[(u, tf)]
                bi = np.searchsorted(bkey, key, side="right") - 1
                for (kind, n), v in cols.items():
                    now = np.where(bi >= 0, v[np.clip(bi, 0, None)], np.nan)
                    prev = np.where(bi >= 3, v[np.clip(bi - 3, 0, None)], np.nan)
                    out.setdefault((view, tf, kind, n, "now"), pd.Series(np.nan, index=sig.index)).loc[rows] = now
                    out.setdefault((view, tf, kind, n, "prev"), pd.Series(np.nan, index=sig.index)).loc[rows] = prev
    return pd.DataFrame({"|".join(map(str, k)): v for k, v in out.items()})


def col(view, *rest) -> str:
    return "|".join(map(str, (view,) + rest))


def grid_filters(F: pd.DataFrame) -> dict:
    """name -> boolean mask (924 filters; the 11-18 pre-reg said 1,188 by an arithmetic slip: 2x11x3x2 = 132 singles, not 264). Inverse ETFs mirrored in the underlying view."""
    masks = {}
    for view in ("own", "und"):
        sgn = F[col(view, "sgn")].values
        close = F[col(view, "close")].values
        for tf in TFS:
            for kind in ("EMA", "SMA"):
                for n in LENGTHS:
                    now = F[col(view, tf, kind, n, "now")].values
                    prev = F[col(view, tf, kind, n, "prev")].values
                    masks[f"{view}|{tf}m|{kind}{n}|above"] = np.nan_to_num(sgn * (close - now)) > 0
                    masks[f"{view}|{tf}m|{kind}{n}|slope"] = np.nan_to_num(sgn * (now - prev)) > 0
                for a, b in combinations(LENGTHS, 2):
                    fa = F[col(view, tf, kind, a, "now")].values
                    fb = F[col(view, tf, kind, b, "now")].values
                    masks[f"{view}|{tf}m|{kind}{a}>{kind}{b}"] = np.nan_to_num(sgn * (fa - fb)) > 0
    return masks


# ------------------------------------------------------------------ statistics
def boot_ci(x: np.ndarray, n: int = 2000, seed: int = 7) -> tuple:
    if len(x) < 2:
        return (math.nan, math.nan)
    rng = np.random.default_rng(seed)
    m = rng.choice(x, size=(n, len(x)), replace=True).mean(axis=1)
    return (float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)))


def summary(t: pd.DataFrame, rnd_pool: np.ndarray | None = None) -> dict:
    if t.empty:
        return {"n": 0}
    x = t.pnl.values
    yr = t.day.str[:4]
    h1 = x[(yr <= "2023").values]
    h2 = x[((yr >= "2024") & (yr <= "2025")).values]
    lo, hi = boot_ci(x)
    out = {"n": int(len(x)), "mean": float(x.mean()), "ci": [lo, hi], "win": float((x > 0).mean()),
           "mean_2x": float(np.nanmean(t.pnl2.values)), "h1": float(h1.mean()) if len(h1) else None,
           "h2": float(h2.mean()) if len(h2) else None, "n_h1": int(len(h1)), "n_h2": int(len(h2)),
           "targets": int((t.reason == "target").sum()), "stops": int((t.reason == "stop").sum()),
           "pf": float(x[x > 0].sum() / -x[x <= 0].sum()) if (x <= 0).any() and x[x <= 0].sum() < 0 else None}
    if rnd_pool is not None and len(rnd_pool) and len(x):
        rng = np.random.default_rng(11)
        draws = rng.choice(rnd_pool, size=(500, len(x)), replace=True).mean(axis=1)
        out["rnd_p95"] = float(np.percentile(draws, 95))
    return out


def passes(s: dict) -> bool:
    return bool(s.get("n", 0) >= 100 and s["mean"] > 0 and s["ci"][0] > 0 and (s["h1"] or 0) > 0
                and (s["h2"] or 0) > 0 and s["mean_2x"] > 0 and s["mean"] > s.get("rnd_p95", math.inf))


def random_pool(data: dict, syms: list, sessions: list, per: int = 3, seed: int = 21) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for day in sessions:
        for _ in range(per):
            sym = syms[rng.integers(len(syms))]
            d = data[sym]
            ii = np.where((d.day.values == day))[0] if False else None
            rows.append((day, sym))
    # vectorised lookup of candidate bars per (sym, day)
    out = []
    by = {}
    for sym in set(s for _, s in rows):
        d = data[sym]
        tt = d.ts.dt.time
        ok = (tt >= ENTRY_START) & (tt < ENTRY_END)
        by[sym] = d.index[ok].to_series().groupby(d.day[ok]).agg(list).to_dict()
    for day, sym in rows:
        cand = by[sym].get(day)
        if not cand:
            continue
        i = cand[rng.integers(len(cand))]
        o = outcome(data[sym], i, 1.0, sym)
        if o:
            out.append({"day": day, "sym": sym, "pnl": o["pnl"]})
    return pd.DataFrame(out)


# ------------------------------------------------------------------ runs
def load_all(src: Path) -> dict:
    return {s: load(src / f"{s}.csv.gz") for s in SYMBOLS}


def rules_all() -> dict:
    return {"volspike": VolSpike(), "volspike_2x": VolSpike(2.0),
            "orb_3x": ORB(3.0), "orb_1.5x": ORB(1.5), "orb_none": ORB(None),
            "ema_3x": EMACross(3.0), "ema_1.5x": EMACross(1.5), "ema_none": EMACross(None)}


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    src, out = Path(argv[0]), Path(argv[1])
    stage = argv[2] if len(argv) > 2 else "dev"
    out.mkdir(parents=True, exist_ok=True)
    data = load_all(src)
    days = sorted(set().union(*[set(d.day) for d in data.values()]))
    trade_from = days[3]
    sig_path = out / "signals.pkl"
    if sig_path.exists():
        sig = pd.read_pickle(sig_path)
    else:
        sig = signal_table(data, rules_all(), trade_from)
        sig.to_pickle(sig_path)
    splits = {s: SPLITS.get(id(d), []) for s, d in data.items()}
    dev_days = [d for d in days if trade_from <= d <= DEV_END]
    hold_days = [d for d in days if d > DEV_END]
    pool = random_pool(data, SYMBOLS, dev_days)
    pool_h = random_pool(data, SYMBOLS, hold_days, seed=22)
    report = {"splits": splits, "sessions_dev": len(dev_days), "sessions_holdout": len(hold_days),
              "first_day": trade_from, "last_day": days[-1]}
    if stage == "dev":
        report.update(run_dev(data, sig, pool, out))
    else:
        report.update(run_holdout(data, sig, pool_h, out))
    (out / f"{stage}.json").write_text(json.dumps(report, indent=1, default=str))
    print(json.dumps({k: v for k, v in report.items() if k not in ("grid_top", "h25", "h26")}, indent=1, default=str)[:3000])
    return 0


def run_dev(data, sig, pool, out) -> dict:
    vs = sig[(sig.rule == "volspike")].reset_index(drop=True)
    dev = vs[vs.day <= DEV_END].reset_index(drop=True)
    F = ma_features(data, dev)
    masks = grid_filters(F)
    base = pick(dev)
    bs = summary(base, pool.pnl.values)
    rng = np.random.default_rng(5)
    rows, rnd_imp = [], []
    for name, m in masks.items():
        t = pick(dev, m)
        x = t.pnl.values
        rows.append({"filter": name, "n": len(x), "mean": x.mean() if len(x) else np.nan,
                     "keep_rate": float(m[dev.valid.values].mean())})
        rm = rng.random(len(dev)) < m.mean()
        rt = pick(dev, rm)
        rnd_imp.append(rt.pnl.mean() - bs["mean"] if len(rt) else np.nan)
    g = pd.DataFrame(rows)
    g["imp"] = g["mean"] - bs["mean"]
    p95 = float(np.nanpercentile(rnd_imp, 95))
    elig = g[g.n >= 100].sort_values("mean", ascending=False)
    top = elig.head(3)["filter"].tolist()
    from scipy import stats as st
    tt = pick(dev, masks[top[0]])
    tstat, p = st.ttest_ind(tt.pnl.values, base.pnl.values, equal_var=False, alternative="greater")
    g.to_csv(out / "grid_dev.csv", index=False)
    tops = {}
    for name in top:
        tops[name] = summary(pick(dev, masks[name]), pool.pnl.values)
    return {"grid_variants": len(masks) + 2, "base_dev": bs, "random_imp_p95": p95,
            "n_beat_random_p95": int((elig.imp > p95).sum()), "n_eligible": int(len(elig)),
            "n_positive_mean": int((elig["mean"] > 0).sum()),
            "top3": top, "top3_dev": tops, "top_bonferroni_p": float(min(1.0, p * len(masks))),
            "top_raw_p": float(p), **run_h25_h26(sig[sig.day <= DEV_END], pool)}


def run_h25_h26(sig, pool) -> dict:
    h25 = {}
    for rule in ("orb_3x", "orb_1.5x", "orb_none", "ema_3x", "ema_1.5x", "ema_none", "volspike", "volspike_2x"):
        s = sig[sig.rule == rule]
        for side, syms in (("long", LONG_SIDE), ("short", SHORT_SIDE)):
            h25[f"{rule}|{side}"] = summary(pick(s[s.sym.isin(syms)]), pool.pnl.values)
    h26 = {}
    for rule in ("orb_none", "ema_none", "volspike"):
        s = sig[sig.rule == rule]
        one = pick(s)
        lo, sh = pick(s[s.sym.isin(LONG_SIDE)]), pick(s[s.sym.isin(SHORT_SIDE)])
        two = pd.concat([lo, sh])
        nd = s.day.nunique()
        h26[rule] = {"one_slot": summary(one), "two_slot": summary(two),
                     "pnl_per_signal_day_one": float(one.pnl.sum() / nd), "pnl_per_signal_day_two": float(two.pnl.sum() / nd)}
    return {"h25": h25, "h26": h26}


def run_holdout(data, sig, pool, out) -> dict:
    frozen = json.loads((out / "dev.json").read_text())
    vs = sig[(sig.rule == "volspike") & (sig.day > DEV_END)].reset_index(drop=True)
    F = ma_features(data, vs)
    masks = grid_filters(F)
    base = pick(vs)
    res = {"base_holdout": summary(base, pool.pnl.values), "top3_holdout": {}}
    bm = res["base_holdout"]["mean"]
    for name in frozen["top3"]:
        t = pick(vs, masks[name])
        s = summary(t, pool.pnl.values)
        x = t.pnl.values
        half = t.day <= "2026-06-30"
        s["hold_h1"] = float(x[half.values].mean()) if half.any() else None
        s["hold_h2"] = float(x[~half.values].mean()) if (~half).any() else None
        s["passes_v2"] = bool(s["n"] >= 20 and s["mean"] > bm and s["ci"][0] > bm and (s["hold_h1"] or -1) > 0
                              and (s["hold_h2"] or -1) > 0 and s["mean_2x"] > 0)
        res["top3_holdout"][name] = s
    hs = sig[sig.day > DEV_END]
    res.update({"holdout_" + k: v for k, v in run_h25_h26(hs, pool).items()})
    return res


def h27(sig: pd.DataFrame, tempest_csv: Path, rules=("volspike", "orb_3x", "ema_3x")) -> dict:
    """H27: prior-close Tempest term_slope > 0 (stress) -> only inverse-ETF signals; else only bull ETFs."""
    tv = pd.read_csv(tempest_csv).sort_values("date")
    tv["stress_next"] = (tv.term_slope > 0).shift(1)          # the prior session's close decides
    m = dict(zip(tv.date, tv.stress_next))
    res = {}
    for rule in rules:
        s = sig[(sig.rule == rule) & (sig.day >= tv.date.iloc[1])].copy()
        s["stress"] = s.day.map(m)
        s = s[s.stress.notna()]
        inv = s.sym.isin(SHORT_SIDE).values
        st = s.stress.astype(bool).values
        days = sorted(s.day.unique())
        mid = days[len(days) // 2]
        out = {}
        for name, mask in (("base", None), ("gate", (st & inv) | (~st & ~inv)), ("calm_only", ~st)):
            t = pick(s, mask)
            sm = summary(t)
            sm["h1"] = float(t[t.day < mid].pnl.mean())
            sm["h2"] = float(t[t.day >= mid].pnl.mean())
            out[name] = sm
        res[rule] = out
    return res


def h28(data: dict, sig: pd.DataFrame, rules=("volspike", "orb_3x", "ema_3x", "orb_none")) -> dict:
    """H28: same entries, +5% target (spec) vs no target (stop and 15:55 only); paired per trade."""
    res = {}
    for rule in rules:
        t = pick(sig[sig.rule == rule]).copy()
        b = [outcome(data[r.sym], int(r.i), 1.0, r.sym, target_pct=1e9) for r in t.itertuples()]
        b2 = [outcome(data[r.sym], int(r.i), 2.0, r.sym, target_pct=1e9) for r in t.itertuples()]
        t["pnl_hold"] = [x["pnl"] for x in b]
        t["pnl_hold2"] = [x["pnl"] for x in b2]
        t["diff"] = t.pnl_hold - t.pnl
        inv = t.sym.isin(SHORT_SIDE)
        out = {}
        for cell, m in (("all", slice(None)), ("inverse", inv), ("bull", ~inv)):
            c = t[m]
            for per, pm in (("dev", c.day <= DEV_END), ("dev_h1", c.day <= "2023-12-31"),
                            ("dev_h2", (c.day > "2023-12-31") & (c.day <= DEV_END)), ("holdout", c.day > DEV_END)):
                x = c[pm]
                if x.empty:
                    continue
                lo, hi = boot_ci(x["diff"].values)
                out[f"{cell}|{per}"] = {"n": int(len(x)), "target_mean": float(x.pnl.mean()),
                                        "hold_mean": float(x.pnl_hold.mean()), "hold_mean_2x": float(x.pnl_hold2.mean()),
                                        "diff": float(x["diff"].mean()), "diff_ci": [lo, hi],
                                        "targets": int((x.reason == "target").sum())}
        res[rule] = out
    return res


if __name__ == "__main__":
    sys.exit(main())
