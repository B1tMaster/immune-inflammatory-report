"""
PDF parsing functionality for extracting CBC values from blood test reports.
"""

import pdfplumber
import pytesseract
from PIL import Image
import re
import io
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

from .constants import FIELD_MAPPINGS, UNIT_CONVERSIONS, PDF_SECTION_HEADERS
from .extractor import extract_cbc_values, parse_value_with_unit
from .validator import validate_pdf_extracted_values


class PDFParsingError(Exception):
    """Custom exception for PDF parsing errors."""
    def __init__(self, message: str, extracted_text: str = "", missing_fields: List[str] = None):
        super().__init__(message)
        self.extracted_text = extracted_text
        self.missing_fields = missing_fields or []


def extract_text_from_pdf(pdf_path: str) -> Tuple[str, str]:
    """
    Extract text from PDF using pdfplumber.
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        Tuple of (extracted_text, extraction_method)
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text_content = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
            
            if text_content:
                return "\n".join(text_content), "text_based"
            else:
                # No text found, might need OCR
                return "", "text_based_failed"
    
    except Exception as e:
        raise PDFParsingError(f"Failed to extract text from PDF: {str(e)}")


def extract_text_with_ocr(pdf_path: str) -> Tuple[str, str]:
    """
    Extract text from PDF using OCR (for scanned PDFs).
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        Tuple of (extracted_text, extraction_method)
    """
    try:
        # Convert PDF pages to images and apply OCR
        with pdfplumber.open(pdf_path) as pdf:
            text_content = []
            for page in pdf.pages:
                # Convert page to image
                page_image = page.to_image()
                pil_image = page_image.original
                
                # Apply OCR
                ocr_text = pytesseract.image_to_string(pil_image)
                if ocr_text.strip():
                    text_content.append(ocr_text)
            
            if text_content:
                return "\n".join(text_content), "ocr"
            else:
                return "", "ocr_failed"
    
    except Exception as e:
        raise PDFParsingError(f"OCR extraction failed: {str(e)}")


def determine_extraction_method(pdf_path: str) -> str:
    """
    Determine the best extraction method for the PDF.
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        Extraction method: "text_based", "ocr", or "mixed"
    """
    try:
        text, method = extract_text_from_pdf(pdf_path)
        if text and len(text.strip()) > 100:  # Reasonable amount of text found
            return "text_based"
        else:
            return "ocr"  # Fall back to OCR
    except:
        return "ocr"


def find_cbc_section(text: str) -> str:
    """
    Find and extract the CBC/FBC section from the PDF text.
    
    Args:
        text: Full text extracted from PDF
    
    Returns:
        CBC section text
    """
    text_upper = text.upper()
    
    # Look for CBC section headers
    for header in PDF_SECTION_HEADERS:
        pattern = rf"{header}.*?(?=(?:{'|'.join(PDF_SECTION_HEADERS)})|$)"
        match = re.search(pattern, text_upper, re.DOTALL)
        if match:
            # Find the corresponding section in original text
            start_pos = text_upper.find(match.group())
            if start_pos != -1:
                # Look for end of section (next section header or end of text)
                end_pos = len(text)
                for next_header in ["KIDNEY", "LIVER", "LIPID", "VITAMIN", "CARDIAC"]:
                    next_pos = text_upper.find(next_header, start_pos + len(header))
                    if next_pos != -1 and next_pos < end_pos:
                        end_pos = next_pos
                
                return text[start_pos:end_pos]
    
    # If no specific section found, return first 2000 characters
    # (CBC is usually at the beginning)
    return text[:2000]


def process_pdf(
    pdf_file_path: str, 
    output_directory: Optional[str] = None,
    patient_age: Optional[int] = None,
    patient_sex: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main function to process a PDF blood test report.
    
    Args:
        pdf_file_path: Path to the PDF file
        output_directory: Directory to save results (optional)
        patient_age: Patient age for interpretation (optional)
        patient_sex: Patient sex (M/F) for interpretation (optional)
    
    Returns:
        Complete results including PDF parsing details and calculated indices
    """
    from .calculator import calculate_indices
    from .interpreter import interpret_results
    
    pdf_path = Path(pdf_file_path)
    if not pdf_path.exists():
        raise PDFParsingError(f"PDF file not found: {pdf_file_path}")
    
    results = {
        "pdf_parsing": {
            "extraction_method": "",
            "confidence_scores": {},
            "extracted_values": {},
            "parsing_warnings": [],
            "manual_verification_needed": False
        },
        "metadata": {
            "pdf_source": str(pdf_path.absolute()),
            "extraction_timestamp": "",
            "warnings": []
        }
    }
    
    try:
        # Determine and apply extraction method
        extraction_method = determine_extraction_method(pdf_file_path)
        results["pdf_parsing"]["extraction_method"] = extraction_method
        
        if extraction_method == "text_based":
            text, _ = extract_text_from_pdf(pdf_file_path)
        elif extraction_method == "ocr":
            text, _ = extract_text_with_ocr(pdf_file_path)
        else:
            # Try text first, fall back to OCR
            text, method = extract_text_from_pdf(pdf_file_path)
            if not text or len(text.strip()) < 100:
                text, _ = extract_text_with_ocr(pdf_file_path)
                results["pdf_parsing"]["extraction_method"] = "mixed"
        
        if not text:
            raise PDFParsingError(
                "No text could be extracted from PDF", 
                extracted_text="", 
                missing_fields=list(FIELD_MAPPINGS.keys())
            )
        
        # Extract CBC section
        cbc_section = find_cbc_section(text)
        
        # Extract CBC values
        extracted_values = extract_cbc_values(cbc_section)
        
        if not extracted_values:
            raise PDFParsingError(
                "No CBC values found in PDF",
                extracted_text=cbc_section[:1000],
                missing_fields=list(FIELD_MAPPINGS.keys())
            )
        
        # Validate extracted values
        validation_result = validate_pdf_extracted_values(extracted_values)
        
        results["pdf_parsing"]["extracted_values"] = extracted_values
        results["pdf_parsing"]["confidence_scores"] = {
            field: data.get("confidence", 0) 
            for field, data in extracted_values.items()
        }
        results["pdf_parsing"]["parsing_warnings"] = validation_result["warnings"]
        results["pdf_parsing"]["manual_verification_needed"] = validation_result["manual_verification_needed"]
        
        if not validation_result["valid"]:
            raise PDFParsingError(
                f"Validation failed: {validation_result['errors']}",
                extracted_text=cbc_section[:1000],
                missing_fields=[field for field, data in validation_result["individual_results"].items() 
                              if not data["valid"]]
            )
        
        # Extract numeric values for calculation
        neutrophils = extracted_values["neutrophils"]["value"]
        lymphocytes = extracted_values["lymphocytes"]["value"]
        platelets = extracted_values["platelets"]["value"]
        monocytes = extracted_values.get("monocytes", {}).get("value")
        
        # Calculate indices
        calculation_results = calculate_indices(neutrophils, lymphocytes, platelets, monocytes)
        
        # Merge results
        results.update(calculation_results)
        
        # Add interpretation with patient context
        if patient_age or patient_sex:
            interpretation = interpret_results(
                calculation_results["results"], 
                patient_age=patient_age, 
                patient_sex=patient_sex
            )
            results["interpretation"] = interpretation
        
        return results
        
    except PDFParsingError:
        raise  # Re-raise PDF parsing errors as-is
    except Exception as e:
        raise PDFParsingError(f"Unexpected error during PDF processing: {str(e)}")


