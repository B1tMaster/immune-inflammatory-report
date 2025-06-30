"""
Command line interface for the Immune Inflammatory Index calculator.
"""

import click
import json
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from . import __version__
from .pdf_parser import process_pdf, manual_fallback_mode, PDFParsingError
from .calculator import calculate_indices
from .reporter import generate_report, save_results


console = Console()


@click.group()
@click.version_option(version=__version__)
def main():
    """
    Immune Inflammatory Index Calculator with PDF Parsing
    
    Calculate immune inflammatory indices from blood test PDFs or manual input.
    Supports automatic extraction from laboratory reports with confidence scoring.
    """
    pass


@main.command()
@click.argument('pdf_path', type=click.Path(exists=True))
@click.option('--output-dir', '-o', type=click.Path(), help='Output directory for results')
@click.option('--patient-age', type=int, help='Patient age for interpretation')
@click.option('--patient-sex', type=click.Choice(['M', 'F'], case_sensitive=False), help='Patient sex (M/F)')
@click.option('--format', 'output_format', type=click.Choice(['pdf', 'json', 'text']), default='pdf', help='Output format')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output with detailed information')
def process_pdf_cmd(pdf_path: str, output_dir: Optional[str], patient_age: Optional[int], 
                   patient_sex: Optional[str], output_format: str, verbose: bool):
    """Process a PDF blood test report and calculate inflammatory indices."""
    
    try:
        with console.status("[bold green]Processing PDF...") as status:
            status.update("[bold green]Extracting text from PDF...")
            
            results = process_pdf(
                pdf_file_path=pdf_path,
                output_directory=output_dir,
                patient_age=patient_age,
                patient_sex=patient_sex.upper() if patient_sex else None
            )
            
            status.update("[bold green]Generating report...")
            
            # Save results
            output_path = save_results(results, output_dir or ".", output_format)
            
        # Display results
        _display_results(results, verbose)
        
        console.print(f"\n[bold green]✓[/bold green] Results saved to: {output_path}")
        
        # Check for warnings
        if results["pdf_parsing"]["manual_verification_needed"]:
            console.print("\n[yellow]⚠️  Manual verification recommended - some values had low confidence[/yellow]")
        
    except PDFParsingError as e:
        console.print(f"\n[red]PDF parsing failed: {e}[/red]")
        
        if e.extracted_text:
            console.print("\n[yellow]Attempting manual fallback...[/yellow]")
            try:
                manual_values = manual_fallback_mode(e.extracted_text, e.missing_fields)
                
                # Calculate with manual values
                results = calculate_indices(**manual_values)
                
                # Display results
                _display_results(results, verbose)
                
                # Save results
                output_path = save_results(results, output_dir or ".", output_format)
                console.print(f"\n[bold green]✓[/bold green] Results saved to: {output_path}")
                
            except KeyboardInterrupt:
                console.print("\n[red]Operation cancelled by user[/red]")
            except Exception as fallback_error:
                console.print(f"\n[red]Manual fallback failed: {fallback_error}[/red]")
    
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")


@main.command()
@click.option('--neutrophils', type=float, required=True, help='Neutrophil count (cells/µL)')
@click.option('--lymphocytes', type=float, required=True, help='Lymphocyte count (cells/µL)')
@click.option('--platelets', type=float, required=True, help='Platelet count (cells/µL)')
@click.option('--monocytes', type=float, help='Monocyte count (cells/µL) [optional]')
@click.option('--output-dir', '-o', type=click.Path(), help='Output directory for results')
@click.option('--patient-age', type=int, help='Patient age for interpretation')
@click.option('--patient-sex', type=click.Choice(['M', 'F'], case_sensitive=False), help='Patient sex (M/F)')
@click.option('--format', 'output_format', type=click.Choice(['pdf', 'json', 'text']), default='text', help='Output format')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output with detailed information')
def manual_input(neutrophils: float, lymphocytes: float, platelets: float, 
                monocytes: Optional[float], output_dir: Optional[str], 
                patient_age: Optional[int], patient_sex: Optional[str], 
                output_format: str, verbose: bool):
    """Calculate indices from manually entered CBC values."""
    
    try:
        with console.status("[bold green]Calculating indices..."):
            results = calculate_indices(
                neutrophils=neutrophils,
                lymphocytes=lymphocytes,
                platelets=platelets,
                monocytes=monocytes
            )
            
            # Add interpretation if patient context provided
            if patient_age or patient_sex:
                from .interpreter import interpret_results
                interpretation = interpret_results(
                    results["results"],
                    patient_age=patient_age,
                    patient_sex=patient_sex.upper() if patient_sex else None
                )
                results["interpretation"] = interpretation
        
        # Display results
        _display_results(results, verbose)
        
        # Save results if output directory specified
        if output_dir:
            output_path = save_results(results, output_dir, output_format)
            console.print(f"\n[bold green]✓[/bold green] Results saved to: {output_path}")
        
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")


@main.command()
@click.option('--guide', is_flag=True, help='Show detailed interpretation guide')
def interpret(guide: bool):
    """Show interpretation guide for inflammatory indices."""
    
    if guide:
        _show_interpretation_guide()
    else:
        console.print("Use --guide flag to see detailed interpretation guide")


