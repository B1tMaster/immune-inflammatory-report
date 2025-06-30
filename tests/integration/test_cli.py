"""Integration tests for the CLI module."""

import pytest
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from immune_inflam_index.cli import main


class TestCLIBasicFunctionality:
    """Test basic CLI functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
        
    def test_cli_help_command(self):
        """Test CLI help command."""
        result = self.runner.invoke(main, ["--help"])
        
        assert result.exit_code == 0
        assert "Immune Inflammatory Index Calculator" in result.output
        assert "process-pdf-cmd" in result.output
        assert "manual-input" in result.output
    
    def test_cli_version_command(self):
        """Test CLI version command."""
        result = self.runner.invoke(main, ["--version"])
        
        assert result.exit_code == 0
        # Version should be displayed
        assert any(char.isdigit() for char in result.output)


class TestManualInputCommand:
    """Test the manual-input command."""
    
    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
    
    def test_manual_input_basic_values(self):
        """Test manual-input command with basic values."""
        result = self.runner.invoke(main, [
            "manual-input",
            "--neutrophils", "6310",
            "--lymphocytes", "1800", 
            "--platelets", "250000"
        ])
        
        assert result.exit_code == 0
        assert "SII" in result.output
        assert "NLR" in result.output
        assert "PLR" in result.output
    
    def test_manual_input_with_monocytes(self):
        """Test manual-input command including monocytes."""
        result = self.runner.invoke(main, [
            "manual-input",
            "--neutrophils", "6310",
            "--lymphocytes", "1800",
            "--platelets", "250000",
            "--monocytes", "480"
        ])
        
        assert result.exit_code == 0
        assert "SII" in result.output
        assert "NLR" in result.output
        assert "PLR" in result.output
        assert "SIRI" in result.output
        assert "MLR" in result.output
        assert "PIV" in result.output
    
    def test_manual_input_with_patient_context(self):
        """Test manual-input command with patient demographics."""
        result = self.runner.invoke(main, [
            "manual-input",
            "--neutrophils", "6310",
            "--lymphocytes", "1800",
            "--platelets", "250000",
            "--patient-age", "45",
            "--patient-sex", "M"
        ])
        
        assert result.exit_code == 0
        assert "SII" in result.output
    
    def test_manual_input_invalid_values(self):
        """Test manual-input command with invalid values."""
        result = self.runner.invoke(main, [
            "manual-input",
            "--neutrophils", "-100",  # Invalid negative value
            "--lymphocytes", "1800",
            "--platelets", "250000"
        ])
        
        assert result.exit_code != 0
    
    def test_manual_input_missing_required_values(self):
        """Test manual-input command with missing required values."""
        result = self.runner.invoke(main, [
            "manual-input",
            "--neutrophils", "6310"
            # Missing lymphocytes and platelets
        ])
        
        assert result.exit_code != 0
    
    def test_manual_input_save_to_file(self):
        """Test manual-input command saving to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(main, [
                "manual-input",
                "--neutrophils", "6310",
                "--lymphocytes", "1800",
                "--platelets", "250000",
                "--output-dir", temp_dir,
                "--format", "json"
            ])
            
            assert result.exit_code == 0
            
            # Check that file was created
            output_files = list(Path(temp_dir).glob("*.json"))
            assert len(output_files) == 1


