"""Generate synthetic blood test PDF reports for testing."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import date
import random


class BloodTestPDFGenerator:
    """Generate realistic blood test PDF reports for testing."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()
        
        # Create custom styles
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.darkblue,
            spaceAfter=20,
        )
        
        self.lab_style = ParagraphStyle(
            'LabStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
        )
    
    def generate_standard_report(
        self,
        filename: str,
        blood_values: Dict[str, float],
        patient_data: Dict[str, Any],
        lab_name: str = "MedLab Diagnostics",
    ) -> Path:
        """Generate a standard text-based blood test report."""
        filepath = self.output_dir / filename
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        story = []
        
        # Header
        story.append(Paragraph(lab_name, self.header_style))
        story.append(Paragraph("Complete Blood Count with Differential", self.styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Patient info
        patient_info = [
            ["Patient Information", ""],
            ["Age:", f"{patient_data.get('age', 'N/A')} years"],
            ["Sex:", patient_data.get('sex', 'N/A')],
            ["Test Date:", patient_data.get('test_date', date.today()).strftime("%m/%d/%Y")],
            ["Report Date:", date.today().strftime("%m/%d/%Y")],
        ]
        
        patient_table = Table(patient_info, colWidths=[2*inch, 3*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 20))
        
        # CBC Results
        story.append(Paragraph("CBC with Differential Results", self.styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Format blood values
        cbc_data = [
            ["Test", "Result", "Reference Range", "Units"],
            ["White Blood Cell Count", f"{sum([blood_values.get('neutrophils', 0), blood_values.get('lymphocytes', 0), blood_values.get('monocytes', 0)]):.0f}", "4,000-11,000", "cells/μL"],
            ["Neutrophils (Absolute)", f"{blood_values.get('neutrophils', 0):.0f}", "1,800-7,700", "cells/μL"],
            ["Lymphocytes (Absolute)", f"{blood_values.get('lymphocytes', 0):.0f}", "1,000-4,000", "cells/μL"],
            ["Monocytes (Absolute)", f"{blood_values.get('monocytes', 0):.0f}", "200-800", "cells/μL"],
            ["Platelets", f"{blood_values.get('platelets', 0):,.0f}", "150,000-450,000", "cells/μL"],
        ]
        
        cbc_table = Table(cbc_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1*inch])
        cbc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(cbc_table)
        story.append(Spacer(1, 20))
        
        # Footer
        story.append(Paragraph("Laboratory Director: Dr. Jane Smith, MD", self.lab_style))
        story.append(Paragraph("Certified Laboratory Professional", self.lab_style))
        
        doc.build(story)
        return filepath
    
    def generate_scanned_report(
        self,
        filename: str,
        blood_values: Dict[str, float],
        patient_data: Dict[str, Any],
        lab_name: str = "Regional Medical Center",
    ) -> Path:
        """Generate a report that simulates a scanned document with slightly different formatting."""
        filepath = self.output_dir / filename
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        story = []
        
        # Slightly different header format to simulate different lab
        story.append(Paragraph(f"<b>{lab_name}</b>", self.styles['Title']))
        story.append(Paragraph("Laboratory Report", self.styles['Heading2']))
        story.append(Paragraph("CBC w/ Auto Differential", self.styles['Heading3']))
        story.append(Spacer(1, 15))
        
        # Patient demographics in paragraph format
        patient_text = f"""
        <b>Patient Demographics:</b><br/>
        Age: {patient_data.get('age', 'N/A')} years old<br/>
        Gender: {patient_data.get('sex', 'N/A')}<br/>
        Collection Date: {patient_data.get('test_date', date.today()).strftime("%B %d, %Y")}<br/>
        Reported: {date.today().strftime("%B %d, %Y")}
        """
        story.append(Paragraph(patient_text, self.lab_style))
        story.append(Spacer(1, 20))
        
        # Results in a more clinical format
        story.append(Paragraph("<b>HEMATOLOGY RESULTS</b>", self.styles['Heading3']))
        
        results_text = f"""
        <b>Complete Blood Count:</b><br/>
        WBC Count: {sum([blood_values.get('neutrophils', 0), blood_values.get('lymphocytes', 0), blood_values.get('monocytes', 0)]):.0f} cells/μL<br/>
        <br/>
        <b>Differential Count (Absolute):</b><br/>
        Neutrophils: {blood_values.get('neutrophils', 0):.0f} cells/μL (Ref: 1800-7700)<br/>
        Lymphocytes: {blood_values.get('lymphocytes', 0):.0f} cells/μL (Ref: 1000-4000)<br/>
        Monocytes: {blood_values.get('monocytes', 0):.0f} cells/μL (Ref: 200-800)<br/>
        <br/>
        <b>Platelet Count:</b><br/>
        Platelets: {blood_values.get('platelets', 0):,.0f} cells/μL (Reference: 150,000-450,000)
        """
        story.append(Paragraph(results_text, self.lab_style))
        story.append(Spacer(1, 30))
        
        # Add some noise that might be in scanned documents
        story.append(Paragraph("Performed by: Automated Hematology Analyzer", self.lab_style))
        story.append(Paragraph("Reviewed by: Dr. Michael Johnson, MD", self.lab_style))
        
        doc.build(story)
        return filepath
    
    def generate_multipage_report(
        self,
        filename: str,
        blood_values: Dict[str, float],
        patient_data: Dict[str, Any],
        lab_name: str = "University Hospital Lab",
    ) -> Path:
        """Generate a multi-page report with CBC on the second page."""
        filepath = self.output_dir / filename
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        story = []
        
        # Page 1 - General lab info and other tests
        story.append(Paragraph(lab_name, self.header_style))
        story.append(Paragraph("Comprehensive Metabolic Panel & CBC", self.styles['Heading2']))
        story.append(Spacer(1, 20))
        
        # Patient info
        story.append(Paragraph(f"<b>Patient:</b> {patient_data.get('age', 'N/A')} year old {patient_data.get('sex', 'N/A')}", self.lab_style))
        story.append(Paragraph(f"<b>Date of Service:</b> {patient_data.get('test_date', date.today()).strftime('%m/%d/%Y')}", self.lab_style))
        story.append(Spacer(1, 20))
        
        # Add some fake metabolic panel results
        story.append(Paragraph("<b>COMPREHENSIVE METABOLIC PANEL</b>", self.styles['Heading3']))
        
        metabolic_data = [
            ["Test", "Result", "Reference Range"],
            ["Glucose", "95", "70-100 mg/dL"],
            ["BUN", "18", "8-20 mg/dL"],
            ["Creatinine", "1.0", "0.6-1.2 mg/dL"],
            ["Sodium", "140", "136-145 mmol/L"],
            ["Potassium", "4.2", "3.5-5.0 mmol/L"],
            ["Chloride", "102", "98-107 mmol/L"],
            ["CO2", "24", "22-29 mmol/L"],
        ]
        
        metabolic_table = Table(metabolic_data, colWidths=[2*inch, 1.5*inch, 2*inch])
        metabolic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(metabolic_table)
        
        # Page break
        story.append(Spacer(1, 8*inch))  # Force page break
        
        # Page 2 - CBC Results
        story.append(Paragraph("<b>COMPLETE BLOOD COUNT WITH DIFFERENTIAL</b>", self.styles['Heading3']))
        story.append(Spacer(1, 20))
        
        cbc_data = [
            ["Parameter", "Patient Value", "Reference Range", "Units"],
            ["WBC", f"{sum([blood_values.get('neutrophils', 0), blood_values.get('lymphocytes', 0), blood_values.get('monocytes', 0)]):.1f}", "4.0-11.0", "x10³/μL"],
            ["Neutrophils#", f"{blood_values.get('neutrophils', 0)/1000:.1f}", "1.8-7.7", "x10³/μL"],
            ["Lymphocytes#", f"{blood_values.get('lymphocytes', 0)/1000:.1f}", "1.0-4.0", "x10³/μL"],
            ["Monocytes#", f"{blood_values.get('monocytes', 0)/1000:.1f}", "0.2-0.8", "x10³/μL"],
            ["Platelets", f"{blood_values.get('platelets', 0)/1000:.0f}", "150-450", "x10³/μL"],
        ]
        
        cbc_table = Table(cbc_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch])
        cbc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(cbc_table)
        
        doc.build(story)
        return filepath
    
    def generate_invalid_file(self, filename: str) -> Path:
        """Generate an invalid PDF file for error testing."""
        filepath = self.output_dir / filename
        
        # Create a file that's not a valid PDF
        with open(filepath, 'w') as f:
            f.write("This is not a valid PDF file.\n")
            f.write("It contains text but no PDF structure.\n")
            f.write("This should cause parsing errors.\n")
        
        return filepath
    
    def generate_all_test_pdfs(self) -> Dict[str, Path]:
        """Generate all test PDF files."""
        from mock_data import BloodTestDataGenerator, PatientDataGenerator
        
        generated_files = {}
        
        # Standard report
        generated_files['standard'] = self.generate_standard_report(
            "standard_lab_report.pdf",
            BloodTestDataGenerator.normal_values(),
            PatientDataGenerator.young_adult_male()
        )
        
        # Scanned report
        generated_files['scanned'] = self.generate_scanned_report(
            "scanned_lab_report.pdf", 
            BloodTestDataGenerator.high_inflammation_values(),
            PatientDataGenerator.elderly_female()
        )
        
        # Multi-page report
        generated_files['multipage'] = self.generate_multipage_report(
            "multipage_lab_report.pdf",
            BloodTestDataGenerator.low_inflammation_values(),
            PatientDataGenerator.middle_aged_female()
        )
        
        # High inflammation report
        generated_files['high_inflammation'] = self.generate_standard_report(
            "high_inflammation_report.pdf",
            BloodTestDataGenerator.high_inflammation_values(),
            PatientDataGenerator.middle_aged_male()
        )
        
        # Edge case - extreme values
        generated_files['extreme_values'] = self.generate_standard_report(
            "extreme_values_report.pdf",
            BloodTestDataGenerator.extreme_high_values(),
            PatientDataGenerator.young_adult_female()
        )
        
        # Invalid file
        generated_files['invalid'] = self.generate_invalid_file("invalid_file.pdf")
        
        return generated_files


def generate_test_pdfs(output_dir: Path) -> Dict[str, Path]:
    """Convenience function to generate all test PDFs."""
    generator = BloodTestPDFGenerator(output_dir)
    return generator.generate_all_test_pdfs()


if __name__ == "__main__":
    # Generate test PDFs when run directly
    test_dir = Path(__file__).parent / "sample_pdfs"
    files = generate_test_pdfs(test_dir)
    print(f"Generated {len(files)} test PDF files:")
    for name, path in files.items():
        print(f"  {name}: {path}")