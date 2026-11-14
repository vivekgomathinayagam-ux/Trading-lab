"""Foundry batch 5 (pre-registered in research/foundry/PREREG_batch5.md before any result was computed).

H14 profit-lock exit (paired), H15 CVD down-morning gate, H16 H13 diagnostics, H17 ORB first-break-only,
H18 regime check of LESSONS 24. Research only: nothing here trades.

  python -m lab.foundry.batch5 --archive1m A --archive5m B --desk-trades trades_1m.csv --out out/foundry/batch5
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from lab.foundry import rules as R
from lab.foundry.batch3 import CANDIDATES as B3, simulate as sim3, stat as stat3
from lab.foundry.batch4 import (EOD_MIN, INDEX, INV, LEV, SLIP, _boot_ratio, _day_sums, by_day, day_shape, halves,
                                load1m, open1_signal, random_set, run_archive, trade_from)
from lab.foundry.rules import COST, add_features, to_5min

ARMS = [0.007, 0.0035, 0.01]          # primary first; the others are reported only
GATE = 0.005
GATE_END = 10 * 60 + 30
EARLY = (9 * 60 + 45, 10 * 60 + 25)
TIME_BARS = 6                          # 30 minutes of 5-min bars
STOP = 0.005
DELAY = 3


# ------------------------------------------------------------------ H14 profit lock
def profit_lock(rows: list, i_fill: int, j_exit: int, side: int, entry: float, base_net: float, arm: float,
                cost: float = COST) -> tuple[float, bool, bool]:
    """Paired variant. rows: one day's 5-min rows with e5/e12; i_fill: fill row; j_exit: row where the base
    exit happened. Uses each bar's own range/close and EMAs (causal). Returns (net, armed, fired)."""
    armed = False
    for j in range(i_fill, j_exit):
        b = rows[j]
        if not armed:
            armed = (b["h"] >= entry * (1 + arm)) if side > 0 else (b["l"] <= entry * (1 - arm))
        if armed:
            lo, hi = min(b["e5"], b["e12"]), max(b["e5"], b["e12"])
            if (side > 0 and b["c"] < lo) or (side < 0 and b["c"] > hi):
                ex = rows[j + 1]["o"]
                return side * (ex / entry - 1) - cost, True, True
    if not armed and j_exit < len(rows):
        b = rows[j_exit]
        armed = (b["h"] >= entry * (1 + arm)) if side > 0 else (b["l"] <= entry * (1 - arm))
    return base_net, armed, False


def _row_index(rows: list) -> dict:
    return {str(r["t"]): i for i, r in enumerate(rows)}


def lock_set(trades: pd.DataFrame, days_by: dict, fill_col: str = "t_in") -> pd.DataFrame:
    """trades need sym, day, side, entry, net, bars and t_in = fill bar time (batch 3/4 conventions)."""
    out = []
    idx_cache = {}
    for r in trades.itertuples(index=False):
        rows = days_by[r.sym].get(r.day)
        if not rows:
            continue
        key = (r.sym, r.day)
        if key not in idx_cache:
            idx_cache[key] = _row_index(rows)
        i = idx_cache[key].get(str(getattr(r, fill_col)))
        if i is None:
            continue
        j = min(i + int(r.bars) - 1, len(rows) - 1)
        rec = dict(sym=r.sym, day=r.day, side=int(r.side), net=float(r.net), shape=day_shape(rows),
                   t_in=str(getattr(r, fill_col)))
        for arm in ARMS:
            n, a, f = profit_lock(rows, i, j, int(r.side), float(r.entry), float(r.net), arm)
            rec[f"pl{arm}"], rec[f"armed{arm}"], rec[f"fired{arm}"] = n, a, f
        out.append(rec)
    return pd.DataFrame(out)


