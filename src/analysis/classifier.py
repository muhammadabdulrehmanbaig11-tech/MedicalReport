from decimal import Decimal
from typing import Optional
from src.analysis.models import ResultStatus

def classify_result(
    value: Decimal,
    reference_low: Optional[Decimal],
    reference_high: Optional[Decimal],
) -> ResultStatus:
    if reference_low is None and reference_high is None:
        return ResultStatus.UNDETERMINED
        
    if reference_low is not None and reference_high is not None:
        if reference_low > reference_high:
            raise ValueError("Lower limit cannot be greater than upper limit")
        if value < reference_low:
            return ResultStatus.LOW
        if value > reference_high:
            return ResultStatus.HIGH
        return ResultStatus.NORMAL
        
    if reference_low is not None:
        if value < reference_low:
            return ResultStatus.LOW
        return ResultStatus.NORMAL
        
    if reference_high is not None:
        if value > reference_high:
            return ResultStatus.HIGH
        return ResultStatus.NORMAL
