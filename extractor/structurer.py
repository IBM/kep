#!/usr/bin/env python3
"""
extractor/structurer.py · 2025-04-29
------------------------------------
• accepts `debug_io`
• logs BASE PROMPT once; with flag, also dumps per-paragraph PROMPT + RAW
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


class Structurer:                                    # alias kept below
    """Extracts structured JSON according to *schema_file* for each paragraph."""

    def __init__(
        self,
        *,
        config: Dict[str, Any],
        provider: str,
        prompt_mode: str,
        schema_file: str,
        num_exem: int,
        output_dir: Path,
        logger: FileLogger,
        metadata: MetadataRecorder,
        chosen_examples: Optional[List[Dict[str, Any]]] = None,
        fallback_dataset: Optional[List[Dict[str, Any]]] = None,
        debug_io: bool = False,                       # ← NEW
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

    # ------------------------------------------------------------------
    def predict(self, dataset: List[Dict[str, Any]]
               ) -> Tuple[List[Dict[str, Any]], str]:

        tracker = ProgressTracker(
            phase_name = "extraction",
            logger     = self.logger,
            metadata   = self.meta,
            total      = len(dataset),
        )

        results: List[Dict[str, Any]] = []

        for idx, item in enumerate(dataset):
            text = (item.get("Text") or item.get("text") or "").strip()
            tracker.tick(text[:60].replace("\n", " "))

            prompt = f"{self.base_prompt}\n\n\"text\": \"{text}\""

            if not self.prompt_logged:
                self.logger.info("\n[Structurer] BASE PROMPT >>>\n%s\n", self.base_prompt)
                self.prompt_logged = True

            try:
                import time
                start_time = time.time()
                raw = self.llm.inference(prompt)["generated_text"]
                duration = round(time.time() - start_time + item.get("duration"), 2)
            except Exception as e:
                self.logger.error("[EXT] inference failed: %s", e)
                raw = ""
                duration = None

            if self.debug_io:
                self.logger.debug("[EXT %04d] PROMPT >>>\n%s", idx, prompt)
                self.logger.debug("[EXT %04d] RAW >>>\n%s",    idx, raw)

            extracted = extract_json_from_response(raw)

            results.append({**item,
                            "data":       extracted,
                            "raw_output": raw,
                            "prompt":     prompt,
                            "duration": duration})

        tracker.done(total_extracted=len(results))
        return results, self.base_prompt


# legacy alias
ExtractorStructurer = Structurer