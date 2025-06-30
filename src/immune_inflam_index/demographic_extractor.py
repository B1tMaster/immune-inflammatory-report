"""
Patient demographic extraction from blood test PDFs.
"""

import re
from typing import Dict, Optional, Tuple, Any
from datetime import datetime


def extract_patient_age(text: str) -> Dict[str, Any]:
    """
    Extract patient age from PDF text using multiple pattern matching strategies.
    
    Args:
        text: Full text extracted from PDF
        
    Returns:
        Dictionary with age value, confidence, and raw text
    """
    age_patterns = [
        # Pattern for "58 Years Male" - highest confidence
        (r'(\d+)\s*[Yy]ears?\s*([Mm]ale|[Ff]emale)', 95),
        
        # Pattern for "Age: 58" - high confidence  
        (r'[Aa]ge[:\s]*(\d+)', 90),
        
        # Pattern for "58 yo" or "58 y.o." - good confidence
        (r'(\d+)\s*[Yy]\.?[Oo]\.?', 85),
        
        # Pattern for "58 M" or "58 F" - moderate confidence
        (r'(\d+)\s*([MF])\b', 80),
        
        # Pattern for standalone age near gender words - lower confidence
        (r'(\d+)(?=.*(?:[Mm]ale|[Ff]emale|[MF]))', 70)
    ]
    
    best_match = None
    best_confidence = 0
    
    for pattern, confidence in age_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                age = int(match.group(1))
                
                # Validate age is reasonable (18-120)
                if 18 <= age <= 120:
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = {
                            "value": age,
                            "confidence": confidence,
                            "raw_text": match.group(0),
                            "pattern_used": pattern
                        }
            except (ValueError, IndexError):
                continue
    
    return best_match or {
        "value": None,
        "confidence": 0,
        "raw_text": "",
        "pattern_used": ""
    }


def extract_patient_sex(text: str) -> Dict[str, Any]:
    """
    Extract patient sex from PDF text using multiple pattern matching strategies.
    
    Args:
        text: Full text extracted from PDF
        
    Returns:
        Dictionary with sex value, confidence, and raw text
    """
    sex_patterns = [
        # Pattern for "58 Years Male" - highest confidence
        (r'\d+\s*[Yy]ears?\s*([Mm]ale|[Ff]emale)', 95),
        
        # Pattern for standalone "Male" or "Female" - high confidence
        (r'\b([Mm]ale|[Ff]emale)\b', 90),
        
        # Pattern for "M" or "F" with context - moderate confidence  
        (r'\b([MF])\b(?=.*(?:[Yy]ears?|[Aa]ge|\d+))', 80),
        
        # Pattern for "Sex: M" or "Gender: F" - good confidence
        (r'(?:[Ss]ex|[Gg]ender)[:\s]*([MF])', 85)
    ]
    
    best_match = None
    best_confidence = 0
    
    for pattern, confidence in sex_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                sex_raw = match.group(1).upper()
                
                # Normalize to M/F
                if sex_raw.startswith('M'):
                    sex_value = 'M'
                elif sex_raw.startswith('F'):  
                    sex_value = 'F'
                else:
                    continue
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = {
                        "value": sex_value,
                        "confidence": confidence,
                        "raw_text": match.group(0),
                        "pattern_used": pattern
                    }
            except (IndexError):
                continue
    
    return best_match or {
        "value": None,
        "confidence": 0,
        "raw_text": "",
        "pattern_used": ""
    }


