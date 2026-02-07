"""
Command-line interface for BTR-TOOLS.

This module provides the main CLI entry point and command structure
for the Btrieve file analysis toolkit.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from btrtools.core.btrieve import BtrieveAnalyzer, BtrieveFileInfo
from btrtools.utils.logging import logger, error_handler, safe_execute, create_error_context, BTRError

# Global console for rich output
console = Console()


def print_success(message: str, use_rich: bool = False):
    """Print success message with optional rich formatting."""
    if use_rich:
        console.print(f"✅ {message}", style="green")
    else:
        print(f"SUCCESS: {message}")


def print_error(message: str, use_rich: bool = False):
    """Print error message with optional rich formatting."""
    if use_rich:
        console.print(f"❌ {message}", style="red")
    else:
        print(f"ERROR: {message}")


def print_warning(message: str, use_rich: bool = False):
    """Print warning message with optional rich formatting."""
    if use_rich:
        console.print(f"⚠️  {message}", style="yellow")
    else:
        print(f"WARNING: {message}")


def print_info(message: str, use_rich: bool = False):
    """Print info message with optional rich formatting."""
    if use_rich:
        console.print(f"ℹ️  {message}", style="blue")
    else:
        print(f"INFO: {message}")


def create_progress_bar(description: str = "Processing"):
    """Create a progress bar for long-running operations."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    )


def display_file_info_rich(info: BtrieveFileInfo):
    """Display file information using rich formatting."""
    table = Table(title="Btrieve File Analysis Results")
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    table.add_row("Filename", info.filename)
    table.add_row("File Size", f"{info.file_size:,} bytes")
    table.add_row("Page Size", f"{info.page_size:,} bytes")
    table.add_row("Header Size", f"{info.header_size:,} bytes")
    table.add_row("FCR Pages", str(info.fcr_pages))
    table.add_row("ASCII Content", f"{info.ascii_percentage:.1f}%")
    table.add_row("Digit Sequences", str(info.digit_sequences))
    table.add_row("Date Patterns", str(info.date_patterns))

    if hasattr(info, 'detected_record_size') and info.detected_record_size:
        table.add_row("Detected Record Size", f"{info.detected_record_size:,} bytes")
        if hasattr(info, 'estimated_records') and info.estimated_records:
            table.add_row("Estimated Records", f"{info.estimated_records:,}")

    console.print(table)


def display_integrity_results_rich(result: dict):
    """Display integrity check results using rich formatting."""
    if result.get('corruption_detected', False):
        console.print(Panel.fit(
            "[red]INTEGRITY CHECK FAILED[/red]\n\n" +
            "\n".join(f"• {detail}" for detail in result.get('corruption_details', [])),
            title="❌ Integrity Issues",
            border_style="red"
        ))
    else:
        checks = [
            ("File exists", result.get('file_exists', False)),
            ("File readable", result.get('readable', False)),
            ("Valid size", result.get('valid_size', False)),
            ("Has FCR pages", result.get('has_fcr_pages', False)),
        ]

        status_text = "\n".join(
            f"{'✅' if status else '❌'} {check}" for check, status in checks
        )

        console.print(Panel.fit(
            f"[green]All integrity checks passed![/green]\n\n{status_text}",
            title="✅ Integrity Check Passed",
            border_style="green"
        ))


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog='btrtools',
        description='Btrieve File Analysis Toolkit - Generic command-line tools for Btrieve database files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  btrtools analyze file.btr              # Analyze a specific Btrieve file
  btrtools analyze file.btr -P           # Analyze with progress display
  btrtools export file.btr --format csv  # Export data to CSV format
  btrtools compare file1.btr file2.btr   # Compare two Btrieve files
  btrtools check file.btr                # Check file integrity
  btrtools repair file.btr --validate-only  # Validate file integrity
  btrtools search file.btr --query "ABC"    # Search for text in records
  btrtools report file.btr --format html   # Generate HTML analysis report
  btrtools stats file.btr --benchmark      # Generate performance statistics
  btrtools batch *.btr --operation export --format csv  # Batch export multiple files

