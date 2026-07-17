"""
Ingestion module for handling PDF uploads and text extraction.
"""

from .exceptions import (
    DocumentProcessingError,
    InvalidFileTypeError,
    OversizedFileError,
    EmptyFileError,
    CorruptPDFError,
    TooManyPagesError,
    PasswordProtectedPDFError,
    NoMeaningfulTextError
)
from .models import ExtractionResult
from .pdf_validator import validate_pdf_bytes, ValidationMetadata
from .pdf_extractor import extract_text_from_pdf_bytes
