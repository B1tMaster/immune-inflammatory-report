"""Unit tests for the interpreter module."""

import pytest
from hypothesis import given, strategies as st

from immune_inflam_index.interpreter import (
    interpret_results, _get_age_considerations, _get_sex_considerations,
    _get_clinical_significance, _get_pathophysiology_explanation,
    _get_differential_diagnosis, _assess_overall_risk, _calculate_composite_score,
    _generate_recommendations, _generate_followup_guidance
)


class TestInterpretResults:
    """Test main interpretation function."""
    
    def test_interpret_results_complete(self):
        """Test interpretation with complete data."""
        indices_results = {
            "sii": {"value": 800, "risk_level": "moderate"},
            "nlr": {"value": 4.0, "risk_level": "moderate"},
            "plr": {"value": 180, "risk_level": "mild"}
        }
        
        result = interpret_results(indices_results, patient_age=45, patient_sex="F")
        
        # Check structure
        expected_keys = ["clinical_assessment", "risk_stratification", "recommendations", 
                        "patient_context", "follow_up"]
        for key in expected_keys:
            assert key in result
        
        # Check patient context
        assert result["patient_context"]["age"] == 45
        assert result["patient_context"]["sex"] == "F"
        assert len(result["patient_context"]["age_considerations"]) > 0
        assert len(result["patient_context"]["sex_considerations"]) > 0
        
        # Check clinical assessment
        for index in indices_results:
            assert index in result["clinical_assessment"]
            assessment = result["clinical_assessment"][index]
            assert "value" in assessment
            assert "risk_level" in assessment
            assert "clinical_significance" in assessment
            assert "pathophysiology" in assessment
            assert "differential_diagnosis" in assessment
    
    def test_interpret_results_no_patient_data(self):
        """Test interpretation without patient demographics."""
        indices_results = {
            "sii": {"value": 400, "risk_level": "normal"},
            "nlr": {"value": 2.5, "risk_level": "normal"}
        }
        
        result = interpret_results(indices_results)
        
        # Should still provide interpretation without patient context
        assert "clinical_assessment" in result
        assert "risk_stratification" in result
        assert len(result["patient_context"]) == 0 or result["patient_context"] == {}
    
    def test_interpret_results_high_risk(self):
        """Test interpretation with high-risk values."""
        indices_results = {
            "sii": {"value": 2500, "risk_level": "high"},
            "nlr": {"value": 10.0, "risk_level": "high"},
            "plr": {"value": 400, "risk_level": "high"}
        }
        
        result = interpret_results(indices_results, patient_age=65, patient_sex="M")
        
        # Should indicate high risk
        assert result["risk_stratification"]["overall_risk_level"] in ["high", "critical"]
        assert result["risk_stratification"]["urgency"] in ["urgent_evaluation", "immediate_attention"]
        
        # Should have immediate recommendations
        assert len(result["recommendations"]["immediate"]) > 0


class TestAgeConsiderations:
    """Test age-specific considerations."""
    
    def test_age_considerations_young_adult(self):
        """Test considerations for young adults."""
        considerations = _get_age_considerations(25)
        
        assert len(considerations) > 0
        assert any("acute pathology" in c for c in considerations)
        assert any("lifestyle factors" in c for c in considerations)
        assert any("autoimmune conditions" in c for c in considerations)
    
    def test_age_considerations_middle_aged(self):
        """Test considerations for middle-aged adults."""
        considerations = _get_age_considerations(50)
        
        assert len(considerations) > 0
        assert any("inflammaging" in c for c in considerations)
        assert any("cardiovascular" in c for c in considerations)
        assert any("cancer screening" in c for c in considerations)
    
    def test_age_considerations_elderly(self):
        """Test considerations for elderly adults."""
        considerations = _get_age_considerations(75)
        
        assert len(considerations) > 0
        assert any("baseline elevation" in c for c in considerations)
        assert any("immunosenescence" in c for c in considerations)
        assert any("functional status" in c for c in considerations)
    
    def test_age_considerations_pediatric(self):
        """Test considerations for pediatric patients."""
        considerations = _get_age_considerations(15)
        
        assert len(considerations) > 0
        assert any("Pediatric" in c for c in considerations)
        assert any("developing" in c for c in considerations)
    
    def test_age_considerations_none(self):
        """Test handling of None age."""
        considerations = _get_age_considerations(None)
        assert considerations == []
    
    def test_age_considerations_boundary_values(self):
        """Test age boundary values."""
        # Test exact boundaries
        young_adult = _get_age_considerations(18)
        middle_aged = _get_age_considerations(35)
        elderly = _get_age_considerations(65)
        
        assert len(young_adult) > 0
        assert len(middle_aged) > 0
        assert len(elderly) > 0
        
        # Verify different considerations for different age groups
        assert young_adult != middle_aged
        assert middle_aged != elderly


