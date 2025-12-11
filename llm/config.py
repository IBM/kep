"""
config.py – lightweight YAML loader with lazy cache.
Keeps each client's configuration **isolated** inside its own folder.
"""

from __future__ import annotations
from pathlib import Path
from functools import lru_cache
from typing import Any, Dict
import yaml


# @lru_cache(maxsize=1024)
def load_yaml(path: str | Path) -> Dict[str, Any]:
    path = Path(path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_client_cfg(cfg_path: str) -> Dict[str, Any]:
    return load_yaml(cfg_path)