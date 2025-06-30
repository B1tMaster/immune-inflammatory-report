"""Unit tests for the demographic_extractor module."""

import pytest
from datetime import datetime
from typing import Dict, Any
from hypothesis import given, strategies as st

from immune_inflam_index.demographic_extractor import (
    extract_patient_age, extract_patient_sex, extract_test_date,
    extract_patient_demographics, validate_demographic_extraction,
    debug_demographic_extraction
)


class TestExtractPatientAge:
    """Test patient age extraction."""
    
    def test_extract_age_years_format(self):
        """Test extraction from 'Years' format."""
        test_cases = [
            ("Patient: 58 Years Male", 58, 95),
            ("32 years female", 32, 95),
            ("45 Years Male", 45, 95),
            ("67 YEARS FEMALE", 67, 95),
        ]
        
        for text, expected_age, min_confidence in test_cases:
            result = extract_patient_age(text)
            assert result["value"] == expected_age
            assert result["confidence"] >= min_confidence
            assert "year" in result["raw_text"].lower()
    
    def test_extract_age_explicit_format(self):
        """Test extraction from explicit 'Age:' format."""
        test_cases = [
            ("Age: 58", 58, 90),
            ("AGE 45", 45, 90),
            ("Patient Age: 72", 72, 90),
            ("Age:32", 32, 90),
        ]
        
        for text, expected_age, min_confidence in test_cases:
            result = extract_patient_age(text)
            assert result["value"] == expected_age
            assert result["confidence"] >= min_confidence
    
    def test_extract_age_yo_format(self):
        """Test extraction from 'y.o.' format."""
        test_cases = [
            ("45 yo Male", 45, 85),
            ("32 y.o. female", 32, 85),
            ("58 YO", 58, 85),
            ("67 Y.O.", 67, 85),
        ]
        
        for text, expected_age, min_confidence in test_cases:
            result = extract_patient_age(text)
            assert result["value"] == expected_age
            assert result["confidence"] >= min_confidence
    
    def test_extract_age_with_gender_letter(self):
        """Test extraction from format with single gender letter."""
        test_cases = [
            ("58 M", 58, 80),
            ("45 F", 45, 80),
            ("Patient: 72 M", 72, 80),
            ("32 F DOB", 32, 80),
        ]
        
        for text, expected_age, min_confidence in test_cases:
            result = extract_patient_age(text)
            assert result["value"] == expected_age
            assert result["confidence"] >= min_confidence
    
    def test_extract_age_invalid_ranges(self):
        """Test rejection of invalid age ranges."""
        invalid_cases = [
            "5 Years Male",    # Too young
            "150 Years Male",  # Too old
            "0 yo",           # Zero age
        ]
        
        for text in invalid_cases:
            result = extract_patient_age(text)
            assert result["value"] is None
            assert result["confidence"] == 0
    
    def test_extract_age_no_match(self):
        """Test cases where no age can be extracted."""
        no_match_cases = [
            "No age information",
            "Patient ID: 12345",
            "Blood test results",
            "",
            "Male Female",
        ]
        
        for text in no_match_cases:
            result = extract_patient_age(text)
            assert result["value"] is None
            assert result["confidence"] == 0
    
    def test_extract_age_multiple_matches(self):
        """Test extraction when multiple age patterns exist."""
        text = "Patient: 58 Years Male, Emergency contact age: 82"
        result = extract_patient_age(text)
        
        # Should pick the highest confidence match
        assert result["value"] == 58  # Should prioritize the patient age
        assert result["confidence"] >= 90
    
    def test_extract_age_boundary_values(self):
        """Test age extraction at boundary values."""
        boundary_cases = [
            ("18 Years Male", 18),  # Minimum valid age
            ("120 Years Female", 120),  # Maximum valid age
        ]
        
        for text, expected_age in boundary_cases:
            result = extract_patient_age(text)
            assert result["value"] == expected_age
            assert result["confidence"] > 0


