"""Pytest configuration and shared fixtures for immune-inflam-index tests."""

import pytest
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, date
import tempfile
import os

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "fixtures"
SAMPLE_PDFS_DIR = TEST_DATA_DIR / "sample_pdfs"
EXPECTED_OUTPUTS_DIR = TEST_DATA_DIR / "expected_outputs"


@pytest.fixture
def sample_blood_values() -> Dict[str, float]:
    """Standard blood test values for testing."""
    return {
        "neutrophils": 4200.0,
        "lymphocytes": 1800.0,
        "platelets": 250000.0,
        "monocytes": 480.0,
    }


@pytest.fixture
def sample_blood_values_high_inflammation() -> Dict[str, float]:
    """Blood values indicating high inflammation."""
    return {
        "neutrophils": 8500.0,
        "lymphocytes": 1200.0,
        "platelets": 450000.0,
        "monocytes": 800.0,
    }


@pytest.fixture
def sample_blood_values_low_inflammation() -> Dict[str, float]:
    """Blood values indicating low inflammation."""
    return {
        "neutrophils": 2500.0,
        "lymphocytes": 2800.0,
        "platelets": 180000.0,
        "monocytes": 300.0,
    }


@pytest.fixture
def sample_patient_demographics() -> Dict[str, Any]:
    """Standard patient demographics for testing."""
    return {
        "age": 35,
        "sex": "M",
        "test_date": date(2025, 6, 30),
    }


@pytest.fixture
def young_female_patient() -> Dict[str, Any]:
    """Young female patient demographics."""
    return {
        "age": 24,
        "sex": "F",
        "test_date": date(2025, 6, 30),
    }


@pytest.fixture
def elderly_male_patient() -> Dict[str, Any]:
    """Elderly male patient demographics."""
    return {
        "age": 72,
        "sex": "M",
        "test_date": date(2025, 6, 30),
    }


@pytest.fixture
def middle_aged_female_patient() -> Dict[str, Any]:
    """Middle-aged female patient demographics."""
    return {
        "age": 52,
        "sex": "F",
        "test_date": date(2025, 6, 30),
    }


@pytest.fixture
def temp_output_dir() -> Path:
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_pdf_path() -> Path:
    """Path to a sample PDF file for testing."""
    return SAMPLE_PDFS_DIR / "standard_lab_report.pdf"


@pytest.fixture
def standard_pdf_with_values(sample_blood_values) -> tuple:
    """Standard PDF file with known blood values for testing."""
    pdf_path = SAMPLE_PDFS_DIR / "standard_lab_report.pdf" 
    # Return tuple of (path, expected_values)
    return (pdf_path, sample_blood_values)


@pytest.fixture
def scanned_pdf_with_values(sample_blood_values_high_inflammation) -> tuple:
    """Scanned PDF file with known blood values for testing."""
    pdf_path = SAMPLE_PDFS_DIR / "scanned_lab_report.pdf"
    # Return tuple of (path, expected_values) 
    return (pdf_path, sample_blood_values_high_inflammation)


@pytest.fixture
def sample_scanned_pdf_path() -> Path:
    """Path to a sample scanned PDF file for testing."""
    return SAMPLE_PDFS_DIR / "scanned_lab_report.pdf"


@pytest.fixture
def sample_multipage_pdf_path() -> Path:
    """Path to a sample multi-page PDF file for testing."""
    return SAMPLE_PDFS_DIR / "multipage_lab_report.pdf"


@pytest.fixture
def invalid_pdf_path() -> Path:
    """Path to an invalid PDF file for testing."""
    return SAMPLE_PDFS_DIR / "invalid_file.pdf"


@pytest.fixture
def expected_normal_report() -> str:
    """Expected output for normal inflammatory values."""
    return (EXPECTED_OUTPUTS_DIR / "normal_report.txt").read_text()


@pytest.fixture
def expected_high_inflammation_report() -> str:
    """Expected output for high inflammatory values."""
    return (EXPECTED_OUTPUTS_DIR / "high_inflammation_report.txt").read_text()


@pytest.fixture
def mock_current_datetime():
    """Mock current datetime for consistent test reports."""
    return datetime(2025, 6, 30, 14, 30, 0)


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment with necessary directories."""
    # Ensure test data directories exist
    TEST_DATA_DIR.mkdir(exist_ok=True)
    SAMPLE_PDFS_DIR.mkdir(exist_ok=True)
    EXPECTED_OUTPUTS_DIR.mkdir(exist_ok=True)
    
    # Set test environment variables
    os.environ["TESTING"] = "1"
    
    yield
    
    # Cleanup
    if "TESTING" in os.environ:
        del os.environ["TESTING"]