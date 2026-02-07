Debugging Guide
===============

This guide covers debugging BTR-TOOLS operations, including logging configuration, error analysis, and troubleshooting common issues.

Logging Configuration
---------------------

BTR-TOOLS uses a comprehensive logging system with multiple levels and outputs.

Log Levels
~~~~~~~~~~

* ``DEBUG``: Detailed diagnostic information
* ``INFO``: General information about operations
* ``WARNING``: Warning messages for potential issues
* ``ERROR``: Error messages for failures
* ``CRITICAL``: Critical errors that prevent operation

Setting Log Level
~~~~~~~~~~~~~~~~~

Via command line::

    btr-analyze myfile.btr --debug

Via environment variable::

    export BTR_LOG_LEVEL=DEBUG
    btr-analyze myfile.btr

Log File Configuration
~~~~~~~~~~~~~~~~~~~~~~

Specify log file location::

    export BTR_LOG_FILE=/var/log/btr-tools.log
    btr-analyze myfile.btr

Default log file location: ``~/.btr-tools/btr-tools.log``

Log Rotation
~~~~~~~~~~~~

Logs are automatically rotated when they reach 10MB, keeping up to 5 backup files.

Console Output
~~~~~~~~~~~~~~

Logs are also displayed on console with color coding:

* Blue: DEBUG
* Green: INFO
* Yellow: WARNING
* Red: ERROR/CRITICAL

Error Analysis
--------------

Common Error Types
~~~~~~~~~~~~~~~~~~

**File Not Found Errors:**

.. code-block:: text

    ERROR: File '/path/to/file.btr' not found
    Cause: Specified file does not exist
    Solution: Check file path and permissions

**Invalid File Format Errors:**

.. code-block:: text

    ERROR: Invalid Btrieve file format
    Cause: File is not a valid Btrieve file or is corrupted
    Solution: Verify file integrity and format

**Permission Errors:**

.. code-block:: text

    ERROR: Permission denied accessing file
    Cause: Insufficient file permissions
    Solution: Check file permissions or run with appropriate privileges

**Memory Errors:**

.. code-block:: text

    ERROR: Out of memory processing file
    Cause: File too large for available memory
    Solution: Process in smaller batches or increase system memory

Bug Reports
-----------

Automatic Bug Report Generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When unexpected errors occur, BTR-TOOLS automatically generates bug reports containing:

* System information
* Python version and environment
* Command line arguments
* Stack trace
* Simulated data (never real file contents)

Bug report location: ``~/.btr-tools/bug-reports/``

Manual Bug Report Creation
~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a bug report manually::

    btr-analyze myfile.btr --create-bug-report

This generates a comprehensive report even if no error occurs.

Bug Report Contents
~~~~~~~~~~~~~~~~~~~

Bug reports include:

* **System Info**: OS, Python version, BTR-TOOLS version
* **Command Context**: Full command line and environment
* **Error Details**: Exception type, message, and stack trace
* **File Metadata**: Safe file information (no actual data)
* **Log Excerpts**: Recent log entries leading to the error
* **Configuration**: Current settings and environment variables

Privacy Protection
~~~~~~~~~~~~~~~~~~

Bug reports never contain actual file data. Instead, they include:

* File size and structure information
* Simulated record data with same format
* Field type information
* Statistical summaries

Troubleshooting Checklist
-------------------------

File Access Issues
~~~~~~~~~~~~~~~~~~

1. Check file exists: ``ls -la /path/to/file.btr``
2. Check permissions: ``stat /path/to/file.btr``
3. Check file type: ``file /path/to/file.btr``
4. Try with absolute path

Memory Issues
~~~~~~~~~~~~~

1. Check available memory: ``free -h`` (Linux) or ``vm_stat`` (macOS)
2. Try processing smaller files first
3. Use ``--quick`` mode for large files
4. Consider splitting large files

Performance Issues
~~~~~~~~~~~~~~~~~~

1. Enable verbose logging to identify bottlenecks
2. Check disk I/O performance
3. Monitor memory usage during processing
4. Consider processing during off-peak hours

Installation Issues
~~~~~~~~~~~~~~~~~~~

1. Verify Python version: ``python --version``
2. Check pip installation: ``pip --version``
3. Try reinstalling: ``pip install --force-reinstall btr-tools``
4. Check for conflicting packages

Development Debugging
---------------------

Debug Mode
~~~~~~~~~~

Enable full debug output::

    export BTR_DEBUG=1
    btr-analyze myfile.btr

This enables:

* Full stack traces on errors
* Detailed internal state logging
* Performance timing information
* Memory usage statistics

Custom Log Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

For advanced debugging, you can modify the logging configuration in the source code.

The logging system is configured in ``btrtools/utils/logging.py``.

Testing with Sample Data
~~~~~~~~~~~~~~~~~~~~~~~~

Use the included test files for debugging::

    python -m pytest tests/ -v

Or run specific tests::

    python -m pytest tests/test_btrieve.py::test_file_analysis -v

Getting Help
------------

If you encounter issues:

1. Check this documentation
2. Review log files for error details
3. Generate and examine bug reports
4. Search existing issues on GitHub
5. Create a new issue with bug report attached

Support Information
~~~~~~~~~~~~~~~~~~~

When reporting issues, please include:

* BTR-TOOLS version (``btr-analyze --version``)
* Python version and platform
* Complete command and error output
* Bug report file (if generated)
* Sample file characteristics (size, format, etc.)