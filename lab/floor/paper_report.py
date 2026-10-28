"""Weekly paper report: the statistics in research/CHARTER.md "Reading the paper data".

  python -m lab.floor.paper_report --trades ledger/daytrade_trades.csv --archive backtests/data/etf1m \
      [--since 2026-10-26] [--evaluation preliminary] [--out report.md] [--json report.json]

Reads the paper trade ledger (branch `data`) and, when given, the 1-minute archive for MAE/MFE,
day types and SPY comparison. Everything is computed here, never by hand.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, pstdev

from .data import NY, load_archive

MIN_N_FOR_LABEL = 10


# ---------------------------------------------------------------- inputs
def load_trades(path: Path, since: str | None = None) -> list[dict]:
    rows = []
    with Path(path).open(newline="") as f:
        for r in csv.DictReader(f):
            if since and r["entry_t"][:10] < since:
                continue
            for k in ("qty",):
                r[k] = int(float(r[k]))
            for k in ("entry_px", "exit_px", "pnl_usd", "pnl_pct_equity", "move_pct", "equity_after"):
                r[k] = float(r[k])
            r["day"] = r["entry_t"][:10]
            rows.append(r)
    rows.sort(key=lambda r: r["entry_t"])
    return rows


def load_bars(archive: Path | None, syms) -> dict:
    out = {}
    if not archive:
        return out
    for s in syms:
        p = Path(archive) / f"{s}.csv.gz"
        if p.exists():
            out[s] = load_archive(p)
    return out


# ---------------------------------------------------------------- stats
def bootstrap_ci(xs: list[float], n_boot: int = 5000, alpha: float = 0.05, seed: int = 7) -> tuple:
    if len(xs) < 2:
        return (math.nan, math.nan)
    rng = random.Random(seed)
    n = len(xs)
    ms = sorted(sum(rng.choice(xs) for _ in range(n)) / n for _ in range(n_boot))
    return (ms[int(alpha / 2 * n_boot)], ms[int((1 - alpha / 2) * n_boot) - 1])


def label(n: int, ci: tuple) -> str:
    if n < MIN_N_FOR_LABEL or any(math.isnan(c) for c in ci):
        return "too small to say"
    if ci[0] > 0:
        return "promising"
    if ci[1] < 0:
        return "failing"
    return "inconclusive"


def max_drawdown(curve: list[float]) -> float:
    peak, mdd = -1e18, 0.0
    for v in curve:
        peak = max(peak, v)
        mdd = min(mdd, v / peak - 1)
    return mdd * 100


def path_after_entry(tr: dict, bars: dict) -> dict | None:
    """MAE/MFE in % of entry from the archived minute bars between entry and exit."""
    b = bars.get(tr["sym"])
    if not b:
        return None
    t0 = datetime.fromisoformat(tr["entry_t"]).astimezone(NY).replace(second=0, microsecond=0)
    t1 = datetime.fromisoformat(tr["exit_t"]).astimezone(NY)
    seg = [x for k, x in b.items() if t0 <= k <= t1]
    if not seg:
        return None
    e = tr["entry_px"]
    return {"mae_pct": round((min(x.l for x in seg) / e - 1) * 100, 3),
            "mfe_pct": round((max(x.h for x in seg) / e - 1) * 100, 3), "bars": len(seg)}


def day_table(bars: dict) -> dict:
    """Per day: SPY open->close %, gap %, prior-day range %, built from the archive."""
    spy = bars.get("SPY") or {}
    byday = defaultdict(list)
    for k in sorted(spy):
        byday[k.date().isoformat()].append(spy[k])
    out, prev = {}, None
    for d in sorted(byday):
        xs = byday[d]
        o, c = xs[0].o, xs[-1].c
        h, l = max(x.h for x in xs), min(x.l for x in xs)
        row = {"spy_oc_pct": round((c / o - 1) * 100, 3), "range_pct": round((h / l - 1) * 100, 3)}
        if prev:
            row["gap_pct"] = round((o / prev["c"] - 1) * 100, 3)
            row["prior_range_pct"] = prev["range_pct"]
        out[d] = row
        prev = {"c": c, "range_pct": row["range_pct"]}
    return out


def tod_bucket(entry_t: str) -> str:
    t = datetime.fromisoformat(entry_t).astimezone(NY)
    m = t.hour * 60 + t.minute
    if m < 10 * 60 + 30:
        return "09:35-10:30"
    if m < 12 * 60:
        return "10:30-12:00"
    if m < 14 * 60:
        return "12:00-14:00"
    return "14:00-15:30"


def corr(a: list[float], b: list[float]) -> float:
    if len(a) < 3 or pstdev(a) == 0 or pstdev(b) == 0:
        return math.nan
    ma, mb = mean(a), mean(b)
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (len(a) * pstdev(a) * pstdev(b))


def desk_stats(trs: list[dict], bars: dict, days: dict, start_equity: float = 1000.0) -> dict:
    pnl = [t["pnl_pct_equity"] for t in trs]
    wins = [p for p in pnl if p > 0]
    losses = [p for p in pnl if p <= 0]
    ci = bootstrap_ci(pnl)
    pf = (sum(wins) / -sum(losses)) if losses and sum(losses) < 0 else (math.inf if wins else 0.0)
    curve = [start_equity] + [t["equity_after"] for t in trs]
    groups = {"exit": defaultdict(list), "symbol": defaultdict(list), "time_of_day": defaultdict(list),
              "gap": defaultdict(list), "spy_day": defaultdict(list)}
    paths = []
    for t in trs:
        groups["exit"][t["reason"]].append(t["pnl_pct_equity"])
        groups["symbol"][t["sym"]].append(t["pnl_pct_equity"])
        groups["time_of_day"][tod_bucket(t["entry_t"])].append(t["pnl_pct_equity"])
        dr = days.get(t["day"], {})
        if "gap_pct" in dr:
            g = dr["gap_pct"]
            groups["gap"]["gap down >0.3%" if g < -0.3 else "gap up >0.3%" if g > 0.3 else "flat open"].append(t["pnl_pct_equity"])
        if "spy_oc_pct" in dr:
            groups["spy_day"]["SPY up day" if dr["spy_oc_pct"] > 0 else "SPY down day"].append(t["pnl_pct_equity"])
        p = path_after_entry(t, bars)
        if p:
            paths.append({**p, "move_pct": t["move_pct"], "reason": t["reason"]})
    spy_same = [days[t["day"]]["spy_oc_pct"] for t in trs if t["day"] in days]
    return {
        "trades": len(trs), "win_rate_pct": round(len(wins) / len(pnl) * 100, 1) if pnl else None,
        "avg_win_pct": round(mean(wins), 3) if wins else None,
        "avg_loss_pct": round(mean(losses), 3) if losses else None,
        "expectancy_pct": round(mean(pnl), 3) if pnl else None,
        "expectancy_ci95": [round(c, 3) if not math.isnan(c) else None for c in ci],
        "profit_factor": (round(pf, 2) if pf != math.inf else "inf (no losses)"),
        "total_return_pct": round((curve[-1] / start_equity - 1) * 100, 3),
        "max_dd_pct": round(max_drawdown(curve), 3),
        "label": label(len(pnl), ci),
        "breakdowns": {g: {k: {"n": len(v), "mean_pct": round(mean(v), 3)} for k, v in sorted(d.items())}
                       for g, d in groups.items()},
        "mae_mfe": paths,
        "mean_mae_pct": round(mean(p["mae_pct"] for p in paths), 3) if paths else None,
        "mean_mfe_pct": round(mean(p["mfe_pct"] for p in paths), 3) if paths else None,
        "spy_oc_same_days_pct": round(sum(spy_same), 3) if spy_same else None,
    }


def build(trades: list[dict], bars: dict) -> dict:
    days = day_table(bars)
    by_desk = defaultdict(list)
    for t in trades:
        by_desk[t["desk"]].append(t)
    out = {"desks": {k: desk_stats(v, bars, days) for k, v in sorted(by_desk.items())},
           "days": days, "first_day": min((t["day"] for t in trades), default=None),
           "last_day": max((t["day"] for t in trades), default=None), "n_trades": len(trades)}
    # daily P&L correlation between desks (0 on days a desk didn't trade)
    all_days = sorted({t["day"] for t in trades})
    daily = {k: [sum(t["pnl_pct_equity"] for t in v if t["day"] == d) for d in all_days] for k, v in by_desk.items()}
    ks = sorted(daily)
    out["correlations"] = {f"{a}~{b}": (None if math.isnan(c := corr(daily[a], daily[b])) else round(c, 2))
                           for i, a in enumerate(ks) for b in ks[i + 1:]}
    out["combined_equal_weight_daily_pct"] = [round(sum(daily[k][i] for k in ks) / len(ks), 3) for i in range(len(all_days))] if ks else []
    out["sessions_with_trades"] = all_days
    return out


def to_markdown(r: dict) -> str:
    L = [f"# Paper report: {r['first_day']} to {r['last_day']} ({r['n_trades']} trades)", "",
         "Expectancy = mean P&L per trade in % of desk equity, after the spec's slippage. CI = bootstrap 95%.", "",
         "| Desk | Trades | Win rate | Avg win | Avg loss | Expectancy (95% CI) | PF | Return | Max DD | MAE / MFE avg | SPY o->c same days | Label |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, s in r["desks"].items():
        ci = s["expectancy_ci95"]
        cis = f"[{ci[0]}, {ci[1]}]" if ci[0] is not None else "n/a"
        L.append(f"| {k} | {s['trades']} | {s['win_rate_pct']}% | {s['avg_win_pct']} | {s['avg_loss_pct']} | "
                 f"{s['expectancy_pct']}% {cis} | {s['profit_factor']} | {s['total_return_pct']}% | {s['max_dd_pct']}% | "
                 f"{s['mean_mae_pct']} / {s['mean_mfe_pct']} | {s['spy_oc_same_days_pct']}% | {s['label']} |")
    L += ["", "## Breakdowns (n, mean % per trade)", ""]
    for k, s in r["desks"].items():
        parts = []
        for g, d in s["breakdowns"].items():
            parts.append(f"{g}: " + ", ".join(f"{a} {v['n']} / {v['mean_pct']}" for a, v in d.items()))
        L.append(f"- **{k}**: " + "; ".join(parts))
    L += ["", "## Desk correlations (daily P&L)", ""]
    L += [f"- {k}: {v}" for k, v in r["correlations"].items()] or ["- n/a"]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trades", required=True)
    ap.add_argument("--archive")
    ap.add_argument("--since")
    ap.add_argument("--out")
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    trades = load_trades(Path(a.trades), a.since)
    bars = load_bars(Path(a.archive) if a.archive else None, {t["sym"] for t in trades} | {"SPY"})
    r = build(trades, bars)
    md = to_markdown(r)
    if a.out:
        Path(a.out).write_text(md)
    if a.json:
        Path(a.json).write_text(json.dumps(r, indent=1, default=str))
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
