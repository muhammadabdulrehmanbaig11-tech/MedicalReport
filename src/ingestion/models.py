"""
Pydantic models for structured validation of ingestion results.
"""

from typing import List
from pydantic import BaseModel, Field

class ExtractionResult(BaseModel):
    """Model representing the result of a successful PDF text extraction."""
    original_filename: str = Field(..., min_length=1)
    page_count: int = Field(..., ge=1)
    extracted_text: str = Field(..., min_length=1)
    extracted_character_count: int = Field(..., ge=0)
    appears_text_based: bool
    warnings: List[str] = Field(default_factory=list)
