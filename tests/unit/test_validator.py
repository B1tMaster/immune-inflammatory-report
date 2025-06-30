"""Unit tests for the validator module."""

import pytest
from hypothesis import given, strategies as st
from typing import Dict, Any

from immune_inflam_index.validator import (
    validate_numeric_value, validate_inputs, validate_pdf_extracted_values,
    check_reference_ranges
)


class TestValidateNumericValue:
    """Test individual numeric value validation."""
    
    def test_valid_numeric_value(self):
        """Test validation of valid numeric values."""
        result = validate_numeric_value(4200, "neutrophils", 1800, 7700)
        
        assert result["valid"] is True
        assert result["value"] == 4200.0
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0
    
    def test_string_numeric_value(self):
        """Test validation accepts string numbers."""
        result = validate_numeric_value("4200", "neutrophils", 1800, 7700)
        
        assert result["valid"] is True
        assert result["value"] == 4200.0
        assert len(result["errors"]) == 0
    
    def test_float_value(self):
        """Test validation of float values."""
        result = validate_numeric_value(4200.5, "neutrophils", 1800, 7700)
        
        assert result["valid"] is True
        assert result["value"] == 4200.5
        assert len(result["errors"]) == 0
    
    def test_invalid_string_value(self):
        """Test validation rejects non-numeric strings."""
        result = validate_numeric_value("not_a_number", "neutrophils", 1800, 7700)
        
        assert result["valid"] is False
        assert "must be a numeric value" in result["errors"][0]
        assert "str" in result["errors"][0]
    
    def test_none_value(self):
        """Test validation rejects None values."""
        result = validate_numeric_value(None, "neutrophils", 1800, 7700)
        
        assert result["valid"] is False
        assert "must be a numeric value" in result["errors"][0]
        assert "NoneType" in result["errors"][0]
    
    def test_negative_value(self):
        """Test validation rejects negative values."""
        result = validate_numeric_value(-1000, "neutrophils", 1800, 7700)
        
        assert result["valid"] is False
        assert "cannot be negative" in result["errors"][0]
    
    def test_zero_lymphocytes(self):
        """Test validation rejects zero lymphocytes (critical for calculations)."""
        result = validate_numeric_value(0, "lymphocytes", 1000, 4000)
        
        assert result["valid"] is False
        assert "cannot be zero" in result["errors"][0]
        assert "ratio calculations" in result["errors"][0]
    
    def test_zero_non_lymphocytes(self):
        """Test validation warns for zero non-lymphocyte values."""
        result = validate_numeric_value(0, "neutrophils", 1800, 7700)
        
        assert result["valid"] is True  # Warning, not error
        assert len(result["warnings"]) == 1
        assert "is zero" in result["warnings"][0]
        assert "severe condition" in result["warnings"][0]
    
    def test_value_outside_normal_range_mild(self):
        """Test validation warns for values outside normal range."""
        result = validate_numeric_value(8000, "neutrophils", 1800, 7700)  # Slightly high
        
        assert result["valid"] is True  # Warning, not error
        assert len(result["warnings"]) == 1
        assert "outside normal range" in result["warnings"][0]
    
    def test_value_extremely_outside_range(self):
        """Test validation errors for extremely abnormal values."""
        result = validate_numeric_value(100000, "neutrophils", 1800, 7700)  # 10x higher than max
        
        assert result["valid"] is False
        assert "extremely outside normal range" in result["errors"][0]
        assert "data entry error" in result["errors"][0]
    
    def test_value_extremely_low(self):
        """Test validation errors for extremely low values."""
        result = validate_numeric_value(18, "neutrophils", 1800, 7700)  # 10x lower than min
        
        assert result["valid"] is False
        assert "extremely outside normal range" in result["errors"][0]


