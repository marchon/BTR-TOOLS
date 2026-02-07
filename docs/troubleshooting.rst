Troubleshooting Guide
====================

This guide helps resolve common issues with BTR-TOOLS.

Installation Problems
---------------------

"Command not found" Error
~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:** ``btr-analyze: command not found``

**Solutions:**

1. **Check PATH:** Ensure Python scripts directory is in PATH::

    # On Windows
    echo $PATH

    # On macOS/Linux
    echo $PATH
    which python
    python -c "import site; print(site.getsitepackages())"

2. **Reinstall with user flag:** ::

    pip install --user btr-tools

3. **Use full path:** ::

    python -m btrtools.cli.analyze /path/to/file.btr

4. **Virtual environment issues:** Activate your virtual environment::

    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate     # Windows

Import Errors
~~~~~~~~~~~~~

**Problem:** ``ModuleNotFoundError`` or ``ImportError``

**Solutions:**

1. **Check installation:** ::

    pip list | grep btr-tools

2. **Reinstall package:** ::

    pip uninstall btr-tools
    pip install btr-tools

3. **Python version mismatch:** Ensure using correct Python version::

    python --version
    pip --version

4. **Virtual environment:** Make sure you're in the right environment

File Access Issues
------------------

Permission Denied
~~~~~~~~~~~~~~~~~

**Problem:** ``PermissionError: [Errno 13] Permission denied``

**Solutions:**

1. **Check file permissions:** ::

    ls -la /path/to/file.btr

2. **Change permissions:** ::

    chmod 644 /path/to/file.btr

3. **Run as administrator/sudo:** (Use with caution)::

    sudo btr-analyze /path/to/file.btr

4. **Check parent directory permissions**

File Not Found
~~~~~~~~~~~~~~

**Problem:** ``FileNotFoundError``

**Solutions:**

1. **Verify path:** ::

    ls -la /path/to/file.btr

2. **Use absolute path:** ::

    btr-analyze /full/path/to/file.btr

3. **Check for special characters:** Escape spaces and special characters::

    btr-analyze "/path/with spaces/file.btr"

4. **Network drives:** Ensure network connection is stable

Memory Issues
-------------

Out of Memory
~~~~~~~~~~~~~

**Problem:** ``MemoryError`` or system slowdown

**Solutions:**

1. **Check system memory:** ::

    # Linux
    free -h

    # macOS
    vm_stat

    # Windows
    systeminfo | findstr Memory

2. **Process smaller batches:** ::

    btr-extract largefile.btr --start 0 --count 10000 --output batch1.csv
    btr-extract largefile.btr --start 10000 --count 10000 --output batch2.csv

3. **Use quick mode:** ::

    btr-check largefile.btr --quick

4. **Increase system memory** or use a machine with more RAM

Performance Issues
------------------

Slow Processing
~~~~~~~~~~~~~~~

**Problem:** Operations take too long

**Solutions:**

1. **Check disk I/O:** ::

    # Linux
    iostat -x 1

    # macOS
    iostat -w 1

2. **Use SSD storage** for better performance

3. **Close other applications** consuming resources

4. **Process during off-peak hours**

5. **Use ``--quick`` mode** where available

File Format Issues
------------------

Invalid File Format
~~~~~~~~~~~~~~~~~~~

**Problem:** ``BTRFileError: Invalid Btrieve file format``

**Solutions:**

1. **Verify file type:** ::

    file /path/to/file.btr
    head -c 100 /path/to/file.btr | hexdump -C

2. **Check file corruption:** ::

    btr-check /path/to/file.btr --verbose

3. **Try different Btrieve version:** Some files may require specific version support

4. **Contact support** with file characteristics

Corrupted Records
~~~~~~~~~~~~~~~~~

**Problem:** Errors extracting specific records

**Solutions:**

1. **Skip corrupted records:** ::

    btr-extract file.btr --skip-errors --output clean.csv

2. **Identify corrupted areas:** ::

    btr-analyze file.btr --verbose | grep -A 10 -B 10 "corrupt"

3. **Extract partial data:** Use ``--start`` and ``--count`` to extract good sections

4. **Check file integrity:** ::

    btr-check file.btr

Logging Issues
--------------

No Log Output
~~~~~~~~~~~~~

**Problem:** No logs generated

**Solutions:**

1. **Check log directory permissions:** ::

    ls -la ~/.btr-tools/
    mkdir -p ~/.btr-tools/

2. **Set log file explicitly:** ::

    export BTR_LOG_FILE=/tmp/btr-tools.log
    btr-analyze file.btr

3. **Check log level:** ::

    export BTR_LOG_LEVEL=INFO

4. **Enable debug mode:** ::

    btr-analyze file.btr --debug

Log File Too Large
~~~~~~~~~~~~~~~~~~

**Problem:** Log files consuming too much space

**Solutions:**

1. **Reduce log level:** ::

    export BTR_LOG_LEVEL=WARNING

2. **Change log file location:** ::

    export BTR_LOG_FILE=/tmp/btr-tools.log

3. **Manual cleanup:** ::

    rm ~/.btr-tools/btr-tools.log.*

4. **Disable logging:** (not recommended)::

    export BTR_LOG_FILE=/dev/null

Configuration Issues
--------------------

Settings Not Applied
~~~~~~~~~~~~~~~~~~~~

**Problem:** Environment variables ignored

**Solutions:**

1. **Export variables correctly:** ::

    export BTR_LOG_LEVEL=DEBUG
    echo $BTR_LOG_LEVEL

2. **Use before command:** ::

    BTR_LOG_LEVEL=DEBUG btr-analyze file.btr

3. **Check shell configuration**

4. **Restart shell** if variables set in profile

Python Path Issues
~~~~~~~~~~~~~~~~~~

**Problem:** Module import issues in custom scripts

**Solutions:**

1. **Add to Python path:** ::

    export PYTHONPATH=$PYTHONPATH:/path/to/btr-tools

2. **Use absolute imports:** ::

    from btrtools.core.btrieve import BtrieveAnalyzer

3. **Install in development mode:** ::

    pip install -e /path/to/btr-tools

Network and Remote Files
------------------------

Network Drive Issues
~~~~~~~~~~~~~~~~~~~~

**Problem:** Problems accessing files on network drives

**Solutions:**

1. **Check network connection**

2. **Use local copy:** ::

    cp /network/path/file.btr /local/path/
    btr-analyze /local/path/file.btr

3. **Check mount options**

4. **Ensure stable connection** during processing

Cloud Storage
~~~~~~~~~~~~~

**Problem:** Issues with cloud-synced files

**Solutions:**

1. **Disable sync** during processing

2. **Use local copies** of cloud files

3. **Check file locking** by cloud client

4. **Ensure file fully downloaded**

Getting Help
------------

If these solutions don't resolve your issue:

1. **Generate bug report:** ::

    btr-analyze file.btr --create-bug-report

2. **Check logs:** ::

    tail -50 ~/.btr-tools/btr-tools.log

3. **Collect system info:** ::

    python -c "import sys, platform; print(f'Python: {sys.version}'); print(f'Platform: {platform.platform()}')"

4. **Contact support** with the above information