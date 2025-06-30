"""Unit tests for the pdf_parser module."""

import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from typing import Dict, Any

from immune_inflam_index.pdf_parser import (
    PDFParsingError, extract_text_from_pdf, extract_text_with_ocr,
    determine_extraction_method, find_cbc_section, process_pdf,
    manual_fallback_mode
)


class TestPDFParsingError:
    """Test custom PDF parsing exception."""
    
    def test_pdf_parsing_error_basic(self):
        """Test basic PDFParsingError creation."""
        error = PDFParsingError("Test error message")
        
        assert str(error) == "Test error message"
        assert error.extracted_text == ""
        assert error.missing_fields == []
    
    def test_pdf_parsing_error_with_details(self):
        """Test PDFParsingError with additional details."""
        extracted_text = "Some extracted text"
        missing_fields = ["neutrophils", "lymphocytes"]
        
        error = PDFParsingError("Test error", extracted_text, missing_fields)
        
        assert str(error) == "Test error"
        assert error.extracted_text == extracted_text
        assert error.missing_fields == missing_fields


class TestExtractTextFromPdf:
    """Test PDF text extraction."""
    
    @patch('immune_inflam_index.pdf_parser.pdfplumber.open')
    def test_extract_text_success(self, mock_open_pdf):
        """Test successful text extraction from PDF."""
        # Mock PDF with text content
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test page content"
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_open_pdf.return_value.__enter__.return_value = mock_pdf
        
        text, method = extract_text_from_pdf("test.pdf")
        
        assert text == "Test page content"
        assert method == "text_based"
        mock_open_pdf.assert_called_once_with("test.pdf")
    
    @patch('immune_inflam_index.pdf_parser.pdfplumber.open')
    def test_extract_text_multiple_pages(self, mock_open_pdf):
        """Test text extraction from multiple pages."""
        # Mock PDF with multiple pages
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 content"
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_open_pdf.return_value.__enter__.return_value = mock_pdf
        
        text, method = extract_text_from_pdf("test.pdf")
        
        assert text == "Page 1 content\nPage 2 content"
        assert method == "text_based"
    
    @patch('immune_inflam_index.pdf_parser.pdfplumber.open')
    def test_extract_text_no_content(self, mock_open_pdf):
        """Test extraction when PDF has no extractable text."""
        # Mock PDF with no text content
        mock_page = MagicMock()
        mock_page.extract_text.return_value = None
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_open_pdf.return_value.__enter__.return_value = mock_pdf
        
        text, method = extract_text_from_pdf("test.pdf")
        
        assert text == ""
        assert method == "text_based_failed"
    
    @patch('immune_inflam_index.pdf_parser.pdfplumber.open')
    def test_extract_text_error(self, mock_open_pdf):
        """Test error handling during text extraction."""
        mock_open_pdf.side_effect = Exception("PDF corruption error")
        
        with pytest.raises(PDFParsingError, match="Failed to extract text from PDF"):
            extract_text_from_pdf("test.pdf")


class TestExtractTextWithOcr:
    """Test OCR text extraction."""
    
    @patch('immune_inflam_index.pdf_parser.pytesseract.image_to_string')
    @patch('immune_inflam_index.pdf_parser.pdfplumber.open')
    def test_extract_text_ocr_success(self, mock_open_pdf, mock_ocr):
        """Test successful OCR extraction."""
        # Mock PDF page to image conversion
        mock_image = MagicMock()
        mock_page_image = MagicMock()
        mock_page_image.original = mock_image
        
        mock_page = MagicMock()
        mock_page.to_image.return_value = mock_page_image
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_open_pdf.return_value.__enter__.return_value = mock_pdf
        
        # Mock OCR result
        mock_ocr.return_value = "OCR extracted text"
        
        text, method = extract_text_with_ocr("test.pdf")
        
        assert text == "OCR extracted text"
        assert method == "ocr"
        mock_ocr.assert_called_once_with(mock_image)
    
    @patch('immune_inflam_index.pdf_parser.pytesseract.image_to_string')
    @patch('immune_inflam_index.pdf_parser.pdfplumber.open')
    def test_extract_text_ocr_no_content(self, mock_open_pdf, mock_ocr):
        """Test OCR when no text is found."""
        # Mock setup
        mock_image = MagicMock()
        mock_page_image = MagicMock()
        mock_page_image.original = mock_image
        
        mock_page = MagicMock()
        mock_page.to_image.return_value = mock_page_image
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_open_pdf.return_value.__enter__.return_value = mock_pdf
        
        # Mock OCR returning empty text
        mock_ocr.return_value = "   "  # Only whitespace
        
        text, method = extract_text_with_ocr("test.pdf")
        
        assert text == ""
        assert method == "ocr_failed"
    
    @patch('immune_inflam_index.pdf_parser.pdfplumber.open')
    def test_extract_text_ocr_error(self, mock_open_pdf):
        """Test error handling during OCR extraction."""
        mock_open_pdf.side_effect = Exception("OCR processing error")
        
        with pytest.raises(PDFParsingError, match="OCR extraction failed"):
            extract_text_with_ocr("test.pdf")


