# Immune Inflammatory Index (III) Calculator with PDF Parsing - Technical Specification

## Project Overview

This Python project provides a comprehensive calculator for multiple immune inflammatory indices derived from standard Complete Blood Count (CBC) with differential blood tests. The tool features automatic PDF parsing capabilities to extract blood test values from laboratory reports, eliminating manual data entry. Based on research referenced by Dr. Jeff Bland and extensive clinical literature, these indices serve as cost-effective biomarkers for assessing systemic inflammation and immune system status.

## Background

The immune inflammatory indices are simple mathematical calculations using routine blood test parameters that provide insights into immune system health and inflammatory burden. These calculations were highlighted by Dr. Jeff Bland's research referencing Danish studies showing that values above certain thresholds indicate inflammatory states associated with various diseases.

## Supported Indices

### 1. Systemic Immune-Inflammation Index (SII)
- **Formula**: `SII = (Neutrophils × Platelets) / Lymphocytes`
- **Input Units**: All values must be in ×10⁹/L (equivalent to cells/µL ÷ 1000)
- **Output Units**: ×10⁹/L (dimensionless when properly normalized)
- **Clinical Significance**: Most comprehensive index reflecting balance between inflammatory and immune status
- **Literature Sources**: 
  - Karaaslan et al. "Predictive Value of Systemic Immune-inflammation Index in Determining Mortality in COVID-19 Patients" (2022)
  - Multiple validation studies across cardiovascular disease, cancer, and inflammatory conditions

### 2. Neutrophil-to-Lymphocyte Ratio (NLR)
- **Formula**: `NLR = Neutrophils / Lymphocytes`
- **Units**: Dimensionless ratio
- **Clinical Significance**: Indicates subclinical inflammation; elevated values suggest immune system activation

### 3. Platelet-to-Lymphocyte Ratio (PLR)
- **Formula**: `PLR = Platelets / Lymphocytes`
- **Units**: Dimensionless ratio
- **Clinical Significance**: Reflects thrombotic and inflammatory burden

### 4. Systemic Inflammatory Response Index (SIRI)
- **Formula**: `SIRI = (Neutrophils × Monocytes) / Lymphocytes`
- **Units**: Dimensionless ratio
- **Clinical Significance**: Incorporates monocyte response for comprehensive inflammatory assessment

### 5. Monocyte-to-Lymphocyte Ratio (MLR)
- **Formula**: `MLR = Monocytes / Lymphocytes`
- **Units**: Dimensionless ratio
- **Clinical Significance**: Reflects monocyte activation and tissue inflammation

### 6. Pan-Immune Inflammation Value (PIV)
- **Formula**: `PIV = (Neutrophils × Monocytes × Platelets) / Lymphocytes`
- **Units**: Dimensionless ratio
- **Clinical Significance**: Comprehensive assessment incorporating all major inflammatory cell types

## Critical Unit Conversion Requirements

**RESEARCH FINDINGS (December 2024)**: Initial implementation had a critical 1000x calculation error due to incorrect unit handling. **FIXED**: Commit 5913c21 corrected unit conversion.

### Formula Units (Based on Literature Review)
All immune inflammatory index formulas expect blood cell counts in **×10⁹/L** units, not raw cells/µL:

- **Standard Lab Report Units**: cells/µL (microliters)
- **Formula Calculation Units**: ×10⁹/L (10^9 cells per liter)
- **Conversion Factor**: cells/µL ÷ 1000 = ×10⁹/L

### Unit Conversion Examples
From sample PDF analysis (Innoquest Diagnostics):
```
Raw PDF Values:
- Neutrophils: 6.31 xIO^/L → 6,310 cells/µL → 6.31 ×10⁹/L
- Lymphocytes: 1.66 xIOS/L → 1,660 cells/µL → 1.66 ×10⁹/L  
- Platelets: 181 x10®/L → 181,000 cells/µL → 181.0 ×10⁹/L

Correct SII Calculation:
SII = (6.31 × 181.0) / 1.66 = 688.0 ×10⁹/L (Mild elevation)

Wrong Calculation (pre-fix):
SII = (6,310 × 181,000) / 1,660 = 688,018.1 (Incorrectly flagged as "Very High")
```

## Evidence-Based Reference Ranges

