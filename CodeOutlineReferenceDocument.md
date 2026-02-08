# BTR-TOOLS Code Outline Reference Document

## Project Overview

**BTR-TOOLS v2.3.0** is a comprehensive command-line toolkit for analyzing, repairing, and exporting data from legacy Btrieve database files. This document provides a complete reference for the codebase organization, function indices, and development guidelines.

**Key Features:**
- Directory scanning for Btrieve files
- File structure analysis and integrity checking
- Data extraction and export (CSV, JSONL, SQLite, Excel, XML)
- Schema detection and field analysis
- File comparison and repair capabilities
- Rich CLI interface with progress indicators

**Architecture:** Modular design with clear separation between CLI commands, core functionality, and utilities.

---

## Module Structure

```
btrtools/
├── __init__.py              # Package initialization and version info
├── cli/                     # Command-line interface modules
│   ├── __init__.py         # Main CLI entry point and command dispatcher
│   ├── analyze.py          # File analysis functionality
│   ├── scan.py             # Directory scanning functionality
│   ├── schema.py           # Schema detection and field analysis
│   ├── export.py           # Data export functionality
│   ├── compare.py          # File comparison functionality
│   └── [other command modules]
├── core/                    # Core business logic
│   ├── __init__.py         # Core module initialization
│   └── btrieve.py          # Main Btrieve file handling and analysis
└── utils/                   # Utility modules
    ├── __init__.py         # Utils module initialization
    └── logging.py          # Logging and error handling utilities
```

---

## Core Module: btrtools.core.btrieve

### Overview
The core Btrieve analyzer providing file analysis, record extraction, and integrity checking functionality.

### Data Classes
- **BtrieveFileInfo**: Information about a Btrieve file (filename, size, structure, content analysis)
- **BtrieveRecord**: A single Btrieve record with extracted data and analysis

### Public API Functions
- **BtrieveAnalyzer.__init__(filepath)**: Initialize analyzer for a Btrieve file
- **BtrieveAnalyzer.analyze_file()**: Analyze basic file structure and content patterns
- **BtrieveAnalyzer.detect_record_size(max_records)**: Detect optimal record size using quality scoring
- **BtrieveAnalyzer.extract_records(record_size, max_records)**: Extract records from the Btrieve file
- **BtrieveAnalyzer.check_integrity()**: Check file integrity and detect potential corruption

### Private Implementation Functions
- **BtrieveAnalyzer._classify_content_type(text, info)**: Classify content type based on patterns
- **BtrieveAnalyzer._create_record(record_num, record_size, record_bytes)**: Create BtrieveRecord from raw bytes
- **BtrieveAnalyzer._extract_basic_fields(text)**: Extract basic fields using regex patterns
- **BtrieveAnalyzer._calculate_quality_score(records)**: Calculate quality score for record set

### Constants
- **COMMON_RECORD_SIZES**: [32, 64, 128, 256, 512, 1024] - Standard record sizes to test
- **PAGE_SIZE**: 4096 - Btrieve page size
- **HEADER_SIZE**: 16 - Header size per page
- **FCR_PAGES**: 2 - File Control Record pages

---

## CLI Module: btrtools.cli.__init__

### Overview
Main command-line interface providing argument parsing, command dispatch, and user interaction.

### Public API Functions
- **main()**: Main CLI entry point - parses arguments and dispatches commands
- **create_parser()**: Create and configure the argument parser

### Display/Printing Functions
- **print_success(message, use_rich)**: Print success message with optional rich formatting
- **print_error(message, use_rich)**: Print error message with optional rich formatting
- **print_warning(message, use_rich)**: Print warning message with optional rich formatting
- **print_info(message, use_rich)**: Print info message with optional rich formatting
- **create_progress_bar(description)**: Create progress bar for long-running operations
- **display_file_info_rich(info)**: Display file information using rich formatting
- **display_integrity_results_rich(result)**: Display integrity check results using rich formatting

