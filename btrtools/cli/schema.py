"""
Schema detection functionality for Btrieve files.
"""

from typing import Any, Dict, List, Optional

from btrtools.core.btrieve import BtrieveAnalyzer, BtrieveRecord


def detect_schema(
    filepath: str, record_size: Optional[int] = None, max_records: int = 1000
) -> Dict[str, Any]:
    """
    Detect schema information from a Btrieve file.

    Args:
        filepath: Path to the Btrieve file
        record_size: Record size (auto-detect if None)
        max_records: Maximum records to analyze

    Returns:
        Dictionary containing schema information
    """
    analyzer = BtrieveAnalyzer(filepath)

    # Auto-detect record size if not provided
    if record_size is None:
        record_size, _ = analyzer.detect_record_size()
        if record_size == 0:
            raise ValueError("Could not detect record size")

    # Extract records for analysis
    records = analyzer.extract_records(record_size, max_records)

    if not records:
        return {"record_size": record_size, "records_analyzed": 0, "fields": []}

    # Analyze field patterns
    field_patterns = _analyze_field_patterns(records)

    # Detect field boundaries and types
    detected_fields = _detect_fields(field_patterns, record_size)

    return {
        "record_size": record_size,
        "records_analyzed": len(records),
        "fields": detected_fields,
    }


def _analyze_field_patterns(records: List[BtrieveRecord]) -> Dict[int, Dict[str, Any]]:
    """
    Analyze patterns in record positions to identify field boundaries.

    Returns a dictionary mapping positions to field characteristics.
    """
    if not records:
        return {}

    record_size = records[0].record_size
    position_stats: Dict[int, Dict[str, Any]] = {}

    # Initialize position statistics
    for pos in range(record_size):
        position_stats[pos] = {
            "ascii_count": 0,
            "digit_count": 0,
            "alpha_count": 0,
            "space_count": 0,
            "null_count": 0,
            "printable_count": 0,
            "total_records": len(records),
            "unique_chars": set(),
        }

    # Analyze each position across all records
    for record in records:
        text = record.decoded_text.ljust(record_size)  # Pad to record size

        for pos, char in enumerate(text):
            if pos >= record_size:
                break

            stats = position_stats[pos]
            stats["unique_chars"].add(char)

            if char == "\x00" or char == "\0":
                stats["null_count"] += 1
            elif char.isdigit():
                stats["digit_count"] += 1
            elif char.isalpha():
                stats["alpha_count"] += 1
            elif char.isspace():
                stats["space_count"] += 1
            elif char.isprintable():
                stats["printable_count"] += 1
                stats["ascii_count"] += 1

    return position_stats


def _detect_fields(
    position_stats: Dict[int, Dict[str, Any]], record_size: int
) -> List[Dict[str, Any]]:
    """
    Detect field boundaries and types from position statistics.
    """
    fields = []
    current_field_start = None
    current_field_type = None

    for pos in range(record_size):
        if pos not in position_stats:
            continue

        stats = position_stats[pos]
        total_records = stats["total_records"]

        # Calculate percentages
        ascii_percent = (stats["ascii_count"] / total_records) * 100
        digit_percent = (stats["digit_count"] / total_records) * 100
        alpha_percent = (stats["alpha_count"] / total_records) * 100
        null_percent = (stats["null_count"] / total_records) * 100

        # Determine position type
        if null_percent > 80:
            pos_type = "null_padding"
        elif digit_percent > 70:
            pos_type = "digits"
        elif alpha_percent > 50:
            pos_type = "alpha"
        elif ascii_percent > 50:
            pos_type = "text"
        else:
            pos_type = "mixed"

        # Field boundary detection
        if current_field_start is None:
            # Start new field
            if pos_type != "null_padding":
                current_field_start = pos
                current_field_type = pos_type
        else:
            # Check if we should end current field
            if pos_type == "null_padding" or pos_type != current_field_type:
                # End current field
                field_length = pos - current_field_start
                if field_length > 0:
                    field_info = _create_field_info(
                        current_field_start,
                        field_length,
                        current_field_type,
                        position_stats,
                    )
                    if field_info:
                        fields.append(field_info)

                # Start new field if not null padding
                if pos_type != "null_padding":
                    current_field_start = pos
                    current_field_type = pos_type
                else:
                    current_field_start = None
                    current_field_type = None

    # Handle final field
    if current_field_start is not None:
        field_length = record_size - current_field_start
        if field_length > 0:
            field_info = _create_field_info(
                current_field_start, field_length, current_field_type, position_stats
            )
            if field_info:
                fields.append(field_info)

    return fields


def _create_field_info(
    start_pos: int,
    length: int,
    field_type: Optional[str],
    position_stats: Dict[int, Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """
    Create field information dictionary.
    """
    if length < 1 or field_type is None:
        return None

    # Analyze the field across its positions
    total_ascii = 0
    total_digits = 0
    total_alpha = 0
    total_records = 0
    unique_chars = set()

    for pos in range(start_pos, start_pos + length):
        if pos in position_stats:
            stats = position_stats[pos]
            total_records = stats["total_records"]
            total_ascii += stats["ascii_count"]
            total_digits += stats["digit_count"]
            total_alpha += stats["alpha_count"]
            unique_chars.update(stats["unique_chars"])

    if total_records == 0:
        return None

    # Determine field type and name
    field_name, field_type_detailed = _infer_field_type_and_name(
        field_type, length, unique_chars, total_digits / total_records
    )

    return {
        "name": field_name,
        "type": field_type_detailed,
        "position": start_pos,
        "length": length,
        "ascii_percent": (total_ascii / (total_records * length)) * 100,
        "digit_percent": (total_digits / (total_records * length)) * 100,
        "alpha_percent": (total_alpha / (total_records * length)) * 100,
    }


def _infer_field_type_and_name(
    field_type: str, length: int, unique_chars: set, avg_digits: float
) -> tuple[str, str]:
    """
    Infer field type and generate a descriptive name.
    """
    # Common field patterns based on dental project experience
    if field_type == "digits":
        if length == 5 and avg_digits > 0.8:
            return "zip_code", "ZIP_CODE"
        elif length >= 10 and avg_digits > 0.9:
            return "phone_number", "PHONE"
        elif length == 4 and all(c.isdigit() or c in "D" for c in unique_chars):
            return "procedure_code", "PROCEDURE_CODE"
        else:
            return f"digit_field_{length}", "DIGITS"

    elif field_type == "alpha":
        if length == 2 and all(len(c) == 1 and c.isalpha() for c in unique_chars):
            return "state_code", "STATE"
        elif length <= 4 and all(len(c) == 1 and c.isupper() for c in unique_chars):
            return "provider_code", "PROVIDER_CODE"
        else:
            return f"alpha_field_{length}", "ALPHA"

    elif field_type == "text":
        if length > 50:
            return "description", "TEXT"
        elif length > 20:
            return "address", "ADDRESS"
        else:
            return f"text_field_{length}", "TEXT"

    else:
        return f"field_{length}", "MIXED"
