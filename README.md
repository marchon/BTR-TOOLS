# BTR-TOOLS

Generic command-line toolkit for Btrieve database file analysis and export.

## Overview

BTR-TOOLS is a comprehensive toolkit for analyzing, repairing, and exporting data from Btrieve database files. This toolkit provides generic tools that can work with any Btrieve v5 format database files, automatically detecting record structures, extracting data, and exporting to multiple formats.

## Features

- **Directory Scanning**: Automatically detect Btrieve files in directories
- **File Analysis**: Comprehensive analysis of file structure and content patterns
- **Data Export**: Export data to CSV, JSON Lines, and SQLite formats
- **Schema Detection**: Automatically detect field boundaries and data types
- **Integrity Checking**: Verify file integrity and detect corruption
- **Record Size Detection**: Automatically determine optimal record sizes
- **Rich CLI Output**: Enhanced terminal interface with progress bars and colored output
- **Comprehensive Testing**: Full test suite with unit, integration, and performance tests
- **CI/CD Pipeline**: Automated testing, linting, and quality assurance

## Installation

### From Source

```bash
git clone <repository-url>
cd btrtools
pip install -e .
```

### Development Installation

For development with all testing and quality tools:

```bash
git clone <repository-url>
cd btrtools
pip install -e ".[dev]"
```

### Direct Usage

You can also run the tools directly without installation:

```bash
python scripts/btrtools --help
```

## Commands

All commands support rich output with progress bars using the `--progress` or `-P` flag.

### Scan Directory

Scan a directory for Btrieve files:

```bash
# Basic scan
btrtools scan /path/to/directory --recursive

# With rich output and progress bars
btrtools --progress scan /path/to/directory --recursive
```

### Analyze File

Analyze a specific Btrieve file:

```bash
# Basic analysis
btrtools analyze file.btr --max-records 1000

# With rich output
btrtools --progress analyze file.btr --max-records 1000
```

### Export Data

Export Btrieve data to various formats:

```bash
# Export to CSV
btrtools export file.btr --format csv

# Export to JSON Lines with progress
btrtools --progress export file.btr --format jsonl

# Export to SQLite database
btrtools export file.btr --format sqlite

# Specify record size and limit records
btrtools export file.btr --format csv --record-size 128 --max-records 1000
```

### Detect Schema

Automatically detect the schema/structure of a Btrieve file:

```bash
btrtools schema file.btr --max-records 1000

# With rich table output
btrtools --progress schema file.btr --max-records 1000
```

### Check Integrity

Verify file integrity and check for corruption:

```bash
btrtools check file.btr --verbose

# With progress indicators
btrtools --progress check file.btr --verbose
```

## Rich CLI Output

BTR-TOOLS supports enhanced terminal output with progress bars, colored text, and structured tables. Enable rich output with the `--progress` or `-P` flag:

```bash
# Enable rich output for any command
btrtools --progress analyze file.btr
btrtools -P scan /data --recursive
```

### Rich Output Features

- **Progress Bars**: Visual progress indicators for long-running operations
- **Colored Output**: Success (green), warnings (yellow), errors (red)
- **Structured Tables**: Formatted data display for analysis results
- **Icons**: Visual indicators for different types of messages
- **Spinners**: Activity indicators during processing

### Example Rich Output

```
BTR-TOOLS - Btrieve File Analysis Toolkit
Version 2.0.0 | Rich output enabled
⠋ Reading file structure... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00

    Btrieve File Analysis Results    
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Property        ┃ Value           ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ Filename        │ example.btr     │
│ File Size       │ 4,096 bytes     │
│ ASCII Content   │ 85.2%           │
│ Quality Score   │ 7.8             │
└─────────────────┴─────────────────┘

✅ Operation completed successfully
```

## Analysis Techniques

The toolkit uses several analysis techniques to understand Btrieve file content:

### Content Pattern Analysis
- ASCII content percentage
- Digit sequence detection
- Date pattern recognition
- Content type classification

### Record Size Detection
- Tests common record sizes (32, 64, 128, 256, 512, 1024 bytes)
- Quality scoring based on text content, digit patterns, and printable characters
- Automatic selection of optimal record size

### Field Extraction
- Regex-based pattern matching for common data patterns:
  - Alphanumeric codes (uppercase letter sequences)
  - Addresses and location patterns
  - Numeric identifiers and sequences
  - Date and time formats
  - Monetary amounts and quantities

### Schema Detection
- Position-by-position analysis across multiple records
- Field boundary detection based on content patterns
- Automatic field type inference
- Quality metrics for each detected field

## Output Formats

### CSV Export
Standard CSV format with headers. Includes both raw data and extracted fields:

```csv
record_num,record_size,decoded_text,printable_chars,has_digits,has_alpha,code_field,text_field,numeric_field
1,64,"ABC COMPANY     123 MAIN ST   ANYTOWN  ST 12345",45,true,true,ABC,"MAIN ST",12345
2,64,"XYZ CORP        800-555-0123         CODE123 125.00",42,true,true,XYZ,,8005550123,CODE123,125.00
```

### JSON Lines Export
One JSON object per line, suitable for streaming processing:

```json
{"record_num": 1, "record_size": 64, "raw_bytes": "4142432...", "decoded_text": "ABC COMPANY...", "printable_chars": 45, "has_digits": true, "has_alpha": true, "extracted_fields": {"code_field": "ABC", "text_field": "MAIN ST", "numeric_field": "12345"}}
```

