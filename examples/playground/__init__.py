"""Tyto UI Playground - interactive component debugging application.

Run with:
    uv run python examples/playground.py
    uv run python -m examples.playground
"""

from __future__ import annotations


def main() -> None:
    """Launch the playground application."""
    import sys

    from PySide6.QtWidgets import QApplication

    from examples.playground.views.playground_window import PlaygroundWindow

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = PlaygroundWindow()
    window.show()

    sys.exit(app.exec())