class TestProcessPdfCommand:
    """Test the process-pdf-cmd command."""
    
    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
    
    def test_process_pdf_missing_file(self):
        """Test process-pdf-cmd with non-existent file."""
        result = self.runner.invoke(main, [
            "process-pdf-cmd",
            "nonexistent.pdf"
        ])
        
        assert result.exit_code != 0
    
    @patch('immune_inflam_index.cli.process_pdf')
    def test_process_pdf_basic(self, mock_process):
        """Test basic PDF processing."""
        # Mock successful processing
        mock_process.return_value = {
            "results": {
                "sii": {"value": 877.8, "risk_level": "normal"},
                "nlr": {"value": 3.5, "risk_level": "mild"}
            },
            "summary": {"overall_inflammatory_status": "Normal"},
            "pdf_parsing": {"extraction_method": "text_based", "manual_verification_needed": False}
        }
        
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"fake pdf content")
            temp_file_path = temp_file.name
        
        try:
            result = self.runner.invoke(main, [
                "process-pdf-cmd",
                temp_file_path
            ])
            
            assert result.exit_code == 0
            mock_process.assert_called_once()
        finally:
            os.unlink(temp_file_path)
    
    @patch('immune_inflam_index.cli.process_pdf')
    def test_process_pdf_with_output_directory(self, mock_process):
        """Test PDF processing with output directory."""
        mock_process.return_value = {
            "results": {"sii": {"value": 877.8, "risk_level": "normal"}},
            "summary": {"overall_inflammatory_status": "Normal"},
            "pdf_parsing": {"extraction_method": "text_based", "manual_verification_needed": False}
        }
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"fake pdf content")
            temp_file_path = temp_file.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                result = self.runner.invoke(main, [
                    "process-pdf-cmd",
                    temp_file_path,
                    "--output-dir", temp_dir
                ])
                
                assert result.exit_code == 0
                mock_process.assert_called_once()
            finally:
                os.unlink(temp_file_path)
    
    @patch('immune_inflam_index.cli.process_pdf')
    def test_process_pdf_with_patient_context(self, mock_process):
        """Test PDF processing with patient demographics."""
        mock_process.return_value = {
            "results": {"sii": {"value": 877.8, "risk_level": "normal"}},
            "summary": {"overall_inflammatory_status": "Normal"},
            "pdf_parsing": {"extraction_method": "text_based", "manual_verification_needed": False}
        }
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"fake pdf content")
            temp_file_path = temp_file.name
        
        try:
            result = self.runner.invoke(main, [
                "process-pdf-cmd",
                temp_file_path,
                "--patient-age", "45",
                "--patient-sex", "M"
            ])
            
            assert result.exit_code == 0
            # Check that the function was called with the correct arguments
            args, kwargs = mock_process.call_args
            assert kwargs['patient_age'] == 45
            assert kwargs['patient_sex'] == 'M'
        finally:
            os.unlink(temp_file_path)


class TestInterpretCommand:
    """Test the interpret command."""
    
    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
    
    def test_interpret_without_guide(self):
        """Test interpret command without guide flag."""
        result = self.runner.invoke(main, ["interpret"])
        
        assert result.exit_code == 0
        assert "Use --guide flag" in result.output
    
    def test_interpret_with_guide(self):
        """Test interpret command with guide flag."""
        result = self.runner.invoke(main, ["interpret", "--guide"])
        
        assert result.exit_code == 0
        # Should show interpretation guide content


class TestSupportedFormatsCommand:
    """Test the supported-formats command."""
    
    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
    
    def test_supported_formats(self):
        """Test supported-formats command."""
        result = self.runner.invoke(main, ["supported-formats"])
        
        assert result.exit_code == 0
        assert "Supported Laboratory Formats" in result.output
        assert "Neutrophils" in result.output
        assert "Lymphocytes" in result.output


class TestCLIErrorHandling:
    """Test CLI error handling."""
    
    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
    
    def test_invalid_command(self):
        """Test invalid command handling."""
        result = self.runner.invoke(main, ["invalid-command"])
        
        assert result.exit_code != 0
    
    def test_invalid_sex_parameter(self):
        """Test invalid sex parameter."""
        result = self.runner.invoke(main, [
            "manual-input",
            "--neutrophils", "6310",
            "--lymphocytes", "1800",
            "--platelets", "250000",
            "--patient-sex", "X"  # Invalid sex
        ])
        
        assert result.exit_code != 0
    
    def test_invalid_format_parameter(self):
        """Test invalid format parameter."""
        result = self.runner.invoke(main, [
            "manual-input",
            "--neutrophils", "6310",
            "--lymphocytes", "1800",
            "--platelets", "250000",
            "--format", "invalid"  # Invalid format
        ])
        
        assert result.exit_code != 0


class TestCLIOutputQuality:
    """Test CLI output quality and formatting."""
    
    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
    
    def test_manual_input_output_formatting(self):
        """Test that manual-input output is well-formatted."""
        result = self.runner.invoke(main, [
            "manual-input",
            "--neutrophils", "6310",
            "--lymphocytes", "1800",
            "--platelets", "250000",
            "--patient-age", "45",
            "--patient-sex", "M"
        ])
        
        assert result.exit_code == 0
        
        # Check for proper formatting
        output_text = result.output
        assert "SII" in output_text
        assert "NLR" in output_text
        assert "PLR" in output_text
    
    @patch('immune_inflam_index.cli.process_pdf')
    def test_process_pdf_output_formatting(self, mock_process):
        """Test process-pdf output formatting."""
        mock_process.return_value = {
            "results": {
                "sii": {"value": 877.8, "risk_level": "normal", "interpretation": "Normal inflammation"},
                "nlr": {"value": 3.5, "risk_level": "mild", "interpretation": "Mild elevation"}
            },
            "summary": {"overall_inflammatory_status": "Normal inflammatory state"},
            "pdf_parsing": {
                "extraction_method": "text_based",
                "confidence_scores": {"neutrophils": 95, "lymphocytes": 90},
                "manual_verification_needed": False
            },
            "metadata": {"pdf_source": "test.pdf"}
        }
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"fake pdf content")
            temp_file_path = temp_file.name
        
        try:
            result = self.runner.invoke(main, [
                "process-pdf-cmd",
                temp_file_path
            ])
            
            assert result.exit_code == 0
            
            # Check for comprehensive output
            output_text = result.output
            assert "SII" in output_text
            assert "NLR" in output_text
            assert "877.8" in output_text
            assert "3.5" in output_text
        finally:
            os.unlink(temp_file_path)


