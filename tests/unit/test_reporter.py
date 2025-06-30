"""Unit tests for the reporter module."""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from immune_inflam_index.reporter import (
    generate_report, save_results, _generate_pdf_content,
    _generate_json_content, _generate_text_content, _save_pdf_report
)


class TestGenerateReport:
    """Test report generation in different formats."""
    
    def test_generate_report_pdf_format(self):
        """Test PDF format report generation."""
        results = {
            "results": {
                "sii": {"value": 877.8, "risk_level": "normal", "interpretation": "Normal systemic inflammation"},
                "nlr": {"value": 3.5, "risk_level": "mild", "interpretation": "Mild neutrophilia"}
            },
            "summary": {"overall_inflammatory_status": "Normal inflammatory state"},
            "metadata": {"calculation_date": "2025-06-30"}
        }
        
        report = generate_report(results, "pdf")
        
        assert "# Immune Inflammatory Index Report" in report
        assert "## Calculated Indices" in report
        assert "SII: 877.8 (normal)" in report
        assert "NLR: 3.5 (mild)" in report
    
    def test_generate_report_json_format(self):
        """Test JSON format report generation."""
        results = {
            "results": {
                "sii": {"value": 877.8, "risk_level": "normal"}
            },
            "summary": {"overall_inflammatory_status": "Normal"}
        }
        
        report = generate_report(results, "json")
        
        # Should be valid JSON
        parsed = json.loads(report)
        assert "report_metadata" in parsed
        assert "results" in parsed
        assert "summary" in parsed
        assert parsed["results"]["sii"]["value"] == 877.8
    
    def test_generate_report_text_format(self):
        """Test text format report generation."""
        results = {
            "results": {
                "sii": {"value": 877.8, "risk_level": "normal", "interpretation": "Normal systemic inflammation"}
            },
            "summary": {"overall_inflammatory_status": "Normal inflammatory state"}
        }
        
        report = generate_report(results, "text")
        
        assert "IMMUNE INFLAMMATORY INDEX REPORT" in report
        assert "CALCULATED INDICES" in report
        assert "SII: 877.8" in report
        assert "Risk Level: Normal" in report
        assert "OVERALL ASSESSMENT" in report
    
    def test_generate_report_invalid_format(self):
        """Test error handling for invalid format."""
        results = {"results": {}}
        
        with pytest.raises(ValueError, match="Unsupported format type"):
            generate_report(results, "invalid_format")


