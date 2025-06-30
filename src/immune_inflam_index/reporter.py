"""
Report generation functionality for immune inflammatory index results.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors


def generate_report(results: Dict[str, Any], format_type: str = "pdf") -> str:
    """
    Generate a formatted report from calculation results.
    
    Args:
        results: Complete results dictionary
        format_type: Output format ("pdf", "json", "text")
    
    Returns:
        Formatted report content
    """
    if format_type == "pdf":
        return _generate_pdf_content(results)
    elif format_type == "json":
        return _generate_json_content(results)
    elif format_type == "text":
        return _generate_text_content(results)
    else:
        raise ValueError(f"Unsupported format type: {format_type}")


def save_results(results: Dict[str, Any], output_dir: str, format_type: str = "pdf") -> str:
    """
    Save results to file in specified format.
    
    Args:
        results: Complete results dictionary
        output_dir: Directory to save the file
        format_type: Output format ("pdf", "json", "text")
    
    Returns:
        Path to the saved file
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format_type == "pdf":
        filename = f"immune_inflammatory_report_{timestamp}.pdf"
        filepath = output_path / filename
        _save_pdf_report(results, str(filepath))
        
    elif format_type == "json":
        filename = f"immune_inflammatory_results_{timestamp}.json"
        filepath = output_path / filename
        content = _generate_json_content(results)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
    elif format_type == "text":
        filename = f"immune_inflammatory_report_{timestamp}.txt"
        filepath = output_path / filename
        content = _generate_text_content(results)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
    else:
        raise ValueError(f"Unsupported format type: {format_type}")
    
    return str(filepath)


def _generate_pdf_content(results: Dict[str, Any]) -> str:
    """Generate PDF report content structure."""
    # This returns a description of what would be in the PDF
    # The actual PDF generation is handled by _save_pdf_report
    sections = []
    
    sections.append("# Immune Inflammatory Index Report")
    sections.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if "pdf_parsing" in results:
        sections.append("\n## PDF Source Information")
        pdf_info = results["pdf_parsing"]
        sections.append(f"Extraction Method: {pdf_info['extraction_method']}")
        
    sections.append("\n## Calculated Indices")
    for index_name, data in results.get("results", {}).items():
        sections.append(f"{index_name.upper()}: {data['value']} ({data['risk_level']})")
    
    return "\n".join(sections)