class TestSexConsiderations:
    """Test sex-specific considerations."""
    
    def test_sex_considerations_female(self):
        """Test considerations for female patients."""
        considerations = _get_sex_considerations("F")
        
        assert len(considerations) > 0
        assert any("autoimmune" in c for c in considerations)
        assert any("hormonal" in c for c in considerations)
        assert any("pregnancy" in c or "menstrual" in c or "menopause" in c for c in considerations)
    
    def test_sex_considerations_male(self):
        """Test considerations for male patients."""
        considerations = _get_sex_considerations("M")
        
        assert len(considerations) > 0
        assert any("cardiovascular" in c for c in considerations)
        assert any("baseline inflammatory" in c for c in considerations)
    
    def test_sex_considerations_case_insensitive(self):
        """Test sex considerations are case insensitive."""
        considerations_lower = _get_sex_considerations("f")
        considerations_upper = _get_sex_considerations("F")
        
        assert considerations_lower == considerations_upper
    
    def test_sex_considerations_none(self):
        """Test handling of None sex."""
        considerations = _get_sex_considerations(None)
        assert considerations == []
    
    def test_sex_considerations_invalid(self):
        """Test handling of invalid sex values."""
        considerations = _get_sex_considerations("X")
        assert considerations == []


class TestClinicalSignificance:
    """Test clinical significance explanations."""
    
    def test_clinical_significance_all_indices(self):
        """Test clinical significance for all indices and risk levels."""
        indices = ["sii", "nlr", "plr", "siri", "mlr", "piv"]
        risk_levels = ["normal", "mild", "moderate", "high", "very_high"]
        
        for index in indices:
            for risk_level in risk_levels:
                significance = _get_clinical_significance(index, risk_level, 100)
                assert isinstance(significance, str)
                assert len(significance) > 0
                assert significance != "Unknown significance"
    
    def test_clinical_significance_unknown_index(self):
        """Test handling of unknown index."""
        significance = _get_clinical_significance("unknown_index", "high", 100)
        assert significance == "Unknown significance"
    
    def test_clinical_significance_unknown_risk_level(self):
        """Test handling of unknown risk level."""
        significance = _get_clinical_significance("sii", "unknown_level", 100)
        assert significance == "Unknown significance"
    
    def test_clinical_significance_content_quality(self):
        """Test quality of clinical significance content."""
        # High-risk SII should mention urgent evaluation
        sii_high = _get_clinical_significance("sii", "high", 2000)
        assert "urgent" in sii_high.lower() or "serious" in sii_high.lower()
        
        # Normal NLR should mention balance
        nlr_normal = _get_clinical_significance("nlr", "normal", 2.0)
        assert "normal" in nlr_normal.lower() and "balance" in nlr_normal.lower()


