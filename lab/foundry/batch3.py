"""Foundry batch 3 (pre-registered in research/foundry/PREREG_batch3.md).

H5 two-sided opening-range break, H6 failed opening drive (+ continuation contrast),
H7 prior-day high/low hold / reject, H8 stale-high filter overlay. Research only: nothing here trades.

  python -m lab.foundry.batch3 --archive1m <dir> --archive5m <dir> [--desk-trades trades_1m.csv] --out <dir>
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from lab.foundry.rules import COST, add_features, load_bars, to_5min

SYMS = ["SPY", "QQQ"]
EOD_MIN = 15 * 60 + 50           # the 15:50 5-min bar's close = flat at 15:55
DROP_DAYS = {"2026-11-05", "2026-11-06"}


# ------------------------------------------------------------------ data
def clean_wicks(d: pd.DataFrame, lim: float) -> tuple[pd.DataFrame, int]:
    """Clip highs above max(o,c)*(1+lim) and lows below min(o,c)*(1-lim). Returns (bars, n clipped)."""
    d = d.copy()
    top = np.maximum(d["o"], d["c"]) * (1 + lim)
    bot = np.minimum(d["o"], d["c"]) * (1 - lim)
    n = int((d["h"] > top).sum() + (d["l"] < bot).sum())
    d["h"] = np.minimum(d["h"], top)
    d["l"] = np.maximum(d["l"], bot)
    return d, n


def prep(path: Path) -> tuple[pd.DataFrame, int]:
    raw = load_bars(path)
    one_min = len(raw) > 1 and (raw.index[1] - raw.index[0]) < pd.Timedelta(minutes=5)
    raw, n = clean_wicks(raw, 0.004 if one_min else 0.006)
    return add_features(to_5min(raw)), n


# ------------------------------------------------------------------ simulator
def simulate(d: pd.DataFrame, sym: str, rule: str, signal_fn, cost: float = COST) -> list[dict]:
    """Per day: signal_fn(bars, k, ctx) -> (side, stop) | None at bar k's close (bars = that day's rows
    up to and including k only), filled at bar k+1's open. One open position at a time. Stops are
    checked on each bar's range from the fill bar on; otherwise flat at the 15:50 bar's close."""
    out, prev = [], None
    for day, g in d.groupby("day", sort=True):
        rows = g.reset_index().to_dict("records")
        ctx = {"prev": prev, "done": set(), "sym": sym}
        pos = pending = None
        for k, b in enumerate(rows):
            if pending is not None and pos is None:
                side, stop = pending
                pos = dict(side=side, entry=b["o"], stop=stop, k=k, t=b["t"])
                pending = None
            if pos is not None:
                ex = why = None
                if pos["side"] > 0 and b["l"] <= pos["stop"]:
                    ex, why = min(b["o"], pos["stop"]), "stop"
                elif pos["side"] < 0 and b["h"] >= pos["stop"]:
                    ex, why = max(b["o"], pos["stop"]), "stop"
                elif b["mins"] >= EOD_MIN or k == len(rows) - 1:
                    ex, why = b["c"], "eod"
                if ex is not None:
                    gross = pos["side"] * (ex / pos["entry"] - 1)
                    out.append(dict(sym=sym, rule=rule, day=str(day), side=pos["side"], t_in=str(pos["t"]),
                                    t_out=str(b["t"]), entry=pos["entry"], exit=ex, why=why,
                                    bars=k - pos["k"] + 1, gross=gross, net=gross - cost,
                                    mins_in=pd.Timestamp(pos["t"]).hour * 60 + pd.Timestamp(pos["t"]).minute))
                    pos = None
                    continue
            if pos is None and pending is None and b["mins"] < EOD_MIN - 5:
                sig = signal_fn(rows[: k + 1], k, ctx)
                if sig is not None:
                    pending = sig
        prev = dict(h=g["h"].max(), l=g["l"].min(), c=g["c"].iloc[-1])
    return out


# ------------------------------------------------------------------ H5 ORB2
def orb2_signal(buf: float, last_entry_min: int):
    def f(bars, k, ctx):
        b = bars[k]
        if b["mins"] < 9 * 60 + 45 or b["mins"] >= last_entry_min:
            return None
        orb = [x for x in bars if x["mins"] < 9 * 60 + 45]
        if len(orb) < 3:
            return None
        hi, lo = max(x["h"] for x in orb), min(x["l"] for x in orb)
        c = b["c"]
        if "L" not in ctx["done"] and c > hi * (1 + buf):
            ctx["done"].add("L")
            return (1, max(lo, c * 0.99))
        if "S" not in ctx["done"] and c < lo * (1 - buf):
            ctx["done"].add("S")
            return (-1, min(hi, c * 1.01))
        return None
    return f


# ------------------------------------------------------------------ H6 opening drive
DRIVE = {"primary": {"SPY": 0.005, "QQQ": 0.007}, "coach": {"SPY": 0.009, "QQQ": 0.013}}


def drive_of(bars) -> float | None:
    d = [x for x in bars if x["mins"] <= 9 * 60 + 50]
    if not d or d[-1]["mins"] != 9 * 60 + 50:
        return None
    return d[-1]["c"] / d[0]["o"] - 1


def fod_signal(level: str):
    def f(bars, k, ctx):
        b = bars[k]
        if b["mins"] < 9 * 60 + 55 or b["mins"] >= 12 * 60 or ctx["done"]:
            return None
        dr = drive_of(bars)
        if dr is None or abs(dr) < DRIVE[level][ctx["sym"]]:
            return None
        o = bars[0]["o"]
        if dr > 0:
            ext = max(x["h"] for x in bars)
            if b["c"] < (o + ext) / 2:
                ctx["done"].add(1)
                return (-1, ext)
        else:
            ext = min(x["l"] for x in bars)
            if b["c"] > (o + ext) / 2:
                ctx["done"].add(1)
                return (1, ext)
        return None
    return f


def cont_signal(level: str):
    def f(bars, k, ctx):
        b = bars[k]
        if b["mins"] != 9 * 60 + 50 or ctx["done"]:
            return None
        dr = drive_of(bars)
        if dr is None or abs(dr) < DRIVE[level][ctx["sym"]]:
            return None
        ctx["done"].add(1)
        return (1 if dr > 0 else -1, bars[0]["o"])
    return f


# ------------------------------------------------------------------ H7 prior-day levels
def pd_hold_signal():
    def f(bars, k, ctx):
        b, p = bars[k], ctx["prev"]
        if p is None or k < 1 or not (9 * 60 + 45 <= b["mins"] < 13 * 60):
            return None
        a = bars[k - 1]
        if "L" not in ctx["done"] and b["c"] > p["h"] and a["c"] > p["h"] and not any(x["c"] > p["h"] for x in bars[: k - 1]):
            ctx["done"].add("L")
            return (1, p["h"] * (1 - 0.003))
        if "S" not in ctx["done"] and b["c"] < p["l"] and a["c"] < p["l"] and not any(x["c"] < p["l"] for x in bars[: k - 1]):
            ctx["done"].add("S")
            return (-1, p["l"] * (1 + 0.003))
        return None
    return f


def pd_reject_signal():
    def f(bars, k, ctx):
        b, p = bars[k], ctx["prev"]
        if p is None or not (9 * 60 + 45 <= b["mins"] < 13 * 60):
            return None
        recent = bars[max(0, k - 3): k]
        if "S" not in ctx["done"] and b["c"] < p["h"] and any(x["h"] > p["h"] for x in recent + [b]):
            ctx["done"].add("S")
            return (-1, max(x["h"] for x in bars))
        if "L" not in ctx["done"] and b["c"] > p["l"] and any(x["l"] < p["l"] for x in recent + [b]):
            ctx["done"].add("L")
            return (1, min(x["l"] for x in bars))
        return None
    return f


# ------------------------------------------------------------------ random entries (control set + H8)
def random_signal(seed: int, per_day: int = 2):
    rng = np.random.default_rng(seed)
    pick = {}

    def f(bars, k, ctx):
        day = str(bars[0]["day"])
        if day not in pick:
            cand = list(range(9 * 60 + 45, 15 * 60 + 5, 5))
            pick[day] = {int(m): int(rng.choice([1, -1])) for m in rng.choice(cand, size=per_day, replace=False)}
        b = bars[k]
        s = pick[day].get(int(b["mins"]))
        if s is None:
            return None
        ctx.setdefault("stale", {})[str(b["t"])] = stale_flag(bars, k, s)
        return (s, b["c"] * (1 - 0.005 * s))
    return f


def stale_flag(bars, k, side: int, min_age: int = 15) -> bool:
    """Long: session high made min_age+ minutes before this bar's close and close < VWAP. Short mirror."""
    b = bars[k]
    end = b["mins"] + 5
    if side > 0:
        hi = max(x["h"] for x in bars)
        at = max(x["mins"] for x in bars if x["h"] == hi) + 5
        return (end - at) >= min_age and b["c"] < b["vwap"]
    lo = min(x["l"] for x in bars)
    at = max(x["mins"] for x in bars if x["l"] == lo) + 5
    return (end - at) >= min_age and b["c"] > b["vwap"]