### SII (Systemic Immune-Inflammation Index)
**Literature Sources:**
- Karaaslan et al. (2022) - COVID-19 study: cutoff 618.8
- Cancer studies: cutoffs 390-410 ×10⁹/L
- Healthy population studies: median ~759 ×10⁹/L
- Cardiovascular mortality study: cutoffs 335.36-655.56

**Implemented Ranges:**
- Normal: 0-500 ×10⁹/L
- Mild: 500-800 ×10⁹/L  
- Moderate: 800-1,200 ×10⁹/L
- High: 1,200-2,000 ×10⁹/L
- Very High: >2,000 ×10⁹/L

### Supporting References
- BMC Pulmonary Medicine studies on COPD populations
- European Journal of Medical Research - general population mortality
- Scientific Reports - sarcopenia associations
- Multiple cancer prognosis validation studies

## Age-Specific Clinical Significance

**ENHANCED REQUIREMENT**: The system must provide age-appropriate clinical interpretation and recommendations.

### Age Group Classifications
- **Young Adults (18-35)**: Focus on acute inflammatory conditions, lifestyle factors
- **Middle-aged Adults (35-65)**: Consider early inflammaging, cardiovascular risk factors  
- **Elderly (65+)**: Account for baseline inflammatory elevation, immunosenescence

### Age-Specific Considerations by Group

#### Young Adults (18-35 years)
- **Clinical Focus**: Acute inflammatory conditions, infections, autoimmune diseases
- **Baseline Expectations**: Lower baseline inflammatory markers
- **Key Considerations**:
  - Elevated indices more likely to indicate acute pathology
  - Consider lifestyle factors (stress, diet, exercise)
  - Evaluate for underlying autoimmune conditions
  - Monitor for infection or acute inflammatory processes

#### Middle-aged Adults (35-65 years)  
- **Clinical Focus**: Early inflammaging, cardiovascular risk, metabolic syndrome
- **Baseline Expectations**: Gradual increase in inflammatory burden
- **Key Considerations**:
  - "Middle-aged adults may show early signs of inflammaging"
  - "Consider screening for age-related inflammatory conditions"
  - Cardiovascular risk factor assessment becomes critical
  - Metabolic syndrome and insulin resistance considerations
  - Cancer screening implications for persistently elevated indices

#### Elderly Adults (65+ years)
- **Clinical Focus**: Immunosenescence, frailty, chronic disease management
- **Baseline Expectations**: Higher baseline inflammatory markers are normal
- **Key Considerations**:
  - "Elderly patients may have baseline elevation in inflammatory markers" 
  - "Consider age-related immunosenescence effects"
  - "Higher risk for inflammatory complications"
  - Adjust thresholds for clinical significance
  - Focus on functional status and quality of life

### Sex-Specific Considerations

#### Female Patients
- **Key Factors**: "Women have higher baseline risk for autoimmune conditions"
- **Additional Considerations**:
  - "Hormonal fluctuations may affect inflammatory markers"
  - "Consider pregnancy, menstrual cycle, and menopause effects"
  - Higher prevalence of autoimmune diseases (RA, SLE, thyroid)
  - Estrogen effects on inflammatory pathways

#### Male Patients  
- **Key Factors**: "Men may have higher baseline inflammatory burden"
- **Additional Considerations**:
  - "Consider cardiovascular risk factors"
  - Higher risk for cardiovascular disease at younger ages
  - Different inflammatory patterns compared to females
  - Occupational and lifestyle risk factors

### Implementation Requirements
1. **Automatic Age Detection**: Extract patient age from PDF reports
2. **Age-Adjusted Interpretation**: Provide age-appropriate clinical context
3. **Targeted Recommendations**: Customize recommendations based on age group
4. **Risk Stratification**: Consider age in overall risk assessment
5. **Documentation**: Include age-specific considerations in all reports

## Input Methods

The tool supports two input methods:

### Method 1: PDF File Input (Recommended)
- **pdf_file_path**: `str` - Path to blood test PDF report
- Automatically extracts CBC values using advanced PDF parsing
- Supports multiple laboratory formats and layouts
- Provides confidence scores for extracted values
- Falls back to manual entry if parsing fails

### Method 2: Manual Input Parameters
All input values should be provided as absolute counts (cells per microliter) from CBC with differential. 
**CRITICAL**: Values will be automatically converted to ×10⁹/L for proper formula calculation (cells/µL ÷ 1000 = ×10⁹/L):

