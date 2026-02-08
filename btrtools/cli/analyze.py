"""
File analysis functionality for Btrieve files.
"""

from btrtools.core.btrieve import BtrieveAnalyzer, BtrieveFileInfo


def analyze_file(filepath: str, max_records: int = 100) -> BtrieveFileInfo:
    """
    Analyze a Btrieve file and return detailed information.

    Args:
        filepath: Path to the Btrieve file
        max_records: Maximum number of records to analyze for record size detection

    Returns:
        BtrieveFileInfo object with analysis results
    """
    analyzer = BtrieveAnalyzer(filepath)

    # Basic file analysis
    info = analyzer.analyze_file()

    # Detect record size
    try:
        record_size, quality_score = analyzer.detect_record_size(max_records)
        info.detected_record_size = record_size
        info.quality_score = quality_score

        # Estimate total records
        data_size = info.file_size - (2 * 4096)  # Subtract FCR pages
        if record_size > 0:
            info.estimated_records = data_size // record_size

    except (ValueError, ZeroDivisionError, AttributeError):
        # Record size detection failed, but we still have basic info
        pass

    return info
