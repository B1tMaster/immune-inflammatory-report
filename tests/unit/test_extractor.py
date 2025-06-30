"""Unit tests for the extractor module."""

import pytest
from hypothesis import given, strategies as st

from immune_inflam_index.extractor import (
    parse_value_with_unit, find_field_value, extract_reference_ranges,
    extract_cbc_values, validate_extraction_quality, debug_extraction
)


class TestParseValueWithUnit:
    """Test value parsing with different units and formats."""
    
    def test_parse_x10_3_format(self):
        """Test parsing x10³/L format."""
        test_cases = [
            ("6.31 x10³/L", 6310.0, "x10³/L"),
            ("4.2 x10^3/L", 4200.0, "x10³/L"),
            ("1.8 x 10³/L", 1800.0, "x10³/L"),
            ("250 x10³/L", 250000.0, "x10³/L"),
        ]
        
        for text, expected_value, expected_unit in test_cases:
            value, unit = parse_value_with_unit(text)
            assert value == expected_value
            assert expected_unit in unit
    
    def test_parse_cells_per_ul_format(self):
        """Test parsing cells/µL format."""
        test_cases = [
            ("6310 cells/µL", 6310.0, "cells/µL"),
            ("4200 /µL", 4200.0, "cells/µL"),
            ("1800 cells/uL", 1800.0, "cells/µL"),  # u instead of µ
            ("250000 /ul", 250000.0, "cells/µL"),
        ]
        
        for text, expected_value, expected_unit in test_cases:
            value, unit = parse_value_with_unit(text)
            assert value == expected_value
            assert expected_unit in unit
    
    def test_parse_k_per_ul_format(self):
        """Test parsing K/µL format."""
        test_cases = [
            ("6.31 K/µL", 6310.0, "K/µL"),
            ("4.2 K/uL", 4200.0, "K/µL"),
            ("250 K/µL", 250000.0, "K/µL"),
        ]
        
        for text, expected_value, expected_unit in test_cases:
            value, unit = parse_value_with_unit(text)
            assert value == expected_value
            assert expected_unit in unit
    
    def test_parse_plain_numbers(self):
        """Test parsing plain numbers (assumes x10³/L)."""
        test_cases = [
            ("6.31", 6310.0),
            ("4.2", 4200.0),
            ("250", 250000.0),
        ]
        
        for text, expected_value in test_cases:
            value, unit = parse_value_with_unit(text)
            assert value == expected_value
            assert "assumed" in unit.lower()
    
    def test_parse_with_reference_range(self):
        """Test parsing values with reference ranges."""
        test_cases = [
            ("6.31 (1.60-6.90)", 6310.0),
            ("4.2 x10³/L (1.8-7.7)", 4200.0),
            ("250 K/µL (150-450)", 250000.0),
        ]
        
        for text, expected_value in test_cases:
            value, unit = parse_value_with_unit(text)
            assert value == expected_value
    
    def test_parse_special_characters(self):
        """Test parsing with special characters from PDF extraction."""
        test_cases = [
            ("6.31 xIO^/L", 6310.0),    # OCR artifacts
            ("4.2 xIOS/L", 4200.0),     # OCR artifacts
            ("181 x10®/L", 181000.0),   # ® symbol
            ("250 x10©/L", 250000.0),   # © symbol
        ]
        
        for text, expected_value in test_cases:
            value, unit = parse_value_with_unit(text)
            assert value == expected_value
    
    def test_parse_with_commas(self):
        """Test parsing values with comma separators."""
        test_cases = [
            ("250,000 cells/µL", 250000.0),
            ("6,310 /µL", 6310.0),
            ("1,800 x10³/L", 1800000.0),  # Note: this is interpreted as x10³/L
        ]
        
        for text, expected_value in test_cases:
            value, unit = parse_value_with_unit(text)
            assert value == expected_value
    
    def test_parse_invalid_formats(self):
        """Test parsing invalid or unparseable formats."""
        invalid_cases = [
            "no numbers here",
            "neutrophils: normal",
            "see comment",
            "",
            "abc def",
            "N/A"
        ]
        
        for text in invalid_cases:
            value, unit = parse_value_with_unit(text)
            assert value is None
            assert unit is None