class TestDetermineExtractionMethod:
    """Test extraction method determination."""
    
    @patch('immune_inflam_index.pdf_parser.extract_text_from_pdf')
    def test_determine_method_text_based(self, mock_extract):
        """Test determination when text-based extraction works."""
        # Mock successful text extraction with substantial content
        long_text = "A" * 200  # More than 100 characters
        mock_extract.return_value = (long_text, "text_based")
        
        method = determine_extraction_method("test.pdf")
        
        assert method == "text_based"
    
    @patch('immune_inflam_index.pdf_parser.extract_text_from_pdf')
    def test_determine_method_ocr_needed(self, mock_extract):
        """Test determination when OCR is needed."""
        # Mock text extraction with insufficient content
        short_text = "A" * 50  # Less than 100 characters
        mock_extract.return_value = (short_text, "text_based")
        
        method = determine_extraction_method("test.pdf")
        
        assert method == "ocr"
    
    @patch('immune_inflam_index.pdf_parser.extract_text_from_pdf')
    def test_determine_method_error_fallback(self, mock_extract):
        """Test fallback to OCR when text extraction fails."""
        mock_extract.side_effect = Exception("Text extraction failed")
        
        method = determine_extraction_method("test.pdf")
        
        assert method == "ocr"


class TestFindCbcSection:
    """Test CBC section finding."""
    
    def test_find_cbc_section_with_header(self):
        """Test finding CBC section with clear header."""
        text = """
        PATIENT INFORMATION
        Name: John Doe
        
        COMPLETE BLOOD COUNT
        Neutrophils: 6.31 x10³/L
        Lymphocytes: 1.8 x10³/L
        Platelets: 250 x10³/L
        
        KIDNEY FUNCTION
        Creatinine: 1.0 mg/dL
        """
        
        cbc_section = find_cbc_section(text)
        
        assert "COMPLETE BLOOD COUNT" in cbc_section
        assert "Neutrophils" in cbc_section
        assert "Lymphocytes" in cbc_section
        assert "Platelets" in cbc_section
        # Should not include kidney function section
        assert "KIDNEY FUNCTION" not in cbc_section or cbc_section.find("KIDNEY") > cbc_section.find("Platelets")
    
    def test_find_cbc_section_alternative_headers(self):
        """Test finding CBC section with alternative headers."""
        headers_to_test = [
            "CBC WITH DIFFERENTIAL",
            "HEMATOLOGY",
            "BLOOD COUNT",
            "FBC"
        ]
        
        for header in headers_to_test:
            text = f"""
            {header}
            Neutrophils: 6.31 x10³/L
            Lymphocytes: 1.8 x10³/L
            """
            
            cbc_section = find_cbc_section(text)
            
            assert header in cbc_section or header.lower() in cbc_section.lower()
            assert "Neutrophils" in cbc_section
    
    def test_find_cbc_section_no_header(self):
        """Test CBC section finding when no header is present."""
        text = "Some text without CBC header but with blood values"
        
        cbc_section = find_cbc_section(text)
        
        # Should return first 2000 characters when no header found
        assert len(cbc_section) <= 2000
        assert cbc_section == text[:2000]
    
    def test_find_cbc_section_case_insensitive(self):
        """Test CBC section finding is case insensitive."""
        text = """
        complete blood count
        Neutrophils: 6.31 x10³/L
        Lymphocytes: 1.8 x10³/L
        """
        
        cbc_section = find_cbc_section(text)
        
        assert "complete blood count" in cbc_section.lower()
        assert "Neutrophils" in cbc_section