def paired_diff(t: pd.DataFrame, col: str, sessions: list) -> dict:
    if t.empty:
        return dict(n=0)
    t = t.assign(d=t[col] - t["net"])
    h1, h2 = halves(t, sessions)

    def m(x):
        return float(x["d"].mean() * 100) if len(x) else None
    days = sorted(t["day"].unique())
    return dict(n=int(len(t)), base=float(t["net"].mean() * 100), variant=float(t[col].mean() * 100), diff=m(t),
                ci=_boot_ratio([(*_day_sums(t, np.ones(len(t), bool), "d", days), 1)]),
                long=m(t[t.side > 0]), short=m(t[t.side < 0]), h1=m(h1), h2=m(h2))


def lock_report(t: pd.DataFrame, sessions: list) -> dict:
    res = {}
    for arm in ARMS:
        c = f"pl{arm}"
        res[str(arm)] = dict(armed=int(t[f"armed{arm}"].sum()) if len(t) else 0,
                             fired=int(t[f"fired{arm}"].sum()) if len(t) else 0, **paired_diff(t, c, sessions))
    if len(t):
        c = f"pl{ARMS[0]}"
        res["by_shape"] = {f"{'L' if s > 0 else 'S'}|{sh}": dict(n=int(len(g)), base=float(g["net"].mean() * 100),
                                                                   pl=float(g[c].mean() * 100))
                           for (s, sh), g in t.groupby(["side", "shape"])}
    return res


# ------------------------------------------------------------------ desk set for H14 (traded symbol, 5-min)
def desk5(arch1m: Path, s: str):
    b = load1m(arch1m, s)
    if b is None:
        return None
    d5 = add_features(to_5min(b[["o", "h", "l", "c", "v"]]))
    return by_day(d5)


def desk_lock_set(desk_csv: Path, arch1m: Path, desks: tuple) -> pd.DataFrame:
    t = pd.read_csv(desk_csv)
    t = t[t["desk"].isin(desks)]
    t["ets"] = pd.to_datetime(t["entry_t"], utc=True).dt.tz_convert("America/New_York")
    t["xts"] = pd.to_datetime(t["exit_t"], utc=True).dt.tz_convert("America/New_York")
    cache, icache = {}, {}
    out = []
    for _, r in t.iterrows():
        s = r["sym"]
        if s not in cache:
            cache[s] = desk5(arch1m, s)
        if INDEX[s] not in icache:
            icache[INDEX[s]] = desk5(arch1m, INDEX[s])
        days = cache[s]
        day = str(r["ets"].date())
        if not days or day not in days:
            continue
        rows = days[day]
        start = r["ets"].floor("5min") + pd.Timedelta(minutes=5)       # first full 5-min bar after the fill
        i = next((k for k, x in enumerate(rows) if pd.Timestamp(x["t"]) >= start), None)
        if i is None:
            continue
        base = float(r["move_pct"]) / 100
        slip = SLIP.get(s, 0.0005)
        entry = float(r["entry_px"])
        irows = (icache[INDEX[s]] or {}).get(day)
        rec = dict(desk=r["desk"], sym=s, day=day, side=-1 if s in INV else 1, net=base,
                   shape=day_shape(irows) if irows else None)
        for arm in ARMS:
            armed, fired, net = False, False, base
            for k in range(i, len(rows) - 1):
                b = rows[k]
                nxt = pd.Timestamp(rows[k + 1]["t"])
                if nxt >= r["xts"]:
                    break
                if not armed:
                    armed = b["h"] >= entry * (1 + arm)
                if armed and b["c"] < min(b["e5"], b["e12"]):
                    net = rows[k + 1]["o"] * (1 - slip) / entry - 1
                    fired = True
                    break
            rec[f"pl{arm}"], rec[f"armed{arm}"], rec[f"fired{arm}"] = net, armed, fired
        out.append(rec)
    return pd.DataFrame(out)


