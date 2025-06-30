"""Integration tests for the complete PDF processing workflow."""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from immune_inflam_index.pdf_parser import process_pdf, PDFParsingError
from immune_inflam_index.calculator import calculate_indices
from immune_inflam_index.interpreter import interpret_results
from immune_inflam_index.reporter import save_results


class TestCompleteWorkflow:
    """Test the complete PDF to report workflow."""
    
    def test_synthetic_pdf_text_based_workflow(self, standard_pdf_with_values, temp_output_dir):
        """Test complete workflow with synthetic text-based PDF."""
        pdf_path, expected_values = standard_pdf_with_values
        
        # Process the PDF
        results = process_pdf(str(pdf_path), output_directory=str(temp_output_dir))
        
        # Verify PDF parsing results
        assert "pdf_parsing" in results
        assert results["pdf_parsing"]["extraction_method"] in ["text_based", "mixed"]
        assert "extracted_values" in results["pdf_parsing"]
        
        # Verify core calculations
        assert "results" in results
        assert "sii" in results["results"]
        assert "nlr" in results["results"]
        assert "plr" in results["results"]
        
        # Verify calculation values are reasonable
        sii_value = results["results"]["sii"]["value"]
        nlr_value = results["results"]["nlr"]["value"]
        plr_value = results["results"]["plr"]["value"]
        
        assert 100 <= sii_value <= 10000  # Reasonable SII range
        assert 0.5 <= nlr_value <= 50     # Reasonable NLR range
        assert 50 <= plr_value <= 1000    # Reasonable PLR range
        
        # Verify summary and metadata
        assert "summary" in results
        assert "metadata" in results
        assert results["metadata"]["pdf_source"] == str(pdf_path.absolute())
    
    @patch('immune_inflam_index.pdf_parser.extract_text_from_pdf')
    @patch('immune_inflam_index.pdf_parser.extract_text_with_ocr')
    def test_synthetic_pdf_ocr_workflow(self, mock_ocr, mock_text, scanned_pdf_with_values, temp_output_dir):
        """Test complete workflow with synthetic OCR-based PDF."""
        pdf_path, expected_values = scanned_pdf_with_values
        
        # Mock text extraction to simulate scanned PDF (low text content)
        mock_text.return_value = ("", "text_based_failed")
        
        # Mock OCR extraction with realistic medical text
        mock_ocr.return_value = (f"""
        LABORATORY REPORT
        Patient: John Doe
        Age: 58 Years Male
        
        COMPLETE BLOOD COUNT
        Neutrophils: {expected_values['neutrophils']:.0f} cells/µL
        Lymphocytes: {expected_values['lymphocytes']:.0f} cells/µL
        Platelets: {expected_values['platelets']:.0f} cells/µL
        Monocytes: {expected_values.get('monocytes', 480):.0f} cells/µL
        
        Collected: 03/15/2025
        """, "ocr")
        
        # Process the PDF
        results = process_pdf(str(pdf_path), output_directory=str(temp_output_dir))
        
        # Verify OCR was used
        assert results["pdf_parsing"]["extraction_method"] == "ocr"
        
        # Verify calculations were performed
        assert "results" in results
        assert all(index in results["results"] for index in ["sii", "nlr", "plr"])
        
        # Verify OCR called
        mock_ocr.assert_called_once()
    
    def test_workflow_with_patient_demographics(self, standard_pdf_with_values, temp_output_dir):
        """Test workflow with patient demographic extraction."""
        pdf_path, expected_values = standard_pdf_with_values
        
        # Process with patient demographics
        results = process_pdf(
            str(pdf_path), 
            output_directory=str(temp_output_dir),
            patient_age=45,
            patient_sex="M"
        )
        
        # Verify interpretation was added
        assert "interpretation" in results
        
        # Verify patient context
        if "patient_context" in results["interpretation"]:
            context = results["interpretation"]["patient_context"]
            # Should use provided demographics
            assert context.get("age") == 45
            assert context.get("sex") == "M"
    
    def test_workflow_with_report_generation(self, standard_pdf_with_values, temp_output_dir):
        """Test complete workflow including report generation."""
        pdf_path, expected_values = standard_pdf_with_values
        
        # Process PDF
        results = process_pdf(str(pdf_path), output_directory=str(temp_output_dir))
        
        # Generate reports in all formats
        report_files = []
        for format_type in ["pdf", "json", "text"]:
            report_path = save_results(results, str(temp_output_dir), format_type)
            report_files.append(Path(report_path))
            
            # Verify file was created
            assert Path(report_path).exists()
            assert Path(report_path).stat().st_size > 0
        
        # Verify JSON report content
        json_file = next(f for f in report_files if f.suffix == ".json")
        with open(json_file, 'r') as f:
            json_data = json.load(f)
            assert "results" in json_data
            assert "report_metadata" in json_data
            assert json_data["results"]["sii"]["value"] == results["results"]["sii"]["value"]
        
        # Verify text report content
        text_file = next(f for f in report_files if f.suffix == ".txt")
        with open(text_file, 'r') as f:
            text_content = f.read()
            assert "IMMUNE INFLAMMATORY INDEX REPORT" in text_content
            assert "SII:" in text_content
            assert "NLR:" in text_content


