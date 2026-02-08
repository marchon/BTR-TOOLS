"""
File integrity checking functionality for Btrieve files.
"""

from btrtools.core.btrieve import BtrieveAnalyzer


def check_integrity(filepath: str, verbose: bool = False) -> dict:
    """
    Check the integrity of a Btrieve file.

    Args:
        filepath: Path to the Btrieve file
        verbose: Whether to include detailed information

    Returns:
        Dictionary with integrity check results
    """
    analyzer = BtrieveAnalyzer(filepath)

    # Basic integrity check
    result = analyzer.check_integrity()

    if verbose and result["file_exists"] and result["readable"]:
        # Add additional analysis
        try:
            file_info = analyzer.analyze_file()
            result["analysis"] = {
                "file_size": file_info.file_size,
                "content_type": file_info.content_type,
                "ascii_percentage": file_info.ascii_percentage,
                "quality_score": file_info.quality_score,
            }

            # Try record size detection
            try:
                record_size, quality = analyzer.detect_record_size()
                result["analysis"]["detected_record_size"] = record_size
                result["analysis"]["detection_quality"] = quality
            except Exception:
                result["analysis"]["record_size_detection"] = "failed"

        except Exception as e:
            result["analysis_error"] = str(e)

    return result