class TestExtractPatientSex:
    """Test patient sex extraction."""
    
    def test_extract_sex_full_word_format(self):
        """Test extraction from full word format."""
        test_cases = [
            ("58 Years Male", "M", 95),
            ("32 years female", "F", 95),
            ("Patient: MALE", "M", 90),
            ("Gender: Female", "F", 90),
        ]
        
        for text, expected_sex, min_confidence in test_cases:
            result = extract_patient_sex(text)
            assert result["value"] == expected_sex
            assert result["confidence"] >= min_confidence
    
    def test_extract_sex_single_letter_format(self):
        """Test extraction from single letter format."""
        test_cases = [
            ("58 M", "M", 80),
            ("45 F", "F", 80),
            ("Sex: M", "M", 85),
            ("Gender: F", "F", 85),
        ]
        
        for text, expected_sex, min_confidence in test_cases:
            result = extract_patient_sex(text)
            assert result["value"] == expected_sex
            assert result["confidence"] >= min_confidence
    
    def test_extract_sex_case_insensitive(self):
        """Test case insensitive sex extraction."""
        test_cases = [
            ("male", "M"),
            ("FEMALE", "F"),
            ("Male", "M"),
            ("Female", "F"),
            ("m", "M"),
            ("F", "F"),
        ]
        
        for text, expected_sex in test_cases:
            result = extract_patient_sex(text)
            assert result["value"] == expected_sex
    
    def test_extract_sex_with_context(self):
        """Test sex extraction with contextual information."""
        test_cases = [
            ("M 58 years old", "M", 80),
            ("F Age: 45", "F", 80),
            ("Patient M, 32 yo", "M", 80),
        ]
        
        for text, expected_sex, min_confidence in test_cases:
            result = extract_patient_sex(text)
            assert result["value"] == expected_sex
            assert result["confidence"] >= min_confidence
    
    def test_extract_sex_no_match(self):
        """Test cases where no sex can be extracted."""
        no_match_cases = [
            "No gender information",
            "Patient ID: 12345",
            "Blood test results",
            "",
            "Age: 45",
        ]
        
        for text in no_match_cases:
            result = extract_patient_sex(text)
            assert result["value"] is None
            assert result["confidence"] == 0
    
    def test_extract_sex_multiple_matches(self):
        """Test extraction when multiple sex patterns exist."""
        text = "Patient: Male, Emergency contact: Female"
        result = extract_patient_sex(text)
        
        # Should pick the highest confidence match
        assert result["value"] == "M"
        assert result["confidence"] >= 85


class TestExtractTestDate:
    """Test test date extraction."""
    
    def test_extract_date_collected_format(self):
        """Test extraction from 'Collected:' format."""
        test_cases = [
            ("Collected: 03/15/2025", "2025-03-15", 95),
            ("COLLECTED 12/01/24", "2024-12-01", 95),
            ("Collected:06/30/2025", "2025-06-30", 95),
        ]
        
        for text, expected_date, min_confidence in test_cases:
            result = extract_test_date(text)
            assert result["value"] == expected_date
            assert result["confidence"] >= min_confidence
    
    def test_extract_date_reported_format(self):
        """Test extraction from 'Reported:' format."""
        test_cases = [
            ("Reported: 03/15/2025", "2025-03-15", 90),
            ("REPORTED 12/01/24", "2024-12-01", 90),
            ("Reported:06/30/2025", "2025-06-30", 90),
        ]
        
        for text, expected_date, min_confidence in test_cases:
            result = extract_test_date(text)
            assert result["value"] == expected_date
            assert result["confidence"] >= min_confidence
    
    def test_extract_date_iso_format(self):
        """Test extraction from ISO date format."""
        test_cases = [
            ("Date: 2025-03-15", "2025-03-15", 90),
            ("2025-06-30", "2025-06-30", 75),
            ("Test Date: 2024-12-01", "2024-12-01", 90),
        ]
        
        for text, expected_date, min_confidence in test_cases:
            result = extract_test_date(text)
            assert result["value"] == expected_date
            assert result["confidence"] >= min_confidence
    
    def test_extract_date_two_digit_year(self):
        """Test extraction with two-digit years."""
        current_year = datetime.now().year
        
        test_cases = [
            ("Collected: 03/15/25", "2025-03-15"),  # Future year < 50 -> 20xx
            ("Collected: 03/15/75", "1975-03-15"),  # Year >= 50 -> 19xx
            ("12/01/24", "2024-12-01"),
        ]
        
        for text, expected_date in test_cases:
            result = extract_test_date(text)
            if result["value"]:  # Only check if extraction succeeded
                assert result["value"] == expected_date
    
    def test_extract_date_invalid_dates(self):
        """Test rejection of invalid dates."""
        current_year = datetime.now().year
        invalid_cases = [
            f"Collected: 13/35/{current_year}",  # Invalid month/day
            f"Collected: 02/30/{current_year}",  # Invalid day for February
            "Collected: 99/99/99",              # Invalid date
            "Date: 2030-12-01",                 # Too far in future
            "Date: 2010-12-01",                 # Too far in past
        ]
        
        for text in invalid_cases:
            result = extract_test_date(text)
            # Should either fail to extract or have low confidence
            assert result["value"] is None or result["confidence"] < 70
    
    def test_extract_date_no_match(self):
        """Test cases where no date can be extracted."""
        no_match_cases = [
            "No date information",
            "Patient: 58 Years Male",
            "Blood test results",
            "",
            "Invalid date format",
        ]
        
        for text in no_match_cases:
            result = extract_test_date(text)
            assert result["value"] is None
            assert result["confidence"] == 0
    
    def test_extract_date_multiple_dates(self):
        """Test extraction when multiple dates exist."""
        text = "Collected: 03/15/2025, Reported: 03/16/2025"
        result = extract_test_date(text)
        
        # Should pick the highest confidence match (Collected)
        assert result["value"] == "2025-03-15"
        assert result["confidence"] >= 90