### Command Handler Functions
- **cmd_scan(args, use_rich)**: Handle 'scan' command - scan directories for Btrieve files
- **cmd_analyze(args, use_rich)**: Handle 'analyze' command - analyze Btrieve file structure
- **cmd_export(args, use_rich)**: Handle 'export' command - export records to various formats
- **cmd_schema(args, use_rich)**: Handle 'schema' command - detect file schema and field structure
- **cmd_check(args, use_rich)**: Handle 'check' command - check file integrity
- **cmd_compare(args, use_rich)**: Handle 'compare' command - compare two Btrieve files
- **cmd_stats(args, use_rich)**: Handle 'stats' command - performance profiling and statistics
- **cmd_report(args, use_rich)**: Handle 'report' command - generate data visualization reports
- **cmd_search(args, use_rich)**: Handle 'search' command - search and filter records
- **cmd_repair(args, use_rich)**: Handle 'repair' command - validate and repair corrupted files
- **cmd_batch(args, use_rich)**: Handle 'batch' command - process multiple files simultaneously

---

## CLI Command Modules

### btrtools.cli.analyze
**Public Functions:**
- **analyze_file(filepath, max_records)**: Analyze a Btrieve file and return detailed information

### btrtools.cli.scan
**Public Functions:**
- **scan_directory(directory, recursive)**: Scan a directory for Btrieve files

**Private Functions:**
- **_is_potential_btrieve_file(filepath)**: Check if a file is potentially a Btrieve file

### btrtools.cli.schema
**Public Functions:**
- **detect_schema(filepath, record_size, max_records)**: Detect schema information from a Btrieve file

**Private Functions:**
- **_analyze_field_patterns(records)**: Analyze patterns in record fields
- **_detect_fields(records, record_size)**: Detect field boundaries and types
- **_create_field_info(field_data)**: Create field information dictionary
- **_infer_field_type_and_name(field_samples, position)**: Infer field type and name from samples

### btrtools.cli.export
**Public Functions:**
- **export_file(filepath, format_type, record_size, max_records, output_file)**: Export Btrieve file data to specified format

**Private Functions:**
- **_export_csv(records, output_file)**: Export records to CSV format
- **_export_jsonl(records, output_file)**: Export records to JSON Lines format
- **_export_sqlite(records, output_file)**: Export records to SQLite database
- **_export_excel(records, output_file)**: Export records to Excel spreadsheet
- **_export_xml(records, output_file)**: Export records to XML format

### btrtools.cli.compare
**Public Functions:**
- **compare_files(file1, file2, max_records)**: Compare two Btrieve files and return detailed comparison results

**Private Functions:**
- **_compare_records(records1, records2, max_records)**: Compare records between two files

---

## Utilities Module: btrtools.utils.logging

### Overview
Comprehensive logging, error handling, and bug report generation with data simulation for privacy protection.

### Data Classes
- **ErrorContext**: Context information for errors (command, args, file_path, etc.)
- **BugReport**: Structured bug report with simulated data

### Classes
- **BTRLogger**: Enhanced logging system for BTR-TOOLS
- **BTRErrorHandler**: Comprehensive error handling and bug report generation

### BTRLogger Methods
- **__init__(name, level)**: Initialize logger with name and level
- **set_level(level)**: Set logging level from string
- **debug/info/warning/error/critical(message)**: Standard logging methods
- **exception(message)**: Log exception with traceback

### BTRErrorHandler Methods
- **__init__(logger)**: Initialize error handler with logger instance
- **handle_error(error, context)**: Handle exceptions and generate bug reports

### Public Utility Functions
- **safe_execute(func, context, *args, **kwargs)**: Execute function with error handling
- **create_error_context(command, args, **kwargs)**: Create error context from command arguments

### Private Implementation Methods
- **BTRLogger._setup_file_logging()**: Configure file logging with rotation
- **BTRErrorHandler._create_bug_report(error, context)**: Create structured bug report
- **BTRErrorHandler._simulate_data(context)**: Generate simulated data for privacy
- **BTRErrorHandler._get_memory_info()**: Get system memory information
- **BTRErrorHandler._save_bug_report(report)**: Save bug report to file
- **BTRErrorHandler._show_user_error(error, context)**: Display user-friendly error
- **BTRErrorHandler._get_exit_code(error)**: Determine exit code from exception type