Debug Options:
  Set BTRTOOLS_LOG_LEVEL=DEBUG for detailed logging
  Set BTRTOOLS_LOG_LEVEL=INFO for normal operation (default)
        """
    )

    parser.add_argument(
        '--version',
        action='version',
        version='BTR-TOOLS v2.2.0'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    parser.add_argument(
        '--progress', '-P',
        action='store_true',
        help='Show progress bars and rich output'
    )

    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands'
    )

    # Scan command
    scan_parser = subparsers.add_parser(
        'scan',
        help='Scan directory for Btrieve files'
    )
    scan_parser.add_argument(
        'directory',
        help='Directory to scan for Btrieve files'
    )
    scan_parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Scan subdirectories recursively'
    )
    scan_parser.add_argument(
        '--output', '-o',
        help='Output file for results (default: stdout)'
    )

    # Analyze command
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze a Btrieve file structure and content'
    )
    analyze_parser.add_argument(
        'file',
        help='Btrieve file to analyze'
    )
    analyze_parser.add_argument(
        '--max-records', '-n',
        type=int,
        default=100,
        help='Maximum records to analyze (default: 100)'
    )
    analyze_parser.add_argument(
        '--output', '-o',
        help='Output file for analysis (default: stdout)'
    )

    # Export command
    export_parser = subparsers.add_parser(
        'export',
        help='Export Btrieve data to various formats'
    )
    export_parser.add_argument(
        'file',
        help='Btrieve file to export'
    )
    export_parser.add_argument(
        '--format', '-f',
        choices=['csv', 'jsonl', 'sqlite', 'excel'],
        default='csv',
        help='Export format (default: csv)'
    )
    export_parser.add_argument(
        '--record-size', '-s',
        type=int,
        help='Record size (auto-detect if not specified)'
    )
    export_parser.add_argument(
        '--max-records', '-n',
        type=int,
        help='Maximum records to export (default: all)'
    )
    export_parser.add_argument(
        '--output', '-o',
        help='Output file (default: based on input filename)'
    )

    # Schema command
    schema_parser = subparsers.add_parser(
        'schema',
        help='Detect and display Btrieve file schema'
    )
    schema_parser.add_argument(
        'file',
        help='Btrieve file to analyze'
    )
    schema_parser.add_argument(
        '--record-size', '-s',
        type=int,
        help='Record size (auto-detect if not specified)'
    )
    schema_parser.add_argument(
        '--max-records', '-n',
        type=int,
        default=1000,
        help='Maximum records to analyze for schema detection (default: 1000)'
    )
    schema_parser.add_argument(
        '--output', '-o',
        help='Output file for schema (default: stdout)'
    )

    # Compare command
    compare_parser = subparsers.add_parser(
        'compare',
        help='Compare two Btrieve files'
    )
    compare_parser.add_argument(
        'file1',
        help='First Btrieve file to compare'
    )
    compare_parser.add_argument(
        'file2',
        help='Second Btrieve file to compare'
    )
    compare_parser.add_argument(
        '--max-records', '-n',
        type=int,
        default=100,
        help='Maximum records to compare (default: 100)'
    )
    compare_parser.add_argument(
        '--output', '-o',
        help='Output file for comparison results (default: stdout)'
    )

    # Batch command
    batch_parser = subparsers.add_parser(
        'batch',
        help='Process multiple Btrieve files in batch mode'
    )
    batch_parser.add_argument(
        'files',
        nargs='+',
        help='Btrieve files to process (supports glob patterns)'
    )
    batch_parser.add_argument(
        '--operation', '-op',
        choices=['analyze', 'export', 'schema', 'check'],
        default='analyze',
        help='Operation to perform on each file (default: analyze)'
    )
    batch_parser.add_argument(
        '--format', '-f',
        choices=['csv', 'jsonl', 'sqlite', 'excel'],
        help='Export format (required when operation is export)'
    )
    batch_parser.add_argument(
        '--output-dir', '-d',
        help='Output directory for results (default: current directory)'
    )
    batch_parser.add_argument(
        '--record-size', '-s',
        type=int,
        help='Record size (auto-detect if not specified)'
    )
    batch_parser.add_argument(
        '--max-records', '-n',
        type=int,
        help='Maximum records to process per file'
    )
    batch_parser.add_argument(
        '--parallel', '-p',
        type=int,
        default=1,
        help='Number of parallel processes (default: 1)'
    )

    # Repair command
    repair_parser = subparsers.add_parser(
        'repair',
        help='Validate and repair Btrieve file data integrity'
    )
    repair_parser.add_argument(
        'file',
        help='Btrieve file to repair'
    )
    repair_parser.add_argument(
        '--output', '-o',
        help='Output file for repaired data (default: <input>_repaired.btr)'
    )
    repair_parser.add_argument(
        '--record-size', '-s',
        type=int,
        help='Record size (auto-detect if not specified)'
    )
    repair_parser.add_argument(
        '--fix-corruption',
        action='store_true',
        help='Attempt to fix detected corruption'
    )
    repair_parser.add_argument(
        '--backup',
        action='store_true',
        help='Create backup of original file before repair'
    )
    repair_parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate, do not perform repairs'
    )

    # Search command
    search_parser = subparsers.add_parser(
        'search',
        help='Search and filter Btrieve file records'
    )
    search_parser.add_argument(
        'file',
        help='Btrieve file to search'
    )
    search_parser.add_argument(
        '--query', '-q',
        help='Search query (text to find in records)'
    )
    search_parser.add_argument(
        '--record-size', '-s',
        type=int,
        help='Record size (auto-detect if not specified)'
    )
    search_parser.add_argument(
        '--max-records', '-n',
        type=int,
        help='Maximum records to search (default: all)'
    )
    search_parser.add_argument(
        '--output', '-o',
        help='Output file for results (default: stdout)'
    )
    search_parser.add_argument(
        '--format', '-f',
        choices=['text', 'json', 'csv'],
        default='text',
        help='Output format (default: text)'
    )
    search_parser.add_argument(
        '--case-sensitive',
        action='store_true',
        help='Case-sensitive search'
    )
    search_parser.add_argument(
        '--regex',
        action='store_true',
        help='Treat query as regular expression'
    )
    search_parser.add_argument(
        '--invert-match', '-v',
        action='store_true',
        help='Invert match (show non-matching records)'
    )

    # Report command
    report_parser = subparsers.add_parser(
        'report',
        help='Generate data visualization and analysis reports'
    )
    report_parser.add_argument(
        'file',
        help='Btrieve file to analyze'
    )
    report_parser.add_argument(
        '--output', '-o',
        help='Output directory for reports (default: ./reports)'
    )
    report_parser.add_argument(
        '--record-size', '-s',
        type=int,
        help='Record size (auto-detect if not specified)'
    )
    report_parser.add_argument(
        '--max-records', '-n',
        type=int,
        help='Maximum records to analyze (default: 1000)'
    )
    report_parser.add_argument(
        '--format', '-f',
        choices=['html', 'json', 'text'],
        default='html',
        help='Report format (default: html)'
    )
    report_parser.add_argument(
        '--include-charts',
        action='store_true',
        help='Include data visualization charts (requires matplotlib)'
    )

    # Stats command
    stats_parser = subparsers.add_parser(
        'stats',
        help='Generate performance statistics and profiling data'
    )
    stats_parser.add_argument(
        'file',
        help='Btrieve file to analyze'
    )
    stats_parser.add_argument(
        '--record-size', '-s',
        type=int,
        help='Record size (auto-detect if not specified)'
    )
    stats_parser.add_argument(
        '--max-records', '-n',
        type=int,
        help='Maximum records to analyze (default: 1000)'
    )
    stats_parser.add_argument(
        '--output', '-o',
        help='Output file for statistics (default: stdout)'
    )
    stats_parser.add_argument(
        '--benchmark',
        action='store_true',
        help='Run performance benchmarks'
    )
    stats_parser.add_argument(
        '--memory-profile',
        action='store_true',
        help='Include memory usage profiling'
    )

    return parser


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging level
    if hasattr(args, 'debug') and (args.debug or os.environ.get('BTRTOOLS_LOG_LEVEL', '').upper() == 'DEBUG'):
        logger.set_level('DEBUG')
    else:
        log_level = os.environ.get('BTRTOOLS_LOG_LEVEL', 'INFO').upper()
        logger.set_level(log_level)

    # Check if rich output is requested
    use_rich = getattr(args, 'progress', False)

    if use_rich:
        console.print("[bold blue]BTR-TOOLS[/bold blue] - Btrieve File Analysis Toolkit", style="bold")
        console.print(f"Version 2.0.0 | Rich output enabled", style="dim")
    else:
        logger.info("BTR-TOOLS starting")

    if not hasattr(args, 'command') or not args.command:
        if use_rich:
            console.print("[red]No command specified. Use --help for usage information.[/red]")
        else:
            parser.print_help()
        return 1

    # Create error context
    context = create_error_context(args.command, vars(args))

    # Execute command with error handling
    try:
        if args.command == 'scan':
            exit_code = cmd_scan(args, use_rich)
        elif args.command == 'analyze':
            exit_code = cmd_analyze(args, use_rich)
        elif args.command == 'export':
            exit_code = cmd_export(args, use_rich)
        elif args.command == 'schema':
            exit_code = cmd_schema(args, use_rich)
        elif args.command == 'check':
            exit_code = cmd_check(args, use_rich)
        elif args.command == 'compare':
            exit_code = cmd_compare(args, use_rich)
        elif args.command == 'batch':
            exit_code = cmd_batch(args, use_rich)
        elif args.command == 'repair':
            exit_code = cmd_repair(args, use_rich)
        elif args.command == 'search':
            exit_code = cmd_search(args, use_rich)
        elif args.command == 'report':
            exit_code = cmd_report(args, use_rich)
        elif args.command == 'stats':
            exit_code = cmd_stats(args, use_rich)
        else:
            if use_rich:
                console.print(f"[red]Unknown command: {args.command}[/red]")
            else:
                print(f"Unknown command: {args.command}", file=sys.stderr)
                logger.error(f"Unknown command: {args.command}")
            return 1

        if use_rich:
            if exit_code == 0:
                console.print("\n[green]✓ Operation completed successfully[/green]")
            else:
                console.print(f"\n[red]✗ Operation failed with exit code {exit_code}[/red]")
        else:
            logger.info(f"BTR-TOOLS finished with exit code: {exit_code}")

        return exit_code

    except KeyboardInterrupt:
        if use_rich:
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
        else:
            logger.info("Operation cancelled by user")
        return 130
    except Exception as e:
        if use_rich:
            console.print(f"[red]Unexpected error: {e}[/red]")
        else:
            logger.error(f"Unexpected error: {e}")
        return 1


def cmd_scan(args, use_rich: bool = False) -> int:
    """Handle scan command."""
    from btrtools.cli.scan import scan_directory

    if use_rich:
        with create_progress_bar("Scanning directory") as progress:
            task = progress.add_task("Searching for Btrieve files...", total=100)
            progress.update(task, advance=25)

            results = scan_directory(args.directory, args.recursive)

            progress.update(task, advance=75, description=f"Found {len(results)} files...")
    else:
        logger.info(f"Scanning directory: {args.directory} (recursive: {args.recursive})")
        results = scan_directory(args.directory, args.recursive)
        logger.info(f"Scan complete: found {len(results)} potential Btrieve files")

    if use_rich:
        if results:
            table = Table(title=f"Btrieve Files Found ({len(results)})")
            table.add_column("Filename", style="cyan")
            table.add_column("Size", style="magenta", justify="right")
            table.add_column("ASCII %", style="green", justify="right")
            table.add_column("Quality", style="yellow", justify="right")
            table.add_column("Path", style="blue", max_width=50)

            for result in results:
                table.add_row(
                    result.filename,
                    f"{result.file_size:,}",
                    f"{result.ascii_percentage:.1f}%",
                    f"{result.quality_score:.1f}",
                    result.filepath
                )

            console.print(table)
        else:
            print_info("No Btrieve files found in the specified directory", use_rich)
    else:
        if args.output:
            try:
                with open(args.output, 'w') as f:
                    f.write("Btrieve File Scan Results\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"Directory: {args.directory}\n")
                    f.write(f"Recursive: {args.recursive}\n")
                    f.write(f"Files found: {len(results)}\n\n")

                    for result in results:
                        f.write(f"File: {result.filename}\n")
                        f.write(f"Path: {result.filepath}\n")
                        f.write(f"Size: {result.file_size:,} bytes\n")
                        f.write(f"Content Type: {result.content_type}\n")
                        f.write(f"ASCII: {result.ascii_percentage:.1f}%\n")
                        f.write(f"Quality Score: {result.quality_score:.1f}\n")
                        f.write("-" * 40 + "\n")
                if use_rich:
                    print_success(f"Scan results written to: {args.output}", use_rich)
                else:
                    logger.info(f"Scan results written to: {args.output}")
            except Exception as e:
                if use_rich:
                    print_error(f"Failed to write output file: {e}", use_rich)
                else:
                    logger.error(f"Failed to write scan results to {args.output}: {e}")
                raise BTRError(f"Failed to write output file: {e}")
        else:
            print("Btrieve File Scan Results")
            print("=" * 50)
            print(f"Directory: {args.directory}")
            print(f"Recursive: {args.recursive}")
            print(f"Files found: {len(results)}")
            print()

            for result in results:
                print(f"File: {result.filename}")
                print(f"Path: {result.filepath}")
                print(f"Size: {result.file_size:,} bytes")
                print(f"Content Type: {result.content_type}")
                print(f"ASCII: {result.ascii_percentage:.1f}%")
                print(f"Quality Score: {result.quality_score:.1f}")
                print("-" * 40)

    return 0


def cmd_analyze(args, use_rich: bool = False) -> int:
    """Handle analyze command."""
    from btrtools.cli.analyze import analyze_file

    if use_rich:
        with create_progress_bar("Analyzing file") as progress:
            task = progress.add_task("Reading file structure...", total=100)
            progress.update(task, advance=25)

            result = analyze_file(args.file, args.max_records)

            progress.update(task, advance=75, description="Processing content patterns...")
    else:
        logger.info(f"Analyzing file: {args.file} (max_records: {args.max_records})")
        result = analyze_file(args.file, args.max_records)
        logger.info(f"Analysis complete for {args.file}")

    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write("Btrieve File Analysis Report\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"File: {result.filename}\n")
                f.write(f"Path: {result.filepath}\n")
                f.write(f"Size: {result.file_size:,} bytes\n")
                f.write(f"Content Type: {result.content_type}\n")
                f.write(f"ASCII Content: {result.ascii_percentage:.1f}%\n")
                f.write(f"Digit Sequences: {result.digit_sequences}\n")
                f.write(f"Date Patterns: {result.date_patterns}\n")
                f.write(f"Quality Score: {result.quality_score:.1f}\n")

                if result.detected_record_size:
                    f.write(f"Detected Record Size: {result.detected_record_size} bytes\n")
                if result.estimated_records:
                    f.write(f"Estimated Records: {result.estimated_records}\n")

            if use_rich:
                print_success(f"Analysis results written to: {args.output}", use_rich)
            else:
                logger.info(f"Analysis results written to: {args.output}")
        except Exception as e:
            if use_rich:
                print_error(f"Failed to write output file: {e}", use_rich)
            else:
                logger.error(f"Failed to write analysis results to {args.output}: {e}")
            raise BTRError(f"Failed to write output file: {e}")
    else:
        if use_rich:
            display_file_info_rich(result)
        else:
            print("Btrieve File Analysis Report")
            print("=" * 50)
            print(f"File: {result.filename}")
            print(f"Path: {result.filepath}")
            print(f"Size: {result.file_size:,} bytes")
            print(f"Content Type: {result.content_type}")
            print(f"ASCII Content: {result.ascii_percentage:.1f}%")
            print(f"Digit Sequences: {result.digit_sequences}")
            print(f"Date Patterns: {result.date_patterns}")
            print(f"Quality Score: {result.quality_score:.1f}")

            if result.detected_record_size:
                print(f"Detected Record Size: {result.detected_record_size} bytes")
            if result.estimated_records:
                print(f"Estimated Records: {result.estimated_records}")

    return 0


def cmd_export(args, use_rich: bool = False) -> int:
    """Handle export command."""
    from btrtools.cli.export import export_file

    if use_rich:
        with create_progress_bar("Exporting data") as progress:
            task = progress.add_task("Processing records...", total=100)
            progress.update(task, advance=25)

            output_file = export_file(
                args.file,
                args.format,
                args.record_size,
                args.max_records,
                args.output
            )

            progress.update(task, advance=75, description="Finalizing export...")
    else:
        logger.info(f"Exporting file: {args.file} (format: {args.format}, record_size: {args.record_size})")
        output_file = export_file(
            args.file,
            args.format,
            args.record_size,
            args.max_records,
            args.output
        )
        logger.info(f"Export complete: {output_file}")

    if use_rich:
        print_success(f"Successfully exported to: {output_file}", use_rich)
    else:
        print(f"Successfully exported to: {output_file}")
    return 0


def cmd_schema(args, use_rich: bool = False) -> int:
    """Handle schema command."""
    from btrtools.cli.schema import detect_schema

    if use_rich:
        with create_progress_bar("Detecting schema") as progress:
            task = progress.add_task("Analyzing record structure...", total=100)
            progress.update(task, advance=50)

            schema_info = detect_schema(
                args.file,
                args.record_size,
                args.max_records
            )

            progress.update(task, advance=50, description="Processing field definitions...")
    else:
        logger.info(f"Detecting schema for: {args.file} (record_size: {args.record_size}, max_records: {args.max_records})")
        schema_info = detect_schema(
            args.file,
            args.record_size,
            args.max_records
        )
        logger.info(f"Schema detection complete for {args.file}")

    if use_rich:
        # Create rich table for schema display
        table = Table(title="Detected Schema Fields")
        table.add_column("Field Name", style="cyan", no_wrap=True)
        table.add_column("Type", style="magenta")
        table.add_column("Position", style="green", justify="right")
        table.add_column("Length", style="yellow", justify="right")

        for field in schema_info['fields']:
            table.add_row(
                field['name'],
                field['type'],
                str(field['position']),
                str(field['length'])
            )

        console.print(Panel.fit(
            f"[bold]File:[/bold] {args.file}\n"
            f"[bold]Record Size:[/bold] {schema_info['record_size']} bytes\n"
            f"[bold]Records Analyzed:[/bold] {schema_info['records_analyzed']}",
            title="Schema Analysis Results"
        ))
        console.print(table)
    else:
        if args.output:
            try:
                with open(args.output, 'w') as f:
                    f.write("Btrieve File Schema Analysis\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"File: {args.file}\n")
                    f.write(f"Record Size: {schema_info['record_size']} bytes\n")
                    f.write(f"Records Analyzed: {schema_info['records_analyzed']}\n\n")
                    f.write("Detected Fields:\n")
                    for field in schema_info['fields']:
                        f.write(f"  {field['name']}: {field['type']} "
                               f"(position {field['position']}, "
                               f"length {field['length']})\n")
                if use_rich:
                    print_success(f"Schema results written to: {args.output}", use_rich)
                else:
                    logger.info(f"Schema results written to: {args.output}")
            except Exception as e:
                if use_rich:
                    print_error(f"Failed to write output file: {e}", use_rich)
                else:
                    logger.error(f"Failed to write schema results to {args.output}: {e}")
                raise BTRError(f"Failed to write output file: {e}")
        else:
            print("Btrieve File Schema Analysis")
            print("=" * 50)
            print(f"File: {args.file}")
            print(f"Record Size: {schema_info['record_size']} bytes")
            print(f"Records Analyzed: {schema_info['records_analyzed']}")
            print()
            print("Detected Fields:")
            for field in schema_info['fields']:
                print(f"  {field['name']}: {field['type']} "
                     f"(position {field['position']}, "
                     f"length {field['length']})")

    return 0


def cmd_compare(args, use_rich: bool = False) -> int:
    """Handle compare command."""
    from btrtools.cli.compare import compare_files

    if use_rich:
        with create_progress_bar("Comparing files") as progress:
            task = progress.add_task("Analyzing file structures...", total=100)
            progress.update(task, advance=50)

            comparison = compare_files(args.file1, args.file2, args.max_records)

            progress.update(task, advance=50, description="Generating comparison report...")
    else:
        logger.info(f"Comparing files: {args.file1} vs {args.file2}")
        comparison = compare_files(args.file1, args.file2, args.max_records)
        logger.info("Comparison complete")

    if use_rich:
        # Display comparison results with rich formatting
        from rich.panel import Panel
        from rich.text import Text

        # File info panel
        file_info = f"[bold]File 1:[/bold] {comparison['file1']['filename']} ({comparison['file1']['size']:,} bytes)\n"
        file_info += f"[bold]File 2:[/bold] {comparison['file2']['filename']} ({comparison['file2']['size']:,} bytes)"

        console.print(Panel.fit(file_info, title="Files Compared"))

        # Assessment
        assessment = comparison.get('assessment', 'unknown')
        if assessment == 'files_appear_identical':
            assessment_color = "green"
            assessment_icon = "✅"
        elif assessment == 'size_difference_only':
            assessment_color = "yellow"
            assessment_icon = "⚠️"
        elif assessment == 'minor_differences':
            assessment_color = "yellow"
            assessment_icon = "⚠️"
        else:
            assessment_color = "red"
            assessment_icon = "❌"

        console.print(f"\n{assessment_icon} Assessment: [{assessment_color}]{assessment.replace('_', ' ').title()}[/{assessment_color}]")

        # Differences table
        if comparison['differences']:
            diff_table = Table(title="Differences Found")
            diff_table.add_column("Property", style="cyan")
            diff_table.add_column("File 1", style="magenta")
            diff_table.add_column("File 2", style="green")
            diff_table.add_column("Difference", style="yellow")

            for prop, diff in comparison['differences'].items():
                if prop == 'file_size':
                    val1 = f"{diff['file1']:,}"
                    val2 = f"{diff['file2']:,}"
                    diff_val = f"{diff['difference']:,} bytes"
                elif prop in ['ascii_percentage', 'quality_score']:
                    val1 = f"{diff['file1']:.1f}"
                    val2 = f"{diff['file2']:.1f}"
                    diff_val = f"{diff['difference']:.1f}"
                else:
                    val1 = str(diff.get('file1', 'N/A'))
                    val2 = str(diff.get('file2', 'N/A'))
                    diff_val = "N/A"

                diff_table.add_row(prop.replace('_', ' ').title(), val1, val2, diff_val)

            console.print(diff_table)

        # Similarities
        if comparison['similarities']:
            sim_items = [f"{prop.replace('_', ' ').title()}: {value}"
                        for prop, value in comparison['similarities'].items()]
            console.print(Panel.fit("\n".join(sim_items), title="Similarities"))

        # Record comparison if available
        if 'record_comparison' in comparison:
            rec_comp = comparison['record_comparison']
            if 'record_sizes_different' in rec_comp:
                console.print(f"\n[red]Record sizes differ: {rec_comp['file1_record_size']} vs {rec_comp['file2_record_size']}[/red]")
            else:
                match_pct = rec_comp.get('match_percentage', 0)
                console.print(f"\n[yellow]Record Comparison:[/yellow] {rec_comp['identical_records']}/{rec_comp['total_compared']} records identical ({match_pct:.1f}%)")

    else:
        # Plain text output
        print("Btrieve File Comparison Results")
        print("=" * 50)
        print(f"File 1: {comparison['file1']['filename']} ({comparison['file1']['size']:,} bytes)")
        print(f"File 2: {comparison['file2']['filename']} ({comparison['file2']['size']:,} bytes)")
        print()

        assessment = comparison.get('assessment', 'unknown')
        print(f"Assessment: {assessment.replace('_', ' ').title()}")

        if comparison['differences']:
            print("\nDifferences:")
            for prop, diff in comparison['differences'].items():
                if prop == 'file_size':
                    print(f"  {prop}: {diff['file1']:,} vs {diff['file2']:,} (diff: {diff['difference']:,} bytes)")
                else:
                    print(f"  {prop}: {diff.get('file1', 'N/A')} vs {diff.get('file2', 'N/A')}")

        if comparison['similarities']:
            print("\nSimilarities:")
            for prop, value in comparison['similarities'].items():
                print(f"  {prop}: {value}")

        if 'record_comparison' in comparison:
            rec_comp = comparison['record_comparison']
            if 'record_sizes_different' in rec_comp:
                print(f"\nRecord sizes differ: {rec_comp['file1_record_size']} vs {rec_comp['file2_record_size']}")
            else:
                match_pct = rec_comp.get('match_percentage', 0)
                print(f"\nRecord comparison: {rec_comp['identical_records']}/{rec_comp['total_compared']} records identical ({match_pct:.1f}%)")

    # Write to output file if specified
    if args.output:
        try:
            import json
            with open(args.output, 'w') as f:
                json.dump(comparison, f, indent=2)
            if use_rich:
                print_success(f"Comparison results written to: {args.output}", use_rich)
            else:
                logger.info(f"Comparison results written to: {args.output}")
        except Exception as e:
            if use_rich:
                print_error(f"Failed to write output file: {e}", use_rich)
            else:
                logger.error(f"Failed to write comparison results to {args.output}: {e}")
            return 1

    return 0
    """Handle check command."""
    from btrtools.cli.check import check_integrity

    if use_rich:
        with create_progress_bar("Checking integrity") as progress:
            task = progress.add_task("Running integrity checks...", total=100)
            progress.update(task, advance=50)

            result = check_integrity(args.file, args.verbose)

            progress.update(task, advance=50, description="Analyzing results...")
    else:
        logger.info(f"Checking integrity of: {args.file} (verbose: {args.verbose})")
        result = check_integrity(args.file, args.verbose)
        logger.info(f"Integrity check complete for {args.file}")

    if use_rich:
        display_integrity_results_rich(result)
        return 1 if result.get('corruption_detected', False) else 0
    else:
        if result['corruption_detected']:
            logger.warning(f"Corruption detected in {args.file}")
            print("INTEGRITY CHECK FAILED")
            print("=" * 50)
            for detail in result['corruption_details']:
                print(f"ERROR: {detail}")
            return 1
        else:
            print("INTEGRITY CHECK PASSED")
            print("=" * 50)
            if args.verbose:
                print(f"File exists: {result['file_exists']}")
                print(f"Readable: {result['readable']}")
                print(f"Valid size: {result['valid_size']}")
                print(f"Has FCR pages: {result['has_fcr_pages']}")
                print(f"Data pages: {result['data_pages']}")
            return 0


def cmd_stats(args, use_rich: bool = False) -> int:
    """Handle stats command."""
    import time
    import psutil
    import os
    
    if use_rich:
        console.print(f"[bold]Generating performance statistics for:[/bold] {args.file}")
    else:
        logger.info(f"Generating performance statistics for: {args.file}")
    
    try:
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        start_time = time.time()
        
        # Analyze the file
        analyzer = BtrieveAnalyzer(args.file)
        
        # Auto-detect record size if not provided
        if args.record_size is None:
            record_size, _ = analyzer.detect_record_size()
            if record_size == 0:
                raise ValueError("Could not detect record size")
        else:
            record_size = args.record_size
        
        analysis_time = time.time() - start_time
        
        # Extract records
        extract_start = time.time()
        records = analyzer.extract_records(record_size, args.max_records or 1000)
        extract_time = time.time() - extract_start
        
        # Calculate statistics
        total_time = time.time() - start_time
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = final_memory - initial_memory
        
        stats = {
            'file_info': {
                'filename': args.file,
                'file_size': os.path.getsize(args.file),
                'record_size': record_size,
                'total_records': len(records)
            },
            'performance': {
                'total_time_seconds': total_time,
                'analysis_time_seconds': analysis_time,
                'extraction_time_seconds': extract_time,
                'records_per_second': len(records) / extract_time if extract_time > 0 else 0,
                'memory_used_mb': memory_used,
                'peak_memory_mb': final_memory
            },
            'data_quality': {
                'avg_record_size': sum(len(r.raw_bytes) for r in records) / len(records) if records else 0,
                'avg_printable_chars': sum(r.printable_chars for r in records) / len(records) if records else 0,
                'records_with_text': sum(1 for r in records if r.decoded_text.strip()),
                'records_with_digits': sum(1 for r in records if r.has_digits),
                'records_with_alpha': sum(1 for r in records if r.has_alpha)
            }
        }
        
        # Run benchmarks if requested
        if args.benchmark:
            if use_rich:
                console.print("[yellow]Running performance benchmarks...[/yellow]")
            
            benchmark_results = {}
            
            # Benchmark record extraction
            times = []
            for _ in range(3):
                start = time.time()
                analyzer.extract_records(record_size, min(100, len(records)) if records else 10)
                times.append(time.time() - start)
            
            benchmark_results['extraction_avg_time'] = sum(times) / len(times)
            benchmark_results['extraction_min_time'] = min(times)
            benchmark_results['extraction_max_time'] = max(times)
            
            stats['benchmarks'] = benchmark_results
        
        # Output results
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(stats, f, indent=2)
            if use_rich:
                print_success(f"Statistics written to: {args.output}", use_rich)
            else:
                logger.info(f"Statistics written to: {args.output}")
        else:
            # Console output
            if use_rich:
                table = Table(title="Performance Statistics")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="magenta")
                
                table.add_row("File Size", f"{stats['file_info']['file_size']:,} bytes")
                table.add_row("Total Records", str(stats['file_info']['total_records']))
                table.add_row("Record Size", f"{stats['file_info']['record_size']} bytes")
                table.add_row("Total Time", f"{stats['performance']['total_time_seconds']:.3f}s")
                table.add_row("Analysis Time", f"{stats['performance']['analysis_time_seconds']:.3f}s")
                table.add_row("Extraction Time", f"{stats['performance']['extraction_time_seconds']:.3f}s")
                table.add_row("Records/Second", f"{stats['performance']['records_per_second']:.1f}")
                table.add_row("Memory Used", f"{stats['performance']['memory_used_mb']:.1f} MB")
                table.add_row("Avg Record Size", f"{stats['data_quality']['avg_record_size']:.1f} bytes")
                table.add_row("Avg Printable", f"{stats['data_quality']['avg_printable_chars']:.1f} chars")
                
                console.print(table)
                
                if args.benchmark and 'benchmarks' in stats:
                    bench_table = Table(title="Benchmark Results")
                    bench_table.add_column("Test", style="cyan")
                    bench_table.add_column("Avg Time", style="green")
                    bench_table.add_column("Min Time", style="blue")
                    bench_table.add_column("Max Time", style="red")
                    
                    bench_table.add_row("Record Extraction", 
                                      f"{stats['benchmarks']['extraction_avg_time']:.4f}s",
                                      f"{stats['benchmarks']['extraction_min_time']:.4f}s", 
                                      f"{stats['benchmarks']['extraction_max_time']:.4f}s")
                    
                    console.print(bench_table)
            else:
                print("PERFORMANCE STATISTICS:")
                print(f"  File: {args.file}")
                print(f"  File Size: {stats['file_info']['file_size']:,} bytes")
                print(f"  Total Records: {stats['file_info']['total_records']}")
                print(f"  Total Time: {stats['performance']['total_time_seconds']:.3f}s")
                print(f"  Records/Second: {stats['performance']['records_per_second']:.1f}")
                print(f"  Memory Used: {stats['performance']['memory_used_mb']:.1f} MB")
        
        return 0
        
    except Exception as e:
        if use_rich:
            print_error(f"Statistics generation failed: {e}", use_rich)
        else:
            logger.error(f"Statistics generation failed: {e}")
        return 1


def cmd_report(args, use_rich: bool = False) -> int:
    """Handle report command."""
    import os
    from pathlib import Path
    from datetime import datetime
    
    output_dir = args.output or "./reports"
    os.makedirs(output_dir, exist_ok=True)
    
    if use_rich:
        console.print(f"[bold]Generating reports for:[/bold] {args.file}")
        console.print(f"[bold]Output directory:[/bold] {output_dir}")
    else:
        logger.info(f"Generating reports for: {args.file}")
    
    try:
        # Analyze the file
        from btrtools.cli.analyze import analyze_file
        from btrtools.cli.schema import detect_schema
        
        file_info = analyze_file(args.file)
        schema_info = detect_schema(args.file, record_size=args.record_size, max_records=args.max_records or 1000)
        
        # Extract records for detailed analysis
        analyzer = BtrieveAnalyzer(args.file)
        if args.record_size is None:
            record_size, _ = analyzer.detect_record_size()
            if record_size == 0:
                raise ValueError("Could not detect record size")
        else:
            record_size = args.record_size
        
        records = analyzer.extract_records(record_size, args.max_records or 1000)
        
        # Generate statistics
        stats = {
            'file_info': {
                'filename': file_info.filename,
                'file_size': file_info.file_size,
                'page_size': file_info.page_size,
                'ascii_percentage': file_info.ascii_percentage,
                'digit_sequences': file_info.digit_sequences,
                'date_patterns': file_info.date_patterns,
                'quality_score': file_info.quality_score
            },
            'record_analysis': {
                'total_records': len(records),
                'record_size': record_size,
                'avg_printable_chars': sum(r.printable_chars for r in records) / len(records) if records else 0,
                'records_with_digits': sum(1 for r in records if r.has_digits),
                'records_with_alpha': sum(1 for r in records if r.has_alpha),
                'extracted_fields': len(schema_info.get('fields', []))
            },
            'field_analysis': {},
            'generated_at': datetime.now().isoformat()
        }
        
        # Analyze fields
        if records and records[0].extracted_fields:
            field_stats = {}
            for field_name in records[0].extracted_fields.keys():
                values = [r.extracted_fields.get(field_name, '') for r in records if r.extracted_fields]
                non_empty = [v for v in values if v.strip()]
                field_stats[field_name] = {
                    'total_values': len(values),
                    'non_empty_values': len(non_empty),
                    'unique_values': len(set(non_empty)),
                    'avg_length': sum(len(str(v)) for v in non_empty) / len(non_empty) if non_empty else 0
                }
            stats['field_analysis'] = field_stats
        
        # Generate reports based on format
        base_name = Path(args.file).stem
        
        if args.format == 'json':
            import json
            report_file = os.path.join(output_dir, f"{base_name}_report.json")
            with open(report_file, 'w') as f:
                json.dump(stats, f, indent=2)
                
        elif args.format == 'html':
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>BTR-TOOLS Report - {base_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .stat {{ display: inline-block; margin: 10px; padding: 10px; background: #e8f4f8; border-radius: 3px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>BTR-TOOLS Analysis Report</h1>
        <p><strong>File:</strong> {args.file}</p>
        <p><strong>Generated:</strong> {stats['generated_at']}</p>
    </div>
    
    <div class="section">
        <h2>File Information</h2>
        <div class="stat">Size: {stats['file_info']['file_size']:,} bytes</div>
        <div class="stat">ASCII Content: {stats['file_info']['ascii_percentage']:.1f}%</div>
        <div class="stat">Quality Score: {stats['file_info']['quality_score']:.2f}</div>
    </div>
    
    <div class="section">
        <h2>Record Analysis</h2>
        <div class="stat">Total Records: {stats['record_analysis']['total_records']}</div>
        <div class="stat">Record Size: {stats['record_analysis']['record_size']} bytes</div>
        <div class="stat">Avg Printable: {stats['record_analysis']['avg_printable_chars']:.1f} chars</div>
        <div class="stat">With Digits: {stats['record_analysis']['records_with_digits']}</div>
        <div class="stat">With Alpha: {stats['record_analysis']['records_with_alpha']}</div>
    </div>
    
    <div class="section">
        <h2>Field Analysis</h2>
        <table>
            <tr><th>Field Name</th><th>Total Values</th><th>Non-Empty</th><th>Unique</th><th>Avg Length</th></tr>
"""
            for field_name, field_data in stats['field_analysis'].items():
                html_content += f"""
            <tr>
                <td>{field_name}</td>
                <td>{field_data['total_values']}</td>
                <td>{field_data['non_empty_values']}</td>
                <td>{field_data['unique_values']}</td>
                <td>{field_data['avg_length']:.1f}</td>
            </tr>"""
            html_content += """
        </table>
    </div>
</body>
</html>"""
            
            report_file = os.path.join(output_dir, f"{base_name}_report.html")
            with open(report_file, 'w') as f:
                f.write(html_content)
                
        else:  # text format
            report_file = os.path.join(output_dir, f"{base_name}_report.txt")
            with open(report_file, 'w') as f:
                f.write(f"BTR-TOOLS Analysis Report\n")
                f.write(f"File: {args.file}\n")
                f.write(f"Generated: {stats['generated_at']}\n\n")
                
                f.write("FILE INFORMATION:\n")
                f.write(f"  Size: {stats['file_info']['file_size']:,} bytes\n")
                f.write(f"  ASCII Content: {stats['file_info']['ascii_percentage']:.1f}%\n")
                f.write(f"  Quality Score: {stats['file_info']['quality_score']:.2f}\n\n")
                
                f.write("RECORD ANALYSIS:\n")
                f.write(f"  Total Records: {stats['record_analysis']['total_records']}\n")
                f.write(f"  Record Size: {stats['record_analysis']['record_size']} bytes\n")
                f.write(f"  Avg Printable: {stats['record_analysis']['avg_printable_chars']:.1f} chars\n")
                f.write(f"  Records with Digits: {stats['record_analysis']['records_with_digits']}\n")
                f.write(f"  Records with Alpha: {stats['record_analysis']['records_with_alpha']}\n\n")
                
                if stats['field_analysis']:
                    f.write("FIELD ANALYSIS:\n")
                    for field_name, field_data in stats['field_analysis'].items():
                        f.write(f"  {field_name}:\n")
                        f.write(f"    Total Values: {field_data['total_values']}\n")
                        f.write(f"    Non-Empty: {field_data['non_empty_values']}\n")
                        f.write(f"    Unique: {field_data['unique_values']}\n")
                        f.write(f"    Avg Length: {field_data['avg_length']:.1f}\n")
        
        if use_rich:
            print_success(f"Report generated: {report_file}", use_rich)
        else:
            logger.info(f"Report generated: {report_file}")
        
        return 0
        
    except Exception as e:
        if use_rich:
            print_error(f"Report generation failed: {e}", use_rich)
        else:
            logger.error(f"Report generation failed: {e}")
        return 1