@main.command()
def supported_formats():
    """Show supported PDF formats and laboratory types."""
    
    from .constants import SUPPORTED_LAB_FORMATS
    
    console.print(Panel(
        "\n".join([
            "Supported Laboratory Formats:",
            "",
            "✓ Innoquest Diagnostics (Singapore)",
            "✓ Generic CBC formats with standard terminology",
            "✓ Text-based PDFs with extractable content",
            "✓ Scanned PDFs (requires OCR)",
            "",
            "Field Name Variations Supported:",
            "• Neutrophils: Neutrophils, Segs, Segmented Neutrophils, PMN",
            "• Lymphocytes: Lymphocytes, Lymphs, Lympho",
            "• Platelets: Platelets, PLT, Thrombocytes",
            "• Monocytes: Monocytes, Monos, Mono",
            "",
            "Unit Formats Supported:",
            "• x10³/L, x10^3/L (scientific notation)",
            "• K/µL, K/uL (thousands per microliter)",
            "• cells/µL, cells/uL (absolute counts)",
            "• Automatic unit conversion to cells/µL"
        ]),
        title="Supported Formats",
        style="blue"
    ))


def _display_results(results: dict, verbose: bool = False):
    """Display calculation results in formatted tables."""
    
    # Main results table
    table = Table(title="Immune Inflammatory Indices", show_header=True, header_style="bold magenta")
    table.add_column("Index", style="cyan", no_wrap=True)
    table.add_column("Value", justify="right")
    table.add_column("Risk Level", justify="center")
    table.add_column("Interpretation", style="dim")
    
    for index_name, data in results.get("results", {}).items():
        risk_color = {
            "normal": "green",
            "mild": "yellow",
            "moderate": "orange",
            "high": "red",
            "very_high": "bright_red"
        }.get(data["risk_level"], "white")
        
        table.add_row(
            index_name.upper(),
            str(data["value"]),
            Text(data["risk_level"].replace("_", " ").title(), style=risk_color),
            data["interpretation"][:60] + "..." if len(data["interpretation"]) > 60 else data["interpretation"]
        )
    
    console.print(table)
    
    # Summary
    if "summary" in results:
        summary = results["summary"]
        console.print(Panel(
            summary["overall_inflammatory_status"],
            title="Overall Assessment",
            style="blue"
        ))
        
        if summary.get("recommendations"):
            console.print("\n[bold]Recommendations:[/bold]")
            for rec in summary["recommendations"][:3]:  # Show first 3
                console.print(f"• {rec}")
    
    # PDF parsing info (if applicable)
    if "pdf_parsing" in results and verbose:
        pdf_info = results["pdf_parsing"]
        
        console.print(f"\n[bold]PDF Parsing Details:[/bold]")
        console.print(f"Extraction method: {pdf_info['extraction_method']}")
        
        if pdf_info["confidence_scores"]:
            console.print("\nConfidence scores:")
            for field, score in pdf_info["confidence_scores"].items():
                color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
                console.print(f"  {field}: [{color}]{score}%[/{color}]")
    
    # Warnings
    warnings = []
    if "metadata" in results and results["metadata"].get("warnings"):
        warnings.extend(results["metadata"]["warnings"])
    if "pdf_parsing" in results and results["pdf_parsing"].get("parsing_warnings"):
        warnings.extend(results["pdf_parsing"]["parsing_warnings"])
    
    if warnings:
        console.print(f"\n[yellow]Warnings:[/yellow]")
        for warning in warnings:
            console.print(f"⚠️  {warning}")


def _show_interpretation_guide():
    """Show detailed interpretation guide."""
    
    guide_text = """
[bold]Immune Inflammatory Index Interpretation Guide[/bold]

[bold cyan]Systemic Immune-Inflammation Index (SII)[/bold cyan]
Formula: (Neutrophils × Platelets) / Lymphocytes
• Normal: < 500 - Balanced immune-inflammatory state
• Mild: 500-800 - Early inflammatory response
• Moderate: 800-1200 - Active inflammatory condition
• High: 1200-2000 - Serious inflammatory burden
• Very High: > 2000 - Critical inflammatory state

[bold cyan]Neutrophil-to-Lymphocyte Ratio (NLR)[/bold cyan]
Formula: Neutrophils / Lymphocytes
• Normal: < 2.0 - Healthy immune balance
• Mild: 2.0-3.0 - Early immune activation
• Moderate: 3.0-5.0 - Active inflammatory process
• High: 5.0-8.0 - Significant immune burden
• Very High: > 8.0 - Critical immune state

[bold cyan]Platelet-to-Lymphocyte Ratio (PLR)[/bold cyan]
Formula: Platelets / Lymphocytes
• Normal: < 150 - Normal hemostatic balance
• Mild: 150-200 - Mildly elevated thrombotic risk
• Moderate: 200-300 - Moderate thrombotic risk
• High: > 300 - High thrombotic risk

[bold yellow]Clinical Actions by Risk Level:[/bold yellow]
• Normal: Routine monitoring, maintain healthy lifestyle
• Mild: Lifestyle interventions, regular monitoring
• Moderate: Medical evaluation, consider interventions
• High: Urgent medical evaluation, active treatment
• Very High: Immediate medical attention required

[bold red]⚠️  Important Disclaimers:[/bold red]
• These indices are screening tools, not diagnostic tests
• Results must be interpreted in clinical context
• Consult healthcare provider for medical decisions
• Serial measurements more valuable than single values
"""
    
    console.print(Panel(guide_text, title="Clinical Interpretation Guide", style="blue"))


if __name__ == "__main__":
    main()