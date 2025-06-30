"""
Immune Inflammatory Index Calculator with PDF Parsing

This package provides a comprehensive calculator for multiple immune inflammatory 
indices derived from standard Complete Blood Count (CBC) with differential blood tests.
Features automatic PDF parsing capabilities to extract blood test values from 
laboratory reports.
"""

from .calculator import calculate_indices
from .pdf_parser import process_pdf
from .validator import validate_inputs
from .interpreter import interpret_results
from .reporter import generate_report, save_results
from .demographic_extractor import extract_patient_demographics

__version__ = "1.0.0"
__author__ = "Immune Inflammatory Index Project"

__all__ = [
    "calculate_indices",
    "process_pdf", 
    "validate_inputs",
    "interpret_results",
    "generate_report",
    "save_results",
    "extract_patient_demographics",
]