#!/usr/bin/env python3
"""
ingest/chunker.py

Split raw text into smaller pieces for downstream LLM calls.

strategy =  fixed      → sliding word-window (size, overlap)
            sentence   → NLTK sentence tokenizer
            paragraph  → blank-line separated paragraphs
"""

import re, nltk
from typing import List


class Chunker:
    def __init__(
        self,
        *,
        strategy: str = "fixed",
        size: int = 100,
        overlap: int = 25,
        **_ignored,              # swallow legacy kwargs (e.g. folder_path, schema, logger)
    ):
        self.strategy = strategy
        self.size = size
        self.overlap = overlap

        if strategy == "sentence":
            # ensure punkt model is present
            try:
                nltk.data.find("tokenizers/punkt")
            except LookupError:
                nltk.download("punkt")

    # ───────────────────── internal helpers ──────────────────────
    def _fixed(self, text: str) -> List[str]:
        words = text.split()
        step = max(1, self.size - self.overlap)
        return [" ".join(words[i : i + self.size]) for i in range(0, len(words), step)]

    def _sentence(self, text: str) -> List[str]:
        return nltk.sent_tokenize(text)

    def _paragraph(self, text: str) -> List[str]:
        return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    # ───────────────────── public API ────────────────────────────
    def split(self, text: str) -> List[str]:
        if self.strategy == "fixed":
            return self._fixed(text)
        if self.strategy == "sections":
            return self._fixed(text)
        if self.strategy == "sentence":
            return self._sentence(text)
        if self.strategy == "paragraph":
            return self._paragraph(text)
        raise ValueError(f"Invalid strategy '{self.strategy}'")

    # ───────────── legacy shims (back-compat) ─────────────────────
    def fixed_chunking(self, text: str) -> List[str]:
        """Alias for old code – calls split() with strategy='fixed'."""
        return self._fixed(text)

    def sentence_chunking(self, text: str) -> List[str]:
        """Alias for old code – calls split() with strategy='sentence'."""
        return self._sentence(text)

