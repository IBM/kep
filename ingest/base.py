from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

class BaseParser(ABC):
    """
    The Abstract Base Class that defines the interface for all document parsers.
    """
    
    @abstractmethod
    def parse(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parses a document and extracts its text and metadata.
        
        Args:
            file_path: The path to the document file.
            
        Returns:
            A tuple containing the extracted text (str) and metadata (dict).
        """
        pass