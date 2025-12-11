#!/usr/bin/env python3
"""
run_pipeline.py · strict few-shot contract (2025-05-01)
────────────────────────────────────────────────────────
End-to-end helper that

  1. converts PDFs → Markdown → paragraph chunks
  2. classifies each paragraph (“relevant” vs “irrelevant”)
  3. extracts structured JSON from the relevant subset

New behaviour
•  If --prompt-mode few is chosen but the *schema* lacks an
   `examples` array, execution stops with a clear error message.
•  All external sampling / --num-exem logic is gone – examples
   must be embedded in the schema.
•  Metadata now reports example counts straight from the schema.
"""

from __future__ import annotations

import yaml
import argparse
import datetime
import json
import os
import random
from pathlib import Path
from typing import Any, Dict, List
from llm.config import load_yaml
from common.file_logger import FileLogger
from common.metadata import MetadataRecorder
from ingest.pdf_converter import PdfConverter
from extractor.classifier import Classifier as ExtractorClassifier
from extractor.structurer import Structurer as ExtractorStructurer
from llm.config import load_client_cfg
import time
import threading
for thread in threading.enumerate():
    print(f"Active Thread: {thread.name}")
start_time = time.time()

ap = argparse.ArgumentParser()
# ─────────────────────────── CLI arg for custom yaml ───────────────────────────
ap.add_argument("-c", "--config",   default= "config/KEP_default.yaml", help="Path to the YAML configuration file.")
# ─────────────────────────── Legacy CLI args ───────────────────────────
ap.add_argument("--pdf-dir")
ap.add_argument("--cls-schema")
ap.add_argument("--ext-schema")
ap.add_argument("--work-dir",)
ap.add_argument("--model-id",)
ap.add_argument("--provider",)
ap.add_argument("--prompt-modecl",    choices=["zero", "few"])
ap.add_argument("--prompt-modeex",    choices=["zero", "few"])
ap.add_argument("--num-exem",       type=int, default=0,     # kept for CLI compatibility (ignored in few-shot)
                help="DEPRECATED – examples must live in the schema now")
ap.add_argument("--chunk-strategy", choices=["fixed", "sentence", "paragraph"])
ap.add_argument("--chunk-size",     type=int)
ap.add_argument("--chunk-overlap",  type=int)
ap.add_argument("--debug-io",       action="store_true", help="Dump prompt + raw output per paragraph")

# ─────────────────────────── Args treatment ───────────────────────────
initial_args, remaining_argv = ap.parse_known_args()
config = {}
if initial_args.config:
    print(f"🔄 Loading configuration from: {initial_args.config}")
    config = load_yaml(initial_args.config)
args = ap.parse_args(remaining_argv, namespace=initial_args)
#   Overriding yaml args with CLI args (legacy)
cli_args = vars(args)
for key, value in cli_args.items():
    if value is not None:
        config[key] = value

required_params = ['pdf_dir', 'classification_config', 'extraction_config']
missing_params = [param for param in required_params if param not in config]
if missing_params:
    raise Exception(f"The following required parameters were not provided: {missing_params}")

# deterministic randomness when chunking etc.
random.seed(int(os.getenv("PIPELINE_SEED", "42")))

# ─────────────────────────── helpers ───────────────────────────
EXAMPLE_KEYS = {"examples", "EXAMPLES", "example", "EXAMPLE"}

def _schema_has_examples(schema: Dict[str, Any]) -> bool:
    """
    Return True if *any* of the accepted spellings for an example array
    is present in the schema JSON.
    """
    try:
        return any(k in schema and schema[k] for k in EXAMPLE_KEYS)
    except Exception:
        return False


def _assert_examples(schema: dict[str, Any] | Path, stage: str):
    """
    Abort if --prompt-mode few is requested but the schema has no examples.
    """
    if (config["prompt_mode_classification"] == "few" or config["prompt_mode_extraction"] == "few") and not _schema_has_examples(schema):
        raise RuntimeError(
            f"Few-shot {stage} requested, but the schema provided has no 'examples' array."
        )


# ─────────────────────────── folders / logging ───────────────────────────
WORK   = Path(config["work_dir"]).resolve()
WORK.mkdir(parents=True, exist_ok=True)
INGEST = WORK / "ingest"
INGEST.mkdir(exist_ok=True)

