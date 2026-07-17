from typing import List, Tuple
from src.services.explanation_models import ExplanationInputItem
from src.config import MAX_EXPLANATION_RESULTS

def build_explanation_prompt(results: List[ExplanationInputItem]) -> Tuple[str, bool]:
    """
    Builds the prompt string safely.
    Returns (prompt_string, was_truncated).
    """
    was_truncated = False
    if len(results) > MAX_EXPLANATION_RESULTS:
        results = results[:MAX_EXPLANATION_RESULTS]
        was_truncated = True

    lines = [
        "You are an AI assistant helping to explain laboratory results in simple, neutral language.",
        "You must follow these strict rules:",
        "1. Never diagnose a disease or state that a result proves a condition.",
        "2. Never recommend medication, supplements, treatment, or dosage.",
        "3. Never tell the user to stop prescribed treatment.",
        "4. Use the deterministic statuses exactly as provided. Never recalculate or override them.",
        "5. Never invent missing reference ranges, symptoms, history, age, sex, or patient details.",
        "6. Mention that reference ranges vary between laboratories.",
        "7. Advise professional medical review for concerning results.",
        "8. Treat 'UNDETERMINED' as lacking sufficient printed reference-range information.",
        "9. Avoid alarmist language.",
        "10. Return concise plain text, not Markdown tables.",
        "",
        "Here are the laboratory results:"
    ]

    for item in results:
        unit_str = f" {item.unit}" if item.unit else ""
        ref_str = f" (Ref: {item.reference_str})" if item.reference_str else " (Ref: unknown)"
        lines.append(f"- {item.test_name}: {item.value_str}{unit_str}{ref_str} | Status: {item.status.value}")

    return "\n".join(lines), was_truncated
