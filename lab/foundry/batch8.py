"""Foundry batch 8 (pre-registered: research/foundry/PREREG_batch8.md, committed a5a1efd before computing).

H30 open-reversal ("V") days: count, then trade with / against the V at its confirmation.
H31 impulse fade: after a 1.5% leg, fade the first lower low (up-leg) / higher high (down-leg).
Underlying signed % per trade, signal at a 5-min close, fill next open, flat at the 15:50 bar's
close (= 15:55), costs = foundry COST.

  python -m lab.foundry.batch8 <out dir> L5=<alpaca5m dir> L1=<alpaca1m dir> Y1=<etf1m dir> Y5=<etf5m dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from lab.foundry.rules import COST, load_bars, to_5min

SYMS = ["SPY", "QQQ"]
EOD_M = 380          # 15:50 bar (closes 15:55)
GAP, FLUSH, VREC, V_END_M = 0.01, 0.01, 0.01, 70      # V close by the 10:40 bar (closes 10:45)
LEG, H31_START_M, H31_END_M = 0.015, 30, 300           # entries decided 10:00-14:30 closes


# ------------------------------------------------------------------ data
def sessions(path: Path) -> list[dict]:
    d = to_5min(load_bars(path))
    d = d.copy()
    d["m"] = d.index.hour * 60 + d.index.minute - 570
    d["day"] = d.index.date
    out, prev_close = [], None
    for day, g in d.groupby("day", sort=True):
        g = g.sort_values("m")
        s = {"day": str(day), "m": g.m.values, "o": g.o.values, "h": g.h.values, "l": g.l.values,
             "c": g.c.values, "pc": prev_close}
        out.append(s)
        prev_close = float(g.c.values[-1])
    return out


def _exit(s: dict, j: int, side: int, stop: float | None):
    """Hold from the open of bar j; stop checked on bar extremes; eod at the 15:50 bar's close."""
    entry = s["o"][j]
    for k in range(j, len(s["m"])):
        if stop is not None:
            if side < 0 and s["h"][k] >= stop:
                return entry, max(s["o"][k], stop), k, "stop"
            if side > 0 and s["l"][k] <= stop:
                return entry, min(s["o"][k], stop), k, "stop"
        if s["m"][k] >= EOD_M or k == len(s["m"]) - 1:
            return entry, s["c"][k], k, "eod"
    return None


def _trade(s, sym, cell, i, side, stop=None, extra=None):
    j = i + 1
    if j >= len(s["m"]) or s["m"][j] > EOD_M:
        return None
    r = _exit(s, j, side, stop)
    if r is None:
        return None
    entry, ex, k, why = r
    gross = side * (ex / entry - 1)
    t = dict(sym=sym, cell=cell, day=s["day"], side=side, sig_m=int(s["m"][i]), exit_m=int(s["m"][k]),
             why=why, gross=gross, net=gross - COST, net2=gross - 2 * COST)
    if extra:
        t.update(extra)
    return t


# ------------------------------------------------------------------ H30
def v_day(s: dict):
    """Returns (gap_dir, T_v bar index) or None. Uses bars up to T_v only."""
    if s["pc"] is None or len(s["m"]) < 20 or s["m"][0] != 0:
        return None
    o0 = s["o"][0]
    gap = o0 / s["pc"] - 1
    if abs(gap) < GAP:
        return None
    up = gap > 0
    flush_i, ext = None, None
    for i in range(len(s["m"])):
        m = s["m"][i]
        if m > V_END_M:
            return None
        if up:
            ext = s["l"][i] if ext is None else min(ext, s["l"][i])
            if flush_i is None and m <= 25 and ext <= o0 * (1 - FLUSH):
                flush_i = i
            if flush_i is not None and i > flush_i and s["c"][i] >= ext * (1 + VREC):
                return 1, i
        else:
            ext = s["h"][i] if ext is None else max(ext, s["h"][i])
            if flush_i is None and m <= 25 and ext >= o0 * (1 + FLUSH):
                flush_i = i
            if flush_i is not None and i > flush_i and s["c"][i] <= ext * (1 - VREC):
                return -1, i
    return None