def cmd_search(args, use_rich: bool = False) -> int:
    """Handle search command."""
    import re
    import csv
    import json
    
    if not args.query:
        if use_rich:
            print_error("Search query is required. Use --query or -q option.", use_rich)
        else:
            logger.error("Search query is required")
        return 1
    
    if use_rich:
        console.print(f"[bold]Searching Btrieve file:[/bold] {args.file}")
        console.print(f"[bold]Query:[/bold] {args.query}")
    else:
        logger.info(f"Searching Btrieve file: {args.file} for query: {args.query}")
    
    try:
        analyzer = BtrieveAnalyzer(args.file)
        
        # Auto-detect record size if not provided
        if args.record_size is None:
            record_size, _ = analyzer.detect_record_size()
            if record_size == 0:
                raise ValueError("Could not detect record size")
        else:
            record_size = args.record_size
        
        # Extract records
        records = analyzer.extract_records(record_size, args.max_records)
        
        if not records:
            if use_rich:
                print_warning("No records found to search", use_rich)
            else:
                logger.warning("No records found to search")
            return 1
        
        # Prepare search function
        if args.regex:
            flags = 0 if args.case_sensitive else re.IGNORECASE
            search_pattern = re.compile(args.query, flags)
            def matches_query(record):
                return bool(search_pattern.search(record.decoded_text))
        else:
            query = args.query if args.case_sensitive else args.query.lower()
            def matches_query(record):
                text = record.decoded_text if args.case_sensitive else record.decoded_text.lower()
                return query in text
        
        # Apply inversion if requested
        if args.invert_match:
            original_matches = matches_query
            matches_query = lambda r: not original_matches(r)
        
        # Filter records
        matching_records = [r for r in records if matches_query(r)]
        
        if use_rich:
            console.print(f"[bold]Results:[/bold] {len(matching_records)}/{len(records)} records matched")
        else:
            logger.info(f"Found {len(matching_records)}/{len(records)} matching records")
        
        # Output results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                if args.format == 'json':
                    json.dump([{
                        'record_num': r.record_num,
                        'record_size': r.record_size,
                        'decoded_text': r.decoded_text,
                        'printable_chars': r.printable_chars,
                        'has_digits': r.has_digits,
                        'has_alpha': r.has_alpha,
                        'extracted_fields': r.extracted_fields
                    } for r in matching_records], f, indent=2)
                elif args.format == 'csv':
                    if matching_records:
                        writer = csv.writer(f)
                        # Write header
                        fieldnames = ['record_num', 'record_size', 'decoded_text', 'printable_chars', 'has_digits', 'has_alpha']
                        if matching_records[0].extracted_fields:
                            fieldnames.extend(sorted(matching_records[0].extracted_fields.keys()))
                        writer.writerow(fieldnames)
                        # Write data
                        for r in matching_records:
                            row = [r.record_num, r.record_size, r.decoded_text, r.printable_chars, r.has_digits, r.has_alpha]
                            if r.extracted_fields:
                                row.extend(r.extracted_fields.get(field, '') for field in sorted(matching_records[0].extracted_fields.keys()))
                            writer.writerow(row)
                else:  # text format
                    f.write(f"Search results for query: {args.query}\n")
                    f.write(f"Total records searched: {len(records)}\n")
                    f.write(f"Matching records: {len(matching_records)}\n\n")
                    for r in matching_records:
                        f.write(f"Record {r.record_num}:\n")
                        f.write(f"  Text: {r.decoded_text}\n")
                        if r.extracted_fields:
                            f.write(f"  Fields: {r.extracted_fields}\n")
                        f.write("\n")
        else:
            # Console output
            if use_rich and matching_records:
                table = Table(title=f"Search Results ({len(matching_records)} matches)")
                table.add_column("Record #", style="cyan", no_wrap=True)
                table.add_column("Text", style="magenta")
                table.add_column("Fields", style="green")
                
                for r in matching_records[:20]:  # Limit display to first 20
                    fields_str = ", ".join(f"{k}={v}" for k, v in r.extracted_fields.items()) if r.extracted_fields else ""
                    table.add_row(str(r.record_num), r.decoded_text[:50] + "..." if len(r.decoded_text) > 50 else r.decoded_text, fields_str)
                
                if len(matching_records) > 20:
                    table.add_row("...", f"... and {len(matching_records) - 20} more matches", "")
                
                console.print(table)
            elif matching_records:
                print(f"Found {len(matching_records)} matching records:")
                for r in matching_records[:10]:  # Limit to first 10
                    print(f"Record {r.record_num}: {r.decoded_text[:100]}...")
                if len(matching_records) > 10:
                    print(f"... and {len(matching_records) - 10} more matches")
            else:
                if use_rich:
                    print_warning("No records matched the search query", use_rich)
                else:
                    print("No records matched the search query")
        
        return 0
        
    except Exception as e:
        if use_rich:
            print_error(f"Search failed: {e}", use_rich)
        else:
            logger.error(f"Search failed: {e}")
        return 1


