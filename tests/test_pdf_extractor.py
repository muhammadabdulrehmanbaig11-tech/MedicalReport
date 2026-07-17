import io
import pytest
from fpdf import FPDF

from src.ingestion.pdf_extractor import extract_text_from_pdf_bytes
from src.ingestion.exceptions import (
    CorruptPDFError,
    PasswordProtectedPDFError,
    TooManyPagesError,
    NoMeaningfulTextError
)
from src.config import MAX_PAGE_COUNT

def create_synthetic_pdf(pages_text):
    """Helper to create a synthetic PDF in memory using fpdf2."""
    pdf = FPDF()
    for text in pages_text:
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        if text.strip():
            pdf.cell(200, 10, text=text, new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())

def test_successful_extraction_valid_text_pdf():
    # Real generated PDF and real pdfplumber.open
    pdf_bytes = create_synthetic_pdf(["This is a test document with more than thirty meaningful characters."])
    result = extract_text_from_pdf_bytes(pdf_bytes, "test.pdf")
    assert "thirty meaningful characters" in result.extracted_text
    assert result.original_filename == "test.pdf"
    assert result.page_count == 1
    assert result.appears_text_based is True
    assert len(result.warnings) == 0

def test_multiple_page_extraction():
    # Real generated PDF
    text1 = "Page one text must be long enough to pass validation thresholds."
    text2 = "Page two text also has some content for the extraction process."
    pdf_bytes = create_synthetic_pdf([text1, text2])
    result = extract_text_from_pdf_bytes(pdf_bytes, "multi.pdf")
    assert result.page_count == 2
    assert text1 in result.extracted_text
    assert text2 in result.extracted_text

def test_corrupt_pdf():
    # Real corrupt bytes
    with pytest.raises(CorruptPDFError):
        extract_text_from_pdf_bytes(b"%PDF-1.4 corrupt data \x00\x01\x02", "corrupt.pdf")

def test_encrypted_or_password_protected_pdf(monkeypatch):
    # Mocking library condition that cannot reasonably be generated simply with fpdf2
    import pdfplumber
    from pdfplumber.utils.exceptions import PdfminerException
    from pdfminer.pdfdocument import PDFPasswordIncorrect
    
    def mock_open(*args, **kwargs):
        raise PdfminerException(PDFPasswordIncorrect("Password required"))
        
    monkeypatch.setattr(pdfplumber, "open", mock_open)
    pdf_bytes = b"%PDF-1.4 dummy valid start to pass validation"
    with pytest.raises(PasswordProtectedPDFError):
        extract_text_from_pdf_bytes(pdf_bytes, "locked.pdf")

def test_pdf_exceeding_page_limit():
    pages = ["Page text " + str(i) for i in range(MAX_PAGE_COUNT + 1)]
    pdf_bytes = create_synthetic_pdf(pages)
    with pytest.raises(TooManyPagesError):
        extract_text_from_pdf_bytes(pdf_bytes, "too_long.pdf")

def test_scanned_or_image_only_pdf_no_meaningful_text():
    # Real generated PDF for low-text rejection (no text/image only equivalent)
    pdf_bytes = create_synthetic_pdf([" "])
    with pytest.raises(NoMeaningfulTextError):
        extract_text_from_pdf_bytes(pdf_bytes, "scanned.pdf")

def test_text_below_minimum_meaningful_character_threshold():
    # Real generated PDF
    pdf_bytes = create_synthetic_pdf(["Too short"])
    with pytest.raises(NoMeaningfulTextError):
        extract_text_from_pdf_bytes(pdf_bytes, "short.pdf")

def test_output_model_metadata_consistency():
    pdf_bytes = create_synthetic_pdf(["This text is exactly enough to be more than thirty meaningful characters."])
    result = extract_text_from_pdf_bytes(pdf_bytes, "meta.pdf")
    assert result.extracted_character_count == len(result.extracted_text)

def test_validation_happens_before_parsing(monkeypatch):
    # Mocking to prove validation occurs before parsing
    import pdfplumber
    calls = []
    def mock_validate(b, f):
        calls.append("validate")
    def mock_open(*args, **kwargs):
        calls.append("open")
        raise CorruptPDFError()
        
    monkeypatch.setattr("src.ingestion.pdf_extractor.validate_pdf_bytes", mock_validate)
    monkeypatch.setattr(pdfplumber, "open", mock_open)
    
    with pytest.raises(CorruptPDFError):
        extract_text_from_pdf_bytes(b"%PDF-valid", "mocked.pdf")
        
    assert calls == ["validate", "open"]

def test_page_returning_no_text(monkeypatch):
    # Simulate a page where extract_text returns None. 
    import pdfplumber
    class MockPage:
        def extract_text(self):
            return None
    class MockPage2:
        def extract_text(self):
            return "Valid text that passes the thirty character threshold limit."
    class MockPDF:
        def __init__(self):
            self.pages = [MockPage(), MockPage2()]
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
            
    def mock_open(*args, **kwargs):
        return MockPDF()
        
    monkeypatch.setattr(pdfplumber, "open", mock_open)
    pdf_bytes = b"%PDF-1.4 dummy valid start"
    result = extract_text_from_pdf_bytes(pdf_bytes, "empty_page.pdf")
    assert result.page_count == 2
    assert len(result.warnings) == 1
    assert "Page 1 returned no text." in result.warnings[0]