def h30(ss: list[dict], sym: str) -> tuple[list, list]:
    trades, vdays = [], []
    for s in ss:
        v = v_day(s)
        if not v:
            continue
        gdir, i = v
        vdays.append(dict(sym=sym, day=s["day"], gap_dir=gdir, tv_m=int(s["m"][i])))
        g = "up" if gdir > 0 else "down"
        for cell, side in ((f"with_gap{g}", gdir), (f"fade_gap{g}", -gdir)):
            t = _trade(s, sym, cell, i, side, extra={"win_lo": int(s["m"][i]), "win_hi": 270})
            if t:
                trades.append(t)
    return trades, vdays


# ------------------------------------------------------------------ H31
def h31_session(s: dict, sym: str) -> list:
    out = []
    n = len(s["m"])
    hi = lo = None
    hi_i = lo_i = None
    lo_before_hi = hi_before_lo = None
    done = {1: False, -1: False}
    for i in range(n):
        h, l = s["h"][i], s["l"][i]
        new_hi = hi is None or h > hi
        new_lo = lo is None or l < lo
        if new_hi:
            hi, hi_i = h, i
            lo_before_hi = min(s["l"][: i + 1])
        if new_lo:
            lo, lo_i = l, i
            hi_before_lo = max(s["h"][: i + 1])
        m = s["m"][i]
        if not (H31_START_M <= m <= H31_END_M) or i == 0:
            continue
        # fade an up-impulse: first lower low after the bar that set the session high
        if not done[-1] and not new_hi and hi_i is not None and i > hi_i and l < s["l"][i - 1] \
                and hi / lo_before_hi - 1 >= LEG and _first_ll(s, hi_i, i):
            t = _trade(s, sym, "fade_up_short", i, -1, stop=hi * 1.001)
            if t:
                t["stop_pct"] = hi * 1.001 / s["o"][i + 1] - 1
                out.append(t)
            done[-1] = True
        if not done[1] and not new_lo and lo_i is not None and i > lo_i and h > s["h"][i - 1] \
                and 1 - lo / hi_before_lo >= LEG and _first_hh(s, lo_i, i):
            t = _trade(s, sym, "fade_down_long", i, 1, stop=lo * 0.999)
            if t:
                t["stop_pct"] = 1 - lo * 0.999 / s["o"][i + 1]
                out.append(t)
            done[1] = True
    return out


def _first_ll(s, hi_i, i):
    return not any(s["l"][k] < s["l"][k - 1] for k in range(hi_i + 1, i))


def _first_hh(s, lo_i, i):
    return not any(s["h"][k] > s["h"][k - 1] for k in range(lo_i + 1, i))


def h31(ss, sym):
    out = []
    for s in ss:
        out += h31_session(s, sym)
    return out


# ------------------------------------------------------------------ stats
def boot_ci(t: pd.DataFrame, col="net", n=2000, seed=7):
    if len(t) < 2:
        return [None, None]
    g = t.groupby("day")[col].agg(["sum", "count"])
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(g), size=(n, len(g)))
    s, c = g["sum"].values[idx].sum(1), g["count"].values[idx].sum(1)
    m = s / c
    return [round(float(np.percentile(m, 2.5)) * 100, 4), round(float(np.percentile(m, 97.5)) * 100, 4)]


_CAND: dict = {}


def random_p95(t: pd.DataFrame, by_day: dict, draws=500, seed=11):
    """Same sessions, side and exit; random signal bar inside the trade's window."""
    rng = np.random.default_rng(seed)
    rows = list(t.itertuples())
    if not rows:
        return None
    means = []
    for _ in range(draws):
        x = []
        for r in rows:
            s = by_day[(r.sym, r.day)]
            lo, hi = (r.win_lo, r.win_hi) if hasattr(r, "win_lo") and not pd.isna(getattr(r, "win_lo", np.nan)) \
                else (H31_START_M, H31_END_M)
            key = (r.sym, r.day, lo, hi)
            cand = _CAND.get(key)
            if cand is None:
                cand = _CAND[key] = [i for i in range(len(s["m"]) - 1) if lo <= s["m"][i] <= hi]
            if not cand:
                continue
            i = cand[rng.integers(0, len(cand))]
            stop = None
            if not pd.isna(getattr(r, "stop_pct", np.nan)):
                e = s["o"][i + 1]
                stop = e * (1 + r.stop_pct) if r.side < 0 else e * (1 - r.stop_pct)
            q = _trade(s, r.sym, "rnd", i, r.side, stop=stop)
            if q:
                x.append(q["net"])
        means.append(np.mean(x) if x else np.nan)
    return round(float(np.nanpercentile(means, 95)) * 100, 4)