def cmd_repair(args, use_rich: bool = False) -> int:
    """Handle repair command."""
    from pathlib import Path
    
    if use_rich:
        console.print(f"[bold]Repairing Btrieve file:[/bold] {args.file}")
    else:
        logger.info(f"Repairing Btrieve file: {args.file}")
    
    # Create backup if requested
    if args.backup:
        backup_file = f"{args.file}.backup"
        try:
            import shutil
            shutil.copy2(args.file, backup_file)
            if use_rich:
                print_success(f"Backup created: {backup_file}", use_rich)
            else:
                logger.info(f"Backup created: {backup_file}")
        except Exception as e:
            if use_rich:
                print_error(f"Failed to create backup: {e}", use_rich)
            else:
                logger.error(f"Failed to create backup: {e}")
            return 1
    
    # Determine output file
    if args.output:
        output_file = args.output
    else:
        stem = Path(args.file).stem
        output_file = f"{stem}_repaired.btr"
    
    # Perform integrity check first
    from btrtools.cli.check import check_integrity
    integrity_result = check_integrity(args.file)
    
    if use_rich:
        display_integrity_results_rich(integrity_result)
    else:
        if integrity_result.get('corruption_detected', False):
            print("INTEGRITY ISSUES DETECTED:")
            for detail in integrity_result.get('corruption_details', []):
                print(f"  - {detail}")
        else:
            print("File integrity check passed.")
    
    if args.validate_only:
        return 0 if not integrity_result.get('corruption_detected', False) else 1
    
    # If no corruption detected, just copy the file
    if not integrity_result.get('corruption_detected', False):
        if use_rich:
            print_info("No corruption detected, copying file as-is", use_rich)
        try:
            import shutil
            shutil.copy2(args.file, output_file)
            if use_rich:
                print_success(f"File copied to: {output_file}", use_rich)
            else:
                logger.info(f"File copied to: {output_file}")
            return 0
        except Exception as e:
            if use_rich:
                print_error(f"Failed to copy file: {e}", use_rich)
            else:
                logger.error(f"Failed to copy file: {e}")
            return 1
    
    # Attempt repairs if corruption detected and fix_corruption is enabled
    if not args.fix_corruption:
        if use_rich:
            print_warning("Corruption detected but --fix-corruption not specified. Use --fix-corruption to attempt repairs.", use_rich)
        else:
            logger.warning("Corruption detected but --fix-corruption not specified")
        return 1
    
    if use_rich:
        console.print("[yellow]Attempting to repair corrupted file...[/yellow]")
    else:
        logger.info("Attempting to repair corrupted file")
    
    try:
        # Basic repair: try to extract valid records and rebuild the file
        analyzer = BtrieveAnalyzer(args.file)
        
        # Auto-detect record size if not provided
        if args.record_size is None:
            record_size, _ = analyzer.detect_record_size()
            if record_size == 0:
                raise ValueError("Could not detect record size")
        else:
            record_size = args.record_size
        
        # Extract records
        records = analyzer.extract_records(record_size)
        
        if not records:
            raise ValueError("No valid records could be extracted from corrupted file")
        
        # Rebuild the file with valid records
        fcr_data = b'\x00' * (analyzer.FCR_PAGES * analyzer.PAGE_SIZE)
        record_data = b''.join(record.raw_bytes for record in records)
        
        with open(output_file, 'wb') as f:
            f.write(fcr_data)
            f.write(record_data)
        
        if use_rich:
            print_success(f"Repaired file created: {output_file}", use_rich)
            print_info(f"Extracted {len(records)} valid records", use_rich)
        else:
            logger.info(f"Repaired file created: {output_file}")
            logger.info(f"Extracted {len(records)} valid records")
        
        return 0
        
    except Exception as e:
        if use_rich:
            print_error(f"Repair failed: {e}", use_rich)
        else:
            logger.error(f"Repair failed: {e}")
        return 1


