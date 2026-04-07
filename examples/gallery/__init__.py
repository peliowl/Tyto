"""Tyto UI Component Gallery - MVVM architecture.

Run with:
    uv run python examples/gallery.py
    uv run python -m examples.gallery
"""

from __future__ import annotations


def main() -> None:
    """Launch the gallery application."""
    import sys

    from PySide6.QtWidgets import QApplication

    from examples.gallery.views.gallery_window import GalleryWindow

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = GalleryWindow()
    window.show()

    sys.exit(app.exec())
