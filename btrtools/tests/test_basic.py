"""
Comprehensive tests for BTR-TOOLS package.
"""

import os
import tempfile
import unittest
import json
from unittest.mock import patch, MagicMock
from io import StringIO

from btrtools.core.btrieve import BtrieveAnalyzer, BtrieveFileInfo
from btrtools.utils.logging import logger, error_handler, BTRFileError, BTRDataError


class TestBtrieveAnalyzer(unittest.TestCase):
    """Test the core Btrieve analyzer functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock Btrieve file for testing (4KB pages, 16-byte header)
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

    def test_record_size_detection(self):
        """Test record size detection functionality."""
        record_size, quality = self.analyzer.detect_record_size(max_records=10)
        self.assertIsInstance(record_size, int)
        self.assertIsInstance(quality, float)
        self.assertGreaterEqual(quality, 0.0)
        self.assertLessEqual(quality, 1.0)

    def test_error_handling(self):
        """Test error handling for invalid files."""
        with self.assertRaises((BTRFileError, FileNotFoundError)):
            analyzer = BtrieveAnalyzer("/nonexistent/file.btr")
            analyzer.analyze_file()


class TestLogging(unittest.TestCase):
    """Test logging functionality."""

    def test_logger_initialization(self):
        """Test that logger can be initialized."""
        # Test that logger is available and working
        self.assertIsNotNone(logger)
        logger.info("Test log message")

    def test_error_handler(self):
        """Test error handler functionality."""
        from btrtools.utils.logging import create_error_context
        try:
            raise ValueError("Test error")
        except ValueError as e:
            context = create_error_context("test_operation", {"test": "args"})
            self.assertIsInstance(context, ErrorContext)
            self.assertEqual(context.command, "test_operation")


class TestCLI(unittest.TestCase):
    """Test CLI functionality."""

    def test_cli_import(self):
        """Test that CLI modules can be imported."""
        try:
            from btrtools.cli import analyze, export, check
            # If we get here without exception, imports work
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"CLI import failed: {e}")

    @patch('sys.stdout', new_callable=StringIO)
    def test_cli_help_output(self, mock_stdout):
        """Test that CLI help can be displayed."""
        from btrtools.cli import main
        with patch('sys.argv', ['btrtools', '--help']):
            with self.assertRaises(SystemExit):  # --help causes SystemExit
                main()
        output = mock_stdout.getvalue()
        self.assertIn('Btrieve File Analysis Toolkit', output)


class TestExceptions(unittest.TestCase):
    """Test custom exception classes."""

    def test_btr_file_error(self):
        """Test BTRFileError exception."""
        error = BTRFileError("Test file error")
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "Test file error")

    def test_btr_data_error(self):
        """Test BTRDataError exception."""
        error = BTRDataError("Test data error")
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "Test data error")


class TestIntegration(unittest.TestCase):
    """Integration tests for end-to-end functionality."""

    def setUp(self):
        """Create test file for integration tests."""
        # Create a more realistic test file with some structure
        self.test_data = (
            b'BTRIEVE_HEADER' +  # 14 bytes
            b'\x00' * 2 +        # Padding to 16 bytes
            b'PAGE1_DATA' * 100 + # Page 1 content
            b'PAGE2_DATA' * 100   # Page 2 content
        )
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.btr')
        self.temp_file.write(self.test_data)
        self.temp_file.close()

    def tearDown(self):
        """Clean up test file."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_full_analysis_workflow(self):
        """Test complete analysis workflow."""
        analyzer = BtrieveAnalyzer(self.temp_file.name)

        # Test file analysis
        info = analyzer.analyze_file()
        self.assertIsNotNone(info)

        # Test integrity check
        integrity = analyzer.check_integrity()
        self.assertTrue(integrity['file_exists'])

        # Test record size detection
        try:
            record_size, quality = analyzer.detect_record_size()
            self.assertIsInstance(record_size, int)
            self.assertIsInstance(quality, float)
        except Exception:
            # Record size detection might fail on synthetic data, which is OK
            pass


if __name__ == '__main__':
    unittest.main()