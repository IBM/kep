# kep/common/progress.py
from __future__ import annotations
import sys, time
from typing import Optional
from pathlib import Path
from .file_logger  import FileLogger
from .metadata     import MetadataRecorder

class ProgressTracker:
    """
    Very light progress reporter.
    ───────────────────────────
    • Prints one‑line updates to stdout **live** (over‑writable).
    • Writes the same messages to FileLogger.
    • Notifies MetadataRecorder when a phase starts / ends so you keep timings
      in metadata.json without changing existing code.
    • You can create *sub‑tasks* (e.g. iterate over N paragraphs) and it will
      show a counter automatically.
    """

    def __init__(
        self,
        phase_name: str,
        logger: FileLogger,
        metadata: Optional[MetadataRecorder] = None,
        total: Optional[int] = None
    ):
        self.phase   = phase_name
        self.logger  = logger
        self.meta    = metadata
        self.total   = total or 0
        self.counter = 0
        self._start  = time.perf_counter()
        if self.meta:
            self.meta.start(self.phase)
        self.logger.info(f"[{self.phase}] ▶ started (total={self.total})")

    # ------------------------------------------------------------------ public
    def tick(self, msg: str = ""):
        """
        Call once per unit of work (e.g. per paragraph).
        """
        self.counter += 1
        bar = f"{self.counter}/{self.total}" if self.total else f"{self.counter}"
        try:
            sys.stdout.write(f"\r[{self.phase}] {bar} {msg:60s}")
            sys.stdout.flush()
        except Exception:
            # stdout may be closed or suppressed; ignore
            pass

    def done(self, **extra):
        """
        Finish the phase – prints newline, logs & updates MetadataRecorder.
        """
        elapsed = time.perf_counter() - self._start
        try:
            sys.stdout.write("\n")      # move to next line
        except Exception:
            pass
        self.logger.info(f"[{self.phase}] ✔ finished in {elapsed:.2f}s")
        if self.meta:
            self.meta.stop(self.phase, total=self.counter, **extra)