---

## Code Organization Principles

### Function Ordering
1. **Public API functions first** (external interfaces)
2. **Private implementation functions last** (internal helpers)
3. **Constructor/initialization methods** at the top
4. **Main business logic** in the middle
5. **Utility and helper functions** at the bottom

### Naming Conventions
- **Public functions**: descriptive names (e.g., `analyze_file`, `export_records`)
- **Private functions**: prefixed with underscore (e.g., `_create_record`, `_calculate_score`)
- **Variables**: descriptive names avoiding abbreviations where possible
- **Constants**: UPPER_CASE with descriptive names

### Documentation Standards
- **Function Index**: At the top of each module with categorization
- **Docstrings**: Comprehensive with Args, Returns, and descriptions
- **Type Hints**: Full type annotations for parameters and return values
- **Comments**: Clear explanations of complex logic

### Error Handling
- **Custom Exceptions**: BTRDataError, BTRFileError, BTRValidationError
- **Context Preservation**: ErrorContext for debugging information
- **Bug Reports**: Automated generation with data simulation
- **Graceful Degradation**: Fail-safe behavior with informative messages

---

## Development Guidelines

### Adding New Features
1. **Start with CLI command** in `btrtools/cli/__init__.py`
2. **Implement core logic** in appropriate module (`core/` or `cli/`)
3. **Add comprehensive tests** in `tests/`
4. **Update documentation** and function indices
5. **Follow naming conventions** and organization principles

### Code Quality Standards
- **PEP 8 Compliance**: 88-character line limits, proper formatting
- **Type Safety**: Full type annotations throughout
- **Test Coverage**: Unit and integration tests for all features
- **Documentation**: Complete docstrings and function indices
- **Linting**: Zero violations (flake8, mypy, etc.)

### Testing Strategy
- **Unit Tests**: Individual function testing
- **Integration Tests**: End-to-end command testing
- **Performance Tests**: Benchmarking and profiling
- **Error Testing**: Exception handling validation
- **Coverage**: 80%+ code coverage target

### Version Control
- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **Descriptive Commits**: Clear messages with context
- **Branch Strategy**: Feature branches for development
- **Release Process**: Automated testing and validation

---

## Recent Improvements (v2.3.0)

### Code Quality Enhancements
- ✅ **Resolved 100+ linting violations**
- ✅ **Added comprehensive type annotations**
- ✅ **Improved error handling and validation**
- ✅ **Enhanced code documentation and organization**

### Documentation Improvements
- ✅ **Function indices** in all major modules
- ✅ **Public/private function categorization**
- ✅ **Clear API boundaries** and interfaces
- ✅ **Professional code organization**

### Architecture Refinements
- ✅ **Modular design** with clear separation of concerns
- ✅ **Consistent naming conventions**
- ✅ **Logical function ordering**
- ✅ **Maintainable code structure**

---

## Quick Reference

### Running Commands
```bash
# Analyze a file
btrtools analyze myfile.btr

# Scan directory
btrtools scan /data --recursive

# Export to CSV
btrtools export myfile.btr --format csv

# Check integrity
btrtools check myfile.btr
```

### Development Setup
```bash
# Install for development
pip install -e ".[dev]"

# Run tests
python -m pytest

# Check linting
flake8 btrtools/

# Type checking
mypy btrtools/
```

### Key Files
- **Entry Point**: `btrtools/cli/__init__.py::main()`
- **Core Logic**: `btrtools/core/btrieve.py::BtrieveAnalyzer`
- **Configuration**: `pyproject.toml`
- **Tests**: `btrtools/tests/`

This document serves as the authoritative reference for understanding and maintaining the BTR-TOOLS codebase. All developers should familiarize themselves with this structure before making changes.