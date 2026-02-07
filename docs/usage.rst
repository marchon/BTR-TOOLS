Usage Guide
===========

This guide covers how to use BTR-TOOLS for analyzing and extracting data from Btrieve files.

Command Line Interface
----------------------

BTR-TOOLS provides a unified command-line interface with multiple subcommands:

* ``btrtools analyze``: Analyze Btrieve file structure and content
* ``btrtools export``: Export records to various formats
* ``btrtools check``: Check file integrity
* ``btrtools scan``: Scan directories for Btrieve files
* ``btrtools schema``: Detect file schema and field structure
* ``btrtools compare``: Compare two Btrieve files for differences

All commands support the ``--help`` flag for detailed usage information.

Rich Output Mode
----------------

All commands support enhanced terminal output with progress bars and colored text using the ``--progress`` or ``-P`` flag::

    btrtools --progress analyze myfile.btr
    btrtools -P scan /data --recursive

Rich output features:

* Progress bars for long-running operations
* Colored success/warning/error messages
* Structured tables for data display
* Visual indicators and spinners

Analyzing Files
---------------

Basic file analysis::

    btrtools analyze myfile.btr

This provides detailed information about the file structure, including:

* File format version and size
* Page structure and allocation
* Record count and size estimates
* Content patterns and quality scores
* ASCII content percentage

Analyze with more records for better accuracy::

    btrtools analyze myfile.btr --max-records 1000

With rich output and progress bars::

    btrtools --progress analyze myfile.btr --max-records 1000

Scanning Directories
--------------------

Scan a directory for Btrieve files::

    btrtools scan /path/to/directory --recursive

This will:

* Search for files with Btrieve characteristics
* Display file information in a table
* Show quality scores and content analysis

With rich output::

    btrtools --progress scan /data --recursive --output scan_results.txt

Extracting Records
------------------

Extract records to CSV::

    btrtools export myfile.btr --format csv --output records.csv

Extract to JSON Lines::

    btrtools export myfile.btr --format jsonl --output records.jsonl

Extract to SQLite database::

    btrtools export myfile.btr --format sqlite --output records.db

Extract to Excel spreadsheet::

    btrtools export myfile.btr --format excel --output records.xlsx

Limit the number of records::

    btrtools export myfile.btr --format csv --max-records 1000

Specify record size (if auto-detection fails)::

    btrtools export myfile.btr --format csv --record-size 128

With progress bars::

    btrtools --progress export myfile.btr --format csv --max-records 5000

Schema Detection
----------------

Automatically detect field structure::

    btrtools schema myfile.btr

This analyzes record patterns to identify:

* Field positions and lengths
* Data types (text, numeric, etc.)
* Field boundaries and separators

With rich table output::

    btrtools --progress schema myfile.btr --max-records 1000 --output schema.txt

Checking Integrity
------------------

Basic integrity check::

    btrtools check myfile.btr

Detailed integrity report::

    btrtools check myfile.btr --verbose

With progress indicators::

    btrtools --progress check myfile.btr --verbose

Comparing Files
---------------

Compare two Btrieve files to identify differences::

    btrtools compare file1.btr file2.btr

Compare with detailed record analysis::

    btrtools compare file1.btr file2.btr --max-records 1000

With rich comparison output::

    btrtools --progress compare file1.btr file2.btr

Save comparison results to JSON file::

    btrtools compare file1.btr file2.btr --output comparison.json

Batch Operations
----------------

Process multiple Btrieve files simultaneously::

    btrtools batch *.btr --operation analyze

Batch export to CSV::

    btrtools batch *.btr --operation export --format csv --output-dir ./exports

Parallel processing::

    btrtools batch *.btr --operation schema --parallel 4

Data Repair
-----------

Validate file integrity::

    btrtools repair myfile.btr --validate-only

Attempt to repair corrupted file::

    btrtools repair myfile.btr --fix-corruption --backup

Repair with custom output::

    btrtools repair myfile.btr --fix-corruption --output repaired.btr

Search and Filter
-----------------

Search for text in records::

    btrtools search myfile.btr --query "JOHN DOE"

Regex search::

    btrtools search myfile.btr --query "customer.*\\d+" --regex

Invert match::

    btrtools search myfile.btr --query "test" --invert-match

Export search results::

    btrtools search myfile.btr --query "error" --format csv --output results.csv

Generate Reports
----------------

Create HTML analysis report::

    btrtools report myfile.btr --format html --output-dir ./reports

Generate JSON report::

    btrtools report myfile.btr --format json

Text report::

    btrtools report myfile.btr --format text

Performance Statistics
----------------------

Basic performance stats::

    btrtools stats myfile.btr

Run benchmarks::

    btrtools stats myfile.btr --benchmark

Memory profiling::

    btrtools stats myfile.btr --memory-profile

Save stats to file::

    btrtools stats myfile.btr --output stats.json

Configuration
-------------

BTR-TOOLS can be configured via environment variables:

* ``BTRTOOLS_LOG_LEVEL``: Set logging level (DEBUG, INFO, WARNING, ERROR)
* ``BTRTOOLS_DEBUG``: Enable debug mode (equivalent to --debug flag)

Example::

    export BTRTOOLS_LOG_LEVEL=DEBUG
    btrtools --debug analyze myfile.btr

Batch Processing
----------------

Process multiple files::

    for file in *.btr; do
        btrtools analyze "$file" > "${file%.btr}_analysis.txt"
    done

Extract all files in a directory::

    find /data -name "*.btr" -exec btrtools export {} --format csv --output {}.csv \;

Scan and analyze all Btrieve files in a directory tree::

    btrtools --progress scan /archive --recursive --output file_inventory.txt

    # Then analyze each file
    while read -r file; do
        btrtools --progress analyze "$file"
    done < file_inventory.txt

Error Handling
--------------

BTR-TOOLS includes comprehensive error handling:

* Invalid files generate detailed error reports
* Corrupted data is handled gracefully
* Bug reports are generated automatically for unexpected errors
* All operations are logged with configurable verbosity

Output Formats
--------------

**CSV Output:**

* Standard CSV format with optional headers
* Suitable for import into spreadsheets or databases
* Handles special characters and escaping

**JSON Output:**

* Structured JSON format
* Includes metadata and field information
* Suitable for programmatic processing

**Text Reports:**

* Human-readable analysis reports
* Detailed file structure information
* Integrity check results

Performance Considerations
--------------------------

* Large files may take time to process
* Use ``--quick`` for fast integrity checks
* Extract operations can be memory-intensive for large record sets
* Consider processing large files in batches

Security Notes
--------------

* BTR-TOOLS only reads files; it never modifies them
* Bug reports contain simulated data to protect sensitive information
* All operations are logged for audit purposes
* No network connections are made during normal operation