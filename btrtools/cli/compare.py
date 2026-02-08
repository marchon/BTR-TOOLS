"""
File comparison functionality for Btrieve files.
"""

import os
from typing import Any, Dict

from btrtools.core.btrieve import BtrieveAnalyzer
from btrtools.utils.logging import logger


def compare_files(file1: str, file2: str, max_records: int = 100) -> Dict[str, Any]:
    """
    Compare two Btrieve files and return detailed comparison results.

    Args:
        file1: Path to first Btrieve file
        file2: Path to second Btrieve file
        max_records: Maximum records to compare

    Returns:
        Dictionary with comparison results
    """
    logger.info(f"Comparing files: {file1} vs {file2}")

    # Analyze both files
    analyzer1 = BtrieveAnalyzer(file1)
    analyzer2 = BtrieveAnalyzer(file2)

    info1 = analyzer1.analyze_file()
    info2 = analyzer2.analyze_file()

    # Basic file comparison
    comparison = {
        "file1": {
            "path": file1,
            "filename": os.path.basename(file1),
            "size": info1.file_size,
            "content_type": info1.content_type,
            "ascii_percentage": info1.ascii_percentage,
            "quality_score": info1.quality_score,
        },
        "file2": {
            "path": file2,
            "filename": os.path.basename(file2),
            "size": info2.file_size,
            "content_type": info2.content_type,
            "ascii_percentage": info2.ascii_percentage,
            "quality_score": info2.quality_score,
        },
        "differences": {},
        "similarities": {},
    }

    # Compare basic properties
    differences: Dict[str, Any] = {}
    similarities: Dict[str, Any] = {}

    # Size comparison
    if info1.file_size != info2.file_size:
        differences["file_size"] = {
            "file1": info1.file_size,
            "file2": info2.file_size,
            "difference": abs(info1.file_size - info2.file_size),
        }
    else:
        similarities["file_size"] = info1.file_size

    # Content type
    if info1.content_type != info2.content_type:
        differences["content_type"] = {
            "file1": info1.content_type,
            "file2": info2.content_type,
        }
    else:
        similarities["content_type"] = info1.content_type

    # ASCII percentage (with tolerance)
    ascii_diff = abs(info1.ascii_percentage - info2.ascii_percentage)
    if ascii_diff > 5.0:  # 5% tolerance
        differences["ascii_percentage"] = {
            "file1": info1.ascii_percentage,
            "file2": info2.ascii_percentage,
            "difference": ascii_diff,
        }
    else:
        similarities["ascii_percentage"] = (
            f"{(info1.ascii_percentage + info2.ascii_percentage) / 2:.1f}%"
        )

    # Quality score (with tolerance)
    quality_diff = abs(info1.quality_score - info2.quality_score)
    if quality_diff > 1.0:  # 1.0 tolerance
        differences["quality_score"] = {
            "file1": info1.quality_score,
            "file2": info2.quality_score,
            "difference": quality_diff,
        }
    else:
        similarities["quality_score"] = (
            f"{(info1.quality_score + info2.quality_score) / 2:.1f}"
        )

    # Try record-level comparison if possible
    record_comparison = _compare_records(analyzer1, analyzer2, max_records)
    if record_comparison:
        comparison["record_comparison"] = record_comparison

    comparison["differences"] = differences
    comparison["similarities"] = similarities

    # Overall assessment
    if not differences:
        comparison["assessment"] = "files_appear_identical"
    elif len(differences) == 1 and "file_size" in differences:
        comparison["assessment"] = "size_difference_only"
    elif len(differences) <= 2:
        comparison["assessment"] = "minor_differences"
    else:
        comparison["assessment"] = "significant_differences"

    logger.info(
        f"Comparison complete: {len(differences)} differences, "
        f"{len(similarities)} similarities"
    )
    return comparison


def _compare_records(
    analyzer1: BtrieveAnalyzer, analyzer2: BtrieveAnalyzer, max_records: int
) -> Dict[str, Any]:
    """
    Compare records between two files if possible.

    Returns comparison data or None if not possible.
    """
    try:
        # Try to detect record sizes
        record_size1, _ = analyzer1.detect_record_size(max_records)
        record_size2, _ = analyzer2.detect_record_size(max_records)

        if record_size1 == 0 or record_size2 == 0:
            return None

        if record_size1 != record_size2:
            return {
                "record_sizes_different": True,
                "file1_record_size": record_size1,
                "file2_record_size": record_size2,
            }

        # Extract records for comparison
        records1 = analyzer1.extract_records(record_size1, max_records)
        records2 = analyzer2.extract_records(record_size2, max_records)

        if not records1 or not records2:
            return None

        # Compare record counts
        record_comparison = {
            "record_size": record_size1,
            "records_compared": min(len(records1), len(records2), max_records),
            "file1_record_count": len(records1),
            "file2_record_count": len(records2),
        }

        # Compare actual record data
        matching_records = 0
        total_compared = 0

        for i, (rec1, rec2) in enumerate(zip(records1, records2)):
            if i >= max_records:
                break
            total_compared += 1
            if rec1.raw_data == rec2.raw_data:
                matching_records += 1

        if total_compared > 0:
            record_comparison["identical_records"] = matching_records
            record_comparison["total_compared"] = total_compared
            record_comparison["match_percentage"] = (
                matching_records / total_compared
            ) * 100

        return record_comparison

    except Exception as e:
        logger.debug(f"Could not compare records: {e}")
        return None