# ------------------------------------------------------------------ stats
def boot(vals_by_day: dict, n: int = 2000, seed: int = 7):
    days = list(vals_by_day)
    if len(days) < 2:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    ms = []
    for _ in range(n):
        v = np.concatenate([vals_by_day[days[j]] for j in rng.integers(0, len(days), len(days))])
        ms.append(v.mean() if len(v) else np.nan)
    return tuple(float(x) for x in np.nanpercentile(ms, [2.5, 97.5]))


def stat(t: pd.DataFrame, sessions: list, col: str = "net") -> dict:
    if t.empty:
        return dict(n=0)
    by = {d: g[col].values for d, g in t.groupby("day")}
    half = set(sessions[: len(sessions) // 2])
    h1, h2 = t[t["day"].isin(half)], t[~t["day"].isin(half)]
    lo, hi = boot(by)
    pos = t[t["gross"] > 0]["gross"].sum()
    neg = -t[t["gross"] <= 0]["gross"].sum()
    rest = t[~t["day"].isin(DROP_DAYS)]
    return dict(n=int(len(t)), days=int(t["day"].nunique()), mean=float(t[col].mean() * 100),
                ci=[lo * 100, hi * 100], win=float((t[col] > 0).mean()),
                mean_2x=float((t["gross"] - 2 * COST).mean() * 100),
                h1=float(h1[col].mean() * 100) if len(h1) else None, h2=float(h2[col].mean() * 100) if len(h2) else None,
                long_n=int((t["side"] > 0).sum()), long=float(t[t["side"] > 0][col].mean() * 100) if (t["side"] > 0).any() else None,
                short_n=int((t["side"] < 0).sum()), short=float(t[t["side"] < 0][col].mean() * 100) if (t["side"] < 0).any() else None,
                ex_nov56=float(rest[col].mean() * 100) if len(rest) else None,
                pf_gross=float(pos / neg) if neg > 0 else None,
                stops=int((t["why"] == "stop").sum()))


def random_p95(d_by_sym: dict, t: pd.DataFrame, draws: int = 500, seed: int = 11) -> float:
    if t.empty:
        return float("nan")
    rng = np.random.default_rng(seed)
    arr = {}
    for s, d in d_by_sym.items():
        ok = np.where((d["mins"].values >= 9 * 60 + 45) & (d["mins"].values <= 15 * 60 + 30))[0]
        arr[s] = (d["o"].values, d["c"].values, d["day"].values, ok)
    means = []
    for _ in range(draws):
        vals = []
        for _, r in t.iterrows():
            o, c, days, ok = arr[r["sym"]]
            for _try in range(20):
                k = int(rng.choice(ok))
                j = k + int(r["bars"]) - 1
                if j < len(c) and days[j] == days[k]:
                    vals.append(r["side"] * (c[j] / o[k] - 1) - COST)
                    break
        means.append(np.mean(vals))
    return float(np.percentile(means, 95) * 100)


# ------------------------------------------------------------------ runner
CANDIDATES = {
    "ORB2_b10_w1100": lambda: orb2_signal(0.001, 11 * 60),
    "ORB2_b10_w1130": lambda: orb2_signal(0.001, 11 * 60 + 30),
    "ORB2_b10_all": lambda: orb2_signal(0.001, 15 * 60 + 25),
    "ORB2_b30_w1100": lambda: orb2_signal(0.003, 11 * 60),
    "ORB2_b30_w1130": lambda: orb2_signal(0.003, 11 * 60 + 30),
    "ORB2_b30_all": lambda: orb2_signal(0.003, 15 * 60 + 25),
    "FOD_primary": lambda: fod_signal("primary"),
    "FOD_coach": lambda: fod_signal("coach"),
    "CONT_primary": lambda: cont_signal("primary"),
    "CONT_coach": lambda: cont_signal("coach"),
    "PD_HOLD": pd_hold_signal,
    "PD_REJ": pd_reject_signal,
}
PRIMARY = ["ORB2_b10_w1100", "FOD_primary", "PD_HOLD", "PD_REJ"]


def run_archive(arch: Path) -> tuple[pd.DataFrame, dict, list, int]:
    d_by, clipped = {}, 0
    for s in SYMS:
        d, n = prep(Path(arch) / f"{s}.csv.gz")
        d_by[s], clipped = d, clipped + n
    tr = []
    for s, d in d_by.items():
        for name, mk in CANDIDATES.items():
            tr += simulate(d, s, name, mk())
    sessions = sorted(set().union(*[set(map(str, d["day"].unique())) for d in d_by.values()]))
    return pd.DataFrame(tr), d_by, sessions, clipped


def drive_days(d_by: dict) -> dict:
    out = {}
    for s, d in d_by.items():
        for day, g in d.groupby("day"):
            rows = g.reset_index().to_dict("records")
            dr = drive_of(rows)
            if dr is None:
                continue
            closes = (g["c"].iloc[-1] / rows[0]["o"] - 1)
            imp = max(abs(x["c"] / rows[0]["o"] - 1) for x in rows if x["mins"] < 10 * 60 + 15)
            out.setdefault(s, []).append(dict(day=str(day), drive=dr, day_ret=closes, impulse45=imp))
    return out


def random_set(d_by: dict, seed: int = 21) -> pd.DataFrame:
    rows = []
    for s, d in d_by.items():
        fn = random_signal(seed + hash(s) % 97)
        holder = {}

        def wrapped(bars, k, ctx, fn=fn, holder=holder):
            r = fn(bars, k, ctx)
            holder.update(ctx.get("stale", {}))
            return r
        tr = simulate(d, s, "RAND", wrapped)
        # the stale flag is keyed by the signal bar; the entry is the next bar
        sig_times = sorted(holder)
        for t in tr:
            prior = [x for x in sig_times if x < t["t_in"]]
            t["stale"] = holder[prior[-1]] if prior else False
        rows += tr
    return pd.DataFrame(rows)


def desk_overlay(desk_csv: Path, arch1m: Path) -> pd.DataFrame:
    """Stale flag on each floor-lab desk backtest entry, from the 1-min bars of the traded symbol
    up to the signal bar (the minute before the fill)."""
    t = pd.read_csv(desk_csv)
    t["entry_ts"] = pd.to_datetime(t["entry_t"], utc=True).dt.tz_convert("America/New_York")
    out = []
    cache = {}
    for _, r in t.iterrows():
        s = r["sym"]
        if s not in cache:
            p = Path(arch1m) / f"{s}.csv.gz"
            if not p.exists():
                continue
            b, _ = clean_wicks(load_bars(p), 0.004)
            day = pd.Series(b.index.date, index=b.index)
            tp = (b["h"] + b["l"] + b["c"]) / 3
            b["vwap"] = (tp * b["v"]).groupby(day).cumsum() / b["v"].groupby(day).cumsum()
            b["day"] = day
            cache[s] = b
        b = cache[s]
        sig_t = r["entry_ts"].floor("min") - pd.Timedelta(minutes=1)
        g = b[(b["day"] == sig_t.date()) & (b.index <= sig_t)]
        if g.empty:
            continue
        hi = g["h"].max()
        at = g.index[g["h"] == hi][-1]
        age = (sig_t - at).total_seconds() / 60
        stale = bool(age >= 15 and g["c"].iloc[-1] < g["vwap"].iloc[-1])
        out.append(dict(desk=r["desk"], sym=s, day=str(sig_t.date()), entry_t=str(r["entry_ts"]),
                        stale=stale, pnl=float(r["pnl_pct_equity"])))
    return pd.DataFrame(out)


def stale_cmp(t: pd.DataFrame, col: str, side=None) -> dict:
    if side is not None:
        t = t[t["side"] == side]
    a, b = t[t["stale"]], t[~t["stale"]]
    res = dict(stale_n=int(len(a)), fresh_n=int(len(b)),
               stale=float(a[col].mean()) if len(a) else None, fresh=float(b[col].mean()) if len(b) else None)
    if len(a) >= 2 and len(b) >= 2:
        days = sorted(t["day"].unique())
        rng = np.random.default_rng(5)
        diffs = []
        for _ in range(2000):
            pick = set()
            sel = [days[j] for j in rng.integers(0, len(days), len(days))]
            aa = np.concatenate([a[a["day"] == x][col].values for x in sel]) if sel else np.array([])
            bb = np.concatenate([b[b["day"] == x][col].values for x in sel]) if sel else np.array([])
            if len(aa) and len(bb):
                diffs.append(aa.mean() - bb.mean())
        res["diff_ci"] = [float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))]
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive1m", required=True)
    ap.add_argument("--archive5m", required=True)
    ap.add_argument("--desk-trades")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    summary = {"prereg": "research/foundry/PREREG_batch3.md"}
    for tag, arch in (("A_1m", a.archive1m), ("B_5m", a.archive5m)):
        tr, d_by, sessions, clipped = run_archive(Path(arch))
        tr.to_csv(out / f"trades_{tag}.csv", index=False)
        res = {"sessions": len(sessions), "first": sessions[0], "last": sessions[-1], "clipped_bars": clipped,
               "rules": {}}
        for name in CANDIDATES:
            t = tr[tr["rule"] == name] if not tr.empty else tr
            st = stat(t, sessions)
            if name in PRIMARY or name.startswith("ORB2"):
                st["rand_p95"] = random_p95(d_by, t)
            res["rules"][name] = st
        dd = drive_days(d_by)
        res["drive_days"] = {s: dict(primary=sum(abs(x["drive"]) >= DRIVE["primary"][s] for x in v),
                                     coach=sum(abs(x["drive"]) >= DRIVE["coach"][s] for x in v),
                                     primary_continued=sum(abs(x["drive"]) >= DRIVE["primary"][s] and np.sign(x["day_ret"]) == np.sign(x["drive"]) for x in v),
                                     impulse_1p5_45min=sum(x["impulse45"] >= 0.015 for x in v),
                                     list=[x for x in v if abs(x["drive"]) >= DRIVE["primary"][s]])
                             for s, v in dd.items()}
        rnd = random_set(d_by)
        rnd.to_csv(out / f"random_{tag}.csv", index=False)
        res["H8_random"] = {"long": stale_cmp(rnd, "net", 1), "short": stale_cmp(rnd, "net", -1),
                            "all_mean": float(rnd["net"].mean() * 100)}
        summary[tag] = res
    if a.desk_trades and Path(a.desk_trades).exists():
        ov = desk_overlay(Path(a.desk_trades), Path(a.archive1m))
        ov.to_csv(out / "h8_desk_overlay.csv", index=False)
        ov["side"] = 1
        summary["H8_desks"] = {"all": stale_cmp(ov, "pnl"),
                               "by_desk": {k: stale_cmp(g, "pnl") for k, g in ov.groupby("desk")}}
    (out / "summary.json").write_text(json.dumps(summary, indent=1, default=str))
    print(json.dumps({k: (v if k.startswith("H8_d") else None) for k, v in summary.items()}, default=str)[:200])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