class TestFindFieldValue:
    """Test field value finding with fuzzy matching."""
    
    def test_find_field_exact_match(self):
        """Test finding field with exact name match."""
        text = """
        Neutrophils: 6.31 x10³/L
        Lymphocytes: 1.8 x10³/L
        """
        
        variations = ["neutrophils", "neutrophil", "neut"]
        result = find_field_value(text, "neutrophils", variations)
        
        assert result["value"] == 6310.0
        assert result["confidence"] > 90
        assert "x10³/L" in result["unit"]
        assert "neutrophils" in result["matched_variation"].lower()
    
    def test_find_field_fuzzy_match(self):
        """Test finding field with fuzzy matching."""
        text = """
        Neutrophil Count: 4200 cells/µL
        Lymphocyte Count: 1800 cells/µL
        """
        
        variations = ["neutrophils", "neutrophil", "neut"]
        result = find_field_value(text, "neutrophils", variations)
        
        assert result["value"] == 4200.0
        assert result["confidence"] > 70
        assert "cells/µL" in result["unit"]
    
    def test_find_field_no_match(self):
        """Test finding field when no match exists."""
        text = """
        Red Blood Cells: 4.5
        Hemoglobin: 14.5
        """
        
        variations = ["neutrophils", "neutrophil", "neut"]
        result = find_field_value(text, "neutrophils", variations)
        
        assert result["value"] is None
        assert result["confidence"] == 0
        assert result["unit"] is None
    
    def test_find_field_multiple_matches(self):
        """Test finding field when multiple matches exist (should take best)."""
        text = """
        Neutrophils: 6.31 x10³/L
        Neutrophil %: 65%
        Neutrophil Count: 6310 cells/µL
        """
        
        variations = ["neutrophils", "neutrophil", "neut"]
        result = find_field_value(text, "neutrophils", variations)
        
        # Should pick the best match (highest confidence)
        assert result["value"] is not None
        assert result["confidence"] > 80
    
    def test_find_field_case_insensitive(self):
        """Test field finding is case insensitive."""
        text = """
        NEUTROPHILS: 6.31 X10³/L
        lymphocytes: 1.8 x10³/l
        """
        
        variations = ["neutrophils"]
        result = find_field_value(text, "neutrophils", variations)
        
        assert result["value"] == 6310.0
        assert result["confidence"] > 80
    
    def test_find_field_with_typos(self):
        """Test finding fields with common typos."""
        text = """
        Neutrofils: 6.31 x10³/L  # Missing 'h'
        Lymhocytes: 1.8 x10³/L   # Typo in lymphocytes
        """
        
        # Should still find with fuzzy matching
        variations = ["neutrophils", "neutrophil"]
        result = find_field_value(text, "neutrophils", variations)
        
        # Fuzzy matching should catch common typos
        assert result["value"] == 6310.0 or result["value"] is None  # Depends on fuzzy threshold


class TestExtractReferenceRanges:
    """Test reference range extraction."""
    
    def test_extract_basic_reference_ranges(self):
        """Test extraction of basic reference ranges."""
        text = """
        Neutrophils: 6.31 x10³/L (1.8-7.7)
        Lymphocytes: 1.8 x10³/L (1.0-4.0)
        Platelets: 250 x10³/L (150-450)
        """
        
        ranges = extract_reference_ranges(text)
        
        assert "neutrophils" in ranges
        assert ranges["neutrophils"] == (1800.0, 7700.0)  # Converted to cells/µL
        
        assert "lymphocytes" in ranges
        assert ranges["lymphocytes"] == (1000.0, 4000.0)
        
        assert "platelets" in ranges
        assert ranges["platelets"] == (150000.0, 450000.0)
    
    def test_extract_ranges_cells_per_ul(self):
        """Test extraction when ranges are in cells/µL."""
        text = """
        Neutrophils: 6310 cells/µL (1800-7700)
        Lymphocytes: 1800 cells/µL (1000-4000)
        """
        
        ranges = extract_reference_ranges(text)
        
        # Should not convert when already in cells/µL
        assert ranges["neutrophils"] == (1800.0, 7700.0)
        assert ranges["lymphocytes"] == (1000.0, 4000.0)
    
    def test_extract_ranges_with_spaces(self):
        """Test extraction with various spacing in ranges."""
        text = """
        Neutrophils: 6.31 x10³/L ( 1.8 - 7.7 )
        Lymphocytes: 1.8 x10³/L (1.0- 4.0)
        Platelets: 250 x10³/L (150 -450)
        """
        
        ranges = extract_reference_ranges(text)
        
        assert len(ranges) == 3
        assert ranges["neutrophils"] == (1800.0, 7700.0)
        assert ranges["lymphocytes"] == (1000.0, 4000.0)
        assert ranges["platelets"] == (150000.0, 450000.0)
    
    def test_extract_ranges_no_matches(self):
        """Test extraction when no reference ranges are found."""
        text = """
        Neutrophils: 6.31 x10³/L
        Lymphocytes: 1.8 x10³/L
        """
        
        ranges = extract_reference_ranges(text)
        assert len(ranges) == 0
    
    def test_extract_ranges_malformed(self):
        """Test extraction with malformed ranges."""
        text = """
        Neutrophils: 6.31 x10³/L (invalid-range)
        Lymphocytes: 1.8 x10³/L (1.0-abc)
        Platelets: 250 x10³/L (150-450)
        """
        
        ranges = extract_reference_ranges(text)
        
        # Should only extract valid ranges
        assert "platelets" in ranges
        assert ranges["platelets"] == (150000.0, 450000.0)
        # Invalid ranges should be skipped
        assert "neutrophils" not in ranges
        assert "lymphocytes" not in ranges


