"""Screen candidate tickers: price, average daily dollar volume, and MEASURED spread (research only)."""
import os, statistics, requests
H = {"APCA-API-KEY-ID": os.environ.get("ALPACA_KEY_ID", ""), "APCA-API-SECRET-KEY": os.environ.get("ALPACA_SECRET_KEY", "")}
D = "https://data.alpaca.markets"
CAND = ("SPY QQQ TQQQ SQQQ SOXL UPRO SPXL XLF IWM "
        "F BAC T PFE INTC SOFI SNAP RIVN NIO LCID AAL CCL WBD KVUE HPE PLTR HOOD RIOT MARA CLSK VALE ITUB WFC CSCO KO").split()
def get(path, **p):
    r = requests.get(D + path, params=p, headers=H, timeout=60)
    return r.json() if r.ok else {}
bars = get("/v2/stocks/bars", symbols=",".join(CAND), timeframe="1Day", start="2026-10-15T00:00:00Z",
           end="2026-11-16T00:00:00Z", feed="sip", limit=10000)
print("symbol  price  adv$M  spread_bps(10:30ET median, 5 days)")
for s in CAND:
    b = (bars.get("bars") or {}).get(s) or []
    if len(b) < 5:
        print(s, "no data"); continue
    px = b[-1]["c"]; adv = statistics.mean(x["c"] * x["v"] for x in b[-15:]) / 1e6
    sp = []
    for day in ("2026-11-10", "2026-11-11", "2026-11-12", "2026-11-13", "2026-11-16"):
        q = get("/v2/stocks/quotes", symbols=s, start=f"{day}T15:30:00Z", end=f"{day}T15:36:00Z", limit=10000, feed="sip")
        for x in (q.get("quotes") or {}).get(s, []):
            if x["bp"] > 0 and x["ap"] >= x["bp"]:
                sp.append((x["ap"] - x["bp"]) / ((x["ap"] + x["bp"]) / 2) * 1e4)
    print(f"{s:6} {px:8.2f} {adv:8.0f} {statistics.median(sp):6.1f}" if sp else f"{s} no quotes")
