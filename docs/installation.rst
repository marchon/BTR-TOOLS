Installation Guide
==================

This guide covers how to install BTR-TOOLS on your system.

Requirements
------------

BTR-TOOLS requires Python 3.8 or later. You can check your Python version with::

    python --version

If you don't have Python 3.8+, download it from `python.org <https://python.org>`_.

Installation from PyPI
-----------------------

The easiest way to install BTR-TOOLS is from PyPI::

    pip install btr-tools

This will install the latest stable version along with all dependencies.

Installation from Source
------------------------

If you want to install from source (for development or testing pre-release versions):

1. Clone the repository::

    git clone https://github.com/your-org/btr-tools.git
    cd btr-tools

2. Install in development mode::

    pip install -e .

This installs BTR-TOOLS in "editable" mode, so changes to the source code are immediately available.

Installation for Development
-----------------------------

If you plan to contribute to BTR-TOOLS:

1. Clone the repository::

    git clone https://github.com/your-org/btr-tools.git
    cd btr-tools

2. Install development dependencies::

    pip install -e ".[dev]"

This includes additional tools for testing, documentation, and development.

Virtual Environment (Recommended)
---------------------------------

It's recommended to install BTR-TOOLS in a virtual environment to avoid conflicts with system packages::

    # Create virtual environment
    python -m venv btr-env

    # Activate virtual environment
    # On Windows:
    btr-env\Scripts\activate
    # On macOS/Linux:
    source btr-env/bin/activate

    # Install BTR-TOOLS
    pip install btr-tools

    # When done, deactivate with:
    deactivate

Verification
------------

After installation, verify BTR-TOOLS is working::

    btr-analyze --help

You should see the help text for the analyze command.

Upgrade
-------

To upgrade to the latest version::

    pip install --upgrade btr-tools

Troubleshooting
---------------

**Command not found**: Make sure the Python scripts directory is in your PATH.

**Permission denied**: Try installing with ``--user``::

    pip install --user btr-tools

**Import errors**: Ensure you're using the correct Python version and virtual environment.

**Build failures**: Make sure you have the necessary build tools installed (usually not needed for BTR-TOOLS).