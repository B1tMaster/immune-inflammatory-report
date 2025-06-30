"""Property-based tests using hypothesis for robust edge case testing."""

import pytest
from hypothesis import given, strategies as st, assume, settings
from hypothesis.strategies import composite
import math

from immune_inflam_index.calculator import calculate_indices
from immune_inflam_index.validator import validate_inputs, validate_pdf_extracted_values
from immune_inflam_index.extractor import extract_cbc_values, parse_value_with_unit
from immune_inflam_index.interpreter import interpret_results


# Custom strategies for realistic blood count values
@composite
def realistic_blood_counts(draw):
    """Generate realistic blood count values."""
    # Realistic ranges based on medical literature
    neutrophils = draw(st.integers(min_value=1000, max_value=25000))
    lymphocytes = draw(st.integers(min_value=200, max_value=8000))
    platelets = draw(st.integers(min_value=50000, max_value=1000000))
    monocytes = draw(st.one_of(
        st.none(),
        st.integers(min_value=100, max_value=2000)
    ))
    
    return {
        'neutrophils': neutrophils,
        'lymphocytes': lymphocytes,
        'platelets': platelets,
        'monocytes': monocytes
    }


@composite
def extreme_blood_counts(draw):
    """Generate extreme but potentially valid blood count values."""
    neutrophils = draw(st.integers(min_value=1, max_value=100000))
    lymphocytes = draw(st.integers(min_value=1, max_value=50000))
    platelets = draw(st.integers(min_value=1, max_value=2000000))
    monocytes = draw(st.one_of(
        st.none(),
        st.integers(min_value=1, max_value=10000)
    ))
    
    return {
        'neutrophils': neutrophils,
        'lymphocytes': lymphocytes,
        'platelets': platelets,
        'monocytes': monocytes
    }


@composite
def patient_demographics(draw):
    """Generate realistic patient demographics."""
    age = draw(st.one_of(st.none(), st.integers(min_value=0, max_value=120)))
    sex = draw(st.one_of(st.none(), st.sampled_from(['M', 'F', 'Male', 'Female'])))
    
    return {'age': age, 'sex': sex}