#### Required Parameters:
- **neutrophils**: `float` - Absolute neutrophil count (cells/µL)
- **lymphocytes**: `float` - Absolute lymphocyte count (cells/µL)
- **platelets**: `float` - Platelet count (cells/µL)

#### Optional Parameters:
- **monocytes**: `float` - Absolute monocyte count (cells/µL) [required for SIRI, MLR, PIV]

### Additional Metadata (Both Methods):
- **patient_age**: `int` - Patient age in years (optional, for age-adjusted interpretation)
- **patient_sex**: `str` - Patient sex ("M"/"F") (optional, for sex-adjusted interpretation)
- **test_date**: `str` - Date of blood test in ISO format (YYYY-MM-DD)
- **output_directory**: `str` - Directory to save results and reports

## PDF Parsing Specifications

### Supported PDF Types
1. **Text-based PDFs**: Direct text extraction using pdfplumber
2. **Scanned PDFs**: OCR extraction using pytesseract + Tesseract OCR
3. **Mixed PDFs**: Combination of text and image elements

### Laboratory Format Support
Based on analysis of sample PDF (Innoquest Diagnostics, Singapore), the parser supports:
- **Innoquest Diagnostics**: Singapore-based laboratory format
- **Generic CBC formats**: Common laboratory report layouts
- **Extensible parsing**: Modular design for adding new lab formats

### Extraction Methodology

#### Text Pattern Recognition
The parser uses multiple strategies to locate CBC values:

1. **Section-based parsing**: Identifies "FBC", "CBC", "HAEMATOLOGY" sections
2. **Field name matching**: Supports variations like:
   - Neutrophils: "Neutrophils", "Neutrophil", "Segs", "Segmented Neutrophils", "PMN"
   - Lymphocytes: "Lymphocytes", "Lymphocyte", "Lymphs"
   - Platelets: "Platelets", "Platelet", "PLT"
   - Monocytes: "Monocytes", "Monocyte", "Monos"

3. **Value extraction patterns**: Recognizes formats like:
   - `6.31 x10³/L`
   - `6.31 x10^3/L`
   - `6310 cells/µL`
   - `6.31 K/µL`
   - `6.31 (1.60-6.90)`

4. **Unit conversion**: Automatically converts between:
   - cells/µL ↔ x10³/L ↔ K/µL
   - Handles scientific notation variations

5. **Patient demographic extraction**: Automatically extracts patient information:
   - Age: "58 Years Male", "Age: 45", "45 yo", "45 y.o."
   - Sex: "Male", "Female", "M", "F" 
   - Test date: "Collected: 03/03/25", "Date: 2025-03-03"

#### Patient Demographic Patterns
The parser recognizes these demographic patterns:
- **Age patterns**:
  - `(\d+)\s*[Yy]ears?\s*([Mm]ale|[Ff]emale)` → "58 Years Male"
  - `[Aa]ge[:\s]*(\d+)` → "Age: 58"  
  - `(\d+)\s*[Yy]\.?[Oo]\.?` → "58 yo", "58 y.o."
  - `(\d+)\s*([Mm]|[Ff]|[Mm]ale|[Ff]emale)` → "58 M"

- **Sex patterns**:
  - `([Mm]ale|[Ff]emale)` → "Male", "Female"
  - `\b([MF])\b` → "M", "F"
  - Context-based extraction from age lines

- **Date patterns**:
  - `[Cc]ollected[:\s]*(\d{2}/\d{2}/\d{2,4})` → "Collected: 03/03/25"
  - `[Dd]ate[:\s]*(\d{4}-\d{2}-\d{2})` → "Date: 2025-03-03"
  - `[Rr]eported[:\s]*(\d{2}/\d{2}/\d{2,4})` → "Reported: 03/03/25"

#### Confidence Scoring
Each extracted value receives a confidence score (0-100):
- **90-100**: Exact pattern match with clear field identification
- **70-89**: Good pattern match with minor ambiguities
- **50-69**: Probable match requiring validation
- **0-49**: Low confidence, manual review required

#### Error Handling and Fallback
1. **Parsing failures**: Show extracted text, request manual input
2. **Ambiguous values**: Present options for user selection
3. **Missing values**: Identify found vs. missing parameters
4. **Validation errors**: Cross-check against physiological ranges

## Output Structure

The program should return a structured result containing:

