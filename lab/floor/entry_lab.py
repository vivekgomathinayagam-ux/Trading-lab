"""Entry-quality study, part 1: the signal dataset (pre-registered: research/entries/PREREG.md).

Every signal fire of every production rule (fresh instances; nothing in strategies/ is modified), with
causal features at the signal bar's close and the outcome of entering at the next bar's open.

  python -m lab.floor.entry_lab --archive path/to/etf1m --out research/entries
"""
from __future__ import annotations

import argparse
import csv
import gzip
import math
from bisect import bisect_left
from collections import deque
from datetime import datetime, time as dtime, timedelta
from pathlib import Path
from statistics import mean, median

from strategies.daytrade.core import (ENTRY_END, ENTRY_START, FLAT_AT, LEVERAGED, OPEN_MIN, SLIP, SYMBOLS,
                                      CVDTurn, EMACross, EMACrossV2, Features, ORB, VolSpike, Bar)

from .data import load_1m
from .engine import simulate
from .exit_lab import FEE, VARS, SymData, run_exit

INDEX = {"SPY": ("SPY", 1), "UPRO": ("SPY", 1), "SPXU": ("SPY", -1),
         "QQQ": ("QQQ", 1), "TQQQ": ("QQQ", 1), "SQQQ": ("QQQ", -1)}
OTHER = {"SPY": "QQQ", "QQQ": "SPY"}
WARMUP = 3


def make_rules():
    return [ORB(), EMACross(), EMACrossV2(), VolSpike(), CVDTurn("SPY"), CVDTurn("TQQQ")]