class TestPathophysiologyExplanations:
    """Test pathophysiology explanations."""
    
    def test_pathophysiology_all_indices(self):
        """Test pathophysiology explanations for all indices."""
        indices = ["sii", "nlr", "plr", "siri", "mlr", "piv"]
        
        for index in indices:
            explanation = _get_pathophysiology_explanation(index)
            assert isinstance(explanation, str)
            assert len(explanation) > 50  # Should be detailed
            assert explanation != "Pathophysiology explanation not available"
    
    def test_pathophysiology_unknown_index(self):
        """Test handling of unknown index."""
        explanation = _get_pathophysiology_explanation("unknown")
        assert explanation == "Pathophysiology explanation not available"
    
    def test_pathophysiology_content_quality(self):
        """Test quality of pathophysiology content."""
        sii_explanation = _get_pathophysiology_explanation("sii")
        assert "neutrophil" in sii_explanation.lower()
        assert "platelet" in sii_explanation.lower()
        assert "lymphocyte" in sii_explanation.lower()
        
        nlr_explanation = _get_pathophysiology_explanation("nlr")
        assert "neutrophil" in nlr_explanation.lower()
        assert "lymphocyte" in nlr_explanation.lower()


class TestDifferentialDiagnosis:
    """Test differential diagnosis suggestions."""
    
    def test_differential_diagnosis_elevated_indices(self):
        """Test differential diagnosis for elevated indices."""
        indices = ["sii", "nlr", "plr", "siri", "mlr", "piv"]
        
        for index in indices:
            diagnoses = _get_differential_diagnosis(index, "high")
            assert isinstance(diagnoses, list)
            assert len(diagnoses) > 0
            assert all(isinstance(dx, str) for dx in diagnoses)
    
    def test_differential_diagnosis_normal_mild(self):
        """Test differential diagnosis for normal/mild elevations."""
        diagnoses_normal = _get_differential_diagnosis("sii", "normal")
        diagnoses_mild = _get_differential_diagnosis("sii", "mild")
        
        # Should be the same for normal and mild
        assert diagnoses_normal == diagnoses_mild
        assert "stress" in str(diagnoses_normal).lower() or "subclinical" in str(diagnoses_normal).lower()
    
    def test_differential_diagnosis_unknown_index(self):
        """Test handling of unknown index."""
        diagnoses = _get_differential_diagnosis("unknown", "high")
        assert len(diagnoses) > 0
        assert "unknown etiology" in diagnoses[0].lower()
    
    def test_differential_diagnosis_content_quality(self):
        """Test quality of differential diagnosis content."""
        nlr_diagnoses = _get_differential_diagnosis("nlr", "high")
        assert any("infection" in dx.lower() for dx in nlr_diagnoses)
        
        plr_diagnoses = _get_differential_diagnosis("plr", "high")
        assert any("thrombotic" in dx.lower() for dx in plr_diagnoses)