class TestCLIIntegrationScenarios:
    """Test realistic CLI usage scenarios."""
    
    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
    
    def test_normal_inflammatory_state_workflow(self):
        """Test workflow for normal inflammatory state."""
        result = self.runner.invoke(main, [
            "manual-input",
            "--neutrophils", "4200",  # Normal values
            "--lymphocytes", "1800",
            "--platelets", "250000",
            "--monocytes", "480",
            "--patient-age", "35",
            "--patient-sex", "F"
        ])
        
        assert result.exit_code == 0
        
        # Should indicate normal/low risk
        output_lower = result.output.lower()
        assert any(word in output_lower for word in ["normal", "low"])
    
    def test_elevated_inflammatory_state_workflow(self):
        """Test workflow for elevated inflammatory state."""
        result = self.runner.invoke(main, [
            "manual-input",
            "--neutrophils", "12000",  # Elevated values
            "--lymphocytes", "800",    # Low lymphocytes
            "--platelets", "450000",   # Elevated platelets
            "--patient-age", "65",
            "--patient-sex", "M"
        ])
        
        assert result.exit_code == 0
        
        # Should indicate elevated risk
        output_lower = result.output.lower()
        assert any(word in output_lower for word in ["elevated", "high", "moderate"])
    
    def test_batch_processing_scenario(self):
        """Test scenario simulating batch processing."""
        test_cases = [
            ("4200", "1800", "250000", None),
            ("8000", "1200", "350000", "600"),
            ("3500", "2200", "180000", "400"),
        ]
        
        for neutrophils, lymphocytes, platelets, monocytes in test_cases:
            cmd = [
                "manual-input",
                "--neutrophils", neutrophils,
                "--lymphocytes", lymphocytes,
                "--platelets", platelets,
                "--format", "text"
            ]
            
            if monocytes:
                cmd.extend(["--monocytes", monocytes])
            
            result = self.runner.invoke(main, cmd)
            
            assert result.exit_code == 0
            
            # Verify output contains expected indices
            assert "SII" in result.output


class TestCLIRegressionTests:
    """Regression tests for known CLI scenarios."""
    
    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
    
    def test_known_calculation_scenario_1(self):
        """Test known calculation scenario 1."""
        # Test case that previously caused issues
        result = self.runner.invoke(main, [
            "manual-input",
            "--neutrophils", "15000",  # Very high
            "--lymphocytes", "500",    # Very low
            "--platelets", "100000",   # Low normal
            "--patient-age", "75",
            "--patient-sex", "M"
        ])
        
        assert result.exit_code == 0
        
        # Should handle extreme values gracefully
        output = result.output
        assert "SII" in output
        assert "NLR" in output
    
    def test_boundary_value_scenario(self):
        """Test boundary value scenario."""
        # Test minimum valid values
        result = self.runner.invoke(main, [
            "manual-input",
            "--neutrophils", "1",
            "--lymphocytes", "1", 
            "--platelets", "1"
        ])
        
        # Should either work or give clear error message
        assert result.exit_code == 0 or "error" in result.output.lower()
    
    def test_unicode_handling_in_output(self):
        """Test Unicode character handling in output."""
        result = self.runner.invoke(main, [
            "manual-input",
            "--neutrophils", "6310",
            "--lymphocytes", "1800",
            "--platelets", "250000"
        ])
        
        assert result.exit_code == 0
        
        # Should handle Unicode characters in output (e.g., μL)
        # The output might contain medical units with Unicode
        output_bytes = result.output.encode('utf-8')
        assert len(output_bytes) > 0  # Should not crash on encoding