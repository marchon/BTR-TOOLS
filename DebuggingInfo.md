# BTR-TOOLS Debugging Information

## Overview

BTR-TOOLS includes comprehensive error handling, multi-level debug logging, stack traces, and bug report generation with data simulation to protect proprietary information while providing detailed diagnostic capabilities.

## Logging System

### Log Levels

BTR-TOOLS supports multiple logging levels:

- **DEBUG**: Detailed execution flow, function entry/exit, parameter values
- **INFO**: General information about operations and progress
- **WARNING**: Potential issues that don't prevent operation
- **ERROR**: Errors that prevent successful completion
- **CRITICAL**: Severe errors requiring immediate attention

### Controlling Log Levels

#### Environment Variable
```bash
export BTRTOOLS_LOG_LEVEL=DEBUG
python scripts/btrtools command [args...]
```

#### Command Line Flag
```bash
python scripts/btrtools --debug command [args...]
```

### Log Output

#### Console Logging
- Clean, timestamped output to stderr
- Appropriate level filtering
- Non-intrusive for normal operation

#### File Logging
- Detailed logs saved to `~/.btrtools/logs/`
- Daily rotation (btrtools_YYYYMMDD.log)
- Maximum 10MB per file, 5 backup files
- Includes function names, line numbers, and full context

## Error Handling

### Exception Hierarchy

BTR-TOOLS defines custom exception classes for different error types:

```python
BTRError                    # Base exception class
├── BTRFileError           # File-related errors (missing, permission, I/O)
├── BTRDataError           # Data processing errors (corruption, parsing)
├── BTRConfigError         # Configuration errors
└── BTRValidationError     # Input validation errors
```

### Exit Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | Operation completed successfully |
| 1 | Generic Error | Unexpected exceptions |
| 2 | File Error | File not found, permission denied, I/O errors |
| 3 | Data Error | Corrupted data, invalid formats, parsing failures |
| 4 | Config Error | Configuration issues |
| 5 | Validation Error | Invalid parameters or constraints |

### Safe Execution

All command execution is wrapped in `safe_execute()` which:

- Catches all exceptions
- Logs full stack traces
- Generates bug reports
- Returns appropriate exit codes
- Provides user-friendly error messages

## Bug Reports

### Automatic Generation

Bug reports are automatically generated for any exception:

- **Unique ID**: Format `BTR-YYYYMMDD-HHMMSS-HASH`
- **Location**: `~/.btrtools/bug-reports/`
- **Format**: JSON with complete diagnostic information

### Report Contents

Each bug report includes:

```json
{
  "report_id": "BTR-20260207-172221-1987b0ca",
  "timestamp": "2026-02-07T17:22:21.188891",
  "version": "1.0.0",
  "platform": "macOS-26.3-arm64-arm-64bit",
  "command": "analyze",
  "error_type": "BTRFileError",
  "error_message": "File not found: nonexistent.btr",
  "stack_trace": "Full Python stack trace...",
  "context": {
    "command": "analyze",
    "args": {"file": "nonexistent.btr", "max_records": 100},
    "file_path": null,
    "record_size": null
  },
  "simulated_data": {
    "file_info": {
      "filename": "simulated_nonexistent.btr",
      "size": 12345,
      "simulated_content_type": "mixed_data"
    }
  },
  "system_info": {
    "platform": "macOS-26.3-arm64-arm-64bit",
    "python_version": "3.12.8",
    "memory": {"total": 17179869184, "available": 1234567890}
  }
}
```

### Data Protection

Bug reports use **simulated data** to avoid exposing proprietary information:

- **File Names**: `simulated_filename.ext`
- **File Contents**: `SIMULATED DATA RECORD FOR BUG REPORT`
- **Field Values**: `SIM_VALUE_1`, `SIM_VALUE_2`
- **Sizes**: Randomized placeholder values
- **Real Data**: Never included in reports

## User Error Messages

### File-Related Errors
```
❌ Error: File not found: missing.btr
This appears to be a file-related error. Please check:
  - File exists and is readable
  - File is not corrupted
  - You have permission to access the file

🐛 Bug report generated: BTR-20260207-172221-1987b0ca
Please include this report ID when submitting bug reports.
Bug report location: /Users/user/.btrtools/bug-reports/BTR-20260207-172221-1987b0ca.json
```

