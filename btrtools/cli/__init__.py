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

from btrtools.core.btrieve import BtrieveAnalyzer, BtrieveFileInfo
from btrtools.utils.logging import logger, error_handler, safe_execute, create_error_context, BTRError


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog='btrtools',
        description='Btrieve File Analysis Toolkit - Generic command-line tools for Btrieve database files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  btrtools scan /path/to/files/          # Scan directory for Btrieve files
  btrtools analyze file.btr              # Analyze a specific Btrieve file
  btrtools export file.btr --format csv  # Export data to CSV format
  btrtools schema file.btr               # Detect and display schema
  btrtools check file.btr                # Check file integrity

Debug Options:
  Set BTRTOOLS_LOG_LEVEL=DEBUG for detailed logging
  Set BTRTOOLS_LOG_LEVEL=INFO for normal operation (default)
        """
    )

    parser.add_argument(
        '--version',
        action='version',
        version='BTR-TOOLS v1.0.0'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands'
    )
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog='btrtools',
        description='Btrieve File Analysis Toolkit - Generic command-line tools for Btrieve database files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  btrtools scan /path/to/files/          # Scan directory for Btrieve files
  btrtools analyze file.btr              # Analyze a specific Btrieve file
  btrtools export file.btr --format csv  # Export data to CSV format
  btrtools schema file.btr               # Detect and display schema
  btrtools check file.btr                # Check file integrity
        """
    )

    parser.add_argument(
        '--version',
        action='version',
        version='BTR-TOOLS v1.0.0'
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

    logger.info("BTR-TOOLS starting")

    if not hasattr(args, 'command') or not args.command:
        parser.print_help()
        return 1

    # Create error context
    context = create_error_context(args.command, vars(args))

    # Execute command with error handling
    if args.command == 'scan':
        result, exit_code = safe_execute(cmd_scan, context, args)
    elif args.command == 'analyze':
        result, exit_code = safe_execute(cmd_analyze, context, args)
    elif args.command == 'export':
        result, exit_code = safe_execute(cmd_export, context, args)
    elif args.command == 'schema':
        result, exit_code = safe_execute(cmd_schema, context, args)
    elif args.command == 'check':
        result, exit_code = safe_execute(cmd_check, context, args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        logger.error(f"Unknown command: {args.command}")
        return 1

    logger.info(f"BTR-TOOLS finished with exit code: {exit_code}")
    return exit_code


def cmd_scan(args) -> int:
    """Handle scan command."""
    from btrtools.cli.scan import scan_directory

    logger.info(f"Scanning directory: {args.directory} (recursive: {args.recursive})")

    results = scan_directory(args.directory, args.recursive)

    logger.info(f"Scan complete: found {len(results)} potential Btrieve files")

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
            logger.info(f"Scan results written to: {args.output}")
        except Exception as e:
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


def cmd_analyze(args) -> int:
    """Handle analyze command."""
    from btrtools.cli.analyze import analyze_file

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
            logger.info(f"Analysis results written to: {args.output}")
        except Exception as e:
            logger.error(f"Failed to write analysis results to {args.output}: {e}")
            raise BTRError(f"Failed to write output file: {e}")
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


def cmd_export(args) -> int:
    """Handle export command."""
    from btrtools.cli.export import export_file

    logger.info(f"Exporting file: {args.file} (format: {args.format}, record_size: {args.record_size})")

    output_file = export_file(
        args.file,
        args.format,
        args.record_size,
        args.max_records,
        args.output
    )

    logger.info(f"Export complete: {output_file}")
    print(f"Successfully exported to: {output_file}")
    return 0


def cmd_schema(args) -> int:
    """Handle schema command."""
    from btrtools.cli.schema import detect_schema

    logger.info(f"Detecting schema for: {args.file} (record_size: {args.record_size}, max_records: {args.max_records})")

    schema_info = detect_schema(
        args.file,
        args.record_size,
        args.max_records
    )

    logger.info(f"Schema detection complete for {args.file}")

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
            logger.info(f"Schema results written to: {args.output}")
        except Exception as e:
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


def cmd_check(args) -> int:
    """Handle check command."""
    from btrtools.cli.check import check_integrity

    logger.info(f"Checking integrity of: {args.file} (verbose: {args.verbose})")

    result = check_integrity(args.file, args.verbose)

    logger.info(f"Integrity check complete for {args.file}")

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
