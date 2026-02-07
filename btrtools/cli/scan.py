"""
Directory scanning functionality for Btrieve files.
"""

import os
from pathlib import Path
from typing import List

from btrtools.core.btrieve import BtrieveAnalyzer, BtrieveFileInfo


def scan_directory(directory: str, recursive: bool = False) -> List[BtrieveFileInfo]:
    """
    Scan a directory for Btrieve files.

    Args:
        directory: Directory path to scan
        recursive: Whether to scan subdirectories

    Returns:
        List of BtrieveFileInfo objects for detected files
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Not a directory: {directory}")

    btrieve_files = []

    # Walk through directory
    if recursive:
        for root, dirs, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                if _is_potential_btrieve_file(filepath):
                    try:
                        analyzer = BtrieveAnalyzer(filepath)
                        info = analyzer.analyze_file()
                        # Only include files with some Btrieve-like characteristics
                        if info.ascii_percentage > 0.1 or info.file_size > 8192:
                            btrieve_files.append(info)
                    except Exception:
                        # Skip files that can't be analyzed
                        continue
    else:
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath) and _is_potential_btrieve_file(filepath):
                try:
                    analyzer = BtrieveAnalyzer(filepath)
                    info = analyzer.analyze_file()
                    # Only include files with some Btrieve-like characteristics
                    if info.ascii_percentage > 0.1 or info.file_size > 8192:
                        btrieve_files.append(info)
                except Exception:
                    # Skip files that can't be analyzed
                    continue

    # Sort by quality score (highest first)
    btrieve_files.sort(key=lambda x: x.quality_score, reverse=True)

    return btrieve_files


def _is_potential_btrieve_file(filepath: str) -> bool:
    """
    Check if a file could potentially be a Btrieve file.

    This is a heuristic check based on file size and extension.
    """
    if not os.path.isfile(filepath):
        return False

    # Check file size (Btrieve files are typically at least 8KB)
    file_size = os.path.getsize(filepath)
    if file_size < 8192:  # 8KB minimum
        return False

    # Check file extension (optional, but common)
    filename = os.path.basename(filepath).lower()
    btrieve_extensions = ['.btr', '.dat', '.idx', '.key']

    # If it has a known Btrieve extension, it's likely a candidate
    if any(filename.endswith(ext) for ext in btrieve_extensions):
        return True

    # For files without extensions, check if size is multiple of page size
    # Btrieve files are often multiples of 4096 bytes (page size)
    if '.' not in filename and file_size % 4096 == 0:
        return True

    # For other files, we'll let the analyzer decide
    return True