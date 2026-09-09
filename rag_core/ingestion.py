import pdfplumber
import logging
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeExtractor:
    def __init__(self):
        pass

    def extract_text(self, pdf_path: str | Path) -> Optional[str]:
        """
        Extracts raw text from a PDF or DOCX resume.
        """
        path = Path(pdf_path)
        if not path.exists():
            logger.error(f"File not found: {path}")
            return None
        
        if path.suffix.lower() == '.pdf':
            return self._extract_from_pdf(path)
        elif path.suffix.lower() == '.docx':
            return self._extract_from_docx(path)
        else:
            logger.error(f"Unsupported file format: {path.suffix}. Expected .pdf or .docx")
            return None

    def _extract_from_pdf(self, path: Path) -> Optional[str]:
        extracted_text = []
        try:
            with pdfplumber.open(path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        extracted_text.append(text)
            
            full_text = "\n".join(extracted_text)
            logger.info(f"Successfully extracted {len(full_text)} characters from {path.name}")
            return full_text
        except Exception as e:
            logger.error(f"Error extracting text from {path.name}: {e}")
            return None

    def _extract_from_docx(self, path: Path) -> Optional[str]:
        try:
            import docx
            doc = docx.Document(path)
            full_text = "\n".join([para.text for para in doc.paragraphs])
            logger.info(f"Successfully extracted {len(full_text)} characters from {path.name}")
            return full_text
        except Exception as e:
            logger.error(f"Error extracting text from {path.name}: {e}")
            return None
