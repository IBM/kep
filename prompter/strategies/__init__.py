"""
Strategy discovery & public helpers.
"""
from importlib import import_module
from pathlib import Path
from .base import get_strategy_cls        # re-export for callers  ✓

# ─────────────────── import every *.py (except base/this) ──────────────────
_pkg_dir = Path(__file__).parent
for _file in _pkg_dir.glob("*.py"):
    if _file.stem not in {"base", "__init__"}:
        import_module(f"{__name__}.{_file.stem}")