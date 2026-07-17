import re
from decimal import Decimal, InvalidOperation
from typing import List, Optional, Tuple

from src.analysis.models import LaboratoryResult
from src.analysis.classifier import classify_result

def _clean_text(text: str) -> str:
    """Normalise dashes and spaces."""
    text = re.sub(r'[\u2010-\u2015\u2212]', '-', text)
    text = re.sub(r'[^\S\r\n]+', ' ', text)
    return text.strip()

def _parse_decimal(val_str: str) -> Optional[Decimal]:
    try:
        return Decimal(val_str)
    except InvalidOperation:
        return None

def _extract_reference_range(ref_str: str) -> Tuple[Optional[Decimal], Optional[Decimal]]:
    """
    Parse reference ranges like:
    13.0 - 17.0
    < 4.0
    > 15
    """
    ref_str = ref_str.strip()
    if not ref_str:
        return None, None
    
    # Range
    m_range = re.match(r'^([\-\d\.]+)\s*-\s*([\-\d\.]+)$', ref_str)
    if m_range:
        low = _parse_decimal(m_range.group(1))
        high = _parse_decimal(m_range.group(2))
        return low, high
        
    # Less than
    m_lt = re.match(r'^(?:<|<=|less than)\s*([\-\d\.]+)$', ref_str, re.IGNORECASE)
    if m_lt:
        high = _parse_decimal(m_lt.group(1))
        return None, high
        
    # Greater than
    m_gt = re.match(r'^(?:>|>=|greater than)\s*([\-\d\.]+)$', ref_str, re.IGNORECASE)
    if m_gt:
        low = _parse_decimal(m_gt.group(1))
        return low, None
        
    return None, None

def parse_laboratory_results(text: str) -> List[LaboratoryResult]:
    results = []
    seen = set()
    
    lines = text.splitlines()
    
    # We look for a pattern: [Test Name] [Value] [Optional Unit] [Optional Reference]
    # To reliably parse without ML, we use regex that captures:
    # 1. Letters/spaces (Test Name)
    # 2. A number (Value)
    # 3. Rest of the line (Unit + Ref Range)
    
    # Common formats:
    # Hemoglobin 12.5 g/dL 13.0 - 17.0
    # Hemoglobin: 12.5 g/dL (13.0-17.0)
    # Glucose | 110 | mg/dL | 70 - 99
    
    for original_line in lines:
        line = _clean_text(original_line)
        if not line:
            continue
            
        # Ignore lines that are obviously not test results
        if re.search(r'(?i)(date|patient|dob|phone|address|page\s+\d+)', line):
            continue
            
        # Replace pipes with spaces
        line_no_pipes = line.replace('|', ' ')
        line_no_pipes = re.sub(r'\s+', ' ', line_no_pipes).strip()
        
        # We need to find the first decimal number which acts as the value
        # Ensure we don't pick up numbers inside the test name easily unless it's isolated
        # Pattern: (Text) (Number) (Rest)
        m = re.match(r'^([a-zA-Z][a-zA-Z0-9\s\/\-\(\)\%\,]+?)\s*[:=]?\s+(-?\d+(?:\.\d+)?)\s*(.*)$', line_no_pipes)
        if not m:
            continue
            
        test_name = m.group(1).strip()
        test_name = test_name.rstrip(':').strip()
        val_str = m.group(2).strip()
        rest = m.group(3).strip()
        
        if len(test_name) < 2:
            continue
            
        value = _parse_decimal(val_str)
        if value is None:
            continue
            
        # Try to parse the rest into unit and reference
        # The reference range might be in parentheses, or at the end
        unit = None
        ref_text = None
        ref_low = None
        ref_high = None
        
        # If rest has parentheses at the end: e.g. "g/dL (13.0-17.0)"
        m_paren = re.search(r'\(([^)]+)\)$', rest)
        if m_paren:
            ref_text = m_paren.group(1).strip()
            unit_part = rest[:m_paren.start()].strip()
            if unit_part:
                unit = unit_part
        else:
            # Maybe it's like "g/dL 13.0 - 17.0" or "mIU/L < 4.0"
            # Let's split by space and look for range patterns from the right
            # Range patterns: X - Y, < X, > X
            m_range = re.search(r'(-?\d+(?:\.\d+)?\s*-\s*-?\d+(?:\.\d+)?)$', rest)
            m_ltgt = re.search(r'([<>]\s*-?\d+(?:\.\d+)?)$', rest)
            
            if m_range:
                ref_text = m_range.group(1)
                unit = rest[:m_range.start()].strip()
            elif m_ltgt:
                ref_text = m_ltgt.group(1)
                unit = rest[:m_ltgt.start()].strip()
            else:
                if rest:
                    unit = rest
                    
        if ref_text:
            ref_low, ref_high = _extract_reference_range(ref_text)
            # If we couldn't parse the reference range but we extracted ref_text, 
            # maybe it wasn't a real reference range. We just keep it as reference_text anyway.

        if not unit:
            unit = None
            
        if not ref_text:
            ref_text = None

        try:
            status = classify_result(value, ref_low, ref_high)
            
            result = LaboratoryResult(
                test_name=test_name,
                value=value,
                unit=unit,
                reference_low=ref_low,
                reference_high=ref_high,
                reference_text=ref_text,
                status=status,
                source_line=original_line
            )
            
            # Deduplicate exact matching attributes (ignoring source_line for dedup logic to be safe, but usually exact)
            dedup_key = (result.test_name, result.value, result.unit, result.reference_text)
            if dedup_key not in seen:
                seen.add(dedup_key)
                results.append(result)
        except ValueError:
            # e.g., reversed limits
            continue
            
    return results