class TestValidateInputs:
    """Test complete input validation."""
    
    def test_valid_complete_inputs(self, sample_blood_values):
        """Test validation of valid complete blood count."""
        result = validate_inputs(**sample_blood_values)
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert result["summary"]["parameters_validated"] == 4  # All 4 parameters
        
        # Check individual results
        for param in ["neutrophils", "lymphocytes", "platelets", "monocytes"]:
            assert param in result["individual_results"]
            assert result["individual_results"][param]["valid"] is True
    
    def test_valid_inputs_no_monocytes(self, sample_blood_values):
        """Test validation without monocytes."""
        blood_values = sample_blood_values.copy()
        blood_values.pop("monocytes")
        
        result = validate_inputs(**blood_values)
        
        assert result["valid"] is True
        assert result["summary"]["parameters_validated"] == 3  # Only 3 parameters
        assert "monocytes" not in result["individual_results"]
    
    def test_invalid_lymphocytes_zero(self):
        """Test validation fails with zero lymphocytes."""
        result = validate_inputs(4200, 0, 250000, 480)
        
        assert result["valid"] is False
        assert any("lymphocytes" in error and "zero" in error for error in result["errors"])
    
    def test_invalid_string_inputs(self):
        """Test validation fails with invalid string inputs."""
        result = validate_inputs("invalid", 1800, 250000, 480)
        
        assert result["valid"] is False
        assert any("neutrophils" in error and "numeric" in error for error in result["errors"])
    
    def test_mixed_valid_invalid_inputs(self):
        """Test validation with mix of valid and invalid inputs."""
        result = validate_inputs(-1000, 1800, "invalid", 480)
        
        assert result["valid"] is False
        assert len(result["errors"]) == 2  # Two invalid inputs
        assert any("neutrophils" in error and "negative" in error for error in result["errors"])
        assert any("platelets" in error and "numeric" in error for error in result["errors"])
    
    def test_extreme_nlr_warning(self):
        """Test warning for extremely high NLR."""
        result = validate_inputs(50000, 100, 250000, 480)  # NLR = 500
        
        assert result["valid"] is True  # Valid but with warnings
        assert any("NLR" in warning and "extremely high" in warning for warning in result["warnings"])
    
    def test_extreme_plr_warning(self):
        """Test warning for extremely high PLR."""
        result = validate_inputs(4200, 100, 200000, 480)  # PLR = 2000
        
        assert result["valid"] is True
        assert any("PLR" in warning and "extremely high" in warning for warning in result["warnings"])
    
    def test_validation_summary(self, sample_blood_values_high_inflammation):
        """Test validation summary generation."""
        result = validate_inputs(**sample_blood_values_high_inflammation)
        
        summary = result["summary"]
        assert "total_errors" in summary
        assert "total_warnings" in summary
        assert "parameters_validated" in summary
        assert summary["parameters_validated"] == 4


class TestValidatePdfExtractedValues:
    """Test PDF extracted values validation."""
    
    def test_valid_pdf_extraction(self):
        """Test validation of good PDF extraction."""
        extracted_values = {
            "neutrophils": {"value": 4200, "confidence": 95},
            "lymphocytes": {"value": 1800, "confidence": 90},
            "platelets": {"value": 250000, "confidence": 98},
            "monocytes": {"value": 480, "confidence": 85}
        }
        
        result = validate_pdf_extracted_values(extracted_values)
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert result["manual_verification_needed"] is False
        assert len(result["confidence_issues"]) == 0
    
    def test_missing_required_field(self):
        """Test validation fails when required field is missing."""
        extracted_values = {
            "neutrophils": {"value": 4200, "confidence": 95},
            # Missing lymphocytes
            "platelets": {"value": 250000, "confidence": 98}
        }
        
        result = validate_pdf_extracted_values(extracted_values)
        
        assert result["valid"] is False
        assert any("lymphocytes" in error and "not found" in error for error in result["errors"])
    
    def test_low_confidence_extraction(self):
        """Test handling of low confidence extractions."""
        extracted_values = {
            "neutrophils": {"value": 4200, "confidence": 45},  # Low confidence
            "lymphocytes": {"value": 1800, "confidence": 90},
            "platelets": {"value": 250000, "confidence": 98}
        }
        
        result = validate_pdf_extracted_values(extracted_values)
        
        assert result["valid"] is True  # Valid but needs verification
        assert result["manual_verification_needed"] is True
        assert len(result["confidence_issues"]) == 1
        assert "neutrophils" in result["confidence_issues"][0]
        assert any("Low confidence" in warning for warning in result["warnings"])
    
    def test_moderate_confidence_extraction(self):
        """Test handling of moderate confidence extractions."""
        extracted_values = {
            "neutrophils": {"value": 4200, "confidence": 65},  # Moderate confidence
            "lymphocytes": {"value": 1800, "confidence": 90},
            "platelets": {"value": 250000, "confidence": 98}
        }
        
        result = validate_pdf_extracted_values(extracted_values)
        
        assert result["valid"] is True
        assert result["manual_verification_needed"] is True  # Due to confidence issue
        assert len(result["confidence_issues"]) == 1
        assert len(result["warnings"]) == 0  # No warning for moderate confidence
    
    def test_invalid_extracted_values(self):
        """Test validation of invalid extracted values."""
        extracted_values = {
            "neutrophils": {"value": -1000, "confidence": 95},  # Invalid value
            "lymphocytes": {"value": 0, "confidence": 90},      # Zero lymphocytes
            "platelets": {"value": 250000, "confidence": 98}
        }
        
        result = validate_pdf_extracted_values(extracted_values)
        
        assert result["valid"] is False
        assert len(result["errors"]) >= 2  # At least 2 errors
        assert any("negative" in error for error in result["errors"])
        assert any("cannot be zero" in error for error in result["errors"])
    
    def test_optional_monocytes_extraction(self):
        """Test handling of optional monocytes in PDF extraction."""
        extracted_values = {
            "neutrophils": {"value": 4200, "confidence": 95},
            "lymphocytes": {"value": 1800, "confidence": 90},
            "platelets": {"value": 250000, "confidence": 98},
            "monocytes": {"value": 480, "confidence": 75}
        }
        
        result = validate_pdf_extracted_values(extracted_values)
        
        assert result["valid"] is True
        assert "monocytes" in result["individual_results"]
        assert result["individual_results"]["monocytes"]["valid"] is True


