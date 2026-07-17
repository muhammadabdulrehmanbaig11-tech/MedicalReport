from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, model_validator, field_validator

class ResultStatus(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    UNDETERMINED = "UNDETERMINED"

class LaboratoryResult(BaseModel):
    test_name: str
    value: Decimal = Field(allow_inf_nan=False)
    unit: Optional[str] = None
    reference_low: Optional[Decimal] = Field(default=None, allow_inf_nan=False)
    reference_high: Optional[Decimal] = Field(default=None, allow_inf_nan=False)
    reference_text: Optional[str] = None
    status: ResultStatus
    source_line: str

    @field_validator("test_name", "source_line", "unit", "reference_text", mode="before")
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            stripped = v.strip()
            if not stripped:
                return None
            return stripped
        return v

    @model_validator(mode="after")
    def validate_fields(self):
        if not self.test_name:
            raise ValueError("test_name cannot be blank")
        if not self.source_line:
            raise ValueError("source_line cannot be blank")
        
        if self.reference_low is not None and self.reference_high is not None:
            if self.reference_low > self.reference_high:
                raise ValueError("reference_low cannot be greater than reference_high")
        
        return self