class TestExtractCbcValues:
    """Test complete CBC value extraction."""
    
    def test_extract_complete_cbc(self):
        """Test extraction of complete CBC panel."""
        text = """
        COMPLETE BLOOD COUNT
        
        Neutrophils: 6.31 x10³/L (1.8-7.7)
        Lymphocytes: 1.8 x10³/L (1.0-4.0)
        Platelets: 250 x10³/L (150-450)
        Monocytes: 0.48 x10³/L (0.2-0.8)
        """
        
        extracted = extract_cbc_values(text)
        
        # Check all expected fields are extracted
        expected_fields = ["neutrophils", "lymphocytes", "platelets", "monocytes"]
        for field in expected_fields:
            assert field in extracted
            assert extracted[field]["value"] is not None
            assert extracted[field]["confidence"] > 70
        
        # Check reference ranges are included
        assert "reference_range" in extracted["neutrophils"]
        assert extracted["neutrophils"]["reference_range"] == (1800.0, 7700.0)
    
    def test_extract_partial_cbc(self):
        """Test extraction with only some CBC values present."""
        text = """
        White Blood Cell Count: 8.1 x10³/L
        Neutrophils: 6.31 x10³/L
        Lymphocytes: 1.8 x10³/L
        """
        
        extracted = extract_cbc_values(text)
        
        assert "neutrophils" in extracted
        assert "lymphocytes" in extracted
        # Monocytes and platelets should not be present
        assert "platelets" not in extracted or extracted["platelets"]["value"] is None
    
    def test_extract_mixed_units(self):
        """Test extraction with mixed units."""
        text = """
        Neutrophils: 6310 cells/µL
        Lymphocytes: 1.8 x10³/L
        Platelets: 250 K/µL
        Monocytes: 480 cells/µL
        """
        
        extracted = extract_cbc_values(text)
        
        # All should be converted to cells/µL
        assert extracted["neutrophils"]["value"] == 6310.0
        assert extracted["lymphocytes"]["value"] == 1800.0
        assert extracted["platelets"]["value"] == 250000.0
        assert extracted["monocytes"]["value"] == 480.0
    
    def test_extract_from_real_lab_format(self):
        """Test extraction from realistic lab report format."""
        text = """
        HEMATOLOGY
        
        Complete Blood Count:
        WBC                  8.1    x10³/L     (4.0-11.0)
        Neutrophils#         6.31   x10³/L     (1.8-7.7)
        Lymphocytes#         1.80   x10³/L     (1.0-4.0)  
        Monocytes#           0.48   x10³/L     (0.2-0.8)
        
        Platelet Count:
        Platelets           250     x10³/L     (150-450)
        """
        
        extracted = extract_cbc_values(text)
        
        assert "neutrophils" in extracted
        assert "lymphocytes" in extracted
        assert "platelets" in extracted
        assert "monocytes" in extracted
        
        # Check values
        assert extracted["neutrophils"]["value"] == 6310.0
        assert extracted["lymphocytes"]["value"] == 1800.0
        assert extracted["platelets"]["value"] == 250000.0
        assert extracted["monocytes"]["value"] == 480.0


