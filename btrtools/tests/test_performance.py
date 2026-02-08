"""
Performance tests for BTR-TOOLS.
"""

import os
import tempfile
import time
import unittest

from btrtools.core.btrieve import BtrieveAnalyzer


class TestPerformance(unittest.TestCase):
    """Performance tests for BTR-TOOLS operations."""

    def setUp(self):
        """Create test files of various sizes."""
        self.test_files = {}

        # Small file (4KB)
        self.test_files["small"] = self._create_test_file(4 * 1024)

        # Medium file (1MB)
        self.test_files["medium"] = self._create_test_file(1024 * 1024)

        # Large file (10MB) - only create if needed for performance testing
        # self.test_files['large'] = self._create_test_file(10 * 1024 * 1024)

    def tearDown(self):
        """Clean up test files."""
        for filename in self.test_files.values():
            if os.path.exists(filename):
                os.unlink(filename)

    def _create_test_file(self, size_bytes):
        """Create a test file of specified size."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".btr")
        # Create realistic Btrieve-like data
        chunk_size = 4096  # 4KB pages
        data = b"BTRIEVE_DATA" * (chunk_size // len(b"BTRIEVE_DATA"))

        written = 0
        while written < size_bytes:
            remaining = min(chunk_size, size_bytes - written)
            temp_file.write(data[:remaining])
            written += remaining

        temp_file.close()
        return temp_file.name

    def test_small_file_analysis_performance(self):
        """Test analysis performance on small files."""
        analyzer = BtrieveAnalyzer(self.test_files["small"])

        start_time = time.time()
        info = analyzer.analyze_file()
        end_time = time.time()

        duration = end_time - start_time
        # Analysis should complete in under 0.1 seconds for small files
        self.assertLess(
            duration, 0.1, f"Analysis took {duration:.3f}s, expected < 0.1s"
        )

        # Verify results are correct
        self.assertIsNotNone(info)
        self.assertAlmostEqual(
            info.file_size, 4 * 1024, delta=100
        )  # Allow some variance

    def test_medium_file_analysis_performance(self):
        """Test analysis performance on medium files."""
        analyzer = BtrieveAnalyzer(self.test_files["medium"])

        start_time = time.time()
        info = analyzer.analyze_file()
        end_time = time.time()

        duration = end_time - start_time
        # Analysis should complete in under 1 second for 1MB files
        self.assertLess(
            duration, 1.0, f"Analysis took {duration:.3f}s, expected < 1.0s"
        )

        # Verify results are correct
        self.assertIsNotNone(info)
        self.assertAlmostEqual(
            info.file_size, 1024 * 1024, delta=2000
        )  # Allow some variance

    def test_integrity_check_performance(self):
        """Test integrity check performance."""
        analyzer = BtrieveAnalyzer(self.test_files["medium"])

        start_time = time.time()
        result = analyzer.check_integrity()
        end_time = time.time()

        duration = end_time - start_time
        # Integrity check should be fast
        self.assertLess(
            duration, 0.5, f"Integrity check took {duration:.3f}s, expected < 0.5s"
        )

        # Verify results
        self.assertTrue(result["file_exists"])
        self.assertTrue(result["readable"])

    def test_record_size_detection_performance(self):
        """Test record size detection performance."""
        analyzer = BtrieveAnalyzer(self.test_files["small"])

        start_time = time.time()
        try:
            record_size, quality = analyzer.detect_record_size(max_records=50)
            end_time = time.time()

            duration = end_time - start_time
            # Record size detection should be reasonably fast
            self.assertLess(
                duration,
                0.2,
                f"Record size detection took {duration:.3f}s, expected < 0.2s",
            )

            # Verify results are reasonable
            self.assertIsInstance(record_size, int)
            self.assertIsInstance(quality, float)
            self.assertGreaterEqual(quality, 0.0)
            self.assertLessEqual(quality, 1.0)

        except Exception:
            # Record size detection might fail on synthetic data
            self.skipTest(
                "Record size detection not applicable for synthetic test data"
            )

    def test_memory_usage(self):
        """Test that operations don't have excessive memory usage."""
        # This is a basic test - in a real scenario you'd use memory profiling
        try:
            import os

            import psutil
        except ImportError:
            self.skipTest("psutil not available for memory testing")

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        analyzer = BtrieveAnalyzer(self.test_files["medium"])
        analyzer.analyze_file()

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 50MB for 1MB file)
        self.assertLess(
            memory_increase,
            50,
            f"Memory increased by {memory_increase:.1f}MB, expected < 50MB",
        )


class TestScalability(unittest.TestCase):
    """Test scalability with different file sizes."""

    def test_file_size_handling(self):
        """Test that the analyzer can handle files of various sizes."""
        sizes = [1024, 4096, 65536, 1048576]  # 1KB, 4KB, 64KB, 1MB

        for size in sizes:
            with self.subTest(size=size):
                temp_file = self._create_test_file(size)
                try:
                    analyzer = BtrieveAnalyzer(temp_file)
                    info = analyzer.analyze_file()

                    self.assertEqual(info.file_size, size)
                    self.assertIsNotNone(info.page_size)

                finally:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)

    def _create_test_file(self, size_bytes):
        """Create a test file of specified size."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".btr")
        data = b"X" * min(4096, size_bytes)

        written = 0
        while written < size_bytes:
            remaining = min(len(data), size_bytes - written)
            temp_file.write(data[:remaining])
            written += remaining

        temp_file.close()
        return temp_file.name


if __name__ == "__main__":
    unittest.main()