class TestExtractPatientDemographics:
    """Test complete demographic extraction."""
    
    def test_extract_complete_demographics(self):
        """Test extraction of complete demographic information."""
        text = """
        Patient Information:
        Name: John Doe
        Age: 58 Years Male
        Collected: 03/15/2025
        """
        
        demographics = extract_patient_demographics(text)
        
        assert "age" in demographics
        assert "sex" in demographics
        assert "test_date" in demographics
        
        assert demographics["age"]["value"] == 58
        assert demographics["sex"]["value"] == "M"
        assert demographics["test_date"]["value"] == "2025-03-15"
    
    def test_extract_partial_demographics(self):
        """Test extraction with only some demographic info available."""
        text = """
        Patient: 45 F
        Lab results follow...
        """
        
        demographics = extract_patient_demographics(text)
        
        assert demographics["age"]["value"] == 45
        assert demographics["sex"]["value"] == "F"
        assert demographics["test_date"]["value"] is None
    
    def test_extract_no_demographics(self):
        """Test extraction when no demographic info is available."""
        text = "Just some random text with no patient information"
        
        demographics = extract_patient_demographics(text)
        
        assert demographics["age"]["value"] is None
        assert demographics["sex"]["value"] is None
        assert demographics["test_date"]["value"] is None
    
    def test_extract_demographics_structure(self):
        """Test the structure of extracted demographics."""
        text = "Age: 45, Male, Collected: 03/15/2025"
        
        demographics = extract_patient_demographics(text)
        
        for field in ["age", "sex", "test_date"]:
            assert field in demographics
            assert "value" in demographics[field]
            assert "confidence" in demographics[field]
            assert "raw_text" in demographics[field]
            assert "pattern_used" in demographics[field]


class TestValidateDemographicExtraction:
    """Test demographic extraction validation."""
    
    def test_validate_high_confidence_extraction(self):
        """Test validation of high-confidence extraction."""
        demographics = {
            "age": {"value": 58, "confidence": 95},
            "sex": {"value": "M", "confidence": 90},
            "test_date": {"value": "2025-03-15", "confidence": 90}
        }
        
        result = validate_demographic_extraction(demographics)
        
        assert result["valid"] is True
        assert len(result["warnings"]) == 0
        assert result["manual_verification_needed"] is False
    
    def test_validate_low_confidence_extraction(self):
        """Test validation of low-confidence extraction."""
        demographics = {
            "age": {"value": 58, "confidence": 60},      # Low confidence
            "sex": {"value": "M", "confidence": 65},     # Low confidence
            "test_date": {"value": "2025-03-15", "confidence": 60}  # Low confidence
        }
        
        result = validate_demographic_extraction(demographics)
        
        assert result["valid"] is True  # Still valid, just warnings
        assert len(result["warnings"]) >= 2  # Age and sex warnings
        assert result["manual_verification_needed"] is True
        assert any("age" in warning.lower() for warning in result["warnings"])
        assert any("sex" in warning.lower() for warning in result["warnings"])
    
    def test_validate_missing_demographics(self):
        """Test validation when demographics are missing."""
        demographics = {
            "age": {"value": None, "confidence": 0},
            "sex": {"value": None, "confidence": 0},
            "test_date": {"value": "2025-03-15", "confidence": 85}
        }
        
        result = validate_demographic_extraction(demographics)
        
        assert result["valid"] is True  # Valid but with warnings
        assert len(result["warnings"]) >= 2
        assert any("age not found" in warning for warning in result["warnings"])
        assert any("sex not found" in warning for warning in result["warnings"])
    
    def test_validate_mixed_quality_extraction(self):
        """Test validation with mixed quality extraction."""
        demographics = {
            "age": {"value": 58, "confidence": 95},      # High confidence
            "sex": {"value": None, "confidence": 0},     # Missing
            "test_date": {"value": "2025-03-15", "confidence": 65}  # Low confidence
        }
        
        result = validate_demographic_extraction(demographics)
        
        assert result["valid"] is True
        assert len(result["warnings"]) >= 2
        assert any("sex not found" in warning for warning in result["warnings"])
        assert any("test date" in warning.lower() for warning in result["warnings"])
    
    def test_validate_empty_demographics(self):
        """Test validation with empty demographics."""
        demographics = {}
        
        result = validate_demographic_extraction(demographics)
        
        # Should handle empty input gracefully
        assert result["valid"] is True
        assert len(result["warnings"]) >= 2  # Missing age and sex