class TestOverallRiskAssessment:
    """Test overall risk assessment logic."""
    
    def test_assess_overall_risk_normal(self):
        """Test risk assessment with normal values."""
        indices_results = {
            "sii": {"risk_level": "normal"},
            "nlr": {"risk_level": "normal"},
            "plr": {"risk_level": "normal"}
        }
        
        risk_assessment = _assess_overall_risk(indices_results, None, None)
        
        assert risk_assessment["overall_risk_level"] == "low"
        assert risk_assessment["urgency"] == "routine_monitoring"
        assert risk_assessment["risk_distribution"]["normal"] == 3
    
    def test_assess_overall_risk_high(self):
        """Test risk assessment with high values."""
        indices_results = {
            "sii": {"risk_level": "high"},
            "nlr": {"risk_level": "moderate"},
            "plr": {"risk_level": "normal"}
        }
        
        risk_assessment = _assess_overall_risk(indices_results, None, None)
        
        assert risk_assessment["overall_risk_level"] == "high"
        assert risk_assessment["urgency"] == "urgent_evaluation"
    
    def test_assess_overall_risk_critical(self):
        """Test risk assessment with very high values."""
        indices_results = {
            "sii": {"risk_level": "very_high"},
            "nlr": {"risk_level": "high"}
        }
        
        risk_assessment = _assess_overall_risk(indices_results, None, None)
        
        assert risk_assessment["overall_risk_level"] == "critical"
        assert risk_assessment["urgency"] == "immediate_attention"
    
    def test_assess_overall_risk_age_modifiers(self):
        """Test risk assessment with age modifiers."""
        indices_results = {
            "sii": {"risk_level": "moderate"}
        }
        
        risk_assessment = _assess_overall_risk(indices_results, 75, "F")
        
        assert len(risk_assessment["risk_modifiers"]) > 0
        assert any("advanced age" in modifier for modifier in risk_assessment["risk_modifiers"])
        assert any("autoimmune" in modifier for modifier in risk_assessment["risk_modifiers"])
    
    def test_assess_overall_risk_composite_score(self):
        """Test composite score calculation."""
        indices_results = {
            "sii": {"risk_level": "high"},
            "nlr": {"risk_level": "moderate"},
            "plr": {"risk_level": "mild"}
        }
        
        risk_assessment = _assess_overall_risk(indices_results, None, None)
        
        assert "composite_score" in risk_assessment
        assert isinstance(risk_assessment["composite_score"], float)
        assert 1.0 <= risk_assessment["composite_score"] <= 5.0


class TestCompositeScore:
    """Test composite score calculation."""
    
    def test_calculate_composite_score_all_normal(self):
        """Test composite score with all normal values."""
        indices_results = {
            "sii": {"risk_level": "normal"},
            "nlr": {"risk_level": "normal"},
            "plr": {"risk_level": "normal"},
            "siri": {"risk_level": "normal"},
            "mlr": {"risk_level": "normal"},
            "piv": {"risk_level": "normal"}
        }
        
        score = _calculate_composite_score(indices_results)
        assert score == 1.0
    
    def test_calculate_composite_score_all_high(self):
        """Test composite score with all high values."""
        indices_results = {
            "sii": {"risk_level": "high"},
            "nlr": {"risk_level": "high"},
            "plr": {"risk_level": "high"},
            "siri": {"risk_level": "high"},
            "mlr": {"risk_level": "high"},
            "piv": {"risk_level": "high"}
        }
        
        score = _calculate_composite_score(indices_results)
        assert score == 4.0
    
    def test_calculate_composite_score_mixed(self):
        """Test composite score with mixed values."""
        indices_results = {
            "sii": {"risk_level": "high"},      # score 4, weight 0.25
            "nlr": {"risk_level": "moderate"},  # score 3, weight 0.20
            "plr": {"risk_level": "normal"}     # score 1, weight 0.15
        }
        
        score = _calculate_composite_score(indices_results)
        expected = (4*0.25 + 3*0.20 + 1*0.15) / 0.60
        assert abs(score - expected) < 0.01
    
    def test_calculate_composite_score_unknown_indices(self):
        """Test composite score with unknown indices."""
        indices_results = {
            "unknown_index": {"risk_level": "high"}
        }
        
        score = _calculate_composite_score(indices_results)
        assert score == 1.0  # Default when no known indices


