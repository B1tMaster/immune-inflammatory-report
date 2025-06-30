"""
Results interpretation and clinical guidance for immune inflammatory indices.
"""

from typing import Dict, List, Any, Optional


def interpret_results(
    indices_results: Dict[str, Dict], 
    patient_age: Optional[int] = None, 
    patient_sex: Optional[str] = None
) -> Dict[str, Any]:
    """
    Provide detailed clinical interpretation of calculated indices.
    
    Args:
        indices_results: Calculated index results
        patient_age: Patient age for context (optional)
        patient_sex: Patient sex (M/F) for context (optional)
    
    Returns:
        Detailed interpretation with clinical guidance
    """
    interpretation = {
        "clinical_assessment": {},
        "risk_stratification": {},
        "recommendations": {},
        "patient_context": {},
        "follow_up": {}
    }
    
    # Patient context
    if patient_age or patient_sex:
        interpretation["patient_context"] = {
            "age": patient_age,
            "sex": patient_sex,
            "age_considerations": _get_age_considerations(patient_age),
            "sex_considerations": _get_sex_considerations(patient_sex)
        }
    
    # Assess each index
    for index_name, data in indices_results.items():
        risk_level = data["risk_level"]
        value = data["value"]
        
        interpretation["clinical_assessment"][index_name] = {
            "value": value,
            "risk_level": risk_level,
            "clinical_significance": _get_clinical_significance(index_name, risk_level, value),
            "pathophysiology": _get_pathophysiology_explanation(index_name),
            "differential_diagnosis": _get_differential_diagnosis(index_name, risk_level)
        }
    
    # Overall risk stratification
    interpretation["risk_stratification"] = _assess_overall_risk(indices_results, patient_age, patient_sex)
    
    # Generate recommendations
    interpretation["recommendations"] = _generate_recommendations(indices_results, patient_age, patient_sex)
    
    # Follow-up guidance
    interpretation["follow_up"] = _generate_followup_guidance(indices_results)
    
    return interpretation


def _get_age_considerations(age: Optional[int]) -> List[str]:
    """Get age-specific considerations for interpretation."""
    if age is None:
        return []
    
    considerations = []
    
    if age < 18:
        considerations.append("Pediatric ranges may differ from adult reference values")
        considerations.append("Immune system still developing - values may be more variable")
    elif age >= 65:
        considerations.append("Elderly patients may have baseline elevation in inflammatory markers")
        considerations.append("Consider age-related immunosenescence effects")
        considerations.append("Higher risk for inflammatory complications")
    elif age >= 50:
        considerations.append("Middle-aged adults may show early signs of inflammaging")
        considerations.append("Consider screening for age-related inflammatory conditions")
    
    return considerations


def _get_sex_considerations(sex: Optional[str]) -> List[str]:
    """Get sex-specific considerations for interpretation."""
    if sex is None:
        return []
    
    considerations = []
    
    if sex.upper() == "F":
        considerations.append("Women have higher baseline risk for autoimmune conditions")
        considerations.append("Hormonal fluctuations may affect inflammatory markers")
        considerations.append("Consider pregnancy, menstrual cycle, and menopause effects")
    elif sex.upper() == "M":
        considerations.append("Men may have higher baseline inflammatory burden")
        considerations.append("Consider cardiovascular risk factors")
    
    return considerations