def manual_fallback_mode(extracted_text: str, missing_fields: List[str]) -> Dict[str, float]:
    """
    Interactive fallback mode when PDF parsing fails.
    
    Args:
        extracted_text: Text that was extracted from PDF
        missing_fields: List of fields that couldn't be parsed
    
    Returns:
        Manually entered values
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    
    console = Console()
    
    console.print(Panel(
        "PDF parsing failed. Please review the extracted text and enter values manually.",
        title="Manual Input Required",
        style="yellow"
    ))
    
    if extracted_text:
        console.print(Panel(
            extracted_text[:1000] + ("..." if len(extracted_text) > 1000 else ""),
            title="Extracted Text (first 1000 characters)",
            style="dim"
        ))
    
    manual_values = {}
    
    # Define prompts for each field
    field_prompts = {
        "neutrophils": "Enter Neutrophil count (cells/µL or x10³/L)",
        "lymphocytes": "Enter Lymphocyte count (cells/µL or x10³/L)", 
        "platelets": "Enter Platelet count (cells/µL or x10³/L)",
        "monocytes": "Enter Monocyte count (cells/µL or x10³/L) [optional, press Enter to skip]"
    }
    
    required_fields = ["neutrophils", "lymphocytes", "platelets"]
    
    for field in required_fields + ["monocytes"]:
        if field in missing_fields or field == "monocytes":
            while True:
                try:
                    user_input = Prompt.ask(field_prompts[field])
                    
                    if field == "monocytes" and not user_input.strip():
                        break  # Skip optional field
                    
                    # Try to parse the value
                    value, _ = parse_value_with_unit(user_input)
                    if value is not None:
                        manual_values[field] = value
                        break
                    else:
                        console.print(f"[red]Invalid input. Please enter a numeric value.[/red]")
                
                except KeyboardInterrupt:
                    console.print("\n[red]Operation cancelled.[/red]")
                    raise
                except Exception as e:
                    console.print(f"[red]Error: {str(e)}[/red]")
    
    return manual_values