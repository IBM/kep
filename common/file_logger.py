#!/usr/bin/env python3
"""
common/file_logger.py

Ultra-minimal file logger (disk only, no console).
"""

from datetime import datetime
from pathlib import Path
import traceback

class FileLogger:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    # ----------------------------- internals -----------------------------
    def _write(self, level: str, msg: str):
        ts = datetime.now().isoformat(sep=" ", timespec="seconds")
        with self.path.open("a", encoding="utf-8") as fp:
            fp.write(f"{ts} [{level.upper()}] {msg}\n")

    # ----------------------------- public API ---------------------------
    def _fmt(self, template: str, *args) -> str:
        return template % args if args else template

    def info(self, msg, *a):       self._write("info",      self._fmt(msg, *a))
    def debug(self, msg, *a):      self._write("debug",     self._fmt(msg, *a))
    def error(self, msg, *a):      self._write("error",     self._fmt(msg, *a))
    def exception(self, msg, *a):  # adds traceback
        self._write("exception", f"{self._fmt(msg,*a)}\n{traceback.format_exc()}")