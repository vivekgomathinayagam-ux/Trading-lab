"""Daily session post-mortem: what the market offered, what each desk took, what it missed.

  python -m lab.foundry.postmortem --archive backtests/data/etf1m --trades ledger/daytrade_trades.csv \
      --out out/postmortem [--day 2026-11-03]

Writes <out>/<day>.md and <out>/<day>.json. Hindsight numbers (best leg, MFE) describe the
opportunity; they are never used to pick rules. Rules are only changed through pre-registered tests.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from lab.foundry.batch3 import clean_wicks
from lab.foundry.rules import RULES, add_features, load_bars, simulate, to_5min

SYMS = ["SPY", "QQQ", "TQQQ", "UPRO", "SQQQ", "SPXU"]


def best_legs(g: pd.DataFrame) -> dict:
    """Largest low->later-high and high->later-low moves in the session (1-min bars)."""
    lo_px, lo_t, best_up = None, None, (0.0, None, None)
    hi_px, hi_t, best_dn = None, None, (0.0, None, None)
    for t, b in g.iterrows():
        if lo_px is None or b["l"] < lo_px:
            lo_px, lo_t = b["l"], t
        if hi_px is None or b["h"] > hi_px:
            hi_px, hi_t = b["h"], t
        up = b["h"] / lo_px - 1
        dn = 1 - b["l"] / hi_px
        if up > best_up[0]:
            best_up = (up, lo_t, t)
        if dn > best_dn[0]:
            best_dn = (dn, hi_t, t)
    f = lambda x: (round(100 * x[0], 3), str(x[1].time()) if x[1] is not None else None,
                   str(x[2].time()) if x[2] is not None else None)
    return {"up": f(best_up), "down": f(best_dn)}


def trade_excursion(g: pd.DataFrame, t_in, t_out, entry: float, side: int = 1) -> dict:
    w = g[(g.index >= t_in) & (g.index <= t_out)]
    if w.empty:
        return {}
    mfe = side * ((w["h"].max() if side > 0 else w["l"].min()) / entry - 1)
    mae = side * ((w["l"].min() if side > 0 else w["h"].max()) / entry - 1)
    return {"mfe_pct": round(100 * mfe, 3), "mae_pct": round(100 * mae, 3)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", required=True)
    ap.add_argument("--trades", required=False)
    ap.add_argument("--out", required=True)
    ap.add_argument("--day", default=None)
    a = ap.parse_args()
    arch = Path(a.archive)
    # wick cleaning at ingest (LESSONS 25; PREREG_batch3): clip 1-min wicks beyond 0.4% x leverage of the body
    bars = {s: clean_wicks(load_bars(arch / f"{s}.csv.gz"), 0.004 * (3 if s in ("TQQQ", "UPRO", "SQQQ", "SPXU") else 1))[0]
            for s in SYMS if (arch / f"{s}.csv.gz").exists()}
    day = a.day or str(max(bars["SPY"].index.date))
    rep = {"day": day, "market": {}, "desks": [], "foundry": [], "lessons_prompt": []}
    lines = [f"# Session post-mortem {day}", ""]
    lines += ["## What the market offered (1-min, regular hours)", "",
              "| Symbol | Open | High | Low | Close | Day % | Best up-leg % (from-to ET) | Best down-leg % |",
              "|---|---|---|---|---|---|---|---|"]
    for s, d in bars.items():
        g = d[d.index.date.astype(str) == day] if hasattr(d.index.date, "astype") else d[[str(x) == day for x in d.index.date]]
        if g.empty:
            continue
        legs = best_legs(g)
        o, h, l, c = g["o"].iloc[0], g["h"].max(), g["l"].min(), g["c"].iloc[-1]
        rep["market"][s] = dict(o=o, h=h, l=l, c=c, day_pct=round(100 * (c / o - 1), 3), **legs)
        lines.append(f"| {s} | {o:.2f} | {h:.2f} | {l:.2f} | {c:.2f} | {100*(c/o-1):+.2f} | "
                     f"{legs['up'][0]} ({legs['up'][1]}-{legs['up'][2]}) | {legs['down'][0]} ({legs['down'][1]}-{legs['down'][2]}) |")
    lines.append("")

    # paper desks
    if a.trades and Path(a.trades).exists():
        tr = pd.read_csv(a.trades)
        tr = tr[tr["entry_t"].astype(str).str.startswith(day)]
        lines += ["## What the paper desks did", "",
                  "| Desk | Symbol | In | Out | Exit | P&L $ | Move % | Best open profit (MFE) % | Worst (MAE) % | Gave back (MFE − result) % |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for _, t in tr.iterrows():
            g = bars.get(t["sym"])
            ti = pd.Timestamp(t["entry_t"]).tz_convert("America/New_York")
            to = pd.Timestamp(t["exit_t"]).tz_convert("America/New_York")
            ex = trade_excursion(g, ti, to, float(t["entry_px"])) if g is not None else {}
            left = round(ex.get("mfe_pct", 0) - float(t["move_pct"]), 3) if ex else None
            rec = dict(desk=t["desk"], sym=t["sym"], t_in=str(ti.time()), t_out=str(to.time()),
                       reason=t["reason"], pnl=float(t["pnl_usd"]), move_pct=float(t["move_pct"]), left_pct=left, **ex)
            rep["desks"].append(rec)
            lines.append(f"| {rec['desk']} | {rec['sym']} | {rec['t_in'][:5]} | {rec['t_out'][:5]} | {rec['reason']} | "
                         f"{rec['pnl']:+.2f} | {rec['move_pct']:+.3f} | {ex.get('mfe_pct','')} | {ex.get('mae_pct','')} | {left} |")
        if tr.empty:
            lines.append("| (no desk traded) | | | | | | | | | |")
        lines.append("")

    # foundry rules on the day (run on the full history so EMAs are warm; keep the day's trades)
    lines += ["## Foundry rules on this day (research only, not traded)", "",
              "| Rule | Symbol | Side | In | Out | Exit | Net % |", "|---|---|---|---|---|---|---|"]
    for s in ("SPY", "QQQ"):
        if s not in bars:
            continue
        f5 = add_features(to_5min(bars[s]))
        for r in RULES:
            for t in simulate(f5, r, s):
                if t["day"] == day:
                    rep["foundry"].append(t)
                    lines.append(f"| {r} | {s} | {'long' if t['side']>0 else 'short'} | {t['t_in'][11:16]} | "
                                 f"{t['t_out'][11:16]} | {t['why']} | {100*t['net']:+.3f} |")
    lines.append("")
    # prompts for the agent writing LESSONS.md (facts only; the agent writes the lesson)
    for dsk in rep["desks"]:
        if dsk.get("left_pct") is not None and dsk["left_pct"] > 0.3:
            rep["lessons_prompt"].append(f"{dsk['desk']} {dsk['sym']} gave back {dsk['left_pct']}% from its best open profit (exit {dsk['reason']}).")
    spy = rep["market"].get("SPY")
    if spy:
        taken = [x for x in rep["desks"] if x["sym"] in ("SPY", "UPRO", "SPXU")]
        rep["lessons_prompt"].append(
            f"SPY best up-leg {spy['up'][0]}%, best down-leg {spy['down'][0]}%; desks on SPY-family: {len(taken)} trades.")
    lines += ["## Facts for the lesson", ""] + [f"- {x}" for x in rep["lessons_prompt"]] + [""]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{day}.md").write_text("\n".join(lines))
    (out / f"{day}.json").write_text(json.dumps(rep, indent=1, default=str))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
