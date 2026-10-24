"""Historical BTC/ETH candles from Coinbase Exchange's public API (no key needed).

Endpoint: GET https://api.exchange.coinbase.com/products/{product}/candles
  granularity (seconds): 60, 300, 900, 3600, 21600, 86400
  max 300 candles per request; rows are [time, low, high, open, close, volume],
  newest first.

Bars are returned oldest first as a pandas DataFrame indexed by UTC timestamp
(bar OPEN time) with columns open, high, low, close, volume.
Runs on GitHub Actions or Railway (Claude's own workspace can't reach Coinbase).
"""
from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests

API = "https://api.exchange.coinbase.com/products/{product}/candles"
MAX_PER_REQ = 300
UA = {"User-Agent": "compound-city-lab/1.0 (research backtests)"}


def _get(url: str, params: dict, tries: int = 6) -> list:
    wait = 1.0
    for attempt in range(tries):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=30)
            if r.status_code == 429 or r.status_code >= 500:
                raise requests.HTTPError(f"status {r.status_code}")
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError):
            if attempt == tries - 1:
                raise
            time.sleep(wait)
            wait = min(wait * 2, 30)
    return []


def fetch_candles(product: str, granularity: int, start: datetime, end: datetime,
                  pause: float = 0.35) -> pd.DataFrame:
    """Download candles between start and end (UTC), oldest first."""
    url = API.format(product=product)
    step = timedelta(seconds=granularity * MAX_PER_REQ)
    rows: list = []
    t = start
    while t < end:
        t2 = min(t + step, end)
        chunk = _get(url, {"granularity": granularity,
                           "start": t.isoformat(), "end": t2.isoformat()})
        if isinstance(chunk, list):
            rows.extend(chunk)
        t = t2
        time.sleep(pause)
    if not rows:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    df = pd.DataFrame(rows, columns=["time", "low", "high", "open", "close", "volume"])
    df = df.drop_duplicates("time").sort_values("time")
    df.index = pd.to_datetime(df["time"], unit="s", utc=True)
    df = df[["open", "high", "low", "close", "volume"]].astype(float)
    return clean(df)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Drop impossible rows (non-positive prices, high < low) and keep order."""
    ok = (df[["open", "high", "low", "close"]] > 0).all(axis=1) & (df["high"] >= df["low"])
    df = df[ok].copy()
    df["high"] = df[["high", "open", "close"]].max(axis=1)
    df["low"] = df[["low", "open", "close"]].min(axis=1)
    return df[~df.index.duplicated()].sort_index()


def resample(df: pd.DataFrame, rule: str, min_count: int) -> pd.DataFrame:
    """Aggregate to a coarser bar (e.g. '4h' from 1h). Buckets with fewer than
    min_count source bars are dropped, so no bar is built from partial data."""
    g = df.resample(rule, label="left", closed="left")
    out = pd.DataFrame({
        "open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(),
        "close": g["close"].last(), "volume": g["volume"].sum(), "n": g["close"].count(),
    })
    out = out[out["n"] >= min_count].drop(columns="n")
    return out.dropna()


def load_or_fetch(cache_dir: Path, product: str, granularity: int,
                  start: datetime, end: datetime) -> pd.DataFrame:
    """Cache to CSV so reruns only fetch the missing tail."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"{product}_{granularity}.csv"
    have = None
    if path.exists():
        have = pd.read_csv(path, index_col=0, parse_dates=True)
        if have.index.tz is None:
            have.index = have.index.tz_localize("UTC")
        last = have.index.max().to_pydatetime()
        if last >= end - timedelta(seconds=granularity * 2):
            return clean(have[(have.index >= start) & (have.index < end)])
        fetch_from = last + timedelta(seconds=granularity)
    else:
        fetch_from = start
    new = fetch_candles(product, granularity, fetch_from, end)
    df = new if have is None else clean(pd.concat([have, new]))
    df.to_csv(path)
    return df[(df.index >= start) & (df.index < end)]


def utc(y: int, m: int, d: int) -> datetime:
    return datetime(y, m, d, tzinfo=timezone.utc)