class TestWorkflowErrorHandling:
    """Test workflow error handling and recovery."""
    
    def test_workflow_with_missing_pdf(self, temp_output_dir):
        """Test workflow with missing PDF file."""
        with pytest.raises(PDFParsingError, match="PDF file not found"):
            process_pdf("nonexistent.pdf", output_directory=str(temp_output_dir))
    
    def test_workflow_with_corrupt_pdf(self, temp_output_dir):
        """Test workflow with corrupt PDF file."""
        # Create a fake PDF file with invalid content
        fake_pdf = temp_output_dir / "corrupt.pdf"
        fake_pdf.write_text("This is not a PDF file")
        
        with pytest.raises(PDFParsingError):
            process_pdf(str(fake_pdf), output_directory=str(temp_output_dir))
    
    @patch('immune_inflam_index.pdf_parser.extract_text_from_pdf')
    @patch('immune_inflam_index.pdf_parser.extract_text_with_ocr')
    def test_workflow_with_no_extractable_text(self, mock_ocr, mock_text, temp_output_dir):
        """Test workflow when no text can be extracted."""
        # Create a minimal PDF file
        test_pdf = temp_output_dir / "empty.pdf"
        test_pdf.write_bytes(b"%PDF-1.4\n%%EOF")  # Minimal PDF structure
        
        # Mock both extraction methods to fail
        mock_text.return_value = ("", "text_based_failed")
        mock_ocr.return_value = ("", "ocr_failed")
        
        with pytest.raises(PDFParsingError, match="No text could be extracted"):
            process_pdf(str(test_pdf), output_directory=str(temp_output_dir))
    
    @patch('immune_inflam_index.pdf_parser.extract_text_from_pdf')
    def test_workflow_with_no_cbc_values(self, mock_text, temp_output_dir):
        """Test workflow when no CBC values can be found."""
        # Create a minimal PDF file
        test_pdf = temp_output_dir / "no_cbc.pdf"
        test_pdf.write_bytes(b"%PDF-1.4\n%%EOF")
        
        # Mock text extraction with irrelevant content
        mock_text.return_value = ("This is a medical report but has no CBC values.", "text_based")
        
        with pytest.raises(PDFParsingError, match="No CBC values found"):
            process_pdf(str(test_pdf), output_directory=str(temp_output_dir))
    
    @patch('immune_inflam_index.pdf_parser.extract_text_from_pdf')
    def test_workflow_with_invalid_cbc_values(self, mock_text, temp_output_dir):
        """Test workflow with invalid CBC values."""
        # Create a minimal PDF file
        test_pdf = temp_output_dir / "invalid_cbc.pdf"
        test_pdf.write_bytes(b"%PDF-1.4\n%%EOF")
        
        # Mock text extraction with invalid CBC values
        mock_text.return_value = ("""
        COMPLETE BLOOD COUNT
        Neutrophils: -100 cells/µL
        Lymphocytes: 0 cells/µL
        Platelets: 999999999 cells/µL
        """, "text_based")
        
        with pytest.raises(PDFParsingError, match="Validation failed"):
            process_pdf(str(test_pdf), output_directory=str(temp_output_dir))


