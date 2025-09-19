"""Sphinx configuration for the Check4Parts documentation."""

from __future__ import annotations

import os
import sys
from datetime import datetime


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_PATH = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PATH)


project = "Check4Parts"
author = "Check4Parts Engineering"
copyright = f"{datetime.utcnow():%Y}, {author}"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
]

autosummary_generate = True

templates_path = ["_templates"]
exclude_patterns: list[str] = []

html_theme = "alabaster"