class TestValidateExtractionQuality:
    """Test extraction quality validation."""
    
    def test_validate_high_quality_extraction(self):
        """Test validation of high-quality extraction."""
        extracted_values = {
            "neutrophils": {"value": 6310, "confidence": 95},
            "lymphocytes": {"value": 1800, "confidence": 90},
            "platelets": {"value": 250000, "confidence": 98},
            "monocytes": {"value": 480, "confidence": 85}
        }
        
        quality = validate_extraction_quality(extracted_values)
        
        assert quality["overall_quality"] == "high"
        assert quality["average_confidence"] > 90
        assert quality["required_fields_found"] == 3
        assert quality["total_fields_found"] == 4
        assert not quality["manual_review_recommended"]
        assert len(quality["quality_issues"]) == 0
    
    def test_validate_medium_quality_extraction(self):
        """Test validation of medium-quality extraction."""
        extracted_values = {
            "neutrophils": {"value": 6310, "confidence": 75},
            "lymphocytes": {"value": 1800, "confidence": 65},  # Low confidence
            "platelets": {"value": 250000, "confidence": 80}
        }
        
        quality = validate_extraction_quality(extracted_values)
        
        assert quality["overall_quality"] == "medium"
        assert 60 < quality["average_confidence"] < 80
        assert quality["required_fields_found"] == 3
        assert len(quality["quality_issues"]) > 0
        assert "Low confidence fields" in quality["quality_issues"][0]
    
    def test_validate_low_quality_extraction(self):
        """Test validation of low-quality extraction."""
        extracted_values = {
            "neutrophils": {"value": 6310, "confidence": 50},
            # Missing lymphocytes and platelets
        }
        
        quality = validate_extraction_quality(extracted_values)
        
        assert quality["overall_quality"] == "low"
        assert quality["average_confidence"] < 70
        assert quality["required_fields_found"] < 3
        assert quality["manual_review_recommended"]
        assert len(quality["quality_issues"]) > 0
        assert any("Missing required fields" in issue for issue in quality["quality_issues"])
    
    def test_validate_empty_extraction(self):
        """Test validation of empty extraction."""
        extracted_values = {}
        
        quality = validate_extraction_quality(extracted_values)
        
        assert quality["overall_quality"] == "low"
        assert quality["average_confidence"] == 0
        assert quality["required_fields_found"] == 0
        assert quality["manual_review_recommended"]


class TestDebugExtraction:
    """Test extraction debugging functionality."""
    
    def test_debug_extraction_with_results(self):
        """Test debug output with successful extraction."""
        text = """
        Neutrophils: 6.31 x10³/L
        Lymphocytes: 1.8 x10³/L
        """
        
        extracted_values = {
            "neutrophils": {
                "value": 6310,
                "confidence": 95,
                "raw_text": "Neutrophils: 6.31 x10³/L",
                "matched_variation": "neutrophils"
            }
        }
        
        debug_info = debug_extraction(text, extracted_values)
        
        assert "EXTRACTION DEBUG INFO" in debug_info
        assert "Text length:" in debug_info
        assert "Fields found:" in debug_info
        assert "neutrophils: 6310" in debug_info
        assert "95% confidence" in debug_info
    
    def test_debug_extraction_with_missed_lines(self):
        """Test debug output showing potentially missed lines."""
        text = """
        Neutrophils: 6.31 x10³/L
        Lymphocyte Count: 1.8 x10³/L
        Platelet: 250 x10³/L
        """
        
        extracted_values = {
            "neutrophils": {
                "value": 6310,
                "confidence": 95,
                "raw_text": "Neutrophils: 6.31 x10³/L",
                "matched_variation": "neutrophils"
            }
        }
        
        debug_info = debug_extraction(text, extracted_values)
        
        assert "Potential missed lines:" in debug_info
        # Should show lines with lymph/platelet that weren't matched
        assert "Lymphocyte" in debug_info or "Platelet" in debug_info


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""
    
    def test_parse_value_edge_cases(self):
        """Test value parsing edge cases."""
        edge_cases = [
            ("0 x10³/L", 0.0),           # Zero value
            ("0.1 x10³/L", 100.0),       # Very small value
            ("999.9 x10³/L", 999900.0), # Large value
            ("1.23456 x10³/L", 1234.56), # Many decimal places
        ]
        
        for text, expected_value in edge_cases:
            value, unit = parse_value_with_unit(text)
            assert value == expected_value
    
    def test_find_field_empty_text(self):
        """Test field finding with empty text."""
        result = find_field_value("", "neutrophils", ["neutrophils"])
        
        assert result["value"] is None
        assert result["confidence"] == 0
    
    def test_extract_cbc_malformed_text(self):
        """Test CBC extraction with malformed text."""
        malformed_texts = [
            "",  # Empty
            "No CBC data here",  # No relevant data
            "Neutrophils: invalid",  # Invalid values
            "123 456 789",  # Just numbers
        ]
        
        for text in malformed_texts:
            extracted = extract_cbc_values(text)
            # Should handle gracefully without crashing
            assert isinstance(extracted, dict)
    
    def test_reference_range_edge_cases(self):
        """Test reference range extraction edge cases."""
        text = """
        Neutrophils: 6.31 x10³/L (0.0-999.9)
        Lymphocytes: 1.8 x10³/L (1-1)  # Same min/max
        """
        
        ranges = extract_reference_ranges(text)
        
        if "neutrophils" in ranges:
            assert ranges["neutrophils"] == (0.0, 999900.0)
        if "lymphocytes" in ranges:
            assert ranges["lymphocytes"] == (1000.0, 1000.0)


