#!/usr/bin/env python3
"""
common/metadata.py

Lightweight recorder for phase timings & arbitrary run information.

Public API
----------
start(phase)              – mark phase start timestamp
stop(phase, **extra)      – mark phase end timestamp + arbitrary info
read_all() → dict         – return   current metadata in-memory
write(path)               – write    metadata JSON file to `path`
"""
import json, datetime
from pathlib import Path
from typing import Any, Dict


class MetadataRecorder:
    """Collect timings + arbitrary info during a run."""

    def __init__(self, logger):
        self._logger = logger
        self._data: Dict[str, Any] = {"phases": {}}

    # ───────────────────────── phase helpers ──────────────────────────
    def start(self, phase: str):
        self._data["phases"].setdefault(phase, {})["start"] = (
            datetime.datetime.now().isoformat(timespec="seconds")
        )

    def stop(self, phase: str, **extra):
        p = self._data["phases"].setdefault(phase, {})
        p["end"] = datetime.datetime.now().isoformat(timespec="seconds")
        p.update(extra)

    # ───────────────────────── public helpers ─────────────────────────
    def read_all(self) -> Dict[str, Any]:
        """Return a *shallow* copy of everything recorded so far."""
        return dict(self._data)

    def write(self, path: Path | str) -> None:
        """
        Persist metadata to disk as pretty-printed UTF-8 JSON.

        `path` may be pathlib.Path or str.  Parent directories are created.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
        self._logger.info(f"[META] wrote {path}")