LOGGER = FileLogger(WORK / "run.log")
META   = MetadataRecorder(LOGGER)
timestamp = datetime.datetime.now().isoformat(timespec="seconds")

# ─────────────────────────── 1) PDF → chunks ───────────────────────────
LOGGER.info("Step 1/3  – Conversion (strategy=%s)", config["chunk_strategy"])
PdfConverter.convert_dir(
    parser_name= config["parser"],
    dir_in=config["pdf_dir"],
    dir_out=INGEST,
    logger=LOGGER,
    metadata=META,
    output_mode="combined",
    chunk_strategy=config["chunk_strategy"],
    chunk_size=config["chunk_size"],
    chunk_overlap=config["chunk_overlap"],
)
paragraphs: List[Dict[str, Any]] = json.loads(
    (INGEST / "all_paragraphs.json").read_text()
)

# ─────────────────────────── 2) Classification ───────────────────────────


classification_config_path = config.get("classification_config")
classification_config = load_client_cfg(classification_config_path)

extraction_config_path = config.get("extraction_config")
extraction_config = load_client_cfg(extraction_config_path)
_assert_examples(classification_config["classification_schema"], "classification")


LOGGER.info("Step 2/3  – Paragraph classification (%s-shot)", config["prompt_mode_classification"])
clf = ExtractorClassifier(
    config= classification_config,               # folder, not file ⇒ loads provider config
    provider=classification_config["provider"],
    schema_file=classification_config["classification_schema"],
    prompt_mode=config["prompt_mode_classification"],
    num_exem=config["num_exem"],          # ignored for few-shot
    output_dir=WORK / "classification",
    logger=LOGGER,
    metadata=META,
    chosen_examples=None,            # external override no longer supported
    debug_io=config["debug_io"],
)


pred_all, relevant_only, cls_prompt = clf.predict(paragraphs)
import threading
for thread in threading.enumerate():
    print(f"Active Thread: {thread.name}")
    
(WORK / "classification/classified_full.json").write_text(
    json.dumps(pred_all, indent=2, ensure_ascii=False)
)
(WORK / "classification/classified_relevant.json").write_text(
    json.dumps(relevant_only, indent=2, ensure_ascii=False)
)

# ─────────────────────────── 3) Extraction ───────────────────────────
_assert_examples(extraction_config["extraction_schema"], "extraction")
LOGGER.info("Step 3/3  – Structured extraction (%s-shot)", config["prompt_mode_extraction"])

ks = ExtractorStructurer(
    config=load_client_cfg(extraction_config_path),
    provider=extraction_config["provider"],
    schema_file=extraction_config["extraction_schema"],
    prompt_mode=config["prompt_mode_extraction"],
    num_exem=config["num_exem"],
    output_dir=WORK / "extraction",
    logger=LOGGER,
    metadata=META,
    chosen_examples=None,
    debug_io=config["debug_io"],
)
structured, ext_prompt = ks.predict(relevant_only)

(WORK / "extraction/structured.json").write_text(
    json.dumps(structured, indent=2, ensure_ascii=False)
)

# ─────────────────────────── 4) Metadata ───────────────────────────
META.write(WORK / "general_metadata.json")
(WORK / "llm_metadata.json").write_text(
    json.dumps(
        {
            "timestamp":             timestamp,
            "classification_model":  classification_config["model_id"],
            "extraction_model":                 extraction_config["model_id"],
            "classification_provider":              classification_config["provider"],
            "extraction_provider":                  extraction_config["provider"],
            "prompt_mode_cl":        config["prompt_mode_classification"],
            "prompt_mode_ex":        config["prompt_mode_extraction"],
            "classification_prompt": cls_prompt,
            "extraction_prompt":     ext_prompt,
            "cls_schema":            extraction_config["classification_schema"],
            "ext_schema":            extraction_config["extraction_schema"],
            "cls_example_count":     classification_config["classification_schema"].get("examples", []),
            "ext_example_count":     extraction_config["extraction_schema"].get("examples", [])
        },
        indent=2,
        ensure_ascii=False,
    )
)

end_time = time.time()
print("✅  Pipeline finished →", WORK)
print(f"Time taken: {end_time - start_time:.0f} seconds.")