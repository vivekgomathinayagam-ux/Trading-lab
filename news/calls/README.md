# Pre-market call log (news_scalp forward track, research only)
One file per trading day, `<YYYY-MM-DD>.json`, written by the pre-market Newsie run before 9:30 ET, never edited after the open.
Each call: {"ticker", "direction": "up"|"down", "move_pct", "window_et": "09:40-11:30", "confidence": 0-100,
"catalyst", "macro_link", "chart_note", "volume_note", "flow_note", "sources": [urls]}.
The lab scores each call after the close against Alpaca 1-min bars: did price reach move_pct in the direction before the window ended,
before moving the same distance the other way? Calibration by confidence bucket vs. a no-skill baseline decides whether a desk is built.
