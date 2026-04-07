"""InputShowcase: demonstrates TInput features."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TInput


class InputShowcase(BaseShowcase):
    """Showcase for the TInput atom component.

    Sections: basic usage, clearable, password mode.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Basic usage
        self.add_section(
            "Basic Usage",
            "A simple text input field.",
            TInput(placeholder="Enter text..."),
        )

        # Clearable
        self.add_section(
            "Clearable",
            "Shows a clear button when text is present.",
            TInput(placeholder="Type and clear...", clearable=True),
        )

        # Password mode
        self.add_section(
            "Password Mode",
            "Masks input text with a visibility toggle button.",
            TInput(placeholder="Password", password=True),
        )