class TestSaveResults:
    """Test saving results to files."""
    
    def test_save_results_pdf(self, temp_output_dir):
        """Test saving results as PDF."""
        results = {
            "results": {
                "sii": {"value": 877.8, "risk_level": "normal", "interpretation": "Normal"}
            },
            "summary": {"overall_inflammatory_status": "Normal"}
        }
        
        with patch('immune_inflam_index.reporter._save_pdf_report') as mock_save_pdf:
            filepath = save_results(results, str(temp_output_dir), "pdf")
            
            assert filepath.endswith(".pdf")
            assert "immune_inflammatory_report_" in filepath
            assert Path(filepath).parent == temp_output_dir
            mock_save_pdf.assert_called_once()
    
    def test_save_results_json(self, temp_output_dir):
        """Test saving results as JSON."""
        results = {
            "results": {
                "sii": {"value": 877.8, "risk_level": "normal"}
            }
        }
        
        filepath = save_results(results, str(temp_output_dir), "json")
        
        assert filepath.endswith(".json")
        assert "immune_inflammatory_results_" in filepath
        
        # Verify file was created and contains valid JSON
        with open(filepath, 'r') as f:
            data = json.load(f)
            assert "report_metadata" in data
            assert data["results"]["sii"]["value"] == 877.8
    
    def test_save_results_text(self, temp_output_dir):
        """Test saving results as text."""
        results = {
            "results": {
                "sii": {"value": 877.8, "risk_level": "normal", "interpretation": "Normal"}
            }
        }
        
        filepath = save_results(results, str(temp_output_dir), "text")
        
        assert filepath.endswith(".txt")
        assert "immune_inflammatory_report_" in filepath
        
        # Verify file was created and contains expected content
        with open(filepath, 'r') as f:
            content = f.read()
            assert "IMMUNE INFLAMMATORY INDEX REPORT" in content
            assert "SII: 877.8" in content
    
    def test_save_results_creates_directory(self):
        """Test that save_results creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            non_existent_dir = Path(temp_dir) / "new_directory"
            
            results = {"results": {"sii": {"value": 877.8, "risk_level": "normal", "interpretation": "Normal"}}}
            
            with patch('immune_inflam_index.reporter._save_pdf_report'):
                filepath = save_results(results, str(non_existent_dir), "pdf")
                
                assert non_existent_dir.exists()
                assert Path(filepath).parent == non_existent_dir
    
    def test_save_results_invalid_format(self, temp_output_dir):
        """Test error handling for invalid format in save_results."""
        results = {"results": {}}
        
        with pytest.raises(ValueError, match="Unsupported format type"):
            save_results(results, str(temp_output_dir), "invalid_format")
    
    def test_save_results_filename_timestamp(self, temp_output_dir):
        """Test that saved files have timestamp in filename."""
        results = {"results": {"sii": {"value": 877.8, "risk_level": "normal", "interpretation": "Normal"}}}
        
        with patch('immune_inflam_index.reporter._save_pdf_report'):
            filepath1 = save_results(results, str(temp_output_dir), "pdf")
            filepath2 = save_results(results, str(temp_output_dir), "pdf")
            
            # Files should have different names due to timestamp
            assert filepath1 != filepath2
            assert "immune_inflammatory_report_" in Path(filepath1).name
            assert "immune_inflammatory_report_" in Path(filepath2).name


class TestGeneratePdfContent:
    """Test PDF content generation."""
    
    def test_generate_pdf_content_basic(self):
        """Test basic PDF content generation."""
        results = {
            "results": {
                "sii": {"value": 877.8, "risk_level": "normal"},
                "nlr": {"value": 3.5, "risk_level": "mild"}
            }
        }
        
        content = _generate_pdf_content(results)
        
        assert "# Immune Inflammatory Index Report" in content
        assert "## Calculated Indices" in content
        assert "SII: 877.8 (normal)" in content
        assert "NLR: 3.5 (mild)" in content
        assert "Generated:" in content
    
    def test_generate_pdf_content_with_pdf_parsing(self):
        """Test PDF content generation with PDF parsing info."""
        results = {
            "results": {
                "sii": {"value": 877.8, "risk_level": "normal"}
            },
            "pdf_parsing": {
                "extraction_method": "text_based"
            }
        }
        
        content = _generate_pdf_content(results)
        
        assert "## PDF Source Information" in content
        assert "Extraction Method: text_based" in content
    
    def test_generate_pdf_content_empty_results(self):
        """Test PDF content generation with empty results."""
        results = {}
        
        content = _generate_pdf_content(results)
        
        assert "# Immune Inflammatory Index Report" in content
        assert "Generated:" in content
        # Should handle empty results gracefully


class TestGenerateJsonContent:
    """Test JSON content generation."""
    
    def test_generate_json_content_complete(self):
        """Test JSON content generation with complete data."""
        results = {
            "results": {
                "sii": {"value": 877.8, "risk_level": "normal"}
            },
            "summary": {"overall_inflammatory_status": "Normal"},
            "interpretation": {"clinical_assessment": {}},
            "pdf_parsing": {"extraction_method": "text_based"},
            "metadata": {"calculation_date": "2025-06-30"}
        }
        
        json_content = _generate_json_content(results)
        parsed = json.loads(json_content)
        
        # Check structure
        assert "report_metadata" in parsed
        assert "results" in parsed
        assert "summary" in parsed
        assert "interpretation" in parsed
        assert "pdf_parsing" in parsed
        assert "metadata" in parsed
        
        # Check metadata
        assert "generated_timestamp" in parsed["report_metadata"]
        assert parsed["report_metadata"]["report_type"] == "immune_inflammatory_index"
        assert parsed["report_metadata"]["version"] == "1.0"
        
        # Check data preservation
        assert parsed["results"]["sii"]["value"] == 877.8
        assert parsed["summary"]["overall_inflammatory_status"] == "Normal"
    
    def test_generate_json_content_partial_data(self):
        """Test JSON content generation with partial data."""
        results = {
            "results": {
                "sii": {"value": 877.8, "risk_level": "normal"}
            }
        }
        
        json_content = _generate_json_content(results)
        parsed = json.loads(json_content)
        
        assert "report_metadata" in parsed
        assert "results" in parsed
        assert parsed["results"]["sii"]["value"] == 877.8
        # Missing sections should be empty dicts
        assert parsed["summary"] == {}
        assert parsed["interpretation"] == {}
    
    def test_generate_json_content_unicode_support(self):
        """Test JSON content generation with Unicode characters."""
        results = {
            "results": {
                "sii": {"value": 877.8, "interpretation": "Normal inflammation μL"}
            }
        }
        
        json_content = _generate_json_content(results)
        parsed = json.loads(json_content)
        
        assert "μL" in parsed["results"]["sii"]["interpretation"]


class TestGenerateTextContent:
    """Test text content generation."""
    
    def test_generate_text_content_complete(self):
        """Test text content generation with complete data."""
        results = {
            "results": {
                "sii": {"value": 877.8, "risk_level": "normal", "interpretation": "Normal systemic inflammation"},
                "nlr": {"value": 3.5, "risk_level": "mild", "interpretation": "Mild neutrophilia"}
            },
            "summary": {
                "overall_inflammatory_status": "Normal inflammatory state",
                "recommendations": ["Maintain healthy lifestyle", "Regular monitoring"]
            },
            "interpretation": {
                "risk_stratification": {
                    "overall_risk_level": "low",
                    "urgency": "routine_monitoring"
                },
                "patient_context": {
                    "age": 45,
                    "sex": "M",
                    "age_considerations": ["Middle-aged adults may show early signs of inflammaging"],
                    "sex_considerations": ["Men may have higher baseline inflammatory burden"]
                }
            },
            "pdf_parsing": {
                "extraction_method": "text_based",
                "confidence_scores": {
                    "neutrophils": 95,
                    "lymphocytes": 90
                }
            },
            "metadata": {
                "pdf_source": "test.pdf",
                "warnings": ["Auto-detected patient age: 45 years"]
            }
        }
        
        content = _generate_text_content(results)
        
        # Check main sections
        assert "IMMUNE INFLAMMATORY INDEX REPORT" in content
        assert "PDF SOURCE INFORMATION" in content
        assert "CALCULATED INDICES" in content
        assert "OVERALL ASSESSMENT" in content
        assert "CLINICAL INTERPRETATION" in content
        assert "PATIENT DEMOGRAPHICS & CLINICAL CONTEXT" in content
        assert "EXTRACTION CONFIDENCE" in content
        assert "WARNINGS" in content
        assert "IMPORTANT DISCLAIMERS" in content
        
        # Check specific content
        assert "SII: 877.8" in content
        assert "Risk Level: Normal" in content
        assert "NLR: 3.5" in content
        assert "Risk Level: Mild" in content
        assert "Normal inflammatory state" in content
        assert "Maintain healthy lifestyle" in content
        assert "Overall Risk Level: Low" in content
        assert "Age: 45 years" in content
        assert "Age Group: Middle-aged Adult (35-65)" in content
        assert "Sex: M" in content
        assert "Neutrophils: 95% (High)" in content
        assert "Auto-detected patient age" in content
    
    def test_generate_text_content_minimal(self):
        """Test text content generation with minimal data."""
        results = {
            "results": {
                "sii": {"value": 877.8, "risk_level": "normal", "interpretation": "Normal"}
            }
        }
        
        content = _generate_text_content(results)
        
        assert "IMMUNE INFLAMMATORY INDEX REPORT" in content
        assert "CALCULATED INDICES" in content
        assert "SII: 877.8" in content
        assert "IMPORTANT DISCLAIMERS" in content
        # Should not have sections for missing data
        assert "PDF SOURCE INFORMATION" not in content
        assert "OVERALL ASSESSMENT" not in content
    
    def test_generate_text_content_age_groups(self):
        """Test age group determination in text content."""
        age_test_cases = [
            (15, "Pediatric"),
            (25, "Young Adult (18-35)"),
            (45, "Middle-aged Adult (35-65)"),
            (75, "Elderly Adult (65+)")
        ]
        
        for age, expected_group in age_test_cases:
            results = {
                "results": {"sii": {"value": 877.8, "risk_level": "normal", "interpretation": "Normal"}},
                "interpretation": {
                    "patient_context": {"age": age, "sex": "M"}
                }
            }
            
            content = _generate_text_content(results)
            assert f"Age Group: {expected_group}" in content
    
    def test_generate_text_content_confidence_levels(self):
        """Test confidence level descriptions in text content."""
        confidence_test_cases = [
            (95, "High"),
            (75, "Medium"), 
            (45, "Low")
        ]
        
        for confidence, expected_status in confidence_test_cases:
            results = {
                "results": {"sii": {"value": 877.8, "risk_level": "normal", "interpretation": "Normal"}},
                "pdf_parsing": {
                    "confidence_scores": {
                        "neutrophils": confidence
                    }
                }
            }
            
            content = _generate_text_content(results)
            assert f"Neutrophils: {confidence}% ({expected_status})" in content


class TestSavePdfReport:
    """Test PDF report saving functionality."""
    
    @patch('immune_inflam_index.reporter.SimpleDocTemplate')
    def test_save_pdf_report_structure(self, mock_doc):
        """Test PDF report saving creates proper structure."""
        # Mock the document and story
        mock_doc_instance = MagicMock()
        mock_doc.return_value = mock_doc_instance
        
        results = {
            "results": {
                "sii": {"value": 877.8, "risk_level": "normal", "interpretation": "Normal systemic inflammation"}
            },
            "summary": {"overall_inflammatory_status": "Normal"},
            "interpretation": {
                "risk_stratification": {"overall_risk_level": "low", "urgency": "routine"},
                "patient_context": {"age": 45, "sex": "M"}
            },
            "pdf_parsing": {
                "extraction_method": "text_based",
                "confidence_scores": {"neutrophils": 95}
            }
        }
        
        _save_pdf_report(results, "test_report.pdf")
        
        # Verify document was created and built
        mock_doc.assert_called_once()
        mock_doc_instance.build.assert_called_once()
        
        # The story (content) should be passed to build
        story = mock_doc_instance.build.call_args[0][0]
        assert len(story) > 0  # Should have content elements
    
    @patch('immune_inflam_index.reporter.SimpleDocTemplate')
    def test_save_pdf_report_empty_results(self, mock_doc):
        """Test PDF report saving with empty results."""
        mock_doc_instance = MagicMock()
        mock_doc.return_value = mock_doc_instance
        
        results = {}
        
        _save_pdf_report(results, "test_report.pdf")
        
        # Should still create document without errors
        mock_doc.assert_called_once()
        mock_doc_instance.build.assert_called_once()


class TestReportContentQuality:
    """Test the quality and completeness of generated reports."""
    
    def test_report_contains_required_disclaimers(self):
        """Test that all reports contain required medical disclaimers."""
        results = {
            "results": {"sii": {"value": 877.8, "risk_level": "normal", "interpretation": "Normal"}}
        }
        
        # Test all formats
        text_report = generate_report(results, "text")
        json_report = generate_report(results, "json")
        
        # Text report should have disclaimers section
        assert "IMPORTANT DISCLAIMERS" in text_report
        assert "screening tools, not diagnostic tests" in text_report
        assert "qualified healthcare providers" in text_report
        
        # JSON report should preserve disclaimer content in structure
        json_data = json.loads(json_report)
        assert "report_metadata" in json_data
    
    def test_report_timestamp_consistency(self):
        """Test that report timestamps are recent and consistent."""
        results = {"results": {"sii": {"value": 877.8, "risk_level": "normal", "interpretation": "Normal"}}}
        
        # Generate reports
        text_report = generate_report(results, "text")
        json_report = generate_report(results, "json")
        
        # Check that timestamps are present and recent
        assert "Generated:" in text_report
        
        json_data = json.loads(json_report)
        timestamp_str = json_data["report_metadata"]["generated_timestamp"]
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.now()
        
        # Timestamp should be within last minute
        assert (now - timestamp).total_seconds() < 60
    
    def test_report_handles_special_characters(self):
        """Test that reports handle special characters properly."""
        results = {
            "results": {
                "sii": {
                    "value": 877.8,
                    "risk_level": "normal",
                    "interpretation": "Normal inflammation with μL/mL units"
                }
            }
        }
        
        # All formats should handle Unicode properly
        text_report = generate_report(results, "text")
        json_report = generate_report(results, "json")
        
        assert "μL/mL" in text_report
        
        json_data = json.loads(json_report)
        assert "μL/mL" in json_data["results"]["sii"]["interpretation"]


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""
    
    def test_generate_report_with_missing_fields(self):
        """Test report generation with missing or None fields."""
        # Test with minimal results
        results = {
            "results": {
                "sii": {"value": 877.8}  # Missing risk_level and interpretation
            }
        }
        
        # Should not crash, but handle missing fields gracefully
        text_report = generate_report(results, "text")
        json_report = generate_report(results, "json")
        
        assert "SII: 877.8" in text_report
        
        json_data = json.loads(json_report)
        assert json_data["results"]["sii"]["value"] == 877.8
    
    def test_generate_report_with_none_values(self):
        """Test report generation with None values."""
        results = {
            "results": {
                "sii": {"value": None, "risk_level": None, "interpretation": None}
            },
            "summary": None,
            "interpretation": None
        }
        
        # Should handle None values without crashing
        text_report = generate_report(results, "text")
        json_report = generate_report(results, "json")
        
        assert text_report is not None
        assert json_report is not None
        
        json_data = json.loads(json_report)
        assert "results" in json_data
    
    def test_save_results_permission_error(self, temp_output_dir):
        """Test handling of permission errors during file saving."""
        results = {"results": {"sii": {"value": 877.8, "risk_level": "normal", "interpretation": "Normal"}}}
        
        # Try to save to a read-only directory (simulate permission error)
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(PermissionError):
                save_results(results, str(temp_output_dir), "text")


class TestRegressionTests:
    """Regression tests for known report generation scenarios."""
    
    def test_complete_report_scenario(self):
        """Test complete report generation scenario."""
        # This represents a full workflow result
        complete_results = {
            "results": {
                "sii": {"value": 877.8, "risk_level": "normal", "interpretation": "Normal systemic inflammation"},
                "nlr": {"value": 3.5, "risk_level": "mild", "interpretation": "Mild neutrophilia"},
                "plr": {"value": 125.0, "risk_level": "normal", "interpretation": "Normal platelet balance"}
            },
            "summary": {
                "overall_inflammatory_status": "Normal inflammatory state",
                "highest_risk_indices": [],
                "recommendations": ["Maintain healthy lifestyle", "Regular monitoring"]
            },
            "interpretation": {
                "clinical_assessment": {},
                "risk_stratification": {
                    "overall_risk_level": "low",
                    "urgency": "routine_monitoring"
                },
                "patient_context": {
                    "age": 45,
                    "sex": "M",
                    "age_considerations": ["Middle-aged consideration"],
                    "sex_considerations": ["Male-specific consideration"]
                }
            },
            "pdf_parsing": {
                "extraction_method": "text_based",
                "confidence_scores": {"neutrophils": 95, "lymphocytes": 90, "platelets": 98},
                "manual_verification_needed": False
            },
            "metadata": {
                "pdf_source": "/path/to/test.pdf",
                "warnings": ["Auto-detected patient age: 45 years"]
            }
        }
        
        # Generate all formats
        text_report = generate_report(complete_results, "text")
        json_report = generate_report(complete_results, "json")
        
        # Verify comprehensive content in text report
        assert "SII: 877.8" in text_report
        assert "NLR: 3.5" in text_report
        assert "PLR: 125.0" in text_report
        assert "Normal inflammatory state" in text_report
        assert "Age: 45 years" in text_report
        assert "Sex: M" in text_report
        assert "Neutrophils: 95% (High)" in text_report
        
        # Verify JSON structure
        json_data = json.loads(json_report)
        assert len(json_data["results"]) == 3
        assert json_data["summary"]["overall_inflammatory_status"] == "Normal inflammatory state"
        assert json_data["interpretation"]["patient_context"]["age"] == 45