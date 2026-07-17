import pytest
from src.ingestion.pdf_validator import validate_pdf_bytes
from src.ingestion.exceptions import (
    EmptyFileError,
    InvalidFileTypeError,
    OversizedFileError,
    CorruptPDFError
)
from src.config import MAX_PDF_SIZE_BYTES

def test_valid_minimal_pdf_signature_and_filename():
    meta = validate_pdf_bytes(b"%PDF-1.4\ncontent", "report.pdf")
    assert meta.filename == "report.pdf"
    assert meta.size_bytes == 16

def test_empty_bytes():
    with pytest.raises(EmptyFileError):
        validate_pdf_bytes(b"", "report.pdf")

def test_non_pdf_extension():
    with pytest.raises(InvalidFileTypeError):
        validate_pdf_bytes(b"%PDF-1.4", "report.txt")

def test_uppercase_pdf_acceptance():
    meta = validate_pdf_bytes(b"%PDF-1.4", "REPORT.PDF")
    assert meta.filename == "REPORT.PDF"

def test_invalid_pdf_signature():
    with pytest.raises(CorruptPDFError):
        validate_pdf_bytes(b"PK\x03\x04...", "report.pdf")

def test_file_larger_than_configured_limit():
    large_bytes = b"%PDF-" + b"0" * MAX_PDF_SIZE_BYTES
    with pytest.raises(OversizedFileError):
        validate_pdf_bytes(large_bytes, "large.pdf")

def test_filename_consisting_only_of_whitespace():
    with pytest.raises(InvalidFileTypeError):
        validate_pdf_bytes(b"%PDF-1.4", "   .pdf")

def test_misleading_pdf_filename_containing_non_pdf_bytes():
    with pytest.raises(CorruptPDFError):
        validate_pdf_bytes(b"<html><body>Not a PDF</body></html>", "fake.pdf")