def _save_pdf_report(results: Dict[str, Any], filepath: str):
    """Save results as a PDF report using ReportLab."""
    doc = SimpleDocTemplate(filepath, pagesize=letter, topMargin=1*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2E4057'),
        spaceAfter=20
    )
    story.append(Paragraph("Immune Inflammatory Index Report", title_style))
    story.append(Spacer(1, 12))
    
    # Report metadata
    story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    
    if "pdf_parsing" in results:
        pdf_info = results["pdf_parsing"]
        story.append(Paragraph(f"<b>PDF Source:</b> {results.get('metadata', {}).get('pdf_source', 'Unknown')}", styles['Normal']))
        story.append(Paragraph(f"<b>Extraction Method:</b> {pdf_info['extraction_method']}", styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # Results table
    story.append(Paragraph("Calculated Indices", styles['Heading2']))
    
    table_data = [['Index', 'Value', 'Risk Level', 'Interpretation']]
    
    for index_name, data in results.get("results", {}).items():
        risk_level = data["risk_level"].replace("_", " ").title()
        interpretation = data["interpretation"][:60] + "..." if len(data["interpretation"]) > 60 else data["interpretation"]
        
        table_data.append([
            index_name.upper(),
            str(data["value"]),
            risk_level,
            interpretation
        ])
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Overall assessment
    if "summary" in results:
        story.append(Paragraph("Overall Assessment", styles['Heading2']))
        summary = results["summary"]
        story.append(Paragraph(summary["overall_inflammatory_status"], styles['Normal']))
        
        if summary.get("recommendations"):
            story.append(Spacer(1, 12))
            story.append(Paragraph("Key Recommendations:", styles['Heading3']))
            for i, rec in enumerate(summary["recommendations"][:5], 1):
                story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
    
    # Interpretation details
    if "interpretation" in results:
        story.append(Spacer(1, 20))
        story.append(Paragraph("Clinical Interpretation", styles['Heading2']))
        
        interp = results["interpretation"]
        
        # Risk stratification
        if "risk_stratification" in interp:
            risk_info = interp["risk_stratification"]
            story.append(Paragraph(f"<b>Overall Risk Level:</b> {risk_info['overall_risk_level'].replace('_', ' ').title()}", styles['Normal']))
            story.append(Paragraph(f"<b>Urgency:</b> {risk_info['urgency'].replace('_', ' ').title()}", styles['Normal']))
        
        # Patient context and demographics
        if "patient_context" in interp and interp["patient_context"]:
            story.append(Spacer(1, 12))
            story.append(Paragraph("Patient Demographics & Clinical Context", styles['Heading3']))
            
            context = interp["patient_context"]
            if context.get("age"):
                age = context['age']
                story.append(Paragraph(f"<b>Patient Age:</b> {age} years", styles['Normal']))
                
                # Determine age group for clinical context
                if age < 18:
                    age_group = "Pediatric"
                elif 18 <= age < 35:
                    age_group = "Young Adult (18-35)"
                elif 35 <= age < 65:
                    age_group = "Middle-aged Adult (35-65)"
                else:
                    age_group = "Elderly Adult (65+)"
                    
                story.append(Paragraph(f"<b>Age Group:</b> {age_group}", styles['Normal']))
                
            if context.get("sex"):
                story.append(Paragraph(f"<b>Patient Sex:</b> {context['sex']}", styles['Normal']))
            
            # Add age-specific considerations
            if context.get("age_considerations"):
                story.append(Spacer(1, 6))
                story.append(Paragraph("<b>Age-Specific Clinical Considerations:</b>", styles['Normal']))
                for consideration in context["age_considerations"]:
                    story.append(Paragraph(f"• {consideration}", styles['Normal']))
            
            # Add sex-specific considerations
            if context.get("sex_considerations"):
                story.append(Spacer(1, 6))
                story.append(Paragraph("<b>Sex-Specific Clinical Considerations:</b>", styles['Normal']))
                for consideration in context["sex_considerations"]:
                    story.append(Paragraph(f"• {consideration}", styles['Normal']))
    
    # PDF parsing details
    if "pdf_parsing" in results and results["pdf_parsing"].get("confidence_scores"):
        story.append(Spacer(1, 20))
        story.append(Paragraph("PDF Extraction Details", styles['Heading2']))
        
        # Extraction confidence table
        confidence_data = [['Field', 'Confidence Score', 'Status']]
        for field, score in results["pdf_parsing"]["confidence_scores"].items():
            status = "High" if score >= 80 else "Medium" if score >= 60 else "Low"
            confidence_data.append([field.title().replace('_', ' '), f"{score}%", status])
        
        confidence_table = Table(confidence_data)
        confidence_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(confidence_table)
        
        # Add demographic extraction details if available
        if "patient_demographics" in results["pdf_parsing"]:
            story.append(Spacer(1, 12))
            story.append(Paragraph("Auto-Extracted Patient Demographics", styles['Heading3']))
            
            demographics = results["pdf_parsing"]["patient_demographics"]
            demo_data = [['Field', 'Extracted Value', 'Confidence', 'Source Text']]
            
            for field, data in demographics.items():
                if data.get("value"):
                    confidence = data.get("confidence", 0)
                    status = "✓" if confidence >= 80 else "⚠" if confidence >= 60 else "✗"
                    demo_data.append([
                        field.title(),
                        str(data["value"]),
                        f"{confidence}% {status}",
                        data.get("raw_text", "")[:40] + ("..." if len(data.get("raw_text", "")) > 40 else "")
                    ])
            
            if len(demo_data) > 1:  # If we have data beyond header
                demo_table = Table(demo_data)
                demo_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(demo_table)
    
    # Warnings and disclaimers
    story.append(Spacer(1, 20))
    story.append(Paragraph("Important Disclaimers", styles['Heading2']))
    
    disclaimers = [
        "These indices are screening tools, not diagnostic tests",
        "Results must be interpreted in clinical context by qualified healthcare providers",
        "Consult your healthcare provider for medical decisions and treatment plans",
        "Serial measurements over time are more valuable than single values",
        "This report is for informational purposes only"
    ]
    
    for disclaimer in disclaimers:
        story.append(Paragraph(f"• {disclaimer}", styles['Normal']))
    
    doc.build(story)


def _generate_json_content(results: Dict[str, Any]) -> str:
    """Generate JSON format report."""
    # Clean up the results for JSON serialization
    json_results = {
        "report_metadata": {
            "generated_timestamp": datetime.now().isoformat(),
            "report_type": "immune_inflammatory_index",
            "version": "1.0"
        },
        "results": results.get("results", {}),
        "summary": results.get("summary", {}),
        "interpretation": results.get("interpretation", {}),
        "pdf_parsing": results.get("pdf_parsing", {}),
        "metadata": results.get("metadata", {})
    }
    
    return json.dumps(json_results, indent=2, ensure_ascii=False)


def _generate_text_content(results: Dict[str, Any]) -> str:
    """Generate plain text format report."""
    lines = []
    
    lines.append("=" * 60)
    lines.append("IMMUNE INFLAMMATORY INDEX REPORT")
    lines.append("=" * 60)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # PDF source info
    if "pdf_parsing" in results:
        lines.append("PDF SOURCE INFORMATION")
        lines.append("-" * 30)
        pdf_info = results["pdf_parsing"]
        lines.append(f"Source: {results.get('metadata', {}).get('pdf_source', 'Unknown')}")
        lines.append(f"Extraction Method: {pdf_info['extraction_method']}")
        lines.append("")
    
    # Results
    lines.append("CALCULATED INDICES")
    lines.append("-" * 30)
    
    for index_name, data in results.get("results", {}).items():
        lines.append(f"{index_name.upper()}: {data['value']}")
        lines.append(f"  Risk Level: {data['risk_level'].replace('_', ' ').title()}")
        lines.append(f"  Interpretation: {data['interpretation']}")
        lines.append("")
    
    # Overall assessment
    if "summary" in results:
        lines.append("OVERALL ASSESSMENT")
        lines.append("-" * 30)
        summary = results["summary"]
        lines.append(summary["overall_inflammatory_status"])
        lines.append("")
        
        if summary.get("recommendations"):
            lines.append("RECOMMENDATIONS:")
            for i, rec in enumerate(summary["recommendations"], 1):
                lines.append(f"{i}. {rec}")
            lines.append("")
    
    # Clinical interpretation
    if "interpretation" in results:
        lines.append("CLINICAL INTERPRETATION")
        lines.append("-" * 30)
        
        interp = results["interpretation"]
        
        # Risk stratification
        if "risk_stratification" in interp:
            risk_info = interp["risk_stratification"]
            lines.append(f"Overall Risk Level: {risk_info['overall_risk_level'].replace('_', ' ').title()}")
            lines.append(f"Urgency: {risk_info['urgency'].replace('_', ' ').title()}")
            lines.append("")
        
        # Patient context and demographics
        if "patient_context" in interp and interp["patient_context"]:
            context = interp["patient_context"]
            if context.get("age") or context.get("sex"):
                lines.append("PATIENT DEMOGRAPHICS & CLINICAL CONTEXT")
                lines.append("-" * 50)
                
                if context.get("age"):
                    age = context['age']
                    lines.append(f"Age: {age} years")
                    
                    # Determine age group
                    if age < 18:
                        age_group = "Pediatric"
                    elif 18 <= age < 35:
                        age_group = "Young Adult (18-35)"
                    elif 35 <= age < 65:
                        age_group = "Middle-aged Adult (35-65)"
                    else:
                        age_group = "Elderly Adult (65+)"
                        
                    lines.append(f"Age Group: {age_group}")
                    
                if context.get("sex"):
                    lines.append(f"Sex: {context['sex']}")
                
                # Add age-specific considerations
                if context.get("age_considerations"):
                    lines.append("")
                    lines.append("Age-Specific Clinical Considerations:")
                    for consideration in context["age_considerations"]:
                        lines.append(f"  • {consideration}")
                
                # Add sex-specific considerations
                if context.get("sex_considerations"):
                    lines.append("")
                    lines.append("Sex-Specific Clinical Considerations:")
                    for consideration in context["sex_considerations"]:
                        lines.append(f"  • {consideration}")
                        
                lines.append("")
    
    # PDF extraction confidence
    if "pdf_parsing" in results and results["pdf_parsing"].get("confidence_scores"):
        lines.append("EXTRACTION CONFIDENCE")
        lines.append("-" * 30)
        
        for field, score in results["pdf_parsing"]["confidence_scores"].items():
            status = "High" if score >= 80 else "Medium" if score >= 60 else "Low"
            lines.append(f"{field.title()}: {score}% ({status})")
        lines.append("")
    
    # Warnings
    all_warnings = []
    if "metadata" in results and results["metadata"].get("warnings"):
        all_warnings.extend(results["metadata"]["warnings"])
    if "pdf_parsing" in results and results["pdf_parsing"].get("parsing_warnings"):
        all_warnings.extend(results["pdf_parsing"]["parsing_warnings"])
    
    if all_warnings:
        lines.append("WARNINGS")
        lines.append("-" * 30)
        for warning in all_warnings:
            lines.append(f"⚠️  {warning}")
        lines.append("")
    
    # Disclaimers
    lines.append("IMPORTANT DISCLAIMERS")
    lines.append("-" * 30)
    disclaimers = [
        "These indices are screening tools, not diagnostic tests",
        "Results must be interpreted in clinical context by qualified healthcare providers",
        "Consult your healthcare provider for medical decisions and treatment plans",
        "Serial measurements over time are more valuable than single values",
        "This report is for informational purposes only"
    ]
    
    for disclaimer in disclaimers:
        lines.append(f"• {disclaimer}")
    
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)