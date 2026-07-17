import pytest
from unittest import mock
import groq
from decimal import Decimal

from src.analysis.models import LaboratoryResult, ResultStatus
from src.services.groq_explainer import generate_plain_language_explanation
from src.services.explanation_models import ExplanationResult

def get_sample_results():
    return [
        LaboratoryResult(
            test_name="Hemoglobin",
            value=Decimal("12.5"),
            unit="g/dL",
            reference_low=Decimal("13.0"),
            reference_high=Decimal("17.0"),
            reference_text="13.0 - 17.0",
            status=ResultStatus.LOW,
            source_line="Hemoglobin 12.5 g/dL 13.0 - 17.0"
        )
    ]

def test_no_results():
    result = generate_plain_language_explanation([], api_key="dummy")
    assert result.ai_used is False
    assert "No laboratory results available" in result.summary_text

def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    result = generate_plain_language_explanation(get_sample_results())
    assert result.ai_used is False
    assert "missing" in result.summary_text.lower()

@mock.patch("src.services.groq_explainer.Groq")
def test_successful_response(mock_groq_class):
    mock_client = mock.MagicMock()
    mock_groq_class.return_value = mock_client
    
    mock_response = mock.MagicMock()
    mock_response.choices = [mock.MagicMock()]
    mock_response.choices[0].message.content = "This means your hemoglobin is slightly low."
    mock_client.chat.completions.create.return_value = mock_response

    result = generate_plain_language_explanation(get_sample_results(), api_key="dummy_key")
    
    assert result.ai_used is True
    assert "slightly low" in result.summary_text
    assert "not a diagnosis" in result.safety_disclaimer.lower()
    
    # Verify mock was called correctly
    mock_client.chat.completions.create.assert_called_once()
    call_args = mock_client.chat.completions.create.call_args[1]
    prompt_sent = call_args["messages"][0]["content"]
    assert "Hemoglobin 12.5 g/dL 13.0 - 17.0" not in prompt_sent  # Raw source line shouldn't be here
    assert "Hemoglobin:" in prompt_sent  # Structured field should be

@mock.patch("src.services.groq_explainer.Groq")
def test_empty_response(mock_groq_class):
    mock_client = mock.MagicMock()
    mock_groq_class.return_value = mock_client
    
    mock_response = mock.MagicMock()
    mock_response.choices = [mock.MagicMock()]
    mock_response.choices[0].message.content = ""
    mock_client.chat.completions.create.return_value = mock_response

    result = generate_plain_language_explanation(get_sample_results(), api_key="dummy_key")
    
    assert result.ai_used is False
    assert "empty" in result.summary_text.lower()

@mock.patch("src.services.groq_explainer.Groq")
def test_auth_failure(mock_groq_class):
    mock_client = mock.MagicMock()
    mock_groq_class.return_value = mock_client
    
    # Create the error correctly using httpx and a response object
    import httpx
    request = httpx.Request("GET", "https://api.groq.com")
    response = httpx.Response(401, request=request)
    mock_client.chat.completions.create.side_effect = groq.AuthenticationError(
        message="Invalid API Key", 
        response=response,
        body=None
    )

    result = generate_plain_language_explanation(get_sample_results(), api_key="dummy_key")
    assert result.ai_used is False
    assert "authentication" in result.summary_text.lower()
    assert "dummy_key" not in result.summary_text

@mock.patch("src.services.groq_explainer.Groq")
def test_rate_limit(mock_groq_class):
    mock_client = mock.MagicMock()
    mock_groq_class.return_value = mock_client
    
    import httpx
    request = httpx.Request("GET", "https://api.groq.com")
    response = httpx.Response(429, request=request)
    mock_client.chat.completions.create.side_effect = groq.RateLimitError(
        message="Rate limited", 
        response=response,
        body=None
    )

    result = generate_plain_language_explanation(get_sample_results(), api_key="dummy_key")
    assert result.ai_used is False
    assert "rate limit" in result.summary_text.lower()

@mock.patch("src.services.groq_explainer.Groq")
def test_network_failure(mock_groq_class):
    mock_client = mock.MagicMock()
    mock_groq_class.return_value = mock_client
    
    import httpx
    request = httpx.Request("GET", "https://api.groq.com")
    mock_client.chat.completions.create.side_effect = groq.APIConnectionError(
        message="Network error", 
        request=request
    )

    result = generate_plain_language_explanation(get_sample_results(), api_key="dummy_key")
    assert result.ai_used is False
    assert "network" in result.summary_text.lower()

@mock.patch("src.services.groq_explainer.Groq")
def test_truncation_warning(mock_groq_class):
    mock_client = mock.MagicMock()
    mock_groq_class.return_value = mock_client
    
    mock_response = mock.MagicMock()
    mock_response.choices = [mock.MagicMock()]
    mock_response.choices[0].message.content = "Explanation"
    mock_client.chat.completions.create.return_value = mock_response

    results = []
    from src.config import MAX_EXPLANATION_RESULTS
    for i in range(MAX_EXPLANATION_RESULTS + 5):
        results.append(LaboratoryResult(
            test_name=f"Test {i}",
            value=Decimal("10"),
            status=ResultStatus.NORMAL,
            source_line=f"Test {i} 10"
        ))

    result = generate_plain_language_explanation(results, api_key="dummy_key")
    
    assert result.ai_used is True
    assert len(result.warnings) == 1
    assert "truncated" in result.warnings[0].lower()