def _get_clinical_significance(index_name: str, risk_level: str, value: float) -> str:
    """Get clinical significance explanation for specific index and risk level."""
    
    significance_map = {
        "sii": {
            "normal": "Balanced systemic immune-inflammatory state with normal cellular interactions",
            "mild": "Early signs of systemic inflammation - may indicate subclinical inflammatory process",
            "moderate": "Significant systemic inflammation suggesting active inflammatory condition requiring evaluation",
            "high": "High-grade systemic inflammation indicating serious inflammatory burden - urgent evaluation needed",
            "very_high": "Critical systemic inflammation - immediate medical attention required"
        },
        "nlr": {
            "normal": "Normal neutrophil-lymphocyte balance indicating healthy immune response",
            "mild": "Mild neutrophilia or lymphopenia - may indicate early inflammatory response or stress",
            "moderate": "Moderate immune imbalance suggesting active inflammatory process or immune suppression",
            "high": "Significant immune dysregulation - high inflammatory burden or severe immune suppression",
            "very_high": "Critical immune imbalance - severe systemic inflammation or profound immune compromise"
        },
        "plr": {
            "normal": "Normal platelet-lymphocyte balance with appropriate hemostatic and immune function",
            "mild": "Mildly elevated thrombotic and inflammatory risk",
            "moderate": "Moderately increased risk for thrombotic complications and inflammation",
            "high": "High risk for thrombotic events and significant inflammatory burden"
        },
        "siri": {
            "normal": "Normal systemic inflammatory response with balanced monocyte activation",
            "mild": "Mild systemic inflammatory response - early tissue inflammation",
            "moderate": "Moderate inflammatory response indicating active tissue inflammation",
            "high": "High-grade inflammatory response with significant monocyte activation"
        },
        "mlr": {
            "normal": "Normal monocyte activation levels",
            "mild": "Mild monocyte activation - early tissue inflammatory response",
            "moderate": "Moderate monocyte activation indicating significant tissue inflammation",
            "high": "High monocyte activation suggesting extensive tissue inflammatory process"
        },
        "piv": {
            "normal": "Normal pan-immune inflammatory status across all major cell types",
            "mild": "Mildly elevated pan-immune inflammation involving multiple cell types",
            "moderate": "Moderate pan-immune inflammation with multi-cellular activation",
            "high": "High-grade pan-immune inflammation with extensive cellular involvement"
        }
    }
    
    return significance_map.get(index_name, {}).get(risk_level, "Unknown significance")


def _get_pathophysiology_explanation(index_name: str) -> str:
    """Get pathophysiology explanation for each index."""
    
    explanations = {
        "sii": ("Reflects the balance between neutrophil-platelet pro-inflammatory activity and "
                "lymphocyte-mediated adaptive immunity. Elevated values indicate predominance of "
                "innate inflammatory responses over adaptive immune regulation."),
        
        "nlr": ("Represents the balance between neutrophil-driven acute inflammation and "
                "lymphocyte-mediated immune regulation. Elevated ratios suggest either "
                "increased inflammatory drive or compromised lymphocyte function."),
        
        "plr": ("Indicates the relationship between platelet-mediated hemostatic/inflammatory "
                "responses and lymphocyte immune function. Elevation may reflect increased "
                "thrombotic risk and inflammatory burden."),
        
        "siri": ("Incorporates monocyte activation alongside neutrophil-lymphocyte balance, "
                 "providing insight into tissue-based inflammatory responses and macrophage "
                 "activation in addition to systemic inflammation."),
        
        "mlr": ("Reflects monocyte activation relative to lymphocyte function, indicating "
                "the degree of tissue inflammatory response and macrophage-mediated "
                "inflammatory processes."),
        
        "piv": ("Comprehensive index incorporating all major inflammatory cell types, "
                "providing overall assessment of pan-immune inflammatory activation "
                "across neutrophils, monocytes, platelets, and lymphocytes.")
    }
    
    return explanations.get(index_name, "Pathophysiology explanation not available")


