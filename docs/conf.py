# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------
project = "dcpmessage"
copyright = "2024, dcpmessage Authors"
author = "dcpmessage Authors"
release = "0.0.1"

# -- General configuration ---------------------------------------------------
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]
autodoc_member_order = "bysource"
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
add_module_names = False
source_suffix = {".rst": "restructuredtext"}

# -- Options for HTML output -------------------------------------------------
html_show_sourcelink = False
html_theme = "sphinx_rtd_theme"
html_baseurl = "https://dcspy.github.io/dcpmessage/"
