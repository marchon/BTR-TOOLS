"""
Core Btrieve file handling utilities.

This module contains the core functionality for reading, analyzing, and extracting
data from Btrieve database files, based on the Btrieve v5 format specifications
and patterns discovered during the dental practice data reconstruction project.
"""

import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from btrtools.utils.logging import (
    BTRDataError,
    BTRFileError,
    BTRValidationError,
    logger,
)


@dataclass
class BtrieveFileInfo:
    """Information about a Btrieve file."""

    filename: str
    filepath: str
    file_size: int
    page_size: int = 4096
    header_size: int = 16
    fcr_pages: int = 2
    estimated_records: Optional[int] = None
    detected_record_size: Optional[int] = None
    content_type: str = "unknown"
    ascii_percentage: float = 0.0
    digit_sequences: int = 0
    date_patterns: int = 0
    quality_score: float = 0.0


@dataclass
class BtrieveRecord:
    """A single Btrieve record with extracted data."""

    record_num: int
    record_size: int
    raw_bytes: bytes
    hex_dump: str
    decoded_text: str
    printable_chars: int
    has_digits: bool
    has_alpha: bool
    extracted_fields: Dict[str, str]


class BtrieveAnalyzer:
    """Core Btrieve file analyzer based on dental practice reconstruction."""

    # Common record sizes to test (based on successful extractions)
    COMMON_RECORD_SIZES = [32, 64, 128, 256, 512, 1024]

    # Btrieve v5 constants
    PAGE_SIZE = 4096
    HEADER_SIZE = 16
    FCR_PAGES = 2

    def __init__(self, filepath: str):
        """Initialize analyzer for a Btrieve file."""
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0

    def analyze_file(self) -> BtrieveFileInfo:
        """Analyze basic file structure and content patterns."""
        logger.debug(f"Analyzing file: {self.filepath}")

        if not os.path.exists(self.filepath):
            logger.error(f"File not found: {self.filepath}")
            raise BTRFileError(f"File not found: {self.filepath}")

        try:
            info = BtrieveFileInfo(
                filename=self.filename, filepath=self.filepath, file_size=self.file_size
            )

            with open(self.filepath, "rb") as f:
                data = f.read()

            logger.debug(f"Read {len(data)} bytes from {self.filepath}")

        except (IOError, OSError) as e:
            logger.error(f"Failed to read file {self.filepath}: {e}")
            raise BTRFileError(f"Failed to read file: {e}")

        # Skip FCR pages
        data_start = self.FCR_PAGES * self.PAGE_SIZE
        data_pages = data[data_start:]

        # Analyze content patterns
        total_bytes = len(data_pages)
        if total_bytes == 0:
            logger.warning(f"No data pages found in {self.filepath}")
            return info

        # ASCII analysis
        ascii_count = sum(1 for b in data_pages if 32 <= b <= 126)
        info.ascii_percentage = (ascii_count / total_bytes) * 100

        # Pattern detection
        try:
            text = data_pages.decode("latin-1", errors="ignore")

            # Digit sequences (3+ consecutive digits)
            info.digit_sequences = len(re.findall(r"\d{3,}", text))

            # Date patterns (MM/DD/YYYY, etc.)
            date_patterns = [
                r"\d{1,2}/\d{1,2}/\d{2,4}",  # MM/DD/YYYY
                r"\d{4}-\d{1,2}-\d{1,2}",  # YYYY-MM-DD
                r"\d{1,2}-\d{1,2}-\d{4}",  # DD-MM-YYYY
            ]
            info.date_patterns = sum(
                len(re.findall(pattern, text)) for pattern in date_patterns
            )

            # Content type classification
            info.content_type = self._classify_content_type(text, info)

            logger.debug(
                f"Content analysis complete: {info.ascii_percentage:.1f}% ASCII, "
                f"{info.digit_sequences} digit sequences"
            )

        except Exception as e:
            logger.warning(f"Content analysis failed for {self.filepath}: {e}")
            info.content_type = "analysis_failed"

        return info

    def _classify_content_type(self, text: str, info: BtrieveFileInfo) -> str:
        """Classify the content type based on patterns."""
        # Insurance provider patterns
        insurance_patterns = [
            r"\b[A-Z]{3,4}\b",  # Provider codes
            r"P\.?O\.?\s*Box\s+\d+",  # PO Box addresses
            r"\b\d{5}(?:-\d{4})?\b",  # ZIP codes
            r"\b800\d{7,10}\b",  # 800 phone numbers
        ]
        insurance_score = sum(
            len(re.findall(pattern, text)) for pattern in insurance_patterns
        )

        # Clinical patterns
        clinical_patterns = [
            r"\bD\d{4}\b",  # Dental procedure codes
            r"\b\d+\.\d{2}\b",  # Money amounts
        ]
        clinical_score = sum(
            len(re.findall(pattern, text)) for pattern in clinical_patterns
        )

        # Sequential patterns (index files)
        sequential_score = len(re.findall(r"(?:6,7,8,9,10|11,12,13,14,15)", text))

        # Character set patterns (system files)
        charset_score = len(re.findall(r"ABCDEFGHIJKLMNOPQRSTUVWXYZ", text))

        # Classification logic
        if insurance_score > 10:
            return "insurance_providers"
        elif clinical_score > 5:
            return "clinical_data"
        elif sequential_score > 3:
            return "index_sequence"
        elif charset_score > 2:
            return "character_set"
        elif info.ascii_percentage < 1.0:
            return "binary_data"
        elif info.ascii_percentage > 50.0:
            return "text_data"
        else:
            return "mixed_data"

    def detect_record_size(self, max_records: int = 100) -> Tuple[int, float]:
        """Detect the optimal record size using quality scoring."""
        logger.debug(
            f"Detecting record size for {self.filepath} (max_records: {max_records})"
        )

        if not os.path.exists(self.filepath):
            raise BTRFileError(f"File not found: {self.filepath}")

        best_size = 64  # Default
        best_score = 0.0

        for record_size in self.COMMON_RECORD_SIZES:
            try:
                logger.debug(f"Trying record size: {record_size}")
                records = self.extract_records(record_size, max_records)
                if not records:
                    logger.debug(f"No records found for size {record_size}")
                    continue

                # Quality scoring
                score = self._calculate_quality_score(records)
                logger.debug(f"Record size {record_size}: score {score:.2f}")

                if score > best_score:
                    best_score = score
                    best_size = record_size

            except Exception as e:
                logger.debug(f"Failed to analyze record size {record_size}: {e}")
                continue

        if best_score == 0.0:
            logger.warning(f"Could not detect record size for "
                           f"{self.filepath}")
            raise BTRDataError(
                "Could not detect record size - file may be corrupted or "
                "not a Btrieve file"
            )

        logger.info(
            f"Detected record size: {best_size} bytes (score: {best_score:.2f})"
        )
        return best_size, best_score / 100.0

    def extract_records(
        self, record_size: int, max_records: Optional[int] = None
    ) -> List[BtrieveRecord]:
        """Extract records from the Btrieve file."""
        logger.debug(
            f"Extracting records from {self.filepath} "
            f"(record_size: {record_size}, max_records: {max_records})"
        )

        if not os.path.exists(self.filepath):
            raise BTRFileError(f"File not found: {self.filepath}")

        if record_size <= 0:
            raise BTRValidationError(f"Invalid record size: {record_size}")

        records = []

        try:
            with open(self.filepath, "rb") as f:
                # Skip FCR pages
                f.seek(self.FCR_PAGES * self.PAGE_SIZE)

                record_num = 1
                while max_records is None or record_num <= max_records:
                    record_bytes = f.read(record_size)
                    if len(record_bytes) != record_size:
                        if len(record_bytes) > 0:
                            logger.debug(
                                f"Incomplete record {record_num} at end of file"
                            )
                        break

                    # Create record object
                    record = self._create_record(record_num, record_size, record_bytes)
                    records.append(record)

                    record_num += 1

        except (IOError, OSError) as e:
            logger.error(f"Failed to read records from {self.filepath}: {e}")
            raise BTRFileError(f"Failed to read file: {e}")

        logger.debug(f"Extracted {len(records)} records")
        return records

    def _create_record(
        self, record_num: int, record_size: int, record_bytes: bytes
    ) -> BtrieveRecord:
        """Create a BtrieveRecord object from raw bytes."""
        # Decode text
        try:
            decoded_text = record_bytes.decode("latin-1").rstrip("\x00")
        except (UnicodeDecodeError, AttributeError):
            decoded_text = "<decode_error>"

        # Analysis
        printable_chars = sum(1 for c in decoded_text if c.isprintable())
        has_digits = any(c.isdigit() for c in decoded_text)
        has_alpha = any(c.isalpha() for c in decoded_text)

        # Field extraction (basic patterns)
        extracted_fields = self._extract_basic_fields(decoded_text)

        return BtrieveRecord(
            record_num=record_num,
            record_size=record_size,
            raw_bytes=record_bytes,
            hex_dump=record_bytes.hex(),
            decoded_text=decoded_text,
            printable_chars=printable_chars,
            has_digits=has_digits,
            has_alpha=has_alpha,
            extracted_fields=extracted_fields,
        )

    def _extract_basic_fields(self, text: str) -> Dict[str, str]:
        """Extract basic fields using regex patterns."""
        fields = {}

        # Provider code
        code_match = re.search(r"\b([A-Z]{3,4})\b", text)
        fields["provider_code"] = code_match.group(1) if code_match else ""

        # Address
        addr_match = re.search(r"(P\.?O\.?\s*Box\s+\d+[A-Z]?)", text, re.IGNORECASE)
        fields["address"] = addr_match.group(1) if addr_match else ""

        # State
        state_match = re.search(
            r"\b(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|"
            r"MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|"
            r"TN|TX|UT|VT|VA|WA|WV|WI|WY)\b",
            text,
        )
        fields["state"] = state_match.group(1) if state_match else ""

        # ZIP code
        zip_match = re.search(r"\b(\d{5}(?:-\d{4})?)\b", text)
        fields["zip_code"] = zip_match.group(1) if zip_match else ""

        # Phone
        phone_match = re.search(r"\b(800\d{7,10})\b", text)
        fields["phone"] = phone_match.group(1) if phone_match else ""

        # Procedure code
        proc_match = re.search(r"\b(D\d{4})\b", text)
        fields["procedure_code"] = proc_match.group(1) if proc_match else ""

        # Amount
        amount_match = re.search(r"\b(\d+\.\d{2})\b", text)
        fields["amount"] = amount_match.group(1) if amount_match else ""

        return fields

    def _calculate_quality_score(self, records: List[BtrieveRecord]) -> float:
        """Calculate quality score for a set of records."""
        if not records:
            return 0.0

        total_records = len(records)

        # Metrics
        text_records = sum(1 for r in records if r.decoded_text.strip())
        digit_records = sum(1 for r in records if r.has_digits)
        alpha_records = sum(1 for r in records if r.has_alpha)
        avg_printable = sum(r.printable_chars for r in records) / total_records

        # Weighted score
        score = (
            (text_records / total_records) * 30  # Text content
            + (digit_records / total_records) * 20  # Digit patterns
            + (alpha_records / total_records) * 20  # Alpha patterns
            + min(avg_printable / 50, 1) * 30  # Printable density
        )

        return score

    def check_integrity(self) -> Dict[str, Any]:
        """Check file integrity and detect potential corruption."""
        logger.debug(f"Checking integrity of {self.filepath}")

        integrity_info: Dict[str, Any] = {
            "file_exists": False,
            "readable": False,
            "valid_size": False,
            "has_fcr_pages": False,
            "data_pages": 0,
            "corruption_detected": False,
            "corruption_details": [],
        }

        if not os.path.exists(self.filepath):
            integrity_info["corruption_details"].append("File does not exist")
            integrity_info["corruption_detected"] = True
            logger.warning(f"File does not exist: {self.filepath}")
            return integrity_info

        integrity_info["file_exists"] = True

        try:
            with open(self.filepath, "rb") as f:
                data = f.read()
            integrity_info["readable"] = True
            logger.debug(f"Successfully read {len(data)} bytes")
        except Exception as e:
            integrity_info["corruption_details"].append(f"Read error: {e}")
            integrity_info["corruption_detected"] = True
            logger.error(f"Failed to read file {self.filepath}: {e}")
            return integrity_info

        # Size validation
        min_size = (self.FCR_PAGES + 1) * self.PAGE_SIZE  # At least FCR + 1 data page
        if len(data) >= min_size:
            integrity_info["valid_size"] = True
        else:
            detail = f"File too small: {len(data)} < {min_size}"
            integrity_info["corruption_details"].append(detail)
            integrity_info["corruption_detected"] = True
            logger.warning(f"File size validation failed: {detail}")

        # FCR pages check
        if len(data) >= self.FCR_PAGES * self.PAGE_SIZE:
            integrity_info["has_fcr_pages"] = True
            data_start = self.FCR_PAGES * self.PAGE_SIZE
            data_pages_size = len(data) - data_start
            integrity_info["data_pages"] = data_pages_size // (
                self.PAGE_SIZE - self.HEADER_SIZE
            )
            logger.debug(f"File has {integrity_info['data_pages']} data pages")

        if integrity_info["corruption_detected"]:
            logger.warning(f"Corruption detected in {self.filepath}")
        else:
            logger.info(f"Integrity check passed for {self.filepath}")

        return integrity_info