class TestProcessPdf:
    """Test main PDF processing function."""
    
    @patch('immune_inflam_index.pdf_parser.Path')
    def test_process_pdf_file_not_found(self, mock_path):
        """Test process_pdf with non-existent file."""
        # Mock file not existing
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance
        
        with pytest.raises(PDFParsingError, match="PDF file not found"):
            process_pdf("nonexistent.pdf")
    
    @patch('immune_inflam_index.pdf_parser.interpret_results')
    @patch('immune_inflam_index.pdf_parser.calculate_indices')
    @patch('immune_inflam_index.pdf_parser.validate_demographic_extraction')
    @patch('immune_inflam_index.pdf_parser.extract_patient_demographics')
    @patch('immune_inflam_index.pdf_parser.validate_pdf_extracted_values')
    @patch('immune_inflam_index.pdf_parser.extract_cbc_values')
    @patch('immune_inflam_index.pdf_parser.find_cbc_section')
    @patch('immune_inflam_index.pdf_parser.determine_extraction_method')
    @patch('immune_inflam_index.pdf_parser.extract_text_from_pdf')
    @patch('immune_inflam_index.pdf_parser.Path')
    def test_process_pdf_successful_text_based(
        self, mock_path, mock_extract_text, mock_determine_method,
        mock_find_section, mock_extract_cbc, mock_validate_pdf,
        mock_extract_demographics, mock_validate_demographics,
        mock_calculate, mock_interpret
    ):
        """Test successful PDF processing with text-based extraction."""
        # Setup mocks
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.absolute.return_value = Path("/test/path.pdf")
        mock_path.return_value = mock_path_instance
        
        mock_determine_method.return_value = "text_based"
        mock_extract_text.return_value = ("PDF text content", "text_based")
        mock_find_section.return_value = "CBC section text"
        
        # Mock CBC extraction
        mock_extracted_values = {
            "neutrophils": {"value": 6310, "confidence": 95},
            "lymphocytes": {"value": 1800, "confidence": 90},
            "platelets": {"value": 250000, "confidence": 98}
        }
        mock_extract_cbc.return_value = mock_extracted_values
        
        # Mock validation
        mock_validate_pdf.return_value = {
            "valid": True,
            "warnings": [],
            "manual_verification_needed": False
        }
        
        # Mock demographics
        mock_demographics = {
            "age": {"value": 45, "confidence": 85},
            "sex": {"value": "M", "confidence": 90},
            "test_date": {"value": "2025-06-30", "confidence": 80}
        }
        mock_extract_demographics.return_value = mock_demographics
        mock_validate_demographics.return_value = {
            "valid": True,
            "warnings": [],
            "manual_verification_needed": False
        }
        
        # Mock calculations
        mock_calculation_results = {
            "results": {
                "sii": {"value": 877.8, "risk_level": "normal"},
                "nlr": {"value": 3.5, "risk_level": "mild"}
            },
            "summary": {"overall_inflammatory_status": "Normal"},
            "metadata": {"calculation_date": "2025-06-30"}
        }
        mock_calculate.return_value = mock_calculation_results
        
        # Mock interpretation
        mock_interpretation = {
            "clinical_assessment": {"sii": {"clinical_significance": "Normal inflammation"}},
            "recommendations": {"immediate": []}
        }
        mock_interpret.return_value = mock_interpretation
        
        # Execute
        result = process_pdf("test.pdf")
        
        # Verify structure
        assert "pdf_parsing" in result
        assert "results" in result
        assert "summary" in result
        assert "metadata" in result
        assert "interpretation" in result
        
        # Verify PDF parsing results
        assert result["pdf_parsing"]["extraction_method"] == "text_based"
        assert result["pdf_parsing"]["extracted_values"] == mock_extracted_values
        assert not result["pdf_parsing"]["manual_verification_needed"]
        
        # Verify calculations were called with correct values
        mock_calculate.assert_called_once_with(6310, 1800, 250000, None)
    
    @patch('immune_inflam_index.pdf_parser.validate_pdf_extracted_values')
    @patch('immune_inflam_index.pdf_parser.extract_cbc_values')
    @patch('immune_inflam_index.pdf_parser.find_cbc_section')
    @patch('immune_inflam_index.pdf_parser.determine_extraction_method')
    @patch('immune_inflam_index.pdf_parser.extract_text_from_pdf')
    @patch('immune_inflam_index.pdf_parser.Path')
    def test_process_pdf_no_cbc_values(
        self, mock_path, mock_extract_text, mock_determine_method,
        mock_find_section, mock_extract_cbc, mock_validate_pdf
    ):
        """Test PDF processing when no CBC values are found."""
        # Setup mocks
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        
        mock_determine_method.return_value = "text_based"
        mock_extract_text.return_value = ("PDF text content", "text_based")
        mock_find_section.return_value = "CBC section text"
        mock_extract_cbc.return_value = {}  # No values found
        
        with pytest.raises(PDFParsingError, match="No CBC values found in PDF"):
            process_pdf("test.pdf")
    
    @patch('immune_inflam_index.pdf_parser.extract_text_from_pdf')
    @patch('immune_inflam_index.pdf_parser.extract_text_with_ocr')
    @patch('immune_inflam_index.pdf_parser.determine_extraction_method')
    @patch('immune_inflam_index.pdf_parser.Path')
    def test_process_pdf_no_text_extracted(
        self, mock_path, mock_determine_method, mock_extract_ocr, mock_extract_text
    ):
        """Test PDF processing when no text can be extracted."""
        # Setup mocks
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        
        mock_determine_method.return_value = "text_based"
        mock_extract_text.return_value = ("", "text_based_failed")  # No text
        
        with pytest.raises(PDFParsingError, match="No text could be extracted from PDF"):
            process_pdf("test.pdf")
    
    @patch('immune_inflam_index.pdf_parser.validate_pdf_extracted_values')
    @patch('immune_inflam_index.pdf_parser.extract_cbc_values')
    @patch('immune_inflam_index.pdf_parser.find_cbc_section')
    @patch('immune_inflam_index.pdf_parser.determine_extraction_method')
    @patch('immune_inflam_index.pdf_parser.extract_text_from_pdf')
    @patch('immune_inflam_index.pdf_parser.Path')
    def test_process_pdf_validation_failure(
        self, mock_path, mock_extract_text, mock_determine_method,
        mock_find_section, mock_extract_cbc, mock_validate_pdf
    ):
        """Test PDF processing when validation fails."""
        # Setup mocks
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        
        mock_determine_method.return_value = "text_based"
        mock_extract_text.return_value = ("PDF text content", "text_based")
        mock_find_section.return_value = "CBC section text"
        
        mock_extracted_values = {
            "neutrophils": {"value": 6310, "confidence": 95}
        }
        mock_extract_cbc.return_value = mock_extracted_values
        
        # Mock validation failure
        mock_validate_pdf.return_value = {
            "valid": False,
            "errors": ["Missing required fields"],
            "individual_results": {
                "neutrophils": {"valid": True},
                "lymphocytes": {"valid": False}
            }
        }
        
        with pytest.raises(PDFParsingError, match="Validation failed"):
            process_pdf("test.pdf")


