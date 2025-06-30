"""Unit tests for the calculator module."""

import pytest
from unittest.mock import patch
from hypothesis import given, strategies as st
import math

from immune_inflam_index.calculator import (
    calculate_sii, calculate_nlr, calculate_plr, calculate_siri, 
    calculate_mlr, calculate_piv, get_risk_level, calculate_indices,
    generate_summary
)


class TestIndividualCalculations:
    """Test individual calculation functions."""
    
    def test_calculate_sii_normal_values(self, sample_blood_values):
        """Test SII calculation with normal values."""
        neutrophils = sample_blood_values["neutrophils"] / 1000  # Convert to 10^9/L
        lymphocytes = sample_blood_values["lymphocytes"] / 1000
        platelets = sample_blood_values["platelets"] / 1000
        
        result = calculate_sii(neutrophils, lymphocytes, platelets)
        expected = (neutrophils * platelets) / lymphocytes
        
        assert abs(result - expected) < 0.01
        assert result > 0
    
    def test_calculate_nlr_normal_values(self, sample_blood_values):
        """Test NLR calculation with normal values."""
        neutrophils = sample_blood_values["neutrophils"] / 1000
        lymphocytes = sample_blood_values["lymphocytes"] / 1000
        
        result = calculate_nlr(neutrophils, lymphocytes)
        expected = neutrophils / lymphocytes
        
        assert abs(result - expected) < 0.01
        assert result > 0
    
    def test_calculate_plr_normal_values(self, sample_blood_values):
        """Test PLR calculation with normal values."""
        platelets = sample_blood_values["platelets"] / 1000
        lymphocytes = sample_blood_values["lymphocytes"] / 1000
        
        result = calculate_plr(platelets, lymphocytes)
        expected = platelets / lymphocytes
        
        assert abs(result - expected) < 0.01
        assert result > 0
    
    def test_calculate_siri_normal_values(self, sample_blood_values):
        """Test SIRI calculation with normal values."""
        neutrophils = sample_blood_values["neutrophils"] / 1000
        lymphocytes = sample_blood_values["lymphocytes"] / 1000
        monocytes = sample_blood_values["monocytes"] / 1000
        
        result = calculate_siri(neutrophils, lymphocytes, monocytes)
        expected = (neutrophils * monocytes) / lymphocytes
        
        assert abs(result - expected) < 0.01
        assert result > 0
    
    def test_calculate_mlr_normal_values(self, sample_blood_values):
        """Test MLR calculation with normal values."""
        monocytes = sample_blood_values["monocytes"] / 1000
        lymphocytes = sample_blood_values["lymphocytes"] / 1000
        
        result = calculate_mlr(monocytes, lymphocytes)
        expected = monocytes / lymphocytes
        
        assert abs(result - expected) < 0.01
        assert result > 0
    
    def test_calculate_piv_normal_values(self, sample_blood_values):
        """Test PIV calculation with normal values."""
        neutrophils = sample_blood_values["neutrophils"] / 1000
        lymphocytes = sample_blood_values["lymphocytes"] / 1000
        platelets = sample_blood_values["platelets"] / 1000
        monocytes = sample_blood_values["monocytes"] / 1000
        
        result = calculate_piv(neutrophils, lymphocytes, platelets, monocytes)
        expected = (neutrophils * monocytes * platelets) / lymphocytes
        
        assert abs(result - expected) < 0.01
        assert result > 0