```python
{
    "pdf_parsing": {  # Only present when PDF input is used
        "extraction_method": str,  # "text_based", "ocr", "mixed"
        "confidence_scores": {
            "neutrophils": float,
            "lymphocytes": float, 
            "platelets": float,
            "monocytes": float,
            "patient_age": float,  # Confidence for demographic extraction
            "patient_sex": float,
            "test_date": float
        },
        "extracted_values": {
            "neutrophils": {"value": float, "unit": str, "raw_text": str},
            "lymphocytes": {"value": float, "unit": str, "raw_text": str},
            "platelets": {"value": float, "unit": str, "raw_text": str},
            "monocytes": {"value": float, "unit": str, "raw_text": str}
        },
        "patient_demographics": {
            "age": {"value": int, "raw_text": str, "confidence": float},
            "sex": {"value": str, "raw_text": str, "confidence": float}, 
            "test_date": {"value": str, "raw_text": str, "confidence": float}
        },
        "parsing_warnings": list,
        "manual_verification_needed": bool
    },
    "results": {
        "sii": {
            "value": float,
            "interpretation": str,
            "risk_level": str,  # "low", "moderate", "high", "very_high"
            "reference_ranges": dict
        },
        "nlr": {
            "value": float,
            "interpretation": str,
            "risk_level": str,
            "reference_ranges": dict
        },
        "plr": {
            "value": float,
            "interpretation": str,
            "risk_level": str,
            "reference_ranges": dict
        },
        "siri": {
            "value": float,
            "interpretation": str,
            "risk_level": str,
            "reference_ranges": dict
        },
        "mlr": {
            "value": float,
            "interpretation": str,
            "risk_level": str,
            "reference_ranges": dict
        },
        "piv": {
            "value": float,
            "interpretation": str,
            "risk_level": str,
            "reference_ranges": dict
        }
    },
    "summary": {
        "overall_inflammatory_status": str,
        "highest_risk_indices": list,
        "recommendations": list
    },
    "metadata": {
        "calculation_date": str,
        "input_validation": dict,
        "pdf_source": str,  # Path to original PDF file
        "warnings": list
    }
}
```

## Reference Ranges and Thresholds

### Systemic Immune-Inflammation Index (SII)
- **Normal**: < 500
- **Mild elevation**: 500-800
- **Moderate elevation**: 800-1200
- **High elevation**: > 1200
- **Critical threshold**: > 2000 (associated with significantly increased mortality risk)

### Neutrophil-to-Lymphocyte Ratio (NLR)
- **Normal**: < 2.0
- **Mild elevation**: 2.0-3.0
- **Moderate elevation**: 3.0-5.0
- **High elevation**: > 5.0
- **Critical threshold**: > 8.0

### Platelet-to-Lymphocyte Ratio (PLR)
- **Normal**: < 150
- **Mild elevation**: 150-200
- **Moderate elevation**: 200-300
- **High elevation**: > 300

### Systemic Inflammatory Response Index (SIRI)
- **Normal**: < 1.0
- **Mild elevation**: 1.0-2.0
- **Moderate elevation**: 2.0-3.0
- **High elevation**: > 3.0

### Monocyte-to-Lymphocyte Ratio (MLR)
- **Normal**: < 0.3
- **Mild elevation**: 0.3-0.5
- **Moderate elevation**: 0.5-0.8
- **High elevation**: > 0.8

### Pan-Immune Inflammation Value (PIV)
- **Normal**: < 300
- **Mild elevation**: 300-600
- **Moderate elevation**: 600-1200
- **High elevation**: > 1200

## Functional Requirements

### Core Functions

1. **`process_pdf(pdf_file_path, output_directory=None)`**
   - Main entry point for PDF processing
   - Extract CBC values from blood test PDFs
   - Return parsed values with confidence scores
   - Handle parsing failures gracefully

2. **`extract_cbc_values(pdf_content)`**
   - Extract neutrophils, lymphocytes, platelets, monocytes from PDF text
   - Support multiple laboratory formats and field name variations
   - Apply unit conversions automatically
   - Generate confidence scores for extracted values

3. **`parse_with_ocr(pdf_file_path)`**
   - OCR fallback for scanned PDFs
   - Image preprocessing and text recognition
   - Integration with pytesseract/Tesseract OCR
   - Quality assessment of OCR results