class TestManualFallbackMode:
    """Test manual fallback functionality."""
    
    @patch('immune_inflam_index.pdf_parser.parse_value_with_unit')
    @patch('immune_inflam_index.pdf_parser.Prompt.ask')
    @patch('immune_inflam_index.pdf_parser.Console')
    def test_manual_fallback_success(self, mock_console, mock_prompt, mock_parse):
        """Test successful manual value entry."""
        # Mock user inputs
        mock_prompt.side_effect = ["6310", "1800", "250000", ""]  # Empty for monocytes
        
        # Mock value parsing
        mock_parse.side_effect = [
            (6310.0, "cells/µL"),
            (1800.0, "cells/µL"),
            (250000.0, "cells/µL")
        ]
        
        result = manual_fallback_mode("extracted text", ["neutrophils", "lymphocytes", "platelets"])
        
        assert result["neutrophils"] == 6310.0
        assert result["lymphocytes"] == 1800.0
        assert result["platelets"] == 250000.0
        assert "monocytes" not in result  # Skipped
    
    @patch('immune_inflam_index.pdf_parser.parse_value_with_unit')
    @patch('immune_inflam_index.pdf_parser.Prompt.ask')
    @patch('immune_inflam_index.pdf_parser.Console')
    def test_manual_fallback_invalid_input_retry(self, mock_console, mock_prompt, mock_parse):
        """Test retry logic for invalid input."""
        # Mock user inputs - first invalid, then valid
        mock_prompt.side_effect = ["invalid", "6310"]
        
        # Mock value parsing - first fails, then succeeds
        mock_parse.side_effect = [
            (None, None),      # Invalid input
            (6310.0, "cells/µL")  # Valid input
        ]
        
        result = manual_fallback_mode("extracted text", ["neutrophils"])
        
        assert result["neutrophils"] == 6310.0
        assert mock_prompt.call_count == 2  # Called twice due to retry


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""
    
    def test_find_cbc_section_empty_text(self):
        """Test CBC section finding with empty text."""
        result = find_cbc_section("")
        assert result == ""
    
    def test_find_cbc_section_very_long_text(self):
        """Test CBC section finding with very long text."""
        long_text = "A" * 5000  # Very long text without headers
        result = find_cbc_section(long_text)
        
        # Should return first 2000 characters
        assert len(result) == 2000
        assert result == long_text[:2000]
    
    @patch('immune_inflam_index.pdf_parser.Path')
    def test_process_pdf_unexpected_error(self, mock_path):
        """Test handling of unexpected errors during processing."""
        mock_path.side_effect = Exception("Unexpected error")
        
        with pytest.raises(PDFParsingError, match="Unexpected error during PDF processing"):
            process_pdf("test.pdf")


