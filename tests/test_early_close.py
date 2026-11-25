"""Early closes (Accountant 2026-11-25): on 13:00 ET days, no entries from 12:30 and flat from 12:55;
every other day unchanged. Run: python -m unittest discover -s tests -t . -v
"""
import unittest
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from strategies.daytrade.core import (EARLY_CLOSES, ENTRY_END, FLAT_AT, Bar, Desk, Features, ORB,
                                      entry_end_for, flat_at_for)
from lab.floor.engine import simulate

NY = ZoneInfo("America/New_York")


def bars_for(day, n, start_px=100.0, step=0.0):
    t0 = datetime(day.year, day.month, day.day, 9, 30, tzinfo=NY)
    out, c = [], start_px
    for i in range(n):
        o = c
        c = o + step
        out.append(Bar(t0 + timedelta(minutes=i), o, max(o, c) + 0.01, min(o, c) - 0.01, c, 1000.0))
    return out


class EarlyClose(unittest.TestCase):
    def test_calendar(self):
        self.assertIn(date(2026, 11, 27), EARLY_CLOSES)
        self.assertEqual(flat_at_for(date(2026, 11, 27)).strftime("%H:%M"), "12:55")
        self.assertEqual(entry_end_for(date(2026, 11, 27)).strftime("%H:%M"), "12:30")
        self.assertEqual(flat_at_for(date(2026, 11, 25)), FLAT_AT)
        self.assertEqual(entry_end_for(date(2026, 11, 30)), ENTRY_END)

    def test_position_flattened_at_1255_on_half_day(self):
        d = Desk(rule=ORB(None))
        day = datetime(2026, 11, 27)
        bars = bars_for(day, 210)                       # 09:30-12:59
        d.fill_entry("SPY", 100.0, bars[60].t)
        hits = [(b.t.strftime("%H:%M"), d.exit_check("SPY", b)) for b in bars[61:]]
        first = next(h for h in hits if h[1])
        self.assertEqual(first[0], "12:55")
        self.assertEqual(first[1][0], "eod")

    def test_same_bars_normal_day_hold_on(self):
        d = Desk(rule=ORB(None))
        bars = bars_for(datetime(2026, 11, 25), 210)
        d.fill_entry("SPY", 100.0, bars[60].t)
        self.assertFalse(any(d.exit_check("SPY", b) for b in bars[61:]))

    def test_no_entries_from_1230(self):
        d = Desk(rule=ORB(None))
        f = Features()
        b = bars_for(datetime(2026, 11, 27), 200)[185]   # 12:35
        self.assertEqual(b.t.strftime("%H:%M"), "12:35")
        self.assertFalse(d.wants_entry("SPY", b, f))
        d.pending, d.pending_day = "SPY", b.t.date().isoformat()
        self.assertFalse(d.pending_valid(b))

    def test_lab_replay_does_not_carry_half_day(self):
        # a breakout after the opening range on the half day, then the next session
        up = bars_for(datetime(2026, 11, 27), 210, step=0.01)
        nxt = bars_for(datetime(2026, 11, 30), 390, start_px=up[-1].c)
        res = simulate({"SPY": up + nxt}, [ORB(None)], trade_from_day=date(2026, 11, 27))
        trades = res["desks"][0].trades
        self.assertTrue(any(str(t["entry_t"])[:10] == "2026-11-27" for t in trades))
        for t in trades:
            if str(t.get("entry_t", ""))[:10] == "2026-11-27":
                self.assertEqual(str(t["exit_t"])[:10], "2026-11-27")


if __name__ == "__main__":
    unittest.main()
