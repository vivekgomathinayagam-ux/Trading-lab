"""Score Newsie's pre-market calls against what price did (research only; nothing trades).

A call {ticker, direction up|down, move_pct, window_et "HH:MM-HH:MM"} is a HIT if, inside the window, price reached
move_pct in the called direction (from the first bar's open) before it moved move_pct the other way; a MISS if the
opposite came first; NONE if neither. Down calls are scored on the ticker itself falling (the inverse ETF or put is
just the vehicle). Same-bar double touch counts as a miss (pessimistic).
Usage: python -m lab.news.score_calls <calls dir> [day]   (keys from env ALPACA_KEY_ID / ALPACA_SECRET_KEY)
Writes <calls dir>/scores/<day>.json and refreshes <calls dir>/scores/SUMMARY.md (hit rate by confidence bucket).
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

NY = ZoneInfo("America/New_York")
URL = "https://data.alpaca.markets/v2/stocks/bars"


def score_bars(bars: list[dict], direction: str, move_pct: float) -> dict:
    """bars: [{o,h,l,c}] inside the window, in order."""
    if not bars:
        return {"result": "no_data"}
    p0 = bars[0]["o"]
    up, dn = p0 * (1 + move_pct / 100), p0 * (1 - move_pct / 100)
    want_up = direction == "up"
    best_fav = 0.0
    for b in bars:
        hit_up, hit_dn = b["h"] >= up, b["l"] <= dn
        fav = (b["h"] / p0 - 1) * 100 if want_up else (1 - b["l"] / p0) * 100
        best_fav = max(best_fav, fav)
        if hit_up and hit_dn:
            return {"result": "miss", "entry": p0, "note": "both sides in one bar", "best_fav_pct": round(best_fav, 3)}
        if (hit_up and want_up) or (hit_dn and not want_up):
            return {"result": "hit", "entry": p0, "best_fav_pct": round(best_fav, 3)}
        if hit_up or hit_dn:
            return {"result": "miss", "entry": p0, "best_fav_pct": round(best_fav, 3)}
    end = bars[-1]["c"]
    return {"result": "none", "entry": p0, "end_move_pct": round((end / p0 - 1) * 100 * (1 if want_up else -1), 3),
            "best_fav_pct": round(best_fav, 3)}


def fetch(sym: str, day: str, w0: str, w1: str, headers: dict) -> list[dict]:
    def utc(hm):
        h, m = map(int, hm.split(":"))
        return datetime.fromisoformat(f"{day}T{h:02d}:{m:02d}:00").replace(tzinfo=NY).isoformat()
    for feed in ("sip", "iex"):
        r = requests.get(URL, params={"symbols": sym, "timeframe": "1Min", "start": utc(w0), "end": utc(w1),
                                      "limit": 10000, "feed": feed, "adjustment": "raw"}, headers=headers, timeout=60)
        if r.ok:
            return (r.json().get("bars") or {}).get(sym, []) or []
    return []


def summarize(scores_dir: Path) -> str:
    rows = []
    for f in sorted(scores_dir.glob("20*.json")):
        rows += json.load(open(f)).get("scored", [])
    lines = ["# Newsie call scores (hit = called move reached before the same move the other way)\n",
             f"Calls scored: {len(rows)}\n", "| confidence | calls | hit | miss | none | hit rate (hit / hit+miss) |", "|---|---|---|---|---|---|"]
    for lo, hi in ((0, 50), (50, 65), (65, 80), (80, 101)):
        b = [r for r in rows if lo <= r.get("confidence", 0) < hi]
        h = sum(r["result"] == "hit" for r in b); m = sum(r["result"] == "miss" for r in b); n = sum(r["result"] == "none" for r in b)
        rate = f"{h / (h + m):.0%}" if h + m else "-"
        lines.append(f"| {lo}-{min(hi, 100)} | {len(b)} | {h} | {m} | {n} | {rate} |")
    lines.append("\nNo-skill baseline is about 50% (a random direction with symmetric target/stop). A bucket earns trust only with 30+ decided calls above it.")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    d = Path(argv[1])
    day = argv[2] if len(argv) > 2 else datetime.now(NY).strftime("%Y-%m-%d")
    f = d / f"{day}.json"
    out_dir = d / "scores"; out_dir.mkdir(parents=True, exist_ok=True)
    if not f.exists():
        print("no calls for", day); (out_dir / "SUMMARY.md").write_text(summarize(out_dir)); return 0
    headers = {"APCA-API-KEY-ID": os.environ.get("ALPACA_KEY_ID", ""), "APCA-API-SECRET-KEY": os.environ.get("ALPACA_SECRET_KEY", "")}
    calls = json.load(open(f))
    scored = []
    for c in calls.get("calls", []):
        w0, w1 = (c.get("window_et") or "09:40-11:30").split("-")
        res = score_bars(fetch(c["ticker"].upper(), day, w0, w1, headers), c["direction"], float(c["move_pct"]))
        scored.append({**{k: c.get(k) for k in ("ticker", "direction", "move_pct", "window_et", "confidence")}, **res})
        print(scored[-1])
    json.dump({"day": day, "scored": scored, "market_read": calls.get("market_read")}, open(out_dir / f"{day}.json", "w"), indent=1)
    (out_dir / "SUMMARY.md").write_text(summarize(out_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