class TestZeroDivisionHandling:
    """Test handling of zero lymphocyte counts."""
    
    def test_sii_zero_lymphocytes_raises_error(self):
        """Test SII calculation with zero lymphocytes raises ValueError."""
        with pytest.raises(ValueError, match="Lymphocyte count cannot be zero"):
            calculate_sii(4.2, 0, 250)
    
    def test_nlr_zero_lymphocytes_raises_error(self):
        """Test NLR calculation with zero lymphocytes raises ValueError."""
        with pytest.raises(ValueError, match="Lymphocyte count cannot be zero"):
            calculate_nlr(4.2, 0)
    
    def test_plr_zero_lymphocytes_raises_error(self):
        """Test PLR calculation with zero lymphocytes raises ValueError."""
        with pytest.raises(ValueError, match="Lymphocyte count cannot be zero"):
            calculate_plr(250, 0)
    
    def test_siri_zero_lymphocytes_raises_error(self):
        """Test SIRI calculation with zero lymphocytes raises ValueError."""
        with pytest.raises(ValueError, match="Lymphocyte count cannot be zero"):
            calculate_siri(4.2, 0, 0.48)
    
    def test_mlr_zero_lymphocytes_raises_error(self):
        """Test MLR calculation with zero lymphocytes raises ValueError."""
        with pytest.raises(ValueError, match="Lymphocyte count cannot be zero"):
            calculate_mlr(0.48, 0)
    
    def test_piv_zero_lymphocytes_raises_error(self):
        """Test PIV calculation with zero lymphocytes raises ValueError."""
        with pytest.raises(ValueError, match="Lymphocyte count cannot be zero"):
            calculate_piv(4.2, 0, 250, 0.48)


class TestRiskLevelDetermination:
    """Test risk level determination logic."""
    
    def test_get_risk_level_normal(self):
        """Test risk level determination for normal values."""
        ranges = {
            "normal": (0, 3),
            "mild": (3, 5),
            "moderate": (5, 10),
            "high": (10, float('inf'))
        }
        
        assert get_risk_level(2.5, ranges) == "normal"
        assert get_risk_level(4.0, ranges) == "mild"
        assert get_risk_level(7.5, ranges) == "moderate"
        assert get_risk_level(15.0, ranges) == "high"  # Within high range
    
    def test_get_risk_level_boundary_values(self):
        """Test risk level determination at boundary values."""
        ranges = {
            "normal": (0, 3),
            "mild": (3, 5),
            "moderate": (5, 10),
            "high": (10, 20)
        }
        
        assert get_risk_level(3.0, ranges) == "mild"  # Exact boundary
        assert get_risk_level(2.999, ranges) == "normal"  # Just below
        assert get_risk_level(5.0, ranges) == "moderate"
        assert get_risk_level(10.0, ranges) == "high"
        assert get_risk_level(25.0, ranges) == "very_high"  # Above all


class TestCalculateIndices:
    """Test the main calculate_indices function."""
    
    def test_calculate_indices_complete_blood_count(self, sample_blood_values):
        """Test calculation with complete blood count."""
        result = calculate_indices(**sample_blood_values)
        
        # Check structure
        assert "results" in result
        assert "summary" in result
        assert "metadata" in result
        
        # Check all indices are calculated
        expected_indices = ["sii", "nlr", "plr", "siri", "mlr", "piv"]
        for index in expected_indices:
            assert index in result["results"]
            assert "value" in result["results"][index]
            assert "risk_level" in result["results"][index]
            assert "interpretation" in result["results"][index]
    
    def test_calculate_indices_no_monocytes(self, sample_blood_values):
        """Test calculation without monocytes."""
        blood_values = sample_blood_values.copy()
        blood_values.pop("monocytes")
        
        result = calculate_indices(**blood_values)
        
        # Check basic indices are calculated
        basic_indices = ["sii", "nlr", "plr"]
        for index in basic_indices:
            assert index in result["results"]
        
        # Check monocyte-dependent indices are not calculated
        monocyte_indices = ["siri", "mlr", "piv"]
        for index in monocyte_indices:
            assert index not in result["results"]
    
    def test_calculate_indices_unit_conversion(self):
        """Test that input values are properly converted from cells/µL to ×10⁹/L."""
        # Test with known values
        neutrophils = 4200  # cells/µL
        lymphocytes = 1800  # cells/µL
        platelets = 250000  # cells/µL
        
        result = calculate_indices(neutrophils, lymphocytes, platelets)
        
        # Calculate expected SII using converted units
        expected_sii = (4.2 * 250) / 1.8  # Using ×10⁹/L units
        actual_sii = result["results"]["sii"]["value"]
        
        assert abs(actual_sii - expected_sii) < 0.1
    
    @patch('immune_inflam_index.validator.validate_inputs')
    def test_calculate_indices_validation_failure(self, mock_validate):
        """Test handling of validation failures."""
        mock_validate.return_value = {
            "valid": False,
            "errors": ["Neutrophil count too low"]
        }
        
        with pytest.raises(ValueError, match="Input validation failed"):
            calculate_indices(100, 1800, 250000, 480)
    
    def test_calculate_indices_zero_lymphocytes(self):
        """Test handling of zero lymphocytes in main function."""
        with pytest.raises(ValueError):
            calculate_indices(4200, 0, 250000, 480)
    
    def test_calculate_indices_metadata(self, sample_blood_values):
        """Test metadata generation."""
        result = calculate_indices(**sample_blood_values)
        
        assert "calculation_date" in result["metadata"]
        assert "input_validation" in result["metadata"]
        assert "warnings" in result["metadata"]
        assert isinstance(result["metadata"]["warnings"], list)


