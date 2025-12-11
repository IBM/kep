#!/usr/bin/env python3
"""
utils/runner.py · dynamic version
---------------------------------
Tiny helper that:
  1. converts PDFs to paragraphs (PdfConverter)
  2. classifies them (Classifier)
  3. extracts structured JSON from the relevant ones (Structurer)

Use it when you just want raw LLM output, no evaluation.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import json

from ingest.pdf_converter        import PdfConverter
from extractor.classifier        import Classifier
from extractor.structurer        import Structurer
from common.file_logger          import FileLogger
from common.metadata             import MetadataRecorder


class Runner:
    # ──────────────────────────────────────────────────────────────────
    def __init__(
        self,
        pdf_dir: str | Path,
        work_dir: str | Path,
        *,
        provider: str                         = "watsonx",
        model_id: str                         = "mistralai/mistral-large",
        prompt_mode: str                      = "zero",         # "zero" | "few"
        num_exem: int                         = 0,
        cfg_file: str | Path                  = "config/model_config.yaml",
        cls_schema: str | Path                = "schemas/classification.json",
        ext_schema: str | Path                = "schemas/extraction.json",
        output_mode: str                      = "per_pdf",
        chunk_strategy: str                   = "paragraph",    # fixed | sentence | paragraph
        chunk_size: int                       = 100,
        chunk_overlap: int                    = 25,
    ):
        self.pdf_dir        = Path(pdf_dir)
        self.work_dir       = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)

        self.provider       = provider
        self.model_id       = model_id
        self.prompt_mode    = prompt_mode
        self.num_exem       = num_exem
        self.cfg_file       = str(cfg_file)
        self.cls_schema     = str(cls_schema)
        self.ext_schema     = str(ext_schema)

        self.output_mode    = output_mode
        self.chunk_strategy = chunk_strategy
        self.chunk_size     = chunk_size
        self.chunk_overlap  = chunk_overlap

        # logging / metadata
        self.logger = FileLogger(self.work_dir / "run.log")
        self.meta   = MetadataRecorder(self.logger)

    # ──────────────────────────────────────────────────────────────────
    def _convert_pdfs(self) -> List[Dict[str, Any]]:
        """PDF → markdown → paragraph chunks"""
        self.logger.info("▶ [Runner] Converting PDFs under %s", self.pdf_dir)
        PdfConverter.convert_dir(
            dir_in         = self.pdf_dir,
            dir_out        = self.work_dir / "ingest",
            logger         = self.logger,
            metadata       = self.meta,
            output_mode    = "combined",
            chunk_strategy = self.chunk_strategy,
            chunk_size     = self.chunk_size,
            chunk_overlap  = self.chunk_overlap,
        )
        ingest_file = self.work_dir / "ingest" / "all_paragraphs.json"
        return json.loads(ingest_file.read_text(encoding="utf-8"))

    # ──────────────────────────────────────────────────────────────────
    def run(self) -> None:
        """Execute the three-step pipeline."""
        paragraphs = self._convert_pdfs()
        cfg        = self.cfg_file

        # ---- 1) Classification ---------------------------------------
        self.logger.info("▶ [Runner] Classification (%s-shot)", self.prompt_mode)
        clf = Classifier(
            config = cfg,
            provider    = self.provider,
            model_name  = self.model_id,
            prompt_mode = self.prompt_mode,
            schema_file = self.cls_schema,
            num_exem    = self.num_exem,
            output_dir  = self.work_dir / "classification",
            logger      = self.logger,
            metadata    = self.meta,
        )
        full_preds, relevant, _ = clf.predict(paragraphs)

        # persist
        (self.work_dir / "classified_full.json").write_text(
            json.dumps(full_preds, indent=2, ensure_ascii=False))
        (self.work_dir / "classified_relevant.json").write_text(
            json.dumps(relevant,   indent=2, ensure_ascii=False))

        # ---- 2) Extraction -------------------------------------------
        self.logger.info("▶ [Runner] Extraction (%s-shot)", self.prompt_mode)
        ks = Structurer(
            config = cfg,
            provider    = self.provider,
            model_name  = self.model_id,
            prompt_mode = self.prompt_mode,
            schema_file = self.ext_schema,
            num_exem    = self.num_exem,
            output_dir  = self.work_dir / "extraction",
            logger      = self.logger,
            metadata    = self.meta,
        )
        struct_out, _ = ks.predict(relevant)
        (self.work_dir / "structured.json").write_text(
            json.dumps(struct_out, indent=2, ensure_ascii=False))

        # ---- 3) Finish ----------------------------------------------
        self.meta.write(self.work_dir / "metadata.json")
        self.logger.info("✅ Runner finished → %s", self.work_dir)


# ─────────────────────────── CLI helper (optional) ───────────────────────────
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf-dir",  required=True)
    ap.add_argument("--work-dir", required=True)
    ap.add_argument("--provider", default="watsonx")
    ap.add_argument("--model-id", default="mistralai/mistral-large")
    ap.add_argument("--prompt-mode", choices=["zero", "few"], default="zero")
    ap.add_argument("--num-exem", type=int, default=0)
    args = ap.parse_args()

    Runner(
        pdf_dir      = args.pdf_dir,
        work_dir     = args.work_dir,
        provider     = args.provider,
        model_id     = args.model_id,
        prompt_mode  = args.prompt_mode,
        num_exem     = args.num_exem,
    ).run()