class TestWorkflowEdgeCases:
    """Test workflow edge cases and boundary conditions."""
    
    @patch('immune_inflam_index.pdf_parser.extract_text_from_pdf')
    def test_workflow_with_minimal_cbc_data(self, mock_text, temp_output_dir):
        """Test workflow with minimal CBC data (only required fields)."""
        # Create a minimal PDF file
        test_pdf = temp_output_dir / "minimal_cbc.pdf"
        test_pdf.write_bytes(b"%PDF-1.4\n%%EOF")
        
        # Mock text extraction with minimal CBC data
        mock_text.return_value = ("""
        COMPLETE BLOOD COUNT
        Neutrophils: 4200 cells/µL
        Lymphocytes: 1800 cells/µL
        Platelets: 250000 cells/µL
        """, "text_based")
        
        results = process_pdf(str(test_pdf), output_directory=str(temp_output_dir))
        
        # Should calculate SII, NLR, PLR but not SIRI, MLR, PIV (no monocytes)
        assert "sii" in results["results"]
        assert "nlr" in results["results"]
        assert "plr" in results["results"]
        assert "siri" not in results["results"]
        assert "mlr" not in results["results"]
        assert "piv" not in results["results"]
    
    @patch('immune_inflam_index.pdf_parser.extract_text_from_pdf')
    def test_workflow_with_boundary_values(self, mock_text, temp_output_dir):
        """Test workflow with boundary CBC values."""
        # Create a minimal PDF file
        test_pdf = temp_output_dir / "boundary_cbc.pdf"
        test_pdf.write_bytes(b"%PDF-1.4\n%%EOF")
        
        # Mock text extraction with boundary values
        mock_text.return_value = ("""
        COMPLETE BLOOD COUNT
        Neutrophils: 1 cells/µL
        Lymphocytes: 1 cells/µL
        Platelets: 1 cells/µL
        Monocytes: 1 cells/µL
        """, "text_based")
        
        results = process_pdf(str(test_pdf), output_directory=str(temp_output_dir))
        
        # Should handle boundary values without crashing
        assert "results" in results
        assert all(isinstance(results["results"][idx]["value"], (int, float)) 
                  for idx in results["results"])
    
    @patch('immune_inflam_index.pdf_parser.extract_text_from_pdf')
    def test_workflow_with_very_high_values(self, mock_text, temp_output_dir):
        """Test workflow with very high CBC values."""
        # Create a minimal PDF file
        test_pdf = temp_output_dir / "high_cbc.pdf"
        test_pdf.write_bytes(b"%PDF-1.4\n%%EOF")
        
        # Mock text extraction with very high values
        mock_text.return_value = ("""
        COMPLETE BLOOD COUNT
        Neutrophils: 50000 cells/µL
        Lymphocytes: 200 cells/µL
        Platelets: 1000000 cells/µL
        Monocytes: 5000 cells/µL
        """, "text_based")
        
        results = process_pdf(str(test_pdf), output_directory=str(temp_output_dir))
        
        # Should calculate extremely high indices
        assert results["results"]["sii"]["value"] > 10000  # Very high SII
        assert results["results"]["nlr"]["value"] > 200    # Very high NLR
        
        # Should classify as high risk
        assert any("high" in results["results"][idx]["risk_level"].lower() 
                  for idx in results["results"])
    
    @patch('immune_inflam_index.pdf_parser.extract_text_from_pdf')
    def test_workflow_with_unicode_content(self, mock_text, temp_output_dir):
        """Test workflow with Unicode characters in PDF content."""
        # Create a minimal PDF file
        test_pdf = temp_output_dir / "unicode_cbc.pdf"
        test_pdf.write_bytes(b"%PDF-1.4\n%%EOF")
        
        # Mock text extraction with Unicode characters
        mock_text.return_value = ("""
        LABORATÓRIO MÉDICO
        Paciente: José María
        
        COMPLETE BLOOD COUNT
        Neutrófilos: 4200 células/μL
        Linfócitos: 1800 células/μL
        Plaquetas: 250000 células/μL
        """, "text_based")
        
        results = process_pdf(str(test_pdf), output_directory=str(temp_output_dir))
        
        # Should handle Unicode content gracefully
        assert "results" in results
        assert "sii" in results["results"]


class TestWorkflowPerformance:
    """Test workflow performance characteristics."""
    
    def test_workflow_processing_speed(self, standard_pdf_with_values, temp_output_dir):
        """Test that workflow completes in reasonable time."""
        import time
        
        pdf_path, expected_values = standard_pdf_with_values
        
        start_time = time.time()
        results = process_pdf(str(pdf_path), output_directory=str(temp_output_dir))
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should complete within reasonable time (adjust based on system)
        assert processing_time < 30  # 30 seconds max
        
        # Verify results were produced
        assert "results" in results
        assert len(results["results"]) >= 3  # At least SII, NLR, PLR
    
    def test_workflow_memory_usage(self, standard_pdf_with_values, temp_output_dir):
        """Test workflow memory usage is reasonable."""
        import tracemalloc
        
        pdf_path, expected_values = standard_pdf_with_values
        
        tracemalloc.start()
        
        results = process_pdf(str(pdf_path), output_directory=str(temp_output_dir))
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Memory usage should be reasonable (adjust based on system)
        assert peak < 100 * 1024 * 1024  # Less than 100MB peak
        
        # Verify results were produced
        assert "results" in results
    
    def test_workflow_concurrent_processing(self, standard_pdf_with_values, temp_output_dir):
        """Test workflow can handle concurrent processing."""
        import concurrent.futures
        import tempfile
        
        pdf_path, expected_values = standard_pdf_with_values
        
        def process_single():
            with tempfile.TemporaryDirectory() as single_temp_dir:
                return process_pdf(str(pdf_path), output_directory=single_temp_dir)
        
        # Run multiple concurrent processes
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(process_single) for _ in range(3)]
            results_list = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All should succeed and produce consistent results
        assert len(results_list) == 3
        
        # Results should be consistent across runs
        sii_values = [r["results"]["sii"]["value"] for r in results_list]
        assert all(abs(val - sii_values[0]) < 0.01 for val in sii_values)


