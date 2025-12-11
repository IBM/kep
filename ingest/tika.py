from typing import Dict, Any, Tuple
from .base import BaseParser

# --- Installation Check and Safe Import for Tika ---
try:
    from tika import parser as tika_parser
except ImportError:
    print("Warning: The 'tika' library is not installed. TikaParser will not be available.")
    print("You can install it by running: pip install tika")
    tika_parser = None

class TikaParser(BaseParser):
    """
    A concrete parser implementation that uses the Apache Tika library
    to extract content and metadata from various file types.
    """
    
    def parse(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Implements the parsing logic using the 'tika' library.
        
        This method fulfills the contract established by the BaseParser interface.
        """
        if tika_parser is None:
            raise RuntimeError("The 'tika' library is required to use TikaParser.")
            
        print("--> Using TikaParser...")
    
        parsed_data = tika_parser.from_file(str(file_path))
        
        if not parsed_data:
            return ""
        
        text = parsed_data.get('content', '') or ''
        
        return text.strip()