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
  btrtools check file.btr                # Check file integrity

Debug Options:
  Set BTRTOOLS_LOG_LEVEL=DEBUG for detailed logging
  Set BTRTOOLS_LOG_LEVEL=INFO for normal operation (default)
        """
    )

    parser.add_argument(
        '--version',
        action='version',
        version='BTR-TOOLS v2.0.0'
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
        choices=['csv', 'jsonl', 'sqlite'],
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

    # Check command
    check_parser = subparsers.add_parser(
        'check',
        help='Check Btrieve file integrity'
    )
    check_parser.add_argument(
        'file',
        help='Btrieve file to check'
    )
    check_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
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


def cmd_check(args, use_rich: bool = False) -> int:
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


if __name__ == '__main__':
    sys.exit(main())
