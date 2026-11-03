"""Fetch Yahoo 5-minute bars (last ~59 days) into a gzip CSV archive. Runs on GitHub Actions."""
import sys
from pathlib import Path

from lab.floor.data import fetch_intraday, load_archive, save_archive

out = Path(sys.argv[1])
for sym in sys.argv[2].split(","):
    path = out / f"{sym}.csv.gz"
    have = load_archive(path)
    for b in fetch_intraday(sym, "5m", 59):
        have[b.t] = b
    save_archive(path, have)
    print(sym, len(have))
