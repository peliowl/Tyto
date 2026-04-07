"""RadioShowcase: demonstrates TRadio and TRadioGroup."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TRadio, TRadioGroup


class RadioShowcase(BaseShowcase):
    """Showcase for the TRadio / TRadioGroup atom components.

    Sections: basic usage, group mutual exclusion.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Basic usage
        self.add_section(
            "Basic Usage",
            "A single radio button.",
            self.hbox(TRadio("Option", value="opt")),
        )

        # Group mutual exclusion
        group = TRadioGroup()
        group.add_radio(TRadio("Option A", value="a"))
        group.add_radio(TRadio("Option B", value="b", checked=True))
        group.add_radio(TRadio("Option C", value="c"))

        self.add_section(
            "Group Mutual Exclusion",
            "Only one radio can be selected within a group.",
            group,
        )