class TestDebugDemographicExtraction:
    """Test demographic extraction debugging."""
    
    def test_debug_successful_extraction(self):
        """Test debug output for successful extraction."""
        text = "Patient: 58 Years Male, Collected: 03/15/2025"
        demographics = {
            "age": {
                "value": 58,
                "confidence": 95,
                "raw_text": "58 Years Male",
                "pattern_used": r'(\d+)\s*[Yy]ears?\s*([Mm]ale|[Ff]emale)'
            },
            "sex": {
                "value": "M",
                "confidence": 95,
                "raw_text": "58 Years Male",
                "pattern_used": r'\d+\s*[Yy]ears?\s*([Mm]ale|[Ff]emale)'
            },
            "test_date": {
                "value": "2025-03-15",
                "confidence": 70,
                "raw_text": "03/15/2025",
                "pattern_used": r'(\d{2}/\d{2}/\d{2,4})'
            }
        }
        
        debug_info = debug_extraction(text, demographics)
        
        assert "DEMOGRAPHIC EXTRACTION DEBUG INFO" in debug_info
        assert "age: 58" in debug_info
        assert "sex: M" in debug_info
        assert "test_date: 2025-03-15" in debug_info
        assert "95% confidence" in debug_info
    
    def test_debug_failed_extraction(self):
        """Test debug output for failed extraction."""
        text = "No demographic information here"
        demographics = {
            "age": {"value": None, "confidence": 0, "raw_text": "", "pattern_used": ""},
            "sex": {"value": None, "confidence": 0, "raw_text": "", "pattern_used": ""},
            "test_date": {"value": None, "confidence": 0, "raw_text": "", "pattern_used": ""}
        }
        
        debug_info = debug_extraction(text, demographics)
        
        assert "NOT FOUND" in debug_info
        assert "age: NOT FOUND" in debug_info
        assert "sex: NOT FOUND" in debug_info
        assert "test_date: NOT FOUND" in debug_info
    
    def test_debug_potential_lines(self):
        """Test debug output showing potential missed lines."""
        text = """
        Some text here
        Patient age is 45 years
        Gender: Male
        Collection date was 03/15/2025
        """
        
        demographics = {
            "age": {"value": None, "confidence": 0, "raw_text": "", "pattern_used": ""},
            "sex": {"value": None, "confidence": 0, "raw_text": "", "pattern_used": ""},
            "test_date": {"value": None, "confidence": 0, "raw_text": "", "pattern_used": ""}
        }
        
        debug_info = debug_extraction(text, demographics)
        
        assert "Potential demographic lines found:" in debug_info
        # Should show lines with age, gender, and date keywords
        assert "45 years" in debug_info or "Male" in debug_info or "03/15/2025" in debug_info


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""
    
    def test_extract_age_with_noise(self):
        """Test age extraction with noisy text."""
        text = "Patient ID: 123456, Age: 58, Test #78954"
        result = extract_patient_age(text)
        
        assert result["value"] == 58
        # Should not pick up the ID numbers
    
    def test_extract_sex_ambiguous_context(self):
        """Test sex extraction with ambiguous context."""
        text = "Patient M seen by Dr. F. Smith"
        result = extract_patient_sex(text)
        
        # Should pick up patient sex, not doctor's
        assert result["value"] == "M"
    
    def test_extract_date_multiple_formats(self):
        """Test date extraction with multiple date formats in same text."""
        text = "Born: 01/01/1965, Collected: 03/15/2025, Due: 04/01/2025"
        result = extract_test_date(text)
        
        # Should pick collection date as highest priority
        assert result["value"] == "2025-03-15"
        assert result["confidence"] >= 90
    
    def test_extract_demographics_empty_input(self):
        """Test demographic extraction with empty input."""
        demographics = extract_patient_demographics("")
        
        assert demographics["age"]["value"] is None
        assert demographics["sex"]["value"] is None
        assert demographics["test_date"]["value"] is None
    
    def test_extract_demographics_very_long_text(self):
        """Test demographic extraction with very long text."""
        # Create long text with demographics buried in it
        long_text = "Lorem ipsum " * 1000 + " Age: 45, Male, Collected: 03/15/2025 " + "dolor sit amet " * 1000
        
        demographics = extract_patient_demographics(long_text)
        
        # Should still find demographics in long text
        assert demographics["age"]["value"] == 45
        assert demographics["sex"]["value"] == "M"
        assert demographics["test_date"]["value"] == "2025-03-15"


