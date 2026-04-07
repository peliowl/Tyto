"""CheckboxShowcase: demonstrates TCheckbox states."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TCheckbox


class CheckboxShowcase(BaseShowcase):
    """Showcase for the TCheckbox atom component.

    Sections: basic usage, three-state display.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Basic usage
        self.add_section(
            "Basic Usage",
            "Click to toggle between checked and unchecked.",
            self.hbox(
                TCheckbox("Unchecked"),
                TCheckbox("Checked", state=TCheckbox.CheckState.CHECKED),
            ),
        )

        # Three states
        self.add_section(
            "Three States",
            "Checkbox supports Unchecked, Checked, and Indeterminate states.",
            self.hbox(
                TCheckbox("Unchecked", state=TCheckbox.CheckState.UNCHECKED),
                TCheckbox("Checked", state=TCheckbox.CheckState.CHECKED),
                TCheckbox("Indeterminate", state=TCheckbox.CheckState.INDETERMINATE),
            ),
        )
