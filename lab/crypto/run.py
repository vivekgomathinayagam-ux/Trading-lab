"""Run the Crypto Pier backtest suite and write results.

  python -m lab.crypto.run --out out/crypto            # real Coinbase data
  python -m lab.crypto.run --out out/test --synthetic  # offline smoke test

Outputs (in --out): results.json, REPORT.md, equity_daily.csv, trades_main.csv
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from . import data as D
from .engine import Costs, metrics, run as run_bt
from .strategies import CONTROL, MAIN, VARIANTS, PATTERNS_MAIN, PATTERNS_VARIANTS, Spec

ASSETS = ["BTC-USD", "ETH-USD"]
START = D.utc(2017, 1, 1)
TRAIN_END = pd.Timestamp("2022-01-01", tz="UTC")       # walk-forward split
PERIODS = [("2017-2019", "2017-01-01", "2020-01-01"),
           ("2020-2022", "2020-01-01", "2023-01-01"),
           ("2023-now", "2023-01-01", "2100-01-01")]
COSTS = {
    "gross": Costs(0.0, 0.0005),          # slippage only: is there any edge before fees?
    "mid": Costs(0.0040, 0.0005),         # assumed cheaper exchange taker fee
    "robinhood": Costs(0.0095, 0.0005),   # Robinhood API entry tier: taker rate up to 0.95%
}
SIZINGS = {"full": None, "risk5": 0.05, "risk2": 0.02}  # risk = max loss at the stop, share of equity
HEADLINE_COST, HEADLINE_SIZING = "robinhood", "risk5"


def synthetic(seed: int = 7) -> dict:
    """Random-walk hourly bars with alternating regimes, for offline tests only."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2017-01-01", "2026-10-20", freq="1h", tz="UTC")
    n = len(idx)
    drift = np.repeat(rng.choice([-0.00015, 0.0, 0.0002], size=n // 2000 + 1), 2000)[:n]
    r = drift + rng.standard_normal(n) * 0.008
    c = 1000 * np.exp(np.cumsum(r))
    o = np.r_[c[0], c[:-1]]
    w = np.abs(rng.standard_normal(n)) * 0.004
    df = pd.DataFrame({"open": o, "high": np.maximum(o, c) * (1 + w), "low": np.minimum(o, c) * (1 - w),
                       "close": c, "volume": 1.0}, index=idx)
    return {"1h": df, "1d": D.resample(df, "1D", 20)}


def load_asset(product: str, cache: Path, end: datetime) -> dict:
    h = D.load_or_fetch(cache, product, 3600, START, end)
    d = D.load_or_fetch(cache, product, 86400, START, end)
    return {"1h": h, "1d": d}


def bars_for(spec: Spec, bundle: dict) -> pd.DataFrame:
    if spec.timeframe == "4h":
        return D.resample(bundle["1h"], "4h", 3)
    return bundle[spec.timeframe]


def quality(bundle: dict) -> dict:
    out = {}
    for tf, df in bundle.items():
        step = pd.Timedelta("1h" if tf == "1h" else "1D")
        expected = int((df.index[-1] - df.index[0]) / step) + 1
        moves = (df["close"].pct_change().abs() * 100).dropna()
        # flash-crash wicks: the low is less than half of both the open and the close
        body_lo = df[["open", "close"]].min(axis=1)
        wicks = df.index[df["low"] < 0.5 * body_lo]
        out[tf] = {"bars": len(df), "first": str(df.index[0]), "last": str(df.index[-1]),
                   "missing_pct": round((1 - len(df) / expected) * 100, 2),
                   "largest_bar_move_pct": round(float(moves.max()), 1),
                   "flash_crash_bars": [str(t) for t in wicks[:10]]}
    return out


def slice_metrics(res, start: str, end: str) -> dict:
    s, e = pd.Timestamp(start, tz="UTC"), pd.Timestamp(end, tz="UTC")
    eq = res.equity[(res.equity.index >= s) & (res.equity.index < e)]
    if len(eq) < 30:
        return {}
    sub = type(res)(eq, [t for t in res.trades if s <= t.entry_time < e], 0.0, 0)
    m = metrics(sub, len(eq))
    return {k: m[k] for k in ("cagr_pct", "max_dd_pct", "sharpe", "trades", "expectancy_pct",
                              "profit_factor") if k in m}


def evaluate(spec: Spec, product: str, bundle: dict) -> list[dict]:
    df = bars_for(spec, bundle)
    sig = spec.builder(df, bundle["1d"], **spec.params)
    rows = []
    sizings = ["full"] if spec.style == "control" else list(SIZINGS)
    for cname, cost in COSTS.items():
        for sizing in sizings:
            cap = SIZINGS[sizing]
            res = run_bt(df, sig, cost, sizing="risk" if cap else "full", risk_cap=cap or 0.05)
            m = metrics(res, len(df))
            fracs = [t.frac for t in res.trades]
            row = {"asset": product, "strategy": spec.key, "name": spec.name, "style": spec.style,
                   "timeframe": spec.timeframe, "main": spec.main, "cost": cname, "sizing": sizing,
                   **m, "avg_exposure_frac": round(float(np.mean(fracs)), 3) if fracs else 0.0,
                   "periods": {p: slice_metrics(res, a, b) for p, a, b in PERIODS},
                   "train": slice_metrics(res, "2017-01-01", "2022-01-01"),
                   "test": slice_metrics(res, "2022-01-01", "2100-01-01")}
            row["_res"] = res
            rows.append(row)
    return rows


def breakeven_fee(gross_row: dict) -> float | None:
    """Approximate per-side fee at which average trade P&L reaches zero."""
    if not gross_row.get("trades") or not gross_row.get("avg_exposure_frac"):
        return None
    per_trade = gross_row["expectancy_pct"] / 100.0
    return round(max(per_trade / (2 * gross_row["avg_exposure_frac"]), 0.0) * 100, 3)


def screen(row: dict, bh_sharpe: float) -> tuple[bool, list[str]]:
    why = []
    if row.get("trades", 0) < 30:
        why.append(f"only {row.get('trades', 0)} trades (<30)")
    if row.get("expectancy_pct", 0) <= 0:
        why.append("expectancy <= 0 after costs")
    if row.get("profit_factor", 0) < 1.2:
        why.append(f"profit factor {row.get('profit_factor')} < 1.2")
    if row.get("max_dd_pct", -100) < -20:
        why.append(f"max drawdown {row.get('max_dd_pct')}% worse than -20%")
    if row.get("sharpe", 0) <= bh_sharpe:
        why.append(f"Sharpe {row.get('sharpe')} not above buy-and-hold {bh_sharpe}")
    pos = sum(1 for p in row["periods"].values() if p and p.get("cagr_pct", -1) > 0)
    if pos < 2:
        why.append(f"positive in only {pos} of 3 periods")
    if not row["test"] or row["test"].get("sharpe", 0) <= 0:
        why.append("not positive out-of-sample (2022+)")
    return (not why), why


def walk_forward(rows: list[dict]) -> list[dict]:
    """For each asset and strategy family: pick the variant with the best TRAIN
    Sharpe (headline costs/sizing), then show what it did in the TEST years."""
    out = []
    pool = [r for r in rows if r["cost"] == HEADLINE_COST and r["sizing"] == HEADLINE_SIZING]
    for asset in ASSETS:
        for fam in sorted({r["strategy"] for r in pool}):
            cands = [r for r in pool if r["asset"] == asset and r["strategy"] == fam and r["train"]]
            if not cands:
                continue
            best = max(cands, key=lambda r: r["train"].get("sharpe", -9))
            main = next((r for r in cands if r["main"]), None)
            out.append({"asset": asset, "family": fam, "picked": best["name"],
                        "train_sharpe": best["train"].get("sharpe"),
                        "test_sharpe": best["test"].get("sharpe") if best["test"] else None,
                        "test_cagr_pct": best["test"].get("cagr_pct") if best["test"] else None,
                        "main_test_sharpe": main["test"].get("sharpe") if main and main["test"] else None,
                        "variants_compared": len(cands)})
    return out


def fmt(v, suf=""):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "–"
    return f"{v}{suf}"


def write_report(out: Path, meta: dict, rows: list[dict], wf: list[dict], bh: dict) -> None:
    L = []
    L.append("# Crypto Pier — historical backtest report\n")
    L.append(f"_Generated {meta['generated']} UTC from {meta['source']}. "
             f"Data {meta['start']} to {meta['end']}._\n")
    if meta.get("synthetic"):
        L.append("> **SYNTHETIC DATA — pipeline test only. These numbers mean nothing.**\n")
    L.append("## How to read this\n")
    L.append("- Long-only spot BTC and ETH. No leverage, no shorting.")
    L.append("- Signals at a bar's close, fills at the next bar's open plus 0.05% slippage; stops fill at the stop or worse on a gap.")
    L.append("- **Headline = Robinhood costs (0.95% fee per side, its entry-tier taker rate for API orders) with 5%-risk sizing** (a stop hit loses at most ~5% of equity, money rule 5). 2%-risk sizing is shown too: same rules, smaller bets, smaller drawdowns.")
    L.append("- 'mid' assumes a 0.40% fee (cheaper exchange, assumption). 'gross' = slippage only, to see if any edge exists before fees.")
    L.append(f"- Parameters were fixed before running. {meta['variants_total']} parameter variants per asset were run in total "
             f"({meta['variants_main']} pre-registered + {meta['variants_extra']} sensitivity). Results from many variants overstate edge; "
             "the walk-forward table shows how picking the best backtest actually held up.")
    L.append("- The 'pattern' family (drop_bounce, momentum_burst, squeeze_breakout) are short-horizon (3-15 day) "
             "setups meant to map to a defined-risk long call/put on a crypto ETF, not the spot position actually "
             "simulated here. They do not model options theta, implied vol, or ETF tracking error — a pass here is "
             "a reason to size a real options trade carefully in paper, not evidence the options trade itself works.\n")

    L.append("## Data quality\n")
    L.append("| Asset | Timeframe | Bars | Missing | Largest 1-bar move | Flash-crash wicks (low < half the bar's body) |")
    L.append("|---|---|---|---|---|---|")
    for a, q in meta["quality"].items():
        for tf, d in q.items():
            fc = ", ".join(x[:10] for x in d.get("flash_crash_bars", [])) or "none"
            L.append(f"| {a} | {tf} | {d['bars']} | {d['missing_pct']}% | {d['largest_bar_move_pct']}% | {fc} |")
    L.append("")
    L.append("A flash-crash wick on one exchange can trigger a resting stop far below the real market (ETH on Coinbase's exchange, 21 June 2017, traded near $0.10 for a moment). The engine fills such stops at the stop price, as a real stop order on that venue could have, so these bars can cause large one-day losses. 'Worst day' in the screen shows it.\n")

    L.append("## Benchmarks (buy and hold, no costs after entry)\n")
    L.append("| Asset | CAGR | Max DD | Sharpe |")
    L.append("|---|---|---|---|")
    for a in ASSETS:
        b = bh[a]
        L.append(f"| {a} | {fmt(b.get('cagr_pct'), '%')} | {fmt(b.get('max_dd_pct'), '%')} | {fmt(b.get('sharpe'))} |")
    L.append("| Cash | 0% | 0% | 0 |\n")

    def table(title, cost, sizing):
        L.append(f"## {title}\n")
        L.append("| Asset | Strategy | Style | Trades | Win% | Exp/trade | PF | CAGR | Max DD | Sharpe | Exposure | Fees paid | 2017-19 | 2020-22 | 2023-now | Test Sharpe (2022+) |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for r in rows:
            if not (r["main"] and r["cost"] == cost and r["sizing"] == sizing and r["style"] != "control"):
                continue
            p = r["periods"]
            pc = [fmt(p[k].get("cagr_pct"), "%") if p.get(k) else "–" for k, _, _ in PERIODS]
            L.append(f"| {r['asset']} | {r['name']} | {r['style']} | {r['trades']} | {r['win_rate_pct']}% | "
                     f"{r['expectancy_pct']}% | {r['profit_factor']} | {r['cagr_pct']}% | {r['max_dd_pct']}% | "
                     f"{r['sharpe']} | {r['exposure_pct']}% | {r['fees_pct_of_start']}% | {pc[0]} | {pc[1]} | {pc[2]} | "
                     f"{fmt(r['test'].get('sharpe') if r['test'] else None)} |")
        L.append("")

    table("Headline: Robinhood fees, 5%-risk sizing (the rule maximum)", "robinhood", "risk5")
    table("Robinhood fees, 2%-risk sizing (same rules, smaller bets)", "robinhood", "risk2")
    table("Same rules at a 0.40% fee (assumed cheaper exchange), 5%-risk sizing", "mid", "risk5")
    table("Before fees (slippage only), 5%-risk sizing", "gross", "risk5")
    table("Robinhood fees, full sizing (ignores the 5% rule; for comparison)", "robinhood", "full")

    L.append("## Screen for paper trading (Robinhood costs; 5% and 2% risk sizing)\n")
    L.append("Pass = 30+ trades, positive expectancy after costs, profit factor 1.2+, max drawdown no worse than -20%, "
             "Sharpe above the same asset's buy-and-hold, positive in 2 of 3 periods, positive Sharpe in 2022+.\n")
    L.append("| Asset | Strategy | Sizing | Result | Why | Worst day | Approx. breakeven fee per side |")
    L.append("|---|---|---|---|---|---|---|")
    for r in rows:
        if r["main"] and r["cost"] == HEADLINE_COST and r["sizing"] in ("risk5", "risk2") and r["style"] != "control":
            L.append(f"| {r['asset']} | {r['name']} | {r['sizing']} | {'PASS' if r['screen_pass'] else 'fail'} | "
                     f"{'; '.join(r['screen_why']) or '–'} | {fmt(r.get('worst_day_pct'), '%')} | {fmt(r.get('breakeven_fee_pct'), '%')} |")
    L.append("")

    L.append("## Walk-forward check: pick the best variant on 2017-2021, then test 2022+\n")
    L.append("| Asset | Family | Picked on train | Train Sharpe | Test Sharpe | Test CAGR | Pre-registered main, test Sharpe | Variants compared |")
    L.append("|---|---|---|---|---|---|---|---|")
    for w in wf:
        L.append(f"| {w['asset']} | {w['family']} | {w['picked']} | {fmt(w['train_sharpe'])} | {fmt(w['test_sharpe'])} | "
                 f"{fmt(w['test_cagr_pct'], '%')} | {fmt(w['main_test_sharpe'])} | {w['variants_compared']} |")
    L.append("")
    L.append("## Caveats\n")
    L.append("- One exchange's history (Coinbase). Real fills on Robinhood can differ; paper trading measures that.")
    L.append("- Daily and 4h strategies can gap through stops overnight-style in crypto's 24/7 market; 'worst trade' shows the real damage.")
    L.append("- Sharpe uses daily returns x sqrt(365). Cash earns 0% here; stablecoin yield would help flat periods slightly.")
    L.append("- A backtest pass is a reason to paper trade, not to trade live.\n")
    (out / "REPORT.md").write_text("\n".join(L))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out/crypto")
    ap.add_argument("--cache", default="backtests/data/crypto")
    ap.add_argument("--synthetic", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    end = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    bundles = {}
    for p in ASSETS:
        bundles[p] = synthetic(seed=7 if p.startswith("BTC") else 11) if a.synthetic \
            else load_asset(p, Path(a.cache), end)
        print(f"{p}: 1h bars {len(bundles[p]['1h'])}, 1d bars {len(bundles[p]['1d'])}", flush=True)

    specs = MAIN + VARIANTS + PATTERNS_MAIN + PATTERNS_VARIANTS
    rows: list[dict] = []
    bh: dict = {}
    for p, b in bundles.items():
        ctrl = evaluate(CONTROL, p, b)
        rows += ctrl
        bh[p] = next(r for r in ctrl if r["cost"] == "robinhood")
        for s in specs:
            rows += evaluate(s, p, b)
            print(f"  done {p} {s.name}", flush=True)

    for r in rows:
        if r["style"] == "control":
            continue
        g = next(x for x in rows if x["asset"] == r["asset"] and x["name"] == r["name"]
                 and x["cost"] == "gross" and x["sizing"] == r["sizing"])
        r["breakeven_fee_pct"] = breakeven_fee(g)
        r["screen_pass"], r["screen_why"] = screen(r, bh[r["asset"]].get("sharpe", 0))
    wf = walk_forward([r for r in rows if r["style"] != "control"])

    # equity curves (headline) and trades, for the city and for review
    curves = {}
    trades = []
    for r in rows:
        keep = (r["main"] and r["cost"] == HEADLINE_COST and r["sizing"] in ("risk5", "risk2")) \
            or (r["style"] == "control" and r["cost"] == "robinhood")
        if keep:
            eq = r["_res"].equity.resample("1D").last().dropna()
            tag = "" if r["style"] == "control" else f"|{r['sizing']}"
            curves[f"{r['asset']}|{r['name']}{tag}"] = (eq / eq.iloc[0] * 100).round(2)
            if r["style"] != "control" and r["sizing"] == HEADLINE_SIZING:
                for t in r["_res"].trades:
                    trades.append({"asset": r["asset"], "strategy": r["name"], "entry": t.entry_time.isoformat(),
                                   "exit": t.exit_time.isoformat(), "entry_px": round(t.entry_px, 2),
                                   "exit_px": round(t.exit_px, 2), "frac": round(t.frac, 3),
                                   "pnl_pct": round(t.pnl_pct, 3),
                                   "r": round(t.r_mult, 3) if np.isfinite(t.r_mult) else None,
                                   "bars": t.bars, "reason": t.reason})
    pd.DataFrame(curves).to_csv(out / "equity_daily.csv")
    pd.DataFrame(trades).to_csv(out / "trades_main.csv", index=False)

    any_b = next(iter(bundles.values()))
    meta = {"generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
            "source": "SYNTHETIC random walk" if a.synthetic else "Coinbase Exchange public candles (1h, 1d)",
            "synthetic": a.synthetic, "start": str(any_b["1h"].index[0].date()),
            "end": str(any_b["1h"].index[-1].date()),
            "costs": {k: {"fee_per_side": v.fee, "slippage_per_side": v.slip} for k, v in COSTS.items()},
            "headline": {"cost": HEADLINE_COST, "sizing": HEADLINE_SIZING, "risk_cap": 0.05},
            "variants_main": len(MAIN) + len(PATTERNS_MAIN), "variants_extra": len(VARIANTS) + len(PATTERNS_VARIANTS),
            "variants_total": len(MAIN) + len(VARIANTS) + len(PATTERNS_MAIN) + len(PATTERNS_VARIANTS),
            "quality": {p: quality(b) for p, b in bundles.items()},
            "periods": PERIODS}
    clean_rows = [{k: v for k, v in r.items() if k != "_res"} for r in rows]
    (out / "results.json").write_text(json.dumps({"meta": meta, "rows": clean_rows, "walk_forward": wf},
                                                 indent=1, default=str))
    write_report(out, meta, rows, wf, bh)
    passed = [f"{r['asset']} {r['name']} [{r['sizing']}]" for r in rows
              if r.get("screen_pass") and r["main"] and r["cost"] == HEADLINE_COST and r["sizing"] in ("risk5", "risk2")]
    print("SCREEN PASS:", passed or "none", flush=True)


if __name__ == "__main__":
    main()
