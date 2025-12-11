from typing import Dict, Any, Tuple
import io
from .base import BaseParser

# --- Installation Check and Safe Import for PyMuPDF, Pillow, and Tesseract ---
try:
    import fitz  # PyMuPDF
except ImportError:
    print("Warning: 'pymupdf' is not installed. PyMuPDFParser will not be available.")
    print("You can install it by running: pip install pymupdf")
    fitz = None

try:
    from PIL import Image
    import pytesseract
except ImportError:
    print("Warning: 'pillow' or 'pytesseract' is not installed. OCR functionality will fail.")
    print("You can install them by running: pip install pillow pytesseract")
    Image = None
    pytesseract = None


class PyMuPDFParser(BaseParser):
    """
    A concrete parser implementation that uses PyMuPDF (fitz) for text extraction
    and Tesseract OCR as a fallback for scanned pages.
    """

    def parse(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        if fitz is None:
            raise RuntimeError("The 'pymupdf' library is required to use PyMuPDFParser.")
        if Image is None or pytesseract is None:
             raise RuntimeError("The 'pillow' and 'pytesseract' libraries are required for this parser.")

        print(f"--> Using PyMuPDFParser on {file_path}...")

        OCR_LANGUAGE = 'en'
        OCR_DPI = 300
        TEXT_THRESHOLD = 100
        
        total_text = ""
        metadata = {}

        try:
            doc = fitz.open(str(file_path))
            
            if doc.metadata:
                metadata = doc.metadata

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                page_text = page.get_text().strip()
                
                if len(page_text) > TEXT_THRESHOLD:
                    total_text += page_text + "\n"
                else:
                    zoom = OCR_DPI / 72
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat)
                    
                    img_data = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_data))
                    
                    try:
                        extracted = pytesseract.image_to_string(img, lang=OCR_LANGUAGE)
                        total_text += extracted + "\n"
                    except Exception as ocr_error:
                        print(f"Warning: OCR failed on page {page_num}: {ocr_error}")
                        pass
            
            doc.close()
            return total_text.strip()

        except Exception as e:
            raise RuntimeError(f"Error parsing PDF with PyMuPDF: {e}")