Changelog
=========

All notable changes to BTR-TOOLS will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

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