# ------------------------------------------------------------------ H15 CVD down-morning gate
def trade_time(rows: list, k: int, side: int, max_bars: int | None, stop_pct: float = STOP) -> dict | None:
    """Signal at bar k's close, fill at bar k+1's open; stop on ranges; exit at the close of the
    max_bars-th bar held (None = flat at 15:55)."""
    if k + 1 >= len(rows):
        return None
    entry = rows[k + 1]["o"]
    stop = entry * (1 - stop_pct * side)
    for j in range(k + 1, len(rows)):
        b = rows[j]
        ex = why = None
        if side > 0 and b["l"] <= stop:
            ex, why = min(b["o"], stop), "stop"
        elif side < 0 and b["h"] >= stop:
            ex, why = max(b["o"], stop), "stop"
        elif (max_bars and j - k >= max_bars) or b["mins"] >= EOD_MIN or j == len(rows) - 1:
            ex, why = b["c"], "time" if (max_bars and j - k >= max_bars) else "eod"
        if ex is not None:
            g = side * (ex / entry - 1)
            return dict(entry=entry, exit=ex, why=why, bars=j - k, gross=g, net=g - COST)
    return None


def from_open_at(rows: list, t) -> float | None:
    """Index close / 09:30 open − 1 at the bar starting at t (rows up to that bar only)."""
    for x in rows:
        if str(x["t"]) == str(t):
            return x["c"] / rows[0]["o"] - 1
    return None


def early_set(days_by: dict) -> pd.DataFrame:
    out = []
    q = days_by.get("QQQ", {})
    for s, days in days_by.items():
        for day, rows in days.items():
            qrows = q.get(day)
            for k, b in enumerate(rows):
                if not (EARLY[0] <= b["mins"] <= EARLY[1]):
                    continue
                fo_q = from_open_at(qrows, b["t"]) if qrows else None
                fo_own = b["c"] / rows[0]["o"] - 1
                if fo_q is None:
                    continue
                for side in (1, -1):
                    t30 = trade_time(rows, k, side, TIME_BARS)
                    teod = trade_time(rows, k, side, None)
                    if t30 is None or teod is None:
                        continue
                    g = (fo_q <= -GATE) if side > 0 else (fo_q >= GATE)
                    g_own = (fo_own <= -GATE) if side > 0 else (fo_own >= GATE)
                    out.append(dict(sym=s, day=day, side=side, mins=b["mins"], net=t30["net"], net_eod=teod["net"],
                                    gated=bool(g), gated_own=bool(g_own)))
    return pd.DataFrame(out)


def gate_diff(t: pd.DataFrame, flag: str, col: str = "net", boot: bool = True) -> dict:
    a, b = t[t[flag]], t[~t[flag]]
    res = dict(gated_n=int(len(a)), other_n=int(len(b)), gated_days=int(a["day"].nunique()) if len(a) else 0,
               gated=float(a[col].mean() * 100) if len(a) else None,
               other=float(b[col].mean() * 100) if len(b) else None)
    res["diff"] = (res["gated"] - res["other"]) if (len(a) and len(b)) else None
    if boot and len(a) >= 5 and len(b) >= 5:
        days = sorted(t["day"].unique())
        m = t[flag].values.astype(bool)
        res["ci"] = _boot_ratio([(*_day_sums(t, m, col, days), 1), (*_day_sums(t, ~m, col, days), -1)])
    return res


def gate_block(t: pd.DataFrame, flag: str, sessions: list, col: str = "net") -> dict:
    h1, h2 = halves(t, sessions)
    return {"pooled": gate_diff(t, flag, col), "long": gate_diff(t[t.side > 0], flag, col),
            "short": gate_diff(t[t.side < 0], flag, col),
            "h1": gate_diff(h1, flag, col, boot=False), "h2": gate_diff(h2, flag, col, boot=False)}


def cvd_desk_gate(desk_csv: Path, arch1m: Path) -> pd.DataFrame:
    t = pd.read_csv(desk_csv)
    t = t[t["desk"].isin(["cvd_spy", "cvd_tqqq"])]
    q = load1m(arch1m, "QQQ")
    out = []
    for _, r in t.iterrows():
        ets = pd.Timestamp(r["entry_t"]).tz_convert("America/New_York")
        sig = ets.floor("min") - pd.Timedelta(minutes=1)
        day = str(sig.date())
        g = q[(q["day"] == day) & (q.index <= sig)]
        if g.empty:
            continue
        fo = g["c"].iloc[-1] / g["o"].iloc[0] - 1
        mins = sig.hour * 60 + sig.minute
        out.append(dict(desk=r["desk"], day=day, side=1, net=float(r["move_pct"]) / 100, from_open_q=fo,
                        gated=bool(mins < GATE_END and fo <= -GATE), reason=r["reason"]))
    return pd.DataFrame(out)