def _get_differential_diagnosis(index_name: str, risk_level: str) -> List[str]:
    """Get differential diagnosis considerations based on elevated indices."""
    
    if risk_level in ["normal", "mild"]:
        return ["Consider physiological stress", "Subclinical infection", "Early inflammatory response"]
    
    differential_diagnoses = {
        "sii": [
            "Systemic inflammatory conditions (RA, SLE, IBD)",
            "Active infections (bacterial, viral, fungal)",
            "Malignancy with inflammatory response",
            "Cardiovascular disease with inflammation",
            "Metabolic syndrome with chronic inflammation"
        ],
        "nlr": [
            "Acute bacterial infections",
            "Neutrophilic inflammatory conditions",
            "Stress response (physical or psychological)",
            "Corticosteroid effects",
            "Hematologic malignancies"
        ],
        "plr": [
            "Thrombotic disorders",
            "Inflammatory conditions with platelet activation",
            "Malignancy with paraneoplastic effects",
            "Cardiovascular disease",
            "Autoimmune conditions"
        ],
        "siri": [
            "Tissue inflammatory conditions",
            "Chronic inflammatory diseases",
            "Infectious processes with monocyte activation",
            "Granulomatous diseases",
            "Metabolic inflammatory conditions"
        ],
        "mlr": [
            "Chronic inflammatory conditions",
            "Tissue inflammatory processes",
            "Infectious diseases with monocyte response",
            "Autoimmune conditions",
            "Inflammatory bowel disease"
        ],
        "piv": [
            "Multi-system inflammatory disorders",
            "Severe inflammatory conditions",
            "Systemic infections",
            "Advanced autoimmune diseases",
            "Inflammatory complications of chronic diseases"
        ]
    }
    
    return differential_diagnoses.get(index_name, ["Inflammatory condition of unknown etiology"])


def _assess_overall_risk(
    indices_results: Dict[str, Dict], 
    patient_age: Optional[int], 
    patient_sex: Optional[str]
) -> Dict[str, Any]:
    """Assess overall inflammatory risk based on all indices."""
    
    risk_levels = [data["risk_level"] for data in indices_results.values()]
    
    # Count risk levels
    risk_counts = {
        "normal": risk_levels.count("normal"),
        "mild": risk_levels.count("mild"),
        "moderate": risk_levels.count("moderate"),
        "high": risk_levels.count("high"),
        "very_high": risk_levels.count("very_high")
    }
    
    # Determine overall risk
    if risk_counts["very_high"] > 0:
        overall_risk = "critical"
        urgency = "immediate_attention"
    elif risk_counts["high"] > 0:
        overall_risk = "high"
        urgency = "urgent_evaluation"
    elif risk_counts["moderate"] >= 2:
        overall_risk = "moderate_to_high"
        urgency = "prompt_evaluation"
    elif risk_counts["moderate"] == 1 or risk_counts["mild"] >= 2:
        overall_risk = "moderate"
        urgency = "routine_evaluation"
    else:
        overall_risk = "low"
        urgency = "routine_monitoring"
    
    # Adjust for age and sex
    risk_modifiers = []
    if patient_age and patient_age >= 65:
        risk_modifiers.append("Increased risk due to advanced age")
    if patient_sex and patient_sex.upper() == "F":
        risk_modifiers.append("Consider higher autoimmune disease risk in females")
    
    return {
        "overall_risk_level": overall_risk,
        "urgency": urgency,
        "risk_distribution": risk_counts,
        "risk_modifiers": risk_modifiers,
        "composite_score": _calculate_composite_score(indices_results)
    }


def _calculate_composite_score(indices_results: Dict[str, Dict]) -> float:
    """Calculate a composite inflammatory score."""
    
    # Weight different indices based on clinical importance
    weights = {
        "sii": 0.25,
        "nlr": 0.20,
        "plr": 0.15,
        "siri": 0.20,
        "mlr": 0.10,
        "piv": 0.10
    }
    
    risk_scores = {
        "normal": 1,
        "mild": 2,
        "moderate": 3,
        "high": 4,
        "very_high": 5
    }
    
    weighted_score = 0
    total_weight = 0
    
    for index_name, data in indices_results.items():
        if index_name in weights:
            risk_level = data["risk_level"]
            score = risk_scores[risk_level]
            weight = weights[index_name]
            
            weighted_score += score * weight
            total_weight += weight
    
    return round(weighted_score / total_weight if total_weight > 0 else 1, 2)


