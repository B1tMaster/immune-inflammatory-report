"""
Core calculation functions for immune inflammatory indices.
"""

from typing import Dict, Any, Optional
import math
from datetime import datetime

from .constants import REFERENCE_RANGES, INTERPRETATIONS


def calculate_sii(neutrophils: float, lymphocytes: float, platelets: float) -> float:
    """Calculate Systemic Immune-Inflammation Index (SII)."""
    if lymphocytes == 0:
        raise ValueError("Lymphocyte count cannot be zero for SII calculation")
    return (neutrophils * platelets) / lymphocytes


def calculate_nlr(neutrophils: float, lymphocytes: float) -> float:
    """Calculate Neutrophil-to-Lymphocyte Ratio (NLR)."""
    if lymphocytes == 0:
        raise ValueError("Lymphocyte count cannot be zero for NLR calculation")
    return neutrophils / lymphocytes


def calculate_plr(platelets: float, lymphocytes: float) -> float:
    """Calculate Platelet-to-Lymphocyte Ratio (PLR)."""
    if lymphocytes == 0:
        raise ValueError("Lymphocyte count cannot be zero for PLR calculation")
    return platelets / lymphocytes


def calculate_siri(neutrophils: float, lymphocytes: float, monocytes: float) -> float:
    """Calculate Systemic Inflammatory Response Index (SIRI)."""
    if lymphocytes == 0:
        raise ValueError("Lymphocyte count cannot be zero for SIRI calculation")
    return (neutrophils * monocytes) / lymphocytes


def calculate_mlr(monocytes: float, lymphocytes: float) -> float:
    """Calculate Monocyte-to-Lymphocyte Ratio (MLR)."""
    if lymphocytes == 0:
        raise ValueError("Lymphocyte count cannot be zero for MLR calculation")
    return monocytes / lymphocytes


def calculate_piv(neutrophils: float, lymphocytes: float, platelets: float, monocytes: float) -> float:
    """Calculate Pan-Immune Inflammation Value (PIV)."""
    if lymphocytes == 0:
        raise ValueError("Lymphocyte count cannot be zero for PIV calculation")
    return (neutrophils * monocytes * platelets) / lymphocytes


def get_risk_level(value: float, ranges: Dict[str, tuple]) -> str:
    """Determine risk level based on value and reference ranges."""
    for level, (min_val, max_val) in ranges.items():
        if min_val <= value < max_val:
            return level
    return "very_high"  # Default for values above all ranges