4. **`calculate_indices(neutrophils, lymphocytes, platelets, monocytes=None)`**
   - Calculate all applicable immune inflammatory indices
   - Validate input parameters
   - Return structured results with interpretations

5. **`validate_inputs(neutrophils, lymphocytes, platelets, monocytes=None)`**
   - Check for valid numeric values
   - Ensure values are within physiological ranges
   - Flag potential data entry errors
   - Cross-reference against PDF reference ranges when available

6. **`interpret_results(indices_dict, patient_age=None, patient_sex=None)`**
   - Provide clinical interpretation of calculated indices
   - Adjust interpretations based on age/sex if provided
   - Generate risk assessments and recommendations

7. **`generate_report(results_dict, output_directory, format="pdf")`**
   - Generate comprehensive reports with PDF parsing details
   - Support multiple formats: "pdf", "text", "json", "html"
   - Include visualizations and confidence scores
   - Save alongside original PDF file

8. **`manual_fallback_mode(extracted_text, missing_fields)`**
   - Interactive mode when PDF parsing fails
   - Display extracted text for user review
   - Request manual input for missing/uncertain values
   - Validate manual entries

### Input Validation Rules

- **Neutrophils**: 1,000 - 25,000 cells/µL (physiological range)
- **Lymphocytes**: 500 - 8,000 cells/µL (physiological range)
- **Platelets**: 100,000 - 1,000,000 cells/µL (physiological range)
- **Monocytes**: 100 - 2,000 cells/µL (physiological range)
- **Zero values**: Flag as potential error, prevent division by zero
- **Extreme ratios**: Flag ratios > 50 as potential data entry errors

### Error Handling

1. **Division by Zero**: Return appropriate error when lymphocyte count is zero
2. **Invalid Inputs**: Raise `ValueError` with descriptive messages for invalid inputs
3. **Out of Range Values**: Issue warnings for values outside physiological ranges
4. **Missing Required Parameters**: Clear error messages for missing required values

## Technical Implementation

### Project Structure
```
immune-inflam-index/
├── pyproject.toml              # uv project configuration
├── README.md                   # Project documentation
├── .python-version             # Python version specification (3.12)
├── src/
│   └── immune_inflam_index/
│       ├── __init__.py
│       ├── cli.py              # Command line interface
│       ├── pdf_parser.py       # PDF parsing and OCR functionality
│       ├── extractor.py        # CBC value extraction logic
│       ├── calculator.py       # Core calculation functions
│       ├── validator.py        # Input validation
│       ├── interpreter.py      # Results interpretation
│       ├── reporter.py         # Report generation (PDF, text, JSON)
│       ├── constants.py        # Reference ranges and field mappings
│       └── utils.py            # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_pdf_parser.py      # PDF parsing tests
│   ├── test_extractor.py       # Value extraction tests
│   ├── test_calculator.py      # Calculation tests
│   ├── test_validator.py       # Validation tests
│   ├── test_interpreter.py     # Interpretation tests
│   ├── test_cli.py             # CLI tests
│   └── test_integration.py     # End-to-end tests
├── test_data/
│   ├── sample_reports/         # Sample PDF files for testing
│   └── expected_outputs/       # Expected test results
├── examples/
│   ├── basic_pdf_usage.py
│   ├── manual_input_usage.py
│   ├── batch_processing.py
│   └── cli_examples.sh
└── docs/
    ├── api_reference.md
    ├── clinical_interpretation.md
    ├── pdf_parsing_guide.md
    ├── troubleshooting.md
    └── changelog.md
```

### Dependencies

#### Core Dependencies (Required)
- **Python**: >= 3.12
- **pdfplumber**: PDF text extraction (`~=0.11.7`)
- **pytesseract**: OCR capabilities (`~=0.3.13`)
- **Pillow**: Image processing for OCR (`~=11.2.0`)
- **fuzzywuzzy**: Fuzzy string matching for field names (`~=0.18.0`)
- **python-Levenshtein**: Fast fuzzy matching backend (`~=0.25.0`)
- **click**: CLI framework (`~=8.1.0`)
- **rich**: Enhanced terminal output (`~=13.7.0`)

#### Optional Dependencies
- **reportlab**: PDF report generation (`~=4.2.0`)
- **matplotlib**: Basic visualization (`~=3.8.0`)
- **pandas**: Batch processing and data manipulation (`~=2.2.0`)
- **pytest**: Testing framework (`~=8.3.0`)
- **black**: Code formatting (`~=24.8.0`)
- **mypy**: Type checking (`~=1.11.0`)
- **coverage**: Test coverage (`~=7.6.0`)

