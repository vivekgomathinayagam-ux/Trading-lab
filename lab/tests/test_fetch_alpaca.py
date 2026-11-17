import unittest
from lab.foundry.fetch_alpaca import fetch, parse_bars


class FakeResp:
    status_code = 200
    def __init__(self, j): self._j = j
    def raise_for_status(self): pass
    def json(self): return self._j


class FakeSession:
    def __init__(self): self.calls = 0
    def get(self, url, params=None, headers=None, timeout=0):
        self.calls += 1
        if self.calls == 1:
            return FakeResp({"bars": {"SPY": [
                {"t": "2026-11-16T14:30:00Z", "o": 1, "h": 2, "l": 0.5, "c": 1.5, "v": 10},   # 09:30 ET
                {"t": "2026-11-16T22:00:00Z", "o": 1, "h": 2, "l": 0.5, "c": 1.5, "v": 10}]},  # 17:00 ET: dropped
                "next_page_token": "x"})
        return FakeResp({"bars": {"SPY": [{"t": "2026-11-16T14:35:00Z", "o": 1, "h": 2, "l": 1, "c": 2, "v": 5}]},
                         "next_page_token": None})


class T(unittest.TestCase):
    def test_pages_and_regular_hours_only(self):
        bars = fetch("SPY", "a", "b", "sip", {}, session=FakeSession())
        self.assertEqual([b.t.strftime("%H:%M") for b in bars], ["09:30", "09:35"])

    def test_empty(self):
        self.assertEqual(parse_bars({"bars": None}, "SPY"), [])


if __name__ == "__main__":
    unittest.main()