# Property-based testing with hypothesis
class TestPropertyBasedDemographicExtraction:
    """Property-based tests for demographic extraction."""
    
    @given(age=st.integers(min_value=18, max_value=120))
    def test_age_extraction_properties(self, age):
        """Test age extraction properties."""
        # Test various formats
        formats = [
            f"{age} Years Male",
            f"Age: {age}",
            f"{age} yo",
            f"{age} M"
        ]
        
        for text in formats:
            result = extract_patient_age(text)
            if result["value"] is not None:
                assert result["value"] == age
                assert 70 <= result["confidence"] <= 95
    
    @given(sex=st.sampled_from(["M", "F"]))
    def test_sex_extraction_properties(self, sex):
        """Test sex extraction properties."""
        full_word = "Male" if sex == "M" else "Female"
        
        formats = [
            f"58 Years {full_word}",
            f"Sex: {sex}",
            f"{sex} 45 years",
            full_word
        ]
        
        for text in formats:
            result = extract_patient_sex(text)
            if result["value"] is not None:
                assert result["value"] == sex
                assert result["confidence"] > 0
    
    @given(
        year=st.integers(min_value=2020, max_value=2030),
        month=st.integers(min_value=1, max_value=12),
        day=st.integers(min_value=1, max_value=28)  # Safe day range
    )
    def test_date_extraction_properties(self, year, month, day):
        """Test date extraction properties."""
        # Test MM/DD/YYYY format
        date_str = f"{month:02d}/{day:02d}/{year}"
        text = f"Collected: {date_str}"
        
        result = extract_test_date(text)
        if result["value"] is not None:
            expected = f"{year}-{month:02d}-{day:02d}"
            assert result["value"] == expected
            assert result["confidence"] > 0


class TestRegressionTests:
    """Regression tests for known demographic extraction scenarios."""
    
    def test_real_lab_format_1(self):
        """Test extraction from real lab format 1."""
        text = """
        LABORATORY REPORT
        
        Patient Information:
        Name: John Doe
        DOB: 01/15/1967
        Age: 58 Years Male
        
        Collection Date: 03/15/2025
        Report Date: 03/16/2025
        """
        
        demographics = extract_patient_demographics(text)
        
        assert demographics["age"]["value"] == 58
        assert demographics["sex"]["value"] == "M"
        assert demographics["test_date"]["value"] == "2025-03-15"
    
    def test_real_lab_format_2(self):
        """Test extraction from real lab format 2."""
        text = """
        PATIENT: JANE SMITH
        AGE: 32    SEX: F
        COLLECTED: 06/30/25
        
        COMPLETE BLOOD COUNT
        """
        
        demographics = extract_patient_demographics(text)
        
        assert demographics["age"]["value"] == 32
        assert demographics["sex"]["value"] == "F"
        assert demographics["test_date"]["value"] == "2025-06-30"
    
    def test_minimal_demographics_format(self):
        """Test extraction from minimal format."""
        text = "45 M 03/15/25"
        
        demographics = extract_patient_demographics(text)
        
        assert demographics["age"]["value"] == 45
        assert demographics["sex"]["value"] == "M"
        assert demographics["test_date"]["value"] == "2025-03-15"


# Helper function for debugging
def debug_extraction(text: str, demographics: Dict[str, Dict[str, Any]]) -> str:
    """Helper function that matches the module's debug function."""
    return debug_demographic_extraction(text, demographics)