# ------------------------------------------------------------------ H16 H13 delayed stop
def h13_delayed(rows: list, i_fill: int, side: int, entry: float, stop: float, cost: float = COST) -> dict:
    """Stop inactive for the first DELAY bars from the fill; a stop already breached at the close of the
    last inactive bar exits at that close. Flat at 15:55."""
    for j in range(i_fill, len(rows)):
        b = rows[j]
        ex = why = None
        if j >= i_fill + DELAY:
            if side > 0 and b["l"] <= stop:
                ex, why = min(b["o"], stop), "stop"
            elif side < 0 and b["h"] >= stop:
                ex, why = max(b["o"], stop), "stop"
        elif j == i_fill + DELAY - 1 and ((side > 0 and b["c"] <= stop) or (side < 0 and b["c"] >= stop)):
            ex, why = b["c"], "stop_late"
        if ex is None and (b["mins"] >= EOD_MIN or j == len(rows) - 1):
            ex, why = b["c"], "eod"
        if ex is not None:
            g = side * (ex / entry - 1)
            return dict(net=g - cost, why=why)
    return dict(net=None, why=None)


def h13_diag(h13: pd.DataFrame, days_by: dict, sessions: list) -> dict:
    if h13.empty:
        return {}
    recs = []
    for r in h13.itertuples(index=False):
        rows = days_by[r.sym][r.day]
        i = _row_index(rows)[str(r.t_in)]
        stop = (rows[0]["o"] + rows[i - 1]["c"]) / 2
        dl = h13_delayed(rows, i, int(r.side), float(r.entry), stop)
        recs.append(dict(day=r.day, sym=r.sym, side=int(r.side), net=float(r.net), why=r.why,
                         mins=int(r.mins_in), delayed=dl["net"], delayed_why=dl["why"]))
    t = pd.DataFrame(recs)
    early = t[t["mins"] < 11 * 60]
    late = t[t["mins"] >= 11 * 60]

    def s(x):
        return dict(n=int(len(x)), mean=float(x["net"].mean() * 100) if len(x) else None,
                    stops=int((x["why"] == "stop").sum()))
    return dict(early=s(early), late=s(late), delayed_stop=paired_diff(t.rename(columns={})[["day", "side", "net", "delayed"]]
                                                                         .assign(sym="x"), "delayed", sessions),
                rows=t.to_dict("records"))


# ------------------------------------------------------------------ H17 ORB first break
def orb_label(desk_csv: Path, arch1m: Path) -> pd.DataFrame:
    t = pd.read_csv(desk_csv)
    t = t[t["desk"].isin(["orb_vol", "orb_plain"])]
    cache, out = {}, []
    for _, r in t.iterrows():
        s = r["sym"]
        if s not in cache:
            cache[s] = load1m(arch1m, s)
        b = cache[s]
        ets = pd.Timestamp(r["entry_t"]).tz_convert("America/New_York")
        sig = ets.floor("min") - pd.Timedelta(minutes=1)
        day = str(sig.date())
        g = b[b["day"] == day]
        mins = g.index.hour * 60 + g.index.minute
        orh = g[(mins >= 9 * 60 + 30) & (mins < 9 * 60 + 45)]["h"].max()
        before = g[(mins >= 9 * 60 + 45) & (g.index < sig)]
        first = not bool((before["c"] > orh).any())
        out.append(dict(desk=r["desk"], sym=s, day=day, side=-1 if s in INV else 1, net=float(r["move_pct"]) / 100,
                        first=first, prior_closes_above=int((before["c"] > orh).sum())))
    return pd.DataFrame(out)