def stats(t: pd.DataFrame, by_day=None, halves=None, rnd=True) -> dict:
    if t.empty:
        return {"n": 0}
    out = {"n": int(len(t)), "mean": round(float(t.net.mean()) * 100, 4), "ci": boot_ci(t),
           "mean_2x": round(float(t.net2.mean()) * 100, 4), "win": round(float((t.net > 0).mean()), 3),
           "stops": int((t.why == "stop").sum())}
    if halves:
        a, b = halves
        out["half1"] = round(float(t[t.day <= a].net.mean()) * 100, 4) if (t.day <= a).any() else None
        out["half2"] = round(float(t[t.day >= b].net.mean()) * 100, 4) if (t.day >= b).any() else None
        out["n_half"] = [int((t.day <= a).sum()), int((t.day >= b).sum())]
    if rnd and by_day is not None:
        out["rnd_p95"] = random_p95(t, by_day)
    return out


HALVES = {"L5": ("2022-12-31", "2023-01-01"), "L1": ("2023-12-31", "2024-01-01"), "Y1": None, "Y5": None}


def run(archives: dict) -> dict:
    res = {}
    for name, path in archives.items():
        by_day, tr30, tr31, vd = {}, [], [], []
        for sym in SYMS:
            f = Path(path) / f"{sym}.csv.gz"
            if not f.exists():
                continue
            ss = sessions(f)
            for s in ss:
                by_day[(sym, s["day"])] = s
            a, v = h30(ss, sym)
            tr30 += a
            vd += v
            tr31 += h31(ss, sym)
        t30, t31, vdf = pd.DataFrame(tr30), pd.DataFrame(tr31), pd.DataFrame(vd)
        n_sess = len({k[1] for k in by_day})
        r = {"sessions": n_sess, "v_days": {}, "H30": {}, "H31": {}}
        if not vdf.empty:
            vdf["year"] = vdf.day.str[:4]
            r["v_days"] = {f"{s}_{'up' if g > 0 else 'down'}": int(n) for (s, g), n in vdf.groupby(["sym", "gap_dir"]).size().items()}
            r["v_days_by_year"] = {y: int(n) for y, n in vdf.groupby("year").size().items()}
        hv = HALVES.get(name)
        big = name in ("L5", "L1")
        if not t30.empty:
            for cell, g in t30.groupby("cell"):
                r["H30"][cell] = stats(g, by_day, hv, rnd=big)
                r["H30"][cell]["by_sym"] = {s: round(float(x.net.mean()) * 100, 4) for s, x in g.groupby("sym")}
        if not t31.empty:
            for cell, g in t31.groupby("cell"):
                r["H31"][cell] = stats(g, by_day, hv, rnd=big)
                r["H31"][cell]["by_sym"] = {s: round(float(x.net.mean()) * 100, 4) for s, x in g.groupby("sym")}
        res[name] = r
        res[name]["_trades"] = (t30, t31)
    return res


def passes(L5: dict, L1: dict) -> bool:
    if not L5 or L5.get("n", 0) < 60:
        return False
    return bool(L5["mean"] > 0 and L5["ci"][0] is not None and L5["ci"][0] > 0 and (L5.get("half1") or 0) > 0
                and (L5.get("half2") or 0) > 0 and L5["mean_2x"] > 0 and L5.get("rnd_p95") is not None
                and L5["mean"] > L5["rnd_p95"] and L1 and (L1.get("half1") or 0) > 0 and (L1.get("half2") or 0) > 0)


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    out = Path(argv[0])
    out.mkdir(parents=True, exist_ok=True)
    arch = dict(a.split("=", 1) for a in argv[1:])
    res = run(arch)
    for name, r in res.items():
        t30, t31 = r.pop("_trades")
        if not t30.empty:
            t30.to_csv(out / f"h30_{name}.csv", index=False)
        if not t31.empty:
            t31.to_csv(out / f"h31_{name}.csv", index=False)
    verdict = {}
    for h in ("H30", "H31"):
        for cell in (res.get("L5", {}).get(h) or {}):
            verdict[f"{h}:{cell}"] = passes(res["L5"][h][cell], (res.get("L1", {}).get(h) or {}).get(cell, {}))
    res["verdict"] = verdict
    (out / "summary.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps(res, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