### SQLite Export
Creates a SQLite database with a `btrieve_records` table containing all data and extracted fields.

## Examples

### Basic File Analysis Workflow

```bash
# Scan a directory for Btrieve files
btrtools scan /data/archive --recursive --output scan_results.txt

# Analyze a discovered file
btrtools analyze inventory.btr

# Check file integrity
btrtools check inventory.btr --verbose

# Detect the data schema
btrtools schema inventory.btr --output schema.txt

# Export data to CSV format
btrtools export inventory.btr --format csv --output inventory.csv
```

### Advanced Usage

```bash
# Analyze with more records for better schema detection
btrtools analyze large_file.btr --max-records 5000

# Export specific number of records
btrtools export data.btr --format jsonl --max-records 1000 --output data.jsonl

# Force specific record size for problematic files
btrtools export data.btr --format sqlite --record-size 256 --output data.db

# Batch process multiple files
for file in *.btr; do
    btrtools export "$file" --format csv
done
```

### Data Migration Scenario

```bash
# Step 1: Verify file integrity
btrtools check legacy_data.btr

# Step 2: Analyze file structure
btrtools analyze legacy_data.btr --max-records 1000

# Step 3: Detect schema automatically
btrtools schema legacy_data.btr

# Step 4: Export to modern format
btrtools export legacy_data.btr --format sqlite --output modern_data.db
```

## Quality Scoring

The toolkit uses a quality scoring system to evaluate extraction success:

- **Text Content** (30 points): Percentage of records with readable text
- **Digit Patterns** (20 points): Records containing digit sequences
- **Alpha Patterns** (20 points): Records containing alphabetic characters
- **Printable Density** (30 points): Average printable characters per record

Scores range from 0-100, with higher scores indicating better data quality and more reliable extractions.

## Troubleshooting

### Common Issues

1. **"Could not detect record size"**
   - Try specifying the record size manually: `--record-size 128`
   - Check file integrity: `btrtools check file.btr`

2. **"No records found to export"**
   - Verify the file is a valid Btrieve file
   - Try different record sizes
   - Check if the file has data pages beyond the FCR

3. **Low quality scores**
   - File may be corrupted or not a Btrieve file
   - Try smaller record sizes for better granularity
   - Check ASCII content percentage

4. **Memory issues with large files**
   - Use `--max-records` to limit processing
   - Export in smaller batches

### File Size Requirements

- Minimum file size: 8KB (2 FCR pages + 1 data page)
- Files should be multiples of 4KB (page size) for best results
- Very large files (>100MB) may require batch processing

## Use Cases

BTR-TOOLS is useful for:

- **Legacy System Migration**: Extract data from old Btrieve databases
- **Data Recovery**: Recover data from corrupted or damaged files
- **Database Archaeology**: Analyze unknown legacy file formats
- **Data Conversion**: Transform Btrieve data to modern formats
- **Forensic Analysis**: Examine file contents for auditing purposes
- **Research**: Study historical data storage formats

## Development

### Testing

BTR-TOOLS includes a comprehensive test suite covering unit tests, integration tests, and performance benchmarks:

```bash
# Run all tests
pytest btrtools/tests/

# Run with coverage report
pytest btrtools/tests/ --cov=btrtools --cov-report=html

# Run specific test categories
pytest btrtools/tests/test_basic.py     # Unit tests
pytest btrtools/tests/test_cli.py       # CLI integration tests
pytest btrtools/tests/test_performance.py  # Performance tests
```

### Code Quality

The project uses multiple tools for code quality assurance:

```bash
# Format code
black btrtools/
isort btrtools/

# Lint code
flake8 btrtools/
mypy btrtools/

# Security scanning
bandit -r btrtools/
safety check
```

### CI/CD Pipeline

BTR-TOOLS uses GitHub Actions for automated testing and quality assurance:

- **Multi-platform testing**: Windows, macOS, Linux
- **Python version matrix**: 3.8, 3.9, 3.10, 3.11
- **Automated linting**: black, isort, flake8, mypy
- **Security scanning**: bandit, safety
- **Documentation building**: Sphinx
- **Test coverage reporting**: pytest-cov

### Project Structure

```
btrtools/
├── __init__.py          # Package initialization
├── core/
│   ├── __init__.py
│   └── btrieve.py       # Core Btrieve file handling
├── cli/
│   ├── __init__.py      # Main CLI entry point
│   ├── scan.py          # Directory scanning
│   ├── analyze.py       # File analysis
│   ├── export.py        # Data export
│   ├── schema.py        # Schema detection
│   └── check.py         # Integrity checking
├── utils/
│   ├── __init__.py
│   └── logging.py       # Logging and error handling
└── tests/
    ├── __init__.py
    ├── test_basic.py    # Unit tests
    ├── test_cli.py      # CLI integration tests
    └── test_performance.py  # Performance benchmarks
```

### Adding New Commands

1. Create a new module in `btrtools/cli/`
2. Implement the command function
3. Add the command to the main CLI parser in `__init__.py`
4. Update this README

### Extending Field Extraction

The field extraction patterns in `btrieve.py` can be extended by adding new regex patterns to the `_extract_basic_fields` method for domain-specific data patterns.

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.

## Related Projects

- Btrieve file format documentation
- Database migration tools
- Legacy system analysis utilities