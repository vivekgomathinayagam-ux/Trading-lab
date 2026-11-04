"""Foundry batch 2 (pre-registered in research/foundry/PREREG_batch2.md).

H1 giveback trail (exit overlay), H2 trend-day gate at 10:30 ET, H3 reversal day, H4 entry-time buckets.
Research only: nothing here trades.

  python -m lab.foundry.batch2 --archive1m <dir> --archive5m <dir> --desk-trades <trades_1m.csv> --out <dir>
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from lab.foundry.rules import (COST, HARD_STOP, add_features, boot_ci, close_exit, entry_signal,
                               load_bars, random_control, to_5min)

LEV = {"SPY": 1, "QQQ": 1, "TQQQ": 3, "UPRO": 3, "SQQQ": 3, "SPXU": 3}
SLIP = {"SPY": 0.0002, "QQQ": 0.0002, "TQQQ": 0.0005, "UPRO": 0.0005, "SQQQ": 0.0005, "SPXU": 0.0005}
GB_ARM = 0.003
GB_KEEP = 0.5
WARMUP = 10


# ------------------------------------------------------------------ generic engine
def simulate2(d: pd.DataFrame, sym: str, rule: str, signal_fn, exit_fn=None, gb=False,
              cost=COST, max_per_day=3, window=(9 * 60 + 40, 15 * 60 + 25)):
    """One position at a time. signal_fn(rows, i, state) -> (side, stop, target) | None at a bar close,
    filled at the next bar's open. exit_fn(b, side, pos) -> reason | None fills at the bar close
    (batch-1 convention). GB fills at the next bar's open after the trigger close."""
    rows = d.reset_index().to_dict("records")
    n = len(rows)
    trades, state, count = [], {}, {}
    pos = pending = None
    gb_pending = False
    arm = GB_ARM * LEV.get(sym, 1)
    for i in range(n):
        b = rows[i]
        day = b["day"]
        new_day = i == 0 or rows[i - 1]["day"] != day
        if new_day:
            pending = None
        if pos is not None and gb_pending:
            ex = b["o"]
            trades.append(_trade(sym, rule, pos, b, i, ex, "gb", cost))
            pos, gb_pending = None, False
        if pending is not None and pos is None:
            side, stop, target = pending
            if stop is None:
                stop = b["o"] * (1 - HARD_STOP) if side > 0 else b["o"] * (1 + HARD_STOP)
            pos = dict(side=side, entry=b["o"], stop=stop, target=target, i=i, t=b["t"], day=day, best=0.0)
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
            if ex is None and exit_fn is not None:
                cx = exit_fn(b, side, pos)
                if cx:
                    ex, why = b["c"], cx
            last_bar = (i + 1 == n) or rows[i + 1]["day"] != day or b["mins"] >= 15 * 60 + 50
            if ex is None and last_bar:
                ex, why = b["c"], "eod"
            if ex is not None:
                trades.append(_trade(sym, rule, pos, b, i, ex, why, cost))
                pos = None
                continue
            fav = (b["h"] / pos["entry"] - 1) if side > 0 else (1 - b["l"] / pos["entry"])
            pos["best"] = max(pos["best"], fav)
            now = side * (b["c"] / pos["entry"] - 1)
            if gb and pos["best"] >= arm and now <= GB_KEEP * pos["best"]:
                gb_pending = True
        if pos is None and window[0] <= b["mins"] <= window[1] and count.get(day, 0) < max_per_day:
            sig = signal_fn(rows, i, state)
            if sig:
                pending = sig
    return trades


def _trade(sym, rule, pos, b, i, ex, why, cost):
    gross = pos["side"] * (ex / pos["entry"] - 1)
    return dict(sym=sym, rule=rule, day=str(pos["day"]), side=pos["side"], t_in=str(pos["t"]), t_out=str(b["t"]),
                entry=pos["entry"], exit=ex, why=why, bars=i - pos["i"] + 1, net=gross - cost, gross=gross,
                mins_in=pd.Timestamp(pos["t"]).hour * 60 + pd.Timestamp(pos["t"]).minute)


# ------------------------------------------------------------------ batch-1 rules as signal/exit fns
def b1_signal(rule, min_mins=None, allow=None):
    fib_used = {}

    def f(rows, i, state):
        if min_mins is not None and rows[i]["mins"] < min_mins:
            return None
        s = entry_signal(rule, rows, i, fib_used)
        if s is None:
            return None
        if allow is not None and not allow(rows[i], s[0]):
            return None
        return (s[0], s[1], s[2])
    return f


def b1_exit(rule):
    return lambda b, side, pos: close_exit(rule, b, side, pos)


