"""SwitchShowcase: demonstrates TSwitch states."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TSwitch


class SwitchShowcase(BaseShowcase):
    """Showcase for the TSwitch atom component.

    Sections: basic usage, disabled state.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Basic usage
        self.add_section(
            "Basic Usage",
            "iOS/NaiveUI-style toggle switch.",
            self.hbox(
                TSwitch(checked=False),
                TSwitch(checked=True),
            ),
        )

        # Disabled
        self.add_section(
            "Disabled",
            "Disabled switches cannot be toggled.",
            self.hbox(
                TSwitch(checked=False, disabled=True),
                TSwitch(checked=True, disabled=True),
            ),
        )
