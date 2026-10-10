"""Finds every strategy folder with a config.yaml and a strategy.py exposing
`build(cfg) -> Strategy`. Only stages "paper" and "live" are run."""
from __future__ import annotations

import importlib
import logging
from pathlib import Path

from strategies.base import Strategy, StrategyConfig

log = logging.getLogger("registry")
ROOT = Path(__file__).parent
RUNNABLE = {"paper", "live"}


def discover() -> list[StrategyConfig]:
    out = []
    for folder in sorted(ROOT.iterdir()):
        if folder.is_dir() and (folder / "config.yaml").exists():
            out.append(StrategyConfig.load(folder))
    return out


def load_runnable() -> list[Strategy]:
    strategies: list[Strategy] = []
    for cfg in discover():
        if cfg.stage not in RUNNABLE:
            continue
        try:
            mod = importlib.import_module(f"strategies.{cfg.name}.strategy")
            strategies.append(mod.build(cfg))
            log.info("loaded strategy %s (stage=%s)", cfg.name, cfg.stage)
        except Exception as e:  # noqa: BLE001
            log.error("could not load strategy %s: %s", cfg.name, e)
    return strategies
