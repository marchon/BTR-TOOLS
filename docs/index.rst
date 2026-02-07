BTR-TOOLS Documentation
=======================

.. image:: https://img.shields.io/badge/python-3.8+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

.. image:: https://readthedocs.org/projects/btr-tools/badge/?version=latest
   :target: https://btr-tools.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

BTR-TOOLS is a generic command-line toolkit for Btrieve database file analysis and export.
It provides comprehensive tools for analyzing legacy Btrieve database files, extracting records,
and generating detailed reports about file structure and content.

Overview
--------

BTR-TOOLS supports multiple Btrieve file formats and provides:

* **File Analysis**: Detailed analysis of Btrieve file structure and metadata
* **Record Extraction**: Safe extraction of records with proper error handling
* **Integrity Checking**: Comprehensive validation of file integrity
* **Debug Logging**: Multi-level logging with stack traces and bug reports
* **CLI Interface**: Command-line tools for batch processing and automation

Key Features
------------

* **Robust Error Handling**: Comprehensive exception handling with custom error classes
* **Multi-level Logging**: Configurable logging with file rotation and console output
* **Bug Report Generation**: Automated bug reports with data simulation for privacy
* **Cross-platform**: Works on Windows, macOS, and Linux
* **Zero Dependencies**: Uses only Python standard library
* **Production Ready**: Enterprise-grade error handling and logging

Installation
------------

Install from PyPI::

    pip install btr-tools

Or install from source::

    git clone https://github.com/your-org/btr-tools.git
    cd btr-tools
    pip install -e .

Quick Start
-----------

Analyze a Btrieve file::

    btr-analyze /path/to/file.btr

Extract records to CSV::

    btr-extract /path/to/file.btr --output records.csv

Check file integrity::

    btr-check /path/to/file.btr

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide:

   installation
   usage
   debugging
   troubleshooting

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   api/modules
   api/exceptions
   api/logging
   api/core

.. toctree::
   :maxdepth: 1
   :caption: Development:

   contributing
   changelog

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

License
-------

BTR-TOOLS is licensed under the MIT License. See the `LICENSE <https://github.com/your-org/btr-tools/blob/main/LICENSE>`_ file for details.

Support
-------

For support and questions:

* `GitHub Issues <https://github.com/your-org/btr-tools/issues>`_
* `Documentation <https://btr-tools.readthedocs.io/>`_
* Email: support@btr-tools.org

Contributing
------------

We welcome contributions! Please see our `Contributing Guide <contributing.html>`_ for details on how to get started.