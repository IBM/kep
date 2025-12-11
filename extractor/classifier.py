#!/usr/bin/env python3
"""
extractor/classifier.py · 2025-04-29
------------------------------------
• accepts `debug_io` flag
• if debug_io=True  → log PROMPT + RAW for every paragraph
• if debug_io=False → show single BASE PROMPT + compact per-paragraph lines
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any

from common.file_logger     import FileLogger
from common.metadata        import MetadataRecorder
from common.progress        import ProgressTracker
from llm                    import LLMFactory
from prompter               import Prompter
from utils.utility          import extract_json_from_response


class Classifier:                                   # alias kept below
    """Zero/-few-shot relevance classifier for paragraph chunks."""

    # ─────────────────────────── init ────────────────────────────
    def __init__(
        self,
        *,
        config: dict[str, Any],
        provider: str,
        prompt_mode: str,                 # "zero" | "few"
        schema_file: str,
        num_exem: int,
        output_dir: Path,
        logger: FileLogger,
        metadata: MetadataRecorder,
        chosen_examples: Optional[List[Dict[str, Any]]] = None,
        fallback_dataset: Optional[List[Dict[str, Any]]] = None,
        debug_io: bool = False,           # ← NEW
        debug_llm: bool = False,
        
    ):
        self.llm = LLMFactory.create(
            provider   = provider,
            cfg        = config,
            debug      = debug_llm,
        )

        self.logger  = logger
        self.meta    = metadata
        self.out_dir = output_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)

        self.base_prompt = Prompter(
            schema_json      = schema_file,
            strategy         = prompt_mode,
            num_examples     = num_exem,
            chosen_examples  = chosen_examples,
            fallback_dataset = fallback_dataset,
        ).build()

        self.prompt_logged = False
        self.debug_io      = debug_io

    # ─────────────────────────── public ───────────────────────────
    def predict(
        self, dataset: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], str]:

        tracker = ProgressTracker(
            phase_name = "classification",
            logger     = self.logger,
            metadata   = self.meta,
            total      = len(dataset),
        )

        full, relevant = [], []

        for idx, item in enumerate(dataset):
            text = (item.get("Text") or item.get("text") or "").strip()
            tracker.tick(text[:60].replace("\n", " "))

            prompt = f"{self.base_prompt}\n\n\"text\": \"{text}\""

            # log the BASE PROMPT once
            if not self.prompt_logged:
                self.logger.info("\n[Classifier] BASE PROMPT >>>\n%s\n", self.base_prompt)
                self.prompt_logged = True

            # LLM inference
            try:
                import time
                start_time = time.time()
                raw = self.llm.inference(prompt)["generated_text"]
                duration = round(time.time() - start_time, 2)
            except Exception as e:
                self.logger.error("[CLS] inference failed: %s", e)
                raw = ""
                duration = None

            # extra logging if the flag is on
            if self.debug_io:
                self.logger.debug("[CLS %04d] PROMPT >>>\n%s", idx, prompt)
                self.logger.debug("[CLS %04d] RAW >>>\n%s",    idx, raw)

            parsed = extract_json_from_response(raw)
            label  = (parsed.get("classification") or "").lower().strip()
            if label not in {"relevant", "irrelevant"}:
                self.logger.error("Invalid label '%s' – forcing 'irrelevant'", label)
                label = "irrelevant"

            rec = {**item,
                   "classification": label,
                   "raw_output":     raw,
                   "prompt":         prompt,
                   "duration":       duration}
            full.append(rec)
            if label == "relevant":
                relevant.append(rec)

        tracker.done(total_classified=len(full), total_relevant=len(relevant))
        return full, relevant, self.base_prompt


# legacy alias (old imports still work)
ExtractorClassifier = Classifier