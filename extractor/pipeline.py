"""
extractor.pipeline
──────────────────
End-to-end driver used by `extractor.run_pipeline()`.

1.  Loads chunked paragraphs from  <ingest_dir>/all_paragraphs.json
2.  Classifies them   →   keeps only 'relevant'
3.  Extracts JSON for the relevant subset
4.  Writes results + metadata into <work_dir>/*
"""

from __future__ import annotations
import json, datetime, random
from pathlib import Path
from typing import List, Dict, Any, Optional

from .classifier  import ExtractorClassifier
from .structurer  import ExtractorStructurer
from common.file_logger  import FileLogger
from common.metadata     import MetadataRecorder


class ExtractorPipeline:
    def __init__(
        self,
        *,
        ingest_dir: Path,
        work_dir:   Path,
        cfg_file:   str,
        provider:   str,
        model_id:   str,
        cls_schema: str | Path,
        ext_schema: str | Path,
        prompt_mode: str = "zero",
        num_examples: int = 0,
        rng_seed: int = 42,
    ):
        self.ingest_dir   = ingest_dir
        self.work_dir     = work_dir
        self.work_dir.mkdir(parents=True, exist_ok=True)

        self.cfg_file     = cfg_file
        self.provider     = provider
        self.model_id     = model_id
        self.cls_schema   = cls_schema
        self.ext_schema   = ext_schema
        self.mode         = prompt_mode
        self.N            = num_examples
        self.rng_seed     = rng_seed

        self.logger = FileLogger(self.work_dir / "extractor.log")
        self.meta   = MetadataRecorder(self.logger)

        random.seed(rng_seed)

    # ------------------------------------------------------------------
    def _load_paragraphs(self) -> List[Dict[str, Any]]:
        src = self.ingest_dir / "all_paragraphs.json"
        if not src.exists():
            raise FileNotFoundError(
                f"{src} not found – run PdfConverter.convert_dir() first"
            )
        return json.loads(src.read_text(encoding="utf-8"))

    # ------------------------------------------------------------------
    def run(self):
        ts_start = datetime.datetime.now().isoformat(timespec="seconds")
        self.logger.info("▶ ExtractorPipeline start")

        # 1) load chunks -------------------------------------------------
        paragraphs = self._load_paragraphs()
        self.logger.info(f"Loaded {len(paragraphs)} paragraphs from ingest")

        # 2) classification ---------------------------------------------
        cls = ExtractorClassifier(
            config     = self.cfg_file,
            provider        = self.provider,
            model_name      = self.model_id,
            schema_file     = self.cls_schema,
            prompt_mode     = self.mode,
            num_exem        = self.N,
            output_dir      = self.work_dir / "classification",
            logger          = self.logger,
            metadata        = self.meta,
        )
        cls_full, relevant, _ = cls.predict(paragraphs)     # ← FIXED
        (self.work_dir / "classified_full.json").write_text(
            json.dumps(cls_full, indent=2, ensure_ascii=False))
        (self.work_dir / "classified_relevant.json").write_text(
            json.dumps(relevant, indent=2, ensure_ascii=False))

        # 3) extraction --------------------------------------------------
        st = ExtractorStructurer(
            config     = self.cfg_file,
            provider        = self.provider,
            model_name      = self.model_id,      # ← FIXED
            schema_file     = self.ext_schema,
            prompt_mode     = self.mode,
            num_exem    = self.N,
            output_dir      = self.work_dir / "extraction",
            logger          = self.logger,
            metadata        = self.meta,
        )
        structured, base_prompt = st.predict(relevant)
        (self.work_dir / "structured.json").write_text(
            json.dumps(structured, indent=2, ensure_ascii=False))
        self.logger.info("Extraction finished")

        # 4) metadata ----------------------------------------------------
        ts_end = datetime.datetime.now().isoformat(timespec="seconds")
        self.meta.stop("run", start=ts_start, end=ts_end,
                       total_paragraphs=len(paragraphs),
                       relevant=len(relevant))
        self.meta.write(self.work_dir / "run_metadata.json")
        self.logger.info("✔ ExtractorPipeline complete")