class TestRecommendations:
    """Test recommendation generation."""
    
    def test_generate_recommendations_normal(self):
        """Test recommendations for normal values."""
        indices_results = {
            "sii": {"risk_level": "normal"},
            "nlr": {"risk_level": "normal"}
        }
        
        recommendations = _generate_recommendations(indices_results, None, None)
        
        # Should have basic structure
        expected_keys = ["immediate", "short_term", "long_term", "lifestyle", "monitoring"]
        for key in expected_keys:
            assert key in recommendations
            assert isinstance(recommendations[key], list)
        
        # Normal values shouldn't have immediate recommendations
        assert len(recommendations["immediate"]) == 0
    
    def test_generate_recommendations_high_risk(self):
        """Test recommendations for high-risk values."""
        indices_results = {
            "sii": {"risk_level": "high"},
            "nlr": {"risk_level": "very_high"}
        }
        
        recommendations = _generate_recommendations(indices_results, None, None)
        
        # Should have immediate recommendations
        assert len(recommendations["immediate"]) > 0
        assert any("urgent" in rec.lower() or "emergency" in rec.lower() 
                  for rec in recommendations["immediate"])
        
        # Should have short-term recommendations
        assert len(recommendations["short_term"]) > 0
        
        # Should have lifestyle recommendations
        assert len(recommendations["lifestyle"]) > 0
    
    def test_generate_recommendations_moderate_risk(self):
        """Test recommendations for moderate-risk values."""
        indices_results = {
            "sii": {"risk_level": "moderate"},
            "nlr": {"risk_level": "mild"}
        }
        
        recommendations = _generate_recommendations(indices_results, None, None)
        
        # Should have short-term and lifestyle recommendations
        assert len(recommendations["short_term"]) > 0
        assert len(recommendations["lifestyle"]) > 0
        
        # Monitoring should be monthly
        monitoring_text = " ".join(recommendations["monitoring"])
        assert "monthly" in monitoring_text
    
    def test_generate_recommendations_monitoring_frequency(self):
        """Test monitoring frequency based on risk level."""
        # High risk
        high_risk_results = {"sii": {"risk_level": "high"}}
        high_recs = _generate_recommendations(high_risk_results, None, None)
        high_monitoring = " ".join(high_recs["monitoring"])
        assert "monthly" in high_monitoring
        
        # Moderate risk
        mod_risk_results = {"sii": {"risk_level": "moderate"}}
        mod_recs = _generate_recommendations(mod_risk_results, None, None)
        mod_monitoring = " ".join(mod_recs["monitoring"])
        assert "quarterly" in mod_monitoring
        
        # Normal risk
        normal_risk_results = {"sii": {"risk_level": "normal"}}
        normal_recs = _generate_recommendations(normal_risk_results, None, None)
        normal_monitoring = " ".join(normal_recs["monitoring"])
        assert "annually" in normal_monitoring


class TestFollowUpGuidance:
    """Test follow-up guidance generation."""
    
    def test_generate_followup_guidance_high_risk(self):
        """Test follow-up guidance for high-risk values."""
        indices_results = {
            "sii": {"risk_level": "high"},
            "nlr": {"risk_level": "moderate"}
        }
        
        guidance = _generate_followup_guidance(indices_results)
        
        expected_keys = ["follow_up_timing", "monitoring_frequency", 
                        "key_parameters_to_track", "concerning_changes", 
                        "specialist_referral_criteria"]
        for key in expected_keys:
            assert key in guidance
        
        assert "2-4 weeks" in guidance["follow_up_timing"]
        assert "bi-weekly" in guidance["monitoring_frequency"]
    
    def test_generate_followup_guidance_critical_risk(self):
        """Test follow-up guidance for critical risk."""
        indices_results = {
            "sii": {"risk_level": "very_high"}
        }
        
        guidance = _generate_followup_guidance(indices_results)
        
        assert "1-2 weeks" in guidance["follow_up_timing"]
        assert "weekly" in guidance["monitoring_frequency"]
    
    def test_generate_followup_guidance_normal_risk(self):
        """Test follow-up guidance for normal risk."""
        indices_results = {
            "sii": {"risk_level": "normal"},
            "nlr": {"risk_level": "normal"}
        }
        
        guidance = _generate_followup_guidance(indices_results)
        
        assert "3-6 months" in guidance["follow_up_timing"]
        assert "quarterly" in guidance["monitoring_frequency"]
    
    def test_followup_guidance_content_quality(self):
        """Test quality of follow-up guidance content."""
        indices_results = {"sii": {"risk_level": "moderate"}}
        guidance = _generate_followup_guidance(indices_results)
        
        # Should include CBC tracking
        parameters = guidance["key_parameters_to_track"]
        assert any("blood count" in param.lower() for param in parameters)
        
        # Should include concerning changes
        changes = guidance["concerning_changes"]
        assert len(changes) > 0
        assert any("worsening" in change.lower() for change in changes)
        
        # Should include referral criteria
        criteria = guidance["specialist_referral_criteria"]
        assert len(criteria) > 0
        assert any("elevated" in criterion.lower() for criterion in criteria)


