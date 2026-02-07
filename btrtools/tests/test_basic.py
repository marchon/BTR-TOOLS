"""
Basic tests for BTR-TOOLS package.
"""

import os
import tempfile
import unittest
from unittest.mock import patch

from btrtools.core.btrieve import BtrieveAnalyzer, BtrieveFileInfo


class TestBtrieveAnalyzer(unittest.TestCase):
    """Test the core Btrieve analyzer functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock Btrieve file for testing
        self.test_data = b'ABCD' * 1024  # 4KB of test data
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(self.test_data)
        self.temp_file.close()
        self.analyzer = BtrieveAnalyzer(self.temp_file.name)

    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_file.name)

    def test_file_info_creation(self):
        """Test that file info is created correctly."""
        info = self.analyzer.analyze_file()

        self.assertIsInstance(info, BtrieveFileInfo)
        self.assertEqual(info.filename, os.path.basename(self.temp_file.name))
        self.assertEqual(info.file_size, len(self.test_data))
        self.assertEqual(info.page_size, 4096)
        self.assertEqual(info.header_size, 16)
        self.assertEqual(info.fcr_pages, 2)

    def test_integrity_check(self):
        """Test integrity checking."""
        result = self.analyzer.check_integrity()

        self.assertTrue(result['file_exists'])
        self.assertTrue(result['readable'])
        self.assertTrue(result['valid_size'])
        self.assertTrue(result['has_fcr_pages'])
        self.assertFalse(result['corruption_detected'])

    def test_content_analysis(self):
        """Test content pattern analysis."""
        info = self.analyzer.analyze_file()

        # Test data is all ASCII letters, so should have high ASCII percentage
        self.assertGreater(info.ascii_percentage, 90)
        self.assertEqual(info.digit_sequences, 0)  # No digits in test data
        self.assertEqual(info.date_patterns, 0)    # No dates in test data


class TestCLI(unittest.TestCase):
    """Test CLI functionality."""

    def test_cli_import(self):
        """Test that CLI modules can be imported."""
        try:
            from btrtools.cli import scan, analyze, export, schema, check
            # If we get here without exception, imports work
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"CLI import failed: {e}")


if __name__ == '__main__':
    unittest.main()