### Data-Related Errors
```
❌ Error: Could not detect record size - file may be corrupted or not a Btrieve file
This appears to be a data processing error. Please check:
  - File contains valid Btrieve data
  - Record size is correct
  - File is not truncated
```

### Validation Errors
```
❌ Error: Invalid record size: -1
This appears to be a data validation error. Please check:
  - Input parameters are valid
  - File format is supported
```

## Debugging Commands

### Enable Debug Logging
```bash
# Environment variable
BTRTOOLS_LOG_LEVEL=DEBUG btrtools analyze file.btr

# Command line flag
btrtools --debug analyze file.btr
```

### Check Bug Reports
```bash
# List recent bug reports
ls -la ~/.btrtools/bug-reports/

# View a specific report
cat ~/.btrtools/bug-reports/BTR-20260207-172221-1987b0ca.json
```

### Check Logs
```bash
# View current log
tail -f ~/.btrtools/logs/btrtools_$(date +%Y%m%d).log

# Search for specific errors
grep "ERROR" ~/.btrtools/logs/btrtools_*.log
```

## Troubleshooting Common Issues

### "Could not detect record size"
**Symptoms**: Analysis fails with record size detection error
**Debug Steps**:
1. Enable debug logging: `BTRTOOLS_LOG_LEVEL=DEBUG btrtools analyze file.btr`
2. Check file size and basic integrity: `btrtools check file.btr --verbose`
3. Try manual record size: `btrtools analyze file.btr --record-size 128`

### "No records found to export"
**Symptoms**: Export commands return empty results
**Debug Steps**:
1. Verify file integrity: `btrtools check file.btr`
2. Check record size detection: `btrtools analyze file.btr`
3. Try different record sizes: `btrtools export file.btr --record-size 64`

### High Memory Usage
**Symptoms**: Tool consumes excessive memory with large files
**Debug Steps**:
1. Use `--max-records` to limit processing
2. Process files in batches
3. Check available memory in bug reports

### Permission Errors
**Symptoms**: "Permission denied" errors
**Debug Steps**:
1. Check file permissions: `ls -la file.btr`
2. Verify user has read access
3. Check if file is locked by another process

## Performance Debugging

### Logging Overhead
- Debug logging adds significant overhead
- Use INFO level for normal operation
- File logging has minimal console impact

### Memory Profiling
Bug reports include memory information:
```json
"system_info": {
  "memory": {
    "total": 17179869184,
    "available": 1234567890,
    "percent": 65.5
  }
}
```

### Timing Information
Enable debug logging to see operation timing:
```
2026-02-07 17:22:19,752 - btrtools - DEBUG - Executing cmd_check
2026-02-07 17:22:19,752 - btrtools - DEBUG - Successfully executed cmd_check
```

## Development Debugging

### Adding Debug Logging
```python
from btrtools.utils.logging import logger

def my_function():
    logger.debug(f"Processing with parameters: {params}")
    # ... function logic ...
    logger.debug(f"Completed processing, result: {result}")
```

### Custom Error Types
```python
from btrtools.utils.logging import BTRDataError

def validate_data(data):
    if not data:
        raise BTRDataError("Data validation failed: empty dataset")
```

### Testing Error Handling
```python
from btrtools.utils.logging import safe_execute, create_error_context

context = create_error_context("test", {"param": "value"})
result, exit_code = safe_execute(problematic_function, context, arg1, arg2)
```

## Directory Structure

```
~/.btrtools/
├── logs/
│   ├── btrtools_20260207.log
│   ├── btrtools_20260206.log
│   └── ...
└── bug-reports/
    ├── BTR-20260207-172221-1987b0ca.json
    ├── BTR-20260207-152340-4f2c8d1e.json
    └── ...
```

## Support Information

When reporting bugs, please include:

1. **Bug Report ID**: The unique identifier shown in error messages
2. **Command Used**: Full command line that caused the error
3. **File Information**: File size, source, any known corruption
4. **Environment**: OS version, Python version, available memory
5. **Expected Behavior**: What you expected to happen

Bug reports contain all necessary diagnostic information while protecting your proprietary data through simulation.