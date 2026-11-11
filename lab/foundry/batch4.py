"""Foundry batch 4 (pre-registered in research/foundry/PREREG_batch4.md).

H9 distance-from-extreme filter, H10 1%-from-open filter, H11 fail-fast exit, H12 exits by day shape.
Research only: nothing here trades.

  python -m lab.foundry.batch4 --archive1m <dir> --archive5m <dir> [--desk-trades trades_1m.csv] --out <dir>
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from lab.foundry import rules as R
from lab.foundry.batch3 import CANDIDATES as B3, clean_wicks, prep, random_p95, simulate as sim3, stat as stat3
from lab.foundry.rules import COST, load_bars

SYMS = ["SPY", "QQQ"]
EOD_MIN = 15 * 60 + 50
SEEDS = list(range(21, 29))
PER_DAY = 3
STOP = 0.005
THR = [0.003, 0.005, 0.0075]
OPEN_THR = 0.01
FF_BARS = 3          # 15 minutes of 5-min bars, counting the fill bar
FF_MFE = 0.001
LEV = {"SPY": 1, "QQQ": 1, "UPRO": 3, "TQQQ": 3, "SPXU": 3, "SQQQ": 3}
INDEX = {"SPY": "SPY", "UPRO": "SPY", "SPXU": "SPY", "QQQ": "QQQ", "TQQQ": "QQQ", "SQQQ": "QQQ"}
INV = {"SPXU", "SQQQ"}
SLIP = {"SPY": 0.0002, "QQQ": 0.0002}


# ------------------------------------------------------------------ features (signal bar only)
def features(day_rows: list, k: int, side: int) -> dict:
    """Uses rows[0..k] only."""
    seen = day_rows[: k + 1]
    c = seen[-1]["c"]
    hi = max(x["h"] for x in seen)
    lo = min(x["l"] for x in seen)
    o = seen[0]["o"]
    dist = (1 - c / hi) if side > 0 else (c / lo - 1)
    from_open = c / o - 1
    stretched = (from_open <= -OPEN_THR) if side > 0 else (from_open >= OPEN_THR)
    return dict(dist=dist, from_open=from_open, stretched=bool(stretched))


# ------------------------------------------------------------------ independent trade from a signal bar
def trade_from(day_rows: list, k: int, side: int, stop_pct: float = STOP) -> dict | None:
    """Signal at bar k's close, fill at bar k+1's open; stop on bar ranges; flat at 15:55."""
    if k + 1 >= len(day_rows):
        return None
    f = day_rows[k + 1]
    entry = f["o"]
    stop = entry * (1 - stop_pct * side)
    for j in range(k + 1, len(day_rows)):
        b = day_rows[j]
        ex = why = None
        if side > 0 and b["l"] <= stop:
            ex, why = min(b["o"], stop), "stop"
        elif side < 0 and b["h"] >= stop:
            ex, why = max(b["o"], stop), "stop"
        elif b["mins"] >= EOD_MIN or j == len(day_rows) - 1:
            ex, why = b["c"], "eod"
        if ex is not None:
            g = side * (ex / entry - 1)
            return dict(t_in=str(f["t"]), t_out=str(b["t"]), entry=entry, exit=ex, why=why,
                        bars=j - k, gross=g, net=g - COST)
    return None


def fail_fast(day_rows: list, i_fill: int, side: int, entry: float, bars: int, base_net: float) -> tuple[float, bool]:
    """Paired fail-fast variant of a trade filled at row i_fill and held `bars` bars (fill bar = 1).
    At the close of the FF_BARS-th bar, exit if the best favorable excursion never reached FF_MFE."""
    if bars <= FF_BARS:
        return base_net, False
    win = day_rows[i_fill: i_fill + FF_BARS]
    if len(win) < FF_BARS:
        return base_net, False
    mfe = (max(x["h"] for x in win) / entry - 1) if side > 0 else (1 - min(x["l"] for x in win) / entry)
    if mfe >= FF_MFE:
        return base_net, False
    ex = win[-1]["c"]
    return side * (ex / entry - 1) - COST, True


# ------------------------------------------------------------------ data helpers
def by_day(d: pd.DataFrame) -> dict:
    return {str(day): g.reset_index().to_dict("records") for day, g in d.groupby("day", sort=True)}


def day_shape(rows: list) -> str:
    o, c = rows[0]["o"], rows[-1]["c"]
    hi, lo = max(x["h"] for x in rows), min(x["l"] for x in rows)
    r = c / o - 1
    if r >= 0.004:
        return "up"
    if r <= -0.004:
        return "down"
    return "V" if (hi - lo) / o >= 0.008 else "chop"


def random_set(days_by_sym: dict) -> pd.DataFrame:
    out = []
    for s, days in days_by_sym.items():
        for seed in SEEDS:
            rng = np.random.default_rng(seed * 1000 + (1 if s == "SPY" else 2))
            for day, rows in days.items():
                ok = [k for k, b in enumerate(rows) if 9 * 60 + 45 <= b["mins"] <= 15 * 60 + 5]
                if len(ok) < PER_DAY:
                    continue
                for k in sorted(rng.choice(ok, size=PER_DAY, replace=False)):
                    side = int(rng.choice([1, -1]))
                    t = trade_from(rows, int(k), side)
                    if t is None:
                        continue
                    ff, hit = fail_fast(rows, int(k) + 1, side, t["entry"], t["bars"], t["net"])
                    out.append(dict(sym=s, seed=seed, day=day, side=side, **t, **features(rows, int(k), side),
                                    ff_net=ff, ff_hit=hit))
    return pd.DataFrame(out)


def rule_set(d_by: dict, days_by_sym: dict) -> pd.DataFrame:
    """Batch 1-3 rule entries, with the paired fail-fast variant."""
    tr = []
    for s, d in d_by.items():
        for r in R.RULES:
            tr += R.simulate(d, r, s)
        for name in ("ORB2_b10_w1100", "PD_HOLD", "PD_REJ"):
            tr += sim3(d, s, name, B3[name]())
    out = []
    for t in tr:
        rows = days_by_sym[t["sym"]][t["day"]]
        idx = {str(b["t"]): i for i, b in enumerate(rows)}
        i = idx.get(t["t_in"])
        if i is None:
            continue
        ff, hit = fail_fast(rows, i, t["side"], t["entry"], t["bars"], t["net"])
        out.append(dict(sym=t["sym"], rule=t["rule"], day=t["day"], side=t["side"], net=t["net"], gross=t["gross"],
                        bars=t["bars"], ff_net=ff, ff_hit=hit, shape=day_shape(rows)))
    return pd.DataFrame(out)


# ------------------------------------------------------------------ stats
def _day_sums(t: pd.DataFrame, mask: np.ndarray, col: str, days: list):
    g = pd.DataFrame({"day": t["day"].values, "v": t[col].values * mask, "n": mask.astype(float)})
    a = g.groupby("day")[["v", "n"]].sum().reindex(days, fill_value=0.0)
    return a["v"].values, a["n"].values


def _boot_ratio(parts, n=2000, seed=7):
    """parts: list of (sum_by_day, count_by_day, sign). Statistic = sum(sign * mean_i)."""
    k = len(parts[0][0])
    if k < 3:
        return [None, None]
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, k, size=(n, k))
    stat = np.zeros(n)
    for sv, cv, sg in parts:
        num, den = sv[idx].sum(1), cv[idx].sum(1)
        with np.errstate(invalid="ignore", divide="ignore"):
            stat += sg * num / den
    stat = stat[np.isfinite(stat)]
    if not len(stat):
        return [None, None]
    return [float(np.percentile(stat, 2.5) * 100), float(np.percentile(stat, 97.5) * 100)]


def split_diff(t: pd.DataFrame, flag: str, col: str = "net", boot: bool = True) -> dict:
    """far(flag) − near mean, % per trade."""
    a, b = t[t[flag]], t[~t[flag]]
    res = dict(far_n=int(len(a)), near_n=int(len(b)),
               far=float(a[col].mean() * 100) if len(a) else None, near=float(b[col].mean() * 100) if len(b) else None)
    res["diff"] = (res["far"] - res["near"]) if (len(a) and len(b)) else None
    if boot and len(a) >= 5 and len(b) >= 5:
        days = sorted(t["day"].unique())
        m = t[flag].values.astype(bool)
        res["ci"] = _boot_ratio([(*_day_sums(t, m, col, days), 1), (*_day_sums(t, ~m, col, days), -1)])
    return res


def halves(t: pd.DataFrame, sessions: list) -> tuple[pd.DataFrame, pd.DataFrame]:
    h = set(sessions[: len(sessions) // 2])
    return t[t["day"].isin(h)], t[~t["day"].isin(h)]


def filter_block(rnd: pd.DataFrame, flag: str, sessions: list) -> dict:
    h1, h2 = halves(rnd, sessions)
    out = {"pooled": split_diff(rnd, flag), "long": split_diff(rnd[rnd.side > 0], flag),
           "short": split_diff(rnd[rnd.side < 0], flag),
           "h1": split_diff(h1, flag, boot=False), "h2": split_diff(h2, flag, boot=False)}
    return out


def paired(t: pd.DataFrame, sessions: list) -> dict:
    t = t.assign(d=t["ff_net"] - t["net"])
    h1, h2 = halves(t, sessions)

    def m(x):
        return float(x["d"].mean() * 100) if len(x) else None
    return dict(n=int(len(t)), hit=int(t["ff_hit"].sum()), base=float(t["net"].mean() * 100),
                ff=float(t["ff_net"].mean() * 100), diff=m(t),
                ci=_boot_ratio([(*_day_sums(t, np.ones(len(t), bool), "d", sorted(t["day"].unique())), 1)]),
                long=m(t[t.side > 0]), short=m(t[t.side < 0]), h1=m(h1), h2=m(h2))


# ------------------------------------------------------------------ desk set (1-min)
def load1m(arch: Path, s: str) -> pd.DataFrame | None:
    p = Path(arch) / f"{s}.csv.gz"
    if not p.exists():
        return None
    b, _ = clean_wicks(load_bars(p), 0.004 * LEV.get(s, 1))
    b["day"] = pd.Series(b.index.date, index=b.index).astype(str)
    tp = (b["h"] + b["l"] + b["c"]) / 3
    b["vwap"] = (tp * b["v"]).groupby(b["day"]).cumsum() / b["v"].groupby(b["day"]).cumsum()
    return b


def desk_set(desk_csv: Path, arch1m: Path) -> pd.DataFrame:
    t = pd.read_csv(desk_csv)
    t["ets"] = pd.to_datetime(t["entry_t"], utc=True).dt.tz_convert("America/New_York")
    t["xts"] = pd.to_datetime(t["exit_t"], utc=True).dt.tz_convert("America/New_York")
    cache = {}

    def bars(s):
        if s not in cache:
            cache[s] = load1m(arch1m, s)
        return cache[s]
    out = []
    for _, r in t.iterrows():
        s, ix = r["sym"], INDEX.get(r["sym"])
        tb, ib = bars(s), bars(ix) if ix else None
        if tb is None or ib is None:
            continue
        sig = r["ets"].floor("min") - pd.Timedelta(minutes=1)
        day = str(sig.date())
        g = ib[(ib["day"] == day) & (ib.index <= sig)]
        if g.empty:
            continue
        iside = -1 if s in INV else 1
        c, hi, lo, o = g["c"].iloc[-1], g["h"].max(), g["l"].min(), g["o"].iloc[0]
        dist = (1 - c / hi) if iside > 0 else (c / lo - 1)
        fo = c / o - 1
        stretched = (fo <= -OPEN_THR) if iside > 0 else (fo >= OPEN_THR)
        base = float(r["move_pct"]) / 100
        slip = SLIP.get(s, 0.0005)
        lev = LEV.get(s, 1)
        after = tb[(tb["day"] == day) & (tb.index >= r["ets"].floor("min"))]
        ff, hit = base, False
        held = (r["xts"] - r["ets"]).total_seconds() / 60
        w = after.iloc[:15]
        if held > 15 and len(w) == 15:
            mfe = w["h"].max() / r["entry_px"] - 1
            if mfe < FF_MFE * lev:
                ff, hit = w["c"].iloc[-1] * (1 - slip) / r["entry_px"] - 1, True
        # H12 alternatives for CVD desks: hold to 15:55, first close below VWAP
        eod = after[after.index.hour * 60 + after.index.minute <= 15 * 60 + 55]
        hold = eod["c"].iloc[-1] * (1 - slip) / r["entry_px"] - 1 if len(eod) else None
        below = after[after["c"] < after["vwap"]]
        below = below[below.index <= (eod.index[-1] if len(eod) else below.index.max())]
        vw = (below["c"].iloc[0] * (1 - slip) / r["entry_px"] - 1) if len(below) else hold
        irows = ib[ib["day"] == day].reset_index().rename(columns={"index": "t"}).to_dict("records")
        out.append(dict(desk=r["desk"], sym=s, day=day, side=iside, net=base, dist=dist, from_open=fo,
                        stretched=bool(stretched), ff_net=ff, ff_hit=hit, hold=hold, vwap_exit=vw,
                        shape=day_shape(irows) if irows else None, reason=r["reason"]))
    return pd.DataFrame(out)


# ------------------------------------------------------------------ H13 1%-from-open continuation
def open1_signal(thr: float = OPEN_THR, last_min: int = 14 * 60):
    """First 5-min close 09:45-14:00 at >= thr from the 09:30 open: trade with it. Stop at the midpoint of
    the open and the signal close (the fill is the next open; the close is the causal proxy)."""
    def f(bars, k, ctx):
        b = bars[k]
        if ctx["done"] or not (9 * 60 + 45 <= b["mins"] <= last_min):
            return None
        o = bars[0]["o"]
        r = b["c"] / o - 1
        if r >= thr:
            ctx["done"].add(1)
            return (1, (o + b["c"]) / 2)
        if r <= -thr:
            ctx["done"].add(1)
            return (-1, (o + b["c"]) / 2)
        return None
    return f


# ------------------------------------------------------------------ runner
def run_archive(arch: Path):
    d_by, clipped = {}, 0
    for s in SYMS:
        d, n = prep(Path(arch) / f"{s}.csv.gz")
        d_by[s], clipped = d, clipped + n
    days_by = {s: by_day(d) for s, d in d_by.items()}
    sessions = sorted(set().union(*[set(v) for v in days_by.values()]))
    return d_by, days_by, sessions, clipped


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive1m", required=True)
    ap.add_argument("--archive5m", required=True)
    ap.add_argument("--desk-trades")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    summary = {"prereg": "research/foundry/PREREG_batch4.md"}
    for tag, arch in (("A_1m", a.archive1m), ("B_5m", a.archive5m)):
        d_by, days_by, sessions, clipped = run_archive(Path(arch))
        rnd = random_set(days_by)
        rnd.to_csv(out / f"random_{tag}.csv.gz", index=False)
        res = {"sessions": len(sessions), "first": sessions[0], "last": sessions[-1], "clipped_bars": clipped,
               "random_n": int(len(rnd)), "random_mean": float(rnd["net"].mean() * 100)}
        res["H9"] = {}
        for thr in THR:
            rnd[f"far{thr}"] = rnd["dist"] >= thr
            res["H9"][str(thr)] = filter_block(rnd, f"far{thr}", sessions)
        res["H10"] = {"stretched_long": int(rnd[(rnd.side > 0)]["stretched"].sum()),
                      "stretched_short": int(rnd[(rnd.side < 0)]["stretched"].sum()),
                      "stretched_days": int(rnd[rnd["stretched"]]["day"].nunique()),
                      **filter_block(rnd, "stretched", sessions)}
        res["H11_random"] = paired(rnd, sessions)
        rs = rule_set(d_by, days_by)
        rs.to_csv(out / f"rules_{tag}.csv", index=False)
        res["H11_rules"] = {"all": paired(rs, sessions),
                            "by_rule": {k: paired(g, sessions) for k, g in rs.groupby("rule")}}
        cells = {}
        for (rule, side, shape), g in rs[rs["rule"].isin(["F1_cloud_ride", "F2_cloud_ride_tight"])].groupby(["rule", "side", "shape"]):
            cells[f"{rule}|{'L' if side > 0 else 'S'}|{shape}"] = dict(n=int(len(g)), mean=float(g["net"].mean() * 100))
        res["H12_F1F2"] = cells
        shapes = {}
        for s, days in days_by.items():
            for d, rows in days.items():
                shapes.setdefault(day_shape(rows), set()).add(f"{s}:{d}")
        res["day_shapes"] = {k: len(v) for k, v in shapes.items()}
        h13 = []
        for sym, d in d_by.items():
            h13 += sim3(d, sym, "H13_open1", open1_signal())
        h13 = pd.DataFrame(h13)
        h13.to_csv(out / f"h13_{tag}.csv", index=False)
        st = stat3(h13, sessions)
        if len(h13):
            st["rand_p95"] = random_p95(d_by, h13)
        res["H13"] = st
        summary[tag] = res
    if a.desk_trades and Path(a.desk_trades).exists():
        ds = desk_set(Path(a.desk_trades), Path(a.archive1m))
        ds.to_csv(out / "desk_overlay.csv", index=False)
        sess = sorted(ds["day"].unique())
        ds["far"] = ds["dist"] >= 0.003
        summary["desks"] = {"n": int(len(ds)),
                            "H9_far0.003": filter_block(ds, "far", sess),
                            "H9_by_desk": {k: split_diff(g, "far", boot=False) for k, g in ds.groupby("desk")},
                            "H10_cvd": split_diff(ds[ds.desk.str.startswith("cvd")], "stretched"),
                            "H10_all": split_diff(ds, "stretched"),
                            "H11": paired(ds, sess),
                            "H11_by_desk": {k: paired(g, sess) for k, g in ds.groupby("desk")}}
        cvd = ds[ds.desk.str.startswith("cvd")]
        h12 = {}
        for (desk, shape), g in cvd.groupby(["desk", "shape"]):
            h12[f"{desk}|{shape}"] = dict(n=int(len(g)), actual=float(g["net"].mean() * 100),
                                          hold=float(g["hold"].mean() * 100), vwap=float(g["vwap_exit"].mean() * 100))
        summary["desks"]["H12_cvd"] = h12
    (out / "summary.json").write_text(json.dumps(summary, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
