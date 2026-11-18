"""Batch 6 Skylit tests (pre-registered in research/foundry/PREREG_batch6.md): H23 market tide, H24 Flux Field.
Research only: nothing here trades.

  python -m lab.foundry.skylit6 --tide tide_daily.json --long <alpaca5m dir> --flux <flux dir> --a <etf1m dir> --out <dir>

Flux files: <day>_<SYM>.json with points [{time (epoch s), level, inner{upper,lower}, outer, extreme, price}].
Skylit stamps a minute point at the bar's END (its price equals the previous 1-min bar's close), so a decision
at the close of bar t could use the point stamped t+1; we use the point stamped t-1 (two minutes older).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from lab.foundry.batch6 import boot_days, diff_ci, load5, days_of
from lab.foundry.rules import COST, load_bars

ET = ZoneInfo("America/New_York")
SEEDS = list(range(21, 29))
PER_DAY = 5
STOP = 0.005


# ------------------------------------------------------------------ H23 market tide
def tide_frame(rows: list) -> pd.DataFrame:
    t = pd.DataFrame([dict(day=dt.datetime.fromtimestamp(r["timestamp"], dt.timezone.utc).date().isoformat(),
                           ncp=r["ncp"], npp=r["npp"]) for r in rows])
    t["N"] = t["ncp"] - t["npp"]
    return t.sort_values("day").drop_duplicates("day").reset_index(drop=True)


def daily_spy(arch5: Path) -> pd.DataFrame:
    d = load5(Path(arch5) / "SPY.csv.gz")
    g = d.groupby("day")
    return pd.DataFrame(dict(o=g["o"].first(), c=g["c"].last())).reset_index()


def h23(tide: pd.DataFrame, spy: pd.DataFrame) -> dict:
    spy = spy.sort_values("day").reset_index(drop=True)
    spy["prev_c"] = spy["c"].shift(1)
    nxt = {d: i for i, d in enumerate(spy["day"])}
    rows = []
    for _, r in tide.iterrows():
        # next SPY session strictly after the tide day
        later = spy[spy["day"] > r["day"]]
        if later.empty:
            continue
        s = later.iloc[0]
        oc = s["c"] / s["o"] - 1
        cc = s["c"] / s["prev_c"] - 1 if s["day"] in nxt and not np.isnan(s["prev_c"]) else np.nan
        side = 1 if r["N"] > 0 else -1
        rows.append(dict(day=s["day"], tide_day=r["day"], N=r["N"], dN=np.nan, side=side,
                         gross=side * oc, net=side * oc - COST, oc=oc, cc=cc, why="eod"))
    t = pd.DataFrame(rows)
    t["dN"] = t["N"].diff()
    sessions = sorted(t["day"])
    half = set(sessions[: len(sessions) // 2])
    m = lambda x: float(x["net"].mean() * 100) if len(x) else None
    L, S = t[t["side"] > 0], t[t["side"] < 0]
    out = dict(n=int(len(t)), first=sessions[0], last=sessions[-1], mean=m(t), ci=boot_days(t),
               win=float((t["net"] > 0).mean()), mean_2x=float((t["gross"] - 2 * COST).mean() * 100),
               h1=m(t[t["day"].isin(half)]), h2=m(t[~t["day"].isin(half)]), long=m(L), long_n=int(len(L)),
               short=m(S), short_n=int(len(S)),
               always_long=float((t["oc"] - COST).mean() * 100),
               corr_N_oc=float(t["N"].corr(t["oc"])), corr_dN_oc=float(t["dN"].corr(t["oc"])),
               corr_N_cc=float(t["N"].corr(t["cc"])))
    # random-sign control: p95 of the mean with random sides
    rng = np.random.default_rng(11)
    oc = t["oc"].values
    out["rand_p95"] = float(np.percentile([(rng.choice([1, -1], size=len(oc)) * oc - COST).mean()
                                           for _ in range(2000)], 95) * 100)
    out["pass"] = bool(out["mean"] > 0 and out["ci"][0] > 0 and out["h1"] > 0 and out["h2"] > 0 and
                       (out["long"] or 0) > 0 and (out["short"] or 0) > 0 and out["mean_2x"] > 0 and
                       out["mean"] > out["rand_p95"])
    return out


# ------------------------------------------------------------------ H24 Flux Field
def load_flux(flux_dir: Path, sym: str) -> pd.DataFrame:
    rows = []
    for f in sorted(Path(flux_dir).glob(f"*_{sym}.json")):
        for p in json.loads(f.read_text())["points"]:
            rows.append(dict(t=dt.datetime.fromtimestamp(p["time"], ET), lvl=p["level"],
                             iu=p["inner"]["upper"], il=p["inner"]["lower"]))
    return pd.DataFrame(rows).set_index("t").sort_index()


def one_min_days(arch1m: Path, sym: str, flux: pd.DataFrame) -> dict:
    a = load_bars(Path(arch1m) / f"{sym}.csv.gz")
    a = a[pd.Series(a.index.date, index=a.index).astype(str).isin(set(flux.index.date.astype(str)))]
    # flux point of minute t-1 for the decision at bar t's close
    f = flux.shift(1).reindex(a.index)
    a = a.join(f)
    a["mins"] = a.index.hour * 60 + a.index.minute
    out = {}
    for day, g in a.groupby(a.index.date):
        g = g.dropna(subset=["lvl"])
        if len(g) < 300:
            continue
        out[str(day)] = dict(o=g["o"].values, h=g["h"].values, l=g["l"].values, c=g["c"].values,
                             mins=g["mins"].values, lvl=g["lvl"].values, iu=g["iu"].values, il=g["il"].values,
                             t=[str(x) for x in g.index])
    return out


def trade1(b: dict, k: int, side: int, max_bars: int | None) -> dict | None:
    n = len(b["o"])
    if k + 1 >= n:
        return None
    entry = b["o"][k + 1]
    stop = entry * (1 - STOP * side)
    for j in range(k + 1, n):
        ex = None
        if side > 0 and b["l"][j] <= stop:
            ex, why = min(b["o"][j], stop), "stop"
        elif side < 0 and b["h"][j] >= stop:
            ex, why = max(b["o"][j], stop), "stop"
        elif (max_bars and j - k >= max_bars) or b["mins"][j] >= 955 or j == n - 1:
            ex, why = b["c"][j], "time" if (max_bars and j - k >= max_bars) else "eod"
        if ex is not None:
            g = side * (ex / entry - 1)
            return dict(side=side, why=why, gross=float(g), net=float(g - COST), t_in=b["t"][k + 1])
    return None


def zone(b: dict, k: int) -> str:
    c = b["c"][k]
    return "above" if c > b["iu"][k] else ("below" if c < b["il"][k] else "inside")


def h24(days_by: dict) -> dict:
    rnd = []
    for s, days in days_by.items():
        for seed in SEEDS:
            rng = np.random.default_rng(seed * 1000 + (1 if s == "SPY" else 2))
            for day, b in days.items():
                ok = np.where((b["mins"] >= 585) & (b["mins"] <= 900))[0]
                for k in sorted(rng.choice(ok, size=PER_DAY, replace=False)):
                    k, side = int(k), int(rng.choice([1, -1]))
                    z = zone(b, k)
                    rel = "inside" if z == "inside" else ("with" if (z == "above") == (side > 0) else "against")
                    for ex, mb in (("t30", 30), ("eod", None)):
                        t = trade1(b, k, side, mb)
                        if t:
                            rnd.append(dict(sym=s, seed=seed, day=day, exit=ex, zone=z, rel=rel, **t))
    r = pd.DataFrame(rnd)
    sessions = sorted(r["day"].unique())
    half = set(sessions[: len(sessions) // 2])
    out = dict(sessions=len(sessions), first=sessions[0], last=sessions[-1])
    for ex in ("t30", "eod"):
        e = r[r["exit"] == ex]
        res = {rel: dict(n=int((e["rel"] == rel).sum()), mean=float(e[e["rel"] == rel]["net"].mean() * 100))
               for rel in ("with", "against", "inside")}
        res["with_vs_against"] = diff_ci(e[e["rel"] == "with"], e[e["rel"] == "against"])
        res["with_vs_inside"] = diff_ci(e[e["rel"] == "with"], e[e["rel"] == "inside"])
        for side, nm in ((1, "long"), (-1, "short")):
            es = e[e["side"] == side]
            res[nm] = diff_ci(es[es["rel"] == "with"], es[es["rel"] == "against"])
        for hn, mask in (("h1", e["day"].isin(half)), ("h2", ~e["day"].isin(half))):
            eh = e[mask]
            res[hn] = diff_ci(eh[eh["rel"] == "with"], eh[eh["rel"] == "against"])
        res["share"] = {z: float((e["zone"] == z).mean()) for z in ("above", "below", "inside")}
        w = res
        w["lead"] = bool(all((w[x].get("diff") or -1) > 0 for x in ("long", "short", "h1", "h2"))
                         and w["with_vs_against"]["ci"][0] > 0)
        out[ex] = res
    # level reclaim / loss rule
    tr = []
    for s, days in days_by.items():
        for day, b in days.items():
            below = above = 0
            done = set()
            for k in range(len(b["c"])):
                c, lv = b["c"][k], b["lvl"][k]
                if 585 <= b["mins"][k] <= 900:
                    if 1 not in done and c > lv and below >= 15:
                        t = trade1(b, k, 1, None)
                        if t:
                            tr.append(dict(sym=s, day=day, **t))
                        done.add(1)
                    if -1 not in done and c < lv and above >= 15:
                        t = trade1(b, k, -1, None)
                        if t:
                            tr.append(dict(sym=s, day=day, **t))
                        done.add(-1)
                below = below + 1 if c < lv else 0
                above = above + 1 if c > lv else 0
    t = pd.DataFrame(tr)
    if not t.empty:
        m = lambda x: float(x["net"].mean() * 100) if len(x) else None
        out["reclaim"] = dict(n=int(len(t)), mean=m(t), ci=boot_days(t), win=float((t["net"] > 0).mean()),
                              long=m(t[t["side"] > 0]), long_n=int((t["side"] > 0).sum()),
                              short=m(t[t["side"] < 0]), short_n=int((t["side"] < 0).sum()),
                              h1=m(t[t["day"].isin(half)]), h2=m(t[~t["day"].isin(half)]),
                              rand_eod=float(r[r["exit"] == "eod"]["net"].mean() * 100))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tide")
    ap.add_argument("--long")
    ap.add_argument("--flux")
    ap.add_argument("--a")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    res = {}
    if a.tide and a.long:
        res["H23"] = h23(tide_frame(json.loads(Path(a.tide).read_text())), daily_spy(Path(a.long)))
    if a.flux and a.a:
        days_by = {s: one_min_days(Path(a.a), s, load_flux(Path(a.flux), s)) for s in ("SPY", "QQQ")}
        res["H24"] = h24(days_by)
    (out / "skylit_summary.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps(res, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
