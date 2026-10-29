"""Entry-quality study, part 2: analysis of research/entries/signals.csv.gz (pre-registered: PREREG.md).

  python -m lab.floor.entry_analysis --signals research/entries/signals.csv.gz --out research/entries
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from .entry_lab import FEATURES, emulate

TRAIN_END, VAL_END = "2026-10-15", "2026-10-22"
RULES = ["orb_vol", "ema_vol", "ema_vol_v2", "volspike", "cvd_spy", "cvd_tqqq"]
RNG = np.random.default_rng(17)


def split(day: str) -> str:
    return "train" if day <= TRAIN_END else ("val" if day <= VAL_END else "test")


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    m = ~(np.isnan(x) | np.isnan(y))
    if m.sum() < 8:
        return np.nan
    a, b = rankdata(x[m]), rankdata(y[m])
    if a.std() == 0 or b.std() == 0:
        return np.nan
    return float(np.corrcoef(a, b)[0, 1])


def boot_rho(df: pd.DataFrame, feat: str, out: str, iters: int = 300) -> tuple[float, float, float]:
    days = df["day"].unique()
    groups = {d: g for d, g in df.groupby("day")}
    rho = spearman(df[feat].to_numpy(float), df[out].to_numpy(float))
    stats = []
    for _ in range(iters):
        pick = RNG.choice(days, len(days))
        g = pd.concat([groups[d] for d in pick])
        stats.append(spearman(g[feat].to_numpy(float), g[out].to_numpy(float)))
    s = np.array([v for v in stats if not np.isnan(v)])
    if not len(s):
        return rho, np.nan, np.nan
    return rho, float(np.percentile(s, 5)), float(np.percentile(s, 95))


def within_rule_pct(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Percentile rank within each rule (pooling rules without mixing their scales)."""
    out = df.copy()
    for c in cols:
        out[c] = df.groupby("rule")[c].rank(pct=True)
    return out


# ------------------------------------------------------------------ metrics
def trade_metrics(tr: pd.DataFrame, col: str = "ret", n_days: int | None = None) -> dict:
    if not len(tr):
        return {"n": 0}
    r = tr.sort_values("t")[col].to_numpy(float)
    wins, losses = r[r > 0], r[r <= 0]
    pf = wins.sum() / -losses.sum() if losses.sum() < 0 else (99.0 if len(wins) else 0.0)
    eq = np.cumprod(1 + r / 100)
    dd = (eq / np.maximum.accumulate(np.concatenate([[1.0], eq]))[1:] - 1).min()
    return {"n": int(len(r)), "per_day": round(len(r) / n_days, 2) if n_days else None,
            "win_rate": round(float((r > 0).mean() * 100), 1),
            "avg_win": round(float(wins.mean()), 3) if len(wins) else 0.0,
            "avg_loss": round(float(losses.mean()), 3) if len(losses) else 0.0,
            "expectancy": round(float(r.mean()), 3), "pf": round(float(min(pf, 99)), 2),
            "total_return": round(float((eq[-1] - 1) * 100), 2), "max_dd": round(float(min(dd, 0) * 100), 2),
            "mfe": round(float(tr["mfe_close"].mean()), 3), "mae": round(float(tr["mae_close"].mean()), 3)}


def day_boot_mean(df: pd.DataFrame, col: str, iters: int = 2000) -> tuple[float, float, float]:
    if not len(df):
        return (np.nan, np.nan, np.nan)
    g = df.groupby("day")[col].agg(["sum", "count"])
    s, c = g["sum"].to_numpy(), g["count"].to_numpy()
    idx = RNG.integers(0, len(g), (iters, len(g)))
    m = s[idx].sum(1) / c[idx].sum(1)
    return float(s.sum() / c.sum()), float(np.percentile(m, 5)), float(np.percentile(m, 95))


# ------------------------------------------------------------------ regimes (causal, instrument's view)
def regimes(df: pd.DataFrame) -> pd.DataFrame:
    sign = df["sym"].map({"SPY": 1, "UPRO": 1, "SPXU": -1, "QQQ": 1, "TQQQ": 1, "SQQQ": -1})
    atrd = df["idx_day_range_avg"]
    so, s30 = sign * df["idx_ret_open"], sign * df["idx_ret30"]
    trend = np.where((so >= 0.35 * atrd) & (s30 > 0), "strong_bull",
             np.where((so <= -0.35 * atrd) & (s30 < 0), "strong_bear",
              np.where((so.abs() < 0.15 * atrd) & (s30.abs() < 0.10 * atrd), "sideways", "mixed")))
    vol = np.where(df["idx_range_ratio"] >= 1.25, "high_vol", np.where(df["idx_range_ratio"] <= 0.8, "low_vol", "normal_vol"))
    at_high = np.where(sign > 0, df["idx_dist_hod"] <= 0.05, df["idx_dist_lod"] <= 0.05)
    reversal = (np.sign(s30) != np.sign(so)) & (s30.abs() >= 0.10 * atrd)
    struct = np.where(at_high, "breakout", np.where(reversal, "reversal", "neither"))
    out = df.copy()
    out["reg_trend"], out["reg_vol"], out["reg_struct"] = trend, vol, struct
    return out


