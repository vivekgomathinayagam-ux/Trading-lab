"""Skylit pilot 1 (pre-registered in research/skylit/STUDY.md). python -m research.skylit.pilot1"""
import json
import math
import random
from pathlib import Path

# raw cache lives on branch `data` (research/skylit/raw/); extract it first:
#   mkdir -p research/skylit/raw && for f in $(git ls-tree --name-only origin/data research/skylit/raw/); do git show origin/data:$f > $f; done
D = Path(__file__).parent / "raw"
closes = json.load(open(D / "stats_daily_close.json"))
rows = []
for f in sorted(D.glob("heat_1000et_part*.jsonl")):
    for line in open(f):
        r = json.loads(line)
        if "error" in r:
            continue
        st = r["strikes"]
        king = [s for s in st if s[2] == "king"][0]
        net = sum(s[1] for s in st)
        c = closes[r["symbol"]].get(r["date"])
        if c is None:
            continue
        s10 = r["spot"]
        rows.append({"date": r["date"], "sym": r["symbol"], "spot10": s10, "close": c, "king": king[0], "king_val": king[1],
                     "net": net, "ret_pct": (c / s10 - 1) * 100, "king_dist_pct": (king[0] / s10 - 1) * 100})


def binom_ci(k, n):
    p = k / n
    h = 1.96 * math.sqrt(p * (1 - p) / n)
    return round(p * 100, 1), round((p - h) * 100, 1), round((p + h) * 100, 1)


def boot_diff(a, b, n=5000, seed=3):
    rng = random.Random(seed)
    ds = sorted(sum(rng.choice(a) for _ in a) / len(a) - sum(rng.choice(b) for _ in b) / len(b) for _ in range(n))
    return round(sum(a) / len(a) - sum(b) / len(b), 3), round(ds[int(0.025 * n)], 3), round(ds[int(0.975 * n)], 3)


out = {"n_rows": len(rows), "by_symbol": {}}
for sym in ("SPY", "QQQ", "ALL"):
    R = [r for r in rows if sym == "ALL" or r["sym"] == sym]
    off = [r for r in R if abs(r["king_dist_pct"]) > 0.05]          # king not at spot
    toward = sum(1 for r in off if (r["close"] - r["spot10"]) * (r["king"] - r["spot10"]) > 0)
    nearer = sum(1 for r in off if abs(r["close"] - r["king"]) < abs(r["spot10"] - r["king"]))
    pos = [abs(r["ret_pct"]) for r in R if r["net"] > 0]
    neg = [abs(r["ret_pct"]) for r in R if r["net"] <= 0]
    kpos = [abs(r["close"] / r["king"] - 1) * 100 for r in R if r["king_val"] > 0]
    kneg = [abs(r["close"] / r["king"] - 1) * 100 for r in R if r["king_val"] <= 0]
    out["by_symbol"][sym] = {
        "n": len(R), "n_king_off_spot": len(off),
        "Q1_close_moves_toward_king_pct_ci": binom_ci(toward, len(off)),
        "Q1_close_nearer_king_than_spot10_pct_ci": binom_ci(nearer, len(off)),
        "Q2_abs_move_after_10_net_pos_vs_neg": {"n_pos": len(pos), "n_neg": len(neg),
                                                 "mean_pos": round(sum(pos) / len(pos), 3) if pos else None,
                                                 "mean_neg": round(sum(neg) / len(neg), 3) if neg else None,
                                                 "diff_ci": boot_diff(pos, neg) if pos and neg else None},
        "Q3_close_to_king_dist_pos_king_vs_neg_king": {"n_pos": len(kpos), "n_neg": len(kneg),
                                                        "diff_ci": boot_diff(kpos, kneg) if kpos and kneg else None},
    }
(Path(__file__).parent / "pilot1_results.json").write_text(json.dumps(out, indent=1))
(Path(__file__).parent / "features_1000et.json").write_text(json.dumps(rows, indent=0))
print(json.dumps(out, indent=1))
