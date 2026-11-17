"""Probe what the Alpaca key can reach (status codes and counts only; keys never printed)."""
import os, requests
H = {"APCA-API-KEY-ID": os.environ.get("ALPACA_KEY_ID", ""), "APCA-API-SECRET-KEY": os.environ.get("ALPACA_SECRET_KEY", "")}
D = "https://data.alpaca.markets"
tests = {
  "news_hist_2024": (f"{D}/v1beta1/news", {"start": "2024-03-01T13:00:00Z", "end": "2024-03-01T15:00:00Z", "limit": 50}),
  "news_latest": (f"{D}/v1beta1/news", {"limit": 50}),
  "trades_hist_sip": (f"{D}/v2/stocks/trades", {"symbols": "AAPL", "start": "2025-06-02T13:30:00Z", "end": "2025-06-02T13:32:00Z", "limit": 10000, "feed": "sip"}),
  "quotes_hist_sip": (f"{D}/v2/stocks/quotes", {"symbols": "AAPL", "start": "2025-06-02T13:30:00Z", "end": "2025-06-02T13:31:00Z", "limit": 10000, "feed": "sip"}),
  "snapshot_iex": (f"{D}/v2/stocks/snapshots", {"symbols": "AAPL,SPY", "feed": "iex"}),
  "snapshot_sip": (f"{D}/v2/stocks/snapshots", {"symbols": "AAPL,SPY", "feed": "sip"}),
  "movers": (f"{D}/v1beta1/screener/stocks/movers", {"top": 20}),
  "most_actives": (f"{D}/v1beta1/screener/stocks/most-actives", {"top": 20}),
  "bars_1min_2019": (f"{D}/v2/stocks/bars", {"symbols": "NVDA", "timeframe": "1Min", "start": "2019-03-01T14:30:00Z", "end": "2019-03-01T15:30:00Z", "feed": "sip"}),
}
for k, (u, p) in tests.items():
    try:
        r = requests.get(u, params=p, headers=H, timeout=30)
        j = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        n = None
        if isinstance(j, dict):
            for key in ("news", "trades", "quotes", "bars", "gainers", "most_actives"):
                v = j.get(key)
                if isinstance(v, list): n = len(v)
                elif isinstance(v, dict): n = sum(len(x) for x in v.values())
            if n is None and r.ok: n = len(j)
        msg = (j.get("message") if isinstance(j, dict) else "") or ""
        print(f"{k}: HTTP {r.status_code} count={n} {msg[:80]}")
    except Exception as e:
        print(f"{k}: error {type(e).__name__}")
# paper trading account reachable with the same key? (read only)
r = requests.get("https://paper-api.alpaca.markets/v2/account", headers=H, timeout=30)
print("paper_account:", r.status_code, (r.json().get("status") if r.ok else ""))