class TestIntegrationScenarios:
    """Test complete interpretation scenarios."""
    
    def test_young_healthy_adult_scenario(self):
        """Test interpretation for young healthy adult."""
        indices_results = {
            "sii": {"value": 400, "risk_level": "normal"},
            "nlr": {"value": 2.0, "risk_level": "normal"},
            "plr": {"value": 120, "risk_level": "normal"}
        }
        
        result = interpret_results(indices_results, patient_age=25, patient_sex="M")
        
        assert result["risk_stratification"]["overall_risk_level"] == "low"
        assert len(result["recommendations"]["immediate"]) == 0
        assert "acute pathology" in str(result["patient_context"]["age_considerations"])
    
    def test_elderly_high_inflammation_scenario(self):
        """Test interpretation for elderly patient with high inflammation."""
        indices_results = {
            "sii": {"value": 2500, "risk_level": "high"},
            "nlr": {"value": 8.0, "risk_level": "high"},
            "plr": {"value": 350, "risk_level": "high"},
            "siri": {"value": 5.0, "risk_level": "high"}
        }
        
        result = interpret_results(indices_results, patient_age=75, patient_sex="F")
        
        assert result["risk_stratification"]["overall_risk_level"] in ["high", "critical"]
        assert len(result["recommendations"]["immediate"]) > 0
        assert any("age" in modifier for modifier in result["risk_stratification"]["risk_modifiers"])
        assert "baseline elevation" in str(result["patient_context"]["age_considerations"])
    
    def test_middle_aged_female_moderate_inflammation(self):
        """Test interpretation for middle-aged female with moderate inflammation."""
        indices_results = {
            "sii": {"value": 800, "risk_level": "moderate"},
            "nlr": {"value": 4.0, "risk_level": "moderate"},
            "plr": {"value": 200, "risk_level": "mild"}
        }
        
        result = interpret_results(indices_results, patient_age=45, patient_sex="F")
        
        assert result["risk_stratification"]["overall_risk_level"] in ["moderate", "moderate_to_high"]
        assert "autoimmune" in str(result["patient_context"]["sex_considerations"])
        assert "inflammaging" in str(result["patient_context"]["age_considerations"])
        assert len(result["recommendations"]["lifestyle"]) > 0


# Property-based testing
class TestPropertyBasedInterpretation:
    """Property-based tests for interpretation functions."""
    
    @given(age=st.integers(min_value=1, max_value=100))
    def test_age_considerations_properties(self, age):
        """Test age considerations properties."""
        considerations = _get_age_considerations(age)
        
        # Should always return a list
        assert isinstance(considerations, list)
        
        # Should have considerations for all ages
        assert len(considerations) > 0
        
        # All considerations should be strings
        assert all(isinstance(c, str) for c in considerations)
    
    @given(risk_level=st.sampled_from(["normal", "mild", "moderate", "high", "very_high"]))
    def test_composite_score_properties(self, risk_level):
        """Test composite score calculation properties."""
        indices_results = {
            "sii": {"risk_level": risk_level},
            "nlr": {"risk_level": risk_level}
        }
        
        score = _calculate_composite_score(indices_results)
        
        # Score should be between 1 and 5
        assert 1.0 <= score <= 5.0
        
        # Score should increase with risk level
        risk_order = ["normal", "mild", "moderate", "high", "very_high"]
        expected_score = risk_order.index(risk_level) + 1
        assert abs(score - expected_score) < 0.1