# ------------------------------------------------------------------ score
class Score:
    def __init__(self, train: pd.DataFrame, feats: list[str], min_rho: float = 0.05, drop: str | None = None):
        self.maps = {}
        for rule, g in train.groupby("rule"):
            self.maps[rule] = {f: np.sort(g[f].dropna().to_numpy(float)) for f in feats}
        pt = self.pct(train, feats)
        y = train.groupby("rule")["ret"].rank(pct=True).to_numpy(float)
        self.rho = {f: spearman(pt[f].to_numpy(float), y) for f in feats}
        self.w = {f: float(np.sign(r)) for f, r in self.rho.items() if not np.isnan(r) and abs(r) >= min_rho and f != drop}
        s = self.raw(train)
        self.cuts = (float(np.nanpercentile(s, 33.3)), float(np.nanpercentile(s, 66.7)))

    def pct(self, df: pd.DataFrame, feats: list[str]) -> pd.DataFrame:
        out = pd.DataFrame(index=df.index)
        for f in feats:
            vals = np.full(len(df), np.nan)
            for rule, idx in df.groupby("rule").groups.items():
                arr = self.maps.get(rule, {}).get(f)
                if arr is None or not len(arr):
                    continue
                x = df.loc[idx, f].to_numpy(float)
                p = np.searchsorted(arr, x, side="right") / len(arr)
                p[np.isnan(x)] = np.nan
                vals[df.index.get_indexer(idx)] = p
            out[f] = vals
        return out

    def raw(self, df: pd.DataFrame) -> np.ndarray:
        if not self.w:
            return np.zeros(len(df))
        p = self.pct(df, list(self.w))
        s = sum(self.w[f] * (p[f].fillna(0.5) - 0.5) for f in self.w)
        return (s / len(self.w)).to_numpy(float)

    def tercile(self, df: pd.DataFrame) -> np.ndarray:
        s = self.raw(df)
        return np.where(s <= self.cuts[0], "low", np.where(s <= self.cuts[1], "mid", "high"))