# ------------------------------------------------------------------ H2 trend-day gate
def trend_days(d: pd.DataFrame) -> dict:
    """day -> dict(trend: bool, dir: ±1, warm: bool). Uses only bars 09:30-10:29 of that day
    and earlier days' first hours."""
    out, hist_r, hist_v = {}, [], []
    for day, g in d.groupby("day"):
        fh = g[(g["mins"] >= 570) & (g["mins"] < 630)]
        if len(fh) < 6:
            continue
        rng = (fh["h"].max() - fh["l"].min()) / fh["o"].iloc[0]
        vol = fh["v"].sum()
        last = fh.iloc[-1]
        early = fh[fh["mins"] <= 9 * 60 + 45]
        vw0 = early["vwap"].iloc[-1]
        dist = (last["c"] - last["vwap"]) / last["vwap"]
        direction = 1 if dist > 0 else -1
        slope = last["vwap"] - vw0
        warm = len(hist_r) >= WARMUP
        trend = False
        if warm:
            mr, mv = np.median(hist_r[-WARMUP:]), np.median(hist_v[-WARMUP:])
            trend = bool(rng >= 1.2 * mr and vol >= 1.0 * mv and np.sign(slope) == direction and abs(dist) >= 0.001)
        out[day] = dict(trend=trend, dir=direction, warm=warm, rng=rng, vol=vol, dist=dist)
        hist_r.append(rng)
        hist_v.append(vol)
    return out


def g3_signal(td, want_trend=True):
    def f(rows, i, state):
        b = rows[i]
        info = td.get(b["day"])
        if not info or not info["warm"] or info["trend"] != want_trend:
            return None
        if b["mins"] != 10 * 60 + 25 or state.get(("g3", b["day"])):
            return None
        state[("g3", b["day"])] = True
        return (info["dir"], None, None)
    return f


# ------------------------------------------------------------------ H3 reversal day
def r1_signal():
    def f(rows, i, state):
        b = rows[i]
        if not (11 * 60 <= b["mins"] < 14 * 60 + 30) or i == 0 or rows[i - 1]["day"] != b["day"]:
            return None
        p = rows[i - 1]
        hi, lo = b["s_hi"], b["s_lo"]
        if lo <= 0 or (hi - lo) / lo < 0.006:
            return None
        if b["hi_at"] > b["lo_at"] and b["c"] < b["vwap"] and p["c"] >= p["vwap"] and not state.get((b["day"], -1)):
            state[(b["day"], -1)] = True
            return (-1, hi, None)
        if b["lo_at"] > b["hi_at"] and b["c"] > b["vwap"] and p["c"] <= p["vwap"] and not state.get((b["day"], 1)):
            state[(b["day"], 1)] = True
            return (1, lo, None)
        return None
    return f


# ------------------------------------------------------------------ H1 random entries
def random_signal(d: pd.DataFrame, seed=21, per_day=2):
    rng = np.random.default_rng(seed)
    picks = {}
    for day, g in d.groupby("day"):
        ok = g[(g["mins"] >= 9 * 60 + 45) & (g["mins"] <= 15 * 60)]
        if len(ok) < per_day:
            continue
        ts = sorted(rng.choice(len(ok), size=per_day, replace=False))
        for k in ts:
            picks[ok.index[k]] = 1 if rng.random() < 0.5 else -1

    def f(rows, i, state):
        s = picks.get(rows[i]["t"])
        return (s, None, None) if s else None
    return f


# ------------------------------------------------------------------ H1 set 1: desk entries on 1-min bars
def desk_overlay(desk_trades: pd.DataFrame, bars1m: dict) -> pd.DataFrame:
    """Re-run each desk trade bar by bar; add the GB exit; keep the desk's own exit when it comes first."""
    out = []
    for _, t in desk_trades.iterrows():
        sym = t["sym"]
        if sym not in bars1m:
            continue
        b = bars1m[sym]
        t_in, t_out = pd.Timestamp(t["entry_t"]), pd.Timestamp(t["exit_t"])
        seg = b[(b.index >= t_in.floor("min")) & (b.index.date == t_in.date())]
        base = t["exit_px"] / t["entry_px"] - 1
        res, why, t_gb = base, t["reason"], None
        arm, best = GB_ARM * LEV[sym], 0.0
        idx = list(seg.index)
        for k, ts in enumerate(idx):
            if ts + pd.Timedelta(minutes=1) > t_out:   # this bar's close is at/after the desk's own exit
                break
            r = seg.loc[ts]
            best = max(best, r["h"] / t["entry_px"] - 1)
            now = r["c"] / t["entry_px"] - 1
            if best >= arm and now <= GB_KEEP * best and k + 1 < len(idx) and idx[k + 1] < t_out:
                px = seg.loc[idx[k + 1], "o"] * (1 - SLIP[sym])
                res, why, t_gb = px / t["entry_px"] - 1, "gb", idx[k + 1]
                break
        day = str(t_in.date())
        out.append(dict(desk=t["desk"], sym=sym, day=day, t_in=str(t_in), mins_in=t_in.hour * 60 + t_in.minute,
                        base=base, gb=res, diff=res - base, why=why, t_gb=str(t_gb) if t_gb is not None else ""))
    return pd.DataFrame(out)


