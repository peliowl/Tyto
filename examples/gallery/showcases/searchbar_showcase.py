"""SearchBarShowcase: demonstrates TSearchBar features."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TSearchBar


class SearchBarShowcase(BaseShowcase):
    """Showcase for the TSearchBar molecule component.

    Sections: basic usage, clearable.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Basic usage
        self.add_section(
            "Basic Usage",
            "TInput + TButton composite search bar.",
            TSearchBar(placeholder="Search..."),
        )

        # Clearable
        self.add_section(
            "Clearable",
            "Search bar with a clear button.",
            TSearchBar(placeholder="Search...", clearable=True),
        )
