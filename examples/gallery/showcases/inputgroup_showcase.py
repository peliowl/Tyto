"""InputGroupShowcase: demonstrates TInputGroup features."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TButton, TInput, TInputGroup


class InputGroupShowcase(BaseShowcase):
    """Showcase for the TInputGroup molecule component.

    Sections: basic usage.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Basic usage
        group = TInputGroup()
        group.add_widget(TInput(placeholder="https://"))
        group.add_widget(TButton("Go", button_type=TButton.ButtonType.PRIMARY))

        self.add_section(
            "Basic Usage",
            "Compact horizontal arrangement with merged border-radius.",
            group,
        )
