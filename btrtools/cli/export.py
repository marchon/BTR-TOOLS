"""
Data export functionality for Btrieve files.
"""

import csv
import json
import sqlite3
import os
from typing import Optional, List

from btrtools.core.btrieve import BtrieveAnalyzer, BtrieveRecord


def export_file(
    filepath: str,
    format_type: str,
    record_size: Optional[int] = None,
    max_records: Optional[int] = None,
    output_file: Optional[str] = None
) -> str:
    """
    Export Btrieve file data to the specified format.

    Args:
        filepath: Path to the Btrieve file
        format_type: Export format ('csv', 'jsonl', or 'sqlite')
        record_size: Record size (auto-detect if None)
        max_records: Maximum records to export (None for all)
        output_file: Output file path (auto-generate if None)

    Returns:
        Path to the exported file
    """
    analyzer = BtrieveAnalyzer(filepath)

    # Auto-detect record size if not provided
    if record_size is None:
        record_size, _ = analyzer.detect_record_size()
        if record_size == 0:
            raise ValueError("Could not detect record size")

    # Extract records
    records = analyzer.extract_records(record_size, max_records)

    if not records:
        raise ValueError("No records found to export")

    # Generate output filename if not provided
    if output_file is None:
        base_name = os.path.splitext(os.path.basename(filepath))[0]
        if format_type == 'csv':
            output_file = f"{base_name}.csv"
        elif format_type == 'jsonl':
            output_file = f"{base_name}.jsonl"
        elif format_type == 'sqlite':
            output_file = f"{base_name}.db"

    # Export based on format
    if format_type == 'csv':
        _export_csv(records, output_file)
    elif format_type == 'jsonl':
        _export_jsonl(records, output_file)
    elif format_type == 'sqlite':
        _export_sqlite(records, output_file)
    else:
        raise ValueError(f"Unsupported format: {format_type}")

    return output_file


def _export_csv(records: List[BtrieveRecord], output_file: str) -> None:
    """Export records to CSV format."""
    if not records:
        return

    # Collect all unique field names
    field_names = set()
    for record in records:
        field_names.update(record.extracted_fields.keys())

    # Add standard fields
    standard_fields = [
        'record_num', 'record_size', 'decoded_text',
        'printable_chars', 'has_digits', 'has_alpha'
    ]
    all_fields = standard_fields + sorted(list(field_names))

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=all_fields)
        writer.writeheader()

        for record in records:
            row = {
                'record_num': record.record_num,
                'record_size': record.record_size,
                'decoded_text': record.decoded_text,
                'printable_chars': record.printable_chars,
                'has_digits': record.has_digits,
                'has_alpha': record.has_alpha,
            }
            # Add extracted fields
            row.update(record.extracted_fields)
            writer.writerow(row)


def _export_jsonl(records: List[BtrieveRecord], output_file: str) -> None:
    """Export records to JSON Lines format."""
    with open(output_file, 'w', encoding='utf-8') as f:
        for record in records:
            data = {
                'record_num': record.record_num,
                'record_size': record.record_size,
                'raw_bytes': record.raw_bytes.hex(),
                'decoded_text': record.decoded_text,
                'printable_chars': record.printable_chars,
                'has_digits': record.has_digits,
                'has_alpha': record.has_alpha,
                'extracted_fields': record.extracted_fields
            }
            f.write(json.dumps(data, ensure_ascii=False) + '\n')


def _export_sqlite(records: List[BtrieveRecord], output_file: str) -> None:
    """Export records to SQLite database."""
    if not records:
        return

    # Collect all unique field names for table creation
    field_names = set()
    for record in records:
        field_names.update(record.extracted_fields.keys())

    # Create table schema
    standard_fields = [
        ('record_num', 'INTEGER'),
        ('record_size', 'INTEGER'),
        ('raw_bytes', 'TEXT'),
        ('decoded_text', 'TEXT'),
        ('printable_chars', 'INTEGER'),
        ('has_digits', 'BOOLEAN'),
        ('has_alpha', 'BOOLEAN')
    ]

    # Add extracted fields (all as TEXT for flexibility)
    extracted_fields = [(name, 'TEXT') for name in sorted(field_names)]

    all_fields = standard_fields + extracted_fields

    # Create table SQL
    columns_sql = ', '.join(f'"{name}" {type_}' for name, type_ in all_fields)
    create_table_sql = f'CREATE TABLE btrieve_records ({columns_sql})'

    # Insert SQL
    placeholders = ', '.join('?' for _ in all_fields)
    insert_sql = f'INSERT INTO btrieve_records VALUES ({placeholders})'

    conn = sqlite3.connect(output_file)
    try:
        cursor = conn.cursor()

        # Create table
        cursor.execute(create_table_sql)

        # Insert records
        for record in records:
            values = [
                record.record_num,
                record.record_size,
                record.raw_bytes.hex(),
                record.decoded_text,
                record.printable_chars,
                record.has_digits,
                record.has_alpha,
            ]

            # Add extracted field values
            for field_name, _ in extracted_fields:
                values.append(record.extracted_fields.get(field_name, ''))

            cursor.execute(insert_sql, values)

        conn.commit()

    finally:
        conn.close()