from decimal import Decimal
from src.analysis.lab_parser import parse_laboratory_results
from src.analysis.models import ResultStatus

def test_standard_space_separated_row():
    text = "Hemoglobin 12.5 g/dL 13.0 - 17.0"
    results = parse_laboratory_results(text)
    assert len(results) == 1
    assert results[0].test_name == "Hemoglobin"
    assert results[0].value == Decimal("12.5")
    assert results[0].unit == "g/dL"
    assert results[0].reference_low == Decimal("13.0")
    assert results[0].reference_high == Decimal("17.0")
    assert results[0].status == ResultStatus.LOW

def test_colon_and_parentheses_format():
    text = "Hemoglobin: 12.5 g/dL (13.0-17.0)"
    results = parse_laboratory_results(text)
    assert len(results) == 1
    assert results[0].test_name == "Hemoglobin"
    assert results[0].unit == "g/dL"
    assert results[0].reference_low == Decimal("13.0")
    assert results[0].reference_high == Decimal("17.0")

def test_pipe_separated_format():
    text = "Glucose | 110 | mg/dL | 70 - 99"
    results = parse_laboratory_results(text)
    assert len(results) == 1
    assert results[0].test_name == "Glucose"
    assert results[0].value == Decimal("110")
    assert results[0].unit == "mg/dL"
    assert results[0].reference_low == Decimal("70")
    assert results[0].reference_high == Decimal("99")
    assert results[0].status == ResultStatus.HIGH

def test_integer_result():
    text = "Platelets 250 10^3/uL 150-450"
    results = parse_laboratory_results(text)
    assert len(results) == 1
    assert results[0].value == Decimal("250")
    assert results[0].status == ResultStatus.NORMAL

def test_decimal_result():
    text = "TSH 4.2 mIU/L"
    results = parse_laboratory_results(text)
    assert len(results) == 1
    assert results[0].value == Decimal("4.2")

def test_upper_only_reference_limit():
    text = "TSH 4.2 mIU/L < 4.0"
    results = parse_laboratory_results(text)
    assert len(results) == 1
    assert results[0].reference_low is None
    assert results[0].reference_high == Decimal("4.0")
    assert results[0].status == ResultStatus.HIGH

def test_lower_only_reference_limit():
    text = "Ferritin 8 ng/mL > 15"
    results = parse_laboratory_results(text)
    assert len(results) == 1
    assert results[0].reference_low == Decimal("15")
    assert results[0].reference_high is None
    assert results[0].status == ResultStatus.LOW

def test_unicode_dash_normalisation():
    text = "WBC 5.0 K/uL 4.0\u201311.0"
    results = parse_laboratory_results(text)
    assert len(results) == 1
    assert results[0].reference_low == Decimal("4.0")
    assert results[0].reference_high == Decimal("11.0")

def test_multiple_laboratory_rows():
    text = "TestA 10 u 5-15\nTestB 20 u 15-25"
    results = parse_laboratory_results(text)
    assert len(results) == 2
    assert results[0].test_name == "TestA"
    assert results[1].test_name == "TestB"

def test_blank_lines_and_headings_ignored():
    text = "\n\nCHEMISTRY PANEL\n\nGlucose 90 mg/dL 70-99\n\n"
    results = parse_laboratory_results(text)
    assert len(results) == 1
    assert results[0].test_name == "Glucose"

def test_malformed_row_ignored():
    text = "Just some random text without numbers"
    results = parse_laboratory_results(text)
    assert len(results) == 0

def test_date_line_ignored():
    text = "Date: 2023-10-15"
    results = parse_laboratory_results(text)
    assert len(results) == 0

def test_patient_id_line_ignored():
    text = "Patient ID: 12345678"
    results = parse_laboratory_results(text)
    assert len(results) == 0

def test_phone_number_line_ignored():
    text = "Phone: 555-1234"
    results = parse_laboratory_results(text)
    assert len(results) == 0

def test_duplicate_row_deduplication():
    text = "Test 10 u 5-15\nTest 10 u 5-15"
    results = parse_laboratory_results(text)
    assert len(results) == 1

def test_missing_unit():
    text = "Sodium 140 135-145"
    results = parse_laboratory_results(text)
    assert len(results) == 1
    assert results[0].test_name == "Sodium"
    assert results[0].value == Decimal("140")
    assert results[0].unit is None

def test_status_classification_integration():
    text = "Potassium 5.5 mEq/L 3.5-5.0"
    results = parse_laboratory_results(text)
    assert len(results) == 1
    assert results[0].status == ResultStatus.HIGH

def test_empty_input():
    results = parse_laboratory_results("")
    assert len(results) == 0

def test_ordinary_prose_without_results():
    text = "The patient is feeling well. Blood pressure is normal. Will re-evaluate next week."
    results = parse_laboratory_results(text)
    assert len(results) == 0

def test_no_fabricated_reference_range():
    text = "Bilirubin 1.2 mg/dL"
    results = parse_laboratory_results(text)
    assert len(results) == 1
    assert results[0].reference_low is None
    assert results[0].reference_high is None
    assert results[0].reference_text is None
