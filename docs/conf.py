# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'BTR-TOOLS'
copyright = '2026, Btrieve Analysis Team'
author = 'Btrieve Analysis Team'
release = '2.3.0'
version = '2.3.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',      # Core autodoc functionality
    'sphinx.ext.autosummary',  # Generate autosummary tables
    'sphinx.ext.viewcode',     # Add source code links
    'sphinx.ext.napoleon',     # Support for NumPy/Google style docstrings
    'sphinx.ext.intersphinx',  # Link to external documentation
    'sphinx.ext.todo',         # Support for todo items
    'sphinx.ext.coverage',     # Check documentation coverage
]

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'member-order': 'bysource',
}

# Autosummary settings
autosummary_generate = True

# Napoleon settings (for Google/NumPy style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Theme options
html_theme_options = {
    'canonical_url': '',
    'analytics_id': '',
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    # Toc options
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Custom CSS (if needed)
html_css_files = []

# Logo and favicon
html_logo = '_static/logo.png'  # Add this file if you have a logo
html_favicon = '_static/favicon.ico'  # Add this file if you have a favicon

# -- Options for manual page output ------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-manual-page-output

man_pages = [
    ('index', 'btrtools', 'BTR-TOOLS Documentation', [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-texinfo-output

texinfo_documents = [
    ('index', 'BTRTOOLS', 'BTR-TOOLS Documentation', author, 'BTRTOOLS',
     'Generic command-line toolkit for Btrieve database file analysis and export.', 'Miscellaneous'),
]

# -- Extension configuration --------------------------------------------------

# Todo extension
todo_include_todos = True

# Coverage extension
coverage_modules = ['btrtools']
coverage_ignore_modules = ['btrtools.tests']
coverage_ignore_functions = ['test_*', 'setup', 'teardown']
coverage_ignore_classes = ['Test*']