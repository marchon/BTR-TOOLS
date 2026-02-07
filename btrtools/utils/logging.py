"""
Logging and error handling utilities for BTR-TOOLS.

This module provides comprehensive logging, exception handling, and bug report
generation capabilities with data simulation to protect proprietary information.
"""

import logging
import logging.handlers
import sys
import traceback
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import json
import os


@dataclass
class ErrorContext:
    """Context information for errors."""
    command: str
    args: Dict[str, Any]
    file_path: Optional[str] = None
    record_size: Optional[int] = None
    operation: Optional[str] = None
    record_count: Optional[int] = None


@dataclass
class BugReport:
    """Structured bug report with simulated data."""
    report_id: str
    timestamp: str
    version: str
    platform: str
    command: str
    error_type: str
    error_message: str
    stack_trace: str
    context: ErrorContext
    simulated_data: Dict[str, Any]
    system_info: Dict[str, Any]


class BTRLogger:
    """Enhanced logging system for BTR-TOOLS."""

    def __init__(self, name: str = "btrtools", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Console handler with custom formatter
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler for detailed logs (if log directory exists)
        self._setup_file_logging()

        self.logger.info("BTR-TOOLS logger initialized")

    def _setup_file_logging(self):
        """Setup file logging if possible."""
        try:
            log_dir = Path.home() / ".btrtools" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)

            log_file = log_dir / f"btrtools_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)

            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

        except Exception as e:
            # If file logging fails, just continue with console logging
            self.logger.debug(f"File logging setup failed: {e}")

    def set_level(self, level: str):
        """Set logging level."""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }

        if level.upper() in level_map:
            self.logger.setLevel(level_map[level.upper()])
            for handler in self.logger.handlers:
                handler.setLevel(level_map[level.upper()])

    def debug(self, message: str, *args, **kwargs):
        """Log debug message."""
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        """Log info message."""
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log warning message."""
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """Log error message."""
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """Log critical message."""
        self.logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs):
        """Log exception with traceback."""
        self.logger.exception(message, *args, **kwargs)


class BTRError(Exception):
    """Base exception class for BTR-TOOLS."""

    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        super().__init__(message)
        self.context = context or ErrorContext(command="unknown", args={})


class BTRFileError(BTRError):
    """File-related errors."""
    pass


class BTRDataError(BTRError):
    """Data processing errors."""
    pass


class BTRConfigError(BTRError):
    """Configuration errors."""
    pass


class BTRValidationError(BTRError):
    """Data validation errors."""
    pass


class ErrorHandler:
    """Centralized error handling and bug report generation."""

    def __init__(self, logger: BTRLogger):
        self.logger = logger
        self.version = "1.0.0"

    def handle_error(self, error: Exception, context: ErrorContext) -> int:
        """
        Handle an error with comprehensive logging and user feedback.

        Returns exit code.
        """
        # Log the full error with stack trace
        self.logger.exception(f"Error in {context.command}: {error}")

        # Create bug report
        bug_report = self._create_bug_report(error, context)

        # Save bug report
        self._save_bug_report(bug_report)

        # Show user-friendly error message
        self._show_user_error(error, context, bug_report.report_id)

        # Return appropriate exit code
        return self._get_exit_code(error)

    def _create_bug_report(self, error: Exception, context: ErrorContext) -> BugReport:
        """Create a comprehensive bug report with simulated data."""
        import platform

        # Generate unique report ID
        error_hash = hashlib.md5(f"{datetime.now()}{error}{context}".encode()).hexdigest()[:8]
        report_id = f"BTR-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{error_hash}"

        # Get stack trace
        stack_trace = "".join(traceback.format_exception(type(error), error, error.__traceback__))

        # Simulate sensitive data
        simulated_data = self._simulate_data(context)

        # System information
        system_info = {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'architecture': platform.architecture(),
            'processor': platform.processor(),
            'memory': self._get_memory_info()
        }

        return BugReport(
            report_id=report_id,
            timestamp=datetime.now().isoformat(),
            version=self.version,
            platform=platform.platform(),
            command=context.command,
            error_type=type(error).__name__,
            error_message=str(error),
            stack_trace=stack_trace,
            context=context,
            simulated_data=simulated_data,
            system_info=system_info
        )

    def _simulate_data(self, context: ErrorContext) -> Dict[str, Any]:
        """Generate simulated data to avoid exposing proprietary information."""
        simulated = {}

        if context.file_path:
            # Simulate file information
            simulated['file_info'] = {
                'filename': f"simulated_{Path(context.file_path).name}",
                'size': 12345,  # Simulated size
                'simulated_content_type': 'mixed_data'
            }

        if context.record_size:
            simulated['record_info'] = {
                'record_size': context.record_size,
                'simulated_records': [
                    {
                        'record_num': 1,
                        'simulated_text': 'SIMULATED DATA RECORD FOR BUG REPORT',
                        'simulated_fields': {
                            'field1': 'SIM_VALUE_1',
                            'field2': 'SIM_VALUE_2',
                            'field3': '12345'
                        }
                    }
                ]
            }

        if context.operation:
            simulated['operation_context'] = {
                'operation': context.operation,
                'simulated_parameters': {
                    'param1': 'simulated_value',
                    'param2': 42
                }
            }

        return simulated

    def _get_memory_info(self) -> Dict[str, Any]:
        """Get basic memory information."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent
            }
        except ImportError:
            return {'error': 'psutil not available'}

    def _save_bug_report(self, report: BugReport):
        """Save bug report to file."""
        try:
            report_dir = Path.home() / ".btrtools" / "bug-reports"
            report_dir.mkdir(parents=True, exist_ok=True)

            report_file = report_dir / f"{report.report_id}.json"

            # Convert dataclasses to dicts for JSON serialization
            report_dict = {
                'report_id': report.report_id,
                'timestamp': report.timestamp,
                'version': report.version,
                'platform': report.platform,
                'command': report.command,
                'error_type': report.error_type,
                'error_message': report.error_message,
                'stack_trace': report.stack_trace,
                'context': {
                    'command': report.context.command,
                    'args': report.context.args,
                    'file_path': report.context.file_path,
                    'record_size': report.context.record_size,
                    'operation': report.context.operation,
                    'record_count': report.context.record_count
                },
                'simulated_data': report.simulated_data,
                'system_info': report.system_info
            }

            with open(report_file, 'w') as f:
                json.dump(report_dict, f, indent=2)

            self.logger.info(f"Bug report saved: {report_file}")

        except Exception as e:
            self.logger.error(f"Failed to save bug report: {e}")

    def _show_user_error(self, error: Exception, context: ErrorContext, report_id: str):
        """Show user-friendly error message."""
        print(f"\n❌ Error: {error}", file=sys.stderr)

        if isinstance(error, BTRFileError):
            print("This appears to be a file-related error. Please check:", file=sys.stderr)
            print("  - File exists and is readable", file=sys.stderr)
            print("  - File is not corrupted", file=sys.stderr)
            print("  - You have permission to access the file", file=sys.stderr)

        elif isinstance(error, BTRDataError):
            print("This appears to be a data processing error. Please check:", file=sys.stderr)
            print("  - File contains valid Btrieve data", file=sys.stderr)
            print("  - Record size is correct", file=sys.stderr)
            print("  - File is not truncated", file=sys.stderr)

        elif isinstance(error, BTRValidationError):
            print("This appears to be a data validation error. Please check:", file=sys.stderr)
            print("  - Input parameters are valid", file=sys.stderr)
            print("  - File format is supported", file=sys.stderr)

        print(f"\n🐛 Bug report generated: {report_id}", file=sys.stderr)
        print("Please include this report ID when submitting bug reports.", file=sys.stderr)
        print(f"Bug report location: {Path.home() / '.btrtools' / 'bug-reports' / f'{report_id}.json'}", file=sys.stderr)

        # Show debug info if debug logging is enabled
        if self.logger.logger.isEnabledFor(logging.DEBUG):
            print(f"\n🔍 Debug Information:", file=sys.stderr)
            print(f"Command: {context.command}", file=sys.stderr)
            print(f"File: {context.file_path or 'N/A'}", file=sys.stderr)
            print(f"Record Size: {context.record_size or 'auto'}", file=sys.stderr)
            print(f"Operation: {context.operation or 'N/A'}", file=sys.stderr)

    def _get_exit_code(self, error: Exception) -> int:
        """Get appropriate exit code for error type."""
        if isinstance(error, (BTRFileError, FileNotFoundError, PermissionError)):
            return 2  # File-related errors
        elif isinstance(error, (BTRDataError, ValueError)):
            return 3  # Data-related errors
        elif isinstance(error, BTRConfigError):
            return 4  # Configuration errors
        elif isinstance(error, BTRValidationError):
            return 5  # Validation errors
        else:
            return 1  # Generic error


# Global instances
logger = BTRLogger()
error_handler = ErrorHandler(logger)


def safe_execute(func, context: ErrorContext, *args, **kwargs):
    """
    Execute a function with comprehensive error handling.

    Returns (result, exit_code) tuple.
    """
    try:
        logger.debug(f"Executing {func.__name__} with context: {context}")
        result = func(*args, **kwargs)
        logger.debug(f"Successfully executed {func.__name__}")

        # If the function returns an integer, treat it as an exit code
        if isinstance(result, int):
            return result, result
        else:
            return result, 0

    except Exception as e:
        logger.debug(f"Exception in {func.__name__}: {e}")
        exit_code = error_handler.handle_error(e, context)
        return None, exit_code


def create_error_context(command: str, args: Dict[str, Any], **kwargs) -> ErrorContext:
    """Create an error context from command arguments."""
    return ErrorContext(
        command=command,
        args=args,
        file_path=kwargs.get('file_path'),
        record_size=kwargs.get('record_size'),
        operation=kwargs.get('operation'),
        record_count=kwargs.get('record_count')
    )