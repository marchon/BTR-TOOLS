Logging System
==============

BTR-TOOLS includes a comprehensive logging system with multiple levels, file rotation, and console output.

Logger Class
------------

.. autoclass:: btrtools.utils.logging.BTRLogger
   :members:
   :undoc-members:
   :show-inheritance:

Error Handler Class
-------------------

.. autoclass:: btrtools.utils.logging.ErrorHandler
   :members:
   :undoc-members:
   :show-inheritance:

Bug Report Class
----------------

.. autoclass:: btrtools.utils.logging.BugReport
   :members:
   :undoc-members:
   :show-inheritance:

Safe Execute Function
---------------------

.. autofunction:: btrtools.utils.logging.safe_execute

Logging Configuration
---------------------

Log Levels
~~~~~~~~~~

The logging system supports standard Python logging levels:

* ``DEBUG`` (10): Detailed diagnostic information
* ``INFO`` (20): General information about operations
* ``WARNING`` (30): Warning messages for potential issues
* ``ERROR`` (40): Error messages for failures
* ``CRITICAL`` (50): Critical errors that prevent operation

Default Configuration
~~~~~~~~~~~~~~~~~~~~~

* **Log Level**: INFO
* **Log File**: ``~/.btr-tools/btr-tools.log``
* **Max File Size**: 10 MB
* **Backup Count**: 5 files
* **Console Output**: Colored output enabled

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

* ``BTR_LOG_LEVEL``: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
* ``BTR_LOG_FILE``: Specify custom log file path
* ``BTR_DEBUG``: Enable debug mode (equivalent to --debug flag)

Configuration File
~~~~~~~~~~~~~~~~~~

Advanced logging configuration can be done by modifying ``btrtools/utils/logging.py``.

Log Format
----------

Console Format
~~~~~~~~~~~~~~

::

    [LEVEL] message

File Format
~~~~~~~~~~~

::

    YYYY-MM-DD HH:MM:SS - btr-tools - LEVEL - module:function:line - message

Log Rotation
------------

Logs are automatically rotated when they reach the maximum size:

* Maximum file size: 10 MB
* Backup files: 5 generations
* Rotation timing: On file size limit

Backup files are named with ``.1``, ``.2``, etc. suffixes.

Usage Examples
--------------

Basic logging::

    from btrtools.utils.logging import get_logger

    logger = get_logger(__name__)
    logger.info("Starting analysis")
    logger.debug("Processing page 1")
    logger.error("Failed to read record")

Exception logging::

    try:
        # Some operation
        pass
    except Exception as e:
        logger.exception("Operation failed")

Custom log levels::

    import os
    os.environ['BTR_LOG_LEVEL'] = 'DEBUG'
    # Restart or reconfigure logger

Custom log file::

    import os
    os.environ['BTR_LOG_FILE'] = '/var/log/my-app.log'

Performance Considerations
--------------------------

* DEBUG logging can impact performance
* File I/O for logging may slow down operations
* Log rotation is handled automatically
* Consider log level based on use case:

  * Development: DEBUG
  * Production monitoring: INFO
  * Production alerts: WARNING
  * Error tracking: ERROR

Log Analysis
------------

Searching logs::

    # Find errors
    grep "ERROR" ~/.btr-tools/btr-tools.log

    # Find specific operations
    grep "analyze_file" ~/.btr-tools/btr-tools.log

    # Recent entries
    tail -50 ~/.btr-tools/btr-tools.log

Log maintenance::

    # Clean old logs
    find ~/.btr-tools/ -name "btr-tools.log.*" -mtime +30 -delete

    # Archive logs
    tar -czf logs-$(date +%Y%m%d).tar.gz ~/.btr-tools/*.log*