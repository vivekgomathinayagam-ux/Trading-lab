"""Intraday scalping backtest on 1-minute bars (research only; nothing here trades).

PRE-REGISTERED (written before any result was computed; see strategies/scalp/PLAN.md):
  tickers   : 23 (10 original large caps/ETFs + 13 added ETFs / lower-priced stocks)
  setups    : orb15, vwap_reclaim, ema_fast_cross, rsi3_fade, vol_spike_mom   (indicators/charts only, no news)
  windows   : W1 09:45-11:30 ET, W2 14:00-15:45 ET (entry bar close inside the window)
  exits     : target in {0.15,0.20,0.30,0.40,0.50,0.75}% x stop in {0.10,0.15,0.20,0.30}%, time stop 5 bars
  fills     : signal on bar close, entry at NEXT bar open; stop first if both hit in one bar; gaps fill at the open
  costs     : per side = max(0.02%, measured median half-spread) + 0.003%, applied to every trade
  sides     : long and short both tested (shorting needs margin: for information; live would be long-only / inverse ETFs)
  splits    : train 2024-11..2025-10, validation 2025-11..2026-04, holdout 2026-05..2026-11 (touched once)
  selection : config must have pooled mean net bps > 0 in train AND validation (>=300 trades each); rank by min of the two;
              top 10 go to holdout. Variants tried are counted and reported.
  control   : random entry = same exits applied to EVERY eligible bar in the same window and side
  primary   : net bps per trade (percentage); secondary: net $/trade and $/day on a $1,000 whole-share position
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

TARGETS = [0.15, 0.20, 0.30, 0.40, 0.50, 0.75]
STOPS = [0.10, 0.15, 0.20, 0.30]
HOLD = 5
WINDOWS = {"W1": (9 * 60 + 45, 11 * 60 + 30), "W2": (14 * 60, 15 * 60 + 45)}
SETUPS = ["orb15", "vwap_reclaim", "ema_fast_cross", "rsi3_fade", "vol_spike_mom"]
SPLITS = {"train": ("2024-11-01", "2025-10-31"), "val": ("2025-11-01", "2026-04-30"), "hold": ("2026-05-01", "2026-12-31")}
GROUPS = {
    "orig": "SPY QQQ AAPL MSFT NVDA AMZN META GOOGL TSLA AMD".split(),
    "etf_added": "TQQQ SQQQ SOXL UPRO".split(),
    "low_priced": "PFE T CCL SOFI RIOT AAL RIVN F".split(),
    "stress": ["MARA"],
}
FEE = 0.003 / 100


def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    t = pd.to_datetime(df["t"], utc=True).dt.tz_convert("America/New_York")
    df = df.assign(t=t).sort_values("t").reset_index(drop=True)
    df["day"] = df["t"].dt.strftime("%Y-%m-%d")
    df["min"] = df["t"].dt.hour * 60 + df["t"].dt.minute
    df = df[(df["min"] >= 570) & (df["min"] < 960)].reset_index(drop=True)
    return df


def indicators(df: pd.DataFrame) -> dict:
    c, h, l, v, o = (df[k].to_numpy(float) for k in "chlvo")
    day = df["day"].to_numpy()
    g = df.groupby("day", sort=False)
    typ = (df["h"] + df["l"] + df["c"]) / 3
    vwap = ((typ * df["v"]).groupby(df["day"]).cumsum() / df["v"].groupby(df["day"]).cumsum().replace(0, np.nan)).to_numpy()
    ema9 = g["c"].transform(lambda s: s.ewm(span=9, adjust=False).mean()).to_numpy()
    ema21 = g["c"].transform(lambda s: s.ewm(span=21, adjust=False).mean()).to_numpy()
    d = df["c"].diff()
    up = d.clip(lower=0).groupby(df["day"]).transform(lambda s: s.ewm(alpha=1 / 3, adjust=False).mean())
    dn = (-d.clip(upper=0)).groupby(df["day"]).transform(lambda s: s.ewm(alpha=1 / 3, adjust=False).mean())
    rsi3 = (100 - 100 / (1 + up / dn.replace(0, np.nan))).to_numpy()
    vol_avg = g["v"].transform(lambda s: s.shift(1).rolling(20, min_periods=10).mean()).to_numpy()
    first = df["min"].to_numpy() == 570
    or_hi = g["h"].transform(lambda s: s.iloc[:15].max()).to_numpy()
    or_lo = g["l"].transform(lambda s: s.iloc[:15].min()).to_numpy()
    return dict(c=c, h=h, l=l, o=o, v=v, day=day, vwap=vwap, ema9=ema9, ema21=ema21, rsi3=rsi3, vol_avg=vol_avg,
                or_hi=or_hi, or_lo=or_lo, mins=df["min"].to_numpy())


def prev(a, k=1):
    out = np.full_like(a, np.nan, dtype=float)
    out[k:] = a[:-k]
    return out


def signals(ix: dict) -> dict[str, dict[str, np.ndarray]]:
    c, vwap, e9, e21, rsi, v, va = ix["c"], ix["vwap"], ix["ema9"], ix["ema21"], ix["rsi3"], ix["v"], ix["vol_avg"]
    pc = prev(c)
    ret = (c / pc - 1) * 100
    S = {}
    # ORB 15: close breaks the 09:30-09:45 range (first close beyond it)
    hi, lo = ix["or_hi"], ix["or_lo"]
    S["orb15"] = {"long": (c > hi) & (prev(c) <= hi), "short": (c < lo) & (prev(c) >= lo)}
    # VWAP reclaim: close crosses VWAP after >=3 bars on the other side
    below3 = (prev(c, 1) < prev(vwap, 1)) & (prev(c, 2) < prev(vwap, 2)) & (prev(c, 3) < prev(vwap, 3))
    above3 = (prev(c, 1) > prev(vwap, 1)) & (prev(c, 2) > prev(vwap, 2)) & (prev(c, 3) > prev(vwap, 3))
    S["vwap_reclaim"] = {"long": below3 & (c > vwap), "short": above3 & (c < vwap)}
    # fast EMA cross on 1-minute closes, with price on the right side of VWAP
    S["ema_fast_cross"] = {"long": (e9 > e21) & (prev(e9) <= prev(e21)) & (c > vwap),
                           "short": (e9 < e21) & (prev(e9) >= prev(e21)) & (c < vwap)}
    # RSI(3) fade: extreme RSI then the first bar back
    S["rsi3_fade"] = {"long": (prev(rsi) < 10) & (c > pc), "short": (prev(rsi) > 90) & (c < pc)}
    # volume-spike momentum: >=3x average volume and a >=0.15% bar in the direction
    S["vol_spike_mom"] = {"long": (v > 3 * va) & (ret >= 0.15), "short": (v > 3 * va) & (ret <= -0.15)}
    return S


def thin(sig: np.ndarray, day: np.ndarray) -> np.ndarray:
    """No new signal within HOLD bars of the previous kept one on the same day (one trade at a time)."""
    out = np.zeros_like(sig)
    last_i, last_d = -10**9, None
    for i in np.flatnonzero(sig):
        if day[i] != last_d or i - last_i > HOLD:
            out[i] = True
            last_i, last_d = i, day[i]
    return out


def outcomes(ix: dict, side: str, T: float, Sx: float, cost: float) -> np.ndarray:
    """Net return (decimal) of entering at the OPEN of bar i+1 for every bar i; NaN if the trade would not fit in the day."""
    o, h, l, c, day = ix["o"], ix["h"], ix["l"], ix["c"], ix["day"]
    n = len(o)
    res = np.full(n, np.nan)
    if n < HOLD + 3:
        return res
    idx = np.arange(n - HOLD - 1)
    p0 = o[idx + 1]
    ok = day[idx + 1] == day[idx + 1 + HOLD]
    sgn = 1.0 if side == "long" else -1.0
    tgt = p0 * (1 + sgn * T / 100)
    stp = p0 * (1 - sgn * Sx / 100)
    exit_px = c[idx + HOLD].copy()                 # time stop at the close of bar HOLD
    done = np.zeros(len(idx), bool)
    for k in range(HOLD):
        ok_k = ~done
        ob, hb, lb = o[idx + 1 + k], h[idx + 1 + k], l[idx + 1 + k]
        if side == "long":
            hit_s, hit_t = lb <= stp, hb >= tgt
            gap_s, gap_t = ob <= stp, ob >= tgt
        else:
            hit_s, hit_t = hb >= stp, lb <= tgt
            gap_s, gap_t = ob >= stp, ob <= tgt
        if k == 0:
            gap_s = gap_t = np.zeros(len(idx), bool)
        s_now = ok_k & hit_s
        t_now = ok_k & hit_t & ~hit_s                 # both in one bar -> stop first (pessimistic)
        px_s = np.where(gap_s, ob, stp)
        px_t = np.where(gap_t, ob, tgt)
        exit_px = np.where(s_now, px_s, np.where(t_now, px_t, exit_px))
        done |= s_now | t_now
    gross = sgn * (exit_px / p0 - 1)
    net = gross - 2 * cost
    res[idx] = np.where(ok, net, np.nan)
    return res


def pf(x: np.ndarray) -> float:
    w, ls = x[x > 0].sum(), -x[x < 0].sum()
    return float(w / ls) if ls > 0 else float("inf") if w > 0 else 0.0


def main(data_dir: str, spreads_json: str, out_dir: str) -> None:
    data = Path(data_dir)
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    spreads = json.load(open(spreads_json)) if Path(spreads_json).exists() else {}
    syms = [s for g in GROUPS.values() for s in g if (data / f"{s}.csv.gz").exists()]
    rows = []                                    # one row per trade-set: (sym, setup, win, side, T, S, split) -> aggregates
    daily = []                                   # per-trade records for chosen configs later (kept compact via arrays)
    store = {}
    for s in syms:
        df = load(data / f"{s}.csv.gz")
        ix = indicators(df)
        sg = signals(ix)
        sp = spreads.get(s, {})
        vals = [x for x in (sp.get("open"), sp.get("mid"), sp.get("late")) if x]
        half = (np.median(vals) / 2 / 1e4) if vals else 0.0
        cost = max(0.0002, half) + FEE
        mins, days = ix["mins"], ix["day"]
        splitv = np.full(len(df), "", dtype=object)
        for name, (a, b) in SPLITS.items():
            splitv[(days >= a) & (days <= b)] = name
        px = ix["o"]
        shares_val = lambda p: np.floor(1000 / p) * p
        tsig = {(st, sd, wn): thin(sg[st][sd] & ((mins >= w0) & (mins < w1)), days)
                for st in SETUPS for sd in ("long", "short") for wn, (w0, w1) in WINDOWS.items()}
        print(f"{s}: {len(df)} bars {df['day'].nunique()} days cost/side {cost*1e4:.1f}bps", flush=True)
        for side in ("long", "short"):
            for T in TARGETS:
                for Sx in STOPS:
                    net = outcomes(ix, side, T, Sx, cost)
                    notional = np.full(len(df), np.nan)
                    notional[:-1] = shares_val(px[1:])
                    for wn, (w0, w1) in WINDOWS.items():
                        win = (mins >= w0) & (mins < w1)
                        for setup in SETUPS + ["RANDOM"]:
                            sig = win & np.isfinite(net) if setup == "RANDOM" else tsig[(setup, side, wn)] & np.isfinite(net)
                            for sp_name in SPLITS:
                                m = sig & (splitv == sp_name)
                                if not m.any():
                                    continue
                                x = net[m]
                                rows.append((s, setup, wn, side, T, Sx, sp_name, len(x), float(x.sum()), float(x[x > 0].sum()),
                                             float(-x[x < 0].sum()), float((x * notional[m]).sum()), len(set(days[m]))))
                    # keep the net array only for hold split of signal sets (needed for bootstrap later)
                    for wn, (w0, w1) in WINDOWS.items():
                        win = (mins >= w0) & (mins < w1)
                        for setup in SETUPS:
                            m = tsig[(setup, side, wn)] & np.isfinite(net) & (splitv == "hold")
                            if m.any():
                                store[(s, setup, wn, side, T, Sx)] = (days[m].copy(), net[m].copy(), (net[m] * notional[m]).copy())
    cols = ["sym", "setup", "win", "side", "T", "S", "split", "n", "sum_net", "sum_win", "sum_loss", "sum_usd", "days"]
    R = pd.DataFrame(rows, columns=cols)
    R.to_csv(out / "grid_by_ticker.csv.gz", index=False)
    pool = R.groupby(["setup", "win", "side", "T", "S", "split"]).agg(n=("n", "sum"), sn=("sum_net", "sum"), sw=("sum_win", "sum"),
                                                                      sl=("sum_loss", "sum"), su=("sum_usd", "sum"), d=("days", "sum")).reset_index()
    pool["bps"] = pool["sn"] / pool["n"] * 1e4
    pool.to_csv(out / "grid_pooled.csv", index=False)
    key = ["setup", "win", "side", "T", "S"]
    pv = pool.pivot_table(index=key, columns="split", values=["bps", "n"], aggfunc="first")
    pv.columns = [f"{a}_{b}" for a, b in pv.columns]
    pv = pv.reset_index()
    real = pv[pv["setup"] != "RANDOM"].copy()
    ctrl = pv[pv["setup"] == "RANDOM"].set_index(["win", "side", "T", "S"])
    nvar = len(real)
    cand = real[(real["bps_train"] > 0) & (real["bps_val"] > 0) & (real["n_train"] >= 300) & (real["n_val"] >= 300)].copy()
    cand["score"] = cand[["bps_train", "bps_val"]].min(axis=1)
    cand = cand.sort_values("score", ascending=False)
    n_tr = int((real["bps_train"] > 0).sum()); n_va = int((real["bps_val"] > 0).sum())
    top = cand.head(10)
    rng = np.random.default_rng(7)
    lines = [f"# Scalp backtest results ({pd.Timestamp.now('UTC'):%Y-%m-%d %H:%M} UTC)\n",
             f"Variants tried (setup x window x side x target x stop): **{nvar}**. Profitable in train: {n_tr}; in validation: {n_va}; "
             f"in both with >=300 trades each: **{len(cand)}**. Expected false positives are large when {nvar} configs are tried; read the holdout, not the train numbers.\n",
             "Random-entry control = same exits applied to every eligible bar (mean net bps by split) is in grid_pooled.csv.\n",
             "## Top configs by min(train, validation) net bps, then HOLDOUT\n",
             "| setup | win | side | T% | S% | train bps (n) | val bps (n) | **holdout bps (n)** | hold PF | hold 95% CI bps | control hold bps | hold $/trade | hold $/day | tickers + / total |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in top.iterrows():
        keyv = (r["setup"], r["win"], r["side"], r["T"], r["S"])
        h = pool[(pool.setup == r["setup"]) & (pool.win == r["win"]) & (pool.side == r["side"]) & (pool["T"] == r["T"]) & (pool["S"] == r["S"]) & (pool.split == "hold")]
        c = ctrl.loc[(r["win"], r["side"], r["T"], r["S"])]
        if h.empty:
            lines.append(f"| {r['setup']} | {r['win']} | {r['side']} | {r['T']} | {r['S']} | {r['bps_train']:.1f} ({int(r['n_train'])}) | {r['bps_val']:.1f} ({int(r['n_val'])}) | no holdout trades | | | | | | |")
            continue
        h = h.iloc[0]
        per = R[(R.setup == r["setup"]) & (R.win == r["win"]) & (R.side == r["side"]) & (R["T"] == r["T"]) & (R["S"] == r["S"]) & (R.split == "hold")]
        npos = int((per["sum_net"] > 0).sum())
        # day-block bootstrap on pooled holdout trades
        d_all, x_all = [], []
        for (s_, st, wn, sd, T_, S_), (dd, xx, uu) in store.items():
            if (st, wn, sd, T_, S_) == (r["setup"], r["win"], r["side"], r["T"], r["S"]):
                d_all.append(dd); x_all.append(xx)
        dd = np.concatenate(d_all); xx = np.concatenate(x_all)
        ud, inv = np.unique(dd, return_inverse=True)
        sums = np.bincount(inv, weights=xx); cnts = np.bincount(inv)
        boots = []
        for _ in range(2000):
            pick = rng.integers(0, len(ud), len(ud))
            boots.append(sums[pick].sum() / max(cnts[pick].sum(), 1) * 1e4)
        lo, hi = np.percentile(boots, [2.5, 97.5])
        pfv = h["sw"] / h["sl"] if h["sl"] > 0 else float("inf")
        lines.append(f"| {r['setup']} | {r['win']} | {r['side']} | {r['T']} | {r['S']} | {r['bps_train']:.1f} ({int(r['n_train'])}) | {r['bps_val']:.1f} ({int(r['n_val'])}) | "
                     f"**{h['bps']:.1f} ({int(h['n'])})** | {pfv:.2f} | {lo:.1f} to {hi:.1f} | {c.get('bps_hold', float('nan')):.1f} | "
                     f"{h['su'] / h['n']:.2f} | {h['su'] / max(h['d'], 1):.2f} | {npos}/{len(per)} |")
    if top.empty:
        lines.append("| *no config was profitable in both train and validation with enough trades* | | | | | | | | | | | | | |")
    # honest summary by setup: best holdout of ANY config is not shown (would be cherry-picking); show median and share positive
    lines.append("\n## By setup: share of the configs that were profitable (net) per split\n")
    lines.append("| setup | train | val | hold |\n|---|---|---|---|")
    for st in SETUPS:
        sub = real[real.setup == st]
        hh = pool[(pool.setup == st) & (pool.split == "hold")]
        lines.append(f"| {st} | {(sub['bps_train'] > 0).mean():.0%} | {(sub['bps_val'] > 0).mean():.0%} | {(hh['bps'] > 0).mean():.0%} |")
    rc = pool[(pool.setup == "RANDOM")]
    lines.append("\nRandom-entry control, mean net bps per trade: " + ", ".join(
        f"{sp_}: {rc[rc.split == sp_]['bps'].mean():.2f}" for sp_ in SPLITS))
    lines.append("\n## Per ticker group, same top configs, holdout net bps (pooled)\n")
    gmap = {s: g for g, ss in GROUPS.items() for s in ss}
    R["grp"] = R["sym"].map(gmap)
    lines.append("| setup | win | side | T | S | " + " | ".join(GROUPS) + " |\n|---|---|---|---|---|" + "---|" * len(GROUPS))
    for _, r in top.iterrows():
        sub = R[(R.setup == r["setup"]) & (R.win == r["win"]) & (R.side == r["side"]) & (R["T"] == r["T"]) & (R["S"] == r["S"]) & (R.split == "hold")]
        g = sub.groupby("grp").agg(n=("n", "sum"), sn=("sum_net", "sum"))
        cells = [f"{g.loc[k, 'sn'] / g.loc[k, 'n'] * 1e4:.1f} ({int(g.loc[k, 'n'])})" if k in g.index and g.loc[k, "n"] else "-" for k in GROUPS]
        lines.append(f"| {r['setup']} | {r['win']} | {r['side']} | {r['T']} | {r['S']} | " + " | ".join(cells) + " |")
    (out / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
