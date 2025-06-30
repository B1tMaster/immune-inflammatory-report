# Immune Inflammatory Index Calculator

A comprehensive calculator for multiple immune inflammatory indices derived from standard Complete Blood Count (CBC) with differential blood tests. This tool provides automated PDF parsing capabilities to extract blood test values from laboratory reports and generates detailed clinical reports with age-specific and sex-specific interpretations.

## Table of Contents

- [What is the Immune Inflammatory Index?](#what-is-the-immune-inflammatory-index)
- [Calculated Indices](#calculated-indices)
- [Scientific Background](#scientific-background)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Sample Reports](#sample-reports)
- [Understanding Your Results](#understanding-your-results)
- [Input Requirements](#input-requirements)
- [Clinical Interpretation](#clinical-interpretation)
- [Limitations and Disclaimers](#limitations-and-disclaimers)
- [Contributing](#contributing)
- [License](#license)

## What is the Immune Inflammatory Index?

The Immune Inflammatory Index (III) is a comprehensive assessment tool that calculates multiple inflammatory markers from standard blood test results. These indices provide insights into systemic inflammation, immune activation, and potential disease risk by analyzing the relationships between different white blood cell populations and platelets.

Unlike traditional single markers (like C-reactive protein), these indices leverage the natural balance between different immune cell types to provide a more nuanced view of inflammatory status. They are particularly valuable for:

- Early detection of systemic inflammation
- Cardiovascular disease risk assessment
- Cancer screening and prognosis
- Autoimmune disease monitoring
- General health and wellness tracking

## Calculated Indices

### 1. Systemic Immune-Inflammation Index (SII)
**Formula:** `SII = (Neutrophils × Platelets) / Lymphocytes`

Reflects the balance between neutrophil-platelet pro-inflammatory activity and lymphocyte-mediated adaptive immunity. Higher values indicate predominance of innate inflammatory responses.

### 2. Neutrophil-to-Lymphocyte Ratio (NLR)
**Formula:** `NLR = Neutrophils / Lymphocytes`

Represents the balance between neutrophil-driven acute inflammation and lymphocyte-mediated immune regulation. Elevated ratios suggest increased inflammatory drive or compromised lymphocyte function.

### 3. Platelet-to-Lymphocyte Ratio (PLR)
**Formula:** `PLR = Platelets / Lymphocytes`

Indicates the relationship between platelet-mediated hemostatic/inflammatory responses and lymphocyte immune function. Elevation may reflect increased thrombotic risk and inflammatory burden.

### 4. Systemic Inflammatory Response Index (SIRI)
**Formula:** `SIRI = (Neutrophils × Monocytes) / Lymphocytes`

Incorporates monocyte activation alongside neutrophil-lymphocyte balance, providing insight into tissue-based inflammatory responses and macrophage activation.

### 5. Monocyte-to-Lymphocyte Ratio (MLR)
**Formula:** `MLR = Monocytes / Lymphocytes`

Reflects monocyte activation relative to lymphocyte function, indicating the degree of tissue inflammatory response and macrophage-mediated inflammatory processes.

### 6. Pan-Immune-Inflammation Value (PIV)
**Formula:** `PIV = (Neutrophils × Platelets × Monocytes) / Lymphocytes`

Comprehensive index incorporating all major inflammatory cell types, providing overall assessment of pan-immune inflammatory activation across all cell populations.

## Scientific Background

These inflammatory indices are based on extensive research in inflammatory biomarkers:

- **SII Research:** [Hu et al. (2014)](https://pubmed.ncbi.nlm.nih.gov/24618514/) - "Systemic immune-inflammation index predicts prognosis of patients after curative resection for hepatocellular carcinoma"
- **NLR Studies:** [Forget et al. (2017)](https://pubmed.ncbi.nlm.nih.gov/28364909/) - "What is the normal value of the neutrophil-to-lymphocyte ratio?"
- **PLR Research:** [Templeton et al. (2014)](https://pubmed.ncbi.nlm.nih.gov/24618783/) - "Prognostic role of platelet to lymphocyte ratio in solid tumors"
- **SIRI Studies:** [Qi et al. (2016)](https://pubmed.ncbi.nlm.nih.gov/27053248/) - "A novel systemic inflammation response index (SIRI) for predicting the survival of patients with pancreatic adenocarcinoma after chemotherapy"
- **MLR Research:** [Naranbhai et al. (2014)](https://pubmed.ncbi.nlm.nih.gov/24218446/) - "The association between the ratio of monocytes to lymphocytes and risk of tuberculosis among HIV-infected postpartum women"

## Features

- **Automated PDF Parsing:** Extract blood values directly from laboratory reports
- **Automatic Demographic Detection:** Extract patient age, sex, and test date from PDFs
- **Comprehensive Calculation:** All six major inflammatory indices
- **Age-Specific Interpretation:** Clinical considerations based on patient age groups
- **Sex-Specific Analysis:** Different interpretations for male and female patients
- **Multiple Output Formats:** PDF, text, and JSON reports
- **Confidence Scoring:** Reliability indicators for extracted values
- **Clinical Recommendations:** Actionable guidance based on results
- **Manual Input Support:** Fallback for failed PDF parsing

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### macOS Installation

```bash
# Install system dependencies
brew install tesseract

# Clone the repository
git clone https://github.com/yourusername/immune-inflam-index.git
cd immune-inflam-index

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Windows Installation

```powershell
# Install Tesseract OCR
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add tesseract to your PATH

# Clone the repository
git clone https://github.com/yourusername/immune-inflam-index.git
cd immune-inflam-index

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Configuration

### Tesseract OCR Setup

#### macOS
```bash
# Tesseract should be automatically configured after brew installation
# Verify installation:
tesseract --version
```

#### Windows
```powershell
# Add Tesseract to system PATH or set environment variable
$env:TESSDATA_PREFIX = "C:\Program Files\Tesseract-OCR\tessdata"
```

### Optional: Configure default output directory

Create a configuration file at `~/.immune_inflam_config.json`:

```json
{
    "default_output_dir": "/path/to/your/reports",
    "default_format": "pdf"
}
```

## Usage

### Command Line Interface

#### Basic PDF Processing (macOS)

```bash
# Process a PDF blood test report
python -m immune_inflam_index.cli process-pdf path/to/bloodtest.pdf

# Specify output directory
python -m immune_inflam_index.cli process-pdf path/to/bloodtest.pdf --output-dir ./reports

# Specify patient demographics manually (overrides auto-detection)
python -m immune_inflam_index.cli process-pdf path/to/bloodtest.pdf --patient-age 45 --patient-sex F

# Generate specific format
python -m immune_inflam_index.cli process-pdf path/to/bloodtest.pdf --format json

# Multiple formats
python -m immune_inflam_index.cli process-pdf path/to/bloodtest.pdf --format pdf --format text --format json
```

#### Basic PDF Processing (Windows)

```powershell
# Process a PDF blood test report
python -m immune_inflam_index.cli process-pdf "C:\path\to\bloodtest.pdf"

# Specify output directory
python -m immune_inflam_index.cli process-pdf "C:\path\to\bloodtest.pdf" --output-dir "C:\Reports"

# Specify patient demographics manually
python -m immune_inflam_index.cli process-pdf "C:\path\to\bloodtest.pdf" --patient-age 45 --patient-sex F

# Generate specific format
python -m immune_inflam_index.cli process-pdf "C:\path\to\bloodtest.pdf" --format json
```

#### Manual Value Entry

```bash
# Calculate indices from manual input
python -m immune_inflam_index.cli calculate \
    --neutrophils 4200 \
    --lymphocytes 1800 \
    --platelets 250000 \
    --monocytes 480 \
    --patient-age 32 \
    --patient-sex M \
    --output-dir ./reports
```

#### Interactive Mode

```bash
# Start interactive mode for manual value entry
python -m immune_inflam_index.cli interactive
```

### Python API Usage

```python
from immune_inflam_index import process_pdf, calculate_indices

# Process PDF file
results = process_pdf("path/to/bloodtest.pdf", patient_age=35, patient_sex="M")

# Manual calculation
indices = calculate_indices(
    neutrophils=4200,
    lymphocytes=1800, 
    platelets=250000,
    monocytes=480
)

# Generate report
from immune_inflam_index import generate_report, save_results

report_content = generate_report(results, format_type="pdf")
saved_path = save_results(results, output_dir="./reports", format_type="pdf")
```

## Sample Reports

### Example 1: Young Adult - Normal Results

**Patient:** 24-year-old female
**Test Values:** Neutrophils: 3,500, Lymphocytes: 2,200, Platelets: 280,000, Monocytes: 400

```
IMMUNE INFLAMMATORY INDEX REPORT
Generated: 2025-06-30 14:30:00

CALCULATED INDICES
SII: 444.5
  Risk Level: Normal
  Interpretation: Balanced systemic immune-inflammatory state

NLR: 1.6
  Risk Level: Normal  
  Interpretation: Normal neutrophil-lymphocyte balance

PLR: 127.3
  Risk Level: Normal
  Interpretation: Normal platelet-lymphocyte balance

SIRI: 0.6
  Risk Level: Normal
  Interpretation: Normal systemic inflammatory response

MLR: 0.18
  Risk Level: Normal
  Interpretation: Normal monocyte activation levels

PIV: 177.8
  Risk Level: Normal
  Interpretation: Normal pan-immune inflammatory status

OVERALL ASSESSMENT: Normal inflammatory state - maintain healthy lifestyle

PATIENT DEMOGRAPHICS & CLINICAL CONTEXT
Age: 24 years
Age Group: Young Adult (18-35)
Sex: F

Age-Specific Clinical Considerations:
" Elevated indices more likely to indicate acute pathology
" Consider lifestyle factors (stress, diet, exercise)
" Evaluate for underlying autoimmune conditions
```

### Example 2: Middle-Aged Adult - Moderate Risk

**Patient:** 52-year-old male
**Test Values:** Neutrophils: 6,800, Lymphocytes: 1,400, Platelets: 380,000, Monocytes: 650

```
IMMUNE INFLAMMATORY INDEX REPORT
Generated: 2025-06-30 14:35:00

CALCULATED INDICES
SII: 1,848.6
  Risk Level: High
  Interpretation: High-grade systemic inflammation indicating serious inflammatory burden

NLR: 4.9
  Risk Level: High
  Interpretation: Significant immune dysregulation - high inflammatory burden

PLR: 271.4
  Risk Level: Moderate
  Interpretation: Moderately increased risk for thrombotic complications

SIRI: 3.2
  Risk Level: Moderate
  Interpretation: Moderate inflammatory response indicating active tissue inflammation

MLR: 0.46
  Risk Level: Moderate
  Interpretation: Moderate monocyte activation indicating significant tissue inflammation

PIV: 1,201.6
  Risk Level: High
  Interpretation: High-grade pan-immune inflammation with extensive cellular involvement

OVERALL ASSESSMENT: High inflammatory state - urgent medical evaluation recommended

PATIENT DEMOGRAPHICS & CLINICAL CONTEXT
Age: 52 years
Age Group: Middle-aged Adult (35-65)
Sex: M

Age-Specific Clinical Considerations:
" Middle-aged adults may show early signs of inflammaging
" Cardiovascular risk factor assessment becomes critical
" Metabolic syndrome and insulin resistance considerations
" Cancer screening implications for persistently elevated indices

RECOMMENDATIONS:
1. Medical evaluation within 24-48 hours
2. Complete inflammatory workup (ESR, CRP, cytokines)
3. Assess for signs and symptoms of inflammatory conditions
4. Consider infectious disease evaluation
```

### Example 3: Elderly Adult - Mild Elevation

**Patient:** 72-year-old female
**Test Values:** Neutrophils: 4,800, Lymphocytes: 1,600, Platelets: 320,000, Monocytes: 520

```
IMMUNE INFLAMMATORY INDEX REPORT
Generated: 2025-06-30 14:40:00

CALCULATED INDICES
SII: 960.0
  Risk Level: Mild
  Interpretation: Mildly elevated systemic inflammation - monitor and consider lifestyle interventions

NLR: 3.0
  Risk Level: Mild
  Interpretation: Mild neutrophilia or lymphopenia - may indicate early inflammatory response

PLR: 200.0
  Risk Level: Mild
  Interpretation: Mildly elevated thrombotic and inflammatory risk

SIRI: 1.6
  Risk Level: Mild
  Interpretation: Mild systemic inflammatory response - early tissue inflammation

MLR: 0.33
  Risk Level: Mild
  Interpretation: Mild monocyte activation - early tissue inflammatory response

PIV: 499.2
  Risk Level: Mild
  Interpretation: Mildly elevated pan-immune inflammation involving multiple cell types

OVERALL ASSESSMENT: Mild inflammatory state - lifestyle interventions recommended

PATIENT DEMOGRAPHICS & CLINICAL CONTEXT
Age: 72 years
Age Group: Elderly Adult (65+)
Sex: F

Age-Specific Clinical Considerations:
" Elderly patients may have baseline elevation in inflammatory markers
" Consider age-related immunosenescence effects
" Higher risk for inflammatory complications
" Adjust thresholds for clinical significance
" Focus on functional status and quality of life

Sex-Specific Clinical Considerations:
" Women have higher baseline risk for autoimmune conditions
" Consider pregnancy, menstrual cycle, and menopause effects (post-menopausal)
" Higher prevalence of autoimmune diseases
```

## Understanding Your Results

### Risk Levels

- **Normal:** Values within expected healthy ranges
- **Mild:** Slightly elevated, may indicate early inflammatory response
- **Moderate:** Significantly elevated, suggesting active inflammatory process
- **High:** Markedly elevated, indicating serious inflammatory burden
- **Very High:** Critical elevation requiring immediate medical attention

### Age-Specific Considerations

#### Young Adults (18-35)
- Elevated indices more likely to indicate acute pathology
- Focus on lifestyle factors and autoimmune screening

#### Middle-aged Adults (35-65)
- Early signs of inflammaging may appear
- Cardiovascular and metabolic screening becomes critical
- Cancer screening implications for persistently elevated indices

#### Elderly Adults (65+)
- Baseline elevation may be normal due to immunosenescence
- Higher risk for inflammatory complications
- Focus on functional status and quality of life

### Sex-Specific Considerations

#### Females
- Higher baseline risk for autoimmune conditions
- Hormonal fluctuations may affect inflammatory markers
- Consider reproductive health factors

#### Males
- Higher baseline inflammatory burden
- Earlier cardiovascular disease risk
- Different inflammatory patterns compared to females

## Input Requirements

### Required Blood Test Values

1. **Neutrophils** (cells/µL or ×10³/L)
2. **Lymphocytes** (cells/µL or ×10³/L)
3. **Platelets** (cells/µL or ×10³/L)

### Optional Values

4. **Monocytes** (cells/µL or ×10³/L) - enhances MLR, SIRI, and PIV calculations

### Patient Information (Optional but Recommended)

- **Age:** For age-specific interpretation
- **Sex:** For sex-specific considerations
- **Test Date:** For record keeping

### Supported PDF Formats

- Standard laboratory reports with text-based content
- Scanned reports (OCR will be applied automatically)
- Common formats from major laboratory providers
- Multi-page reports (CBC section will be automatically located)

## Clinical Interpretation

### Normal Ranges (Approximate)

| Index | Normal Range | Mild | Moderate | High |
|-------|-------------|------|----------|------|
| SII | <500 | 500-1000 | 1000-2000 | >2000 |
| NLR | <3.0 | 3.0-5.0 | 5.0-10.0 | >10.0 |
| PLR | <150 | 150-200 | 200-300 | >300 |
| SIRI | <1.0 | 1.0-2.0 | 2.0-4.0 | >4.0 |
| MLR | <0.3 | 0.3-0.5 | 0.5-0.8 | >0.8 |
| PIV | <300 | 300-800 | 800-1500 | >1500 |

*Note: These ranges may vary based on laboratory standards and patient demographics*

### When to Seek Medical Attention

**Immediate (24-48 hours):**
- Any index in "High" or "Very High" range
- Multiple indices in "Moderate" range
- Concerning symptoms present

**Routine Follow-up:**
- Single index in "Mild" range
- Trending upward over time
- For lifestyle intervention guidance

## Limitations and Disclaimers

### Important Medical Disclaimers

- **Not a Diagnostic Tool:** These indices are screening tools, not diagnostic tests
- **Professional Interpretation Required:** Results must be interpreted by qualified healthcare providers
- **Clinical Context Essential:** Always consider symptoms, medical history, and other test results
- **Serial Measurements Preferred:** Trends over time are more valuable than single measurements
- **Individual Variation:** Normal ranges may vary between individuals and populations

### Technical Limitations

- PDF parsing accuracy depends on document quality and format
- OCR may introduce errors in scanned documents
- Manual verification recommended for critical decisions
- Age and sex considerations are based on general population data

### When This Tool May Not Be Suitable

- Pediatric patients (under 18 years)
- Patients with known hematologic malignancies
- Active chemotherapy or radiation therapy
- Recent major surgery or trauma
- Pregnancy (may require adjusted interpretations)

## Contributing

We welcome contributions to improve this tool! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone and install in development mode
git clone https://github.com/yourusername/immune-inflam-index.git
cd immune-inflam-index
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8 src/
black src/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions, issues, or feature requests:
- Create an issue on [GitHub](https://github.com/yourusername/immune-inflam-index/issues)
- Contact: support@immune-inflam-index.com

## Acknowledgments

- Research teams who developed and validated these inflammatory indices
- Medical professionals who provided clinical interpretation guidance
- Open source communities for the underlying technologies

---

**Disclaimer:** This software is for educational and research purposes only. Always consult with qualified healthcare professionals for medical decisions and treatment plans.