"""
Extracts text from validated PDF files using pdfplumber in memory.
"""

import io
import re
import pdfplumber
from pdfplumber.utils.exceptions import PdfminerException
from pdfminer.pdfdocument import PDFPasswordIncorrect

from src.config import MAX_PAGE_COUNT, MIN_MEANINGFUL_TEXT_LENGTH
from src.ingestion.pdf_validator import validate_pdf_bytes
from src.ingestion.models import ExtractionResult
from src.ingestion.exceptions import (
    CorruptPDFError,
    PasswordProtectedPDFError,
    TooManyPagesError,
    NoMeaningfulTextError
)

def extract_text_from_pdf_bytes(file_bytes: bytes, filename: str) -> ExtractionResult:
    """
    Validates and extracts text from a PDF securely in memory.
    """
    # 1. Call validator before parsing
    validate_pdf_bytes(file_bytes, filename)

    warnings = []
    text_pages = []

    # 2. Open PDF from memory
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            # 5. Reject documents exceeding maximum pages
            page_count = len(pdf.pages)
            if page_count > MAX_PAGE_COUNT:
                raise TooManyPagesError("The PDF exceeds the maximum allowed page count.")
            
            # 6. Extract text page by page
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                # 7. Safely handle None
                if page_text is None:
                    warnings.append(f"Page {i+1} returned no text.")
                    continue
                # 9. Normalise excessive whitespace without destroying line structure
                # Replace multiple spaces with a single space, but leave newlines
                page_text = re.sub(r'[^\S\r\n]+', ' ', page_text)
                text_pages.append(page_text.strip())

    except PdfminerException as e:
        if e.args and isinstance(e.args[0], PDFPasswordIncorrect):
            # 4. Reject encrypted/password-protected PDFs
            raise PasswordProtectedPDFError("The PDF is password protected or encrypted.") from e
        # 3. Reject corrupt/unreadable PDFs
        raise CorruptPDFError("The PDF is corrupt or unreadable.") from e

    # 8. Preserve reasonable page separation
    full_text = "\n\n".join(text_pages).strip()

    # 10. Reject documents with fewer than 30 meaningful characters
    # Count non-whitespace characters
    meaningful_char_count = len(re.sub(r'\s+', '', full_text))
    if meaningful_char_count < MIN_MEANINGFUL_TEXT_LENGTH:
        raise NoMeaningfulTextError("No meaningful extractable text found. The document may be an image-only scan.")

    # 11. Return validated Pydantic model
    return ExtractionResult(
        original_filename=filename,
        page_count=page_count,
        extracted_text=full_text,
        extracted_character_count=len(full_text),
        appears_text_based=True,
        warnings=warnings
    )
