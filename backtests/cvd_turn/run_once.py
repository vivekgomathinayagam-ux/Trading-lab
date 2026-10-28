"""First-adoption backtest, run ONCE (2026-10-28): cvd_spy, cvd_tqqq, ema_vol_v2 on the archived 1-minute bars.
  python -m backtests.cvd_turn.run_once <archive_dir> <out_dir>
"""
import json
import sys
from pathlib import Path

from lab.floor.data import load_archive
from lab.floor.engine import desk_metrics, simulate
from lab.floor.paper_report import bootstrap_ci
from strategies.daytrade.core import SLIP, SYMBOLS, CVDTurn, EMACrossV2

arch, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
bars = {}
for s in SYMBOLS:
    d = load_archive(arch / f"{s}.csv.gz")
    bars[s] = [d[k] for k in sorted(d)]
res_all = {}
for mult in (1, 2, 3):
    res = simulate(bars, [CVDTurn("SPY"), CVDTurn("TQQQ"), EMACrossV2()], slip_mult=mult)
    rows = []
    for d in res["desks"]:
        m = desk_metrics(d, res["eod_equity"][d.key])
        m["expectancy_ci95"] = [round(x, 3) for x in bootstrap_ci([t["pnl_pct_equity"] for t in d.trades])]
        rows.append(m)
        if mult == 1:
            with (out / f"trades_{d.key}.json").open("w") as f:
                json.dump(d.trades, f, indent=1)
    res_all[f"{mult}x"] = {"first_day": res["first_day"], "last_day": res["last_day"], "sessions": res["sessions"], "desks": rows}
# "just be long" control: buy at 09:48 open, sell 15:55 open, same symbol, every session traded
ctl = {}
for s in ("SPY", "TQQQ"):
    byday = {}
    for b in bars[s]:
        byday.setdefault(b.t.date(), {})[b.t.strftime("%H:%M")] = b
    days = sorted(byday)[3:]
    rets = []
    for d in days:
        x = byday[d]
        if "09:48" in x and "15:55" in x:
            e, q = x["09:48"].o * (1 + SLIP[s]), x["15:55"].o * (1 - SLIP[s])
            rets.append((q / e - 1) * 100)
    ctl[s] = {"days": len(rets), "mean_move_pct": round(sum(rets) / len(rets), 3), "ci95": [round(v, 3) for v in bootstrap_ci(rets)]}
res_all["control_long_0948_to_1555"] = ctl
(out / "results.json").write_text(json.dumps(res_all, indent=1))
print(json.dumps(res_all, indent=1))
