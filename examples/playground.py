"""Tyto UI Playground - interactive component debugging application.

Run with:
    uv run python examples/playground.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the project root is on sys.path so that 'examples' is importable.
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from examples.playground import main

if __name__ == "__main__":
    main()