# ------------------------------------------------------------------ stats helpers
def stat(t: pd.DataFrame, col="net", sessions=None) -> dict:
    if t.empty:
        return dict(trades=0)
    lo, hi = boot_ci(t, col)
    o = dict(trades=int(len(t)), exp_pct=round(100 * t[col].mean(), 4), ci=[round(100 * lo, 4), round(100 * hi, 4)],
             win=round(float((t[col] > 0).mean()), 3))
    w, l_ = t[t[col] > 0][col].sum(), -t[t[col] < 0][col].sum()
    o["pf"] = round(float(w / l_), 2) if l_ > 0 else None
    if sessions is not None:
        half = set(str(s) for s in sessions[: len(sessions) // 2])
        h1, h2 = t[t["day"].isin(half)], t[~t["day"].isin(half)]
        o["half1"] = round(100 * h1[col].mean(), 4) if len(h1) else None
        o["half2"] = round(100 * h2[col].mean(), 4) if len(h2) else None
        o["n1"], o["n2"] = int(len(h1)), int(len(h2))
    if "side" in t:
        for nm, sd in (("long", 1), ("short", -1)):
            s = t[t["side"] == sd]
            o[nm] = [int(len(s)), round(100 * s[col].mean(), 4) if len(s) else None]
    if col == "net":
        o["exp_2x"] = round(100 * (t["net"] - (t["gross"] - t["net"])).mean(), 4)
    return o


def buckets(t: pd.DataFrame, col: str) -> dict:
    out = {}
    for nm, lo, hi in (("pre1130", 0, 690), ("1130_1300", 690, 780), ("from1300", 780, 2000), ("from1130", 690, 2000)):
        s = t[(t["mins_in"] >= lo) & (t["mins_in"] < hi)]
        if s.empty:
            out[nm] = dict(trades=0)
            continue
        a, b = boot_ci(s, col)
        out[nm] = dict(trades=int(len(s)), exp_pct=round(100 * s[col].mean(), 4), ci=[round(100 * a, 4), round(100 * b, 4)])
    return out


# ------------------------------------------------------------------ run one 5-min archive
def run_archive(arch: Path, syms) -> tuple[pd.DataFrame, dict, list, dict]:
    all_tr, d_by, sess, gates = [], {}, set(), {}
    for s in syms:
        p = arch / f"{s}.csv.gz"
        if not p.exists():
            continue
        d = add_features(to_5min(load_bars(p)))
        d_by[s] = d
        sess |= set(d["day"].unique())
        td = trend_days(d)
        gates[s] = td
        warm_days = {k for k, v in td.items() if v["warm"]}
        on_dir = lambda b, side, td=td: td.get(b["day"], {}).get("trend") and td[b["day"]]["dir"] == side
        warm_ok = lambda b, side, w=warm_days: b["day"] in w
        for base_rule, tag in (("F1_cloud_ride", "G1"), ("F2_cloud_ride_tight", "G2")):
            all_tr += simulate2(d, s, tag, b1_signal(base_rule, 630, on_dir), b1_exit(base_rule))
            all_tr += simulate2(d, s, tag + "_ungated", b1_signal(base_rule, 630, warm_ok), b1_exit(base_rule))
        all_tr += simulate2(d, s, "G3", g3_signal(td, True))
        all_tr += simulate2(d, s, "G3x", g3_signal(td, False))
        all_tr += simulate2(d, s, "R1", r1_signal())
        # H1 set 2: F1/F3 with and without GB
        for r in ("F1_cloud_ride", "F3_vwap_trend"):
            all_tr += simulate2(d, s, r, b1_signal(r), b1_exit(r))
            all_tr += simulate2(d, s, r + "+GB", b1_signal(r), b1_exit(r), gb=True)
        # H1 set 3: random entries, hold vs GB
        all_tr += simulate2(d, s, "RND_hold", random_signal(d), max_per_day=2, window=(9 * 60 + 40, 15 * 60 + 5))
        all_tr += simulate2(d, s, "RND+GB", random_signal(d), gb=True, max_per_day=2, window=(9 * 60 + 40, 15 * 60 + 5))
    return pd.DataFrame(all_tr), d_by, sorted(sess), gates


def paired(tr: pd.DataFrame, a: str, b: str) -> dict:
    """Paired diff b - a on identical entries (same sym, t_in, side)."""
    k = ["sym", "t_in", "side"]
    x = tr[tr["rule"] == a].set_index(k)["net"]
    y = tr[tr["rule"] == b].set_index(k)["net"]
    j = pd.concat([x.rename("a"), y.rename("b")], axis=1, join="inner").reset_index()
    if j.empty:
        return dict(n=0)
    j["diff"] = j["b"] - j["a"]
    j["day"] = j["t_in"].str[:10]
    lo, hi = boot_ci(j, "diff")
    o = dict(n=int(len(j)), unmatched=int(max(len(x), len(y)) - len(j)), diff_pct=round(100 * j["diff"].mean(), 4),
             ci=[round(100 * lo, 4), round(100 * hi, 4)])
    for nm, sd in (("long", 1), ("short", -1)):
        s = j[j["side"] == sd]
        o[nm] = [int(len(s)), round(100 * s["diff"].mean(), 4) if len(s) else None]
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive1m", required=True)
    ap.add_argument("--archive5m", required=True)
    ap.add_argument("--desk-trades", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    outd = Path(a.out)
    outd.mkdir(parents=True, exist_ok=True)
    res = {}

    # H1 set 1
    bars1m = {s: load_bars(Path(a.archive1m) / f"{s}.csv.gz") for s in LEV if (Path(a.archive1m) / f"{s}.csv.gz").exists()}
    dt = pd.read_csv(a.desk_trades)
    dt = dt[dt["desk"].isin(["orb_vol", "ema_vol", "ema_vol_v2", "volspike", "cvd_spy", "cvd_tqqq"])]
    ov = desk_overlay(dt, bars1m)
    ov.to_csv(outd / "h1_desk_overlay.csv", index=False)
    sess1 = sorted(ov["day"].unique())
    half = set(sess1[: len(sess1) // 2])
    lo, hi = boot_ci(ov, "diff")
    res["H1_set1_desks"] = dict(
        trades=int(len(ov)), gb_fired=int((ov["why"] == "gb").sum()),
        base_pct=round(100 * ov["base"].mean(), 4), gb_pct=round(100 * ov["gb"].mean(), 4),
        diff_pct=round(100 * ov["diff"].mean(), 4), ci=[round(100 * lo, 4), round(100 * hi, 4)],
        half1=round(100 * ov[ov["day"].isin(half)]["diff"].mean(), 4),
        half2=round(100 * ov[~ov["day"].isin(half)]["diff"].mean(), 4),
        by_desk={k: [int(len(g)), round(100 * g["diff"].mean(), 4), int((g["why"] == "gb").sum())] for k, g in ov.groupby("desk")},
        time_buckets_base=buckets(ov, "base"),
    )

    for tag, arch in (("A_1m", a.archive1m), ("B_5m", a.archive5m)):
        tr, d_by, sess, gates = run_archive(Path(arch), ["SPY", "QQQ"])
        tr.to_csv(outd / f"trades_{tag}.csv", index=False)
        r = dict(sessions=len(sess), first=str(sess[0]), last=str(sess[-1]))
        r["trend_days"] = {s: [str(k) for k, v in g.items() if v["trend"]] for s, g in gates.items()}
        r["warm_days"] = {s: sum(v["warm"] for v in g.values()) for s, g in gates.items()}
        for rule in ("G1", "G1_ungated", "G2", "G2_ungated", "G3", "G3x", "R1", "F1_cloud_ride", "F1_cloud_ride+GB",
                     "F3_vwap_trend", "F3_vwap_trend+GB", "RND_hold", "RND+GB"):
            t = tr[tr["rule"] == rule] if not tr.empty else tr
            st = stat(t, "net", sess)
            if rule in ("G1", "G2", "G3", "R1") and len(t):
                st["rand95"] = round(100 * np.nanmean([random_control(d_by[s], t[t["sym"] == s]) for s in t["sym"].unique()]), 4)
            r[rule] = st
        r["paired_F1_GB"] = paired(tr, "F1_cloud_ride", "F1_cloud_ride+GB")
        r["paired_F3_GB"] = paired(tr, "F3_vwap_trend", "F3_vwap_trend+GB")
        r["paired_RND_GB"] = paired(tr, "RND_hold", "RND+GB")
        base_rules = tr[tr["rule"].isin(["F1_cloud_ride", "F3_vwap_trend", "G1_ungated", "G2_ungated", "R1"])]
        r["time_buckets_foundry"] = buckets(base_rules, "net")
        res[tag] = r

    (outd / "summary.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