class Tracker:
    """Extra causal per-symbol state for the study's features (the production Features class is reused
    for vol_ratio, minute_ratio, vwap, prior_high and the opening range)."""

    def __init__(self, sym: str):
        self.sym = sym
        self.lev = 3 if sym in LEVERAGED else 1
        self.day = None
        self.closes_hist: deque = deque(maxlen=6)           # prior sessions' closes
        self.prev_high = self.prev_low = None
        self.cumvol_hist: deque = deque(maxlen=5)           # per prior day: list[390] cumulative volume
        self.range_hist: deque = deque(maxlen=5)            # per prior day: list[390] range so far
        self.ema9 = self.ema20 = None
        self.ema_n = 0
        self.c5_id = None
        self.c5_close = None
        self._new(None)

    def _new(self, d) -> None:
        if self.day is not None:
            self.cumvol_hist.append(self._fill(self.cum_by_min))
            self.range_hist.append(self._fill(self.rng_by_min))
            self.closes_hist.append(self.closes[-1] if self.closes else None)
            self.prev_high, self.prev_low = self.hod, self.lod
        self.day = d
        self.open = None
        self.hod, self.lod = -math.inf, math.inf
        self.cum = 0.0
        self.cum_by_min: dict[int, float] = {}
        self.rng_by_min: dict[int, float] = {}
        self.closes: list[float] = []
        self.vols: list[float] = []
        self.cvd: list[float] = [0.0]
        self.deltas: list[float] = []
        self.orh_cross = 0
        self.prev_close_vs_orh = None

    @staticmethod
    def _fill(d: dict) -> list:
        out, last = [], math.nan
        for m in range(390):
            if m in d:
                last = d[m]
            out.append(last)
        return out

    def update(self, b: Bar, or_high) -> None:
        d = b.t.date()
        if d != self.day:
            self._new(d)
        m = b.t.hour * 60 + b.t.minute - OPEN_MIN
        if self.open is None:
            self.open = b.o
        self.hod, self.lod = max(self.hod, b.h), min(self.lod, b.l)
        self.cum += b.v
        if 0 <= m < 390:
            self.cum_by_min[m] = self.cum
            self.rng_by_min[m] = self.hod - self.lod
        rng = b.h - b.l
        delta = b.v * ((b.c - b.l) - (b.h - b.c)) / rng if rng > 0 else 0.0
        self.deltas.append(delta)
        self.cvd.append(self.cvd[-1] + delta)
        self.closes.append(b.c)
        self.vols.append(b.v)
        if or_high is not None and m >= 15:
            above = b.c > or_high
            if self.prev_close_vs_orh is not None and above and not self.prev_close_vs_orh:
                self.orh_cross += 1
            self.prev_close_vs_orh = above
        # 5-minute clock candles, EMA 9/20 carried across sessions
        cid = (d, m // 5)
        if self.c5_id is not None and cid != self.c5_id:
            self._close5(self.c5_close)
        self.c5_id, self.c5_close = cid, b.c
        if (m + 1) % 5 == 0:
            self._close5(b.c)
            self.c5_id = None

    def _close5(self, c: float) -> None:
        if self.ema9 is None:
            self.ema9 = self.ema20 = c
        else:
            self.ema9 = c * 0.2 + self.ema9 * 0.8
            self.ema20 = c * (2 / 21) + self.ema20 * (1 - 2 / 21)
        self.ema_n += 1

    def hist_at(self, hist: deque, m: int) -> float:
        xs = [h[min(max(m, 0), 389)] for h in hist if h and not math.isnan(h[min(max(m, 0), 389)])]
        return mean(xs) if len(xs) >= 3 else math.nan

    def slope(self, n: int, back: int = 0) -> float:
        k = len(self.deltas) - back
        if k < n:
            return math.nan
        v = sum(self.vols[k - n:k])
        return sum(self.deltas[k - n:k]) / v if v > 0 else 0.0


def features(sym: str, b: Bar, f: Features, tr: dict[str, Tracker], atr: float, n_prior: int) -> dict:
    t = tr[sym]
    m = b.t.hour * 60 + b.t.minute - OPEN_MIN
    A = atr if atr and atr > 0 else math.nan
    idx, sign = INDEX[sym]
    it, ot = tr[idx], tr[OTHER[idx]]

    def ret_open(x: Tracker) -> float:
        return (x.closes[-1] / x.open - 1) * 100 if x.closes and x.open else math.nan

    def ret_n(x: Tracker, n: int) -> float:
        return (x.closes[-1] / x.closes[-1 - n] - 1) * 100 if len(x.closes) > n else math.nan

    vols = t.vols
    exp5 = math.nan
    if len(vols) >= 25:
        base = mean(vols[-25:-5])
        exp5 = mean(vols[-5:]) / base if base > 0 else math.nan
    rv_hist = t.hist_at(t.cumvol_hist, m)
    rg_hist = t.hist_at(t.range_hist, m)
    align = 0
    if t.ema9 is not None and t.ema_n > 20:
        if b.c > t.ema9 > t.ema20:
            align = 1
        elif b.c < t.ema9 < t.ema20:
            align = -1
    pc = t.closes_hist[-1] if t.closes_hist else None
    pc2 = t.closes_hist[-2] if len(t.closes_hist) >= 2 else None
    c5 = t.closes_hist[0] if len(t.closes_hist) >= 5 else None
    s5, s5b = t.slope(5), t.slope(5, back=5)
    return {
        "vol_ratio": f.vol_ratio, "minute_ratio": f.minute_ratio,
        "rvol_cum": t.cum / rv_hist if rv_hist and rv_hist > 0 else math.nan,
        "vol_exp5": exp5,
        "cvd_slope15": t.slope(15), "cvd_slope5": s5,
        "cvd_accel": s5 - s5b if not (math.isnan(s5) or math.isnan(s5b)) else math.nan,
        "cvd_day": t.cvd[-1] / t.cum if t.cum > 0 else 0.0,
        "vwap_atr": (b.c - f.vwap) / A,
        "ema_align": align if t.ema_n > 20 else math.nan,
        "ema_spread_atr": (t.ema9 - t.ema20) / A if t.ema9 is not None and t.ema_n > 20 else math.nan,
        "ret30_atr": (b.c - t.closes[-31]) / A if len(t.closes) > 30 else math.nan,
        "ret_open_atr": (b.c - t.open) / A,
        "prev_day_ret": ((pc / pc2 - 1) * 100 / t.lev) if pc and pc2 else math.nan,
        "ret5d": ((b.c / c5 - 1) * 100 / t.lev) if c5 else math.nan,
        "atr_pct": A / b.c * 100 / t.lev,
        "range_ratio": (t.hod - t.lod) / rg_hist if rg_hist and rg_hist > 0 else math.nan,
        "dist_hod_atr": (t.hod - b.c) / A,
        "dist_pdh_atr": (b.c - t.prev_high) / A if t.prev_high else math.nan,
        "dist_orh_atr": (b.c - f.or_high) / A if f.or_high is not None and m >= 15 else math.nan,
        "orh_crosses": t.orh_cross,
        "minute": m,
        "mkt_open": sign * ret_open(it), "mkt_30": sign * ret_n(it, 30), "mkt_other": sign * ret_open(ot),
        "brk_atr": (b.c - f.prior_high) / A if not math.isnan(f.prior_high) else math.nan,
        "close_loc": (b.c - b.l) / (b.h - b.l) if b.h > b.l else 0.5,
        "n_prior_sig": n_prior,
        # regime inputs (index level, causal)
        "idx_ret_open": ret_open(it), "idx_ret30": ret_n(it, 30),
        "idx_range_ratio": (it.hod - it.lod) / it.hist_at(it.range_hist, m) if it.hist_at(it.range_hist, m) > 0 else math.nan,
        "idx_dist_hod": (it.hod / it.closes[-1] - 1) * 100 if it.closes else math.nan,
        "idx_dist_lod": (it.closes[-1] / it.lod - 1) * 100 if it.closes else math.nan,
        "idx_day_range_avg": it.hist_at(it.range_hist, 389) / it.closes[-1] * 100 if it.closes else math.nan,
    }


FEATURES = ["vol_ratio", "minute_ratio", "rvol_cum", "vol_exp5", "cvd_slope15", "cvd_slope5", "cvd_accel", "cvd_day",
            "vwap_atr", "ema_align", "ema_spread_atr", "ret30_atr", "ret_open_atr", "prev_day_ret", "ret5d", "atr_pct",
            "range_ratio", "dist_hod_atr", "dist_pdh_atr", "dist_orh_atr", "orh_crosses", "minute", "mkt_open",
            "mkt_30", "mkt_other", "brk_atr", "close_loc", "n_prior_sig"]


def scan(bars: dict[str, list[Bar]]) -> list[dict]:
    """Replays the engine's per-bar order (observe -> features -> signal) and records every signal."""
    syms = [s for s in SYMBOLS if bars.get(s)]
    order = {s: i for i, s in enumerate(SYMBOLS)}
    rules = make_rules()
    hub = {s: Features() for s in syms}
    tr = {s: Tracker(s) for s in syms}
    sd = {s: SymData(s, bars[s]) for s in syms}
    days = sorted({b.t.date() for s in syms for b in bars[s]})
    trade_from = days[WARMUP]
    events = sorted(((b.t, order[s], s, b) for s in syms for b in bars[s]), key=lambda e: (e[0], e[1]))
    counts: dict = {}
    out = []
    for t, _, s, b in events:
        for r in rules:
            r.observe(s, b)
        hub[s].update(b)
        tr[s].update(b, hub[s].or_high)
        if b.t.date() < trade_from or not (ENTRY_START <= b.t.time() < ENTRY_END):
            continue
        for r in rules:
            if isinstance(r, CVDTurn) and s != r.sym:
                continue                                  # see report: CVDTurn.signal does not check the symbol
            if not r.signal(hub[s], b):
                continue
            key = (r.key, s, b.t.date())
            n_prior = counts.get(key, 0)
            counts[key] = n_prior + 1
            i = sd[s].idx[b.t]
            row = {"rule": r.key, "sym": s, "day": b.t.date().isoformat(), "t": b.t.isoformat(), "order": order[s],
                   **features(s, b, hub[s], tr, sd[s].atr[i], n_prior)}
            row.update(outcomes(sd[s], i, r.key in ("cvd_spy", "cvd_tqqq")))
            out.append(row)
    return out


def outcomes(sd: SymData, i: int, is_cvd: bool) -> dict:
    j = i + 1
    if j >= len(sd.bars) or sd.bars[j].t.date() != sd.bars[i].t.date() or sd.bars[j].t.time() >= ENTRY_END:
        return {"valid": 0}
    slip = SLIP[sd.sym]
    ent = sd.bars[j].o * (1 + slip)
    r = run_exit(sd, j, ent, VARS["BASE"], is_cvd, entry_t_for_sells=sd.bars[j].t)
    r2 = run_exit(sd, j, ent, VARS["BASE"], is_cvd, slip_mult=2.0, entry_t_for_sells=sd.bars[j].t)
    d = sd.bars[j].t.date()
    flat = next((k for k in range(j, len(sd.bars)) if sd.bars[k].t.date() != d or sd.bars[k].t.time() >= FLAT_AT), len(sd.bars))

    def fwd(n: int) -> float:
        k = min(bisect_left(sd.times, sd.bars[j].t + timedelta(minutes=n)), flat - 1)
        return (sd.bars[k].c * (1 - slip) * (1 - FEE) / ent - 1) * 100

    def exc(n: int | None) -> tuple[float, float]:
        k_end = flat if n is None else min(flat, bisect_left(sd.times, sd.bars[j].t + timedelta(minutes=n)))
        hs = [sd.bars[k].h for k in range(j, max(k_end, j + 1))]
        ls = [sd.bars[k].l for k in range(j, max(k_end, j + 1))]
        return (max(hs) / ent - 1) * 100, (min(ls) / ent - 1) * 100

    m60, a60 = exc(60)
    mc, ac = exc(None)
    return {"valid": 1, "entry_t": sd.bars[j].t.isoformat(), "entry_px": ent, "ret": r["ret"], "ret_2x": r2["ret"],
            "exit_reason": r["reason"], "hold_min": r["hold_min"], "fwd30": fwd(30), "fwd60": fwd(60),
            "mfe60": m60, "mae60": a60, "mfe_close": mc, "mae_close": ac,
            "lev": 3 if sd.sym in LEVERAGED else 1}


def emulate(rows: list[dict], keep=lambda r: True) -> list[dict]:
    """One entry per rule per day: the first valid signal that passes `keep` (engine order: time, then symbol)."""
    first: dict = {}
    for r in sorted(rows, key=lambda r: (r["t"], r["order"])):
        if not r.get("valid"):
            continue
        k = (r["rule"], r["day"])
        if k in first or not keep(r):
            continue
        first[k] = r
    return list(first.values())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    bars = {s: load_1m(s, Path(a.archive), fetch=False) for s in SYMBOLS}
    rows = scan(bars)
    # parity: the unfiltered emulation must reproduce the engine's trades
    res = simulate(bars, make_rules())
    eng = {(d.key, t["entry_t"][:10]): t for d in res["desks"] for t in d.trades}
    emu = {(r["rule"], r["day"]): r for r in emulate(rows)}
    miss = [k for k in eng if k not in emu or emu[k]["entry_t"] != eng[k]["entry_t"] or abs(emu[k]["ret"] - eng[k]["move_pct"]) > 0.02]
    extra = [k for k in emu if k not in eng]
    cols = list(rows[0].keys())
    for r in rows:
        for c in cols:
            r.setdefault(c, "")
    cols = sorted({c for r in rows for c in r}, key=lambda c: (cols.index(c) if c in cols else 999, c))
    with gzip.open(out / "signals.csv.gz", "wt", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: (round(v, 6) if isinstance(v, float) else v) for c, v in r.items()})
    print({"signals": len(rows), "valid": sum(1 for r in rows if r.get("valid")), "engine_trades": len(eng),
           "parity_mismatch": len(miss), "emulated_extra": len(extra), "mismatch_keys": miss[:5], "extra_keys": extra[:5]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