def _generate_recommendations(
    indices_results: Dict[str, Dict], 
    patient_age: Optional[int], 
    patient_sex: Optional[str]
) -> Dict[str, List[str]]:
    """Generate clinical recommendations based on results."""
    
    recommendations = {
        "immediate": [],
        "short_term": [],
        "long_term": [],
        "lifestyle": [],
        "monitoring": []
    }
    
    risk_levels = [data["risk_level"] for data in indices_results.values()]
    
    # Immediate recommendations
    if "very_high" in risk_levels:
        recommendations["immediate"].extend([
            "Urgent medical evaluation required",
            "Consider emergency department evaluation if symptomatic",
            "Rule out serious inflammatory conditions",
            "Consider immediate anti-inflammatory intervention if indicated"
        ])
    elif "high" in risk_levels:
        recommendations["immediate"].extend([
            "Medical evaluation within 24-48 hours",
            "Assess for signs and symptoms of inflammatory conditions",
            "Consider infectious disease evaluation"
        ])
    
    # Short-term recommendations
    if any(level in risk_levels for level in ["high", "very_high", "moderate"]):
        recommendations["short_term"].extend([
            "Complete inflammatory workup (ESR, CRP, cytokines)",
            "Assess for autoimmune markers if indicated",
            "Consider imaging studies for inflammatory conditions",
            "Evaluate for infectious sources",
            "Review medication effects on inflammatory markers"
        ])
    
    # Long-term recommendations
    recommendations["long_term"].extend([
        "Regular monitoring of inflammatory indices",
        "Trend analysis over time",
        "Correlation with clinical symptoms and conditions"
    ])
    
    # Lifestyle recommendations
    if any(level in risk_levels for level in ["mild", "moderate", "high"]):
        recommendations["lifestyle"].extend([
            "Anti-inflammatory diet implementation",
            "Regular moderate exercise program",
            "Stress reduction techniques",
            "Adequate sleep hygiene (7-9 hours)",
            "Weight management if indicated",
            "Smoking cessation if applicable",
            "Limit alcohol consumption"
        ])
    
    # Monitoring recommendations
    monitoring_interval = "monthly" if "high" in risk_levels else "quarterly" if "moderate" in risk_levels else "annually"
    recommendations["monitoring"].extend([
        f"Repeat inflammatory indices {monitoring_interval}",
        "Track clinical symptoms and correlation",
        "Monitor response to interventions"
    ])
    
    return recommendations


def _generate_followup_guidance(indices_results: Dict[str, Dict]) -> Dict[str, Any]:
    """Generate follow-up guidance and monitoring recommendations."""
    
    risk_levels = [data["risk_level"] for data in indices_results.values()]
    
    # Determine follow-up timing
    if "very_high" in risk_levels:
        follow_up_timing = "1-2 weeks"
        monitoring_frequency = "weekly initially"
    elif "high" in risk_levels:
        follow_up_timing = "2-4 weeks"
        monitoring_frequency = "bi-weekly initially"
    elif "moderate" in risk_levels:
        follow_up_timing = "4-8 weeks"
        monitoring_frequency = "monthly"
    else:
        follow_up_timing = "3-6 months"
        monitoring_frequency = "quarterly"
    
    return {
        "follow_up_timing": follow_up_timing,
        "monitoring_frequency": monitoring_frequency,
        "key_parameters_to_track": [
            "Complete blood count with differential",
            "Inflammatory markers (ESR, CRP)",
            "Clinical symptoms and functional status",
            "Response to interventions"
        ],
        "concerning_changes": [
            "Worsening of any inflammatory index",
            "Development of new symptoms",
            "Failure to improve with interventions",
            "Emergence of complications"
        ],
        "specialist_referral_criteria": [
            "Persistently elevated indices despite treatment",
            "Development of organ-specific complications",
            "Suspicion of underlying autoimmune or inflammatory disease",
            "Need for specialized inflammatory disease evaluation"
        ]
    }