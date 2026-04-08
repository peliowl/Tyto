"""SwitchShowcase: demonstrates TSwitch sizes, loading, square, and track text."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TSwitch


class SwitchShowcase(BaseShowcase):
    """Showcase for the TSwitch atom component.

    Sections: basic usage, disabled, sizes, loading, square, track text.

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

        # Sizes
        self.add_section(
            "Sizes",
            "Small, Medium, and Large size variants.",
            self.hbox(
                TSwitch(checked=True, size=TSwitch.SwitchSize.SMALL),
                TSwitch(checked=True, size=TSwitch.SwitchSize.MEDIUM),
                TSwitch(checked=True, size=TSwitch.SwitchSize.LARGE),
            ),
        )

        # Loading
        self.add_section(
            "Loading",
            "Loading switches show a spinner on the thumb and block interaction.",
            self.hbox(
                TSwitch(checked=False, loading=True),
                TSwitch(checked=True, loading=True),
            ),
        )

        # Square (round=False)
        self.add_section(
            "Square",
            "Square track and thumb when round is disabled.",
            self.hbox(
                TSwitch(checked=False, round=False),
                TSwitch(checked=True, round=False),
            ),
        )

        # Track text
        self.add_section(
            "Track Text",
            "Display on/off text labels inside the track.",
            self.hbox(
                TSwitch(checked=False, checked_text="ON", unchecked_text="OFF"),
                TSwitch(checked=True, checked_text="ON", unchecked_text="OFF"),
            ),
        )