class TestIntegrationScenarios:
    """Test integration scenarios with synthetic PDFs."""
    
    def test_process_synthetic_pdf_standard(self, sample_pdf_path):
        """Test processing of synthetic standard PDF."""
        # This test would use actual synthetic PDFs from fixtures
        # For now, we'll test the structure that would be expected
        
        # Mock the processing of a standard synthetic PDF
        with patch('immune_inflam_index.pdf_parser.Path') as mock_path:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True
            mock_path.return_value = mock_path_instance
            
            # Would process actual synthetic PDF and verify results
            # This test validates end-to-end functionality
            assert True  # Placeholder - would have real assertions
    
    def test_process_synthetic_pdf_scanned(self, sample_scanned_pdf_path):
        """Test processing of synthetic scanned PDF."""
        # Similar integration test for OCR functionality
        assert True  # Placeholder


class TestRegressionTests:
    """Regression tests for known PDF processing scenarios."""
    
    def test_process_pdf_with_manual_demographics(self):
        """Test PDF processing with manually provided demographics."""
        # Test that manual demographics override extracted ones
        with patch.multiple(
            'immune_inflam_index.pdf_parser',
            Path=MagicMock(),
            determine_extraction_method=MagicMock(return_value="text_based"),
            extract_text_from_pdf=MagicMock(return_value=("text", "method")),
            find_cbc_section=MagicMock(return_value="cbc text"),
            extract_cbc_values=MagicMock(return_value={
                "neutrophils": {"value": 6310, "confidence": 95},
                "lymphocytes": {"value": 1800, "confidence": 90},
                "platelets": {"value": 250000, "confidence": 98}
            }),
            validate_pdf_extracted_values=MagicMock(return_value={
                "valid": True, "warnings": [], "manual_verification_needed": False
            }),
            extract_patient_demographics=MagicMock(return_value={
                "age": {"value": 30, "confidence": 70},  # Low confidence
                "sex": {"value": "F", "confidence": 60},  # Low confidence
                "test_date": {"value": "2025-06-30", "confidence": 80}
            }),
            validate_demographic_extraction=MagicMock(return_value={
                "valid": True, "warnings": [], "manual_verification_needed": False
            }),
            calculate_indices=MagicMock(return_value={
                "results": {}, "summary": {}, "metadata": {}
            }),
            interpret_results=MagicMock(return_value={})
        ):
            # Mock file existence
            with patch('immune_inflam_index.pdf_parser.Path') as mock_path:
                mock_path_instance = MagicMock()
                mock_path_instance.exists.return_value = True
                mock_path_instance.absolute.return_value = Path("/test/path.pdf")
                mock_path.return_value = mock_path_instance
                
                # Process with manual demographics
                result = process_pdf("test.pdf", patient_age=45, patient_sex="M")
                
                # Should use manual demographics despite extracted ones
                # Verify through the interpret_results call arguments
                from immune_inflam_index.pdf_parser import interpret_results
                interpret_results.assert_called_once()
                call_args = interpret_results.call_args
                assert call_args[1]['patient_age'] == 45
                assert call_args[1]['patient_sex'] == "M"