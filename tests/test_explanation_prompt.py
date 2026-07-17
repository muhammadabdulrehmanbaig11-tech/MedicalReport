from src.services.explanation_models import ExplanationInputItem
from src.analysis.models import ResultStatus
from src.services.explanation_prompt import build_explanation_prompt
from src.config import MAX_EXPLANATION_RESULTS

def test_prompt_includes_structured_fields():
    items = [
        ExplanationInputItem(
            test_name="Hemoglobin",
            value_str="12.5",
            unit="g/dL",
            reference_str="13.0 - 17.0",
            status=ResultStatus.LOW
        )
    ]
    prompt, truncated = build_explanation_prompt(items)
    assert not truncated
    assert "Hemoglobin" in prompt
    assert "12.5" in prompt
    assert "g/dL" in prompt
    assert "13.0 - 17.0" in prompt
    assert "LOW" in prompt
    assert "source_line" not in prompt
    assert "extracted text" not in prompt.lower()
    
def test_prompt_forbids_diagnosis_and_treatment():
    items = []
    prompt, _ = build_explanation_prompt(items)
    assert "Never diagnose a disease" in prompt
    assert "Never recommend medication" in prompt
    assert "Never tell the user to stop prescribed treatment" in prompt
    assert "Never recalculate or override" in prompt
    assert "UNDETERMINED" in prompt

def test_prompt_truncation():
    items = [
        ExplanationInputItem(
            test_name=f"Test {i}",
            value_str=str(i),
            status=ResultStatus.NORMAL
        ) for i in range(MAX_EXPLANATION_RESULTS + 5)
    ]
    prompt, truncated = build_explanation_prompt(items)
    assert truncated
    assert f"Test {MAX_EXPLANATION_RESULTS - 1}" in prompt
    assert f"Test {MAX_EXPLANATION_RESULTS}" not in prompt

def test_empty_results():
    prompt, truncated = build_explanation_prompt([])
    assert not truncated
    assert "Here are the laboratory results:" in prompt