#### System Dependencies
- **Tesseract OCR**: Required for scanned PDF processing
  - macOS: `brew install tesseract`
  - Ubuntu/Debian: `apt-get install tesseract-ocr`
  - Windows: Download from GitHub releases

### Configuration Management
- Support for custom reference ranges via configuration files
- Environment-specific settings (research vs. clinical use)
- User-defined interpretation criteria

## Installation and Setup

### Prerequisites
1. **Python 3.12 or higher**
2. **uv package manager**: Install from https://docs.astral.sh/uv/
3. **Tesseract OCR** (for scanned PDF support):
   ```bash
   # macOS
   brew install tesseract
   
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # Windows
   # Download from: https://github.com/UB-Mannheim/tesseract/wiki
   ```

### Project Setup

#### Initialize Project
```bash
# Create project directory
mkdir immune-inflam-index
cd immune-inflam-index

# Initialize uv project with Python 3.12
uv init --python 3.12
uv python pin 3.12
```

#### Install Dependencies
```bash
# Core dependencies
uv add pdfplumber pytesseract pillow fuzzywuzzy python-Levenshtein click rich

# Optional dependencies for enhanced features
uv add reportlab matplotlib pandas --optional

# Development dependencies
uv add pytest black mypy coverage --dev
```

#### Install as Editable Package
```bash
# Install the package in development mode
uv add -e .
```

#### Verify Installation
```bash
# Test basic functionality
uv run immune-inflam-index --help

# Test PDF parsing (if Tesseract is installed)
uv run python -c "
import pytesseract
import pdfplumber
print('PDF parsing dependencies installed successfully')
"
```

### Configuration Files

#### pyproject.toml Example
```toml
[project]
name = "immune-inflam-index"
version = "1.0.0"
description = "Calculate immune inflammatory indices from blood test PDFs"
requires-python = ">=3.12"
dependencies = [
    "pdfplumber~=0.11.7",
    "pytesseract~=0.3.13", 
    "pillow~=11.2.0",
    "fuzzywuzzy~=0.18.0",
    "python-Levenshtein~=0.25.0",
    "click~=8.1.0",
    "rich~=13.7.0",
]

[project.optional-dependencies]
reports = ["reportlab~=4.2.0"]
visualization = ["matplotlib~=3.8.0"]
batch = ["pandas~=2.2.0"]
all = ["reportlab~=4.2.0", "matplotlib~=3.8.0", "pandas~=2.2.0"]

[project.scripts]
immune-inflam-index = "immune_inflam_index.cli:main"

[tool.uv]
dev-dependencies = [
    "pytest~=8.3.0",
    "black~=24.8.0", 
    "mypy~=1.11.0",
    "coverage~=7.6.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

#### Environment Variables
```bash
# Optional: Set custom Tesseract path
export TESSERACT_CMD="/usr/local/bin/tesseract"

# Optional: Enable debug logging
export III_DEBUG=1

# Optional: Custom config directory
export III_CONFIG_DIR="./config"
```

## Usage Examples

### Command Line Interface (Primary Usage)

#### Process PDF Blood Test Report
```bash
# Basic PDF processing
uv run immune-inflam-index process-pdf "blood_test.pdf"

# With output directory and patient info
uv run immune-inflam-index process-pdf "blood_test.pdf" \
    --output-dir "./results" \
    --patient-age 58 \
    --patient-sex M

# Batch processing multiple PDFs
uv run immune-inflam-index batch-process "*.pdf" --output-dir "./batch_results"
```

#### Manual Input Mode
```bash
# Interactive manual input
uv run immune-inflam-index manual-input \
    --neutrophils 6310 \
    --lymphocytes 1660 \
    --platelets 181000 \
    --monocytes 670

# Save results to specific directory
uv run immune-inflam-index manual-input \
    --neutrophils 6310 \
    --lymphocytes 1660 \
    --platelets 181000 \
    --output-dir "./results"
```

#### Help and Information
```bash
# Show help
uv run immune-inflam-index --help

# Show interpretation guide
uv run immune-inflam-index interpret --guide

# Show supported PDF formats
uv run immune-inflam-index supported-formats
```

### Python API Usage

#### PDF Processing
```python
from immune_inflam_index import process_pdf

