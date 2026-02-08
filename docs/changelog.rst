Changelog
=========

All notable changes to BTR-TOOLS will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[2.3.0] - 2026-02-07
--------------------

**Added**

* Comprehensive code quality improvements and linting fixes
* Enhanced type annotations throughout the codebase
* Improved error handling and validation

**Changed**

* Refactored HTML template generation for better maintainability
* Updated all f-string formatting for consistency and readability
* Improved code structure and organization

**Fixed**

* Resolved all flake8 linting violations (100+ issues fixed)
* Fixed syntax errors in f-string concatenations
* Corrected long lines and formatting issues
* Removed unused imports and variables
* Fixed unnecessary f-strings and other code quality issues

**Security**

* Enhanced input validation and error handling
* Improved security through better code practices

[2.2.0] - 2026-02-07
--------------------

**Added**

* Excel export functionality with ``btrtools export --format excel`` command
* Batch processing with ``btrtools batch`` command for processing multiple files
* Data repair capabilities with ``btrtools repair`` command
* Advanced search and filtering with ``btrtools search`` command
* Data visualization reports with ``btrtools report`` command
* Performance profiling and statistics with ``btrtools stats`` command
* Support for regex search patterns and case-insensitive matching
* Parallel processing support for batch operations
* Memory usage profiling and benchmarking tools
* HTML, JSON, and text report formats
* Comprehensive test coverage for all new features

**Changed**

* Updated CLI help text with new command examples
* Enhanced documentation with usage examples for all new features
* Added new dependencies: openpyxl, psutil
* Improved error handling and validation for new commands

**Fixed**

* Test file creation issues for batch processing tests
* Memory profiling compatibility issues
* Report generation edge cases

[2.1.0] - 2026-02-07
--------------------

**Added**

* Rich CLI output with progress bars and colored terminal interface
* `--progress` / `-P` flag for enhanced user experience
* Comprehensive test suite with unit, integration, and performance tests
* GitHub Actions CI/CD pipeline with multi-platform testing
* Automated code quality tools (black, isort, flake8, mypy)
* Security scanning with bandit and safety
* Enhanced documentation with usage examples
* New CLI commands: scan, export, schema
* File comparison functionality with ``btrtools compare`` command
* Improved error handling and user feedback

**Changed**

* Enhanced all CLI commands to support rich output
* Improved performance and memory usage in testing
* Updated documentation with new features and examples

**Fixed**

* CLI argument parsing issues
* Test import errors and missing dependencies
* Documentation inconsistencies

**Security**

* Added security scanning to CI/CD pipeline
* Enhanced input validation for CLI arguments

[1.0.0] - 2023-12-01
--------------------

**Added**

* Initial release of BTR-TOOLS
* Basic Btrieve file analysis functionality
* Simple command-line interface
* Support for Btrieve v5 files
* Record extraction capabilities

**Known Issues**

* Limited error handling
* No logging system
* Not installable as package
* Basic documentation only