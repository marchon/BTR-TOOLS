Core Classes
============

This module contains the core classes for Btrieve file analysis.

BtrieveAnalyzer Class
---------------------

.. autoclass:: btrtools.core.btrieve.BtrieveAnalyzer
   :members:
   :undoc-members:
   :show-inheritance:

FileAnalyzer Class
------------------

.. autoclass:: btrtools.core.analyzer.FileAnalyzer
   :members:
   :undoc-members:
   :show-inheritance:

RecordExtractor Class
---------------------

.. autoclass:: btrtools.core.analyzer.RecordExtractor
   :members:
   :undoc-members:
   :show-inheritance:

Data Structures
---------------

File Metadata
~~~~~~~~~~~~~

.. autoclass:: btrtools.core.btrieve.FileMetadata
   :members:
   :undoc-members:
   :show-inheritance:

Analysis Result
~~~~~~~~~~~~~~~

.. autoclass:: btrtools.core.btrieve.AnalysisResult
   :members:
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

Basic file analysis::

    from btrtools.core.btrieve import BtrieveAnalyzer

    analyzer = BtrieveAnalyzer("myfile.btr")
    result = analyzer.analyze_file()

    print(f"File version: {result.metadata.version}")
    print(f"Record count: {result.metadata.record_count}")

Record extraction::

    from btrtools.core.analyzer import RecordExtractor

    extractor = RecordExtractor("myfile.btr")
    records = extractor.extract_records()

    for record in records:
        print(record.data)

Error handling::

    from btrtools.exceptions import BTRError
    from btrtools.utils.logging import get_logger

    logger = get_logger(__name__)

    try:
        analyzer = BtrieveAnalyzer("myfile.btr")
        result = analyzer.analyze_file()
    except BTRError as e:
        logger.error(f"Analysis failed: {e}")
        # Handle error appropriately