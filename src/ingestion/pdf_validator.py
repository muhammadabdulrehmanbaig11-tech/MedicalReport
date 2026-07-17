"""
Validates uploaded PDF files securely before processing.
"""

import os
from dataclasses import dataclass
from src.config import MAX_PDF_SIZE_BYTES, ALLOWED_EXTENSION
from src.ingestion.exceptions import (
    EmptyFileError,
    InvalidFileTypeError,
    OversizedFileError,
    CorruptPDFError
)

@dataclass
class ValidationMetadata:
    filename: str
    size_bytes: int

def validate_pdf_bytes(file_bytes: bytes, filename: str) -> ValidationMetadata:
    """
    Validates the PDF bytes and filename securely.
    Returns ValidationMetadata on success, or raises a DocumentProcessingError.
    """
    if not file_bytes:
        raise EmptyFileError("The uploaded file is empty.")

    if not filename or filename.strip() == "" or os.path.splitext(filename)[0].strip() == "":
        raise InvalidFileTypeError("The uploaded file has no valid filename.")

    ext = os.path.splitext(filename)[1].lower()
    if ext != ALLOWED_EXTENSION:
        raise InvalidFileTypeError("The uploaded file must be a PDF document.")

    size = len(file_bytes)
    if size > MAX_PDF_SIZE_BYTES:
        raise OversizedFileError("The uploaded file exceeds the 10 MB size limit.")

    if not file_bytes.startswith(b"%PDF-"):
        raise CorruptPDFError("The uploaded file does not have a valid PDF signature.")

    return ValidationMetadata(filename=filename, size_bytes=size)