class TestWorkflowIntegrationScenarios:
    """Test realistic integration scenarios."""
    
    @patch('immune_inflam_index.pdf_parser.extract_text_from_pdf')
    def test_elderly_patient_scenario(self, mock_text, temp_output_dir):
        """Test workflow for elderly patient scenario."""
        # Create a minimal PDF file
        test_pdf = temp_output_dir / "elderly_patient.pdf"
        test_pdf.write_bytes(b"%PDF-1.4\n%%EOF")
        
        # Mock text extraction for elderly patient with elevated inflammation
        mock_text.return_value = ("""
        LABORATORY REPORT
        Patient: Margaret Smith
        Age: 78 Years Female
        Collected: 03/15/2025
        
        COMPLETE BLOOD COUNT
        Neutrophils: 8500 cells/µL
        Lymphocytes: 1200 cells/µL
        Platelets: 420000 cells/µL
        Monocytes: 650 cells/µL
        """, "text_based")
        
        results = process_pdf(str(test_pdf), output_directory=str(temp_output_dir))
        
        # Verify age-specific interpretation
        if "interpretation" in results and "patient_context" in results["interpretation"]:
            context = results["interpretation"]["patient_context"]
            assert context.get("age") == 78
            assert context.get("sex") == "F"
            
            # Should have age-specific considerations
            if "age_considerations" in context:
                considerations = context["age_considerations"]
                assert any("elderly" in str(cons).lower() or "age" in str(cons).lower() 
                          for cons in considerations)
    
    @patch('immune_inflam_index.pdf_parser.extract_text_from_pdf')
    def test_young_adult_scenario(self, mock_text, temp_output_dir):
        """Test workflow for young adult scenario."""
        # Create a minimal PDF file
        test_pdf = temp_output_dir / "young_adult.pdf"
        test_pdf.write_bytes(b"%PDF-1.4\n%%EOF")
        
        # Mock text extraction for young adult with normal values
        mock_text.return_value = ("""
        LABORATORY REPORT
        Patient: Alex Johnson
        Age: 25 Years Male
        Collected: 03/15/2025
        
        COMPLETE BLOOD COUNT
        Neutrophils: 4000 cells/µL
        Lymphocytes: 2200 cells/µL
        Platelets: 275000 cells/µL
        Monocytes: 450 cells/µL
        """, "text_based")
        
        results = process_pdf(str(test_pdf), output_directory=str(temp_output_dir))
        
        # Should indicate normal/low inflammatory state for young adult
        summary = results.get("summary", {})
        if "overall_inflammatory_status" in summary:
            status = summary["overall_inflammatory_status"].lower()
            assert any(word in status for word in ["normal", "low", "good"])
    
    @patch('immune_inflam_index.pdf_parser.extract_text_from_pdf')
    def test_critical_values_scenario(self, mock_text, temp_output_dir):
        """Test workflow with critical lab values."""
        # Create a minimal PDF file
        test_pdf = temp_output_dir / "critical_values.pdf"
        test_pdf.write_bytes(b"%PDF-1.4\n%%EOF")
        
        # Mock text extraction with critical values
        mock_text.return_value = ("""
        LABORATORY REPORT - CRITICAL VALUES
        Patient: Emergency Patient
        Age: 55 Years Male
        Collected: 03/15/2025
        
        COMPLETE BLOOD COUNT
        Neutrophils: 25000 cells/µL  *** CRITICAL HIGH ***
        Lymphocytes: 300 cells/µL     *** CRITICAL LOW ***
        Platelets: 50000 cells/µL     *** CRITICAL LOW ***
        Monocytes: 2000 cells/µL      *** HIGH ***
        """, "text_based")
        
        results = process_pdf(str(test_pdf), output_directory=str(temp_output_dir))
        
        # Should detect extremely high inflammatory indices
        assert results["results"]["sii"]["value"] > 5000  # Extremely high SII
        assert results["results"]["nlr"]["value"] > 50    # Extremely high NLR
        
        # Should classify as critical/high risk
        risk_levels = [results["results"][idx]["risk_level"] for idx in results["results"]]
        assert any("high" in level.lower() or "critical" in level.lower() for level in risk_levels)
        
        # Should have urgent recommendations if interpretation exists
        if "interpretation" in results and "risk_stratification" in results["interpretation"]:
            urgency = results["interpretation"]["risk_stratification"].get("urgency", "")
            assert "urgent" in urgency.lower() or "immediate" in urgency.lower() or urgency == "high_priority"