class TestGenerateSummary:
    """Test summary generation logic."""
    
    def test_generate_summary_normal_values(self):
        """Test summary for normal inflammatory values."""
        indices_results = {
            "sii": {"value": 400, "risk_level": "normal"},
            "nlr": {"value": 2.0, "risk_level": "normal"},
            "plr": {"value": 120, "risk_level": "normal"}
        }
        
        summary = generate_summary(indices_results)
        
        assert "Normal inflammatory status" in summary["overall_inflammatory_status"]
        assert len(summary["highest_risk_indices"]) == 0
        assert "healthy lifestyle" in summary["recommendations"][0]
    
    def test_generate_summary_high_inflammation(self):
        """Test summary for high inflammatory values."""
        indices_results = {
            "sii": {"value": 2500, "risk_level": "high"},
            "nlr": {"value": 8.0, "risk_level": "high"},
            "plr": {"value": 350, "risk_level": "moderate"}
        }
        
        summary = generate_summary(indices_results)
        
        assert "High inflammatory burden" in summary["overall_inflammatory_status"]
        assert len(summary["highest_risk_indices"]) == 2
        assert "healthcare provider immediately" in summary["recommendations"][0]
    
    def test_generate_summary_mixed_levels(self):
        """Test summary for mixed risk levels."""
        indices_results = {
            "sii": {"value": 800, "risk_level": "moderate"},
            "nlr": {"value": 4.0, "risk_level": "moderate"},
            "plr": {"value": 150, "risk_level": "mild"}
        }
        
        summary = generate_summary(indices_results)
        
        assert "Moderate inflammatory state" in summary["overall_inflammatory_status"]
        assert "lifestyle modifications" in summary["recommendations"][0]
    
    def test_generate_summary_empty_results(self):
        """Test summary generation with empty results."""
        summary = generate_summary({})
        
        assert "Cannot determine" in summary["overall_inflammatory_status"]
        assert len(summary["highest_risk_indices"]) == 0
        assert "check input values" in summary["recommendations"][0]


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_very_small_values(self):
        """Test calculation with very small but positive values."""
        result = calculate_indices(1500, 800, 120000, 200)  # Low but valid counts
        
        assert "results" in result
        assert all(result["results"][index]["value"] > 0 for index in result["results"])
    
    def test_very_large_values(self):
        """Test calculation with very large values."""
        result = calculate_indices(50000, 10000, 1000000, 5000)  # Very high counts
        
        assert "results" in result
        assert all(result["results"][index]["value"] > 0 for index in result["results"])
    
    def test_extreme_ratios(self):
        """Test calculation with extreme ratios."""
        # Very high neutrophils, very low lymphocytes
        result = calculate_indices(20000, 200, 500000, 1000)
        
        assert result["results"]["nlr"]["risk_level"] in ["high", "very_high"]
        assert result["results"]["sii"]["risk_level"] in ["high", "very_high"]


