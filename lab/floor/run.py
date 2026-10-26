"""Trading Floor day-trade lab: backtest the pre-registered desks (strategies/daytrade/spec.md).

  python -m lab.floor.run --out out/floor --archive backtests/data/etf1m   # real Yahoo data
  python -m lab.floor.run --out out/test --synthetic                        # offline smoke test

Outputs (in --out): results.json, REPORT.md, trades_1m.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from strategies.daytrade.core import COMPARISON_RULES, PAPER_RULES, SYMBOLS, TARGET_PCT, Bar

from .engine import desk_metrics, simulate

NY = ZoneInfo("America/New_York")


def synthetic_1m(seed: int = 3, days: int = 25) -> dict[str, list[Bar]]:
    rng = random.Random(seed)
    out = {}
    start = datetime(2026, 9, 1, 9, 30, tzinfo=NY)
    for k, sym in enumerate(SYMBOLS):
        lev = 3 if sym not in ("SPY", "QQQ") else 1
        sign = -1 if sym in ("SQQQ", "SPXU") else 1
        px, bars, d = 100.0 + k, [], start
        for _ in range(days):
            while d.weekday() >= 5:
                d += timedelta(days=1)
            drift = rng.gauss(0, 0.0004) * sign
            for m in range(390):
                t = d + timedelta(minutes=m)
                r = (drift + rng.gauss(0, 0.0006)) * lev
                o, c = px, px * (1 + r)
                spike = rng.random() < 0.01
                v = (5000 if m < 30 or m > 370 else 2000) * (8 if spike else 1) * (1 + rng.random())
                bars.append(Bar(t, o, max(o, c) * 1.0003, min(o, c) * 0.9997, c, v))
                px = c
            d = d + timedelta(days=1)
        out[sym] = bars
    return out


def resample(bars: list[Bar], minutes: int) -> list[Bar]:
    out, cur = [], []
    for b in bars:
        m = b.t.hour * 60 + b.t.minute - 570
        if cur and (b.t.date() != cur[0].t.date() or m // minutes != (cur[0].t.hour * 60 + cur[0].t.minute - 570) // minutes):
            out.append(Bar(cur[0].t, cur[0].o, max(x.h for x in cur), min(x.l for x in cur), cur[-1].c, sum(x.v for x in cur)))
            cur = []
        cur.append(b)
    if cur:
        out.append(Bar(cur[0].t, cur[0].o, max(x.h for x in cur), min(x.l for x in cur), cur[-1].c, sum(x.v for x in cur)))
    return out


def base_rates(daily: dict[str, list[tuple]]) -> dict:
    """How often each ETF traded +5% above its open (and -2.5% below it) within one day."""
    out = {}
    for sym, rows in daily.items():
        if not rows:
            continue
        n = len(rows)
        up = sum(1 for _, o, h, l, c in rows if h / o - 1 >= TARGET_PCT)
        dn = sum(1 for _, o, h, l, c in rows if l / o - 1 <= -0.025)
        both = sum(1 for _, o, h, l, c in rows if h / o - 1 >= TARGET_PCT and l / o - 1 <= -0.025)
        close5 = sum(1 for _, o, h, l, c in rows if c / o - 1 >= TARGET_PCT)
        out[sym] = {"from": rows[0][0], "to": rows[-1][0], "days": n,
                    "pct_days_high_5pct_above_open": round(up / n * 100, 2),
                    "pct_days_low_2_5pct_below_open": round(dn / n * 100, 2),
                    "pct_days_both": round(both / n * 100, 2),
                    "pct_days_close_5pct_above_open": round(close5 / n * 100, 2)}
    return out


def run_set(bars: dict, bar_minutes: int, slip_mult: float = 1.0) -> dict:
    res = simulate(bars, PAPER_RULES + COMPARISON_RULES, bar_minutes=bar_minutes, slip_mult=slip_mult)
    return {"sessions": res["sessions"], "first_day": res["first_day"], "last_day": res["last_day"],
            "benchmark_pct": res["benchmark_pct"],
            "desks": [desk_metrics(d, res["eod_equity"][d.key]) for d in res["desks"]],
            "_desks": res["desks"]}


def verdict(m: dict) -> str:
    if m["trades"] < 10:
        return "too few trades to judge"
    if m["expectancy_pct"] <= 0 or m["profit_factor"] < 1.2:
        return "loses or too thin after costs"
    return "promising, keep collecting"


def report(results: dict) -> str:
    L = []
    main = results["main_1m"]
    L.append("# Trading Floor day-trade lab")
    L.append("")
    L.append(f"Run {results['run_at']} · data: {results['data_source']} · spec: `strategies/daytrade/spec.md` (pre-registered)")
    L.append("")
    L.append(f"**1-minute backtest window:** {main['first_day']} to {main['last_day']}, {main['sessions']} trading sessions after a 3-session warm-up. "
             "Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.")
    L.append("")
    L.append("## Results: 1-minute bars (normal slippage)")
    L.append("")
    L.append("| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    paper = {r.key for r in PAPER_RULES}
    for m in main["desks"]:
        L.append(f"| {m['label']} | {'yes' if m['desk'] in paper else 'compare'} | {m['trades']} | {m['win_rate_pct']}% | {m['avg_win_pct']}% | {m['avg_loss_pct']}% | "
                 f"{m['expectancy_pct']}% | {m['profit_factor']} | {m['total_return_pct']}% | {m['max_dd_pct']}% | {m['targets_hit']} | {verdict(m)} |")
    L.append("")
    L.append("Buy-and-hold over the same window: " + ", ".join(f"{s} {v:+.2f}%" for s, v in main["benchmark_pct"].items()))
    L.append("")
    L.append("## Same rules, 3x slippage (stress test)")
    L.append("")
    L.append("| Desk | Trades | Expectancy / trade | Total return |")
    L.append("|---|---|---|---|")
    for m in results["stress_1m"]["desks"]:
        L.append(f"| {m['label']} | {m['trades']} | {m['expectancy_pct']}% | {m['total_return_pct']}% |")
    L.append("")
    if results.get("check_5m"):
        c5 = results["check_5m"]
        L.append(f"## Robustness check: 5-minute bars, {c5['first_day']} to {c5['last_day']} ({c5['sessions']} sessions)")
        L.append("")
        L.append("| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |")
        L.append("|---|---|---|---|---|---|---|")
        for m in c5["desks"]:
            L.append(f"| {m['label']} | {m['trades']} | {m['win_rate_pct']}% | {m['expectancy_pct']}% | {m['profit_factor']} | {m['total_return_pct']}% | {m['max_dd_pct']}% |")
        L.append("")
    br = results.get("base_rates") or {}
    if br:
        L.append("## How realistic is +5% in one day? (daily bars since 2010)")
        L.append("")
        L.append("| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |")
        L.append("|---|---|---|---|---|---|")
        for s, b in br.items():
            L.append(f"| {s} | {b['days']} | {b['pct_days_high_5pct_above_open']}% | {b['pct_days_low_2_5pct_below_open']}% | {b['pct_days_both']}% | {b['pct_days_close_5pct_above_open']}% |")
        L.append("")
    L.append("## Per-ETF breakdown (1-minute, paper desks)")
    L.append("")
    for m in main["desks"]:
        if m["desk"] in paper and m["by_symbol"]:
            L.append(f"- **{m['label']}:** " + "; ".join(f"{s} {v['trades']} trades, ${v['pnl_usd']:+.2f}" for s, v in m["by_symbol"].items())
                     + f" · exits {m['exits']}")
    L.append("")
    L.append("## How to read this")
    L.append("- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. "
             "The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.")
    L.append("- Paper trading runs these exact desks (same code) on live bars, whatever this report says.")
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--archive", default="backtests/data/etf1m")
    ap.add_argument("--synthetic", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    results: dict = {"run_at": datetime.now(timezone.utc).isoformat(timespec="minutes")}
    if a.synthetic:
        b1 = synthetic_1m()
        b5 = {s: resample(v, 5) for s, v in b1.items()}
        daily = {}
        results["data_source"] = "SYNTHETIC (offline test)"
    else:
        from . import data as D
        b1, b5, daily = {}, {}, {}
        for s in SYMBOLS:
            b1[s] = D.load_1m(s, Path(a.archive))
            b5[s] = D.fetch_intraday(s, "5m", 59)
            daily[s] = D.fetch_daily(s)
        results["data_source"] = "Yahoo Finance 1m (archived), 5m, 1d"
        results["bars_1m"] = {s: len(v) for s, v in b1.items()}
    main_1m = run_set(b1, 1)
    stress = run_set(b1, 1, slip_mult=3.0)
    check5 = run_set(b5, 5)
    with open(out / "trades_1m.csv", "w", newline="") as f:
        w = None
        for d in main_1m["_desks"]:
            for t in d.trades:
                if w is None:
                    w = csv.DictWriter(f, fieldnames=list(t.keys()))
                    w.writeheader()
                w.writerow(t)
    for r in (main_1m, stress, check5):
        r.pop("_desks")
    results.update(main_1m=main_1m, stress_1m=stress, check_5m=check5, base_rates=base_rates(daily))
    (out / "results.json").write_text(json.dumps(results, indent=1, default=str))
    (out / "REPORT.md").write_text(report(results))
    print(report(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