class TestCheckReferenceRanges:
    """Test reference range checking."""
    
    def test_values_within_pdf_ranges(self):
        """Test values within PDF reference ranges."""
        extracted_values = {
            "neutrophils": {"value": 4200},
            "lymphocytes": {"value": 1800},
            "platelets": {"value": 250000}
        }
        
        pdf_ranges = {
            "neutrophils": (1800, 7700),
            "lymphocytes": (1000, 4000),
            "platelets": (150000, 450000)
        }
        
        warnings = check_reference_ranges(extracted_values, pdf_ranges)
        
        assert len(warnings) == 0
    
    def test_values_outside_pdf_ranges(self):
        """Test values outside PDF reference ranges."""
        extracted_values = {
            "neutrophils": {"value": 8500},    # Above range
            "lymphocytes": {"value": 800},     # Below range
            "platelets": {"value": 250000}     # Within range
        }
        
        pdf_ranges = {
            "neutrophils": (1800, 7700),
            "lymphocytes": (1000, 4000),
            "platelets": (150000, 450000)
        }
        
        warnings = check_reference_ranges(extracted_values, pdf_ranges)
        
        assert len(warnings) == 2
        assert any("neutrophils" in warning and "outside PDF reference" in warning for warning in warnings)
        assert any("lymphocytes" in warning and "outside PDF reference" in warning for warning in warnings)
    
    def test_missing_pdf_ranges(self):
        """Test handling when PDF ranges are not available."""
        extracted_values = {
            "neutrophils": {"value": 4200},
            "lymphocytes": {"value": 1800}
        }
        
        pdf_ranges = {
            "neutrophils": (1800, 7700)
            # Missing lymphocytes range
        }
        
        warnings = check_reference_ranges(extracted_values, pdf_ranges)
        
        # Should only check neutrophils, no warning for missing lymphocytes range
        assert len(warnings) == 0
    
    def test_missing_values(self):
        """Test handling when extracted values are missing."""
        extracted_values = {
            "neutrophils": {"value": None},  # Missing value
            "lymphocytes": {"value": 1800}
        }
        
        pdf_ranges = {
            "neutrophils": (1800, 7700),
            "lymphocytes": (1000, 4000)
        }
        
        warnings = check_reference_ranges(extracted_values, pdf_ranges)
        
        # Should only check lymphocytes
        assert len(warnings) == 0


