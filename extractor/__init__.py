"""
extractor package
─────────────────
Public façade:

    from extractor import run_pipeline

    run_pipeline(
        ingest_dir      = "runs/demo/ingest",      # produced by PdfConverter
        work_dir        = "runs/demo/extractor",   # results here
        cfg_file        = "config/model_config.yaml",
        provider        = "watsonx",
        model_id        = "mistralai/mistral-large",
        cls_schema      = "schemas/classification.json",
        ext_schema      = "schemas/extraction.json",
        prompt_mode     = "few",                   # "zero" or "few"
        num_examples    = 3
    )
"""
from pathlib import Path
from .pipeline import ExtractorPipeline


def run_pipeline(
    *,
    ingest_dir: str | Path,
    work_dir:   str | Path,
    cfg_file:   str,
    provider:   str,
    model_id:   str,
    cls_schema: str | Path,
    ext_schema: str | Path,
    prompt_mode: str = "zero",
    num_examples: int = 0,
):
    """Convenience wrapper – instantiates `ExtractorPipeline` and runs it."""
    pipe = ExtractorPipeline(
        ingest_dir   = Path(ingest_dir),
        work_dir     = Path(work_dir),
        cfg_file     = cfg_file,
        provider     = provider,
        model_id     = model_id,
        cls_schema   = cls_schema,
        ext_schema   = ext_schema,
        prompt_mode  = prompt_mode,
        num_examples = num_examples,
    )
    pipe.run()