# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

pkg_root = os.path.abspath('..')
sys.path.insert(0, pkg_root)


# -- Project information -----------------------------------------------------
import subprocess

project = 'clictagger'
copyright = '%s, Michaela Mahlberg, Viola Wiegand, Jamie Lentin & Anthony Hennessey' % (
    subprocess.check_output("git log -1 --format=%ai".split()).decode('utf8').split('-', 1)[0],
)
author = 'Michaela Mahlberg, Viola Wiegand, Jamie Lentin & Anthony Hennessey'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.extlinks',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# -- Autodoc configuration ---------------------------------------------------
def run_apidoc(_):
    """
    Auto-run sphinx-autodoc
    """
    import os
    from sphinx.ext import apidoc

    apidoc.main([
        "--doc-project", "Module documentation",
        "--no-toc",
        "--force",
        "--separate",
        "--no-headings",
        "--module-first",
        "--maxdepth", "10",
        "-o", ".",
        pkg_root,
        os.path.join(pkg_root, 'appconfig.py'),
        os.path.join(pkg_root, 'clictagger', 'icuconfig.py'),
        os.path.join(pkg_root, 'clictagger', 'region', 'utils.py'),
        os.path.join(pkg_root, 'conftest.py'),
        os.path.join(pkg_root, 'tests', '*.py'),
        os.path.join(pkg_root, 'setup.py'),
    ])
    # No point having top-level package docs, index.rst will do that
    os.unlink(os.path.join(pkg_root, 'docs', 'clictagger.rst'))

autodoc_mock_imports = """
appconfig
numpy pandas
pybtex
psycopg2
icu
unidecode
flask flask_cors
""".split()

# ----------------------------------------------------------------------------

def setup(app):
    app.connect('builder-inited', run_apidoc)