def cmd_batch(args, use_rich: bool = False) -> int:
    """Handle batch command."""
    import glob
    import concurrent.futures
    from pathlib import Path
    
    # Expand glob patterns
    all_files = []
    for pattern in args.files:
        expanded = glob.glob(pattern)
        if not expanded:
            # If glob didn't match, treat as literal filename
            expanded = [pattern]
        all_files.extend(expanded)
    
    # Remove duplicates and filter for existing files
    all_files = list(set(all_files))
    valid_files = [f for f in all_files if os.path.isfile(f)]
    
    if not valid_files:
        if use_rich:
            print_error("No valid files found to process", use_rich)
        else:
            logger.error("No valid files found to process")
        return 1
    
    if use_rich:
        console.print(f"[bold]Batch processing {len(valid_files)} files[/bold]")
        console.print(f"Operation: {args.operation}")
        if args.format:
            console.print(f"Format: {args.format}")
    else:
        logger.info(f"Batch processing {len(valid_files)} files with operation: {args.operation}")
    
    # Create output directory if specified
    output_dir = args.output_dir or "."
    os.makedirs(output_dir, exist_ok=True)
    
    # Function to process a single file
    def process_file(filepath: str) -> dict:
        try:
            result = {"file": filepath, "success": False, "error": None, "output": None}
            
            if args.operation == 'analyze':
                from btrtools.cli.analyze import analyze_file
                file_info = analyze_file(filepath)
                result["success"] = True
                result["output"] = file_info
                
            elif args.operation == 'export':
                if not args.format:
                    result["error"] = "Format required for export operation"
                    return result
                from btrtools.cli.export import export_file
                output_file = os.path.join(output_dir, 
                    f"{Path(filepath).stem}.{args.format if args.format != 'sqlite' else 'db'}")
                exported_file = export_file(filepath, args.format, 
                                          record_size=args.record_size,
                                          max_records=args.max_records,
                                          output_file=output_file)
                result["success"] = True
                result["output"] = exported_file
                
            elif args.operation == 'schema':
                from btrtools.cli.schema import detect_schema
                schema = detect_schema(filepath, record_size=args.record_size, max_records=args.max_records)
                result["success"] = True
                result["output"] = schema
                
            elif args.operation == 'check':
                from btrtools.cli.check import check_integrity
                check_result = check_integrity(filepath)
                result["success"] = True
                result["output"] = check_result
                
            return result
            
        except Exception as e:
            return {"file": filepath, "success": False, "error": str(e), "output": None}
    
    # Process files
    results = []
    if args.parallel > 1:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel) as executor:
            futures = [executor.submit(process_file, f) for f in valid_files]
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
    else:
        for filepath in valid_files:
            results.append(process_file(filepath))
    
    # Display results
    success_count = sum(1 for r in results if r["success"])
    
    if use_rich:
        table = Table(title="Batch Processing Results")
        table.add_column("File", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Output/Error", style="yellow")
        
        for result in results:
            status = "✅ Success" if result["success"] else "❌ Failed"
            output = result["output"] or result["error"] or ""
            table.add_row(os.path.basename(result["file"]), status, str(output))
        
        console.print(table)
        console.print(f"\n[bold]Summary:[/bold] {success_count}/{len(results)} files processed successfully")
    else:
        print(f"\nBatch processing completed: {success_count}/{len(results)} files successful")
        for result in results:
            status = "SUCCESS" if result["success"] else "FAILED"
            print(f"{status}: {result['file']}")
            if result["error"]:
                print(f"  Error: {result['error']}")
    
    return 0 if success_count == len(results) else 1


if __name__ == '__main__':
    sys.exit(main())