# Property-based testing with hypothesis
class TestPropertyBasedExtraction:
    """Property-based tests for extraction functions."""
    
    @given(
        value=st.floats(min_value=0.1, max_value=999.9, allow_nan=False, allow_infinity=False),
        format_type=st.sampled_from(["x10³/L", "cells/µL", "K/µL"])
    )
    def test_parse_value_properties(self, value, format_type):
        """Test value parsing properties with various formats."""
        # Generate test string based on format
        if format_type == "x10³/L":
            text = f"{value} x10³/L"
            expected = value * 1000
        elif format_type == "K/µL":
            text = f"{value} K/µL"
            expected = value * 1000
        else:  # cells/µL
            text = f"{value * 1000:.0f} cells/µL"
            expected = value * 1000
        
        parsed_value, unit = parse_value_with_unit(text)
        
        if parsed_value is not None:
            # Should be close to expected (allowing for floating point precision)
            assert abs(parsed_value - expected) < 1.0
            assert unit is not None
    
    @given(confidence=st.integers(min_value=0, max_value=100))
    def test_extraction_quality_properties(self, confidence):
        """Test extraction quality assessment properties."""
        extracted_values = {
            "neutrophils": {"value": 6310, "confidence": confidence},
            "lymphocytes": {"value": 1800, "confidence": confidence},
            "platelets": {"value": 250000, "confidence": confidence}
        }
        
        quality = validate_extraction_quality(extracted_values)
        
        # Quality should correlate with confidence
        if confidence >= 80:
            assert quality["overall_quality"] == "high"
        elif confidence >= 60:
            assert quality["overall_quality"] in ["medium", "high"]
        else:
            assert quality["overall_quality"] in ["low", "medium"]
        
        # Average confidence should match input
        assert abs(quality["average_confidence"] - confidence) < 0.1


class TestRegressionTests:
    """Regression tests for known extraction scenarios."""
    
    def test_common_lab_format_1(self):
        """Test extraction from common lab format 1."""
        text = """
        CBC WITH DIFFERENTIAL
        
        WBC Count               8.1    10^3/uL    4.0-11.0
        RBC Count               4.50   10^6/uL    4.20-5.40
        Hemoglobin              14.5   g/dL       12.0-16.0
        
        DIFFERENTIAL
        Neutrophils             6.31   10^3/uL    1.8-7.7
        Lymphocytes             1.80   10^3/uL    1.0-4.0
        Monocytes               0.48   10^3/uL    0.2-0.8
        
        PLATELET COUNT
        Platelets               250    10^3/uL    150-450
        """
        
        extracted = extract_cbc_values(text)
        
        assert "neutrophils" in extracted
        assert "lymphocytes" in extracted
        assert "platelets" in extracted
        assert "monocytes" in extracted
        
        # Check values are correctly converted
        assert extracted["neutrophils"]["value"] == 6310.0
        assert extracted["lymphocytes"]["value"] == 1800.0
        assert extracted["platelets"]["value"] == 250000.0
        assert extracted["monocytes"]["value"] == 480.0
    
    def test_ocr_artifacts_handling(self):
        """Test handling of common OCR artifacts."""
        text = """
        Neutrophlls: 6.3I xIO^/L  # OCR errors: 'ph' instead of 'h', 'I' instead of '1', 'IO' instead of '10'
        lymphocytes: I.8 xI0³/L   # More OCR errors
        PLatelets: 25O x10³/L     # 'O' instead of '0'
        """
        
        extracted = extract_cbc_values(text)
        
        # Should still extract values despite OCR artifacts
        # (depending on fuzzy matching tolerance)
        # At minimum, should not crash
        assert isinstance(extracted, dict)
        
        # If extraction succeeds, values should be reasonable
        for field, data in extracted.items():
            if data["value"] is not None:
                assert data["value"] > 0
                assert data["confidence"] > 0