def calculate_indices(
    neutrophils: float, 
    lymphocytes: float, 
    platelets: float, 
    monocytes: Optional[float] = None
) -> Dict[str, Any]:
    """
    Calculate all applicable immune inflammatory indices.
    
    Args:
        neutrophils: Absolute neutrophil count (cells/µL)
        lymphocytes: Absolute lymphocyte count (cells/µL)
        platelets: Platelet count (cells/µL)
        monocytes: Absolute monocyte count (cells/µL, optional)
    
    Returns:
        Dictionary containing calculated indices with interpretations
    """
    from .validator import validate_inputs
    
    # Validate inputs
    validation_result = validate_inputs(neutrophils, lymphocytes, platelets, monocytes)
    if not validation_result["valid"]:
        raise ValueError(f"Input validation failed: {validation_result['errors']}")
    
    results = {
        "results": {},
        "summary": {},
        "metadata": {
            "calculation_date": datetime.now().isoformat(),
            "input_validation": validation_result,
            "warnings": []
        }
    }
    
    # Calculate basic indices (always available)
    try:
        # SII
        sii_value = calculate_sii(neutrophils, lymphocytes, platelets)
        sii_risk = get_risk_level(sii_value, REFERENCE_RANGES["sii"])
        results["results"]["sii"] = {
            "value": round(sii_value, 1),
            "interpretation": INTERPRETATIONS["sii"][sii_risk],
            "risk_level": sii_risk,
            "reference_ranges": REFERENCE_RANGES["sii"]
        }
        
        # NLR
        nlr_value = calculate_nlr(neutrophils, lymphocytes)
        nlr_risk = get_risk_level(nlr_value, REFERENCE_RANGES["nlr"])
        results["results"]["nlr"] = {
            "value": round(nlr_value, 2),
            "interpretation": INTERPRETATIONS["nlr"][nlr_risk],
            "risk_level": nlr_risk,
            "reference_ranges": REFERENCE_RANGES["nlr"]
        }
        
        # PLR
        plr_value = calculate_plr(platelets, lymphocytes)
        plr_risk = get_risk_level(plr_value, REFERENCE_RANGES["plr"])
        results["results"]["plr"] = {
            "value": round(plr_value, 1),
            "interpretation": INTERPRETATIONS["plr"][plr_risk],
            "risk_level": plr_risk,
            "reference_ranges": REFERENCE_RANGES["plr"]
        }
        
    except ValueError as e:
        results["metadata"]["warnings"].append(f"Calculation error: {str(e)}")
        return results
    
    # Calculate monocyte-dependent indices if monocytes provided
    if monocytes is not None:
        try:
            # SIRI
            siri_value = calculate_siri(neutrophils, lymphocytes, monocytes)
            siri_risk = get_risk_level(siri_value, REFERENCE_RANGES["siri"])
            results["results"]["siri"] = {
                "value": round(siri_value, 1),
                "interpretation": INTERPRETATIONS["siri"][siri_risk],
                "risk_level": siri_risk,
                "reference_ranges": REFERENCE_RANGES["siri"]
            }
            
            # MLR
            mlr_value = calculate_mlr(monocytes, lymphocytes)
            mlr_risk = get_risk_level(mlr_value, REFERENCE_RANGES["mlr"])
            results["results"]["mlr"] = {
                "value": round(mlr_value, 2),
                "interpretation": INTERPRETATIONS["mlr"][mlr_risk],
                "risk_level": mlr_risk,
                "reference_ranges": REFERENCE_RANGES["mlr"]
            }
            
            # PIV
            piv_value = calculate_piv(neutrophils, lymphocytes, platelets, monocytes)
            piv_risk = get_risk_level(piv_value, REFERENCE_RANGES["piv"])
            results["results"]["piv"] = {
                "value": round(piv_value, 1),
                "interpretation": INTERPRETATIONS["piv"][piv_risk],
                "risk_level": piv_risk,
                "reference_ranges": REFERENCE_RANGES["piv"]
            }
            
        except ValueError as e:
            results["metadata"]["warnings"].append(f"Monocyte-dependent calculation error: {str(e)}")
    
    # Generate summary
    results["summary"] = generate_summary(results["results"])
    
    return results


def generate_summary(indices_results: Dict[str, Dict]) -> Dict[str, Any]:
    """Generate summary of overall inflammatory status."""
    if not indices_results:
        return {
            "overall_inflammatory_status": "Cannot determine - calculation errors",
            "highest_risk_indices": [],
            "recommendations": ["Please check input values and recalculate"]
        }
    
    # Count risk levels
    risk_counts = {"normal": 0, "mild": 0, "moderate": 0, "high": 0, "very_high": 0}
    high_risk_indices = []
    
    for index_name, data in indices_results.items():
        risk_level = data["risk_level"]
        risk_counts[risk_level] += 1
        
        if risk_level in ["high", "very_high"]:
            high_risk_indices.append({
                "index": index_name.upper(),
                "value": data["value"],
                "risk_level": risk_level
            })
    
    # Determine overall status
    if risk_counts["very_high"] > 0:
        overall_status = "Critical inflammatory state - multiple indices severely elevated"
    elif risk_counts["high"] > 0:
        overall_status = "High inflammatory burden - medical evaluation recommended"
    elif risk_counts["moderate"] >= 2:
        overall_status = "Moderate inflammatory state - lifestyle interventions recommended"
    elif risk_counts["mild"] >= 2:
        overall_status = "Mild inflammatory activation - monitor and consider prevention"
    else:
        overall_status = "Normal inflammatory status"
    
    # Generate recommendations
    recommendations = []
    if risk_counts["very_high"] > 0 or risk_counts["high"] > 0:
        recommendations.extend([
            "Consult with healthcare provider immediately",
            "Consider comprehensive inflammatory workup",
            "Evaluate for underlying infections or autoimmune conditions"
        ])
    elif risk_counts["moderate"] > 0:
        recommendations.extend([
            "Consider lifestyle modifications (diet, exercise, stress reduction)",
            "Monitor inflammatory markers regularly",
            "Discuss with healthcare provider"
        ])
    elif risk_counts["mild"] > 0:
        recommendations.extend([
            "Focus on anti-inflammatory lifestyle practices",
            "Regular exercise and stress management",
            "Consider dietary improvements"
        ])
    else:
        recommendations.append("Maintain current healthy lifestyle practices")
    
    return {
        "overall_inflammatory_status": overall_status,
        "highest_risk_indices": high_risk_indices,
        "recommendations": recommendations
    }