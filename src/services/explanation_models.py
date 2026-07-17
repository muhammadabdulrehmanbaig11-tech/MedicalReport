from typing import List, Optional
from pydantic import BaseModel
from src.analysis.models import ResultStatus

class ExplanationInputItem(BaseModel):
    test_name: str
    value_str: str
    unit: Optional[str] = None
    reference_str: Optional[str] = None
    status: ResultStatus

class ExplanationResult(BaseModel):
    summary_text: str
    safety_disclaimer: str
    ai_used: bool
    warnings: List[str] = []
