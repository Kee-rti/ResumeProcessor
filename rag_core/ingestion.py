import logging
import tempfile
from pathlib import Path
from typing import Optional

import pdfplumber

logger = logging.getLogger(__name__)


class ResumeExtractor:
    def extract_text(self, file_path: str | Path) -> Optional[str]:
        path = Path(file_path)
        if not path.exists():
            logger.error("File not found: %s", path)
            return None

        if path.suffix.lower() == ".pdf":
            return self._extract_from_pdf(path)
        if path.suffix.lower() == ".docx":
            return self._extract_from_docx(path)

        logger.error("Unsupported file format: %s", path.suffix)
        return None

    def extract_uploaded_file(self, uploaded_file) -> Optional[str]:
        """Extract text from a Django UploadedFile without persisting it."""
        suffix = Path(uploaded_file.name).suffix.lower()
        if suffix not in {".pdf", ".docx"}:
            return None

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                for chunk in uploaded_file.chunks():
                    tmp.write(chunk)
                temp_path = Path(tmp.name)

            return self.extract_text(temp_path)
        finally:
            if temp_path and temp_path.exists():
                temp_path.unlink(missing_ok=True)

    def _extract_from_pdf(self, path: Path) -> Optional[str]:
        extracted_text = []
        try:
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text.append(text)

            full_text = "\n".join(extracted_text)
            logger.info("Extracted %d characters from %s", len(full_text), path.name)
            return full_text
        except Exception:
            logger.exception("Error extracting PDF %s", path.name)
            return None

    def _extract_from_docx(self, path: Path) -> Optional[str]:
        try:
            import docx

            doc = docx.Document(path)
            full_text = "\n".join(
                paragraph.text for paragraph in doc.paragraphs if paragraph.text
            )
            logger.info("Extracted %d characters from %s", len(full_text), path.name)
            return full_text
        except Exception:
            logger.exception("Error extracting DOCX %s", path.name)
            return None