# Property-based testing with hypothesis
class TestPropertyBasedValidation:
    """Property-based tests for validation functions."""
    
    @given(
        value=st.floats(min_value=0.1, max_value=1000000),
        min_val=st.floats(min_value=0.1, max_value=1000),
        max_val=st.floats(min_value=1001, max_value=100000)
    )
    def test_validate_numeric_value_properties(self, value, min_val, max_val):
        """Test properties of numeric value validation."""
        result = validate_numeric_value(value, "test_param", min_val, max_val)
        
        # Result should always have required keys
        assert "valid" in result
        assert "value" in result
        assert "errors" in result
        assert "warnings" in result
        
        # Value should be converted to float
        assert isinstance(result["value"], float)
        
        # If value is within range and positive, should be valid
        if min_val <= value <= max_val and value > 0:
            assert result["valid"] is True
    
    @given(
        neutrophils=st.floats(min_value=1, max_value=100000),
        lymphocytes=st.floats(min_value=1, max_value=50000),
        platelets=st.floats(min_value=1000, max_value=1000000)
    )
    def test_validate_inputs_properties(self, neutrophils, lymphocytes, platelets):
        """Test properties of input validation."""
        result = validate_inputs(neutrophils, lymphocytes, platelets)
        
        # Result should always have required structure
        assert "valid" in result
        assert "individual_results" in result
        assert "errors" in result
        assert "warnings" in result
        assert "summary" in result
        
        # Summary should have correct counts
        summary = result["summary"]
        assert summary["parameters_validated"] == 3  # No monocytes provided
        assert summary["total_errors"] == len(result["errors"])
        assert summary["total_warnings"] == len(result["warnings"])


class TestEdgeCasesAndBoundaryConditions:
    """Test edge cases and boundary conditions."""
    
    def test_boundary_values(self):
        """Test validation at exact boundary values."""
        # Test at exact minimum
        result = validate_numeric_value(1800, "neutrophils", 1800, 7700)
        assert result["valid"] is True
        assert len(result["warnings"]) == 0
        
        # Test at exact maximum
        result = validate_numeric_value(7700, "neutrophils", 1800, 7700)
        assert result["valid"] is True
        assert len(result["warnings"]) == 0
        
        # Test just below minimum
        result = validate_numeric_value(1799, "neutrophils", 1800, 7700)
        assert result["valid"] is True  # Warning, not error
        assert len(result["warnings"]) == 1
        
        # Test just above maximum
        result = validate_numeric_value(7701, "neutrophils", 1800, 7700)
        assert result["valid"] is True  # Warning, not error
        assert len(result["warnings"]) == 1
    
    def test_very_large_numbers(self):
        """Test validation with very large numbers."""
        result = validate_inputs(1e6, 1e5, 1e8, 1e4)  # Very large values
        
        # Should have warnings or errors for extreme values
        assert len(result["warnings"]) > 0 or len(result["errors"]) > 0
    
    def test_very_small_numbers(self):
        """Test validation with very small numbers."""
        result = validate_inputs(0.1, 0.1, 1, 0.01)  # Very small values
        
        # Should have warnings or errors for extreme values
        assert len(result["warnings"]) > 0 or len(result["errors"]) > 0
    
    def test_scientific_notation(self):
        """Test validation accepts scientific notation."""
        result = validate_numeric_value(4.2e3, "neutrophils", 1800, 7700)
        
        assert result["valid"] is True
        assert result["value"] == 4200.0


class TestRegressionTests:
    """Regression tests for known validation scenarios."""
    
    def test_common_lab_values_scenario_1(self):
        """Test validation of common lab values scenario."""
        # Typical healthy adult values
        result = validate_inputs(3500, 2200, 280000, 400)
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
        # May have minor warnings for slightly outside normal range
    
    def test_high_inflammation_scenario(self, sample_blood_values_high_inflammation):
        """Test validation of high inflammation scenario."""
        result = validate_inputs(**sample_blood_values_high_inflammation)
        
        assert result["valid"] is True  # Values are unusual but valid
        # Should have warnings for high values
        assert len(result["warnings"]) > 0
    
    def test_extreme_sepsis_scenario(self):
        """Test validation of extreme sepsis-like values."""
        # Very high neutrophils, very low lymphocytes
        result = validate_inputs(25000, 300, 600000, 1500)
        
        assert result["valid"] is True  # Extreme but medically possible
        assert len(result["warnings"]) > 0  # Should warn about extreme ratios