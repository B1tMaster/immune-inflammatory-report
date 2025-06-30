"""
Input validation for immune inflammatory index calculations.
"""

from typing import Dict, List, Any, Optional, Union
from .constants import PHYSIOLOGICAL_RANGES


def validate_numeric_value(value: Union[float, int], name: str, min_val: float, max_val: float) -> Dict[str, Any]:
    """Validate a single numeric value against physiological ranges."""
    errors = []
    warnings = []
    
    # Check if value is numeric
    try:
        float_value = float(value)
    except (ValueError, TypeError):
        return {
            "valid": False,
            "value": value,
            "errors": [f"{name} must be a numeric value, got {type(value).__name__}"],
            "warnings": []
        }
    
    # Check for negative values
    if float_value < 0:
        errors.append(f"{name} cannot be negative (got {float_value})")
    
    # Check for zero values (problematic for division)
    if float_value == 0:
        if name.lower() == "lymphocytes":
            errors.append(f"{name} cannot be zero (needed for ratio calculations)")
        else:
            warnings.append(f"{name} is zero - this may indicate severe condition")
    
    # Check physiological ranges
    if float_value < min_val or float_value > max_val:
        if float_value < min_val * 0.1 or float_value > max_val * 10:
            errors.append(f"{name} ({float_value}) is extremely outside normal range ({min_val}-{max_val}) - possible data entry error")
        else:
            warnings.append(f"{name} ({float_value}) is outside normal range ({min_val}-{max_val})")
    
    return {
        "valid": len(errors) == 0,
        "value": float_value,
        "errors": errors,
        "warnings": warnings
    }


def validate_inputs(
    neutrophils: float, 
    lymphocytes: float, 
    platelets: float, 
    monocytes: Optional[float] = None
) -> Dict[str, Any]:
    """
    Validate all input parameters for immune inflammatory index calculations.
    
    Args:
        neutrophils: Absolute neutrophil count (cells/µL)
        lymphocytes: Absolute lymphocyte count (cells/µL)
        platelets: Platelet count (cells/µL)
        monocytes: Absolute monocyte count (cells/µL, optional)
    
    Returns:
        Dictionary containing validation results
    """
    validation_results = {}
    all_errors = []
    all_warnings = []
    
    # Validate required parameters
    required_params = [
        (neutrophils, "neutrophils", *PHYSIOLOGICAL_RANGES["neutrophils"]),
        (lymphocytes, "lymphocytes", *PHYSIOLOGICAL_RANGES["lymphocytes"]),
        (platelets, "platelets", *PHYSIOLOGICAL_RANGES["platelets"])
    ]
    
    for value, name, min_val, max_val in required_params:
        result = validate_numeric_value(value, name, min_val, max_val)
        validation_results[name] = result
        all_errors.extend(result["errors"])
        all_warnings.extend(result["warnings"])
    
    # Validate optional monocytes if provided
    if monocytes is not None:
        monocyte_result = validate_numeric_value(
            monocytes, "monocytes", *PHYSIOLOGICAL_RANGES["monocytes"]
        )
        validation_results["monocytes"] = monocyte_result
        all_errors.extend(monocyte_result["errors"])
        all_warnings.extend(monocyte_result["warnings"])
    
    # Additional cross-validation checks
    if validation_results["lymphocytes"]["valid"] and validation_results["neutrophils"]["valid"]:
        lymph_val = validation_results["lymphocytes"]["value"]
        neutro_val = validation_results["neutrophils"]["value"]
        
        # Check for extremely high NLR (potential data entry error)
        if lymph_val > 0:
            nlr = neutro_val / lymph_val
            if nlr > 50:
                all_warnings.append(f"Calculated NLR ({nlr:.1f}) is extremely high - please verify input values")
    
    # Check platelet-to-lymphocyte ratio for extreme values
    if validation_results["platelets"]["valid"] and validation_results["lymphocytes"]["valid"]:
        plat_val = validation_results["platelets"]["value"]
        lymph_val = validation_results["lymphocytes"]["value"]
        
        if lymph_val > 0:
            plr = plat_val / lymph_val
            if plr > 1000:
                all_warnings.append(f"Calculated PLR ({plr:.1f}) is extremely high - please verify input values")
    
    return {
        "valid": len(all_errors) == 0,
        "individual_results": validation_results,
        "errors": all_errors,
        "warnings": all_warnings,
        "summary": {
            "total_errors": len(all_errors),
            "total_warnings": len(all_warnings),
            "parameters_validated": len(validation_results)
        }
    }