class TestWorkflowRegressionTests:
    """Regression tests for known workflow scenarios."""
    
    def test_regression_mixed_units_scenario(self, temp_output_dir):
        """Test regression for mixed unit formats."""
        with patch('immune_inflam_index.pdf_parser.extract_text_from_pdf') as mock_text:
            # Create a minimal PDF file
            test_pdf = temp_output_dir / "mixed_units.pdf"
            test_pdf.write_bytes(b"%PDF-1.4\n%%EOF")
            
            # Mock text with mixed unit formats (regression case)
            mock_text.return_value = ("""
            COMPLETE BLOOD COUNT
            Neutrophils: 6.31 x10³/L
            Lymphocytes: 1800 cells/µL
            Platelets: 250 x10³/L
            Monocytes: 0.48 x10³/L
            """, "text_based")
            
            results = process_pdf(str(test_pdf), output_directory=str(temp_output_dir))
            
            # Should handle mixed units correctly
            extracted = results["pdf_parsing"]["extracted_values"]
            assert 6000 <= extracted["neutrophils"]["value"] <= 7000   # 6.31 x10³/L
            assert 1700 <= extracted["lymphocytes"]["value"] <= 1900   # 1800 cells/µL
            assert 240000 <= extracted["platelets"]["value"] <= 260000 # 250 x10³/L
            assert 400 <= extracted["monocytes"]["value"] <= 500       # 0.48 x10³/L
    
    def test_regression_decimal_precision_scenario(self, temp_output_dir):
        """Test regression for decimal precision handling."""
        with patch('immune_inflam_index.pdf_parser.extract_text_from_pdf') as mock_text:
            # Create a minimal PDF file
            test_pdf = temp_output_dir / "decimal_precision.pdf"
            test_pdf.write_bytes(b"%PDF-1.4\n%%EOF")
            
            # Mock text with high precision values
            mock_text.return_value = ("""
            COMPLETE BLOOD COUNT
            Neutrophils: 6310.567 cells/µL
            Lymphocytes: 1800.123 cells/µL
            Platelets: 250000.789 cells/µL
            """, "text_based")
            
            results = process_pdf(str(test_pdf), output_directory=str(temp_output_dir))
            
            # Should preserve reasonable precision in calculations
            sii_value = results["results"]["sii"]["value"]
            assert isinstance(sii_value, (int, float))
            
            # SII calculation should be reasonable
            expected_sii = (6310.567 * 250000.789) / 1800.123
            assert abs(sii_value - expected_sii) < 10  # Allow for rounding differences
    
    def test_regression_demographic_extraction_scenario(self, temp_output_dir):
        """Test regression for demographic extraction edge cases."""
        with patch('immune_inflam_index.pdf_parser.extract_text_from_pdf') as mock_text:
            # Create a minimal PDF file
            test_pdf = temp_output_dir / "demographics_edge.pdf"
            test_pdf.write_bytes(b"%PDF-1.4\n%%EOF")
            
            # Mock text with edge case demographics
            mock_text.return_value = ("""
            LABORATORY REPORT
            Patient: Dr. F. Smith (Patient)
            Age: 58 Years Male (Patient age, not doctor)
            Emergency Contact: Jane Doe, 32 F
            
            COMPLETE BLOOD COUNT
            Neutrophils: 6310 cells/µL
            Lymphocytes: 1800 cells/µL
            Platelets: 250000 cells/µL
            
            Collected: 03/15/25
            Reported: 03/16/25
            """, "text_based")
            
            results = process_pdf(str(test_pdf), output_directory=str(temp_output_dir))
            
            # Should extract patient demographics, not contact demographics
            demographics = results["pdf_parsing"]["patient_demographics"]
            assert demographics["age"]["value"] == 58  # Patient age, not contact age
            assert demographics["sex"]["value"] == "M"  # Patient sex
            
            # Should prefer collected date over reported date
            assert demographics["test_date"]["value"] == "2025-03-15"