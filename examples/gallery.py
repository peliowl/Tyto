"""Tyto UI Component Gallery - interactive preview of all components.

Run with:
    uv run python examples/gallery.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the project root is on sys.path so that 'examples' is importable.
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from examples.gallery import main

if __name__ == "__main__":
    main()
