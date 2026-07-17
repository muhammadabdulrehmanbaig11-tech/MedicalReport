import io
import pytest
import pdfplumber

from src.ingestion.pdf_extractor import extract_text_from_pdf_bytes
from src.analysis.lab_parser import parse_laboratory_results
from src.analysis.models import ResultStatus
from src.export.pdf_summary import generate_report_summary_pdf

def test_end_to_end_workflow():
    # Read the synthetic demonstration report
    with open("samples/sample_lab_report.pdf", "rb") as f:
        pdf_bytes = f.read()
        
    # 1. secure PDF validation & text extraction
    result = extract_text_from_pdf_bytes(pdf_bytes, "sample_lab_report.pdf")
    assert len(result.extracted_text) > 50
    
    # 2. laboratory parsing
    lab_results = parse_laboratory_results(result.extracted_text)
    
    # Check expected laboratory rows are detected
    assert len(lab_results) == 5
    
    # Check LOW, NORMAL and HIGH statuses are produced
    statuses = {r.test_name: r.status for r in lab_results}
    assert statuses.get("Hemoglobin") == ResultStatus.LOW
    assert statuses.get("Glucose") == ResultStatus.NORMAL
    assert statuses.get("Platelets") == ResultStatus.NORMAL
    assert statuses.get("TSH") == ResultStatus.HIGH
    assert statuses.get("Ferritin") == ResultStatus.NORMAL
    
    # 3. downloadable summary PDF generated without AI service
    summary_pdf_bytes = generate_report_summary_pdf(lab_results, ai_explanation=None)
    
    # Verify the output PDF starts with %PDF-
    assert summary_pdf_bytes.startswith(b"%PDF-")
    
    # The output PDF can be reopened using pdfplumber
    with pdfplumber.open(io.BytesIO(summary_pdf_bytes)) as pdf:
        text = pdf.pages[0].extract_text()
        
    # The summary contains the synthetic test names
    assert "Hemoglobin" in text
    assert "Glucose" in text
    assert "Platelets" in text
    assert "TSH" in text
    assert "Ferritin" in text
    
    # The summary contains the medical disclaimer
    assert "educational purposes only" in text
    assert "not a diagnosis" in text
    
    # Raw source lines are not exported
    # The original string with the pipe chars is not found
    assert "Glucose | 96 | mg/dL | 70 - 99" not in text
