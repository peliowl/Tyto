"""ButtonShowcase: demonstrates TButton types, loading, and disabled states."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TButton


class ButtonShowcase(BaseShowcase):
    """Showcase for the TButton atom component.

    Sections: basic usage, types, loading state, disabled state.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Basic usage
        self.add_section(
            "Basic Usage",
            "A simple default button.",
            self.hbox(TButton("Button")),
        )

        # Types
        self.add_section(
            "Types",
            "Primary, Default, Dashed, and Text button types.",
            self.hbox(
                TButton("Primary", button_type=TButton.ButtonType.PRIMARY),
                TButton("Default", button_type=TButton.ButtonType.DEFAULT),
                TButton("Dashed", button_type=TButton.ButtonType.DASHED),
                TButton("Text", button_type=TButton.ButtonType.TEXT),
            ),
        )

        # Loading
        self.add_section(
            "Loading",
            "Buttons in loading state show a spinner and block clicks.",
            self.hbox(
                TButton("Loading", button_type=TButton.ButtonType.PRIMARY, loading=True),
                TButton("Loading", button_type=TButton.ButtonType.DEFAULT, loading=True),
            ),
        )

        # Disabled
        self.add_section(
            "Disabled",
            "Disabled buttons have reduced opacity and block interaction.",
            self.hbox(
                TButton("Disabled", button_type=TButton.ButtonType.PRIMARY, disabled=True),
                TButton("Disabled", button_type=TButton.ButtonType.DEFAULT, disabled=True),
            ),
        )
