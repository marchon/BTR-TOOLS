Exception Classes
=================

BTR-TOOLS defines a comprehensive hierarchy of exception classes for different types of errors.

Base Exception Class
--------------------

.. autoclass:: btrtools.exceptions.BTRError
   :members:
   :undoc-members:
   :show-inheritance:

File-Related Exceptions
-----------------------

.. autoclass:: btrtools.exceptions.BTRFileError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: btrtools.exceptions.BTRFileNotFoundError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: btrtools.exceptions.BTRInvalidFileError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: btrtools.exceptions.BTRCorruptedFileError
   :members:
   :undoc-members:
   :show-inheritance:

Data-Related Exceptions
-----------------------

.. autoclass:: btrtools.exceptions.BTRDataError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: btrtools.exceptions.BTRRecordError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: btrtools.exceptions.BTRFieldError
   :members:
   :undoc-members:
   :show-inheritance:

Analysis Exceptions
-------------------

.. autoclass:: btrtools.exceptions.BTRAnalysisError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: btrtools.exceptions.BTRIntegrityError
   :members:
   :undoc-members:
   :show-inheritance:

Configuration Exceptions
------------------------

.. autoclass:: btrtools.exceptions.BTRConfigError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: btrtools.exceptions.BTRLoggingError
   :members:
   :undoc-members:
   :show-inheritance:

Exception Hierarchy
-------------------

::

    BTRError
    ├── BTRFileError
    │   ├── BTRFileNotFoundError
    │   ├── BTRInvalidFileError
    │   └── BTRCorruptedFileError
    ├── BTRDataError
    │   ├── BTRRecordError
    │   └── BTRFieldError
    ├── BTRAnalysisError
    ├── BTRIntegrityError
    ├── BTRConfigError
    └── BTRLoggingError

Usage Examples
--------------

Catching specific exceptions::

    from btrtools.exceptions import BTRFileNotFoundError, BTRInvalidFileError

    try:
        analyzer = BtrieveAnalyzer(file_path)
        analyzer.analyze()
    except BTRFileNotFoundError:
        print("File not found")
    except BTRInvalidFileError:
        print("Invalid Btrieve file")
    except BTRError as e:
        print(f"BTR-TOOLS error: {e}")

Catching all BTR-TOOLS exceptions::

    from btrtools.exceptions import BTRError

    try:
        # BTR-TOOLS operations
        pass
    except BTRError as e:
        # Handle any BTR-TOOLS specific error
        print(f"BTR-TOOLS error: {e}")
        # Generate bug report
        error_handler.generate_bug_report(e)