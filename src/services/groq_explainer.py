import os
from typing import List, Optional
import groq
from groq import Groq

from src.analysis.models import LaboratoryResult
from src.services.explanation_models import ExplanationInputItem, ExplanationResult
from src.services.explanation_prompt import build_explanation_prompt
from src.config import GROQ_MODEL_NAME, MAX_EXPLANATION_TOKENS, GROQ_API_KEY_ENV_VAR

def generate_plain_language_explanation(
    results: List[LaboratoryResult],
    api_key: Optional[str] = None
) -> ExplanationResult:
    
    if not results:
        return ExplanationResult(
            summary_text="No laboratory results available to explain.",
            safety_disclaimer="Not an AI diagnosis.",
            ai_used=False
        )

    key_to_use = api_key or os.environ.get(GROQ_API_KEY_ENV_VAR)
    if not key_to_use:
        return ExplanationResult(
            summary_text="AI explanation is unavailable because the Groq API key is missing.",
            safety_disclaimer="Not an AI diagnosis.",
            ai_used=False
        )
        
    input_items = []
    for r in results:
        ref_str = ""
        if r.reference_text:
            ref_str = r.reference_text
        elif r.reference_low is not None and r.reference_high is not None:
            ref_str = f"{r.reference_low} - {r.reference_high}"
        elif r.reference_low is not None:
            ref_str = f"> {r.reference_low}"
        elif r.reference_high is not None:
            ref_str = f"< {r.reference_high}"
            
        input_items.append(ExplanationInputItem(
            test_name=r.test_name,
            value_str=str(r.value),
            unit=r.unit,
            reference_str=ref_str if ref_str else None,
            status=r.status
        ))
        
    prompt, was_truncated = build_explanation_prompt(input_items)
    warnings = []
    if was_truncated:
        warnings.append("Too many results. Explanation was truncated to the first few tests.")
        
    try:
        client = Groq(api_key=key_to_use)
        response = client.chat.completions.create(
            model=GROQ_MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=MAX_EXPLANATION_TOKENS
        )
        
        if not response.choices or not response.choices[0].message.content:
            return ExplanationResult(
                summary_text="The AI returned an empty response.",
                safety_disclaimer="Not an AI diagnosis.",
                ai_used=False,
                warnings=warnings
            )
            
        content = response.choices[0].message.content.strip()
        if not content:
            return ExplanationResult(
                summary_text="The AI returned an empty response.",
                safety_disclaimer="Not an AI diagnosis.",
                ai_used=False,
                warnings=warnings
            )
            
        return ExplanationResult(
            summary_text=content,
            safety_disclaimer="This AI-generated explanation is for general educational purposes only. It is not a diagnosis, treatment plan or substitute for advice from a qualified healthcare professional.",
            ai_used=True,
            warnings=warnings
        )
        
    except groq.AuthenticationError:
        return ExplanationResult(
            summary_text="AI explanation is unavailable due to an authentication error.",
            safety_disclaimer="Not an AI diagnosis.",
            ai_used=False,
            warnings=warnings
        )
    except groq.RateLimitError:
        return ExplanationResult(
            summary_text="AI explanation is temporarily unavailable due to rate limits. Please try again later.",
            safety_disclaimer="Not an AI diagnosis.",
            ai_used=False,
            warnings=warnings
        )
    except groq.APIConnectionError:
        return ExplanationResult(
            summary_text="AI explanation is unavailable due to a network connection error.",
            safety_disclaimer="Not an AI diagnosis.",
            ai_used=False,
            warnings=warnings
        )
    except groq.APIError:
        return ExplanationResult(
            summary_text="AI explanation is unavailable due to a remote API error.",
            safety_disclaimer="Not an AI diagnosis.",
            ai_used=False,
            warnings=warnings
        )
    except Exception as e:
        if "groq" in str(type(e)).lower():
            return ExplanationResult(
                summary_text="AI explanation is unavailable due to an unexpected SDK error.",
                safety_disclaimer="Not an AI diagnosis.",
                ai_used=False,
                warnings=warnings
            )
        raise