class TestCalculatorProperties:
    """Property-based tests for calculator module."""
    
    @given(realistic_blood_counts())
    @settings(max_examples=200)
    def test_calculate_indices_realistic_values(self, blood_counts):
        """Test calculator with realistic blood count values."""
        results = calculate_indices(
            blood_counts['neutrophils'],
            blood_counts['lymphocytes'],
            blood_counts['platelets'],
            blood_counts['monocytes']
        )
        
        # All calculations should succeed without errors
        assert "results" in results
        assert "summary" in results
        assert "metadata" in results
        
        # Core indices should always be present
        assert "sii" in results["results"]
        assert "nlr" in results["results"]
        assert "plr" in results["results"]
        
        # Values should be positive numbers
        for index_name, index_data in results["results"].items():
            assert index_data["value"] > 0
            assert isinstance(index_data["value"], (int, float))
            assert not math.isnan(index_data["value"])
            assert not math.isinf(index_data["value"])
            
            # Risk levels should be valid
            assert index_data["risk_level"] in ["low", "normal", "mild", "moderate", "high", "severe"]
            
            # Interpretations should be non-empty strings
            assert isinstance(index_data["interpretation"], str)
            assert len(index_data["interpretation"]) > 0
    
    @given(extreme_blood_counts())
    @settings(max_examples=100)
    def test_calculate_indices_extreme_values(self, blood_counts):
        """Test calculator with extreme blood count values."""
        try:
            results = calculate_indices(
                blood_counts['neutrophils'],
                blood_counts['lymphocytes'],
                blood_counts['platelets'],
                blood_counts['monocytes']
            )
            
            # If calculation succeeds, results should be valid
            assert "results" in results
            
            for index_name, index_data in results["results"].items():
                # Values should be finite numbers
                assert isinstance(index_data["value"], (int, float))
                assert not math.isnan(index_data["value"])
                assert not math.isinf(index_data["value"])
                assert index_data["value"] >= 0
                
        except (ValueError, ZeroDivisionError):
            # Some extreme values may legitimately cause errors
            # This is acceptable behavior
            pass
    
    @given(
        neutrophils=st.floats(min_value=1.0, max_value=50000.0, allow_nan=False, allow_infinity=False),
        lymphocytes=st.floats(min_value=1.0, max_value=20000.0, allow_nan=False, allow_infinity=False),
        platelets=st.floats(min_value=1000.0, max_value=1500000.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=150)
    def test_calculate_sii_properties(self, neutrophils, lymphocytes, platelets):
        """Test SII calculation properties."""
        results = calculate_indices(neutrophils, lymphocytes, platelets, None)
        sii_value = results["results"]["sii"]["value"]
        
        # SII = (Neutrophils × Platelets) / Lymphocytes
        expected_sii = (neutrophils * platelets) / lymphocytes
        
        # Allow for small rounding differences
        assert abs(sii_value - expected_sii) < 0.01 * expected_sii
        
        # SII should scale with neutrophils and platelets, inverse with lymphocytes
        # Test monotonicity properties
        if neutrophils > 1:
            higher_n_results = calculate_indices(neutrophils * 2, lymphocytes, platelets, None)
            higher_n_sii = higher_n_results["results"]["sii"]["value"]
            assert higher_n_sii > sii_value  # Higher neutrophils = higher SII
        
        if lymphocytes > 1:
            higher_l_results = calculate_indices(neutrophils, lymphocytes * 2, platelets, None)
            higher_l_sii = higher_l_results["results"]["sii"]["value"]
            assert higher_l_sii < sii_value  # Higher lymphocytes = lower SII
    
    @given(
        neutrophils=st.floats(min_value=1.0, max_value=50000.0, allow_nan=False, allow_infinity=False),
        lymphocytes=st.floats(min_value=1.0, max_value=20000.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=150)
    def test_calculate_nlr_properties(self, neutrophils, lymphocytes):
        """Test NLR calculation properties."""
        results = calculate_indices(neutrophils, lymphocytes, 250000, None)
        nlr_value = results["results"]["nlr"]["value"]
        
        # NLR = Neutrophils / Lymphocytes
        expected_nlr = neutrophils / lymphocytes
        
        # Allow for small rounding differences
        assert abs(nlr_value - expected_nlr) < 0.01 * expected_nlr
        
        # NLR should be >= minimum possible value
        assert nlr_value >= 0.01  # Reasonable minimum
        
        # Test ratio properties
        if neutrophils > lymphocytes:
            assert nlr_value > 1.0  # More neutrophils than lymphocytes
        elif neutrophils < lymphocytes:
            assert nlr_value < 1.0  # More lymphocytes than neutrophils


class TestValidatorProperties:
    """Property-based tests for validator module."""
    
    @given(realistic_blood_counts())
    @settings(max_examples=100)
    def test_validate_inputs_realistic_values(self, blood_counts):
        """Test input validation with realistic values."""
        result = validate_inputs(
            blood_counts['neutrophils'],
            blood_counts['lymphocytes'],
            blood_counts['platelets'],
            blood_counts['monocytes']
        )
        
        # Realistic values should generally pass validation
        assert result["valid"] is True
        assert "errors" not in result or len(result["errors"]) == 0
    
    @given(
        neutrophils=st.one_of(
            st.integers(min_value=-1000, max_value=0),  # Negative values
            st.integers(min_value=100000, max_value=1000000),  # Extremely high values
        ),
        lymphocytes=st.integers(min_value=100, max_value=5000),
        platelets=st.integers(min_value=100000, max_value=500000)
    )
    @settings(max_examples=50)
    def test_validate_inputs_invalid_neutrophils(self, neutrophils, lymphocytes, platelets):
        """Test validation catches invalid neutrophil values."""
        result = validate_inputs(neutrophils, lymphocytes, platelets, None)
        
        if neutrophils <= 0:
            assert result["valid"] is False
            assert any("neutrophil" in error.lower() for error in result["errors"])
        elif neutrophils > 50000:  # Extremely high
            # May pass validation but should generate warnings
            assert "warnings" in result
    
    @given(
        extracted_values=st.dictionaries(
            keys=st.sampled_from(["neutrophils", "lymphocytes", "platelets", "monocytes"]),
            values=st.dictionaries(
                keys=st.sampled_from(["value", "confidence"]),
                values=st.one_of(
                    st.integers(min_value=1, max_value=50000),  # Valid values
                    st.integers(min_value=50, max_value=98)     # Confidence scores
                ),
                min_size=2,
                max_size=2
            ),
            min_size=3,  # At least neutrophils, lymphocytes, platelets
            max_size=4
        )
    )
    @settings(max_examples=50)
    def test_validate_pdf_extracted_values_properties(self, extracted_values):
        """Test PDF validation properties."""
        result = validate_pdf_extracted_values(extracted_values)
        
        # Result should always have required fields
        assert "valid" in result
        assert "warnings" in result
        assert "manual_verification_needed" in result
        
        # If all required fields present, should be valid
        required_fields = {"neutrophils", "lymphocytes", "platelets"}
        if required_fields.issubset(extracted_values.keys()):
            # Check if all values are reasonable
            all_reasonable = all(
                1 <= extracted_values[field]["value"] <= 50000
                for field in required_fields
            )
            if all_reasonable:
                assert result["valid"] is True


class TestExtractorProperties:
    """Property-based tests for extractor module."""
    
    @given(
        value=st.floats(min_value=0.1, max_value=1000000.0, allow_nan=False, allow_infinity=False),
        unit=st.sampled_from(["cells/µL", "x10³/L", "K/µL", "/µL", "cells/uL"])
    )
    @settings(max_examples=100)
    def test_parse_value_with_unit_properties(self, value, unit):
        """Test value parsing properties."""
        # Create test string
        test_string = f"{value:.2f} {unit}"
        
        parsed_value, parsed_unit = parse_value_with_unit(test_string)
        
        if parsed_value is not None:
            # Parsed value should be numeric
            assert isinstance(parsed_value, (int, float))
            assert not math.isnan(parsed_value)
            assert not math.isinf(parsed_value)
            assert parsed_value > 0
            
            # If unit needs conversion, result should be different
            if unit in ["x10³/L", "K/µL"]:
                assert parsed_value != value  # Should be converted
            else:
                # Allow for rounding differences
                assert abs(parsed_value - value) < 0.01 * value
    
    @given(
        st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Pd', 'Ps', 'Pe', 'Po')),
            min_size=10,
            max_size=1000
        )
    )
    @settings(max_examples=50)
    def test_extract_cbc_values_robustness(self, text):
        """Test CBC extraction robustness with random text."""
        # Should not crash on any input
        try:
            result = extract_cbc_values(text)
            
            # Result should be a dictionary
            assert isinstance(result, dict)
            
            # All values should have proper structure if present
            for field_name, field_data in result.items():
                assert isinstance(field_data, dict)
                if "value" in field_data:
                    assert isinstance(field_data["value"], (int, float))
                    assert field_data["value"] > 0
                if "confidence" in field_data:
                    assert 0 <= field_data["confidence"] <= 100
                    
        except Exception as e:
            # Should not raise unexpected exceptions
            assert False, f"Unexpected exception: {e}"


class TestInterpreterProperties:
    """Property-based tests for interpreter module."""
    
    @given(
        results=st.dictionaries(
            keys=st.sampled_from(["sii", "nlr", "plr", "siri", "mlr", "piv"]),
            values=st.dictionaries(
                keys=st.just("value"),
                values=st.floats(min_value=0.1, max_value=10000.0, allow_nan=False, allow_infinity=False)
            ),
            min_size=3,
            max_size=6
        ),
        demographics=patient_demographics()
    )
    @settings(max_examples=100)
    def test_interpret_results_properties(self, results, demographics):
        """Test interpretation properties."""
        # Prepare results in expected format
        formatted_results = {}
        for index_name, index_data in results.items():
            formatted_results[index_name] = {
                "value": index_data["value"],
                "risk_level": "normal",  # Placeholder
                "interpretation": "Test interpretation"
            }
        
        interpretation = interpret_results(
            formatted_results,
            patient_age=demographics['age'],
            patient_sex=demographics['sex']
        )
        
        # Interpretation should have expected structure
        assert isinstance(interpretation, dict)
        
        # Should include clinical assessment
        if "clinical_assessment" in interpretation:
            clinical = interpretation["clinical_assessment"]
            assert isinstance(clinical, dict)
            
            # Each assessed index should have proper structure
            for index_name, assessment in clinical.items():
                assert isinstance(assessment, dict)
                if "clinical_significance" in assessment:
                    assert isinstance(assessment["clinical_significance"], str)
                    assert len(assessment["clinical_significance"]) > 0
        
        # Risk stratification should be valid if present
        if "risk_stratification" in interpretation:
            risk = interpretation["risk_stratification"]
            assert isinstance(risk, dict)
            
            if "overall_risk_level" in risk:
                assert risk["overall_risk_level"] in ["low", "moderate", "high", "critical"]
            
            if "urgency" in risk:
                assert risk["urgency"] in [
                    "routine_monitoring", "increased_monitoring", 
                    "urgent_evaluation", "immediate_attention"
                ]
    
    @given(
        age=st.integers(min_value=18, max_value=100),
        sex=st.sampled_from(['M', 'F'])
    )
    @settings(max_examples=50)
    def test_age_sex_specific_interpretation_properties(self, age, sex):
        """Test age and sex-specific interpretation properties."""
        # Create sample results
        sample_results = {
            "sii": {"value": 1000.0, "risk_level": "normal", "interpretation": "Normal"},
            "nlr": {"value": 2.5, "risk_level": "normal", "interpretation": "Normal"}
        }
        
        interpretation = interpret_results(sample_results, patient_age=age, patient_sex=sex)
        
        # Should include patient context
        if "patient_context" in interpretation:
            context = interpretation["patient_context"]
            assert context["age"] == age
            assert context["sex"] == sex
            
            # Age considerations should be appropriate
            if "age_considerations" in context:
                considerations = context["age_considerations"]
                assert isinstance(considerations, list)
                
                # Check age-appropriate content
                if age < 35:
                    assert any("young" in str(cons).lower() for cons in considerations)
                elif age > 65:
                    assert any("elderly" in str(cons).lower() or "older" in str(cons).lower() 
                              for cons in considerations)


class TestCrossModuleProperties:
    """Property-based tests across multiple modules."""
    
    @given(realistic_blood_counts())
    @settings(max_examples=50)
    def test_full_pipeline_consistency(self, blood_counts):
        """Test consistency across the full calculation pipeline."""
        # Step 1: Validate inputs
        validation = validate_inputs(
            blood_counts['neutrophils'],
            blood_counts['lymphocytes'],
            blood_counts['platelets'],
            blood_counts['monocytes']
        )
        
        if validation["valid"]:
            # Step 2: Calculate indices
            results = calculate_indices(
                blood_counts['neutrophils'],
                blood_counts['lymphocytes'],
                blood_counts['platelets'],
                blood_counts['monocytes']
            )
            
            # Step 3: Interpret results
            interpretation = interpret_results(results["results"])
            
            # Cross-module consistency checks
            assert isinstance(results, dict)
            assert isinstance(interpretation, dict)
            
            # Number of interpreted indices should match calculated indices
            calculated_indices = set(results["results"].keys())
            
            if "clinical_assessment" in interpretation:
                interpreted_indices = set(interpretation["clinical_assessment"].keys())
                # All calculated indices should have clinical assessment
                assert calculated_indices.issubset(interpreted_indices)
    
    @given(
        realistic_blood_counts(),
        age=st.integers(min_value=20, max_value=80),
        sex=st.sampled_from(['M', 'F'])
    )
    @settings(max_examples=30)
    def test_demographic_influence_properties(self, blood_counts, age, sex):
        """Test that demographics appropriately influence interpretation."""
        # Calculate without demographics
        results = calculate_indices(
            blood_counts['neutrophils'],
            blood_counts['lymphocytes'],
            blood_counts['platelets'],
            blood_counts['monocytes']
        )
        
        interpretation_without = interpret_results(results["results"])
        interpretation_with = interpret_results(
            results["results"], 
            patient_age=age, 
            patient_sex=sex
        )
        
        # With demographics should have additional context
        assert len(interpretation_with) >= len(interpretation_without)
        
        # Should include patient context when demographics provided
        assert "patient_context" in interpretation_with
        assert interpretation_with["patient_context"]["age"] == age
        assert interpretation_with["patient_context"]["sex"] == sex
    
    @given(
        value1=st.floats(min_value=1.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
        value2=st.floats(min_value=1.0, max_value=10000.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=50)
    def test_calculation_monotonicity(self, value1, value2):
        """Test monotonicity properties of calculations."""
        assume(abs(value1 - value2) > 0.01)  # Ensure meaningful difference
        
        base_lymphocytes = 2000
        base_platelets = 250000
        
        # Calculate with both neutrophil values
        results1 = calculate_indices(value1, base_lymphocytes, base_platelets, None)
        results2 = calculate_indices(value2, base_lymphocytes, base_platelets, None)
        
        sii1 = results1["results"]["sii"]["value"]
        sii2 = results2["results"]["sii"]["value"]
        nlr1 = results1["results"]["nlr"]["value"]
        nlr2 = results2["results"]["nlr"]["value"]
        
        # SII and NLR should be monotonic with neutrophils
        if value1 > value2:
            assert sii1 > sii2, f"SII not monotonic: {sii1} <= {sii2} for neutrophils {value1} > {value2}"
            assert nlr1 > nlr2, f"NLR not monotonic: {nlr1} <= {nlr2} for neutrophils {value1} > {value2}"
        else:
            assert sii1 < sii2, f"SII not monotonic: {sii1} >= {sii2} for neutrophils {value1} < {value2}"
            assert nlr1 < nlr2, f"NLR not monotonic: {nlr1} >= {nlr2} for neutrophils {value1} < {value2}"


class TestNumericalStabilityProperties:
    """Property-based tests for numerical stability."""
    
    @given(
        neutrophils=st.floats(min_value=1.0, max_value=1e6, allow_nan=False, allow_infinity=False),
        lymphocytes=st.floats(min_value=1.0, max_value=1e5, allow_nan=False, allow_infinity=False),
        platelets=st.floats(min_value=1e3, max_value=1e7, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_numerical_stability(self, neutrophils, lymphocytes, platelets):
        """Test numerical stability with wide range of values."""
        try:
            results = calculate_indices(neutrophils, lymphocytes, platelets, None)
            
            # All results should be finite
            for index_name, index_data in results["results"].items():
                value = index_data["value"]
                assert isinstance(value, (int, float))
                assert math.isfinite(value), f"{index_name} produced non-finite value: {value}"
                assert value > 0, f"{index_name} produced non-positive value: {value}"
                
                # Values should not be unreasonably large
                assert value < 1e10, f"{index_name} produced unreasonably large value: {value}"
                
        except (ValueError, ZeroDivisionError, OverflowError):
            # Some extreme combinations may legitimately fail
            pass
    
    @given(
        small_values=st.tuples(
            st.floats(min_value=0.01, max_value=1.0, allow_nan=False, allow_infinity=False),
            st.floats(min_value=0.01, max_value=1.0, allow_nan=False, allow_infinity=False),
            st.floats(min_value=10.0, max_value=100.0, allow_nan=False, allow_infinity=False)
        )
    )
    @settings(max_examples=50)
    def test_small_value_handling(self, small_values):
        """Test handling of very small values."""
        neutrophils, lymphocytes, platelets = small_values
        
        try:
            results = calculate_indices(neutrophils, lymphocytes, platelets, None)
            
            # Should handle small values gracefully
            for index_name, index_data in results["results"].items():
                value = index_data["value"]
                assert math.isfinite(value)
                assert value >= 0
                
        except (ValueError, ZeroDivisionError):
            # Very small values may legitimately cause issues
            pass