def validate_pdf_extracted_values(extracted_values: Dict[str, Dict]) -> Dict[str, Any]:
    """
    Validate values extracted from PDF parsing.
    
    Args:
        extracted_values: Dictionary of extracted values with metadata
    
    Returns:
        Validation results with confidence assessment
    """
    validation_results = {}
    all_errors = []
    all_warnings = []
    confidence_issues = []
    
    required_fields = ["neutrophils", "lymphocytes", "platelets"]
    
    for field in required_fields:
        if field not in extracted_values:
            all_errors.append(f"Required field '{field}' not found in PDF")
            continue
        
        field_data = extracted_values[field]
        value = field_data.get("value")
        confidence = field_data.get("confidence", 0)
        
        # Validate the extracted value
        min_val, max_val = PHYSIOLOGICAL_RANGES[field]
        result = validate_numeric_value(value, field, min_val, max_val)
        validation_results[field] = result
        
        # Check confidence scores
        if confidence < 70:
            confidence_issues.append(f"{field}: {confidence}% confidence (extracted: {value})")
        
        if confidence < 50:
            all_warnings.append(f"Low confidence ({confidence}%) for {field} extraction - manual verification recommended")
        
        all_errors.extend(result["errors"])
        all_warnings.extend(result["warnings"])
    
    # Check for monocytes if available
    if "monocytes" in extracted_values:
        monocyte_data = extracted_values["monocytes"]
        monocyte_value = monocyte_data.get("value")
        monocyte_confidence = monocyte_data.get("confidence", 0)
        
        min_val, max_val = PHYSIOLOGICAL_RANGES["monocytes"]
        monocyte_result = validate_numeric_value(monocyte_value, "monocytes", min_val, max_val)
        validation_results["monocytes"] = monocyte_result
        
        if monocyte_confidence < 70:
            confidence_issues.append(f"monocytes: {monocyte_confidence}% confidence (extracted: {monocyte_value})")
        
        all_errors.extend(monocyte_result["errors"])
        all_warnings.extend(monocyte_result["warnings"])
    
    return {
        "valid": len(all_errors) == 0,
        "individual_results": validation_results,
        "errors": all_errors,
        "warnings": all_warnings,
        "confidence_issues": confidence_issues,
        "manual_verification_needed": len(confidence_issues) > 0 or len(all_errors) > 0,
        "summary": {
            "total_errors": len(all_errors),
            "total_warnings": len(all_warnings),
            "low_confidence_fields": len(confidence_issues),
            "parameters_validated": len(validation_results)
        }
    }


def check_reference_ranges(extracted_values: Dict[str, Dict], pdf_reference_ranges: Dict[str, tuple]) -> List[str]:
    """
    Cross-check extracted values against PDF reference ranges.
    
    Args:
        extracted_values: Values extracted from PDF
        pdf_reference_ranges: Reference ranges found in PDF
    
    Returns:
        List of warnings for values outside PDF reference ranges
    """
    warnings = []
    
    for field, field_data in extracted_values.items():
        value = field_data.get("value")
        if value is None:
            continue
        
        pdf_range = pdf_reference_ranges.get(field)
        if pdf_range is None:
            continue
        
        min_ref, max_ref = pdf_range
        if value < min_ref or value > max_ref:
            warnings.append(
                f"{field} ({value}) is outside PDF reference range ({min_ref}-{max_ref})"
            )
    
    return warnings