# Property-based testing with hypothesis
class TestPropertyBasedTesting:
    """Property-based tests using hypothesis."""
    
    @given(
        neutrophils=st.floats(min_value=0.1, max_value=50.0),  # ×10⁹/L units
        lymphocytes=st.floats(min_value=0.1, max_value=20.0),
        platelets=st.floats(min_value=10.0, max_value=1000.0)
    )
    def test_sii_properties(self, neutrophils, lymphocytes, platelets):
        """Test SII calculation properties."""
        result = calculate_sii(neutrophils, lymphocytes, platelets)
        
        # SII should always be positive
        assert result > 0
        
        # SII should increase if neutrophils increase (lymphocytes, platelets constant)
        result_higher_neutrophils = calculate_sii(neutrophils * 2, lymphocytes, platelets)
        assert result_higher_neutrophils > result
        
        # SII should decrease if lymphocytes increase (neutrophils, platelets constant)
        result_higher_lymphocytes = calculate_sii(neutrophils, lymphocytes * 2, platelets)
        assert result_higher_lymphocytes < result
    
    @given(
        neutrophils=st.floats(min_value=0.1, max_value=50.0),
        lymphocytes=st.floats(min_value=0.1, max_value=20.0)
    )
    def test_nlr_properties(self, neutrophils, lymphocytes):
        """Test NLR calculation properties."""
        result = calculate_nlr(neutrophils, lymphocytes)
        
        # NLR should always be positive
        assert result > 0
        
        # NLR should equal 1 when neutrophils equal lymphocytes
        if abs(neutrophils - lymphocytes) < 0.01:
            assert abs(result - 1.0) < 0.1
    
    @given(
        platelets=st.floats(min_value=10.0, max_value=1000.0),
        lymphocytes=st.floats(min_value=0.1, max_value=20.0)
    )
    def test_plr_properties(self, platelets, lymphocytes):
        """Test PLR calculation properties."""
        result = calculate_plr(platelets, lymphocytes)
        
        # PLR should always be positive
        assert result > 0
        
        # PLR should be monotonic with respect to inputs
        result_double_platelets = calculate_plr(platelets * 2, lymphocytes)
        assert result_double_platelets > result


class TestRegressionTests:
    """Regression tests for known calculation scenarios."""
    
    def test_known_calculation_scenario_1(self):
        """Test specific scenario from medical literature."""
        # Based on published example: neutrophils=6000, lymphocytes=2000, platelets=300000
        result = calculate_indices(6000, 2000, 300000, 600)
        
        # Expected calculations (converted to ×10⁹/L):
        # SII = (6 × 300) / 2 = 900
        # NLR = 6 / 2 = 3.0
        # PLR = 300 / 2 = 150
        
        assert abs(result["results"]["sii"]["value"] - 900.0) < 1.0
        assert abs(result["results"]["nlr"]["value"] - 3.0) < 0.1
        assert abs(result["results"]["plr"]["value"] - 150.0) < 1.0
    
    def test_high_inflammation_scenario(self, sample_blood_values_high_inflammation):
        """Test high inflammation scenario calculation."""
        result = calculate_indices(**sample_blood_values_high_inflammation)
        
        # Should indicate high inflammatory burden
        high_risk_indices = [
            index for index, data in result["results"].items()
            if data["risk_level"] in ["high", "very_high"]
        ]
        
        assert len(high_risk_indices) >= 2  # Multiple indices should be elevated
        # Should indicate elevated inflammatory state (could be "High" or "Critical")
        assert any(word in result["summary"]["overall_inflammatory_status"] for word in ["High", "Critical", "elevated"])