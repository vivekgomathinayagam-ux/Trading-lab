"""Exit study (pre-registered: research/exits/PREREG.md). ENTRIES ARE FROZEN.

One replay of the shared day-trade core finds each desk's entries. Each entry is then re-run through
alternative exits on the same 1-minute bars. Nothing in strategies/ or engine/ is touched.

  python -m lab.floor.exit_lab --archive path/to/etf1m --out out/exits
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from bisect import bisect_left
from collections import defaultdict
from datetime import datetime, time as dtime, timedelta
from pathlib import Path
from statistics import mean

from strategies.daytrade.core import (FLAT_AT, SLIP, STOP_PCT, SYMBOLS, TARGET_PCT, CVDTurn, EMACross, ORB,
                                      VolSpike, Bar)

from .data import load_1m
from .engine import simulate

FEE = 0.00003              # regulatory fee on sells (SEC/TAF order of magnitude); $0 commission
LEVELS = [0.005, 0.01, 0.015, 0.02, 0.03, 0.05]
CVD_DESKS = {"cvd_spy", "cvd_tqqq"}
DESKS = ["orb_vol", "ema_vol", "volspike", "cvd_spy", "cvd_tqqq"]


# ------------------------------------------------------------------ variants
def variants() -> dict[str, dict]:
    v: dict[str, dict] = {"BASE": dict(tp=TARGET_PCT, cvd="base")}
    for x in (0.005, 0.01, 0.015, 0.02, 0.03, 0.05):
        v[f"A_tp{x * 100:g}"] = dict(tp=x, cvd=None)
    for x in (0.005, 0.01, 0.015):
        v[f"B_trail{x * 100:g}"] = dict(tp=TARGET_PCT, trail=x, cvd=None)
    for k in (2, 3):
        v[f"B_atr{k}"] = dict(tp=TARGET_PCT, atr=k, cvd=None)
    v["C_half@1"] = dict(tp=TARGET_PCT, part=(0.01, 0.5), cvd="base")
    v["C_half@2"] = dict(tp=TARGET_PCT, part=(0.02, 0.5), cvd="base")
    v["C_half@1.5+trail1"] = dict(tp=TARGET_PCT, part=(0.015, 0.5), part_trail=0.01, cvd="base")
    for n in (1, 2, 3):
        v[f"D_delay{n}"] = dict(tp=TARGET_PCT, cvd=("delay", n), only_cvd=True)
    v["D_confirm"] = dict(tp=TARGET_PCT, cvd=("confirm", 5), only_cvd=True)
    return v


VARS = variants()
PRICE_ONLY = [k for k, c in VARS.items() if not c.get("only_cvd") and c.get("cvd") != "base"]


# ------------------------------------------------------------------ data helpers
class SymData:
    def __init__(self, sym: str, bars: list[Bar]):
        self.sym = sym
        self.bars = bars
        self.times = [b.t for b in bars]
        self.idx = {b.t: i for i, b in enumerate(bars)}
        self.atr = self._atr5()
        self.sells: list[datetime] = []
        if sym in ("SPY", "TQQQ"):
            rule = CVDTurn(sym)
            for b in bars:
                if rule.observe(sym, b) == "cvd_sell":
                    self.sells.append(b.t)

    def _atr5(self, n: int = 14) -> list[float]:
        """Causal 5-minute ATR (simple mean of the last n completed candles' true ranges, carried
        across sessions), value as known at the START of each 1-minute bar."""
        out, trs, cur, cur_id, prev_close = [], [], None, None, None
        for b in self.bars:
            m = b.t.hour * 60 + b.t.minute - 570
            cid = (b.t.date(), m // 5)
            if cur is not None and cid != cur_id:
                h, l, c = cur
                tr = max(h - l, abs(h - prev_close), abs(l - prev_close)) if prev_close is not None and cur_id[0] == cid[0] else h - l
                trs.append(tr)
                prev_close = c
                cur = None
            out.append(mean(trs[-n:]) if len(trs) >= 3 else 0.0)
            if cur is None:
                cur, cur_id = [b.h, b.l, b.c], cid
            else:
                cur[0], cur[1], cur[2] = max(cur[0], b.h), min(cur[1], b.l), b.c
        return out


def day_end_idx(sd: SymData, i0: int) -> int:
    d = sd.bars[i0].t.date()
    j = i0
    while j + 1 < len(sd.bars) and sd.bars[j + 1].t.date() == d:
        j += 1
    return j


# ------------------------------------------------------------------ one trade, one exit rule
def run_exit(sd: SymData, i0: int, entry_px: float, cfg: dict, is_cvd: bool, slip_mult: float = 1.0,
             entry_slip_in_px: bool = True, fee: float = FEE, entry_t_for_sells: datetime | None = None) -> dict:
    slip1 = SLIP[sd.sym]
    raw = entry_px / (1 + slip1) if entry_slip_in_px else entry_px
    ent = raw * (1 + slip1 * slip_mult)
    slip = slip1 * slip_mult
    stop_lvl = ent * (1 - STOP_PCT)
    tp_lvl = ent * (1 + cfg["tp"])
    trail, atr_k = cfg.get("trail"), cfg.get("atr")
    part = cfg.get("part")
    part_done = False
    legs: list[tuple[float, float, str, datetime]] = []
    hwm = ent
    j_end = day_end_idx(sd, i0)
    cvd_mode = cfg.get("cvd")
    if not is_cvd and cvd_mode != "base":
        cvd_mode = None
    sig_t: datetime | None = None
    if is_cvd and cvd_mode:
        t0 = entry_t_for_sells or sd.bars[i0].t
        cands = [t for t in sd.sells if t >= t0 and t.date() == t0.date()]
        sigs = []
        for t in cands:
            if cvd_mode == "base":
                sigs.append(t)
            elif cvd_mode[0] == "delay":
                sigs.append(t + timedelta(minutes=3 * cvd_mode[1]))
            else:  # confirm: first candle close below the sell candle's low, else after N candles
                s = sd.idx[t]
                low = min(sd.bars[k].l for k in range(max(0, s - 2), s + 1))
                chosen = None
                for k in range(1, cvd_mode[1] + 1):
                    j = bisect_left(sd.times, t + timedelta(minutes=3 * k))
                    if j > j_end:
                        break
                    if sd.bars[j].c < low or k == cvd_mode[1]:
                        chosen = sd.bars[j].t
                        break
                if chosen:
                    sigs.append(chosen)
        sig_t = min(sigs) if sigs else None
    pending = False
    mfe_in = 0.0
    remaining = 1.0

    def sell(frac, px, reason, t):
        legs.append((frac, px * (1 - slip) * (1 - fee), reason, t))

    for j in range(i0, j_end + 1):
        b = sd.bars[j]
        if pending:                                      # signal exit decided at the prior bar's close
            sell(remaining, b.o, "cvd_sell" if cvd_mode else "signal", b.t)
            remaining = 0
            break
        if b.t.time() >= FLAT_AT:
            sell(remaining, b.o, "eod", b.t)
            remaining = 0
            break
        lvl = stop_lvl
        if trail:
            lvl = max(lvl, hwm * (1 - trail))
        if atr_k and sd.atr[j] > 0:
            lvl = max(lvl, hwm - atr_k * sd.atr[j])
        if part_done and cfg.get("part_trail"):
            lvl = max(lvl, hwm * (1 - cfg["part_trail"]))
        if b.l <= lvl:
            sell(remaining, min(b.o, lvl), "stop" if lvl <= stop_lvl + 1e-12 else "trail", b.t)
            remaining = 0
            break
        mfe_in = max(mfe_in, hwm / ent - 1)
        if part and not part_done and b.h >= ent * (1 + part[0]):
            px = max(b.o, ent * (1 + part[0]))
            sell(part[1], px, "partial", b.t)
            remaining -= part[1]
            part_done = True
            mfe_in = max(mfe_in, px / ent - 1)
        if b.h >= tp_lvl:
            sell(remaining, max(b.o, tp_lvl), "target", b.t)
            mfe_in = max(mfe_in, cfg["tp"])
            remaining = 0
            break
        hwm = max(hwm, b.h)
        if sig_t is not None and b.t >= sig_t:
            pending = True
    if remaining > 1e-9:                                  # data ended before 15:55
        b = sd.bars[j_end]
        sell(remaining, b.c, "end", b.t)
    ret = sum(f * (px / ent - 1) for f, px, _, _ in legs)
    t_exit = legs[-1][3]
    return {"ret": ret * 100, "reason": legs[-1][2], "t_exit": t_exit, "px_exit": legs[-1][1],
            "hold_min": (t_exit - sd.bars[i0].t).total_seconds() / 60, "mfe_in": mfe_in * 100,
            "partial": any(r == "partial" for _, _, r, _ in legs)}


# ------------------------------------------------------------------ MFE / MAE
def excursions(sd: SymData, i0: int, entry_px: float, exit_t: datetime) -> dict:
    j_end = day_end_idx(sd, i0)
    j_flat = j_end
    for j in range(i0, j_end + 1):
        if sd.bars[j].t.time() >= FLAT_AT:
            j_flat = j
            break
    hi, lo, hi_j = entry_px, entry_px, i0
    reach: dict[float, int | None] = {x: None for x in LEVELS}
    stop_j = None
    for j in range(i0, j_flat):
        b = sd.bars[j]
        if b.h > hi:
            hi, hi_j = b.h, j
        lo = min(lo, b.l)
        for x in LEVELS:
            if reach[x] is None and b.h >= entry_px * (1 + x):
                reach[x] = j
        if stop_j is None and b.l <= entry_px * (1 - STOP_PCT):
            stop_j = j
    close_px = sd.bars[j_flat].o
    out = {"mfe_pct": (hi / entry_px - 1) * 100, "mae_pct": (lo / entry_px - 1) * 100,
           "t_mfe_min": (sd.bars[hi_j].t - sd.bars[i0].t).total_seconds() / 60,
           "hold_to_close_pct": (close_px / entry_px - 1) * 100,
           "giveback_pct": (hi / entry_px - 1) * 100 - (close_px / entry_px - 1) * 100}
    for x in LEVELS:
        j = reach[x]
        out[f"min_to_{x * 100:g}"] = None if j is None else (sd.bars[j].t - sd.bars[i0].t).total_seconds() / 60
        out[f"hit_{x * 100:g}_before_stop"] = bool(j is not None and (stop_j is None or j < stop_j))
    # what happened after the exit (only informative when the baseline exit was early)
    jx = bisect_left(sd.times, exit_t)
    if jx <= j_flat:
        w30 = [sd.bars[k].h for k in range(jx, min(jx + 30, j_flat))]
        w60 = [sd.bars[k].h for k in range(jx, min(jx + 60, j_flat))]
        px_x = sd.bars[min(jx, j_flat)].o
        out["after_max30_pct"] = (max(w30) / px_x - 1) * 100 if w30 else 0.0
        out["after_max60_pct"] = (max(w60) / px_x - 1) * 100 if w60 else 0.0
        out["after_to_close_pct"] = (close_px / px_x - 1) * 100
    return out


# ------------------------------------------------------------------ metrics
def metrics(rets: list[float], holds: list[float] | None = None, mfes: list[float] | None = None) -> dict:
    n = len(rets)
    if not n:
        return {"n": 0}
    wins = [r for r in rets if r > 0]
    losses = [r for r in rets if r <= 0]
    pf = (sum(wins) / -sum(losses)) if losses and sum(losses) < 0 else (99.0 if wins else 0.0)
    eq, peak, mdd = 1.0, 1.0, 0.0
    for r in rets:
        eq *= 1 + r / 100
        peak = max(peak, eq)
        mdd = min(mdd, eq / peak - 1)
    out = {"n": n, "win_rate": round(len(wins) / n * 100, 1),
           "avg_win": round(mean(wins), 3) if wins else 0.0, "avg_loss": round(mean(losses), 3) if losses else 0.0,
           "expectancy": round(mean(rets), 3), "pf": round(min(pf, 99.0), 2),
           "total_return": round((eq - 1) * 100, 2), "max_dd": round(mdd * 100, 2),
           "avg_hold_min": round(mean(holds), 1) if holds else None}
    if mfes is not None:
        for x in LEVELS:
            out[f"reach_{x * 100:g}"] = round(sum(1 for m in mfes if m >= x * 100 - 1e-9) / n * 100, 0)
    return out


def boot_diff(pairs: list[tuple[str, float, float]], iters: int = 3000, seed: int = 7) -> tuple[float, float, float]:
    """pairs = (day, variant_ret, base_ret). Resample days. Returns mean diff and 90% interval."""
    by_day = defaultdict(list)
    for d, a, b in pairs:
        by_day[d].append(a - b)
    days = list(by_day)
    rng = random.Random(seed)
    stats = []
    for _ in range(iters):
        s, c = 0.0, 0
        for _ in days:
            xs = by_day[rng.choice(days)]
            s += sum(xs)
            c += len(xs)
        stats.append(s / c if c else 0.0)
    stats.sort()
    allv = [x for xs in by_day.values() for x in xs]
    return mean(allv), stats[int(0.05 * iters)], stats[int(0.95 * iters)]


# ------------------------------------------------------------------ main pipeline
def find_entries(bars: dict[str, list[Bar]]) -> list[dict]:
    rules = [ORB(), EMACross(), VolSpike(), CVDTurn("SPY"), CVDTurn("TQQQ")]
    res = simulate(bars, rules)
    rows = []
    for d in res["desks"]:
        for t in d.trades:
            rows.append({**t, "desk_key": d.key})
    return rows


def evaluate_trades(trades: list[dict], data: dict[str, SymData], slip_mult: float = 1.0, fee: float = FEE) -> dict:
    """-> {desk: {variant: [row,...]}}"""
    out: dict = {k: {} for k in DESKS}
    for tr in trades:
        sd = data[tr["sym"]]
        t_entry = datetime.fromisoformat(tr["entry_t"])
        i0 = sd.idx[t_entry]
        is_cvd = tr["desk_key"] in CVD_DESKS
        for vn, cfg in VARS.items():
            if cfg.get("only_cvd") and not is_cvd:
                continue
            r = run_exit(sd, i0, tr["entry_px"], cfg, is_cvd, slip_mult=slip_mult, fee=fee, entry_t_for_sells=t_entry)
            r["day"] = t_entry.date().isoformat()
            r["sym"] = tr["sym"]
            out[tr["desk_key"]].setdefault(vn, []).append(r)
    return out


def parity(trades: list[dict], data: dict[str, SymData]) -> dict:
    bad, n = [], 0
    for tr in trades:
        sd = data[tr["sym"]]
        t_entry = datetime.fromisoformat(tr["entry_t"])
        r = run_exit(sd, sd.idx[t_entry], tr["entry_px"], VARS["BASE"], tr["desk_key"] in CVD_DESKS, fee=0.0,
                     entry_t_for_sells=t_entry)
        n += 1
        if abs(r["px_exit"] - tr["exit_px"]) > 2e-3 or r["reason"] != tr["reason"]:
            bad.append({"desk": tr["desk_key"], "entry": tr["entry_t"], "engine": (tr["exit_px"], tr["reason"]),
                        "replay": (round(r["px_exit"], 4), r["reason"])})
    return {"trades": n, "mismatches": bad}


def random_control(data: dict[str, SymData], days: list[str], per: int = 30, seed: int = 11) -> dict:
    rng = random.Random(seed)
    rets = {v: [] for v in PRICE_ONLY}
    for d in days:
        for sym in SYMBOLS:
            sd = data[sym]
            ix = [i for i, b in enumerate(sd.bars) if b.t.date().isoformat() == d
                  and dtime(9, 35) <= b.t.time() < dtime(15, 30)]
            if len(ix) < 10:
                continue
            for _ in range(per):
                i0 = rng.choice(ix)
                px = sd.bars[i0].o * (1 + SLIP[sym])
                for v in PRICE_ONLY:
                    rets[v].append(run_exit(sd, i0, px, VARS[v], False)["ret"])
    return {v: {"n": len(r), "expectancy": round(mean(r), 3), "win_rate": round(sum(1 for x in r if x > 0) / len(r) * 100, 1)}
            for v, r in rets.items() if r}


def walk_forward(ev: dict, min_train_days: int = 8) -> dict:
    """Chronological. Choose the variant with the best mean return on EARLIER days only."""
    days = sorted({r["day"] for d in ev.values() for rs in d.values() for r in rs})
    pooled_names = [v for v in VARS if not VARS[v].get("only_cvd")]
    res = {"days": days, "pooled": [], "per_desk": {}}
    # pooled
    tot_sel, tot_base, steps = [], [], []
    for k in range(min_train_days, len(days)):
        train, test = set(days[:k]), days[k]
        best, best_m = "BASE", -1e9
        for v in pooled_names:
            xs = [r["ret"] for d in ev.values() for r in d.get(v, []) if r["day"] in train]
            if len(xs) >= 5 and mean(xs) > best_m:
                best, best_m = v, mean(xs)
        for dk, d in ev.items():
            for r, b in zip(d.get(best, []), d["BASE"]):
                if r["day"] == test:
                    tot_sel.append((test, r["ret"]))
                    tot_base.append((test, b["ret"]))
        steps.append((test, best))
    res["pooled"] = {"test_trades": len(tot_sel), "selected_mean": round(mean(x for _, x in tot_sel), 3) if tot_sel else None,
                     "base_mean": round(mean(x for _, x in tot_base), 3) if tot_base else None,
                     "choices": steps}
    # per desk
    for dk, d in ev.items():
        names = [v for v in VARS if v in d]
        trades = d["BASE"]
        sel, base, ch = [], [], []
        for i, b in enumerate(trades):
            prior = [t for t in trades[:i]]
            if len(prior) < 5:
                continue
            best, best_m = "BASE", -1e9
            for v in names:
                xs = [d[v][k]["ret"] for k in range(i)]
                if mean(xs) > best_m:
                    best, best_m = v, mean(xs)
            sel.append(d[best][i]["ret"])
            base.append(b["ret"])
            ch.append(best)
        res["per_desk"][dk] = {"test_trades": len(sel), "selected_mean": round(mean(sel), 3) if sel else None,
                               "base_mean": round(mean(base), 3) if base else None, "choices": ch}
    return res


def hold_overnight(trades: list[dict], data: dict[str, SymData], base_rows: dict, slip_mult: float = 1.0) -> dict:
    """For trades the baseline flattened at 15:55 ('eod'): what if they had been held to the NEXT session's
    15:55, with the same -2.5% stop and +5% target measured from entry? Gap risk is real: a stop is filled at
    the gap open if the open is already through it."""
    rows = []
    for tr in trades:
        t_entry = datetime.fromisoformat(tr["entry_t"])
        day = t_entry.date().isoformat()
        base = next(r for r in base_rows[tr["desk_key"]]["BASE"] if r["day"] == day)
        if base["reason"] != "eod":
            continue
        sd = data[tr["sym"]]
        i0 = sd.idx[t_entry]
        j_flat = next((j for j in range(i0, day_end_idx(sd, i0) + 1) if sd.bars[j].t.time() >= FLAT_AT), None)
        if j_flat is None or j_flat + 1 >= len(sd.bars):
            continue
        k0 = day_end_idx(sd, j_flat) + 1
        if k0 >= len(sd.bars):
            continue
        k_end = day_end_idx(sd, k0)
        slip = SLIP[sd.sym] * slip_mult
        ent = tr["entry_px"] / (1 + SLIP[sd.sym]) * (1 + slip)
        stop, tp = ent * (1 - STOP_PCT), ent * (1 + TARGET_PCT)
        out, reason = None, None
        for j in range(j_flat, k_end + 1):
            b = sd.bars[j]
            if b.t.date() > sd.bars[i0].t.date() and b.t.time() >= FLAT_AT:
                out, reason = b.o, "eod2"
                break
            if b.l <= stop:
                out, reason = min(b.o, stop), "stop"
                break
            if b.h >= tp:
                out, reason = max(b.o, tp), "target"
                break
        if out is None:
            out, reason = sd.bars[k_end].c, "end"
        ret = (out * (1 - slip) * (1 - FEE) / ent - 1) * 100
        rows.append({"desk": tr["desk_key"], "day": day, "sym": tr["sym"], "ret_flat": base["ret"], "ret_hold": ret,
                     "gap_pct": (sd.bars[k0].o / sd.bars[j_flat].o - 1) * 100, "reason2": reason})
    return {"n": len(rows), "flat_mean": round(mean(r["ret_flat"] for r in rows), 3) if rows else None,
            "hold_mean": round(mean(r["ret_hold"] for r in rows), 3) if rows else None,
            "gap_mean": round(mean(r["gap_pct"] for r in rows), 3) if rows else None,
            "gap_worst": round(min(r["gap_pct"] for r in rows), 3) if rows else None,
            "worst_hold": round(min(r["ret_hold"] for r in rows), 3) if rows else None,
            "stops": sum(1 for r in rows if r["reason2"] == "stop"),
            "by_desk": {dk: {"n": len([r for r in rows if r["desk"] == dk]),
                              "flat_mean": round(mean(r["ret_flat"] for r in rows if r["desk"] == dk), 3),
                              "hold_mean": round(mean(r["ret_hold"] for r in rows if r["desk"] == dk), 3)}
                        for dk in DESKS if any(r["desk"] == dk for r in rows)}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--random-per", type=int, default=30)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    bars = {s: load_1m(s, Path(a.archive), fetch=False) for s in SYMBOLS}
    data = {s: SymData(s, bars[s]) for s in SYMBOLS}
    trades = find_entries(bars)
    par = parity(trades, data)
    ev = {}
    for m in (1.0, 2.0, 3.0):
        ev[m] = evaluate_trades(trades, data, slip_mult=m)
    e1 = ev[1.0]
    days = sorted({r["day"] for d in e1.values() for rs in d.values() for r in rs})
    # excursions on baseline entries
    exc_rows = []
    for tr in trades:
        sd = data[tr["sym"]]
        t_entry = datetime.fromisoformat(tr["entry_t"])
        i0 = sd.idx[t_entry]
        base = next(r for r in e1[tr["desk_key"]]["BASE"] if r["day"] == t_entry.date().isoformat())
        ex = excursions(sd, i0, tr["entry_px"], base["t_exit"])
        exc_rows.append({"desk": tr["desk_key"], "sym": tr["sym"], "day": t_entry.date().isoformat(),
                         "entry_t": tr["entry_t"], "base_exit": base["reason"], "base_ret": round(base["ret"], 3),
                         "base_hold_min": base["hold_min"], **{k: (round(v, 3) if isinstance(v, float) else v) for k, v in ex.items()}})
    with open(out / "trades_mfe.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(exc_rows[0]))
        w.writeheader()
        w.writerows(exc_rows)
    table = {}
    for m, evm in ev.items():
        table[m] = {}
        for dk in DESKS:
            table[m][dk] = {}
            for vn, rows in evm[dk].items():
                table[m][dk][vn] = metrics([r["ret"] for r in rows], [r["hold_min"] for r in rows], [r["mfe_in"] for r in rows])
    # pooled across desks (non-CVD-only variants)
    pooled = {}
    for vn in VARS:
        if VARS[vn].get("only_cvd"):
            continue
        rows = [r for dk in DESKS for r in e1[dk].get(vn, [])]
        pooled[vn] = metrics([r["ret"] for r in rows], [r["hold_min"] for r in rows], [r["mfe_in"] for r in rows])
    # paired bootstrap vs BASE
    boots = {"pooled": {}, "per_desk": {}}
    for vn in VARS:
        if vn == "BASE":
            continue
        pairs = []
        for dk in DESKS:
            if vn in e1[dk]:
                pairs += [(r["day"], r["ret"], b["ret"]) for r, b in zip(e1[dk][vn], e1[dk]["BASE"])]
        if pairs and not VARS[vn].get("only_cvd"):
            m, lo, hi = boot_diff(pairs)
            boots["pooled"][vn] = {"diff": round(m, 3), "lo90": round(lo, 3), "hi90": round(hi, 3), "n": len(pairs)}
        for dk in DESKS:
            if vn in e1[dk]:
                p = [(r["day"], r["ret"], b["ret"]) for r, b in zip(e1[dk][vn], e1[dk]["BASE"])]
                m, lo, hi = boot_diff(p)
                boots["per_desk"].setdefault(dk, {})[vn] = {"diff": round(m, 3), "lo90": round(lo, 3), "hi90": round(hi, 3), "n": len(p)}
    wf = walk_forward(e1)
    rc = random_control(data, days, per=a.random_per)
    res = {"parity": par, "days": days, "n_trades": len(trades), "variants": list(VARS), "table_1x": table[1.0],
           "table_2x": table[2.0], "table_3x": table[3.0], "pooled_1x": pooled, "bootstrap": boots,
           "walk_forward": wf, "random_control": rc,
           "overnight": hold_overnight(trades, data, e1)}
    (out / "results.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({"parity": par["trades"], "mismatches": len(par["mismatches"]), "trades": len(trades), "days": len(days)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
