import pytest
from decimal import Decimal
from src.analysis.classifier import classify_result
from src.analysis.models import ResultStatus

def test_closed_range_below():
    assert classify_result(Decimal("9.9"), Decimal("10.0"), Decimal("20.0")) == ResultStatus.LOW

def test_closed_range_equal_lower():
    assert classify_result(Decimal("10.0"), Decimal("10.0"), Decimal("20.0")) == ResultStatus.NORMAL

def test_closed_range_within():
    assert classify_result(Decimal("15.5"), Decimal("10.0"), Decimal("20.0")) == ResultStatus.NORMAL

def test_closed_range_equal_upper():
    assert classify_result(Decimal("20.0"), Decimal("10.0"), Decimal("20.0")) == ResultStatus.NORMAL

def test_closed_range_above():
    assert classify_result(Decimal("20.1"), Decimal("10.0"), Decimal("20.0")) == ResultStatus.HIGH

def test_upper_only_below():
    assert classify_result(Decimal("4.0"), None, Decimal("5.0")) == ResultStatus.NORMAL

def test_upper_only_equal():
    assert classify_result(Decimal("5.0"), None, Decimal("5.0")) == ResultStatus.NORMAL

def test_upper_only_above():
    assert classify_result(Decimal("5.1"), None, Decimal("5.0")) == ResultStatus.HIGH

def test_lower_only_below():
    assert classify_result(Decimal("14.9"), Decimal("15.0"), None) == ResultStatus.LOW

def test_lower_only_equal():
    assert classify_result(Decimal("15.0"), Decimal("15.0"), None) == ResultStatus.NORMAL

def test_lower_only_above():
    assert classify_result(Decimal("15.1"), Decimal("15.0"), None) == ResultStatus.NORMAL

def test_no_limits():
    assert classify_result(Decimal("100"), None, None) == ResultStatus.UNDETERMINED

def test_reversed_range_invalid():
    with pytest.raises(ValueError):
        classify_result(Decimal("15"), Decimal("20"), Decimal("10"))

def test_decimal_precision():
    assert classify_result(Decimal("10.0001"), Decimal("10.0000"), Decimal("20")) == ResultStatus.NORMAL
    assert classify_result(Decimal("9.9999"), Decimal("10.0000"), Decimal("20")) == ResultStatus.LOW

def test_negative_values():
    assert classify_result(Decimal("-5"), Decimal("-10"), Decimal("0")) == ResultStatus.NORMAL
    assert classify_result(Decimal("-15"), Decimal("-10"), Decimal("0")) == ResultStatus.LOW
    assert classify_result(Decimal("1"), Decimal("-10"), Decimal("0")) == ResultStatus.HIGH
