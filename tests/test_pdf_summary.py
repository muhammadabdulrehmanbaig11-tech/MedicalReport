import io
import pytest
from decimal import Decimal
import pdfplumber

from src.analysis.models import LaboratoryResult, ResultStatus
from src.export.pdf_summary import generate_report_summary_pdf
from src.export.exceptions import ReportExportError

def test_no_results_raises_exception():
    with pytest.raises(ReportExportError):
        generate_report_summary_pdf([])

def test_one_result_produces_valid_pdf_bytes():
    results = [LaboratoryResult(test_name="Glucose", value=Decimal("90"), status=ResultStatus.NORMAL, source_line="Glucose 90")]
    pdf_bytes = generate_report_summary_pdf(results)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")

def test_multiple_results_and_statuses():
    results = [
        LaboratoryResult(test_name="Glucose", value=Decimal("90"), status=ResultStatus.NORMAL, source_line="fake source line"),
        LaboratoryResult(test_name="Hemoglobin", value=Decimal("12"), status=ResultStatus.LOW, source_line="fake source line"),
        LaboratoryResult(test_name="Cholesterol", value=Decimal("250"), status=ResultStatus.HIGH, source_line="fake source line"),
        LaboratoryResult(test_name="Unknown", value=Decimal("5"), status=ResultStatus.UNDETERMINED, source_line="fake source line")
    ]
    pdf_bytes = generate_report_summary_pdf(results)
    
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        text = pdf.pages[0].extract_text()
        
    assert "Glucose" in text
    assert "Hemoglobin" in text
    assert "Cholesterol" in text
    assert "Unknown" in text
    assert "NORMAL" in text
    assert "LOW" in text
    assert "HIGH" in text
    assert "UNDETERMINED" in text

def test_reference_ranges_and_missing_units():
    results = [
        # closed
        LaboratoryResult(test_name="TestA", value=Decimal("1"), reference_low=Decimal("0"), reference_high=Decimal("2"), status=ResultStatus.NORMAL, source_line="fake source line"),
        # upper-only
        LaboratoryResult(test_name="TestB", value=Decimal("1"), reference_high=Decimal("5"), status=ResultStatus.NORMAL, source_line="fake source line"),
        # lower-only
        LaboratoryResult(test_name="TestC", value=Decimal("10"), reference_low=Decimal("5"), status=ResultStatus.NORMAL, source_line="fake source line"),
        # missing unit / missing reference
        LaboratoryResult(test_name="TestD", value=Decimal("10"), status=ResultStatus.NORMAL, source_line="fake source line")
    ]
    pdf_bytes = generate_report_summary_pdf(results)
    
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        text = pdf.pages[0].extract_text()
        
    assert "0 - 2" in text
    assert "< 5" in text
    assert "> 5" in text
    assert "TestD" in text

def test_ai_explanation():
    results = [LaboratoryResult(test_name="Glucose", value=Decimal("90"), status=ResultStatus.NORMAL, source_line="fake source line")]
    
    # Optional - none provided
    pdf_no_ai = generate_report_summary_pdf(results)
    with pdfplumber.open(io.BytesIO(pdf_no_ai)) as pdf:
        assert "AI-Generated" not in pdf.pages[0].extract_text()
        
    # Blank provided
    pdf_blank_ai = generate_report_summary_pdf(results, ai_explanation="   ")
    with pdfplumber.open(io.BytesIO(pdf_blank_ai)) as pdf:
        assert "AI-Generated" not in pdf.pages[0].extract_text()
        
    # Provided
    pdf_ai = generate_report_summary_pdf(results, ai_explanation="This is a test explanation.")
    with pdfplumber.open(io.BytesIO(pdf_ai)) as pdf:
        text = pdf.pages[0].extract_text()
        assert "AI-Generated Plain-Language Explanation" in text
        assert "This is a test explanation." in text

def test_disclaimers_and_exclusions():
    results = [LaboratoryResult(test_name="Glucose", value=Decimal("90"), status=ResultStatus.NORMAL, source_line="SECRET_SOURCE_LINE_999")]
    pdf_bytes = generate_report_summary_pdf(results)
    
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        text = pdf.pages[0].extract_text()
        
    assert "educational purposes only" in text
    assert "privacy" not in text.lower() # The statement says "The uploaded PDF and extracted report text are not included"
    assert "uploaded PDF and extracted report text" in text
    
    assert "SECRET_SOURCE_LINE_999" not in text
    assert "John Doe" not in text

def test_long_names_and_unicode():
    long_name = "This is a very long test name that should wrap correctly " * 5
    unicode_name = "Test \u2013 \u03bcg"
    results = [
        LaboratoryResult(test_name=long_name, value=Decimal("90"), status=ResultStatus.NORMAL, source_line="fake source line"),
        LaboratoryResult(test_name=unicode_name, value=Decimal("90"), status=ResultStatus.NORMAL, source_line="fake source line")
    ]
    
    pdf_bytes = generate_report_summary_pdf(results)
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        text = pdf.pages[0].extract_text()
        assert "Test - ug" in text # replaced by safe encoding
        # Decimal precision test
        assert "90" in text
