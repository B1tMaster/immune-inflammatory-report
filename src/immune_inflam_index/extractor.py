"""
CBC value extraction logic for parsing blood test reports.
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from fuzzywuzzy import fuzz, process

from .constants import FIELD_MAPPINGS, UNIT_CONVERSIONS


def parse_value_with_unit(text: str) -> Tuple[Optional[float], Optional[str]]:
    """
    Parse a numeric value with its unit from text.
    
    Args:
        text: Text containing value and unit
    
    Returns:
        Tuple of (value_in_cells_per_ul, original_unit)
    """
    # Clean the text
    text = text.strip().replace(",", "")
    
    # Pattern to match various numeric formats with units
    patterns = [
        # Pattern for "6.31 xIO^/L" and "1.66 xIOS/L" (special characters from PDF)
        r"(\d+\.?\d*)\s*x[IO0S]+\^?\s*/\s*L",
        
        # Pattern for "6.31 x10³/L" or "6.31 x10^3/L"
        r"(\d+\.?\d*)\s*x\s*10[³³^3]\s*/\s*L",
        r"(\d+\.?\d*)\s*x\s*10\^?\s*3\s*/\s*L",
        
        # Pattern for "181 x10®/L" (® symbol from PDF)
        r"(\d+\.?\d*)\s*x\s*10[®©]\s*/\s*L",
        
        # Pattern for "6310 cells/µL" or "6310 /µL"
        r"(\d+\.?\d*)\s*(?:cells\s*)?/\s*[µu]L",
        
        # Pattern for "6.31 K/µL"
        r"(\d+\.?\d*)\s*K\s*/\s*[µu]L",
        
        # Pattern for just numbers (assume x10³/L)
        r"^(\d+\.?\d*)$",
        
        # Pattern for numbers with reference range "6.31 (1.60-6.90)"
        r"(\d+\.?\d*)\s*\([^\)]+\)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                value = float(match.group(1))
                
                # Determine unit and convert to cells/µL
                if any(char in text.lower() for char in ["x10", "x 10", "xio", "xios", "x io", "®", "©"]):
                    # Already in x10³/L format, multiply by 1000 to get cells/µL
                    return value * 1000, "x10³/L"
                elif "k/" in text.lower():
                    # K/µL format, multiply by 1000
                    return value * 1000, "K/µL"
                elif "/µl" in text.lower() or "/ul" in text.lower():
                    # Already in cells/µL
                    return value, "cells/µL"
                else:
                    # Assume x10³/L format for plain numbers
                    return value * 1000, "x10³/L (assumed)"
                    
            except ValueError:
                continue
    
    return None, None


def find_field_value(text: str, field_name: str, field_variations: List[str]) -> Dict[str, Any]:
    """
    Find a specific field value in the text using fuzzy matching.
    
    Args:
        text: Text to search in
        field_name: Name of the field (for debugging)
        field_variations: List of possible field name variations
    
    Returns:
        Dictionary with value, confidence, unit, and raw_text
    """
    lines = text.split('\n')
    best_match = None
    best_confidence = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check each variation against the line
        for variation in field_variations:
            # Use fuzzy string matching to find the field name
            ratio = fuzz.partial_ratio(variation.lower(), line.lower())
            
            if ratio > 70:  # Reasonable match threshold
                # Try to extract value from this line
                value, unit = parse_value_with_unit(line)
                
                if value is not None:
                    confidence = min(ratio, 95)  # Cap confidence at 95%
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = {
                            "value": value,
                            "confidence": confidence,
                            "unit": unit,
                            "raw_text": line,
                            "matched_variation": variation
                        }
    
    return best_match or {
        "value": None,
        "confidence": 0,
        "unit": None,
        "raw_text": "",
        "matched_variation": ""
    }


def extract_reference_ranges(text: str) -> Dict[str, Tuple[float, float]]:
    """
    Extract reference ranges from the text.
    
    Args:
        text: Text containing reference ranges
    
    Returns:
        Dictionary mapping field names to (min, max) tuples
    """
    reference_ranges = {}
    
    # Pattern to match reference ranges like "(1.60-6.90)" or "(1.60 - 6.90)"
    range_pattern = r"\((\d+\.?\d*)\s*-\s*(\d+\.?\d*)\)"
    
    for field_name, variations in FIELD_MAPPINGS.items():
        for variation in variations:
            # Look for lines containing the field name and a reference range
            pattern = rf"{re.escape(variation)}.*?{range_pattern}"
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                try:
                    min_val = float(match.group(1))
                    max_val = float(match.group(2))
                    
                    # Convert reference range to cells/µL if needed
                    # Assume reference ranges are in the same unit as the value
                    if "x10" in match.group(0).lower():
                        min_val *= 1000
                        max_val *= 1000
                    
                    reference_ranges[field_name] = (min_val, max_val)
                    break  # Take first match for this field
                except ValueError:
                    continue
    
    return reference_ranges


def extract_cbc_values(text: str) -> Dict[str, Dict[str, Any]]:
    """
    Extract all CBC values from the provided text.
    
    Args:
        text: Text containing CBC values
    
    Returns:
        Dictionary mapping field names to extracted value information
    """
    extracted_values = {}
    
    # Extract values for each field
    for field_name, variations in FIELD_MAPPINGS.items():
        result = find_field_value(text, field_name, variations)
        
        if result["value"] is not None:
            extracted_values[field_name] = result
    
    # Extract reference ranges
    reference_ranges = extract_reference_ranges(text)
    
    # Add reference ranges to extracted values
    for field_name, ranges in reference_ranges.items():
        if field_name in extracted_values:
            extracted_values[field_name]["reference_range"] = ranges
    
    return extracted_values


def validate_extraction_quality(extracted_values: Dict[str, Dict]) -> Dict[str, Any]:
    """
    Assess the quality of the extraction process.
    
    Args:
        extracted_values: Dictionary of extracted values
    
    Returns:
        Quality assessment results
    """
    required_fields = ["neutrophils", "lymphocytes", "platelets"]
    found_required = sum(1 for field in required_fields if field in extracted_values)
    
    # Calculate overall confidence
    confidences = [data["confidence"] for data in extracted_values.values()]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    
    # Check for quality issues
    quality_issues = []
    
    if found_required < len(required_fields):
        missing = [field for field in required_fields if field not in extracted_values]
        quality_issues.append(f"Missing required fields: {', '.join(missing)}")
    
    low_confidence_fields = [
        field for field, data in extracted_values.items() 
        if data["confidence"] < 70
    ]
    
    if low_confidence_fields:
        quality_issues.append(f"Low confidence fields: {', '.join(low_confidence_fields)}")
    
    return {
        "overall_quality": "high" if avg_confidence > 80 and found_required == len(required_fields) else
                          "medium" if avg_confidence > 60 and found_required >= 2 else "low",
        "average_confidence": avg_confidence,
        "required_fields_found": found_required,
        "total_fields_found": len(extracted_values),
        "quality_issues": quality_issues,
        "manual_review_recommended": avg_confidence < 70 or found_required < len(required_fields)
    }


def debug_extraction(text: str, extracted_values: Dict[str, Dict]) -> str:
    """
    Generate debug information for extraction troubleshooting.
    
    Args:
        text: Original text
        extracted_values: Extracted values
    
    Returns:
        Debug information string
    """
    debug_info = []
    debug_info.append("=== EXTRACTION DEBUG INFO ===")
    debug_info.append(f"Text length: {len(text)} characters")
    debug_info.append(f"Number of lines: {len(text.split('\n'))}")
    debug_info.append("")
    
    debug_info.append("Fields found:")
    for field, data in extracted_values.items():
        debug_info.append(f"  {field}: {data['value']} ({data['confidence']}% confidence)")
        debug_info.append(f"    Raw text: {data['raw_text']}")
        debug_info.append(f"    Matched: {data['matched_variation']}")
        debug_info.append("")
    
    # Show lines that might contain CBC values but weren't matched
    potential_lines = []
    for line in text.split('\n'):
        line = line.strip()
        if any(digit in line for digit in '0123456789'):
            if any(keyword in line.lower() for keyword in ['neutro', 'lymph', 'platelet', 'mono']):
                if line not in [data['raw_text'] for data in extracted_values.values()]:
                    potential_lines.append(line)
    
    if potential_lines:
        debug_info.append("Potential missed lines:")
        for line in potential_lines[:5]:  # Show first 5
            debug_info.append(f"  {line}")
    
    return "\n".join(debug_info)