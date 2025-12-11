from typing import Dict, Any, Tuple
from .base import BaseParser

try:
    from docling.datamodel.base_models import ConversionStatus
    from docling.document_converter    import DocumentConverter
except ImportError:
    print("Warning: 'docling' (or its components) is not installed. The DoclingParser will not be available.")
    print("You can install it by running: pip install docling-core")
    DocumentConverter = None
    ConversionStatus = None

class DoclingParser(BaseParser):
    """
    A concrete parser implementation that uses the 'docling' library
    to extract content and metadata from various file types.
    
    This version uses the DocumentConverter class.
    """
    
    def __init__(self, **kwargs):
        """
        Initializes the DocumentConverter.
        Any keyword arguments (e.g., 'ocr_enabled=True') are passed to the converter.
        """
        if DocumentConverter is None:
            raise RuntimeError(
                "'docling' package is required to use DoclingParser. "
                "Please run: pip install docling-core"
            )
            
        self.converter = DocumentConverter(**kwargs)
        print("--> Initialized DoclingParser with DocumentConverter.")

    def parse(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Implements the parsing logic using the 'docling' DocumentConverter.
        
        This method fulfills the contract established by the BaseParser interface.
        """
        if self.converter is None or ConversionStatus is None:
            raise RuntimeError("'docling' package is not correctly initialized.")
            
        print(f"--> Using DoclingParser (DocumentConverter) for: {file_path}")
        
        conversion_result = self.converter.convert(file_path)
        
        if conversion_result.status != ConversionStatus.SUCCESS:
            raise RuntimeError(
                f"Docling failed to parse file '{file_path}'. "
                f"Status: {conversion_result.status.name} "
                f"Message: {conversion_result.message}"
            )
        
        doc = conversion_result.document
        
        if doc is None:
            text = ''
        else:
            text = doc.export_to_markdown() or ''
            
        
        return text.strip()