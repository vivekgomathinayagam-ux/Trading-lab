"""Paper report and parity replay on a made-up ledger."""
import csv
import tempfile
import unittest
from datetime import date
from pathlib import Path

from lab.floor import paper_report as pr
from lab.floor import replay as rp

ROWS = [
    # desk, sym, qty, entry_t, exit_t, entry_px, exit_px, pnl_usd, pnl_pct_equity, move_pct, reason, equity_after
    ("a", "SPY", 1, "2026-10-26T10:00:00-04:00", "2026-10-26T15:56:00-04:00", 100, 101, 1.0, 0.1, 1.0, "eod", 1001.0),
    ("a", "SPY", 1, "2026-10-27T10:00:00-04:00", "2026-10-27T11:00:00-04:00", 100, 97.5, -2.5, -0.25, -2.5, "stop", 998.5),
    ("b", "TQQQ", 10, "2026-10-26T14:30:00-04:00", "2026-10-26T15:56:00-04:00", 50, 52.5, 25.0, 2.5, 5.0, "target", 1025.0),
]
COLS = ["desk", "sym", "qty", "entry_t", "exit_t", "entry_px", "exit_px", "pnl_usd", "pnl_pct_equity",
        "move_pct", "reason", "equity_after"]


def write(path):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        w.writerows(ROWS)


class PaperReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.p = Path(self.tmp.name) / "t.csv"
        write(self.p)

    def tearDown(self):
        self.tmp.cleanup()

    def test_stats(self):
        r = pr.build(pr.load_trades(self.p), {})
        a = r["desks"]["a"]
        self.assertEqual(a["trades"], 2)
        self.assertEqual(a["win_rate_pct"], 50.0)
        self.assertAlmostEqual(a["expectancy_pct"], -0.075)
        self.assertEqual(a["profit_factor"], 0.4)
        self.assertAlmostEqual(a["max_dd_pct"], (998.5 / 1001 - 1) * 100, places=3)
        self.assertEqual(a["label"], "too small to say")
        self.assertEqual(a["breakdowns"]["exit"]["stop"]["n"], 1)
        self.assertEqual(r["desks"]["b"]["breakdowns"]["time_of_day"], {"14:00-15:30": {"n": 1, "mean_pct": 2.5}})
        self.assertIn("a~b", r["correlations"])

    def test_since_filter(self):
        self.assertEqual(len(pr.load_trades(self.p, since="2026-10-27")), 1)

    def test_bootstrap_and_labels(self):
        lo, hi = pr.bootstrap_ci([1.0] * 12)
        self.assertEqual((lo, hi), (1.0, 1.0))
        self.assertEqual(pr.label(12, (0.1, 0.5)), "promising")
        self.assertEqual(pr.label(12, (-0.5, -0.1)), "failing")
        self.assertEqual(pr.label(12, (-0.5, 0.5)), "inconclusive")
        self.assertEqual(pr.label(5, (0.1, 0.5)), "too small to say")


class ReplayCompareTests(unittest.TestCase):
    def test_match_diff_and_missing(self):
        paper = [dict(zip(COLS, map(str, r))) for r in ROWS]
        lab = [
            {"desk": "a", "sym": "SPY", "entry_t": "2026-10-26T10:01:00-04:00", "exit_t": "2026-10-26T15:55:00-04:00",
             "entry_px": 100.02, "exit_px": 101.0, "reason": "eod"},
            {"desk": "a", "sym": "QQQ", "entry_t": "2026-10-27T10:00:00-04:00", "exit_t": "2026-10-27T11:00:00-04:00",
             "entry_px": 100, "exit_px": 97.5, "reason": "stop"},
            {"desk": "c", "sym": "SPY", "entry_t": "2026-10-27T10:00:00-04:00", "exit_t": "2026-10-27T11:00:00-04:00",
             "entry_px": 100, "exit_px": 97.5, "reason": "stop"},
        ]
        r = rp.compare(paper, lab, date(2026, 10, 26), date(2026, 10, 27))
        st = {(x["desk"], x["day"]): x["status"] for x in r["rows"]}
        self.assertEqual(st[("a", "2026-10-26")], "match")
        self.assertEqual(st[("a", "2026-10-27")], "DIFF")
        self.assertEqual(st[("b", "2026-10-26")], "paper only")
        self.assertEqual(st[("c", "2026-10-27")], "lab only")
        self.assertEqual(r["mismatches"], 3)


if __name__ == "__main__":
    unittest.main()