# ------------------------------------------------------------------ runner
def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive1m", required=True)
    ap.add_argument("--archive5m", required=True)
    ap.add_argument("--desk-trades")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    summary = {"prereg": "research/foundry/PREREG_batch5.md"}
    for tag, arch in (("A_1m", a.archive1m), ("B_5m", a.archive5m)):
        d_by, days_by, sessions, clipped = run_archive(Path(arch))
        res = {"sessions": len(sessions), "first": sessions[0], "last": sessions[-1], "clipped_bars": clipped}
        # H14
        rnd = random_set(days_by)
        rnd["t_in"] = rnd["t_in"].astype(str)
        lk = lock_set(rnd, days_by)
        lk.to_csv(out / f"h14_random_{tag}.csv.gz", index=False)
        res["H14_random"] = lock_report(lk, sessions)
        rl = []
        for sym, d in d_by.items():
            rl += sim3(d, sym, "H13", open1_signal())
            for name in ("ORB2_b10_w1100", "PD_HOLD"):
                rl += sim3(d, sym, name, B3[name]())
        rl = pd.DataFrame(rl)
        res["H14_rules"] = {}
        for name, g in rl.groupby("rule"):
            res["H14_rules"][name] = lock_report(lock_set(g, days_by), sessions)
        # H15
        es = early_set(days_by)
        es.to_csv(out / f"h15_early_{tag}.csv.gz", index=False)
        res["H15"] = {"primary_30min": gate_block(es, "gated", sessions),
                      "eod_exit": gate_block(es, "gated", sessions, col="net_eod"),
                      "own_index": gate_block(es, "gated_own", sessions)}
        # H16
        h13 = rl[rl["rule"] == "H13"]
        res["H16"] = h13_diag(h13, days_by, sessions)
        res["H13"] = stat3(h13, sessions)
        # H18
        b1 = []
        for sym, d in d_by.items():
            for r in R.RULES:
                b1 += R.simulate(d, r, sym)
        b1 = pd.DataFrame(b1)
        b1["day"] = b1["day"].astype(str)
        wk = b1["day"] >= "2026-11-09"
        res["H18"] = {k: {"n": int(len(g)), "long_n": int((g.side > 0).sum()),
                          "long": float(g[g.side > 0]["net"].mean() * 100) if (g.side > 0).any() else None,
                          "short_n": int((g.side < 0).sum()),
                          "short": float(g[g.side < 0]["net"].mean() * 100) if (g.side < 0).any() else None}
                      for k, g in (("before_nov9", b1[~wk]), ("nov9_13", b1[wk]))}
        summary[tag] = res
    if a.desk_trades and Path(a.desk_trades).exists():
        dk = desk_lock_set(Path(a.desk_trades), Path(a.archive1m), ("orb_vol", "ema_vol", "ema_vol_v2", "volspike"))
        dk.to_csv(out / "h14_desks.csv", index=False)
        sess = sorted(dk["day"].unique())
        summary["H14_desks"] = {"all": lock_report(dk, sess),
                                "by_desk": {k: lock_report(g, sess) for k, g in dk.groupby("desk")}}
        cg = cvd_desk_gate(Path(a.desk_trades), Path(a.archive1m))
        cg.to_csv(out / "h15_cvd_desks.csv", index=False)
        summary["H15_desks"] = {"all": gate_diff(cg, "gated"),
                                "by_desk": {k: gate_diff(g, "gated", boot=False) for k, g in cg.groupby("desk")}}
        ob = orb_label(Path(a.desk_trades), Path(a.archive1m))
        ob.to_csv(out / "h17_orb.csv", index=False)
        summary["H17"] = {k: dict(first_n=int(g["first"].sum()), first=float(g[g["first"]]["net"].mean() * 100) if g["first"].any() else None,
                                  recross_n=int((~g["first"]).sum()),
                                  recross=float(g[~g["first"]]["net"].mean() * 100) if (~g["first"]).any() else None)
                          for k, g in ob.groupby("desk")}
    (out / "summary.json").write_text(json.dumps(summary, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
