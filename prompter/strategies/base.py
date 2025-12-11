"""
Base class shared by every prompt-building strategy
and central registry (avoids circular imports).
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List, Mapping, Optional, Any, Type
import random
import importlib

# ───────────────────── registry lives here ──────────────────────────
_REGISTRY: Dict[str, Type["PromptStrategy"]] = {}

def _register(name: str, cls: Type["PromptStrategy"]) -> None:
    _REGISTRY[name.lower()] = cls

def get_strategy_cls(name: str) -> Type["PromptStrategy"]:
    key = name.lower()
    if key not in _REGISTRY:
        raise ValueError(f"Unknown strategy '{name}'. Available: {list(_REGISTRY)}")
    return _REGISTRY[key]

def register_strategy(name: str):
    """
    Decorator used by concrete strategies, e.g.

        @register_strategy("few")
        class FewShot(PromptStrategy):
            ...
    """
    def _decorator(cls):
        _register(name, cls)
        return cls
    return _decorator
# ─────────────────────────────────────────────────────────────────────

class PromptStrategy(ABC):
    """Sub-classes override *placeholder_values()* to fill the template."""

    def __init__(
        self,
        *,
        placeholders: Mapping[str, Any],
        num_examples: int,
        chosen_examples: Optional[List[Dict]],
        fallback_dataset: Optional[List[Dict]],
        rng: random.Random,
    ):
        self.ph     = placeholders
        self.N      = num_examples
        self.chosen = chosen_examples or []
        self.pool   = fallback_dataset or []
        self.pick   = rng.sample

    # each concrete strategy implements this
    @abstractmethod
    def placeholder_values(self) -> Dict[str, str]:
        ...