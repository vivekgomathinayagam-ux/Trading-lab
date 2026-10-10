"""Strategy interface. A strategy is deterministic code: it sees quotes and
its own state, and returns proposed Orders. It never talks to a broker; the
worker sends every Order through the risk engine, then the broker.

Lifecycle stage is in each strategy's config.yaml:
  idea -> spec -> backtest -> paper -> live_ready -> live -> retired
Only "paper" and "live" strategies are run by the worker.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from engine.brokers.base import Quote
from engine.risk import Order


@dataclass
class StrategyConfig:
    name: str
    stage: str = "idea"
    symbols: list[str] = field(default_factory=list)
    interval_seconds: int = 60
    params: dict = field(default_factory=dict)

    @classmethod
    def load(cls, folder: Path) -> "StrategyConfig":
        data = yaml.safe_load((folder / "config.yaml").read_text()) or {}
        return cls(name=data.get("name", folder.name), stage=data.get("stage", "idea"),
                   symbols=data.get("symbols", []),
                   interval_seconds=int(data.get("interval_seconds", 60)),
                   params=data.get("params", {}))


class Strategy(ABC):
    def __init__(self, cfg: StrategyConfig):
        self.cfg = cfg
        self.name = cfg.name

    @abstractmethod
    def on_tick(self, quotes: dict[str, Quote], positions: list[dict], mode: str) -> list[Order]:
        """Called every `interval_seconds` during market hours."""
        ...

    def status(self) -> dict:
        return {"name": self.name, "stage": self.cfg.stage, "symbols": self.cfg.symbols}
