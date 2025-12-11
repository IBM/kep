import os

from ingest.base import BaseParser
from ingest.docling import DoclingParser
from ingest.tika import TikaParser
from ingest.pymupdf import PyMuPDFParser
PARSER_REGISTRY = {
    "tika": TikaParser,
    "docling": DoclingParser,
    "pymupdf": PyMuPDFParser
}
class ParserFactory:
    @classmethod
    def create(cls, parser_name: str) -> BaseParser:
        """
        Factory function to get a parser instance by its name.
        """
        parser_class = PARSER_REGISTRY.get(parser_name.lower())
        
        if not parser_class:
            raise ValueError(f"Unsupported parser: '{parser_name}'. Available: {list(PARSER_REGISTRY.keys())}")
            
        return parser_class()

