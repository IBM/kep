#!/usr/bin/env python3
"""
ingest/pdf_converter.py

Convert every PDF in a folder to Markdown via Docling, then split the
text into chunks (fixed, sentence or paragraph).
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Any
import json
import unicodedata
import re 


# Progress / logging
from common.progress     import ProgressTracker
from common.file_logger  import FileLogger
from common.metadata     import MetadataRecorder

# Local chunker
from ingest.base import BaseParser
from ingest.chunker      import Chunker
from ingest.factory import ParserFactory


@dataclass
class ConvertedDoc:
    source: str
    paragraphs: List[str]
    content: Optional[str] = None

class PdfConverter:
    @staticmethod
    def _split_paragraphs(md: str) -> List[str]:
        return [p.strip() for p in md.split("\n\n") if p.strip()]
        
    @staticmethod
    def get_target_sections(md: str, logger) -> str:

        def normalize_heading(h: str) -> str:
            h = ''.join(ch for ch in h if unicodedata.category(ch)[0] != 'So')
            h = h.strip("# ").strip()
            h = h.lower()
            return h

        def split_sections_teste(md: str) -> Dict[str, str]:
            lines = md.splitlines()
            sections = {}
            current_heading = "preamble"
            buffer: List[str] = []

            for idx, line in enumerate(lines):
                stripped = line.strip()

                if stripped.lower().startswith("abstract"):
                    if buffer:
                        sections[current_heading] = "\n".join(buffer).strip()
                        buffer = []
                    current_heading = "abstract"
                    buffer.append(stripped[len("abstract "):].strip())
                    continue

                # Detecta heading (Markdown ou caixa alta curta)
                if stripped.startswith("#"):
                    if buffer:
                        sections[current_heading] = "\n".join(buffer).strip()
                        buffer = []
                    current_heading = normalize_heading(stripped)
                else:
                    buffer.append(line)

            if buffer:
                sections[current_heading] = "\n".join(buffer).strip()

            return sections

        def get_abstract(sections: Dict[str, str]) -> str:
            for key in sections:
                if "abstract" in key:
                    return "ABSTRACT\n" + sections[key]
            logger.warning("Abstract not found")
            return ""

        def get_results_and_discussion(sections: Dict[str, str]) -> str:
            res_keys = [k for k in sections if "results" in k and "discussion" in k]
            if not res_keys:
                logger.warning("Results and Discussion not found")
                return ""
            
            start_key = res_keys[0]
            collected = [sections[start_key]]
            take = False

            for key, content in sections.items():
                if key == start_key:
                    take = True
                    continue
                if take:
                    # se achou uma seção "de saída", para
                    if any(stop in key for stop in ["conclusion", "reference", "acknowledgement"]):
                        break
                    # senão acumula como subseção
                    collected.append(f"{key.upper()}\n{content}")

            return "RESULTS AND DISCUSSION\n" + "\n\n".join(collected)

        # pipeline
        sections = split_sections_teste(md)
        abstract = get_abstract(sections)
        results = get_results_and_discussion(sections)

        return "\n\n".join(s for s in [abstract, results] if s)

    # def _get_sections(md: str, logger) -> List[str]:
    #     sections = []

    #     match_abs = re.search(
    #         r"ABSTRACT(.*?)(?=\n## )",
    #         md,
    #         re.DOTALL)
        
    #     match_res = re.search(r"## ■ RESULTS AND DISCUSSION(.*?)(?=\n## ■[A-Z0-9 _-]+)", md, re.DOTALL)
        
    #     if match_abs:
    #         sections.append(match_abs.group(0).strip())
        
    #     if match_res:
    #         sections.append("RESULTS AND DISCUSSION" + match_res.group(1).strip())
    #     else:
    #         match_res_num = re.search(
    #         r"##\s*\d+\.\s*RESULTS AND DISCUSSION(.*?)(?=\n##\s*\d+\.)",
    #         md,
    #         re.DOTALL | re.IGNORECASE
    #         )
    #         if match_res_num:
    #             sections.append("RESULTS AND DISCUSSION" + match_res_num.group(1).strip())
    #         else:
    #             logger.error("Results and Discussion pattern unknown")
        
        
    #     return "\n\n".join(sections) 

    # ────────────────────────────────────────────────────────────
    @classmethod
    def convert_dir(
        cls,
        parser_name: str,
        dir_in: Path,
        dir_out: Path,
        *,
        logger: FileLogger,
        metadata: Optional[MetadataRecorder] = None,
        output_mode: str = "per_pdf",
        chunk_strategy: str = "paragraph",
        chunk_size: int = 100,
        chunk_overlap: int = 25,
    ) -> Tuple[List[ConvertedDoc], Dict]:
        """
        dir_in        – folder with PDFs
        dir_out       – where JSON chunk files are written
        chunk_strategy: fixed | sentence | paragraph
        """

        dir_in, dir_out = Path(dir_in), Path(dir_out)
        dir_out.mkdir(parents=True, exist_ok=True)

        def replacer(match):
                code = match.group(1)  
                return chr(int(code, 16)) 

        def normalize_uni_codes(text: str) -> str:
            text = re.sub(r"/uni([A-F0-9]{4})", replacer, text)

            text = re.sub(r"\s*([ﬀﬁﬂﬃﬄﬅﬆ])\s*", r"\1", text)

            return text

        pdfs = sorted(dir_in.glob("*.pdf"))
        if not pdfs:
            raise FileNotFoundError(f"No PDFs found in {dir_in}")

        tracker   = ProgressTracker("conversion", logger, metadata, total=len(pdfs))
        converter: BaseParser = ParserFactory.create(parser_name)
        docs: List[ConvertedDoc] = []

        for pdf in pdfs:
            file_name = pdf
            try:
                parsed_text = converter.parse(pdf)
            except Exception as e:
                logger.error(f"Conversion failed: {file_name}. Error: {e}")
                raise e
                continue
            parsed_text = normalize_uni_codes(parsed_text)
            tracker.tick(file_name)

            pdf_stem = file_name.stem

            # Perform chunking as before
            if chunk_strategy == "paragraph":
                paragraphs = cls._split_paragraphs(parsed_text)
            elif chunk_strategy == "sections":
                sections = cls.get_target_sections(parsed_text, logger=logger)

                chunker = Chunker(
                    strategy=chunk_strategy,
                    size=chunk_size,
                    overlap=chunk_overlap,
                )
                paragraphs = chunker.split(sections)
            else:
                # use generic Chunker
                chunker = Chunker(
                    strategy=chunk_strategy,
                    size=chunk_size,
                    overlap=chunk_overlap,
                )
                paragraphs = chunker.split(parsed_text)

            docs.append(ConvertedDoc(
                source=pdf_stem, 
                paragraphs=paragraphs,
                content=parsed_text,
            ))

        tracker.done(success=len(docs))

        # ── write JSON output ─────────────────────────────────────
        if output_mode == "combined":
            combined = [
                {"Source": d.source, "Text": p}
                for d in docs for p in d.paragraphs
            ]
            (dir_out / "all_paragraphs.json").write_text(
                json.dumps(combined, indent=2, ensure_ascii=False)
            )
        else:
            for d in docs:
                payload = [{"Source": d.source, "Text": p} for p in d.paragraphs]
                (dir_out / f"{d.source}_paragraphs.json").write_text(
                    json.dumps(payload, indent=2, ensure_ascii=False)
                )

        summary = {
            "count": len(docs)
        }
        
        return docs, summary
