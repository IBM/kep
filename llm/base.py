"""
base.py – abstract interface and common helpers for every LLM client.
Adheres to SOLID:
* Single-responsibility: only the interface layer.
* Open/closed: concrete back-ends extend `LLMClient`.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict


class LLMClient(ABC):
    """Common interface that every back-end must implement."""

    def __init__(self, config: Dict[str, Any], *, debug: bool = False):
        self._cfg = config
        self.debug = debug

    # ------------------------------------------------------------------ public API
    @abstractmethod
    def inference(self, data: Any) -> Dict[str, Any]:
        """
        Run a **single** inference call.

        Parameters
        ----------
        data : Any
            Prompt (str) for completion-style models **or**
            list[dict] of messages for chat models.

        Returns
        -------
        dict
            Must contain the raw text under key ``"generated_text"`` **or**
            an equivalent client-specific payload.
        """

    # ------------------------------------------------------------------ helpers
    def _dbg(self, *msg):
        if self.debug:
            print("[LLM-DEBUG]", *msg)