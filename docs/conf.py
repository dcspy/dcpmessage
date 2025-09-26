import os
import sys
import tomllib

sys.path.insert(0, os.path.abspath(".."))

with open("../pyproject.toml", "rb") as f:
    pyproject = tomllib.load(f)

# Project information
project = "dcpmessage"
copyright = "2024, dcpmessage Authors"
author = "dcpmessage Authors"
release = pyproject["project"]["version"]

# General configuration
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]
autodoc_member_order = "bysource"
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
add_module_names = False
source_suffix = {".rst": "restructuredtext"}

# Options for HTML output
html_show_sourcelink = False
html_theme = "sphinx_rtd_theme"
html_baseurl = "https://dcspy.github.io/dcpmessage/"
html_context = {
    "display_github": True,
    "github_user": "dcspy",
    "github_repo": "dcpmessage",
    "github_version": "main",
    "conf_py_path": "/docs/",
}