def extract_test_date(text: str) -> Dict[str, Any]:
    """
    Extract test/collection date from PDF text.
    
    Args:
        text: Full text extracted from PDF
        
    Returns:
        Dictionary with date value, confidence, and raw text
    """
    date_patterns = [
        # Pattern for "Collected: 03/03/25" - highest confidence
        (r'[Cc]ollected[:\s]*(\d{2}/\d{2}/\d{2,4})', 95),
        
        # Pattern for "Reported: 03/03/25" - high confidence
        (r'[Rr]eported[:\s]*(\d{2}/\d{2}/\d{2,4})', 90),
        
        # Pattern for "Date: 2025-03-03" - high confidence
        (r'[Dd]ate[:\s]*(\d{4}-\d{2}-\d{2})', 90),
        
        # Pattern for standalone dates - moderate confidence
        (r'(\d{2}/\d{2}/\d{2,4})', 70),
        
        # Pattern for ISO dates - moderate confidence
        (r'(\d{4}-\d{2}-\d{2})', 75)
    ]
    
    best_match = None
    best_confidence = 0
    
    for pattern, confidence in date_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                date_str = match.group(1)
                
                # Try to parse and validate the date
                parsed_date = None
                if '/' in date_str:
                    # Handle MM/DD/YY or MM/DD/YYYY formats
                    if len(date_str.split('/')[-1]) == 2:
                        # Add century for 2-digit years
                        parts = date_str.split('/')
                        year = int(parts[2])
                        if year < 50:  # Assume 20xx for years < 50
                            year += 2000
                        else:  # Assume 19xx for years >= 50
                            year += 1900
                        date_str = f"{parts[0]}/{parts[1]}/{year}"
                    
                    parsed_date = datetime.strptime(date_str, "%m/%d/%Y")
                elif '-' in date_str:
                    parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if parsed_date:
                    # Check if date is reasonable (not too far in past/future)
                    current_year = datetime.now().year
                    if (current_year - 10) <= parsed_date.year <= (current_year + 1):
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_match = {
                                "value": parsed_date.strftime("%Y-%m-%d"),
                                "confidence": confidence,
                                "raw_text": match.group(0),
                                "pattern_used": pattern
                            }
                            
            except (ValueError, IndexError):
                continue
    
    return best_match or {
        "value": None,
        "confidence": 0,
        "raw_text": "",
        "pattern_used": ""
    }


def extract_patient_demographics(text: str) -> Dict[str, Dict[str, Any]]:
    """
    Extract all patient demographic information from PDF text.
    
    Args:
        text: Full text extracted from PDF
        
    Returns:
        Dictionary containing age, sex, and test_date information
    """
    demographics = {
        "age": extract_patient_age(text),
        "sex": extract_patient_sex(text), 
        "test_date": extract_test_date(text)
    }
    
    return demographics


def validate_demographic_extraction(demographics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate extracted demographic information and generate warnings.
    
    Args:
        demographics: Extracted demographic data
        
    Returns:
        Validation results with warnings and recommendations
    """
    validation_result = {
        "valid": True,
        "warnings": [],
        "manual_verification_needed": False
    }
    
    # Check age
    age_data = demographics.get("age", {})
    if age_data.get("confidence", 0) < 70:
        validation_result["warnings"].append("Low confidence age extraction - manual verification recommended")
        validation_result["manual_verification_needed"] = True
    
    # Check sex
    sex_data = demographics.get("sex", {})  
    if sex_data.get("confidence", 0) < 70:
        validation_result["warnings"].append("Low confidence sex extraction - manual verification recommended")
        validation_result["manual_verification_needed"] = True
    
    # Check date
    date_data = demographics.get("test_date", {})
    if date_data.get("confidence", 0) < 70:
        validation_result["warnings"].append("Low confidence test date extraction - manual verification recommended")
    
    # Check for missing critical demographics
    if not age_data.get("value"):
        validation_result["warnings"].append("Patient age not found in PDF - age-specific interpretation unavailable")
    
    if not sex_data.get("value"):
        validation_result["warnings"].append("Patient sex not found in PDF - sex-specific interpretation unavailable")
    
    return validation_result


def debug_demographic_extraction(text: str, demographics: Dict[str, Dict[str, Any]]) -> str:
    """
    Generate debug information for demographic extraction troubleshooting.
    
    Args:
        text: Original PDF text
        demographics: Extracted demographic data
        
    Returns:
        Debug information string
    """
    debug_info = []
    debug_info.append("=== DEMOGRAPHIC EXTRACTION DEBUG INFO ===")
    debug_info.append(f"Text length: {len(text)} characters")
    debug_info.append("")
    
    debug_info.append("Extracted Demographics:")
    for field, data in demographics.items():
        if data.get("value"):
            debug_info.append(f"  {field}: {data['value']} ({data['confidence']}% confidence)")
            debug_info.append(f"    Raw text: {data['raw_text']}")
            debug_info.append(f"    Pattern: {data['pattern_used']}")
        else:
            debug_info.append(f"  {field}: NOT FOUND")
        debug_info.append("")
    
    # Show lines that might contain demographic info but weren't matched
    potential_lines = []
    keywords = ['age', 'male', 'female', 'years', 'collected', 'reported', 'date']
    
    for line in text.split('\n'):
        line = line.strip()
        if any(keyword in line.lower() for keyword in keywords):
            if any(digit in line for digit in '0123456789'):
                potential_lines.append(line)
    
    if potential_lines:
        debug_info.append("Potential demographic lines found:")
        for line in potential_lines[:10]:  # Show first 10
            debug_info.append(f"  {line}")
    
    return "\n".join(debug_info)