# ------------------------------------------------------------------ filters
def make_filters(train: pd.DataFrame) -> dict:
    brk_med = {r: float(g["brk_atr"].median()) for r, g in train.groupby("rule")}
    F = {
        "rvol>1": lambda r: r["rvol_cum"] > 1,
        "cvd_slope15>0": lambda r: r["cvd_slope15"] > 0,
        "above_vwap": lambda r: r["vwap_atr"] > 0,
        "ema_aligned": lambda r: r["ema_align"] == 1,
        "market_confirm": lambda r: r["mkt_open"] > 0,
        "trend30>0": lambda r: r["ret30_atr"] > 0,
        "range_ratio>=1": lambda r: r["range_ratio"] >= 1,
        "before_11:30": lambda r: r["minute"] < 120,
        "breakout>train_median": lambda r: r["brk_atr"] > brk_med.get(r["rule"], 0),
        "cvd+rvol": lambda r: r["cvd_slope15"] > 0 and r["rvol_cum"] > 1,
        "cvd+vwap": lambda r: r["cvd_slope15"] > 0 and r["vwap_atr"] > 0,
        "ema_align+market": lambda r: r["ema_align"] == 1 and r["mkt_open"] > 0,
        "rvol(orb+volume)": lambda r: r["rvol_cum"] > 1,
        "range_ratio+vol_exp": lambda r: r["range_ratio"] >= 1 and r["vol_exp5"] > 1,
    }
    return F


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--signals", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    df = pd.read_csv(a.signals)
    df = df[df["valid"] == 1].copy()
    df["split"] = df["day"].map(split)
    df = regimes(df)
    res: dict = {"counts": df.groupby(["rule", "split"]).size().unstack(fill_value=0).to_dict(orient="index"),
                 "days": {s: sorted(df.loc[df.split == s, "day"].unique().tolist()) for s in ("train", "val", "test")}}
    tr, ho = df[df.split == "train"], df[df.split != "train"]

    # ---------------- Phase 1: feature vs outcome
    p1 = {}
    groups = {**{r: (tr[tr.rule == r], ho[ho.rule == r]) for r in RULES}}
    ptr, pho = within_rule_pct(tr, FEATURES + ["ret", "fwd60", "mfe60", "mae60"]), within_rule_pct(ho, FEATURES + ["ret", "fwd60", "mfe60", "mae60"])
    groups["ALL"] = (ptr, pho)
    for g, (a_tr, a_ho) in groups.items():
        p1[g] = {}
        for f in FEATURES:
            rt, lo, hi = boot_rho(a_tr, f, "ret")
            rh, lo2, hi2 = boot_rho(a_ho, f, "ret")
            p1[g][f] = {"train": [round(rt, 3), round(lo, 3), round(hi, 3)], "holdout": [round(rh, 3), round(lo2, 3), round(hi2, 3)],
                        "train_fwd60": round(spearman(a_tr[f].to_numpy(float), a_tr["fwd60"].to_numpy(float)), 3),
                        "train_mfe60": round(spearman(a_tr[f].to_numpy(float), a_tr["mfe60"].to_numpy(float)), 3),
                        "train_mae60": round(spearman(a_tr[f].to_numpy(float), a_tr["mae60"].to_numpy(float)), 3),
                        "hold_mfe60": round(spearman(a_ho[f].to_numpy(float), a_ho["mfe60"].to_numpy(float)), 3)}
    res["phase1"] = p1

    # ---------------- Phase 2: regimes (all days, descriptive) + split check
    p2 = {}
    for dim in ("reg_trend", "reg_vol", "reg_struct"):
        p2[dim] = {}
        for (rule, lab), g in df.groupby(["rule", dim]):
            desk = pd.DataFrame(emulate(g.to_dict("records")))
            p2[dim].setdefault(rule, {})[lab] = {
                "signals": int(len(g)), "days": int(g.day.nunique()), "mean_ret": round(float(g.ret.mean()), 3),
                "pf": trade_metrics(g)["pf"], "mean_mfe60": round(float(g.mfe60.mean()), 3),
                "train_mean": round(float(g[g.split == "train"].ret.mean()), 3) if (g.split == "train").any() else None,
                "holdout_mean": round(float(g[g.split != "train"].ret.mean()), 3) if (g.split != "train").any() else None,
                "first_of_day_trades": int(len(desk))}
    res["phase2"] = p2

    # ---------------- Phase 3: score (fit on train), shadow evaluation
    sc = Score(tr, FEATURES)
    res["score"] = {"weights": sc.w, "train_rho": {f: round(v, 3) for f, v in sc.rho.items()}, "cuts": sc.cuts}
    df["tercile"] = sc.tercile(df)
    df["score"] = sc.raw(df)
    p3 = {}
    for s in ("train", "val", "test"):
        g = df[df.split == s]
        p3[s] = {t: {"n": int(len(x)), "mean_ret": round(float(x.ret.mean()), 3), "pf": trade_metrics(x)["pf"],
                     "mfe60": round(float(x.mfe60.mean()), 3), "mae60": round(float(x.mae60.mean()), 3),
                     "fwd60": round(float(x.fwd60.mean()), 3)} for t, x in g.groupby("tercile")}
        hi, lo = g[g.tercile == "high"], g[g.tercile == "low"]
        dd = pd.concat([hi.assign(v=hi.ret), lo.assign(v=-lo.ret)])
        p3[s]["score_rho"] = round(spearman(g.score.to_numpy(float), g.ret.to_numpy(float)), 3)
        p3[s]["high_ci"] = [round(v, 3) for v in day_boot_mean(hi, "ret")]
        p3[s]["low_ci"] = [round(v, 3) for v in day_boot_mean(lo, "ret")]
    # per rule, held-out
    p3["per_rule_holdout"] = {r: {t: {"n": int(len(x)), "mean_ret": round(float(x.ret.mean()), 3)}
                                  for t, x in df[(df.split != "train") & (df.rule == r)].groupby("tercile")} for r in RULES}
    # expanding walk-forward from the first validation day
    days = sorted(df.day.unique())
    wf_rows = []
    for d in [x for x in days if x > TRAIN_END]:
        s_k = Score(df[df.day < d], FEATURES)
        g = df[df.day == d].copy()
        g["wf_ter"] = s_k.tercile(g)
        wf_rows.append(g)
    wf = pd.concat(wf_rows)
    p3["walk_forward"] = {t: {"n": int(len(x)), "mean_ret": round(float(x.ret.mean()), 3),
                              "ci": [round(v, 3) for v in day_boot_mean(x, "ret")]} for t, x in wf.groupby("wf_ter")}
    p3["walk_forward"]["all"] = {"n": int(len(wf)), "mean_ret": round(float(wf.ret.mean()), 3)}
    # ablation on validation
    ab = {}
    base_val = df[df.split == "val"]
    full_hi = float(base_val[base_val.tercile == "high"].ret.mean())
    for f in list(sc.w):
        s2 = Score(tr, FEATURES, drop=f)
        t2 = s2.tercile(base_val)
        hi2 = float(base_val[t2 == "high"].ret.mean())
        lo2 = float(base_val[t2 == "low"].ret.mean())
        ab[f] = {"val_high_mean_without": round(hi2, 3), "val_spread_without": round(hi2 - lo2, 3),
                 "change_vs_full_high": round(hi2 - full_hi, 3)}
    p3["ablation_val"] = {"full_high": round(full_hi, 3),
                          "full_spread": round(full_hi - float(base_val[base_val.tercile == "low"].ret.mean()), 3), "drop": ab}
    res["phase3"] = p3

    # ---------------- Phase 4: filters via desk emulation
    F = make_filters(tr)
    F["score_top_tercile"] = None
    recs = df.to_dict("records")
    n_days = {s: len(res["days"][s]) for s in ("train", "val", "test")}
    p4 = {}
    for rule in RULES:
        rr = [r for r in recs if r["rule"] == rule]
        base = pd.DataFrame(emulate(rr))
        p4[rule] = {"BASE": {s: trade_metrics(base[base.split == s], n_days=n_days[s]) for s in n_days}}
        for name, fn in F.items():
            keep = (lambda r: r["tercile"] == "high") if fn is None else (lambda r, fn=fn: bool(fn(r)))
            t = pd.DataFrame(emulate(rr, keep))
            if not len(t):
                p4[rule][name] = {s: {"n": 0} for s in n_days}
                continue
            p4[rule][name] = {s: trade_metrics(t[t.split == s], n_days=n_days[s]) for s in n_days}
            sig = [r for r in rr if keep(r)]
            p4[rule][name]["signal_level"] = {s: round(float(np.mean([r["ret"] for r in sig if r["split"] == s])), 3)
                                              if any(r["split"] == s for r in sig) else None for s in n_days}
        p4[rule]["BASE"]["signal_level"] = {s: round(float(np.mean([r["ret"] for r in rr if r["split"] == s])), 3) for s in n_days}
    # candidates: beat BASE on train AND val, >=5 trades in each
    cands = []
    for rule, d in p4.items():
        b = d["BASE"]
        for name, m in d.items():
            if name == "BASE":
                continue
            ok = all(m[s].get("n", 0) >= 5 and b[s].get("n", 0) and m[s]["expectancy"] > b[s]["expectancy"] for s in ("train", "val"))
            if ok:
                cands.append((rule, name))
    res["phase4"] = p4
    res["candidates"] = cands

    # ---------------- Phase 5: test comparison for candidates (+ regime breakdown, 2x costs)
    p5 = {}
    for rule, name in cands:
        rr = [r for r in recs if r["rule"] == rule]
        fn = F[name]
        keep = (lambda r: r["tercile"] == "high") if fn is None else (lambda r, fn=fn: bool(fn(r)))
        base = pd.DataFrame(emulate(rr))
        t = pd.DataFrame(emulate(rr, keep))
        bt, tt = base[base.split == "test"], t[t.split == "test"]
        # per-day P&L difference over test days (0 when no trade)
        tdays = res["days"]["test"]
        pb = bt.set_index("day")["ret"].reindex(tdays).fillna(0.0)
        pc = tt.set_index("day")["ret"].reindex(tdays).fillna(0.0) if len(tt) else pd.Series(0.0, index=tdays)
        diff = (pc - pb).to_numpy()
        boots = [float(diff[RNG.integers(0, len(diff), len(diff))].mean()) for _ in range(2000)]
        p5[f"{rule} | {name}"] = {
            "test_base": trade_metrics(bt, n_days=len(tdays)), "test_filtered": trade_metrics(tt, n_days=len(tdays)),
            "test_base_2x": trade_metrics(bt, "ret_2x"), "test_filtered_2x": trade_metrics(tt, "ret_2x"),
            "daily_pnl_diff_mean": round(float(diff.mean()), 3),
            "daily_pnl_diff_ci90": [round(float(np.percentile(boots, 5)), 3), round(float(np.percentile(boots, 95)), 3)],
            "test_by_trend": {k: round(float(x.ret.mean()), 3) for k, x in tt.groupby("reg_trend")} if len(tt) else {},
        }
    res["phase5"] = p5
    (out / "analysis.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({"candidates": cands, "score_weights": sc.w}, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
