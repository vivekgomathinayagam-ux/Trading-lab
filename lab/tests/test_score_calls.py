from lab.news.score_calls import score_bars


def b(o, h, l, c):
    return {"o": o, "h": h, "l": l, "c": c}


def test_hit_up_and_down():
    assert score_bars([b(100, 100.2, 99.9, 100.1), b(100.1, 100.6, 100, 100.5)], "up", 0.5)["result"] == "hit"
    assert score_bars([b(100, 100.1, 99.4, 99.5)], "down", 0.5)["result"] == "hit"


def test_miss_when_other_side_first_or_both_in_one_bar():
    assert score_bars([b(100, 100.1, 99.4, 99.5), b(99.5, 101, 99.5, 100.8)], "up", 0.5)["result"] == "miss"
    assert score_bars([b(100, 100.6, 99.4, 100)], "up", 0.5)["result"] == "miss"


def test_none_and_no_data():
    r = score_bars([b(100, 100.2, 99.8, 100.1)], "up", 0.5)
    assert r["result"] == "none" and r["end_move_pct"] == 0.1
    assert score_bars([], "up", 0.5)["result"] == "no_data"