# Process PDF file
results = process_pdf(
    pdf_file_path="blood_test.pdf",
    output_directory="./results",
    patient_age=58,
    patient_sex="M"
)

# Check parsing confidence
if results["pdf_parsing"]["manual_verification_needed"]:
    print("Warning: Low confidence extraction, please verify:")
    for field, score in results["pdf_parsing"]["confidence_scores"].items():
        if score < 70:
            print(f"{field}: {score}% confidence")

print(f"SII: {results['results']['sii']['value']:.1f}")
print(f"Risk Level: {results['results']['sii']['risk_level']}")
```

#### Manual Input
```python
from immune_inflam_index import calculate_indices

# Example CBC values from sample PDF
results = calculate_indices(
    neutrophils=6310,    # cells/µL (converted from 6.31 x10³/L)
    lymphocytes=1660,    # cells/µL (converted from 1.66 x10³/L) 
    platelets=181000,    # cells/µL (converted from 181 x10³/L)
    monocytes=670        # cells/µL (converted from 0.67 x10³/L)
)

print(f"SII: {results['results']['sii']['value']:.1f}")
print(f"Risk Level: {results['results']['sii']['risk_level']}")
```

#### Batch Processing
```python
import pandas as pd
from immune_inflam_index import process_batch_pdfs

# Process multiple PDF files
pdf_files = ["patient1.pdf", "patient2.pdf", "patient3.pdf"]
results_df = process_batch_pdfs(pdf_files, output_directory="./batch_results")

# Process from CSV with manual values
df = pd.read_csv('patient_cbc_data.csv')
results_df = process_batch_manual(df)
```

#### Error Handling and Fallback
```python
from immune_inflam_index import process_pdf, manual_fallback_mode

try:
    results = process_pdf("blood_test.pdf")
except PDFParsingError as e:
    print(f"PDF parsing failed: {e}")
    print("Extracted text for manual review:")
    print(e.extracted_text)
    
    # Manual fallback
    manual_values = manual_fallback_mode(
        extracted_text=e.extracted_text,
        missing_fields=e.missing_fields
    )
    results = calculate_indices(**manual_values)
```

## Clinical Integration Notes

1. **Not for Diagnosis**: These indices are screening and monitoring tools, not diagnostic tests
2. **Clinical Correlation**: Results should always be interpreted in clinical context
3. **Trend Analysis**: Serial measurements are more valuable than single time points
4. **Reference Population**: Consider population-specific reference ranges when available
5. **Comorbidities**: Certain conditions may affect baseline inflammatory markers

## Quality Assurance

### Testing Requirements
- **Unit Tests**: >95% code coverage
- **Integration Tests**: End-to-end workflow validation
- **Performance Tests**: Handle large datasets efficiently
- **Validation Tests**: Compare against published reference calculations

### Documentation Requirements
- **API Documentation**: Complete function documentation with examples
- **Clinical Guidelines**: Clear guidance on interpretation and limitations
- **Validation Studies**: References to supporting literature

## Deployment Options

1. **Command Line Interface**: Simple CLI for individual calculations
2. **Python Package**: Installable via pip for integration into other projects
3. **Web Application**: Browser-based interface for clinical use
4. **API Service**: RESTful API for integration with EMR systems
5. **Jupyter Notebook**: Interactive analysis environment

## Sample PDF Analysis Results

Based on the provided sample PDF (Dmitry Blood report March 2025.pdf - Innoquest Diagnostics):

### Extracted Values:
- **Neutrophils**: 6.31 x10³/L = 6,310 cells/µL
- **Lymphocytes**: 1.66 x10³/L = 1,660 cells/µL  
- **Platelets**: 181 x10³/L = 181,000 cells/µL
- **Monocytes**: 0.67 x10³/L = 670 cells/µL

### Calculated Indices:
- **SII**: (6310 × 181000) / 1660 = 688,253 (High elevation - above normal range)
- **NLR**: 6310 / 1660 = 3.8 (Moderate elevation)
- **PLR**: 181000 / 1660 = 109 (Normal range)
- **SIRI**: (6310 × 670) / 1660 = 2,543 (High elevation)
- **MLR**: 670 / 1660 = 0.40 (Mild elevation)
- **PIV**: (6310 × 670 × 181000) / 1660 = 461,896,627 (Very high elevation)

### Clinical Interpretation:
Multiple inflammatory indices are elevated, suggesting an active inflammatory state requiring clinical correlation and possible intervention.

## Future Enhancements

1. **Enhanced PDF Format Support**: 
   - Support for LabCorp, Quest Diagnostics, and other major lab formats
   - Template-based parsing system for new laboratory formats
   - Automatic format detection and parser selection

2. **Advanced OCR Capabilities**:
   - Improved image preprocessing for low-quality scans
   - Multi-language OCR support for international lab reports
   - Table structure recognition for complex layouts

3. **Machine Learning Integration**: 
   - Predictive models based on inflammatory indices
   - Automated PDF format classification
   - Smart field detection using trained models

4. **Longitudinal Analysis**: 
   - Trend analysis and change detection over time
   - Historical comparison with previous results
   - Progress tracking and visualization

5. **Population Comparisons**: 
   - Benchmarking against population databases
   - Age and gender-specific reference ranges
   - Risk stratification based on demographics

6. **Integration APIs**: 
   - Direct integration with laboratory information systems
   - HL7 FHIR compatibility for healthcare interoperability
   - Electronic health record (EHR) integration

7. **Advanced Reporting**:
   - Interactive web-based reports
   - Physician-friendly interpretation summaries
   - Patient education materials

8. **Mobile Application**: 
   - Point-of-care calculations on mobile devices
   - Photo capture and processing of paper reports
   - Offline functionality for remote locations

## Development Workflow and Version Control

### Git Repository Requirements

**MANDATORY**: This project must be tracked in a git repository for:
- **Code integrity**: Track all changes and fixes, especially critical unit conversion corrections
- **Collaboration**: Enable team development and code review
- **Audit trail**: Medical software requires complete change documentation
- **Rollback capability**: Ability to revert problematic changes
- **Release management**: Tag stable versions for production use

### Git Setup Instructions
```bash
# Initialize repository in project directory
cd /path/to/immune-inflam-index
git init
git add .
git commit -m "Initial commit: Immune Inflammatory Index Calculator v1.0"

# Set up remote repository (recommended)
git remote add origin <repository-url>
git push -u origin main
```

### Commit Message Conventions
For this medical calculation software, use descriptive commit messages:
```
feat: Add PDF parsing support for Innoquest Diagnostics format
fix: CRITICAL - Correct SII unit conversion (was 1000x too high)
docs: Update specification with literature-based reference ranges  
test: Add validation tests for unit conversion accuracy
refactor: Improve error handling in PDF extraction
```

### Change Documentation Requirements
All code changes must include:
1. **Clear commit messages** explaining what and why
2. **Test validation** for calculation accuracy
3. **Documentation updates** in specification
4. **Code comments** explaining complex medical logic
5. **Unit test coverage** for critical calculations

### Branch Strategy
- **main**: Production-ready, tested code only
- **develop**: Integration branch for new features
- **feature/**: Individual feature development
- **hotfix/**: Critical bug fixes (like unit conversion errors)

## Compliance and Regulations

- **HIPAA Compliance**: Ensure patient data protection if handling PHI
- **Medical Device Regulations**: Consider FDA guidance for medical calculation software
- **Clinical Decision Support**: Implement appropriate warnings and disclaimers
- **Data Privacy**: Implement appropriate data handling and storage practices

## References

1. Hu, B., Yang, X. R., Xu, Y., et al. (2014). Systemic immune-inflammation index predicts prognosis of patients after curative resection for hepatocellular carcinoma. Clinical Cancer Research, 20(23), 6212-6222.

2. Chen, J. H., Zhai, E. T., Yuan, Y. J., et al. (2017). Systemic immune-inflammation index for predicting prognosis of colorectal cancer. World Journal of Gastroenterology, 23(34), 6261-6272.

3. Yang, R., Chang, Q., Meng, X., et al. (2018). Prognostic value of Systemic immune-inflammation index in cancer: A meta-analysis. Journal of Cancer, 9(18), 3295-3302.

4. Qin, B., Ma, N., Tang, Q., et al. (2019). Neutrophil to lymphocyte ratio (NLR) and platelet to lymphocyte ratio (PLR) were useful markers in assessment of inflammatory response and disease activity in SLE patients. Modern Rheumatology, 26(3), 372-376.

5. Jeff Bland research references from podcast discussions on immune inflammatory index calculations and Danish studies.